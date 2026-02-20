"""
MCP server stress test — auto-discovers the maximum number of concurrent
threads that fit within a given RAM budget, then soaks at that level.

Phase 1 (Discovery): starts at 5 threads, increases by 5 each round
    (10 s probe per round) until the server RSS exceeds --server-mem-limit.
Phase 2 (Stability): runs the max safe thread count for 30 s to confirm
    everything executes cleanly under sustained load.

Usage:
    python src/mcp_stress.py \
        --mcp-config mcp_config.json \
        --server-mem-limit 4000 \
        --max-duration 300
"""

import argparse
import json
import subprocess
import sys
import threading
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

import psutil

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evals import MCPClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("mcp_stress")


# ─── Server Process Monitor ──────────────────────────────────────────────────

def find_server_pid(port: int) -> int | None:
    """Find the PID of the process listening on the given port via lsof."""
    try:
        out = subprocess.check_output(
            ["lsof", "-ti", f"tcp:{port}", "-sTCP:LISTEN"],
            text=True, stderr=subprocess.DEVNULL,
        ).strip()
        if out:
            return int(out.splitlines()[0])
    except (subprocess.CalledProcessError, ValueError):
        pass
    return None


class ServerMonitor:
    """Background thread that samples a process's CPU% and RSS every interval."""

    def __init__(self, pid: int, interval: float = 1.0, mem_limit_mb: int = 0):
        self.proc = psutil.Process(pid)
        self.interval = interval
        self.mem_limit_mb = mem_limit_mb
        self.samples: list[dict] = []
        self.breached = threading.Event()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self.proc.cpu_percent()  # prime so first real reading isn't 0
        self._thread.start()

    def stop(self) -> dict:
        self._stop.set()
        self._thread.join(timeout=5)
        return self._summarize()

    def reset_for_round(self):
        """Clear samples and breach flag for a new round."""
        self.samples.clear()
        self.breached.clear()

    def peak_rss(self) -> float:
        if not self.samples:
            return 0.0
        return max(s["rss_mb"] for s in self.samples)

    def current_rss(self) -> float:
        try:
            return round(self.proc.memory_info().rss / 1024 / 1024, 1)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0.0

    def _run(self):
        while not self._stop.is_set():
            try:
                mem = self.proc.memory_info()
                cpu = self.proc.cpu_percent()
                rss_mb = round(mem.rss / 1024 / 1024, 1)
                self.samples.append({
                    "ts": round(time.perf_counter(), 2),
                    "cpu_percent": cpu,
                    "rss_mb": rss_mb,
                    "vms_mb": round(mem.vms / 1024 / 1024, 1),
                })
                if self.mem_limit_mb and rss_mb > self.mem_limit_mb:
                    self.breached.set()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break
            self._stop.wait(self.interval)

    def _summarize(self) -> dict:
        if not self.samples:
            return {}
        cpus = [s["cpu_percent"] for s in self.samples]
        rss = [s["rss_mb"] for s in self.samples]
        total_ram_mb = round(psutil.virtual_memory().total / 1024 / 1024, 1)
        cpu_cores = psutil.cpu_count(logical=True)
        cpu_cores_physical = psutil.cpu_count(logical=False)
        return {
            "samples": len(self.samples),
            "cpu_cores_physical": cpu_cores_physical,
            "cpu_cores_logical": cpu_cores,
            "total_ram_mb": total_ram_mb,
            "cpu_percent_avg": round(sum(cpus) / len(cpus), 1),
            "cpu_percent_max": round(max(cpus), 1),
            "rss_mb_start": rss[0],
            "rss_mb_end": rss[-1],
            "rss_mb_max": max(rss),
            "rss_mb_min": min(rss),
        }


# ─── Stress Thread ───────────────────────────────────────────────────────────

def stress_thread(thread_id: int, mcp_url: str, query: str,
                  channels: list[str], duration: float,
                  timeout: int = 30,
                  abort_event: threading.Event | None = None) -> list[dict]:
    """Loop graph_search until duration expires or abort_event is set."""
    mcp = MCPClient(mcp_url, timeout=timeout)
    mcp.initialize()

    results = []
    deadline = time.perf_counter() + duration
    call_num = 0

    while time.perf_counter() < deadline:
        if abort_event and abort_event.is_set():
            logger.info(f"[T{thread_id}] Stopping — memory limit breached")
            break
        call_num += 1
        t0 = time.perf_counter()
        try:
            resp = mcp.call_tool("graph_search", {
                "query": query,
                "channels": channels,
            })
            elapsed = round(time.perf_counter() - t0, 3)
            results.append({
                "thread": thread_id,
                "call": call_num,
                "status": "ok",
                "latency_seconds": elapsed,
                "response_length": len(resp),
            })
            logger.info(f"[T{thread_id}] call {call_num} | {elapsed}s | {len(resp)} chars")
        except Exception as e:
            elapsed = round(time.perf_counter() - t0, 3)
            results.append({
                "thread": thread_id,
                "call": call_num,
                "status": "error",
                "latency_seconds": elapsed,
                "error": f"{type(e).__name__}: {e}",
            })
            logger.error(f"[T{thread_id}] call {call_num} | {elapsed}s | FAILED: {e}")

    return results


# ─── Run a single round ──────────────────────────────────────────────────────

def run_round(num_threads: int, duration: float, mcp_url: str,
              query: str, channels: list[str], timeout: int,
              abort_event: threading.Event) -> list[dict]:
    """Spin up num_threads and hammer the server for duration seconds."""
    all_results: list[dict] = []
    with ThreadPoolExecutor(max_workers=num_threads) as pool:
        futures = {
            pool.submit(stress_thread, tid, mcp_url, query,
                        channels, duration, timeout, abort_event): tid
            for tid in range(num_threads)
        }
        for future in as_completed(futures):
            tid = futures[future]
            try:
                all_results.extend(future.result())
            except Exception as e:
                logger.error(f"[T{tid}] Unhandled: {e}")
    return all_results


def print_round_stats(results: list[dict], elapsed: float, label: str = ""):
    """Log a compact summary for a single round."""
    ok = [r for r in results if r["status"] == "ok"]
    errs = [r for r in results if r["status"] == "error"]
    latencies = [r["latency_seconds"] for r in ok]
    avg = round(sum(latencies) / len(latencies), 3) if latencies else 0
    rps = round(len(results) / elapsed, 1) if elapsed > 0 else 0
    logger.info(f"  {label}Calls: {len(ok)} ok / {len(errs)} err | "
                f"RPS: {rps} | Avg latency: {avg}s")
    if errs:
        for r in errs[:3]:
            logger.info(f"    error sample: T{r['thread']} call {r['call']}: {r.get('error')}")
        if len(errs) > 3:
            logger.info(f"    ... and {len(errs) - 3} more errors")


def _print_per_thread(results: list[dict]):
    """Log a per-thread latency table from a list of call results."""
    by_thread: dict[int, list[dict]] = {}
    for r in results:
        by_thread.setdefault(r["thread"], []).append(r)

    header = (f"  {'Thread':>8} | {'Calls':>6} | {'OK':>4} | {'Err':>4} | "
              f"{'Avg':>7} | {'Min':>7} | {'Max':>7} | {'p50':>7} | {'p99':>7}")
    sep = (f"  {'-'*8}-+-{'-'*6}-+-{'-'*4}-+-{'-'*4}-+-"
           f"{'-'*7}-+-{'-'*7}-+-{'-'*7}-+-{'-'*7}-+-{'-'*7}")
    logger.info(header)
    logger.info(sep)

    for tid in sorted(by_thread.keys()):
        calls = by_thread[tid]
        ok = [c for c in calls if c["status"] == "ok"]
        errs = [c for c in calls if c["status"] == "error"]
        lats = sorted(c["latency_seconds"] for c in ok)
        if lats:
            avg = round(sum(lats) / len(lats), 3)
            mn = round(lats[0], 3)
            mx = round(lats[-1], 3)
            p50 = round(lats[len(lats) // 2], 3)
            p99 = round(lats[min(int(len(lats) * 0.99), len(lats) - 1)], 3)
        else:
            avg = mn = mx = p50 = p99 = 0.0
        logger.info(f"  {'T'+str(tid):>8} | {len(calls):>6} | {len(ok):>4} | {len(errs):>4} | "
                     f"{avg:>6.3f}s | {mn:>6.3f}s | {mx:>6.3f}s | {p50:>6.3f}s | {p99:>6.3f}s")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="MCP stress test — auto-discover max threads within a RAM budget")
    parser.add_argument("--mcp-config", "-m", required=True,
                        help="Path to MCP config JSON file")
    parser.add_argument("--server-mem-limit", type=int, default=4000,
                        help="Max server RSS in MB (default: 4000)")
    parser.add_argument("--start-threads", type=int, default=5,
                        help="Initial thread count (default: 5)")
    parser.add_argument("--thread-step", type=int, default=5,
                        help="Threads to add each round (default: 5)")
    parser.add_argument("--probe-duration", type=float, default=10,
                        help="Seconds per discovery probe round (default: 10)")
    parser.add_argument("--soak-duration", type=float, default=30,
                        help="Seconds for stability soak phase (default: 30)")
    parser.add_argument("--query", default="SharedInformer",
                        help="Search query string (default: SharedInformer)")
    parser.add_argument("--channels", nargs="+", default=["classes", "imports"],
                        help="Search channels (default: classes imports)")
    parser.add_argument("--timeout", type=int, default=30,
                        help="Read timeout per MCP call in seconds (default: 30)")
    parser.add_argument("--sample-interval", type=float, default=1.0,
                        help="Server monitor sample interval in seconds (default: 1.0)")
    parser.add_argument("--max-duration", type=float, default=300,
                        help="Hard time limit for the entire test in seconds (default: 300)")
    args = parser.parse_args()

    # ── Load MCP URL ──
    with open(Path(args.mcp_config)) as f:
        mcp_config = json.load(f)
    mcp_url = list(mcp_config.get("mcpServers", {}).values())[0]["url"]
    parsed = urlparse(mcp_url)
    port = parsed.port or 80

    # ── Find & monitor server process ──
    server_pid = find_server_pid(port)
    if not server_pid:
        logger.error(f"Could not find process listening on port {port}. "
                     "Make sure the MCP server is running.")
        sys.exit(1)

    proc = psutil.Process(server_pid)
    baseline_rss = round(proc.memory_info().rss / 1024 / 1024, 1)

    global_deadline = time.perf_counter() + args.max_duration

    logger.info("=" * 60)
    logger.info("MCP STRESS TEST — auto thread discovery")
    logger.info("=" * 60)
    logger.info(f"  Server PID:      {server_pid} ({proc.name()})")
    logger.info(f"  Baseline RSS:    {baseline_rss} MB")
    logger.info(f"  Memory limit:    {args.server_mem_limit} MB")
    logger.info(f"  Max duration:    {args.max_duration}s")
    logger.info(f"  Start threads:   {args.start_threads}")
    logger.info(f"  Thread step:     +{args.thread_step}")
    logger.info(f"  Probe duration:  {args.probe_duration}s per round")
    logger.info(f"  Soak duration:   {args.soak_duration}s")
    logger.info(f"  Query:           {args.query}")
    logger.info(f"  Channels:        {args.channels}")
    logger.info(f"  MCP endpoint:    {mcp_url.split('?')[0]}")
    logger.info("=" * 60)

    monitor = ServerMonitor(server_pid, interval=args.sample_interval,
                            mem_limit_mb=args.server_mem_limit)
    monitor.start()

    # ── PHASE 1: DISCOVERY ────────────────────────────────────────────────
    logger.info("")
    logger.info("PHASE 1: DISCOVERY — ramping up threads until memory limit is hit")
    logger.info("-" * 60)

    safe_threads = 0
    current_threads = args.start_threads
    discovery_results: dict[int, list[dict]] = {}
    round_num = 0

    while True:
        remaining = global_deadline - time.perf_counter()
        if remaining <= 0:
            logger.info("")
            logger.info("  !! MAX DURATION reached — stopping discovery")
            break

        round_num += 1
        probe_dur = min(args.probe_duration, remaining)
        monitor.reset_for_round()

        logger.info("")
        logger.info(f">> Round {round_num}: {current_threads} threads for {probe_dur:.0f}s "
                     f"(~{remaining:.0f}s remaining) ...")
        logger.info(f"   Server RSS before round: {monitor.current_rss()} MB")

        t0 = time.perf_counter()
        results = run_round(current_threads, probe_dur, mcp_url,
                            args.query, args.channels, args.timeout,
                            monitor.breached)
        elapsed = round(time.perf_counter() - t0, 2)

        peak_rss = monitor.peak_rss()
        rss_now = monitor.current_rss()
        ok_count = sum(1 for r in results if r["status"] == "ok")
        err_count = sum(1 for r in results if r["status"] == "error")
        discovery_results[current_threads] = results

        print_round_stats(results, elapsed)
        logger.info(f"  Peak RSS: {peak_rss} MB | Current RSS: {rss_now} MB "
                     f"| Limit: {args.server_mem_limit} MB")

        breached = monitor.breached.is_set()
        has_errors = err_count > 0

        if breached:
            logger.info(f"  !! MEMORY LIMIT BREACHED ({peak_rss} MB > {args.server_mem_limit} MB)")
            logger.info(f"     {current_threads} threads is too many.")
            break

        if has_errors:
            logger.info(f"  !! {err_count} ERRORS detected at {current_threads} threads.")
            logger.info(f"     Treating this as the ceiling.")
            break

        # Round passed
        safe_threads = current_threads
        logger.info(f"  OK — {current_threads} threads fit within limits "
                     f"({peak_rss}/{args.server_mem_limit} MB)")
        current_threads += args.thread_step

    logger.info("")
    logger.info("-" * 60)

    if safe_threads == 0:
        logger.error(f"Even {args.start_threads} threads exceeded the memory limit or errored.")
        logger.error("Try increasing --server-mem-limit or reducing --start-threads.")
        monitor.stop()
        sys.exit(1)

    logger.info(f"DISCOVERY COMPLETE: max safe threads = {safe_threads}")
    logger.info("-" * 60)

    # ── PHASE 2: STABILITY SOAK ──────────────────────────────────────────
    remaining = global_deadline - time.perf_counter()
    soak_dur = min(args.soak_duration, max(remaining - 2, 0))  # reserve 2s settle

    if soak_dur <= 0:
        logger.info("")
        logger.info("PHASE 2: SKIPPED — no time remaining (max duration exhausted)")
        logger.info(f"  Discovery used all {args.max_duration}s budget.")
        soak_results = []
        soak_elapsed = 0.0
    else:
        logger.info("")
        logger.info(f"PHASE 2: STABILITY — soaking at {safe_threads} threads "
                    f"for {soak_dur:.0f}s (~{remaining:.0f}s remaining)")
        logger.info("-" * 60)

        # Give the server a moment to settle between phases
        time.sleep(2)
        monitor.reset_for_round()

        logger.info(f"  Server RSS at soak start: {monitor.current_rss()} MB")
        logger.info(f"  Running ...")

        t0 = time.perf_counter()
        soak_abort = monitor.breached
        soak_results = run_round(safe_threads, soak_dur, mcp_url,
                                 args.query, args.channels, args.timeout,
                                 soak_abort)
        soak_elapsed = round(time.perf_counter() - t0, 2)

    soak_ok = [r for r in soak_results if r["status"] == "ok"]
    soak_errs = [r for r in soak_results if r["status"] == "error"]
    soak_latencies = [r["latency_seconds"] for r in soak_ok]
    soak_breached = monitor.breached.is_set()
    soak_peak = monitor.peak_rss()

    # ── Final server stats ──
    server_stats = monitor.stop()

    # ── REPORT ────────────────────────────────────────────────────────────
    logger.info("")
    logger.info("=" * 60)
    if soak_breached:
        logger.info("RESULT: UNSTABLE — memory limit breached during soak!")
    elif soak_errs:
        logger.info("RESULT: UNSTABLE — errors occurred during soak!")
    else:
        logger.info("RESULT: STABLE")
    logger.info("=" * 60)

    total_elapsed = round(time.perf_counter() - (global_deadline - args.max_duration), 1)
    logger.info(f"  Total time:        {total_elapsed}s / {args.max_duration}s max")
    logger.info(f"  Max safe threads:  {safe_threads}")
    logger.info(f"  Memory limit:      {args.server_mem_limit} MB")
    logger.info(f"  Soak duration:     {soak_elapsed}s")
    logger.info(f"  Soak total calls:  {len(soak_results)}")
    logger.info(f"  Soak successful:   {len(soak_ok)}")
    logger.info(f"  Soak errors:       {len(soak_errs)}")

    if soak_latencies:
        avg = round(sum(soak_latencies) / len(soak_latencies), 3)
        p50 = round(sorted(soak_latencies)[len(soak_latencies) // 2], 3)
        p99_idx = min(int(len(soak_latencies) * 0.99), len(soak_latencies) - 1)
        p99 = round(sorted(soak_latencies)[p99_idx], 3)
        rps = round(len(soak_results) / soak_elapsed, 1) if soak_elapsed > 0 else 0
        logger.info(f"  Soak RPS:          {rps}")
        logger.info(f"  Avg latency:       {avg}s")
        logger.info(f"  p50 latency:       {p50}s")
        logger.info(f"  p99 latency:       {p99}s")
        logger.info(f"  Min latency:       {round(min(soak_latencies), 3)}s")
        logger.info(f"  Max latency:       {round(max(soak_latencies), 3)}s")

    logger.info("-" * 60)

    if server_stats:
        cores_phys = server_stats['cpu_cores_physical']
        cores_log = server_stats['cpu_cores_logical']
        total_ram = server_stats['total_ram_mb']

        def ram_pct(mb):
            return round(mb / total_ram * 100, 1) if total_ram else 0

        logger.info(f"SERVER RESOURCE USAGE (PID {server_pid})")
        logger.info(f"  CPU cores:         {cores_phys} physical / {cores_log} logical")
        logger.info(f"  CPU avg:           {server_stats['cpu_percent_avg']}% "
                     f"({round(server_stats['cpu_percent_avg'] / 100 * cores_log, 2)} cores)")
        logger.info(f"  CPU max:           {server_stats['cpu_percent_max']}% "
                     f"({round(server_stats['cpu_percent_max'] / 100 * cores_log, 2)} cores)")
        logger.info(f"  System RAM:        {total_ram} MB")
        logger.info(f"  Soak peak RSS:     {soak_peak} MB ({ram_pct(soak_peak)}%)")
        logger.info(f"  Soak RSS start:    {server_stats['rss_mb_start']} MB")
        logger.info(f"  Soak RSS end:      {server_stats['rss_mb_end']} MB")
        logger.info(f"  Samples:           {server_stats['samples']}")

    logger.info("=" * 60)

    # ── Discovery summary table ──
    logger.info("")
    logger.info("DISCOVERY ROUNDS SUMMARY:")
    logger.info(f"  {'Threads':>8} | {'OK':>6} | {'Err':>5} | {'Verdict'}")
    logger.info(f"  {'-'*8}-+-{'-'*6}-+-{'-'*5}-+-{'-'*16}")
    for n_threads in sorted(discovery_results.keys()):
        res = discovery_results[n_threads]
        ok_n = sum(1 for r in res if r["status"] == "ok")
        err_n = sum(1 for r in res if r["status"] == "error")
        if n_threads <= safe_threads:
            verdict = "PASS"
        else:
            verdict = "FAIL (limit hit)"
        logger.info(f"  {n_threads:>8} | {ok_n:>6} | {err_n:>5} | {verdict}")

    # Per-thread breakdown for each discovery round
    for n_threads in sorted(discovery_results.keys()):
        res = discovery_results[n_threads]
        logger.info("")
        logger.info(f"  Round {n_threads} threads — per-thread breakdown:")
        _print_per_thread(res)
    logger.info("")

    # ── Soak per-thread breakdown ──
    if soak_results:
        logger.info("SOAK PER-THREAD BREAKDOWN:")
        _print_per_thread(soak_results)
        logger.info("")

    if soak_errs:
        logger.info("SOAK ERRORS:")
        for r in soak_errs:
            logger.info(f"  T{r['thread']} call {r['call']}: {r.get('error')}")

    failed = bool(soak_errs or soak_breached)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
