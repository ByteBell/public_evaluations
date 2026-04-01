#!/usr/bin/env python3
"""
Visualize a Claude Code OTel session.

Usage:
    python visualize_session.py <events_file> [metrics_file] [--verbose]

Supports both .json (single object or array) and .jsonl (one JSON per line).

Flags:
    --verbose   Show all attributes, full prompt text, raw tool inputs/outputs,
                resource metadata, batch structure, metrics raw dump, and
                a cumulative token/cost chart.
"""

import json
import sys
import os
import textwrap
from datetime import datetime
from collections import Counter

# ── ANSI colours ────────────────────────────────────────────────────────────
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
ITALIC  = "\033[3m"
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
BLUE    = "\033[94m"
MAGENTA = "\033[95m"
CYAN    = "\033[96m"
WHITE   = "\033[97m"
ORANGE  = "\033[33m"

EVENT_COLORS = {
    "user_prompt":   CYAN,
    "api_request":   GREEN,
    "tool_decision": YELLOW,
    "tool_result":   BLUE,
    "api_error":     RED,
}

# ── Helpers ──────────────────────────────────────────────────────────────────

def color(text, c): return f"{c}{text}{RESET}"
def bold(text):     return f"{BOLD}{text}{RESET}"
def dim(text):      return f"{DIM}{text}{RESET}"
def italic(text):   return f"{ITALIC}{text}{RESET}"

def fmt_bytes(b):
    b = int(b)
    if b < 1024:    return f"{b} B"
    if b < 1024**2: return f"{b/1024:.1f} KB"
    return f"{b/1024**2:.2f} MB"

def fmt_ms(ms):
    ms = int(ms)
    if ms < 1000: return f"{ms}ms"
    return f"{ms/1000:.2f}s"

def fmt_tokens(n):
    n = int(n)
    return f"{n:,}" if n >= 1000 else str(n)

def parse_ts(ts):
    if not ts: return None
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))

def elapsed(t1, t2):
    if t1 and t2:
        return f"+{(t2-t1).total_seconds():.3f}s"
    return ""

def wrap_text(text, width=100, indent="        "):
    """Wrap long text with indent."""
    lines = []
    for para in str(text).split("\n"):
        if len(para) <= width:
            lines.append(indent + para)
        else:
            wrapped = textwrap.wrap(para, width=width)
            lines.extend(indent + w for w in wrapped)
    return "\n".join(lines)

# ── File loading ─────────────────────────────────────────────────────────────

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
    for batch_idx, batch in enumerate(batches):
        data = batch.get("data", batch)
        for rl in data.get("resourceLogs", []):
            resource_attrs = extract_attrs(rl.get("resource", {}))
            for sl in rl.get("scopeLogs", []):
                scope = sl.get("scope", {})
                for lr in sl.get("logRecords", []):
                    attrs = extract_attrs(lr)
                    attrs["__batch_idx"]      = batch_idx
                    attrs["__resource_attrs"] = resource_attrs
                    attrs["__scope_name"]     = scope.get("name", "")
                    attrs["__scope_version"]  = scope.get("version", "")
                    attrs["__time_unix_nano"] = lr.get("timeUnixNano", "")
                    attrs["__observed_nano"]  = lr.get("observedTimeUnixNano", "")
                    attrs["__body"]           = lr.get("body", {}).get("stringValue", "")
                    attrs["__severity"]       = lr.get("severityText", "")
                    records.append(attrs)
    records.sort(key=lambda r: int(r.get("event.sequence", 0)))
    return records

def extract_metrics(batches):
    points = []
    for batch in batches:
        data = batch.get("data", batch)
        for rm in data.get("resourceMetrics", []):
            for sm in rm.get("scopeMetrics", []):
                for metric in sm.get("metrics", []):
                    name = metric.get("name", "")
                    desc = metric.get("description", "")
                    unit = metric.get("unit", "")
                    container = metric.get("sum", metric.get("gauge", {}))
                    is_monotonic = container.get("isMonotonic", None)
                    agg_temp = container.get("aggregationTemporality", "")
                    for d in container.get("dataPoints", []):
                        mattrs = {}
                        for a in d.get("attributes", []):
                            val = a.get("value", {})
                            v = val.get("stringValue", val.get("intValue", val.get("doubleValue", "")))
                            mattrs[a["key"]] = v
                        val = d.get("asInt", d.get("asDouble", 0))
                        t   = d.get("timeUnixNano", 0)
                        st  = d.get("startTimeUnixNano", 0)
                        points.append({
                            "name": name, "desc": desc, "unit": unit,
                            "type_attr": mattrs.get("type", ""),
                            "attrs": mattrs, "value": val,
                            "time_nano": t, "start_nano": st,
                            "monotonic": is_monotonic, "agg": agg_temp,
                        })
    return points

# ── Event rendering ───────────────────────────────────────────────────────────

PERSONAL_KEYS = {"user.id","user.email","user.account_uuid","user.account_id",
                 "organization.id","session.id","app.version","terminal.type",
                 "prompt.id"}
META_KEYS     = {"event.name","event.timestamp","event.sequence",
                 "__batch_idx","__resource_attrs","__scope_name","__scope_version",
                 "__time_unix_nano","__observed_nano","__body","__severity"}

def render_event(attrs, prev_ts, first_ts, verbose=False):
    name    = attrs.get("event.name", "unknown")
    ts_str  = attrs.get("event.timestamp", "")
    seq     = attrs.get("event.sequence", "?")
    ts      = parse_ts(ts_str)
    c       = EVENT_COLORS.get(name, WHITE)

    abs_time = ts_str[11:23] if len(ts_str) >= 23 else ts_str
    rel_time = elapsed(first_ts, ts) if first_ts else ""
    delta    = elapsed(prev_ts, ts)  if prev_ts  else ""

    header = (
        f"{bold(color(f'[{seq:>3}]', c))}  "
        f"{dim(abs_time)}  "
        f"{dim(f'({rel_time:>9})')}"
        + (f"  {dim(f'Δ{delta}'):>14}" if verbose and delta else "")
        + f"  {color(bold(name), c)}"
    )

    lines = [header]

    # ── Verbose: internal metadata ───────────────────────────────────────────
    if verbose:
        batch_idx     = attrs.get("__batch_idx", "?")
        scope_name    = attrs.get("__scope_name", "")
        scope_ver     = attrs.get("__scope_version", "")
        time_nano     = attrs.get("__time_unix_nano", "")
        observed_nano = attrs.get("__observed_nano", "")
        body          = attrs.get("__body", "")
        severity      = attrs.get("__severity", "")
        lines.append(dim(f"      ┌─ OTel metadata"))
        lines.append(dim(f"      │  batch_idx        : {batch_idx}"))
        if scope_name:    lines.append(dim(f"      │  scope.name       : {scope_name}  v{scope_ver}"))
        if time_nano:     lines.append(dim(f"      │  timeUnixNano     : {time_nano}"))
        if observed_nano: lines.append(dim(f"      │  observedUnixNano : {observed_nano}"))
        if body:          lines.append(dim(f"      │  body             : {body}"))
        if severity:      lines.append(dim(f"      │  severity         : {severity}"))
        lines.append(dim(f"      └─"))

    # ── Event-specific fields ────────────────────────────────────────────────
    if name == "user_prompt":
        pl     = attrs.get("prompt_length", "?")
        prompt = attrs.get("prompt", "")
        lines.append(f"      prompt_length : {fmt_tokens(pl)} chars")
        if verbose and prompt:
            lines.append(f"      {bold('prompt text')}:")
            lines.append(color(wrap_text(prompt, width=110), CYAN))

    elif name == "api_request":
        model   = attrs.get("model", "?")
        inp     = int(attrs.get("input_tokens", 0) or 0)
        out     = int(attrs.get("output_tokens", 0) or 0)
        cache_r = int(attrs.get("cache_read_tokens", 0) or 0)
        cache_c = int(attrs.get("cache_creation_tokens", 0) or 0)
        cost    = float(attrs.get("cost_usd", 0) or 0)
        dur     = int(attrs.get("duration_ms", 0) or 0)
        speed   = attrs.get("speed", "")

        lines.append(f"      model         : {bold(model)}")
        lines.append(
            f"      tokens        : in={color(fmt_tokens(inp), CYAN)}  "
            f"out={color(fmt_tokens(out), GREEN)}  "
            f"cache_read={color(fmt_tokens(cache_r), MAGENTA)}  "
            f"cache_create={color(fmt_tokens(cache_c), YELLOW)}"
        )
        lines.append(
            f"      cost / time   : {color(f'${cost:.6f}', GREEN)}  "
            f"dur={color(fmt_ms(dur), YELLOW)}  speed={speed}"
        )
        if verbose:
            # Efficiency ratios
            total_ctx = inp + cache_r + cache_c
            cache_pct = (cache_r / total_ctx * 100) if total_ctx else 0
            tok_per_s = (out / (dur / 1000)) if dur else 0
            lines.append(
                f"      efficiency    : cache_hit={color(f'{cache_pct:.1f}%', MAGENTA)}  "
                f"output_speed={color(f'{tok_per_s:.1f} tok/s', YELLOW)}  "
                f"total_ctx_tokens={color(fmt_tokens(total_ctx), CYAN)}"
            )
            # Show ALL remaining attributes
            shown = {"model","input_tokens","output_tokens","cache_read_tokens",
                     "cache_creation_tokens","cost_usd","duration_ms","speed"}
            extra = {k: v for k, v in attrs.items()
                     if k not in shown and k not in PERSONAL_KEYS and k not in META_KEYS}
            if extra:
                lines.append(f"      {dim('extra attrs')}  :")
                for k, v in extra.items():
                    lines.append(f"        {dim(k):<30} {v}")

    elif name == "tool_decision":
        tool     = attrs.get("tool_name", "?")
        decision = attrs.get("decision", "?")
        source   = attrs.get("source", "?")
        lines.append(f"      tool          : {bold(tool)}")
        lines.append(f"      decision      : {decision}  (source: {source})")
        if verbose:
            shown = {"tool_name","decision","source"}
            extra = {k: v for k, v in attrs.items()
                     if k not in shown and k not in PERSONAL_KEYS and k not in META_KEYS}
            if extra:
                lines.append(f"      {dim('extra attrs')}  :")
                for k, v in extra.items():
                    lines.append(f"        {dim(k):<30} {v}")

    elif name == "tool_result":
        tool      = attrs.get("tool_name", "?")
        success   = attrs.get("success", "?")
        dur       = int(attrs.get("duration_ms", 0) or 0)
        size      = int(attrs.get("tool_result_size_bytes", 0) or 0)
        mcp_scope = attrs.get("mcp_server_scope", "")
        raw_input = attrs.get("tool_input", "")
        raw_params= attrs.get("tool_parameters", "")

        ok_str = color("✓ success", GREEN) if str(success) == "true" else color("✗ failed", RED)
        lines.append(f"      tool          : {bold(tool)}  {ok_str}")
        lines.append(f"      result_size   : {fmt_bytes(size)}  dur={fmt_ms(dur)}"
                     + (f"  scope={mcp_scope}" if mcp_scope else ""))

        # MCP server/tool name from parameters
        if raw_params and verbose:
            try:
                p = json.loads(raw_params) if isinstance(raw_params, str) else raw_params
                if isinstance(p, dict):
                    mcp_srv  = p.get("mcp_server_name","")
                    mcp_tool = p.get("mcp_tool_name","")
                    if mcp_srv or mcp_tool:
                        lines.append(f"      mcp           : server={bold(mcp_srv)}  tool={bold(mcp_tool)}")
            except Exception:
                pass
        elif raw_params:
            try:
                p = json.loads(raw_params) if isinstance(raw_params, str) else raw_params
                mcp_tool = (p or {}).get("mcp_tool_name", "")
                if mcp_tool:
                    lines.append(f"      mcp_tool      : {mcp_tool}")
            except Exception:
                pass

        # Tool input
        if raw_input:
            try:
                ti = json.loads(raw_input) if isinstance(raw_input, str) else raw_input
                if isinstance(ti, dict):
                    for k, v in ti.items():
                        sv = str(v)
                        limit = 300 if verbose else 120
                        if len(sv) > limit: sv = sv[:limit] + "…"
                        lines.append(f"      {k:<14} : {dim(sv)}")
                else:
                    sv = str(ti)
                    limit = 300 if verbose else 120
                    if len(sv) > limit: sv = sv[:limit] + "…"
                    lines.append(f"      input         : {dim(sv)}")
            except Exception:
                sv = str(raw_input)
                if len(sv) > 120: sv = sv[:120] + "…"
                lines.append(f"      input         : {dim(sv)}")

        if verbose:
            shown = {"tool_name","success","duration_ms","tool_result_size_bytes",
                     "mcp_server_scope","tool_input","tool_parameters"}
            extra = {k: v for k, v in attrs.items()
                     if k not in shown and k not in PERSONAL_KEYS and k not in META_KEYS}
            if extra:
                lines.append(f"      {dim('extra attrs')}  :")
                for k, v in extra.items():
                    sv = str(v)
                    if len(sv) > 200: sv = sv[:200] + "…"
                    lines.append(f"        {dim(k):<30} {sv}")

    elif name == "api_error":
        model  = attrs.get("model", "?")
        error  = attrs.get("error", "?")
        status = attrs.get("status_code", "?")
        dur    = int(attrs.get("duration_ms", 0) or 0)
        attempt= attrs.get("attempt", "?")
        speed  = attrs.get("speed", "")
        lines.append(f"      model         : {bold(model)}")
        lines.append(f"      error         : {color(error, RED)}")
        lines.append(f"      status_code   : {status}  dur={fmt_ms(dur)}")
        if verbose:
            lines.append(f"      attempt       : {attempt}  speed={speed}")
            shown = {"model","error","status_code","duration_ms","attempt","speed"}
            extra = {k: v for k, v in attrs.items()
                     if k not in shown and k not in PERSONAL_KEYS and k not in META_KEYS}
            if extra:
                for k, v in extra.items():
                    lines.append(f"      {dim(k):<20} : {v}")

    # ── Verbose: dump ALL remaining keys we didn't handle ───────────────────
    if verbose and name not in ("user_prompt","api_request","tool_decision","tool_result","api_error"):
        shown = set()
        extra = {k: v for k, v in attrs.items()
                 if k not in shown and k not in PERSONAL_KEYS and k not in META_KEYS}
        if extra:
            lines.append(f"      {dim('all attrs')}:")
            for k, v in extra.items():
                sv = str(v)
                if len(sv) > 200: sv = sv[:200] + "…"
                lines.append(f"        {dim(k):<30} {sv}")

    return "\n".join(lines)

# ── Summary rendering ─────────────────────────────────────────────────────────

def render_summary(records, metric_points, verbose=False):
    api_reqs = [r for r in records if r.get("event.name") == "api_request"]
    tool_res = [r for r in records if r.get("event.name") == "tool_result"]
    errors   = [r for r in records if r.get("event.name") == "api_error"]

    total_in   = sum(int(r.get("input_tokens", 0) or 0)          for r in api_reqs)
    total_out  = sum(int(r.get("output_tokens", 0) or 0)         for r in api_reqs)
    total_cr   = sum(int(r.get("cache_read_tokens", 0) or 0)     for r in api_reqs)
    total_cc   = sum(int(r.get("cache_creation_tokens", 0) or 0) for r in api_reqs)
    total_cost = sum(float(r.get("cost_usd", 0) or 0)            for r in api_reqs)
    models     = sorted({r.get("model","") for r in api_reqs if r.get("model")})

    tss = [parse_ts(r.get("event.timestamp","")) for r in api_reqs if r.get("event.timestamp")]
    tss = [t for t in tss if t]
    duration = (tss[-1] - tss[0]).total_seconds() if len(tss) >= 2 else 0

    tool_names  = Counter(r.get("tool_name","") for r in tool_res)
    total_bytes = sum(int(r.get("tool_result_size_bytes", 0) or 0) for r in tool_res)

    lines = [
        "",
        bold(color("━" * 70, CYAN)),
        bold(color("  SESSION SUMMARY", CYAN)),
        bold(color("━" * 70, CYAN)),
        f"  Duration          : {color(f'{duration:.1f}s', YELLOW)}",
        f"  API requests      : {len(api_reqs)}",
        f"  Tool calls        : {len(tool_res)}",
        f"  Errors            : {color(str(len(errors)), RED) if errors else color('0', GREEN)}",
        "",
        bold("  Token Usage"),
        f"    input           : {fmt_tokens(total_in)}",
        f"    output          : {fmt_tokens(total_out)}",
        f"    cache read      : {color(fmt_tokens(total_cr), MAGENTA)}",
        f"    cache creation  : {color(fmt_tokens(total_cc), YELLOW)}",
        f"    total cost      : {color(f'${total_cost:.6f}', GREEN)}",
        "",
        bold("  Models Used"),
    ]
    for m in models:
        lines.append(f"    · {m}")

    lines += ["", bold("  Tool Call Breakdown")]
    for tool, count in tool_names.most_common():
        bar = color("█" * min(count, 40), BLUE)
        lines.append(f"    {tool:<32} {count:>3}×  {bar}")

    lines.append(f"\n  Total data received from tools : {fmt_bytes(total_bytes)}")

    # ── Per-request cost table ────────────────────────────────────────────────
    lines += [
        "",
        bold("  Per-Request Cost Table"),
        dim(f"  {'Seq':>4}  {'Model':<30}  {'In':>7}  {'Out':>7}  {'CacheR':>8}  {'CacheC':>8}  {'Cost':>10}  {'Dur':>8}"),
        dim("  " + "─" * 92),
    ]
    for r in api_reqs:
        seq   = r.get("event.sequence", "?")
        model = (r.get("model","?") or "?")[-28:]
        inp   = int(r.get("input_tokens", 0) or 0)
        out   = int(r.get("output_tokens", 0) or 0)
        cr    = int(r.get("cache_read_tokens", 0) or 0)
        cc    = int(r.get("cache_creation_tokens", 0) or 0)
        cost  = float(r.get("cost_usd", 0) or 0)
        dur   = int(r.get("duration_ms", 0) or 0)
        lines.append(
            f"  {seq:>4}  {model:<30}  {fmt_tokens(inp):>7}  {fmt_tokens(out):>7}  "
            f"{fmt_tokens(cr):>8}  {fmt_tokens(cc):>8}  "
            f"{f'${cost:.5f}':>10}  {fmt_ms(dur):>8}"
        )

    # ── Verbose: cumulative token/cost chart ─────────────────────────────────
    if verbose:
        lines += ["", bold("  Cumulative Output Tokens (per api_request)")]
        cum = 0
        max_out = max((int(r.get("output_tokens", 0) or 0) for r in api_reqs), default=1)
        bar_width = 50
        for r in api_reqs:
            seq = r.get("event.sequence", "?")
            out = int(r.get("output_tokens", 0) or 0)
            cum += out
            bar_len = int(out / max_out * bar_width)
            bar = color("▓" * bar_len, GREEN) + color("░" * (bar_width - bar_len), DIM)
            lines.append(f"    [{seq:>3}]  {bar}  {fmt_tokens(out):>6} tok  (cum: {fmt_tokens(cum)})")

        lines += ["", bold("  Cumulative Cache Read Tokens (growing context window)")]
        cum_cr = 0
        max_cr = max((int(r.get("cache_read_tokens", 0) or 0) for r in api_reqs), default=1)
        for r in api_reqs:
            seq = r.get("event.sequence", "?")
            cr  = int(r.get("cache_read_tokens", 0) or 0)
            bar_len = int(cr / max_cr * bar_width)
            bar = color("▓" * bar_len, MAGENTA) + color("░" * (bar_width - bar_len), DIM)
            lines.append(f"    [{seq:>3}]  {bar}  {fmt_tokens(cr):>8} tok")

        lines += ["", bold("  Cost per API request")]
        max_cost = max((float(r.get("cost_usd", 0) or 0) for r in api_reqs), default=0.0001)
        cum_cost = 0.0
        for r in api_reqs:
            seq  = r.get("event.sequence", "?")
            cost = float(r.get("cost_usd", 0) or 0)
            cum_cost += cost
            bar_len = int(cost / max_cost * bar_width)
            bar = color("▓" * bar_len, GREEN) + color("░" * (bar_width - bar_len), DIM)
            lines.append(f"    [{seq:>3}]  {bar}  ${cost:.5f}  (cum: ${cum_cost:.5f})")

    # ── Verbose: raw metrics dump ─────────────────────────────────────────────
    if verbose and metric_points:
        lines += [
            "",
            bold("  Raw Metrics Dump"),
            dim(f"  {'metric name':<35}  {'type':<14}  {'value':>12}  {'agg'}"),
            dim("  " + "─" * 75),
        ]
        for p in metric_points:
            ts_s = ""
            if p["time_nano"]:
                ts_s = datetime.utcfromtimestamp(int(p["time_nano"]) / 1e9).strftime("%H:%M:%S")
            mono = " (monotonic)" if p["monotonic"] else ""
            lines.append(
                f"  {p['name']:<35}  {p['type_attr']:<14}  {str(p['value']):>12}  "
                f"{p['agg']}{mono}  {dim(ts_s)}"
            )
            if verbose and p["desc"]:
                lines.append(dim(f"    desc: {p['desc']}"))

    lines.append(bold(color("━" * 70, CYAN)))
    return "\n".join(lines)

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    verbose = "--verbose" in args or "-v" in args
    args = [a for a in args if a not in ("--verbose", "-v")]

    if not args:
        print(f"Usage: {sys.argv[0]} <events_file> [metrics_file] [--verbose|-v]")
        sys.exit(1)

    events_path  = args[0]
    metrics_path = args[1] if len(args) > 1 else None

    if not os.path.exists(events_path):
        print(f"Error: events file not found: {events_path}")
        sys.exit(1)

    print(bold(color(f"\n  Claude Code Session Visualizer", CYAN))
          + (color("  [VERBOSE]", YELLOW) if verbose else ""))
    print(dim(f"  events  : {events_path}"))
    if metrics_path:
        print(dim(f"  metrics : {metrics_path}"))
    print()

    event_batches  = load_otel_file(events_path)
    metric_batches = load_otel_file(metrics_path) if metrics_path and os.path.exists(metrics_path) else []

    if verbose:
        print(dim(f"  Loaded {len(event_batches)} event batch(es), {len(metric_batches)} metric batch(es)"))
        print()

    records       = extract_events(event_batches)
    metric_points = extract_metrics(metric_batches)

    if not records:
        print(color("No log records found.", RED))
        sys.exit(1)

    api_tss  = [parse_ts(r.get("event.timestamp","")) for r in records if r.get("event.name") == "api_request"]
    api_tss  = [t for t in api_tss if t]
    first_ts = api_tss[0] if api_tss else None

    # ── Event timeline ───────────────────────────────────────────────────────
    print(bold(color("━" * 70, BLUE)))
    print(bold(color("  EVENT TIMELINE", BLUE)))
    print(bold(color("━" * 70, BLUE)))
    hdr = f"  {'[seq]':<8}  {'time (UTC)':<14}  {'(+elapsed)':>10}"
    if verbose: hdr += f"  {'(Δ prev)':>12}"
    hdr += "  event"
    print(dim(hdr))
    print()

    prev_ts = None
    for attrs in records:
        ts = parse_ts(attrs.get("event.timestamp",""))
        print(render_event(attrs, prev_ts, first_ts, verbose=verbose))
        print()
        prev_ts = ts

    # ── Summary ──────────────────────────────────────────────────────────────
    print(render_summary(records, metric_points, verbose=verbose))
    print()

if __name__ == "__main__":
    main()
