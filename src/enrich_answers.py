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


def enrich_task(task_dir):
    answer_path = os.path.join(task_dir, "answer.json")
    telemetry_dir = os.path.join(task_dir, "telemetry")

    if not os.path.exists(answer_path):
        return False, "no answer.json"

    if not os.path.exists(telemetry_dir):
        return False, "no telemetry dir"

    # Find events/metrics files
    events_file = None
    metrics_file = None
    for fname in os.listdir(telemetry_dir):
        fpath = os.path.join(telemetry_dir, fname)
        if fname.endswith("_events.json"):
            events_file = fpath
        elif fname.endswith("_metrics.json"):
            metrics_file = fpath

    if not events_file:
        return False, "no events file"

    with open(answer_path) as f:
        answer = json.load(f)

    try:
        metrics = compute_metrics(events_file, metrics_file)
    except Exception as e:
        return False, f"telemetry parse error: {e}"

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
