#!/usr/bin/env python3
"""
Evaluate LLM answers using an LLM judge for accuracy scoring.

For each question folder in results/:
  - Reads question.json
  - Reads each model answer file
  - Passes the condensed answer text to an LLM judge
  - Judge scores each model independently as percentage accuracy (0-100%)
  - Writes evaluation.json with per-model metadata
  - Writes analysis.json with LLM judge scores
"""

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset" / "Kubecluster"

# Known repo aliases → canonical directory name in dataset/Kubecluster/
REPO_ALIASES = {
    "argocd": "argo-cd", "argo-cd": "argo-cd", "argo_cd": "argo-cd",
    "cert-manager": "cert-manager", "certmanager": "cert-manager",
    "external-dns": "external-dns", "externaldns": "external-dns",
    "external-secrets": "external-secrets", "externalsecrets": "external-secrets",
    "ingress-nginx": "ingress-nginx", "ingressnginx": "ingress-nginx",
    "opentelemetry-collector": "opentelemetry-collector",
    "opentelemetry-collector-contrib": "opentelemetry-collector-contrib",
    "opentelemetry-operator": "opentelemetry-operator",
    "otel-collector": "opentelemetry-collector",
    "otel-collector-contrib": "opentelemetry-collector-contrib",
    "karpenter": "karpenter", "karpenter-provider-aws": "karpenter",
    "loki-operator": "loki",
}


def _resolve_repo(repo_name: str) -> str:
    """Resolve a repo name (or alias) to the canonical directory name."""
    low = repo_name.lower().strip()
    if low in REPO_ALIASES:
        return REPO_ALIASES[low]
    # Exact match against existing dirs
    if (DATASET_DIR / low).is_dir():
        return low
    # Fallback: return as-is
    return low


def verify_file_paths(condensed_answer: str) -> dict:
    """Extract file paths from a condensed answer and verify against the dataset.

    Returns dict with keys: verified (list of existing paths),
    hallucinated (list of non-existing paths), total.
    """
    verified = []
    hallucinated = []

    if not condensed_answer:
        return {"verified": verified, "hallucinated": hallucinated, "total": 0}

    # Parse "- repo/path/to/file — reason" lines from FILES: section
    in_files = False
    for line in condensed_answer.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith("FILES:"):
            in_files = True
            continue
        if not in_files:
            continue
        if not stripped.startswith("- "):
            if stripped and not stripped.startswith("#"):
                continue
            continue

        # Remove leading "- "
        entry = stripped[2:].strip()
        # Split on " — " or " - " to separate path from reason
        for sep in [" — ", " – ", " - "]:
            if sep in entry:
                entry = entry.split(sep, 1)[0].strip()
                break

        # entry should now be like "repo/path/to/file.go"
        if "/" not in entry:
            continue

        parts = entry.split("/", 1)
        repo_raw = parts[0].strip()
        file_path = parts[1].strip() if len(parts) > 1 else ""
        if not file_path:
            continue

        repo = _resolve_repo(repo_raw)
        full_path = DATASET_DIR / repo / file_path
        if full_path.is_file():
            verified.append(f"{repo}/{file_path}")
        else:
            hallucinated.append(f"{repo}/{file_path}")

    return {
        "verified": verified,
        "hallucinated": hallucinated,
        "total": len(verified) + len(hallucinated),
    }


# ─── Model answer loading ─────────────────────────────────────────────────────


def load_model_answers(folder_path: Path) -> list[dict]:
    """Load all model answer files from a question folder.

    Returns list of dicts with model metadata + full answer text.
    """
    answer_files = [
        f for f in sorted(folder_path.iterdir())
        if f.suffix == ".json"
        and f.name not in (
            "question.json", "evaluation.json", "analysis.json",
            "analysis_summary.json", "ground_truth.json",
            "claude_opus_4.6_direct_data_access.json",
        )
    ]

    answers = []
    for af in answer_files:
        try:
            with open(af) as f:
                data = json.load(f)
            cost = data.get("cost", {})
            # Extract tool call result previews
            tool_calls_raw = data.get("tool_calls", [])
            tool_results = []
            for tc in tool_calls_raw:
                preview = tc.get("result_preview", "")
                if preview:
                    tool_results.append({
                        "tool": tc.get("tool_name", "unknown"),
                        "args": tc.get("arguments", {}),
                        "result_preview": preview[:500],
                    })
            entry = {
                "model": data.get("model", af.stem),
                "status": data.get("status", "unknown"),
                "full_answer": data.get("answer", ""),
                "answer": data.get("llm_condensed_answer") or data.get("answer", ""),
                "tool_calls_count": data.get("tool_calls_count", 0),
                "input_tokens": cost.get("input_tokens", 0),
                "output_tokens": cost.get("output_tokens", 0),
                "total_tokens": cost.get("total_tokens", 0),
                "cost_usd": cost.get("cost_usd", 0.0),
                "tool_results": tool_results,
            }
            if data.get("llm_condensed_answer"):
                entry["llm_condensed_answer"] = data["llm_condensed_answer"]
            answers.append(entry)
        except (json.JSONDecodeError, KeyError) as e:
            answers.append({
                "model": af.stem,
                "status": "parse_error",
                "answer": "",
                "tool_calls_count": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "error": str(e),
            })
    return answers


def process_question_folder(folder_path: Path) -> dict | None:
    """Process a single question folder and return evaluation data."""
    question_file = folder_path / "question.json"
    if not question_file.exists():
        return None

    with open(question_file) as f:
        question = json.load(f)

    answers = load_model_answers(folder_path)
    if not answers:
        return None

    return {
        "question_id": question.get("id", folder_path.name),
        "question": question.get("question", ""),
        "model_evaluations": answers,
    }


# ─── LLM comparative judge ────────────────────────────────────────────────────


def _build_model_section(model_answer: dict) -> str:
    """Build the prompt section for one model's condensed answer for the judge.

    Includes filesystem verification: how many listed files actually exist
    in dataset/Kubecluster/ and which ones are hallucinated (don't exist).
    """
    model = model_answer["model"]
    tool_calls = model_answer.get("tool_calls_count", 0)
    # Use condensed answer if available, otherwise fall back to full answer
    answer = model_answer.get("llm_condensed_answer") or model_answer.get("answer", "").strip() or "(empty)"

    # Verify file paths against the actual dataset
    fv = verify_file_paths(answer)
    n_verified = len(fv["verified"])
    n_hallucinated = len(fv["hallucinated"])
    n_total = fv["total"]

    lines = [
        f"--- {model} ---",
        f"Tool calls used: {tool_calls}",
        f"File paths verified against dataset: {n_verified}/{n_total} exist, {n_hallucinated} hallucinated",
    ]
    if fv["hallucinated"]:
        lines.append("Hallucinated paths (DO NOT EXIST on disk):")
        for hp in fv["hallucinated"]:
            lines.append(f"  ✗ {hp}")
    lines.append("Answer:")
    lines.append(answer)

    return "\n".join(lines)


def generate_comparative_analysis(
    folder_path: Path, api_key: str, judge_model: str,
    smoke_test_model: str = "xiaomi/mimo-v2-flash",
) -> dict | None:
    """Generate analysis.json using a single LLM call that compares all models.

    Each model's answer is first condensed via the smoke_test_model into
    a short summary + file list, then the condensed versions are sent to
    the judge. Each model gets an independent accuracy score (0-100%).
    """
    from evals import condense_answer

    question_file = folder_path / "question.json"
    if not question_file.exists():
        return None

    with open(question_file) as f:
        question = json.load(f)

    q_text = question.get("question", "")

    # Load ground truth if available
    ground_truth_text = ""
    gt_file = folder_path / "ground_truth.json"
    if gt_file.exists():
        with open(gt_file) as f:
            gt_data = json.load(f)
        # Build ground truth section from expected_files and condensed answer
        gt_answer = gt_data.get("llm_condensed_answer") or gt_data.get("answer", "")
        gt_expected = gt_data.get("expected_files", [])
        gt_parts = [gt_answer]
        if gt_expected:
            gt_parts.append("\nExpected files:")
            for ef in gt_expected:
                repo = ef.get("repo", "")
                files = ef.get("files", [])
                reason = ef.get("reason", "")
                for fp in files:
                    gt_parts.append(f"  - {repo}/{fp} — {reason}")
        ground_truth_text = "\n".join(gt_parts)

    # Load evaluation data
    eval_file = folder_path / "evaluation.json"
    if not eval_file.exists():
        return None

    with open(eval_file) as f:
        eval_data = json.load(f)

    model_evals = eval_data.get("model_evaluations", [])
    # Filter to models with answers or tool call results
    active_evals = [
        m for m in model_evals
        if m.get("status") == "success"
        and (m.get("answer", "").strip() or m.get("tool_results"))
    ]

    if not active_evals:
        return None

    # Condense each model's full answer via smoke_test_model
    # Use full_answer (original) — not answer (which may already be condensed)
    for me in active_evals:
        if me.get("llm_condensed_answer"):
            continue  # already condensed, skip
        raw = me.get("full_answer") or me.get("answer", "")
        raw = raw.strip()
        if raw:
            print(f"      condensing {me['model'].split('/')[-1]}...", end=" ", flush=True)
            me["llm_condensed_answer"] = condense_answer(
                raw, q_text, api_key, model=smoke_test_model,
            )
            print("done")

    # Build prompt sections for each model (uses llm_condensed_answer)
    model_sections = []
    for me in active_evals:
        model_sections.append(_build_model_section(me))

    models_text = "\n\n".join(model_sections)
    model_names = [me["model"] for me in active_evals]

    # Build ground truth section for the prompt
    gt_prompt_section = ""
    if ground_truth_text:
        gt_prompt_section = (
            f"GROUND TRUTH (reference answer — use this as the authoritative baseline):\n"
            f"{ground_truth_text}\n\n"
        )

    prompt = (
        "You are an expert evaluator for a code-impact-analysis benchmark.\n\n"
        "A question was asked about cross-repository code impact. Multiple AI models provided answers. "
        "Each model had access to a knowledge graph of 25 Cloud Native repositories and used tool calls "
        "to search and retrieve file information before answering.\n\n"
        f"QUESTION:\n{q_text}\n\n"
        f"{gt_prompt_section}"
        f"MODEL ANSWERS:\n\n{models_text}\n\n"
        "Score each model's answer INDEPENDENTLY as a percentage accuracy (0-100).\n"
        "Each model gets its own score — scores are NOT relative to each other.\n\n"
        "Weighted criteria:\n\n"
        "1. GROUND TRUTH RECALL (50% of score):\n"
        "   - Compare each model's listed files against the GROUND TRUTH expected files\n"
        "   - What fraction of the ground truth files did the model find?\n"
        "   - Did the model identify the correct affected repositories and files?\n\n"
        "2. EXTRA CORRECT FILES (20% of score — BONUS):\n"
        "   - Each model section shows how many of its listed file paths were VERIFIED to exist on disk\n"
        "   - Award points for extra files beyond the ground truth that actually exist and are relevant to the question\n"
        "   - Test files, YAML configs, and other supplementary files count as correct if they exist and relate to the change\n"
        "   - More verified extra files = higher bonus\n\n"
        "3. REASONING QUALITY (20% of score):\n"
        "   - Did the model explain WHY each file is affected (interface implementation, dependency chain, data flow)?\n"
        "   - Did it describe what specifically needs to change in each file?\n"
        "   - Is the analysis thorough — covering architecture, cross-repo impact, and breaking changes?\n\n"
        "4. HALLUCINATION PENALTY (10% of score — DEDUCT for errors):\n"
        "   - Each model section lists which file paths are HALLUCINATED (do not exist on disk)\n"
        "   - Deduct points proportional to the number of hallucinated paths\n"
        "   - Zero hallucinated paths = full 10 points. Many hallucinated paths = 0 points\n\n"
        "IMPORTANT: Each score is an independent percentage (0-100). Multiple models CAN have the same score.\n"
        "A perfect answer = 100. A completely wrong answer = 0. Most answers fall between 20-80.\n"
        f"Models to score (use EXACTLY these names): {json.dumps(model_names)}\n\n"
        "Respond ONLY with a single line of valid JSON. No markdown, no code fences, no newlines inside strings.\n"
        "Keep each justification short (max 15 words).\n"
        '{"scores": [{"model": "<model_name>", "score": <int 0-100>, "justification": "<max 15 words>"}, ...]}'
    )

    import time as _time
    eval_by_model = {me["model"]: me for me in active_evals}

    for attempt in range(1, 4):  # up to 3 attempts
        try:
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json={
                    "model": judge_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0,
                    "max_tokens": 15000,
                },
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                timeout=120,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"    LLM judge request failed (attempt {attempt}/3): {e}")
            if attempt < 3:
                _time.sleep(attempt * 5)
                continue
            return None

        resp_json = resp.json()
        choice = resp_json.get("choices", [{}])[0]
        content = choice.get("message", {}).get("content", "")
        content = content.strip()



        if content.startswith("```"):
            content = "\n".join(content.split("\n")[1:])
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        try:
            parsed = json.loads(content)
            scores = parsed.get("scores", [])

            scores = [s for s in scores if s.get("model") in eval_by_model]

            if not scores:
                print(f"    No matching model scores after filtering (attempt {attempt}/3)")
                if attempt < 3:
                    _time.sleep(attempt * 5)
                    continue
                return None

            # Clamp scores to 0-100 range
            for s in scores:
                s["score"] = max(0, min(100, int(round(s.get("score", 0)))))

            # Enrich each score with token counts and cost
            for s in scores:
                me = eval_by_model.get(s.get("model"), {})
                s["tool_calls_count"] = me.get("tool_calls_count", 0)
                s["input_tokens"] = me.get("input_tokens", 0)
                s["output_tokens"] = me.get("output_tokens", 0)
                s["total_tokens"] = me.get("total_tokens", 0)
                s["cost_usd"] = me.get("cost_usd", 0.0)

            return {
                "question_id": question.get("id", folder_path.name),
                "question": q_text,
                "model_scores": scores,
            }
        except (json.JSONDecodeError, ValueError, TypeError):
            print(f"    Failed to parse LLM response (attempt {attempt}/3): {content[:200]}")
            if attempt < 3:
                _time.sleep(attempt * 5)
                continue
            return None

    return None


def _write_scores_to_evaluation(eval_path: Path, scores: list[dict]):
    """Write relevance scores from analysis back into evaluation.json per model."""
    with open(eval_path) as f:
        eval_data = json.load(f)

    score_by_model = {s["model"]: s for s in scores}
    for me in eval_data.get("model_evaluations", []):
        model = me.get("model", "")
        if model in score_by_model:
            me["relevance_score"] = score_by_model[model].get("score", 0)
            me["judge_justification"] = score_by_model[model].get("justification", "")
        else:
            me["relevance_score"] = 0
            me["judge_justification"] = ""

    with open(eval_path, "w") as f:
        json.dump(eval_data, f, indent=2)


# ─── Main ─────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate LLM answers using a comparative LLM judge")
    parser.add_argument("--results-dir", "-r", required=True,
                        help="Path to results folder (e.g. results/KubeCluster40)")
    parser.add_argument("--force", "-f", action="store_true",
                        help="Force re-evaluation even if evaluation.json/analysis.json exist")
    parser.add_argument("--questions", "-n", type=str, default=None,
                        help="Comma-separated question IDs to run (e.g. OBS_TC001,OBS_TC002). Default: all")
    parser.add_argument("--workers", "-w", type=int, default=1,
                        help="Number of parallel workers for judge calls (default: 1)")
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    if not results_dir.exists():
        print(f"Error: results directory not found: {results_dir}")
        sys.exit(1)

    load_dotenv()

    # Load judge model
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from evals import load_models_config, condense_answer
    models_cfg = load_models_config()
    judge_model = models_cfg.get("judge_model", "anthropic/claude-haiku-4.5")
    smoke_test_model = models_cfg.get("smoke_test_model", "xiaomi/mimo-v2-flash")

    api_key = os.getenv("OPENROUTER_API_KEY", "")
    run_analysis = bool(api_key)
    if not api_key:
        print("No OPENROUTER_API_KEY set — skipping LLM judge analysis")
        print("Set OPENROUTER_API_KEY in .env to enable comparative scoring")
        print()

    if run_analysis:
        print(f"Judge model: {judge_model}")
        print(f"Condenser model: {smoke_test_model}")
    print()

    # Find all question folders
    question_folders = sorted([
        d for d in results_dir.iterdir()
        if d.is_dir() and d.name.startswith("question_")
    ])

    if args.questions is not None:
        requested_ids = {qid.strip() for qid in args.questions.split(",")}
        question_folders = [f for f in question_folders if f.name.replace("question_", "") in requested_ids]
        missing = requested_ids - {f.name.replace("question_", "") for f in question_folders}
        if missing:
            print(f"Warning: question IDs not found: {', '.join(sorted(missing))}")
        print(f"Found {len(question_folders)} question folders (filtered: {args.questions})\n")
    else:
        print(f"Found {len(question_folders)} question folders\n")

    total_evals = 0
    total_analyses = 0

    # Step 1: Build evaluation.json for each folder (fast, no LLM calls)
    folders_to_judge: list[tuple[Path, Path]] = []  # (folder, eval_path)
    for folder in question_folders:
        eval_path = folder / "evaluation.json"
        if eval_path.exists() and not args.force:
            with open(eval_path) as f:
                result = json.load(f)
            n_models = len(result.get("model_evaluations", []))
            print(f"  {folder.name}: evaluation.json exists ({n_models} models) — skipping")
        else:
            result = process_question_folder(folder)
            if result is None:
                print(f"  SKIP {folder.name} — no question.json or no answer files")
                continue

            with open(eval_path, "w") as f:
                json.dump(result, f, indent=2)

            n_models = len(result["model_evaluations"])
            n_success = sum(1 for e in result["model_evaluations"] if e["status"] == "success")
            print(f"  {folder.name}: {n_models} models ({n_success} success)")

        total_evals += 1

        # Queue for judge analysis
        if run_analysis:
            analysis_path = folder / "analysis.json"
            if analysis_path.exists() and not args.force:
                with open(analysis_path) as f:
                    existing_analysis = json.load(f)
                existing_scores = existing_analysis.get("model_scores", [])
                _write_scores_to_evaluation(eval_path, existing_scores)
                print(f"    analysis.json exists — skipping (scores synced to evaluation.json)")
                total_analyses += 1
            else:
                folders_to_judge.append((folder, eval_path))

    # Step 2: LLM judge — parallel with --workers
    if run_analysis and folders_to_judge:
        n_workers = min(args.workers, len(folders_to_judge))
        print(f"\nRunning LLM judge on {len(folders_to_judge)} questions with {n_workers} workers...\n")

        def _judge_one(folder: Path, eval_path: Path) -> tuple[str, bool]:
            """Judge one question folder. Returns (folder_name, success)."""
            analysis_path = folder / "analysis.json"
            analysis = generate_comparative_analysis(folder, api_key, judge_model, smoke_test_model)
            if analysis:
                with open(analysis_path, "w") as f:
                    json.dump(analysis, f, indent=2)
                scores = analysis.get("model_scores", [])
                score_parts = ", ".join(
                    f"{s['model'].split('/')[-1]}={s['score']}%" for s in scores
                )
                print(f"    {folder.name}: {len(scores)} models | {score_parts}")
                _write_scores_to_evaluation(eval_path, scores)
                return folder.name, True
            else:
                print(f"    {folder.name}: skipped (no data or LLM error)")
                return folder.name, False

        with ThreadPoolExecutor(max_workers=n_workers) as pool:
            futures = {
                pool.submit(_judge_one, folder, eval_path): folder.name
                for folder, eval_path in folders_to_judge
            }
            for future in as_completed(futures):
                _, success = future.result()
                if success:
                    total_analyses += 1

    # ── Aggregate analysis_summary.json ──
    if run_analysis and total_analyses > 0:
        from collections import defaultdict

        model_agg: dict[str, dict] = defaultdict(lambda: {
            "scores": [], "input_tokens": 0, "output_tokens": 0,
            "total_tokens": 0, "cost_usd": 0.0,
        })
        all_question_rows = []

        for folder in question_folders:
            af = folder / "analysis.json"
            if not af.exists():
                continue
            with open(af) as f:
                adata = json.load(f)

            q_id = adata.get("question_id", folder.name)
            q_text = adata.get("question", "")
            row = {"question_id": q_id, "question": q_text[:120], "models": {}}

            for ms in adata.get("model_scores", []):
                model = ms.get("model", "")
                score = ms.get("score", 0)
                justification = ms.get("justification", "")
                row["models"][model] = {
                    "score": score,
                    "justification": justification,
                    "cost_usd": ms.get("cost_usd", 0.0),
                }
                agg = model_agg[model]
                agg["scores"].append(score)
                agg["input_tokens"] += ms.get("input_tokens", 0)
                agg["output_tokens"] += ms.get("output_tokens", 0)
                agg["total_tokens"] += ms.get("total_tokens", 0)
                agg["cost_usd"] += ms.get("cost_usd", 0.0)

            all_question_rows.append(row)

        model_summaries = []
        for model, agg in sorted(model_agg.items()):
            scores = agg["scores"]
            avg_pct = round(sum(scores) / len(scores), 2) if scores else 0
            total_cost = round(agg["cost_usd"], 4)
            # Accuracy per dollar — higher is better
            pct_per_dollar = round(avg_pct / total_cost, 2) if total_cost > 0 else 0
            model_summaries.append({
                "model": model,
                "avg_accuracy_pct": avg_pct,
                "questions_judged": len(scores),
                "input_tokens": agg["input_tokens"],
                "output_tokens": agg["output_tokens"],
                "total_tokens": agg["total_tokens"],
                "total_cost_usd": total_cost,
                "pct_per_dollar": pct_per_dollar,
            })
        model_summaries.sort(key=lambda m: m["avg_accuracy_pct"], reverse=True)

        summary = {
            "judge_model": judge_model,
            "scoring": "independent percentage accuracy (0-100%)",
            "total_questions_analyzed": len(all_question_rows),
            "model_summaries": model_summaries,
            "per_question": all_question_rows,
        }

        summary_path = results_dir / "analysis_summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"\nAnalysis summary saved to: {summary_path}")

        print(f"\n{'Model':<45} | {'Avg %':>7} | {'Cost $':>10} | {'%/$':>8} | {'Judged':>6}")
        print(f"{'-'*45}-+-{'-'*7}-+-{'-'*10}-+-{'-'*8}-+-{'-'*6}")
        for ms in model_summaries:
            print(f"{ms['model']:<45} | {ms['avg_accuracy_pct']:>6.1f}% | "
                  f"${ms['total_cost_usd']:>9.4f} | {ms['pct_per_dollar']:>7.2f} | {ms['questions_judged']:>6}")

    print()
    print(f"Done! Evaluated {total_evals} questions")
    if run_analysis:
        print(f"Generated {total_analyses} analysis.json files with accuracy scores (0-100%)")


if __name__ == "__main__":
    main()
