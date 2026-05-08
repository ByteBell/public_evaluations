#!/usr/bin/env python3
"""
Enhanced evaluation using ground_truth_enhanced.json.

Implements the fact-based marking scheme from evaluation.md:

  Per correct file (max +10 marks):
    - File Detection    (4):   automated binary — file in GT impacted_files?
    - Breaking Pattern  (0-2): LLM judge — did model identify the right pattern(s)?
    - Severity          (0-1): LLM judge — correct severity classification?
    - Fix Quality       (0-3): LLM judge — quality of fix vs GT suggested_fix?

  Per hallucinated file:        -5 (automated)
  Per false positive omitted:   +2 (automated)

  max_possible = (total_impacted × 10) + (total_false_positives × 2)
  final_pct    = raw_score / max_possible × 100  (can go negative)

Output files:
  <question_folder>/enhanced_evaluation.json   — per-model per-file breakdown
  <results_dir>/enhanced_analysis_summary.json — cross-model aggregate
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# ─── Repo alias normalisation ─────────────────────────────────────────────────

REPO_ALIASES: dict[str, str] = {
    "argocd":                        "argo-cd",
    "otel-collector":                "opentelemetry-collector",
    "otel-collector-contrib":        "opentelemetry-collector-contrib",
    "k8s":                           "kubernetes",
    "otel-operator":                 "opentelemetry-operator",
    "oteloperator":                  "opentelemetry-operator",
    "opentelemetry-collector-contrib": "opentelemetry-collector-contrib",
}


def normalize_repo(repo: str) -> str:
    r = repo.lower().strip()
    return REPO_ALIASES.get(r, r)


def normalize_path(path: str) -> str:
    p = path.strip()
    if p.startswith("./"):
        p = p[2:]
    elif p.startswith("/"):
        p = p[1:]
    return p


# ─── Data loading ─────────────────────────────────────────────────────────────


def load_ground_truth_enhanced(folder: Path) -> dict | None:
    gt_file = folder / "ground_truth_enhanced.json"
    if not gt_file.exists():
        return None
    with open(gt_file) as f:
        return json.load(f)


_SKIP_FILES = frozenset({
    "question.json", "evaluation.json", "analysis.json",
    "enhanced_evaluation.json", "analysis_summary.json",
    "enhanced_analysis_summary.json",
    "ground_truth.json", "ground_truth_enhanced.json",
    "claude_opus_4.6_direct_data_access.json",
})


def load_ground_truth_as_answer(folder: Path) -> dict | None:
    """Load ground_truth.json as a pseudo-model answer for self-scoring.

    The original GT was itself an AI-generated answer; scoring it against
    ground_truth_enhanced lets us measure how good that oracle answer was.
    """
    gt_file = folder / "ground_truth.json"
    if not gt_file.exists():
        return None
    with open(gt_file) as f:
        data = json.load(f)

    # Use full answer preferring the richer text; fall back to condensed
    full_answer = data.get("answer", "") or data.get("llm_condensed_answer", "")
    if not full_answer:
        return None

    cost = data.get("cost", {})
    original_model = data.get("model", "unknown")
    return {
        "model":               f"ground_truth_oracle/{original_model}",
        "status":              data.get("status", "success"),
        "full_answer":         full_answer,
        "answer":              data.get("llm_condensed_answer", ""),
        "llm_condensed_answer": data.get("llm_condensed_answer", ""),
        "tool_calls_count":    data.get("tool_calls_count", 0),
        "input_tokens":        cost.get("input_tokens", 0),
        "output_tokens":       cost.get("output_tokens", 0),
        "total_tokens":        cost.get("total_tokens", 0),
        "cost_usd":            cost.get("cost_usd", 0.0),
        "_is_ground_truth_oracle": True,
    }


def load_model_answers(folder: Path) -> list[dict]:
    """Load all model answer files from a question folder."""
    answer_files = [
        f for f in sorted(folder.iterdir())
        if f.suffix == ".json" and f.name not in _SKIP_FILES
    ]
    answers = []
    for af in answer_files:
        try:
            with open(af) as f:
                data = json.load(f)
            cost = data.get("cost", {})
            answers.append({
                "model":               data.get("model", af.stem),
                "status":              data.get("status", "unknown"),
                # prefer full_answer (pre-condensing) for rich extraction
                "full_answer":         data.get("full_answer") or data.get("answer", ""),
                "answer":              data.get("answer", ""),
                "llm_condensed_answer": data.get("llm_condensed_answer", ""),
                "tool_calls_count":    data.get("tool_calls_count", 0),
                "input_tokens":        cost.get("input_tokens", 0),
                "output_tokens":       cost.get("output_tokens", 0),
                "total_tokens":        cost.get("total_tokens", 0),
                "cost_usd":            cost.get("cost_usd", 0.0),
            })
        except (json.JSONDecodeError, KeyError) as e:
            answers.append({
                "model":      af.stem,
                "status":     "parse_error",
                "full_answer": "",
                "answer":     "",
                "error":      str(e),
            })
    return answers


# ─── Step 1: extract structured claims from model answer ──────────────────────


def extract_model_claims(
    answer_text: str,
    question: str,
    api_key: str,
    model: str,
) -> list[dict]:
    """Use cheap LLM to parse a model's answer into a structured file list.

    Returns a list of dicts:
        repo, file, breaking_explanation, severity, fix_suggestion
    """
    # Truncate to keep the extraction prompt under token limits
    answer_trunc = answer_text[:12_000]

    prompt = (
        "You are a JSON extractor for a code-impact-analysis benchmark.\n\n"
        "Extract ALL files the model claims are impacted by the code change described in the question.\n"
        "For each file extract:\n"
        "  - repo: the repository name (e.g. 'argo-cd', 'cert-manager', 'prometheus')\n"
        "  - file: the file path within that repo (e.g. 'pkg/apis/v1/register.go')\n"
        "  - breaking_explanation: the model's explanation of WHY this file breaks "
        "(what code pattern is affected — be as specific as the answer allows)\n"
        "  - severity: map to exactly one of: 'compile_error', 'runtime_behavior_change', "
        "'test_failure', 'test_only', 'unknown'\n"
        "  - fix_suggestion: the specific fix the model recommends for this file "
        "(empty string '' if not mentioned)\n\n"
        f"QUESTION:\n{question}\n\n"
        f"MODEL ANSWER:\n{answer_trunc}\n\n"
        "Return ONLY valid JSON — no markdown fences, no commentary:\n"
        '{"files": [{"repo": "...", "file": "...", "breaking_explanation": "...", '
        '"severity": "...", "fix_suggestion": "..."}]}\n\n'
        "If the model explicitly states nothing breaks or lists no files, return {\"files\": []}."
    )

    for attempt in range(1, 4):
        try:
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0,
                    "max_tokens": 8000,
                },
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                timeout=90,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"      [extract] request failed (attempt {attempt}/3): {e}")
            if attempt < 3:
                time.sleep(attempt * 3)
                continue
            return []

        content = resp.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()

        # Strip markdown fences if present
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:])
        if content.endswith("```"):
            content = content[:-3].rstrip()

        try:
            parsed = json.loads(content)
            files = parsed.get("files", [])
            # Basic validation
            valid = []
            for f in files:
                if isinstance(f, dict) and f.get("repo") and f.get("file"):
                    valid.append({
                        "repo":                 str(f.get("repo", "")),
                        "file":                 str(f.get("file", "")),
                        "breaking_explanation": str(f.get("breaking_explanation", "")),
                        "severity":             str(f.get("severity", "unknown")),
                        "fix_suggestion":       str(f.get("fix_suggestion", "")),
                    })
            return valid
        except (json.JSONDecodeError, ValueError, AttributeError):
            if attempt < 3:
                time.sleep(attempt * 3)
                continue
            return []

    return []


# ─── Step 2: LLM judge — score per-file dimensions ────────────────────────────

_FALLBACK_SCORE = {"breaking_pattern": 0, "severity": 0, "fix_quality": 0, "notes": "judge failed"}


def _judge_batch(
    batch: list[dict],   # each: {"gt_file": ..., "model_file": ...}
    gt_patterns: list[dict],
    api_key: str,
    judge_model: str,
) -> list[dict]:
    """Score one batch of matched files. Returns list of score dicts."""
    pattern_descs = "\n".join(
        f"  - {p['id']}: {p.get('example', '')[:200]} — {p.get('why_breaks', '')[:200]}"
        for p in gt_patterns
    )

    files_to_score = []
    for item in batch:
        gt = item["gt_file"]
        m = item["model_file"]
        files_to_score.append({
            "repo":                gt["repo"],
            "file":                gt["file"],
            "gt_patterns":         gt.get("breaking_patterns", []),
            "gt_severity":         gt.get("severity", "unknown"),
            "gt_fix":              gt.get("suggested_fix", ""),
            "model_explanation":   m.get("breaking_explanation", ""),
            "model_severity":      m.get("severity", "unknown"),
            "model_fix":           m.get("fix_suggestion", ""),
        })

    prompt = (
        "You are a code-impact-analysis scoring judge.\n\n"
        f"Breaking patterns defined for this change:\n{pattern_descs}\n\n"
        "Score each file on 3 dimensions:\n"
        "1. BREAKING_PATTERN (integer 0-2): fraction of GT patterns the model correctly identified\n"
        "   2 = all GT patterns identified  |  1 = some/partial  |  0 = none/wrong\n"
        "2. SEVERITY (integer 0-1): did the model correctly classify the severity?\n"
        "   1 = matches (or logically equivalent)  |  0 = wrong or missing\n"
        "3. FIX_QUALITY (integer 0-3): how specific and correct is the model's fix vs GT?\n"
        "   3 = semantically equivalent to GT fix\n"
        "   2 = directionally correct but missing details\n"
        "   1 = mentions right concept but vague or partially wrong\n"
        "   0 = no fix stated, or completely wrong\n\n"
        f"FILES TO SCORE (JSON):\n{json.dumps(files_to_score, indent=2)}\n\n"
        "Return ONLY a JSON array with exactly one object per file, IN THE SAME ORDER:\n"
        '[{"repo":"...","file":"...","breaking_pattern":0-2,"severity":0-1,'
        '"fix_quality":0-3,"notes":"<20 words max>"}]'
    )

    for attempt in range(1, 4):
        try:
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json={
                    "model": judge_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0,
                    "max_tokens": 4000,
                },
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                timeout=120,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"      [judge] request failed (attempt {attempt}/3): {e}")
            if attempt < 3:
                time.sleep(attempt * 5)
                continue
            return [_FALLBACK_SCORE.copy() for _ in batch]

        content = resp.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        if content.startswith("```"):
            content = "\n".join(content.split("\n")[1:])
        if content.endswith("```"):
            content = content[:-3].rstrip()

        try:
            parsed = json.loads(content)
            # Accept both array and {"scores": [...]} wrapper
            if isinstance(parsed, dict):
                parsed = parsed.get("scores", parsed.get("files", []))

            results = []
            for idx, item in enumerate(batch):
                gt = item["gt_file"]
                if idx < len(parsed) and isinstance(parsed[idx], dict):
                    s = parsed[idx]
                    results.append({
                        "repo":             gt["repo"],
                        "file":             gt["file"],
                        "breaking_pattern": max(0, min(2, int(round(s.get("breaking_pattern", 0))))),
                        "severity":         max(0, min(1, int(round(s.get("severity", 0))))),
                        "fix_quality":      max(0, min(3, int(round(s.get("fix_quality", 0))))),
                        "notes":            str(s.get("notes", ""))[:120],
                    })
                else:
                    results.append({"repo": gt["repo"], "file": gt["file"], **_FALLBACK_SCORE})
            return results

        except (json.JSONDecodeError, ValueError, TypeError):
            if attempt < 3:
                time.sleep(attempt * 5)
                continue
            return [{"repo": item["gt_file"]["repo"], "file": item["gt_file"]["file"],
                     **_FALLBACK_SCORE} for item in batch]

    return [{"repo": item["gt_file"]["repo"], "file": item["gt_file"]["file"],
             **_FALLBACK_SCORE} for item in batch]


def score_matched_files(
    matched: list[dict],
    gt_patterns: list[dict],
    api_key: str,
    judge_model: str,
    batch_size: int = 10,
) -> dict[tuple, dict]:
    """Run LLM judge over all matched files in batches.

    Returns a dict keyed by (norm_repo, norm_path) → score dict.
    """
    if not matched:
        return {}

    all_scores: dict[tuple, dict] = {}
    for i in range(0, len(matched), batch_size):
        batch = matched[i : i + batch_size]
        batch_results = _judge_batch(batch, gt_patterns, api_key, judge_model)
        for s in batch_results:
            key = (normalize_repo(s["repo"]), normalize_path(s["file"]))
            all_scores[key] = s
    return all_scores


# ─── Step 3: main per-model scoring ───────────────────────────────────────────


def score_model_answer(
    gt_data: dict,
    question_text: str,
    model_answer: dict,
    api_key: str,
    extractor_model: str,
    judge_model: str,
) -> dict:
    """Score one model's answer against the enhanced ground truth.

    Returns a dict suitable for inclusion in enhanced_evaluation.json.
    """
    model = model_answer["model"]
    status = model_answer.get("status", "unknown")

    if status != "success":
        return {
            "model": model,
            "status": status,
            "skipped": True,
            "raw_score": 0,
            "max_possible": 0,
            "final_pct": 0.0,
        }

    # Build GT structures
    gt_impacted      = gt_data.get("impacted_files", [])
    gt_false_positives = gt_data.get("false_positives", [])
    gt_patterns      = gt_data.get("breaking_patterns", [])

    total_impacted = len(gt_impacted)
    total_fp       = len(gt_false_positives)
    max_possible   = total_impacted * 10 + total_fp * 2

    # Build GT lookup: (norm_repo, norm_path) → gt_file_dict
    gt_lookup: dict[tuple, dict] = {}
    for f in gt_impacted:
        key = (normalize_repo(f["repo"]), normalize_path(f["file"]))
        gt_lookup[key] = f

    # Build GT false positive key set
    gt_fp_set: set[tuple] = set()
    for fp in gt_false_positives:
        repo = fp.get("repo", "")
        file = fp.get("file", fp.get("path", ""))
        if repo and file:
            gt_fp_set.add((normalize_repo(repo), normalize_path(file)))

    # Get answer text (prefer full_answer for rich extraction)
    answer_text = (model_answer.get("full_answer") or model_answer.get("answer", "")).strip()
    if not answer_text:
        return {
            "model": model,
            "status": "empty_answer",
            "skipped": True,
            "raw_score": 0,
            "max_possible": max_possible,
            "final_pct": 0.0,
        }

    # ── Extract structured claims ────────────────────────────────────────────
    print(f"      extracting {model.split('/')[-1]}...", end=" ", flush=True)
    raw_claims = extract_model_claims(answer_text, question_text, api_key, extractor_model)
    print(f"{len(raw_claims)} claimed")

    # Deduplicate by (norm_repo, norm_path)
    seen_keys: set[tuple] = set()
    model_files: list[dict] = []
    for mf in raw_claims:
        key = (normalize_repo(mf.get("repo", "")), normalize_path(mf.get("file", "")))
        if key == ("", ""):
            continue
        if key not in seen_keys:
            seen_keys.add(key)
            model_files.append(mf)

    # ── Match model files against GT ─────────────────────────────────────────
    matched: list[dict] = []        # [{gt_file, model_file}]
    hallucinated: list[dict] = []   # model_file dicts that don't match GT

    matched_gt_keys: set[tuple] = set()
    model_file_keys: set[tuple] = set()

    for mf in model_files:
        key = (normalize_repo(mf.get("repo", "")), normalize_path(mf.get("file", "")))
        model_file_keys.add(key)

        if key in gt_lookup and key not in matched_gt_keys:
            matched.append({"gt_file": gt_lookup[key], "model_file": mf})
            matched_gt_keys.add(key)
        else:
            # Hallucination whether it's a GT false_positive or completely unknown
            hallucinated.append(mf)

    # ── LLM judge for matched files ──────────────────────────────────────────
    if matched:
        print(f"      judging {len(matched)} matched files...", end=" ", flush=True)
    judge_scores = score_matched_files(matched, gt_patterns, api_key, judge_model)
    if matched:
        print("done")

    # ── Compute per-file breakdown ───────────────────────────────────────────
    per_file_breakdown: list[dict] = []
    total_fd = total_bp = total_sev = total_fq = 0

    for item in matched:
        gt = item["gt_file"]
        key = (normalize_repo(gt["repo"]), normalize_path(gt["file"]))
        js = judge_scores.get(key, {})

        fd  = 4
        bp  = js.get("breaking_pattern", 0)
        sev = js.get("severity", 0)
        fq  = js.get("fix_quality", 0)

        total_fd  += fd
        total_bp  += bp
        total_sev += sev
        total_fq  += fq

        per_file_breakdown.append({
            "repo":    gt["repo"],
            "file":    gt["file"],
            "matched": True,
            "gt_severity":       gt.get("severity", ""),
            "gt_breaking_patterns": gt.get("breaking_patterns", []),
            "model_severity":    item["model_file"].get("severity", ""),
            "model_explanation": item["model_file"].get("breaking_explanation", ""),
            "model_fix":         item["model_file"].get("fix_suggestion", ""),
            "scores": {
                "file_detection":    fd,
                "breaking_pattern":  bp,
                "severity":          sev,
                "fix_quality":       fq,
                "total":             fd + bp + sev + fq,
            },
            "judge_notes": js.get("notes", ""),
        })

    # Missed files (in GT, not found by model)
    for gt in gt_impacted:
        key = (normalize_repo(gt["repo"]), normalize_path(gt["file"]))
        if key not in matched_gt_keys:
            per_file_breakdown.append({
                "repo":    gt["repo"],
                "file":    gt["file"],
                "matched": False,
                "gt_severity": gt.get("severity", ""),
                "gt_breaking_patterns": gt.get("breaking_patterns", []),
                "scores": {
                    "file_detection":   0,
                    "breaking_pattern": 0,
                    "severity":         0,
                    "fix_quality":      0,
                    "total":            0,
                },
                "judge_notes": "not found by model",
            })

    hallucination_penalty = len(hallucinated) * -5

    # False positive bonus: GT FP files the model correctly omitted
    fp_correctly_omitted: list[str] = []
    for fp in gt_false_positives:
        repo = fp.get("repo", "")
        file = fp.get("file", fp.get("path", ""))
        fp_key = (normalize_repo(repo), normalize_path(file))
        if fp_key not in model_file_keys:
            fp_correctly_omitted.append(f"{repo}/{file}")

    fp_bonus = len(fp_correctly_omitted) * 2

    raw_score = total_fd + total_bp + total_sev + total_fq + hallucination_penalty + fp_bonus

    # Final percentage — handle max_possible == 0 gracefully
    if max_possible > 0:
        final_pct = round(raw_score / max_possible * 100, 2)
    elif raw_score == 0:
        # No GT files and model correctly listed nothing
        final_pct = 100.0
    else:
        # Hallucinations on a "nothing breaks" question; treat 100 as baseline
        final_pct = round(100.0 + raw_score, 2)

    return {
        "model":            model,
        "status":           "scored",
        "input_tokens":     model_answer.get("input_tokens", 0),
        "output_tokens":    model_answer.get("output_tokens", 0),
        "total_tokens":     model_answer.get("total_tokens", 0),
        "cost_usd":         model_answer.get("cost_usd", 0.0),
        "tool_calls_count": model_answer.get("tool_calls_count", 0),
        "raw_score":        raw_score,
        "max_possible":     max_possible,
        "final_pct":        final_pct,
        "dimension_totals": {
            "file_detection":       total_fd,
            "breaking_pattern":     total_bp,
            "severity":             total_sev,
            "fix_quality":          total_fq,
            "hallucination_penalty": hallucination_penalty,
            "false_positive_bonus": fp_bonus,
        },
        "files_found":             len(matched),
        "files_missed":            total_impacted - len(matched),
        "files_hallucinated":      len(hallucinated),
        "fp_total":                total_fp,
        "fp_correctly_omitted":    len(fp_correctly_omitted),
        "per_file_breakdown":      per_file_breakdown,
        "hallucinated_files": [
            f"{m.get('repo', '')}/{m.get('file', '')}" for m in hallucinated
        ],
        "fp_correctly_omitted_list": fp_correctly_omitted,
    }


# ─── Question-level processing ────────────────────────────────────────────────


def process_question(
    folder: Path,
    api_key: str,
    extractor_model: str,
    judge_model: str,
    force: bool = False,
) -> dict | None:
    """Score all models in one question folder. Returns the enhanced_evaluation dict."""
    gt_data = load_ground_truth_enhanced(folder)
    if gt_data is None:
        return None

    enhanced_eval_path = folder / "enhanced_evaluation.json"
    if enhanced_eval_path.exists() and not force:
        print(f"  {folder.name}: enhanced_evaluation.json exists — skipping")
        with open(enhanced_eval_path) as f:
            return json.load(f)

    # Load question text (prefer question.json; GT may also have it)
    question_text = ""
    question_file = folder / "question.json"
    if question_file.exists():
        with open(question_file) as f:
            q_json = json.load(f)
        question_text = q_json.get("question", "")

    # GT question field as fallback
    if not question_text:
        question_text = gt_data.get("question", "")

    # Patch GT question for downstream use
    if question_text and not gt_data.get("question"):
        gt_data["question"] = question_text

    gt_impacted = gt_data.get("impacted_files", [])
    gt_fp       = gt_data.get("false_positives", [])
    max_possible = len(gt_impacted) * 10 + len(gt_fp) * 2

    q_id = (gt_data.get("id") or gt_data.get("question_id")
            or folder.name.replace("question_", ""))

    print(f"  {folder.name}: GT={len(gt_impacted)} files, FP={len(gt_fp)}, max={max_possible}")

    answers = load_model_answers(folder)

    # Also score the original ground_truth.json as a pseudo-model so we can
    # measure how accurate the oracle answer itself was vs the enhanced GT.
    gt_oracle = load_ground_truth_as_answer(folder)
    if gt_oracle:
        answers.append(gt_oracle)

    active = [a for a in answers if a.get("status") == "success"]

    if not active:
        print(f"    no successful model answers — skipping")
        return None

    model_results: list[dict] = []
    for ma in active:
        print(f"    [{ma['model'].split('/')[-1]}]")
        result = score_model_answer(
            gt_data, question_text, ma, api_key, extractor_model, judge_model,
        )
        model_results.append(result)

    output = {
        "question_id": q_id,
        "question":    question_text[:200],
        "gt_stats": {
            "total_impacted_files":  len(gt_impacted),
            "total_false_positives": len(gt_fp),
            "max_possible_score":    max_possible,
            "repos_affected":        (gt_data.get("impact_summary") or {}).get("repos_affected", []),
            "by_pattern":            (gt_data.get("impact_summary") or {}).get("by_pattern", {}),
            "by_severity":           (gt_data.get("impact_summary") or {}).get("by_severity", {}),
        },
        "model_scores": model_results,
    }

    with open(enhanced_eval_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"    → written {enhanced_eval_path.name}")
    return output


# ─── Aggregation ──────────────────────────────────────────────────────────────


def aggregate_summary(
    results_dir: Path,
    question_folders: list[Path],
    judge_model: str,
    extractor_model: str,
) -> dict:
    """Build enhanced_analysis_summary.json from per-question enhanced_evaluation files."""

    model_agg: dict[str, dict] = defaultdict(lambda: {
        "scores":            [],
        "raw_scores":        [],
        "max_scores":        [],
        "input_tokens":      0,
        "output_tokens":     0,
        "total_tokens":      0,
        "cost_usd":          0.0,
        "files_found":       0,
        "files_missed":      0,
        "files_hallucinated": 0,
        "fp_correctly_omitted": 0,
        "dim": defaultdict(float),
    })

    per_question: list[dict] = []

    for folder in question_folders:
        ef = folder / "enhanced_evaluation.json"
        if not ef.exists():
            continue
        with open(ef) as f:
            data = json.load(f)

        q_id    = data.get("question_id", folder.name)
        q_text  = data.get("question", "")
        gt_stats = data.get("gt_stats", {})

        row: dict = {
            "question_id": q_id,
            "question":    q_text[:120],
            "gt_stats":    gt_stats,
            "models":      {},
        }

        for ms in data.get("model_scores", []):
            model = ms.get("model", "")
            if ms.get("skipped"):
                continue

            row["models"][model] = {
                "final_pct":          ms.get("final_pct", 0.0),
                "raw_score":          ms.get("raw_score", 0),
                "max_possible":       ms.get("max_possible", 0),
                "files_found":        ms.get("files_found", 0),
                "files_missed":       ms.get("files_missed", 0),
                "files_hallucinated": ms.get("files_hallucinated", 0),
                "fp_correctly_omitted": ms.get("fp_correctly_omitted", 0),
                "cost_usd":           ms.get("cost_usd", 0.0),
                "dimension_totals":   ms.get("dimension_totals", {}),
            }

            agg = model_agg[model]
            agg["scores"].append(ms.get("final_pct", 0.0))
            agg["raw_scores"].append(ms.get("raw_score", 0))
            agg["max_scores"].append(ms.get("max_possible", 0))
            agg["input_tokens"]       += ms.get("input_tokens", 0)
            agg["output_tokens"]      += ms.get("output_tokens", 0)
            agg["total_tokens"]       += ms.get("total_tokens", 0)
            agg["cost_usd"]           += ms.get("cost_usd", 0.0)
            agg["files_found"]        += ms.get("files_found", 0)
            agg["files_missed"]       += ms.get("files_missed", 0)
            agg["files_hallucinated"] += ms.get("files_hallucinated", 0)
            agg["fp_correctly_omitted"] += ms.get("fp_correctly_omitted", 0)
            for dim, val in ms.get("dimension_totals", {}).items():
                agg["dim"][dim] += val

        per_question.append(row)

    model_summaries: list[dict] = []
    for model, agg in sorted(model_agg.items()):
        scores    = agg["scores"]
        avg_pct   = round(sum(scores) / len(scores), 2) if scores else 0.0
        total_raw = sum(agg["raw_scores"])
        total_max = sum(agg["max_scores"])
        # Weighted percentage: aggregate raw/max across all questions
        weighted_pct = round(total_raw / total_max * 100, 2) if total_max > 0 else avg_pct
        total_cost   = round(agg["cost_usd"], 4)
        pct_per_dollar = round(avg_pct / total_cost, 2) if total_cost > 0 else 0.0

        model_summaries.append({
            "model":               model,
            "avg_final_pct":       avg_pct,
            "weighted_pct":        weighted_pct,
            "questions_scored":    len(scores),
            "total_files_found":   agg["files_found"],
            "total_files_missed":  agg["files_missed"],
            "total_files_hallucinated": agg["files_hallucinated"],
            "total_fp_correctly_omitted": agg["fp_correctly_omitted"],
            "dimension_totals":    dict(agg["dim"]),
            "input_tokens":        agg["input_tokens"],
            "output_tokens":       agg["output_tokens"],
            "total_tokens":        agg["total_tokens"],
            "total_cost_usd":      total_cost,
            "pct_per_dollar":      pct_per_dollar,
        })

    model_summaries.sort(key=lambda m: m["weighted_pct"], reverse=True)

    return {
        "scoring_version":  "enhanced_v1",
        "judge_model":      judge_model,
        "extractor_model":  extractor_model,
        "scoring":          "fact-based marking scheme (evaluation.md)",
        "dimensions": {
            "file_detection":        "4 marks — automated binary",
            "breaking_pattern":      "0-2 marks — LLM judge",
            "severity":              "0-1 marks — LLM judge",
            "fix_quality":           "0-3 marks — LLM judge",
            "hallucination_penalty": "-5 marks each — automated",
            "false_positive_bonus":  "+2 marks each — automated",
        },
        "total_questions_scored": len(per_question),
        "model_summaries":        model_summaries,
        "per_question":           per_question,
    }


# ─── Main ─────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Enhanced evaluation using ground_truth_enhanced.json (fact-based marking)")
    parser.add_argument("--results-dir", "-r", required=True,
                        help="Path to results folder (e.g. results/KubeCluster45)")
    parser.add_argument("--force", "-f", action="store_true",
                        help="Force re-evaluation even if enhanced_evaluation.json exists")
    parser.add_argument("--questions", "-n", type=str, default=None,
                        help="Comma-separated question IDs to run (e.g. MIXED_TC001,OBS_TC019)")
    parser.add_argument("--workers", "-w", type=int, default=1,
                        help="Number of parallel workers for question processing (default: 1)")
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    if not results_dir.exists():
        print(f"Error: results directory not found: {results_dir}")
        sys.exit(1)

    load_dotenv()

    # Load model config from models.json (avoid importing evals.py to stay Python 3.9 compat)
    models_json = BASE_DIR / "models.json"
    if models_json.exists():
        with open(models_json) as f:
            models_cfg = json.load(f)
    else:
        models_cfg = {}
    judge_model     = models_cfg.get("judge_model", "qwen/qwen3-next-80b-a3b-instruct:free")
    extractor_model = models_cfg.get("smoke_test_model", "qwen/qwen3-coder:free")

    api_key = os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        print("Error: OPENROUTER_API_KEY not set in .env — cannot run enhanced evaluation")
        sys.exit(1)

    print(f"Judge model:     {judge_model}")
    print(f"Extractor model: {extractor_model}")
    print()

    # Discover question folders
    question_folders = sorted([
        d for d in results_dir.iterdir()
        if d.is_dir() and d.name.startswith("question_")
    ])

    if args.questions:
        requested = {q.strip() for q in args.questions.split(",")}
        question_folders = [
            f for f in question_folders
            if f.name.replace("question_", "") in requested
        ]
        missing = requested - {f.name.replace("question_", "") for f in question_folders}
        if missing:
            print(f"Warning: question IDs not found: {', '.join(sorted(missing))}")

    # Filter to only folders with an enhanced ground truth
    enhanced_folders = [
        f for f in question_folders
        if (f / "ground_truth_enhanced.json").exists()
    ]

    print(
        f"Found {len(enhanced_folders)}/{len(question_folders)} question folders "
        f"with ground_truth_enhanced.json\n"
    )
    if not enhanced_folders:
        print("No enhanced ground truth files found. Nothing to evaluate.")
        sys.exit(0)

    def _process_one(folder: Path) -> dict | None:
        return process_question(folder, api_key, extractor_model, judge_model, args.force)

    if args.workers > 1:
        n = min(args.workers, len(enhanced_folders))
        print(f"Processing {len(enhanced_folders)} questions with {n} workers...\n")
        with ThreadPoolExecutor(max_workers=n) as pool:
            futures = {pool.submit(_process_one, f): f.name for f in enhanced_folders}
            for future in as_completed(futures):
                future.result()  # surface exceptions
    else:
        for folder in enhanced_folders:
            _process_one(folder)

    # Aggregate and write summary
    summary = aggregate_summary(results_dir, enhanced_folders, judge_model, extractor_model)
    summary_path = results_dir / "enhanced_analysis_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nEnhanced analysis summary → {summary_path}")

    # Print leaderboard
    model_summaries = summary.get("model_summaries", [])
    if model_summaries:
        hdr = f"{'Model':<45} | {'Avg%':>7} | {'Wgt%':>7} | {'Found':>6} | {'Halluc':>6} | {'Cost$':>10}"
        sep = f"{'-'*45}-+-{'-'*7}-+-{'-'*7}-+-{'-'*6}-+-{'-'*6}-+-{'-'*10}"
        print(f"\n{hdr}")
        print(sep)
        for ms in model_summaries:
            print(
                f"{ms['model']:<45} | {ms['avg_final_pct']:>6.1f}% | "
                f"{ms['weighted_pct']:>6.1f}% | {ms['total_files_found']:>6} | "
                f"{ms['total_files_hallucinated']:>6} | ${ms['total_cost_usd']:>9.4f}"
            )

    n_scored = summary.get("total_questions_scored", len(enhanced_folders))
    print(f"\nDone — enhanced evaluation of {n_scored} questions complete.")


if __name__ == "__main__":
    main()
