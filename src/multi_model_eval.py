"""
Multi-model evaluation — runs every question against every model in models.json.

For each model, batches all questions through --threads concurrent workers,
tracks per-question results, and produces a side-by-side comparison.

Usage:
    python src/multi_model_eval.py \
        --questions cross_repo_whole.json \
        --mcp-config mcp_config.json

    # Only run specific models:
    python src/multi_model_eval.py \
        --questions cross_repo_whole.json \
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
                    load_models_config, get_model_pricing)


class PaymentError(Exception):
    """Raised on 402 Payment Required — stop immediately, no retries."""
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("multi_model_eval")


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
                     timeout: int = 120, max_retries: int = MAX_RETRIES) -> dict:
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
                      on_result: "callable | None" = None) -> list[dict]:
    """Run all questions for a single model using a continuous thread pool.

    Threads that finish early immediately pick up the next pending question
    instead of waiting for the rest of a batch to complete.

    Args:
        on_result: Optional callback(result_dict) called as each question completes.
    """
    all_results: list[dict] = []
    total = len(questions)

    with ThreadPoolExecutor(max_workers=threads) as pool:
        futures = {}
        for idx, q in enumerate(questions):
            tid = idx % threads
            futures[pool.submit(run_one_question, tid, q, mcp_url,
                                api_key, model, max_steps, timeout)] = (idx, q)

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


# ─── Per-question saving ─────────────────────────────────────────────────────

def save_model_results(output_dir: Path, questions: list[dict],
                       model_id: str, results: list[dict]):
    """Save one model's results into per-question directories immediately."""
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_model = model_id.replace("/", "_").replace(":", "_")

    for q_idx, question in enumerate(questions):
        q_id = question.get("id", q_idx + 1)
        q_dir = output_dir / f"question_{q_id}"
        q_dir.mkdir(parents=True, exist_ok=True)

        # Save question info (idempotent — overwrites if already exists)
        q_info = {
            "id": q_id,
            "question": question.get("question", ""),
            "expected_answer": question.get("answer", ""),
            "expected_files": question.get("files", []),
            "repo": question.get("repo", ""),
        }
        with open(q_dir / "question.json", "w") as f:
            json.dump(q_info, f, indent=2, default=str)

        # Find this question's result
        model_result = None
        for r in results:
            if r.get("question_id") == q_id:
                model_result = r
                break

        if model_result is None:
            continue

        model_output = {
            "model": model_id,
            "answer": model_result.get("answer", ""),
            "cost": {
                "input_tokens": model_result.get("input_tokens", 0),
                "output_tokens": model_result.get("output_tokens", 0),
                "total_tokens": model_result.get("total_tokens", 0),
                "cost_usd": model_result.get("cost_usd", 0.0),
            },
            "status": model_result.get("status", ""),
            "latency_seconds": model_result.get("latency_seconds", 0),
            "tool_calls_count": model_result.get("tool_calls_count", 0),
            "agent_steps": model_result.get("agent_steps", 0),
            "tool_calls": model_result.get("tool_calls", []),
            "error": model_result.get("error", ""),
        }
        with open(q_dir / f"{safe_model}.json", "w") as f:
            json.dump(model_output, f, indent=2, default=str)

    logger.info(f"  Saved {model_id} results to {output_dir}/")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Multi-model evaluation — run all questions against all models")
    parser.add_argument("--questions", "-q", required=True,
                        help="Path to questions JSON file")
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
    parser.add_argument("--num-questions", "-n", type=int, default=None,
                        help="Number of questions to run (default: all)")
    parser.add_argument("--output-dir", "-o", default="results",
                        help="Output directory for per-question results (default: results)")
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

    # Load questions
    qpath = Path(args.questions)
    if not qpath.exists():
        logger.error(f"Questions file not found: {qpath}")
        sys.exit(1)

    with open(qpath) as f:
        raw = json.load(f)

    if isinstance(raw, list):
        questions = raw
    elif isinstance(raw, dict):
        if "test_cases" in raw:
            questions = []
            for tc in raw["test_cases"]:
                sc = tc.get("source_change", {})
                questions.append({
                    "id": tc.get("id", ""),
                    "question": sc.get("description", sc.get("specific_change", "")),
                })
            logger.info(f"Loaded cross-repo format: {len(questions)} test cases")
        else:
            questions = raw.get("questions", raw.get("data", [raw]))

    if not questions:
        logger.error("No questions found in the file")
        sys.exit(1)

    if args.num_questions is not None:
        questions = questions[:args.num_questions]

    # Load MCP URL
    with open(Path(args.mcp_config)) as f:
        mcp_config = json.load(f)
    mcp_url = list(mcp_config.get("mcpServers", {}).values())[0]["url"]

    if args.seed is not None:
        random.seed(args.seed)

    # ── Banner ──
    logger.info("=" * 60)
    logger.info("MULTI-MODEL EVALUATION")
    logger.info("=" * 60)
    logger.info(f"  Models:          {len(model_ids)}")
    for mid in model_ids:
        inp, out = get_model_pricing(mid)
        logger.info(f"    - {mid}  (${inp}/M in, ${out}/M out)")
    logger.info(f"  Questions:       {len(questions)}")
    logger.info(f"  Threads:         {args.threads}")
    logger.info(f"  Max steps:       {args.max_steps}")
    logger.info(f"  Timeout:         {args.timeout}s")
    logger.info(f"  MCP endpoint:    {mcp_url.split('?')[0]}")
    logger.info("=" * 60)

    # ── Run one model (used as thread target) ──
    def _run_model(model_id: str) -> tuple[str, list[dict], dict]:
        """Run all questions for one model, save results, return summary."""
        logger.info(f"  [{model_id}] Starting...")
        safe_model = model_id.replace("/", "_").replace(":", "_")
        out_dir = Path(args.output_dir)

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
                        logger.info(f"  [{model_id}] Skipping q={q_id} (cached success)")
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
                q_dir = out_dir / f"question_{q_id}"
                q_dir.mkdir(parents=True, exist_ok=True)
                model_output = {
                    "model": model_id,
                    "answer": result.get("answer", ""),
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
                                                args.timeout, on_result=_save_one)
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
            # Also save question.json for each pending question
            for q in pending_questions:
                q_id = q.get("id", "?")
                q_dir = out_dir / f"question_{q_id}"
                q_dir.mkdir(parents=True, exist_ok=True)
                q_info = {
                    "id": q_id,
                    "question": q.get("question", ""),
                    "expected_answer": q.get("answer", ""),
                    "expected_files": q.get("files", []),
                    "repo": q.get("repo", ""),
                }
                with open(q_dir / "question.json", "w") as wf:
                    json.dump(q_info, wf, indent=2, default=str)
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
                save_model_results(Path(args.output_dir), questions, mid, error_results)

    total_elapsed = round(time.perf_counter() - test_start, 1)

    # ── Comparison Table ──
    logger.info("")
    logger.info("=" * 60)
    logger.info("COMPARISON TABLE")
    logger.info("=" * 60)

    header = (f"  {'Model':<35} | {'OK':>4} | {'Err':>4} | "
              f"{'Avg Lat':>8} | {'Tokens':>10} | {'Cost':>10} | {'Time':>7}")
    sep = (f"  {'-'*35}-+-{'-'*4}-+-{'-'*4}-+-"
           f"{'-'*8}-+-{'-'*10}-+-{'-'*10}-+-{'-'*7}")
    logger.info(header)
    logger.info(sep)

    grand_cost = 0.0
    grand_tokens = 0
    for mid in model_ids:
        s = model_summaries[mid]
        grand_cost += s["total_cost"]
        grand_tokens += s["total_tokens"]
        model_short = mid if len(mid) <= 35 else mid[:32] + "..."
        logger.info(
            f"  {model_short:<35} | {s['success']:>4} | {s['errors']:>4} | "
            f"{s['avg_latency']:>7.2f}s | {s['total_tokens']:>10} | "
            f"${s['total_cost']:>9.4f} | {s['total_time']:>6.1f}s"
        )

    logger.info(sep)
    logger.info(f"  {'TOTAL':<35} | {'':>4} | {'':>4} | "
                f"{'':>8} | {grand_tokens:>10} | "
                f"${grand_cost:>9.4f} | {total_elapsed:>6.1f}s")
    logger.info("=" * 60)

    # ── Save summary JSON ──
    results_dir = Path(args.output_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    run_ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_path = results_dir / f"{run_ts}-multi_model_eval.json"

    output = {
        "multi_model_eval": True,
        "questions_file": args.questions,
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
