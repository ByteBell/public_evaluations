"""
LLM + MCP smoke test — auto-discovers the maximum number of concurrent
threads the LLM can handle, then answers ALL questions at that concurrency.

Phase 1 (Discovery): starts at 3 threads, bumps +1 each round.
    Each thread picks a random question, calls the LLM agent, and reports.
    If any thread errors (LLM timeout / refusal / crash), discovery stops.
Phase 2 (Answer All): runs every question from the file through the
    max safe thread count, batching them in parallel groups.

If --max-duration is not set the test runs until every question is answered.
Supports both flat question arrays and cross_repo_whole.json format.

Usage:
    python src/smoke_test.py \
        --questions cross_repo_whole.json \
        --mcp-config mcp_config.json

    # With a time cap:
    python src/smoke_test.py \
        --questions cross_repo_whole.json \
        --mcp-config mcp_config.json \
        --max-duration 300
"""

import argparse
import json
import os
import random
import sys
import threading
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

import psutil

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evals import MCPClient, LLMClient, run_agent, estimate_cost, load_models_config
from mcp_stress import find_server_pid, ServerMonitor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("smoke_test")


# ─── Worker ──────────────────────────────────────────────────────────────────

def run_one_question(thread_id: int, question: dict, mcp_url: str,
                     api_key: str, model: str, max_steps: int,
                     timeout: int = 120) -> dict:
    """Run a single random question through the LLM agent. Returns a result dict."""
    q_id = question.get("id", "?")
    q_text = question.get("question", "")
    logger.info(f"  [T{thread_id}] Starting q={q_id}: {q_text[:80]}...")

    mcp = MCPClient(mcp_url, timeout=timeout)
    mcp.initialize()
    llm = LLMClient(api_key, model)

    t0 = time.perf_counter()
    try:
        answer, tool_records, steps, inp_tok, out_tok = run_agent(
            llm, mcp, q_text, max_steps=max_steps, verbose=False,
        )
        elapsed = round(time.perf_counter() - t0, 2)
        cost = estimate_cost(model, inp_tok, out_tok)

        logger.info(f"  [T{thread_id}] Done q={q_id} | {elapsed}s | "
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
    except Exception as e:
        elapsed = round(time.perf_counter() - t0, 2)
        logger.error(f"  [T{thread_id}] FAILED q={q_id} | {elapsed}s | {type(e).__name__}: {e}")
        return {
            "thread": thread_id,
            "question_id": q_id,
            "question_text": q_text,
            "status": "error",
            "latency_seconds": elapsed,
            "error": f"{type(e).__name__}: {e}",
        }


def run_round(num_threads: int, questions: list[dict], mcp_url: str,
              api_key: str, model: str, max_steps: int,
              timeout: int = 120) -> list[dict]:
    """Run num_threads in parallel, each with a random question."""
    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=num_threads) as pool:
        futures = {}
        for tid in range(num_threads):
            q = random.choice(questions)
            futures[pool.submit(run_one_question, tid, q, mcp_url,
                                api_key, model, max_steps, timeout)] = tid
        for future in as_completed(futures):
            tid = futures[future]
            try:
                results.append(future.result())
            except Exception as e:
                logger.error(f"  [T{tid}] Unhandled: {e}")
                results.append({
                    "thread": tid, "status": "error",
                    "latency_seconds": 0,
                    "error": f"{type(e).__name__}: {e}",
                })
    return results


def run_batch(batch: list[dict], mcp_url: str, api_key: str, model: str,
              max_steps: int, timeout: int = 120) -> list[dict]:
    """Run a specific list of questions in parallel (one thread per question)."""
    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=len(batch)) as pool:
        futures = {}
        for tid, q in enumerate(batch):
            futures[pool.submit(run_one_question, tid, q, mcp_url,
                                api_key, model, max_steps, timeout)] = tid
        for future in as_completed(futures):
            tid = futures[future]
            try:
                results.append(future.result())
            except Exception as e:
                logger.error(f"  [T{tid}] Unhandled: {e}")
                results.append({
                    "thread": tid, "status": "error",
                    "latency_seconds": 0,
                    "error": f"{type(e).__name__}: {e}",
                })
    return results


# ─── Reporting helpers ────────────────────────────────────────────────────────

def _print_per_thread(results: list[dict]):
    """Log a per-thread summary row for each thread in the results."""
    header = (f"  {'Thread':>8} | {'Status':>8} | {'Latency':>8} | "
              f"{'Tokens':>8} | {'Tools':>6} | {'Cost':>8} | Question")
    sep = (f"  {'-'*8}-+-{'-'*8}-+-{'-'*8}-+-"
           f"{'-'*8}-+-{'-'*6}-+-{'-'*8}-+-{'-'*30}")
    logger.info(header)
    logger.info(sep)

    for r in sorted(results, key=lambda x: x.get("thread", 0)):
        tid = r.get("thread", "?")
        status = r.get("status", "?")
        lat = r.get("latency_seconds", 0)
        tokens = r.get("total_tokens", 0)
        tools = r.get("tool_calls_count", 0)
        cost = r.get("cost_usd", 0)
        q_text = r.get("question_text", r.get("question_id", "?"))
        q_short = (q_text[:28] + "..") if len(str(q_text)) > 30 else q_text
        err = r.get("error", "")

        if status == "success":
            logger.info(f"  {'T'+str(tid):>8} | {'OK':>8} | {lat:>7.2f}s | "
                         f"{tokens:>8} | {tools:>6} | ${cost:>7.4f} | {q_short}")
        else:
            logger.info(f"  {'T'+str(tid):>8} | {'FAIL':>8} | {lat:>7.2f}s | "
                         f"{'--':>8} | {'--':>6} | {'--':>8} | {q_short}")
            logger.info(f"           Error: {err[:80]}")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="LLM smoke test — auto-discover max concurrent threads")
    parser.add_argument("--questions", "-q", required=True,
                        help="Path to questions JSON file")
    parser.add_argument("--mcp-config", "-m", required=True,
                        help="Path to MCP config JSON file")
    parser.add_argument("--start-threads", type=int, default=3,
                        help="Initial thread count (default: 3)")
    parser.add_argument("--thread-step", type=int, default=1,
                        help="Threads to add each round (default: 1)")
    parser.add_argument("--max-duration", type=float, default=None,
                        help="Hard time limit in seconds. If not set, runs until ALL questions are answered")
    parser.add_argument("--model", default=None,
                        help="OpenRouter model name (default: smoke_test_model from models.json)")
    parser.add_argument("--api-key", default=None,
                        help="OpenRouter API key")
    parser.add_argument("--max-steps", type=int, default=25,
                        help="Max agent steps per question (default: 25)")
    parser.add_argument("--timeout", type=int, default=120,
                        help="Read timeout per MCP call in seconds (default: 120)")
    parser.add_argument("--server-mem-limit", type=int, default=4000,
                        help="Max server RSS in MB; stops test if exceeded (default: 4000)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducibility")
    args = parser.parse_args()

    load_dotenv()

    api_key = args.api_key or os.getenv("OPENROUTER_API_KEY", "")
    models_cfg = load_models_config()
    model = args.model or models_cfg.get("smoke_test_model", "deepseek/deepseek-chat-v3.1")

    if not api_key:
        logger.error("No API key. Set OPENROUTER_API_KEY or use --api-key")
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

    # Load MCP URL
    with open(Path(args.mcp_config)) as f:
        mcp_config = json.load(f)
    mcp_url = list(mcp_config.get("mcpServers", {}).values())[0]["url"]

    if args.seed is not None:
        random.seed(args.seed)

    # ── Find & monitor server process ──
    from urllib.parse import urlparse
    parsed = urlparse(mcp_url)
    port = parsed.port or 80
    server_pid = find_server_pid(port)
    monitor = None

    if server_pid:
        proc = psutil.Process(server_pid)
        baseline_rss = round(proc.memory_info().rss / 1024 / 1024, 1)
        monitor = ServerMonitor(server_pid, interval=1.0,
                                mem_limit_mb=args.server_mem_limit)
        monitor.start()
    else:
        baseline_rss = 0

    has_time_limit = args.max_duration is not None
    global_deadline = (time.perf_counter() + args.max_duration) if has_time_limit else None
    test_start = time.perf_counter()

    logger.info("=" * 60)
    logger.info("LLM SMOKE TEST — auto thread discovery")
    logger.info("=" * 60)
    logger.info(f"  Model:           {model}")
    logger.info(f"  Questions:       {len(questions)} total (ALL will be answered)")
    logger.info(f"  Max duration:    {f'{args.max_duration}s' if has_time_limit else 'unlimited'}")
    logger.info(f"  MCP timeout:     {args.timeout}s")
    logger.info(f"  Mem limit:       {args.server_mem_limit} MB")
    if server_pid:
        logger.info(f"  Server PID:      {server_pid} (baseline RSS: {baseline_rss} MB)")
    else:
        logger.info(f"  Server PID:      not found (mem monitoring disabled)")
    logger.info(f"  Start threads:   {args.start_threads}")
    logger.info(f"  Thread step:     +{args.thread_step}")
    logger.info(f"  Max agent steps: {args.max_steps}")
    logger.info(f"  MCP endpoint:    {mcp_url.split('?')[0]}")
    logger.info("=" * 60)

    # ── PHASE 1: DISCOVERY ────────────────────────────────────────────────
    logger.info("")
    logger.info("PHASE 1: DISCOVERY — ramping up threads until LLM stops responding")
    logger.info("-" * 60)

    safe_threads = 0
    current_threads = args.start_threads
    discovery_results: dict[int, list[dict]] = {}
    round_num = 0

    while True:
        if global_deadline is not None:
            remaining = global_deadline - time.perf_counter()
            if remaining <= 0:
                logger.info("")
                logger.info("  !! MAX DURATION reached — stopping discovery")
                break
            time_str = f"~{remaining:.0f}s remaining"
        else:
            time_str = "no time limit"

        round_num += 1
        if monitor:
            monitor.reset_for_round()
        logger.info("")
        rss_now = monitor.current_rss() if monitor else 0
        logger.info(f">> Round {round_num}: {current_threads} threads, "
                     f"1 random question each ({time_str}) "
                     f"[RSS: {rss_now} MB]")

        t0 = time.perf_counter()
        results = run_round(current_threads, questions, mcp_url,
                            api_key, model, args.max_steps, args.timeout)
        elapsed = round(time.perf_counter() - t0, 2)
        discovery_results[current_threads] = results

        ok_count = sum(1 for r in results if r["status"] == "success")
        err_count = sum(1 for r in results if r["status"] == "error")
        peak_rss = monitor.peak_rss() if monitor else 0
        mem_breached = monitor.breached.is_set() if monitor else False

        logger.info(f"  Round completed in {elapsed}s — {ok_count} ok / {err_count} errors "
                     f"| Peak RSS: {peak_rss} MB")
        _print_per_thread(results)

        if mem_breached:
            logger.info("")
            logger.info(f"  !! MEMORY LIMIT BREACHED ({peak_rss} MB > {args.server_mem_limit} MB)")
            logger.info(f"     {current_threads} threads is too many.")
            break

        if err_count > 0:
            logger.info("")
            logger.info(f"  !! LLM FAILED at {current_threads} threads — "
                         f"{err_count} thread(s) did not get a response")
            logger.info(f"     Ceiling found. Max safe = {safe_threads}")
            break

        safe_threads = current_threads
        logger.info(f"  OK — all {current_threads} threads completed successfully")
        current_threads += args.thread_step

    logger.info("")
    logger.info("-" * 60)

    if safe_threads == 0:
        logger.error(f"Even {args.start_threads} threads failed. "
                     "The LLM may be down or rate-limited.")
        logger.info("")
        logger.info("DISCOVERY ROUNDS SUMMARY:")
        _print_discovery_table(discovery_results, safe_threads)
        sys.exit(1)

    logger.info(f"DISCOVERY COMPLETE: max safe threads = {safe_threads}")
    logger.info("-" * 60)

    # ── PHASE 2: ANSWER ALL QUESTIONS ───────────────────────────────────
    # Batch all questions through the safe thread count
    if global_deadline is not None and (global_deadline - time.perf_counter()) <= 0:
        logger.info("")
        logger.info("PHASE 2: SKIPPED — no time remaining (max duration exhausted)")
        soak_all_results: list[dict] = []
        soak_elapsed = 0.0
    else:
        # Build batches of safe_threads questions each
        all_questions = list(questions)
        random.shuffle(all_questions)
        batches = [all_questions[i:i + safe_threads]
                   for i in range(0, len(all_questions), safe_threads)]

        logger.info("")
        logger.info(f"PHASE 2: ANSWERING ALL {len(all_questions)} QUESTIONS "
                     f"({len(batches)} batches of up to {safe_threads} threads)")
        logger.info("-" * 60)

        time.sleep(2)  # let things settle
        if monitor:
            monitor.reset_for_round()
        soak_start = time.perf_counter()
        soak_all_results: list[dict] = []
        soak_failed = False
        answered = 0

        for batch_num, batch in enumerate(batches, 1):
            if global_deadline is not None and (global_deadline - time.perf_counter()) <= 0:
                logger.info(f"  !! MAX DURATION reached — stopping at batch {batch_num}")
                break

            rss_now = monitor.current_rss() if monitor else 0
            elapsed_so_far = round(time.perf_counter() - test_start, 0)
            if global_deadline is not None:
                time_str = f"{global_deadline - time.perf_counter():.0f}s left"
            else:
                time_str = f"{elapsed_so_far:.0f}s elapsed"
            logger.info(f"  Batch {batch_num}/{len(batches)} — "
                         f"{len(batch)} questions ({time_str}) "
                         f"[RSS: {rss_now} MB]")

            results = run_batch(batch, mcp_url, api_key, model,
                                args.max_steps, args.timeout)
            soak_all_results.extend(results)

            ok_count = sum(1 for r in results if r["status"] == "success")
            err_count = sum(1 for r in results if r["status"] == "error")
            answered += len(results)

            if monitor and monitor.breached.is_set():
                logger.info(f"  !! MEMORY LIMIT BREACHED "
                             f"({monitor.peak_rss()} MB > {args.server_mem_limit} MB)")
                _print_per_thread(results)
                soak_failed = True
                break

            if err_count > 0:
                logger.info(f"  !! {err_count} ERRORS in batch {batch_num}")
                _print_per_thread(results)
                soak_failed = True
                break

            logger.info(f"    {ok_count} ok | "
                         f"Progress: {answered}/{len(all_questions)} questions done")

        soak_elapsed = round(time.perf_counter() - soak_start, 2)
        logger.info("")
        logger.info(f"  Phase 2 completed: {answered}/{len(all_questions)} questions "
                     f"answered in {soak_elapsed}s")

    # ── Stop monitor & collect stats ──
    server_stats = monitor.stop() if monitor else {}
    mem_breached = monitor.breached.is_set() if monitor else False

    # ── REPORT ────────────────────────────────────────────────────────────
    soak_ok = [r for r in soak_all_results if r.get("status") == "success"]
    soak_errs = [r for r in soak_all_results if r.get("status") == "error"]
    soak_latencies = [r["latency_seconds"] for r in soak_ok]
    total_elapsed = round(time.perf_counter() - test_start, 1)

    # Aggregate cost
    all_results_flat = []
    for res_list in discovery_results.values():
        all_results_flat.extend(res_list)
    all_results_flat.extend(soak_all_results)
    total_cost = round(sum(r.get("cost_usd", 0) for r in all_results_flat), 4)
    total_tokens = sum(r.get("total_tokens", 0) for r in all_results_flat)

    logger.info("")
    logger.info("=" * 60)
    total_questions = len(questions)
    answered_count = len(soak_ok)

    if mem_breached:
        logger.info("RESULT: UNSTABLE — server memory limit breached!")
    elif soak_errs:
        logger.info("RESULT: UNSTABLE — LLM errors during answering")
    elif answered_count == 0 and total_elapsed > 0:
        logger.info("RESULT: DISCOVERY ONLY (no time to answer questions)")
    elif answered_count < total_questions:
        logger.info(f"RESULT: PARTIAL — {answered_count}/{total_questions} questions answered")
    else:
        logger.info(f"RESULT: COMPLETE — all {total_questions} questions answered")
    logger.info("=" * 60)

    time_limit_str = f"{args.max_duration}s" if has_time_limit else "unlimited"
    logger.info(f"  Total time:        {total_elapsed}s (limit: {time_limit_str})")
    logger.info(f"  Model:             {model}")
    logger.info(f"  Max safe threads:  {safe_threads}")
    logger.info(f"  Discovery rounds:  {len(discovery_results)}")
    logger.info(f"  Questions total:   {total_questions}")
    logger.info(f"  Questions answered:{answered_count} ({len(soak_errs)} errors)")
    logger.info(f"  Phase 2 duration:  {soak_elapsed}s")

    if soak_latencies:
        avg = round(sum(soak_latencies) / len(soak_latencies), 2)
        soak_sorted = sorted(soak_latencies)
        p50 = round(soak_sorted[len(soak_sorted) // 2], 2)
        p99 = round(soak_sorted[min(int(len(soak_sorted) * 0.99), len(soak_sorted) - 1)], 2)
        logger.info(f"  Soak avg latency:  {avg}s")
        logger.info(f"  Soak p50 latency:  {p50}s")
        logger.info(f"  Soak p99 latency:  {p99}s")
        logger.info(f"  Soak min latency:  {round(min(soak_latencies), 2)}s")
        logger.info(f"  Soak max latency:  {round(max(soak_latencies), 2)}s")

    logger.info(f"  Total tokens:      {total_tokens}")
    logger.info(f"  Total cost:        ${total_cost}")

    if server_stats:
        logger.info("-" * 60)
        logger.info(f"SERVER RESOURCE USAGE (PID {server_pid})")
        logger.info(f"  Mem limit:         {args.server_mem_limit} MB")
        logger.info(f"  CPU avg:           {server_stats['cpu_percent_avg']}%")
        logger.info(f"  CPU max:           {server_stats['cpu_percent_max']}%")
        logger.info(f"  RSS max:           {server_stats['rss_mb_max']} MB")
        logger.info(f"  RSS start:         {server_stats['rss_mb_start']} MB")
        logger.info(f"  RSS end:           {server_stats['rss_mb_end']} MB")
        if mem_breached:
            logger.info(f"  !! MEMORY LIMIT WAS BREACHED")

    # ── Discovery summary table ──
    logger.info("")
    _print_discovery_table(discovery_results, safe_threads)

    # ── Per-thread breakdown for each discovery round ──
    for n_threads in sorted(discovery_results.keys()):
        res = discovery_results[n_threads]
        logger.info("")
        logger.info(f"  Round {n_threads} threads — per-thread breakdown:")
        _print_per_thread(res)

    # ── Phase 2 per-thread breakdown ──
    if soak_all_results:
        logger.info("")
        logger.info("PHASE 2 PER-THREAD BREAKDOWN (all batches combined):")
        _print_per_thread(soak_all_results)

    logger.info("")
    logger.info("=" * 60)

    # ── Save results JSON ──
    run_ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_model = model.replace("/", "_").replace(":", "_")
    output_path = Path(f"{run_ts}-smoke-{safe_model}.json")

    output = {
        "smoke_test": True,
        "auto_discovery": True,
        "model": model,
        "max_safe_threads": safe_threads,
        "max_steps": args.max_steps,
        "questions_file": args.questions,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "config": {
            "start_threads": args.start_threads,
            "thread_step": args.thread_step,
            "max_duration": args.max_duration,
            "timeout": args.timeout,
            "server_mem_limit": args.server_mem_limit,
        },
        "summary": {
            "total_elapsed_seconds": total_elapsed,
            "max_safe_threads": safe_threads,
            "discovery_rounds": len(discovery_results),
            "total_questions": total_questions,
            "questions_answered": answered_count,
            "questions_errors": len(soak_errs),
            "total_tokens": total_tokens,
            "total_cost_usd": total_cost,
        },
        "discovery_results": {
            str(k): v for k, v in discovery_results.items()
        },
        "soak_results": soak_all_results,
    }

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, default=str)

    logger.info(f"Results saved to: {output_path}")

    sys.exit(1 if (soak_errs or mem_breached) else 0)


def _print_discovery_table(discovery_results: dict, safe_threads: int):
    """Print the compact discovery rounds overview table."""
    logger.info("DISCOVERY ROUNDS SUMMARY:")
    logger.info(f"  {'Threads':>8} | {'OK':>4} | {'Err':>4} | {'Avg Lat':>8} | {'Cost':>8} | Verdict")
    logger.info(f"  {'-'*8}-+-{'-'*4}-+-{'-'*4}-+-{'-'*8}-+-{'-'*8}-+-{'-'*16}")
    for n_threads in sorted(discovery_results.keys()):
        res = discovery_results[n_threads]
        ok_n = sum(1 for r in res if r["status"] == "success")
        err_n = sum(1 for r in res if r["status"] == "error")
        lats = [r["latency_seconds"] for r in res if r["status"] == "success"]
        avg_lat = round(sum(lats) / len(lats), 2) if lats else 0
        cost = round(sum(r.get("cost_usd", 0) for r in res), 4)
        verdict = "PASS" if n_threads <= safe_threads else "FAIL"
        logger.info(f"  {n_threads:>8} | {ok_n:>4} | {err_n:>4} | {avg_lat:>7.2f}s | ${cost:>7.4f} | {verdict}")


if __name__ == "__main__":
    main()
