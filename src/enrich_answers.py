#!/usr/bin/env python3
"""
Enrich answer.json files with OTel metrics extracted from telemetry files.

Usage:
    python src/enrich_answers.py <run_dir>

Example:
    python src/enrich_answers.py results_swe_bench/auto_run_on_qwen3.6_plus_preview
"""

import json
import sys
import os
from datetime import datetime, timezone
from collections import defaultdict


def load_otel_file(path):
    with open(path) as f:
        raw = f.read().strip()
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else [data]
    except json.JSONDecodeError:
        batches = []
        for line in raw.splitlines():
            line = line.strip()
            if line:
                batches.append(json.loads(line))
        return batches


def extract_attrs(lr):
    attrs = {}
    for a in lr.get("attributes", []):
        val = a.get("value", {})
        v = val.get("stringValue", val.get("intValue", val.get("doubleValue", None)))
        attrs[a["key"]] = v
    return attrs


def extract_events(batches):
    records = []
    for batch in batches:
        data = batch.get("data", batch)
        for rl in data.get("resourceLogs", []):
            for sl in rl.get("scopeLogs", []):
                for lr in sl.get("logRecords", []):
                    attrs = extract_attrs(lr)
                    attrs["__time_unix_nano"] = lr.get("timeUnixNano", "")
                    records.append(attrs)
    records.sort(key=lambda r: int(r.get("event.sequence", 0)))
    return records


def parse_ts(ts):
    if not ts:
        return None
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def compute_metrics(events_path, metrics_path=None):
    event_batches = load_otel_file(events_path)
    records = extract_events(event_batches)

    api_reqs = [r for r in records if r.get("event.name") == "api_request"]
    tool_res = [r for r in records if r.get("event.name") == "tool_result"]

    # Totals
    total_input  = sum(int(r.get("input_tokens", 0) or 0)          for r in api_reqs)
    total_output = sum(int(r.get("output_tokens", 0) or 0)         for r in api_reqs)
    total_cr     = sum(int(r.get("cache_read_tokens", 0) or 0)     for r in api_reqs)
    total_cc     = sum(int(r.get("cache_creation_tokens", 0) or 0) for r in api_reqs)
    total_cost   = sum(float(r.get("cost_usd", 0) or 0)            for r in api_reqs)
    total_api    = len(api_reqs)
    total_tools  = len(tool_res)

    # Models used
    models = sorted({r.get("model", "") for r in api_reqs if r.get("model")})

    # Per-model breakdown
    model_stats = defaultdict(lambda: {
        "input_tokens": 0, "output_tokens": 0,
        "cache_read_tokens": 0, "cache_creation_tokens": 0,
        "cost_usd": 0.0, "api_requests": 0
    })
    for r in api_reqs:
        m = r.get("model", "unknown")
        # Normalize model name to a key (e.g. "qwen/qwen3.6-plus-preview:free" -> "qwen3_6_plus_preview")
        model_stats[m]["input_tokens"]          += int(r.get("input_tokens", 0) or 0)
        model_stats[m]["output_tokens"]         += int(r.get("output_tokens", 0) or 0)
        model_stats[m]["cache_read_tokens"]     += int(r.get("cache_read_tokens", 0) or 0)
        model_stats[m]["cache_creation_tokens"] += int(r.get("cache_creation_tokens", 0) or 0)
        model_stats[m]["cost_usd"]              += float(r.get("cost_usd", 0) or 0)
        model_stats[m]["api_requests"]          += 1

    # Timing: use first and last event timestamps across all events
    all_tss = []
    for r in records:
        ts = parse_ts(r.get("event.timestamp", ""))
        if ts:
            all_tss.append(ts)

    start_time = all_tss[0].strftime("%Y-%m-%dT%H:%M:%S.") + f"{all_tss[0].microsecond // 1000:03d}Z" if all_tss else None
    end_time   = all_tss[-1].strftime("%Y-%m-%dT%H:%M:%S.") + f"{all_tss[-1].microsecond // 1000:03d}Z" if all_tss else None
    elapsed    = round((all_tss[-1] - all_tss[0]).total_seconds(), 3) if len(all_tss) >= 2 else 0.0

    result = {
        "time_taken_seconds":         elapsed,
        "start_time":                 start_time,
        "end_time":                   end_time,
        "total_cost_usd":             round(total_cost, 5),
        "total_input_tokens":         total_input,
        "total_output_tokens":        total_output,
        "total_cache_read_tokens":    total_cr,
        "total_cache_creation_tokens": total_cc,
        "total_api_requests":         total_api,
        "total_tool_calls":           total_tools,
        "models_used":                models,
    }

    # Add per-model flat keys (using safe key names)
    for model_name, stats in model_stats.items():
        # Build a safe prefix: take the part after last "/" and before ":", replace non-alphanum with "_"
        short = model_name.split("/")[-1].split(":")[0]
        safe = "".join(c if c.isalnum() else "_" for c in short)
        result[f"{safe}_input_tokens"]          = stats["input_tokens"]
        result[f"{safe}_output_tokens"]         = stats["output_tokens"]
        result[f"{safe}_cache_read_tokens"]     = stats["cache_read_tokens"]
        result[f"{safe}_cache_creation_tokens"] = stats["cache_creation_tokens"]
        result[f"{safe}_cost_usd"]              = round(stats["cost_usd"], 5)
        result[f"{safe}_api_requests"]          = stats["api_requests"]

    return result


def compute_metrics_from_kilo_stdout(stdout_path, manifest_path=None):
    """Parse kilo's streaming JSON stdout (step_finish / tool_use events) for metrics."""
    with open(stdout_path) as f:
        lines = f.readlines()

    step_finishes = []
    tool_uses = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        t = d.get("type", "")
        if t == "step_finish":
            step_finishes.append(d)
        elif t == "tool_use":
            tool_uses.append(d)

    total_input    = sum(int(e["part"]["tokens"]["input"])             for e in step_finishes if "tokens" in e.get("part", {}))
    total_output   = sum(int(e["part"]["tokens"]["output"])            for e in step_finishes if "tokens" in e.get("part", {}))
    total_reasoning= sum(int(e["part"]["tokens"].get("reasoning", 0)) for e in step_finishes if "tokens" in e.get("part", {}))
    total_cr       = sum(int(e["part"]["tokens"]["cache"]["read"])     for e in step_finishes if "tokens" in e.get("part", {}))
    total_cc       = sum(int(e["part"]["tokens"]["cache"]["write"])    for e in step_finishes if "tokens" in e.get("part", {}))
    total_cost     = sum(float(e["part"].get("cost", 0))              for e in step_finishes)
    total_api      = len(step_finishes)
    total_tools    = len(tool_uses)

    # Timestamps are unix milliseconds
    all_ts = sorted(e["timestamp"] for e in step_finishes + tool_uses if "timestamp" in e)
    if len(all_ts) >= 2:
        elapsed = round((all_ts[-1] - all_ts[0]) / 1000.0, 3)
        def ms_to_iso(ms):
            dt = datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc)
            return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"
        start_time = ms_to_iso(all_ts[0])
        end_time   = ms_to_iso(all_ts[-1])
    else:
        elapsed, start_time, end_time = 0.0, None, None

    # Fall back to elapsed_s from run_manifest if available and we have no events
    if elapsed == 0.0 and manifest_path and os.path.exists(manifest_path):
        try:
            with open(manifest_path) as f:
                manifest = json.load(f)
            elapsed = manifest.get("elapsed_s", 0.0)
        except Exception:
            pass

    # Model from manifest
    models = []
    if manifest_path and os.path.exists(manifest_path):
        try:
            with open(manifest_path) as f:
                manifest = json.load(f)
            m = manifest.get("model", "")
            if m:
                models = [m]
        except Exception:
            pass

    result = {
        "time_taken_seconds":          elapsed,
        "start_time":                  start_time,
        "end_time":                    end_time,
        "total_cost_usd":              round(total_cost, 5),
        "total_input_tokens":          total_input,
        "total_output_tokens":         total_output,
        "total_reasoning_tokens":      total_reasoning,
        "total_cache_read_tokens":     total_cr,
        "total_cache_creation_tokens": total_cc,
        "total_api_requests":          total_api,
        "total_tool_calls":            total_tools,
        "models_used":                 models,
    }

    if models:
        model_name = models[0]
        short = model_name.split("/")[-1].split(":")[0]
        safe = "".join(c if c.isalnum() else "_" for c in short)
        result[f"{safe}_input_tokens"]          = total_input
        result[f"{safe}_output_tokens"]         = total_output
        result[f"{safe}_cache_read_tokens"]     = total_cr
        result[f"{safe}_cache_creation_tokens"] = total_cc
        result[f"{safe}_cost_usd"]              = round(total_cost, 5)
        result[f"{safe}_api_requests"]          = total_api

    return result


def enrich_task(task_dir):
    answer_path = os.path.join(task_dir, "answer.json")
    telemetry_dir = os.path.join(task_dir, "telemetry")
    manifest_path = os.path.join(task_dir, "run_manifest.json")

    if not os.path.exists(answer_path):
        return False, "no answer.json"

    if not os.path.exists(telemetry_dir):
        return False, "no telemetry dir"

    # Find events/metrics files — prefer session named in manifest, else latest mtime
    session_id = None
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path) as f:
                _m = json.load(f)
            session_id = _m.get("otel_session_id")
        except Exception:
            pass

    all_events  = [os.path.join(telemetry_dir, fn) for fn in os.listdir(telemetry_dir) if fn.endswith("_events.json")]
    all_metrics = [os.path.join(telemetry_dir, fn) for fn in os.listdir(telemetry_dir) if fn.endswith("_metrics.json")]

    events_file  = None
    metrics_file = None

    if session_id:
        # Use the session explicitly recorded in the manifest
        candidate_e = os.path.join(telemetry_dir, f"{session_id}_events.json")
        candidate_m = os.path.join(telemetry_dir, f"{session_id}_metrics.json")
        if os.path.exists(candidate_e):
            events_file  = candidate_e
        if os.path.exists(candidate_m):
            metrics_file = candidate_m

    if not events_file and all_events:
        # Fall back: pick the most-recently modified events file
        events_file  = max(all_events,  key=os.path.getmtime)
    if not metrics_file and all_metrics:
        metrics_file = max(all_metrics, key=os.path.getmtime)

    with open(answer_path) as f:
        answer = json.load(f)

    if not events_file:
        # Fallback: parse kilo streaming JSON from logs/claude_stdout.txt
        stdout_path = os.path.join(task_dir, "logs", "claude_stdout.txt")
        if not os.path.exists(stdout_path):
            return False, "no events file and no kilo stdout"
        try:
            metrics = compute_metrics_from_kilo_stdout(stdout_path, manifest_path)
        except Exception as e:
            return False, f"kilo stdout parse error: {e}"
    else:
        try:
            metrics = compute_metrics(events_file, metrics_file)
        except Exception as e:
            return False, f"telemetry parse error: {e}"

    # OTel only captures API-call spans; local tool operations (Read, Bash, Write)
    # that run after the last API call are invisible to it.  run_manifest.json records
    # the true process wall time in elapsed_s — use it whenever it exceeds the
    # OTel-derived time_taken_seconds (which measures first→last API event only).
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path) as f:
                manifest = json.load(f)
            wall_time = float(manifest.get("elapsed_s") or 0)
            if wall_time > metrics.get("time_taken_seconds", 0):
                metrics["time_taken_seconds"] = round(wall_time, 3)
        except Exception:
            pass

    # Merge: answer fields first, then metrics
    enriched = {"answer": answer.get("answer", "")}
    enriched.update(metrics)
    # Preserve any other existing fields
    for k, v in answer.items():
        if k not in enriched:
            enriched[k] = v

    with open(answer_path, "w") as f:
        json.dump(enriched, f, indent=2)
        f.write("\n")

    return True, "enriched"


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <run_dir>")
        sys.exit(1)

    run_dir = sys.argv[1]
    if not os.path.isdir(run_dir):
        print(f"Error: not a directory: {run_dir}")
        sys.exit(1)

    missing_answer = []
    results = []

    for task_name in sorted(os.listdir(run_dir)):
        task_dir = os.path.join(run_dir, task_name)
        if not os.path.isdir(task_dir):
            continue

        answer_path = os.path.join(task_dir, "answer.json")
        if not os.path.exists(answer_path):
            missing_answer.append(task_name)
            continue

        ok, msg = enrich_task(task_dir)
        results.append((task_name, ok, msg))
        status = "OK  " if ok else "FAIL"
        print(f"  [{status}] {task_name}: {msg}")

    print(f"\nDone: {sum(1 for _, ok, _ in results if ok)} enriched / {len(results)} processed")

    if missing_answer:
        print(f"\nTasks WITHOUT answer.json ({len(missing_answer)}):")
        for t in missing_answer:
            print(f"  - {t}")


if __name__ == "__main__":
    main()
