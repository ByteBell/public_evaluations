"""
MCP Context Generation — runs every question against every model in models.json.

Reads questions from a folder containing question_*/question.json files
(e.g. results/KubeCluster40/). For each model, batches all questions through
--threads concurrent workers, tracks per-question results, and produces a
side-by-side comparison.

Usage:
    python src/mcp_context_generation.py \
        --questions-dir results/KubeCluster40 \
        --mcp-config mcp_config.json

    # Only run specific models:
    python src/mcp_context_generation.py \
        --questions-dir results/KubeCluster40 \
        --mcp-config mcp_config.json \
        --models "xiaomi/mimo-v2-flash" "z-ai/glm-5"
"""

import argparse
import json
import os
import random
import sys
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evals import (MCPClient, LLMClient, run_agent, estimate_cost,
                    load_models_config, get_model_pricing, AgentTimeoutError,
                    condense_answer)


class PaymentError(Exception):
    """Raised on 402 Payment Required — stop immediately, no retries."""
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("mcp_context_generation")


# ─── Question loading ─────────────────────────────────────────────────────────

def load_questions_from_dir(questions_dir: Path) -> list[dict]:
    """Scan questions_dir for question_*/question.json and return a list of question dicts."""
    questions = []
    for q_dir in sorted(questions_dir.iterdir()):
        if not q_dir.is_dir() or not q_dir.name.startswith("question_"):
            continue
        q_file = q_dir / "question.json"
        if not q_file.exists():
            logger.warning(f"Skipping {q_dir.name} — no question.json found")
            continue
        with open(q_file) as f:
            q = json.load(f)
        questions.append(q)
    return questions


# ─── Worker ──────────────────────────────────────────────────────────────────

def _empty_result(thread_id: int, q_id: str, q_text: str,
                   status: str, elapsed: float, error: str) -> dict:
    """Return a stub result for failed/timed-out questions."""
    return {
        "thread": thread_id,
        "question_id": q_id,
        "question_text": q_text,
        "status": status,
        "latency_seconds": elapsed,
        "tool_calls_count": 0,
        "tool_calls": [],
        "agent_steps": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "cost_usd": 0.0,
        "answer": "",
        "error": error,
    }


MAX_RETRIES = 3


def run_one_question(thread_id: int, question: dict, mcp_url: str,
                     api_key: str, model: str, max_steps: int,
                     timeout: int = 120, max_retries: int = MAX_RETRIES,
                     wall_timeout: int = 600) -> dict:
    """Run a single question through the LLM agent with retries."""
    q_id = question.get("id", "?")
    q_text = question.get("question", "")

    last_error = ""
    for attempt in range(1, max_retries + 1):
        if attempt > 1:
            logger.info(f"    [T{thread_id}] [{model}] Retry {attempt}/{max_retries} q={q_id}")

        logger.info(f"    [T{thread_id}] [{model}] q={q_id}: {q_text[:60]}...")

        t0 = time.perf_counter()
        try:
            mcp = MCPClient(mcp_url, timeout=timeout)
            mcp.initialize()
            llm = LLMClient(api_key, model)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            if "402" in str(e):
                raise PaymentError(f"402 Payment Required for model {model}: {e}")
            elapsed = round(time.perf_counter() - t0, 2)
            last_error = f"Init failed: {type(e).__name__}: {e}"
            logger.error(f"    [T{thread_id}] [{model}] INIT FAILED q={q_id} | attempt {attempt} | {elapsed}s | {last_error}")
            time.sleep(min(attempt * 2, 10))
            continue

        try:
            answer, tool_records, steps, inp_tok, out_tok = run_agent(
                llm, mcp, q_text, max_steps=max_steps, verbose=False,
                wall_timeout=wall_timeout,
            )
            elapsed = round(time.perf_counter() - t0, 2)
            cost = estimate_cost(model, inp_tok, out_tok)

            logger.info(f"    [T{thread_id}] [{model}] Done q={q_id} | {elapsed}s | "
                         f"{len(tool_records)} tools | ${cost}")
            return {
                "thread": thread_id,
                "question_id": q_id,
                "question_text": q_text,
                "status": "success",
                "latency_seconds": elapsed,
                "tool_calls_count": len(tool_records),
                "tool_calls": [asdict(tc) for tc in tool_records],
                "agent_steps": steps,
                "input_tokens": inp_tok,
                "output_tokens": out_tok,
                "total_tokens": inp_tok + out_tok,
                "cost_usd": cost,
                "answer": answer,
            }
        except KeyboardInterrupt:
            raise
        except AgentTimeoutError as e:
            elapsed = round(time.perf_counter() - t0, 2)
            last_error = f"AgentTimeoutError: {e}"
            logger.error(f"    [T{thread_id}] [{model}] WALL TIMEOUT q={q_id} | {elapsed}s | {last_error}")
            # Don't retry wall timeouts — they'll just timeout again
            return _empty_result(thread_id, q_id, q_text, "timeout", elapsed, last_error)
        except Exception as e:
            if "402" in str(e):
                raise PaymentError(f"402 Payment Required for model {model}: {e}")
            elapsed = round(time.perf_counter() - t0, 2)
            last_error = f"{type(e).__name__}: {e}"
            logger.error(f"    [T{thread_id}] [{model}] FAILED q={q_id} | attempt {attempt} | {elapsed}s | {last_error}")
            time.sleep(min(attempt * 2, 10))
            continue

    # All retries exhausted
    status = "timeout" if "timeout" in last_error.lower() or "timed out" in last_error.lower() else "error"
    logger.error(f"    [T{thread_id}] [{model}] GAVE UP q={q_id} after {max_retries} attempts")
    return _empty_result(thread_id, q_id, q_text, status, 0,
                         f"Failed after {max_retries} retries: {last_error}")


def run_all_questions(questions: list[dict], mcp_url: str, api_key: str,
                      model: str, max_steps: int, threads: int,
                      timeout: int,
                      on_result: "callable | None" = None,
                      wall_timeout: int = 600) -> list[dict]:
    """Run all questions for a single model using a continuous thread pool.

    Threads that finish early immediately pick up the next pending question
    instead of waiting for the rest of a batch to complete.

    Args:
        on_result: Optional callback(result_dict) called as each question completes.
        wall_timeout: Max wall-clock seconds per question's agent loop (default 600).
    """
    all_results: list[dict] = []
    total = len(questions)

    with ThreadPoolExecutor(max_workers=threads) as pool:
        futures = {}
        for idx, q in enumerate(questions):
            tid = idx % threads
            futures[pool.submit(run_one_question, tid, q, mcp_url,
                                api_key, model, max_steps, timeout,
                                wall_timeout=wall_timeout)] = (idx, q)

        for future in as_completed(futures):
            idx, q = futures[future]
            try:
                result = future.result()
            except PaymentError as e:
                logger.error(f"    PAYMENT ERROR — stopping model: {e}")
                # Cancel all remaining futures
                for f in futures:
                    f.cancel()
                raise
            except KeyboardInterrupt:
                raise
            except Exception as e:
                q_id = q.get("id", "?")
                q_text = q.get("question", "")
                logger.error(f"    [Q{idx}] Unhandled q={q_id}: {e}")
                result = _empty_result(
                    idx % threads, q_id, q_text, "error", 0,
                    f"Unhandled: {type(e).__name__}: {e}",
                )

            all_results.append(result)
            if on_result:
                on_result(result)

            ok = sum(1 for r in all_results if r["status"] == "success")
            err = sum(1 for r in all_results if r["status"] != "success")
            logger.info(f"    Progress: {ok + err}/{total} "
                         f"({ok} ok, {err} errors)")

    return all_results


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="MCP Context Generation — run all questions against all models. "
                    "Reads questions from question_*/question.json folders.")
    parser.add_argument("--questions-dir", "-q", required=True,
                        help="Path to folder containing question_*/question.json files "
                             "(e.g. results/KubeCluster40)")
    parser.add_argument("--mcp-config", "-m", required=True,
                        help="Path to MCP config JSON file")
    parser.add_argument("--models", nargs="+", default=None,
                        help="Specific model(s) to run (default: all from models.json)")
    parser.add_argument("--threads", "-t", type=int, default=3,
                        help="Concurrent threads per model (default: 3)")
    parser.add_argument("--max-steps", type=int, default=25,
                        help="Max agent steps per question (default: 25)")
    parser.add_argument("--timeout", type=int, default=120,
                        help="Read timeout per MCP call in seconds (default: 120)")
    parser.add_argument("--api-key", default=None,
                        help="OpenRouter API key")
    parser.add_argument("--questions", "-n", type=str, default=None,
                        help="Comma-separated question IDs to run (e.g. OBS_TC001,OBS_TC002). Default: all")
    parser.add_argument("--wall-timeout", type=int, default=600,
                        help="Max wall-clock seconds per question agent loop (default: 600)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducibility")
    args = parser.parse_args()

    load_dotenv()

    api_key = args.api_key or os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        logger.error("No API key. Set OPENROUTER_API_KEY or use --api-key")
        sys.exit(1)

    # Load models config
    models_cfg = load_models_config()
    all_models = models_cfg.get("models", {})
    smoke_model = models_cfg.get("smoke_test_model", "xiaomi/mimo-v2-flash")

    if args.models:
        model_ids = args.models
        # Warn about unknown models
        for mid in model_ids:
            if mid not in all_models:
                logger.warning(f"Model '{mid}' not in models.json — cost will be $0.00")
    else:
        model_ids = list(all_models.keys())

    if not model_ids:
        logger.error("No models to evaluate. Add models to models.json or use --models")
        sys.exit(1)

    # Load questions from directory
    questions_dir = Path(args.questions_dir)
    if not questions_dir.is_dir():
        logger.error(f"Questions directory not found: {questions_dir}")
        sys.exit(1)

    questions = load_questions_from_dir(questions_dir)

    if not questions:
        logger.error(f"No question_*/question.json files found in {questions_dir}")
        sys.exit(1)

    if args.questions is not None:
        requested_ids = {qid.strip() for qid in args.questions.split(",")}
        questions = [q for q in questions if q.get("id", "") in requested_ids]
        missing = requested_ids - {q.get("id", "") for q in questions}
        if missing:
            logger.warning(f"Question IDs not found: {', '.join(sorted(missing))}")

    # Output goes to the same questions directory
    output_dir = questions_dir

    # Load MCP URL
    with open(Path(args.mcp_config)) as f:
        mcp_config = json.load(f)
    mcp_url = list(mcp_config.get("mcpServers", {}).values())[0]["url"]

    if args.seed is not None:
        random.seed(args.seed)

    # ── Banner ──
    logger.info("=" * 60)
    logger.info("MCP CONTEXT GENERATION")
    logger.info("=" * 60)
    logger.info(f"  Models:          {len(model_ids)}")
    for mid in model_ids:
        inp, out = get_model_pricing(mid)
        logger.info(f"    - {mid}  (${inp}/M in, ${out}/M out)")
    if args.questions:
        logger.info(f"  Questions:       {len(questions)} (filtered: {args.questions})")
    else:
        logger.info(f"  Questions:       {len(questions)}")
    logger.info(f"  Questions dir:   {questions_dir}")
    logger.info(f"  Threads:         {args.threads}")
    logger.info(f"  Max steps:       {args.max_steps}")
    logger.info(f"  Timeout:         {args.timeout}s")
    logger.info(f"  Wall timeout:    {args.wall_timeout}s")
    logger.info(f"  Condenser:       {smoke_model}")
    logger.info(f"  MCP endpoint:    {mcp_url.split('?')[0]}")
    logger.info("=" * 60)

    # ── Run one model (used as thread target) ──
    def _run_model(model_id: str) -> tuple[str, list[dict], dict]:
        """Run all questions for one model, save results, return summary."""
        logger.info(f"  [{model_id}] Starting...")
        safe_model = model_id.replace("/", "_").replace(":", "_")
        out_dir = output_dir

        # Split questions into cached (already have results) and pending
        pending_questions: list[dict] = []
        cached_results: list[dict] = []
        for q in questions:
            q_id = q.get("id", "?")
            result_file = out_dir / f"question_{q_id}" / f"{safe_model}.json"
            if result_file.exists():
                try:
                    with open(result_file) as rf:
                        cached = json.load(rf)
                    # Only cache successful results — retry errors/blanks
                    if cached.get("status") == "success" and cached.get("answer", "").strip():
                        # Backfill llm_condensed_answer if missing
                        if not cached.get("llm_condensed_answer"):
                            q_text = q.get("question", "")
                            logger.info(f"  [{model_id}] Condensing cached q={q_id}...")
                            cached["llm_condensed_answer"] = condense_answer(
                                cached["answer"], q_text, api_key,
                                model=smoke_model,
                            )
                            with open(result_file, "w") as wf:
                                json.dump(cached, wf, indent=2, default=str)
                        else:
                            logger.info(f"  [{model_id}] Skipping q={q_id} (cached + condensed)")

                        cached_results.append({
                            "thread": 0,
                            "question_id": q_id,
                            "question_text": q.get("question", ""),
                            "status": cached.get("status", "success"),
                            "latency_seconds": cached.get("latency_seconds", 0),
                            "tool_calls_count": cached.get("tool_calls_count", 0),
                            "tool_calls": cached.get("tool_calls", []),
                            "agent_steps": cached.get("agent_steps", 0),
                            "input_tokens": cached.get("cost", {}).get("input_tokens", 0),
                            "output_tokens": cached.get("cost", {}).get("output_tokens", 0),
                            "total_tokens": cached.get("cost", {}).get("total_tokens", 0),
                            "cost_usd": cached.get("cost", {}).get("cost_usd", 0.0),
                            "answer": cached.get("answer", ""),
                        })
                    else:
                        logger.info(f"  [{model_id}] Retrying q={q_id} (previous status: {cached.get('status', '?')})")
                        result_file.unlink()
                        pending_questions.append(q)
                except Exception:
                    pending_questions.append(q)
            else:
                pending_questions.append(q)

        if not pending_questions:
            logger.info(f"  [{model_id}] All {len(questions)} questions already cached — skipping")
            results = cached_results
        else:
            logger.info(f"  [{model_id}] {len(cached_results)} cached, "
                        f"{len(pending_questions)} pending")

            # Save each result to disk as soon as it completes
            def _save_one(result: dict):
                q_id = result.get("question_id", "?")
                q_text = result.get("question_text", "")
                q_dir = out_dir / f"question_{q_id}"
                q_dir.mkdir(parents=True, exist_ok=True)

                full_answer = result.get("answer", "")
                condensed = ""
                if full_answer.strip() and result.get("status") == "success":
                    logger.info(f"    [{model_id}] Condensing q={q_id}...")
                    condensed = condense_answer(
                        full_answer, q_text, api_key,
                        model=smoke_model,
                    )

                model_output = {
                    "model": model_id,
                    "answer": full_answer,
                    "llm_condensed_answer": condensed,
                    "cost": {
                        "input_tokens": result.get("input_tokens", 0),
                        "output_tokens": result.get("output_tokens", 0),
                        "total_tokens": result.get("total_tokens", 0),
                        "cost_usd": result.get("cost_usd", 0.0),
                    },
                    "status": result.get("status", ""),
                    "latency_seconds": result.get("latency_seconds", 0),
                    "tool_calls_count": result.get("tool_calls_count", 0),
                    "agent_steps": result.get("agent_steps", 0),
                    "tool_calls": result.get("tool_calls", []),
                    "error": result.get("error", ""),
                }
                with open(q_dir / f"{safe_model}.json", "w") as wf:
                    json.dump(model_output, wf, indent=2, default=str)

            m_start = time.perf_counter()
            try:
                new_results = run_all_questions(pending_questions, mcp_url, api_key,
                                                model_id, args.max_steps, args.threads,
                                                args.timeout, on_result=_save_one,
                                                wall_timeout=args.wall_timeout)
            except PaymentError as e:
                logger.error(f"  [{model_id}] 402 PAYMENT ERROR — skipping remaining questions: {e}")
                new_results = []
            except KeyboardInterrupt:
                raise
            except Exception as e:
                logger.error(f"  [{model_id}] MODEL FAILED: {type(e).__name__}: {e}")
                new_results = [
                    _empty_result(0, q.get("id", "?"), q.get("question", ""),
                                  "error", 0, f"Model-level failure: {type(e).__name__}: {e}")
                    for q in pending_questions
                ]
            results = cached_results + new_results

        if pending_questions:
            m_elapsed = round(time.perf_counter() - m_start, 2)
        else:
            m_elapsed = 0.0

        ok = [r for r in results if r.get("status") == "success"]
        errs = [r for r in results if r.get("status") != "success"]
        lats = [r["latency_seconds"] for r in ok]
        avg_lat = round(sum(lats) / len(lats), 2) if lats else 0
        total_tok = sum(r.get("total_tokens", 0) for r in results)
        total_cost = round(sum(r.get("cost_usd", 0) for r in results), 4)

        summary = {
            "total_time": m_elapsed,
            "questions": len(results),
            "success": len(ok),
            "errors": len(errs),
            "avg_latency": avg_lat,
            "total_tokens": total_tok,
            "total_cost": total_cost,
        }

        logger.info(f"  [{model_id}] Done: {len(ok)}/{len(results)} ok | "
                     f"{m_elapsed}s | avg {avg_lat}s | "
                     f"{total_tok} tokens | ${total_cost}")
        if errs:
            for r in errs[:3]:
                logger.info(f"    [{model_id}] q={r.get('question_id','?')}: {r.get('error','')[:80]}")
            if len(errs) > 3:
                logger.info(f"    [{model_id}] ... and {len(errs) - 3} more errors")

        return model_id, results, summary

    # ── Run ALL models in parallel ──
    test_start = time.perf_counter()
    model_summaries: dict[str, dict] = {}
    model_results: dict[str, list[dict]] = {}

    logger.info(f"\nLaunching {len(model_ids)} models in parallel...")
    with ThreadPoolExecutor(max_workers=len(model_ids)) as pool:
        futures = {pool.submit(_run_model, mid): mid for mid in model_ids}
        for future in as_completed(futures):
            mid = futures[future]
            try:
                model_id, results, summary = future.result()
                model_results[model_id] = results
                model_summaries[model_id] = summary
            except KeyboardInterrupt:
                raise
            except Exception as e:
                logger.error(f"  [{mid}] Unhandled: {type(e).__name__}: {e}")
                error_results = [
                    _empty_result(0, q.get("id", "?"), q.get("question", ""),
                                  "error", 0, f"Unhandled: {type(e).__name__}: {e}")
                    for q in questions
                ]
                model_results[mid] = error_results
                model_summaries[mid] = {
                    "total_time": 0, "questions": len(questions),
                    "success": 0, "errors": len(questions),
                    "avg_latency": 0, "total_tokens": 0, "total_cost": 0,
                }

    total_elapsed = round(time.perf_counter() - test_start, 1)

    # ── Load existing judge scores from analysis.json files ──
    from collections import defaultdict
    score_agg: dict[str, dict] = defaultdict(lambda: {"scores": [], "hallucinations": 0, "judged": 0})
    for qfolder in sorted(output_dir.iterdir()):
        if not qfolder.is_dir() or not qfolder.name.startswith("question_"):
            continue
        af = qfolder / "analysis.json"
        if not af.exists():
            continue
        try:
            with open(af) as _f:
                adata = json.load(_f)
            for ms in adata.get("model_scores", []):
                model = ms.get("model", "")
                sc = ms.get("score", 0)
                just = (ms.get("justification", "") or "").lower()
                agg = score_agg[model]
                agg["judged"] += 1
                if sc > 0:
                    agg["scores"].append(sc)
                # Count hallucination mentions in justification
                if any(w in just for w in ("hallucin", "irrelevant", "incorrect", "wrong", "fabricat")):
                    agg["hallucinations"] += 1
        except Exception:
            pass

    # ── Comparison Table ──
    logger.info("")
    logger.info("=" * 80)
    logger.info("COMPARISON TABLE")
    logger.info("=" * 80)

    header = (f"  {'Model':<35} | {'OK':>4} | {'Err':>4} | "
              f"{'Avg Lat':>8} | {'Tokens':>10} | {'Cost':>10} | "
              f"{'Score':>6} | {'Halluc':>6} | {'Time':>7}")
    sep = (f"  {'-'*35}-+-{'-'*4}-+-{'-'*4}-+-"
           f"{'-'*8}-+-{'-'*10}-+-{'-'*10}-+-"
           f"{'-'*6}-+-{'-'*6}-+-{'-'*7}")
    logger.info(header)
    logger.info(sep)

    grand_cost = 0.0
    grand_tokens = 0
    for mid in model_ids:
        s = model_summaries[mid]
        grand_cost += s["total_cost"]
        grand_tokens += s["total_tokens"]
        model_short = mid if len(mid) <= 35 else mid[:32] + "..."
        # Judge scores
        sa = score_agg.get(mid, {"scores": [], "hallucinations": 0, "judged": 0})
        avg_score = round(sum(sa["scores"]) / len(sa["scores"]), 4) if sa["scores"] else 0
        halluc = sa["hallucinations"]
        score_str = f"{avg_score:.4f}" if sa["judged"] > 0 else "  n/a "
        halluc_str = f"{halluc:>6}" if sa["judged"] > 0 else "  n/a "
        logger.info(
            f"  {model_short:<35} | {s['success']:>4} | {s['errors']:>4} | "
            f"{s['avg_latency']:>7.2f}s | {s['total_tokens']:>10} | "
            f"${s['total_cost']:>9.4f} | {score_str} | {halluc_str} | {s['total_time']:>6.1f}s"
        )

    logger.info(sep)
    logger.info(f"  {'TOTAL':<35} | {'':>4} | {'':>4} | "
                f"{'':>8} | {grand_tokens:>10} | "
                f"${grand_cost:>9.4f} | {'':>6} | {'':>6} | {total_elapsed:>6.1f}s")
    logger.info("=" * 80)

    # ── Save summary JSON ──
    output_dir.mkdir(parents=True, exist_ok=True)
    run_ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"{run_ts}-mcp_context_generation.json"

    output = {
        "mcp_context_generation": True,
        "questions_dir": str(questions_dir),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "config": {
            "threads": args.threads,
            "max_steps": args.max_steps,
            "timeout": args.timeout,
        },
        "summary": {
            "total_elapsed_seconds": total_elapsed,
            "total_questions": len(questions),
            "total_models": len(model_ids),
            "grand_total_tokens": grand_tokens,
            "grand_total_cost_usd": round(grand_cost, 4),
        },
        "model_summaries": model_summaries,
        "model_results": model_results,
    }

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, default=str)

    logger.info(f"Summary saved to: {output_path}")

    any_errors = any(s["errors"] > 0 for s in model_summaries.values())
    sys.exit(1 if any_errors else 0)


if __name__ == "__main__":
    main()
