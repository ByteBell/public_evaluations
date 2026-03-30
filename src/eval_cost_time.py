#!/usr/bin/env python3
"""
KubeCluster45 — Cost & Time analysis only.
Claude Opus 4.6 pricing: $5/M input · $25/M output tokens.
"""

import json, os
from pathlib import Path

BASE       = Path("/Users/deadbytes/Documents/ByteBell/public_evaluations")
MCP_BASE   = BASE / "New_eval_kube45" / "Answers_with_mcp"
NOMCP_BASE = BASE / "New_eval_kube45" / "Answers_without_mcp"
OUT_DIR    = BASE / "docs"
OUT_DIR.mkdir(exist_ok=True)

INPUT_RATE  = 5.0  / 1_000_000   # $5 per M input tokens
OUTPUT_RATE = 25.0 / 1_000_000   # $25 per M output tokens


# ── Extract metrics from a single answer.json ─────────────────────────────────

def get_mcp_metrics(qid):
    path = MCP_BASE / qid / "answer.json"
    if not path.exists():
        return {}
    d = json.loads(path.read_text())

    # Tool calls — various locations
    tc = (d.get("tool_calls_count") or d.get("total_tool_calls"))
    if tc is None and isinstance(d.get("tool_calls"), list):
        tc = len(d["tool_calls"])
    if tc is None and isinstance(d.get("answer"), dict):
        a = d["answer"]
        tc = a.get("total_tool_calls") or a.get("tool_calls_count")

    return {"tool_calls": tc, "input_tokens": None, "output_tokens": None,
            "time_s": None, "cost_usd": None}


def get_nomcp_metrics(qid):
    path = NOMCP_BASE / qid / "answer.json"
    if not path.exists():
        return {}
    d = json.loads(path.read_text())
    m = d.get("metrics", {}) or {}

    # Input tokens
    tok_in = (m.get("input_tokens_estimate") or
              m.get("total_estimated_input_tokens") or
              m.get("total_input_tokens") or
              (m.get("token_tracking") or {}).get("total_input_tokens"))

    # Output tokens
    tok_out = (m.get("output_tokens_estimate") or
               m.get("total_estimated_output_tokens") or
               m.get("estimated_output_tokens") or
               (m.get("token_tracking") or {}).get("estimated_output_tokens"))

    # Ensure numeric
    tok_in  = tok_in  if isinstance(tok_in,  (int, float)) else None
    tok_out = tok_out if isinstance(tok_out, (int, float)) else None

    # Tool calls
    tc = m.get("total_tool_calls")
    if tc is None:
        tc = (m.get("time_tracking") or {}).get("total_tool_calls")
    if tc is None and isinstance(m.get("tool_calls"), list):
        tc = len(m["tool_calls"])

    # Time
    tt = m.get("time_tracking") or {}
    time_s = (tt.get("total_elapsed_time_seconds") or
              tt.get("total_elapsed_seconds") or
              tt.get("elapsed_seconds"))

    cost = None
    if tok_in is not None and tok_out is not None:
        cost = tok_in * INPUT_RATE + tok_out * OUTPUT_RATE

    return {"tool_calls": tc, "input_tokens": tok_in, "output_tokens": tok_out,
            "time_s": time_s, "cost_usd": cost}


# ── Aggregate ─────────────────────────────────────────────────────────────────

def main():
    questions = sorted(os.listdir(MCP_BASE))

    rows = []
    for qid in questions:
        cat = "MIXED" if qid.startswith("MIXED") else "OBS"
        mcp   = get_mcp_metrics(qid)
        nomcp = get_nomcp_metrics(qid)
        rows.append({"qid": qid, "cat": cat, "mcp": mcp, "nomcp": nomcp})

    return rows


def fmt(v, dec=1):
    if v is None: return "N/A"
    if isinstance(v, float): return f"{v:.{dec}f}"
    return str(v)

def fmtc(v):
    if v is None: return "N/A"
    return f"${v:.4f}"

def fmttok(v):
    if v is None: return "N/A"
    return f"{v:,.0f}"

def avg(lst): return sum(lst)/len(lst) if lst else None
def tot(lst): return sum(lst) if lst else None


def build_report(rows):
    lines = []
    a = lines.append

    a("# KubeCluster45 — Cost & Time Analysis")
    a("")
    a("**Model:** Claude Opus 4.6  ")
    a("**Pricing:** $5.00 / M input tokens · $25.00 / M output tokens  ")
    a("**Dataset:** 45 questions — 11 MIXED · 34 OBS  ")
    a("**Conditions:** MCP-assisted vs Unaided (no MCP, no web search)")
    a("")
    a("---")
    a("")

    # ── No-MCP aggregate ──────────────────────────────────────────────────────
    nm_in   = [r["nomcp"]["input_tokens"]  for r in rows if r["nomcp"].get("input_tokens")  is not None]
    nm_out  = [r["nomcp"]["output_tokens"] for r in rows if r["nomcp"].get("output_tokens") is not None]
    nm_cost = [r["nomcp"]["cost_usd"]      for r in rows if r["nomcp"].get("cost_usd")      is not None]
    nm_tc   = [r["nomcp"]["tool_calls"]    for r in rows if r["nomcp"].get("tool_calls")    is not None]
    nm_time = [r["nomcp"]["time_s"]        for r in rows if r["nomcp"].get("time_s")        is not None]

    mcp_tc  = [r["mcp"]["tool_calls"] for r in rows if r["mcp"].get("tool_calls") is not None]

    a("## 1. No-MCP Run — Overall Summary")
    a("")
    a(f"> Data available for **{len(nm_cost)}/45** questions (cost) · **{len(nm_tc)}/45** (tool calls) · **{len(nm_time)}/45** (time)")
    a("")
    a("| Metric | Total | Avg / question |")
    a("|--------|-------|----------------|")
    a(f"| Input tokens  | {fmttok(tot(nm_in))}  | {fmttok(avg(nm_in))} |")
    a(f"| Output tokens | {fmttok(tot(nm_out))} | {fmttok(avg(nm_out))} |")
    a(f"| **Cost (USD)** | **{fmtc(tot(nm_cost))}** | **{fmtc(avg(nm_cost))}** |")
    a(f"| Tool calls    | {fmt(tot(nm_tc), 0)} | {fmt(avg(nm_tc))} |")
    a(f"| Time (seconds) | {fmt(tot(nm_time), 0)} | {fmt(avg(nm_time))} |")
    a(f"| Time (minutes) | {fmt(tot(nm_time)/60 if nm_time else None)} | {fmt(avg(nm_time)/60 if nm_time else None)} |")
    a("")

    # ── MCP tool calls ────────────────────────────────────────────────────────
    a("## 2. MCP Run — Tool Calls")
    a("")
    a(f"> Token/cost data not consistently recorded in MCP answer files. Tool call data available for **{len(mcp_tc)}/45** questions.")
    a("")
    a("| Metric | Total | Avg / question |")
    a("|--------|-------|----------------|")
    a(f"| MCP tool calls | {fmt(tot(mcp_tc), 0)} | {fmt(avg(mcp_tc))} |")
    a("")

    # ── Category breakdown ────────────────────────────────────────────────────
    a("## 3. No-MCP — By Question Category")
    a("")
    for cat in ["MIXED", "OBS"]:
        cat_rows = [r for r in rows if r["cat"] == cat]
        cc = [r["nomcp"]["cost_usd"] for r in cat_rows if r["nomcp"].get("cost_usd") is not None]
        ct = [r["nomcp"]["time_s"]   for r in cat_rows if r["nomcp"].get("time_s")   is not None]
        ctc = [r["nomcp"]["tool_calls"] for r in cat_rows if r["nomcp"].get("tool_calls") is not None]
        n = len(cat_rows)
        a(f"### {cat} ({n} questions)")
        a("")
        a("| Metric | Total | Avg / question |")
        a("|--------|-------|----------------|")
        a(f"| Cost (USD) | {fmtc(tot(cc))} | {fmtc(avg(cc))} |")
        a(f"| Time (s)   | {fmt(tot(ct), 0)} | {fmt(avg(ct))} |")
        a(f"| Tool calls | {fmt(tot(ctc), 0)} | {fmt(avg(ctc))} |")
        a("")

    # ── Per-question table ────────────────────────────────────────────────────
    a("## 4. Per-Question Detail")
    a("")
    a("| # | Question | Cat | NoMCP In-Tok | NoMCP Out-Tok | NoMCP Cost | NoMCP Tools | NoMCP Time(s) | MCP Tools |")
    a("|---|----------|-----|-------------|--------------|-----------|------------|--------------|-----------|")
    for i, r in enumerate(rows, 1):
        nm = r["nomcp"]
        mc = r["mcp"]
        a(f"| {i} | {r['qid']} | {r['cat']} | "
          f"{fmttok(nm.get('input_tokens'))} | {fmttok(nm.get('output_tokens'))} | "
          f"{fmtc(nm.get('cost_usd'))} | {fmt(nm.get('tool_calls'), 0)} | "
          f"{fmt(nm.get('time_s'), 0)} | {fmt(mc.get('tool_calls'), 0)} |")
    a("")

    # ── Cost breakdown by token type ─────────────────────────────────────────
    a("## 5. Cost Breakdown")
    a("")
    input_cost_total  = tot(nm_in)  * INPUT_RATE  if nm_in  else None
    output_cost_total = tot(nm_out) * OUTPUT_RATE if nm_out else None
    a("| Component | Tokens | Cost | % of total |")
    a("|-----------|--------|------|-----------|")
    total_c = tot(nm_cost) or 1
    if input_cost_total is not None:
        a(f"| Input  | {fmttok(tot(nm_in))}  | {fmtc(input_cost_total)}  | {input_cost_total/total_c*100:.1f}% |")
    if output_cost_total is not None:
        a(f"| Output | {fmttok(tot(nm_out))} | {fmtc(output_cost_total)} | {output_cost_total/total_c*100:.1f}% |")
    a(f"| **Total** | — | **{fmtc(tot(nm_cost))}** | 100% |")
    a("")

    # ── Top 5 most expensive questions ───────────────────────────────────────
    a("## 6. Most Expensive Questions (No-MCP)")
    a("")
    a("| Question | Cost | Input Tok | Output Tok | Time(s) | Tools |")
    a("|----------|------|-----------|-----------|---------|-------|")
    costed = sorted([r for r in rows if r["nomcp"].get("cost_usd") is not None],
                    key=lambda r: r["nomcp"]["cost_usd"], reverse=True)
    for r in costed[:10]:
        nm = r["nomcp"]
        a(f"| {r['qid']} | {fmtc(nm['cost_usd'])} | {fmttok(nm.get('input_tokens'))} | "
          f"{fmttok(nm.get('output_tokens'))} | {fmt(nm.get('time_s'), 0)} | {fmt(nm.get('tool_calls'), 0)} |")
    a("")

    # ── Key numbers ───────────────────────────────────────────────────────────
    a("## 7. Key Numbers")
    a("")
    a(f"- **Total no-MCP cost across 45 questions:** {fmtc(tot(nm_cost))} *(from {len(nm_cost)} questions with cost data)*")
    a(f"- **Average cost per question (no-MCP):** {fmtc(avg(nm_cost))}")
    a(f"- **Average time per question (no-MCP):** {fmt(avg(nm_time))} seconds")
    a(f"- **Average tool calls per question (no-MCP):** {fmt(avg(nm_tc))}")
    a(f"- **Average tool calls per question (MCP):** {fmt(avg(mcp_tc))} *(from {len(mcp_tc)} questions with data)*")
    if nm_time:
        a(f"- **Total wall-clock time (no-MCP, all 45q):** ~{tot(nm_time)/60:.1f} minutes *(from {len(nm_time)} questions)*")
    a("")
    a("---")
    a("*Prices: Claude Opus 4.6 — $5.00/M input tokens · $25.00/M output tokens (Anthropic, Feb 2026)*")

    return "\n".join(lines)


if __name__ == "__main__":
    rows = main()
    report = build_report(rows)

    out = OUT_DIR / "kube45_cost_time_report.md"
    out.write_text(report)
    print(f"Report → {out}")

    # Quick summary
    nm_cost = [r["nomcp"]["cost_usd"] for r in rows if r["nomcp"].get("cost_usd") is not None]
    nm_time = [r["nomcp"]["time_s"] for r in rows if r["nomcp"].get("time_s") is not None]
    nm_tc   = [r["nomcp"]["tool_calls"] for r in rows if r["nomcp"].get("tool_calls") is not None]
    mcp_tc  = [r["mcp"]["tool_calls"] for r in rows if r["mcp"].get("tool_calls") is not None]
    print(f"\nNo-MCP total cost:  ${sum(nm_cost):.4f}  (avg ${sum(nm_cost)/len(nm_cost):.4f}/q, {len(nm_cost)} q)")
    print(f"No-MCP avg time:    {sum(nm_time)/len(nm_time):.0f}s  ({len(nm_time)} q)")
    print(f"No-MCP avg tools:   {sum(nm_tc)/len(nm_tc):.1f}  ({len(nm_tc)} q)")
    print(f"MCP avg tools:      {sum(mcp_tc)/len(mcp_tc):.1f}  ({len(mcp_tc)} q)")
