#!/usr/bin/env python3
"""
KubeCluster45 — Cost, Time, and File Accuracy (reported vs true) analysis.
Claude Opus 4.6: $5/M input · $25/M output tokens.
"""

import json, os, re
from pathlib import Path
from collections import defaultdict

BASE       = Path("/Users/deadbytes/Documents/ByteBell/public_evaluations")
GT_BASE    = BASE / "results" / "KubeCluster45"
MCP_BASE   = BASE / "New_eval_kube45" / "Answers_with_mcp"
NOMCP_BASE = BASE / "New_eval_kube45" / "Answers_without_mcp"
OUT_DIR    = BASE / "docs"
OUT_DIR.mkdir(exist_ok=True)

INPUT_RATE  = 5.0  / 1_000_000
OUTPUT_RATE = 25.0 / 1_000_000

# ── Repo normalisation ─────────────────────────────────────────────────────────
REPO_MAP = {
    "prometheus/prometheus": "prometheus", "grafana/mimir": "mimir",
    "grafana/loki": "loki", "grafana/grafana": "grafana", "grafana/tempo": "tempo",
    "thanos-io/thanos": "thanos", "argoproj/argo-cd": "argo-cd",
    "kubernetes/ingress-nginx": "ingress-nginx",
    "external-secrets/external-secrets": "external-secrets", "helm/helm": "helm",
    "open-telemetry/opentelemetry-operator": "opentelemetry-operator",
    "open-telemetry/opentelemetry-collector-contrib": "opentelemetry-collector-contrib",
    "jaegertracing/jaeger": "jaeger",
}
KNOWN_REPOS = set(list(REPO_MAP.values()) + ["prometheus", "mimir", "loki", "thanos",
    "grafana", "tempo", "helm", "argo-cd", "argocd", "ingress-nginx",
    "external-secrets", "opentelemetry-operator", "opentelemetry-collector-contrib",
    "opentelemetry-collector", "jaeger", "cilium", "cert-manager"])

def norm_repo(r):
    r = r.strip()
    if r in REPO_MAP: return REPO_MAP[r]
    rl = r.lower()
    for k, v in REPO_MAP.items():
        if k.lower() == rl: return v
    parts = r.split("/")
    if len(parts) >= 2:
        c = "/".join(parts[-2:])
        if c in REPO_MAP: return REPO_MAP[c]
    return r.lower()

# ── Ground truth ───────────────────────────────────────────────────────────────
def load_gt(qid):
    p = GT_BASE / f"question_{qid}" / "ground_truth_enhanced.json"
    if not p.exists(): return set()
    d = json.loads(p.read_text())
    return {(norm_repo(f["repo"]), f["file"].strip()) for f in d.get("impacted_files", [])}

# ── File extractors ────────────────────────────────────────────────────────────

def _from_dict_of_lists(d):
    result = set()
    for repo_key, items in d.items():
        if not isinstance(items, (list, dict)): continue
        rk = norm_repo(repo_key)
        if isinstance(items, list):
            for item in items:
                if isinstance(item, str):
                    result.add((rk, item.strip()))
                elif isinstance(item, dict):
                    f = item.get("file") or item.get("path") or item.get("filename")
                    if f: result.add((rk, str(f).strip()))
    return result

def _recursive(obj, depth=0, parent_repo=None):
    if depth > 6: return set()
    result = set()
    if isinstance(obj, dict):
        repo = obj.get("repo") or obj.get("source_repo") or parent_repo
        file = obj.get("file") or obj.get("path") or obj.get("filename")
        if file and repo:
            result.add((norm_repo(repo), str(file).strip()))
        repo_key_count = sum(1 for k in obj if norm_repo(k) in KNOWN_REPOS)
        if repo_key_count >= 1:
            for k, v in obj.items():
                pr = k if norm_repo(k) in KNOWN_REPOS else parent_repo
                result |= _recursive(v, depth+1, parent_repo=pr)
        else:
            for v in obj.values():
                result |= _recursive(v, depth+1, parent_repo=parent_repo)
    elif isinstance(obj, list):
        for item in obj:
            result |= _recursive(item, depth+1, parent_repo=parent_repo)
    return result

FILE_PAT = re.compile(
    r"[-*•]\s*(?:`+)?"
    r"([a-z][\w\-\.]+)/([a-zA-Z0-9_\-\./]+\.\w+)"
    r"(?:`+)?", re.MULTILINE)

def _from_text(text):
    result = set()
    for m in FILE_PAT.finditer(text):
        r, f = m.group(1), m.group(2)
        nr = norm_repo(r)
        if nr in KNOWN_REPOS or "/" in r:
            result.add((nr, f.strip()))
    return result

def extract_mcp_files(qid):
    p = MCP_BASE / qid / "answer.json"
    if not p.exists(): return set()
    d = json.loads(p.read_text())

    if "expected_files" in d:
        result = set()
        for e in d["expected_files"]:
            for f in e.get("files", []):
                result.add((norm_repo(e.get("repo", "")), f.strip()))
        if result: return result

    if "affected_files" in d and isinstance(d["affected_files"], dict):
        r = _from_dict_of_lists(d["affected_files"])
        if r: return r

    ans = d.get("answer")
    if not ans: return set()

    if isinstance(ans, str):
        return _from_text(ans)

    if not isinstance(ans, dict): return set()

    if "files_list" in ans:
        result = set()
        for item in ans["files_list"]:
            if isinstance(item, str) and ":" in item:
                r, f = item.split(":", 1)
                result.add((norm_repo(r), f.strip()))
        if result: return result

    if "affected_files" in ans and isinstance(ans["affected_files"], dict):
        r = _from_dict_of_lists(ans["affected_files"])
        if r: return r

    for key in ("files_to_modify", "files_to_change", "files_changed", "impacted_files"):
        if key in ans and isinstance(ans[key], list):
            r = set()
            for item in ans[key]:
                if isinstance(item, dict):
                    repo = item.get("repo") or item.get("source_repo")
                    file = item.get("file") or item.get("path") or item.get("filename")
                    if file and repo:
                        r.add((norm_repo(repo), str(file).strip()))
            if r: return r

    # Singular file_to_modify
    if "file_to_modify" in ans:
        f = ans["file_to_modify"]
        repo = ans.get("repo") or d.get("repo") or ""
        if isinstance(f, str) and f:
            return {(norm_repo(repo), f.strip())}

    # Recursive fallback
    return _recursive(ans)

def extract_nomcp_files(qid):
    p = NOMCP_BASE / qid / "answer.json"
    if not p.exists(): return set()
    d = json.loads(p.read_text())

    cond = d.get("llm_condensed_answer", "")
    if cond:
        section = cond.split("FILES:", 1)[1] if "FILES:" in cond else cond
        r = _from_text(section)
        if r: return r

    ans = d.get("answer", "")
    if isinstance(ans, str) and ans:
        return _from_text(ans)
    if isinstance(ans, dict):
        return _recursive(ans)
    return set()

# ── Metrics extractors ─────────────────────────────────────────────────────────

def get_mcp_metrics(qid):
    p = MCP_BASE / qid / "answer.json"
    if not p.exists(): return {}
    d = json.loads(p.read_text())
    tc = d.get("tool_calls_count") or d.get("total_tool_calls")
    if tc is None and isinstance(d.get("tool_calls"), list):
        tc = len(d["tool_calls"])
    if tc is None and isinstance(d.get("answer"), dict):
        a = d["answer"]
        tc = a.get("total_tool_calls") or a.get("tool_calls_count")
    return {"tool_calls": tc}

def get_nomcp_metrics(qid):
    p = NOMCP_BASE / qid / "answer.json"
    if not p.exists(): return {}
    d = json.loads(p.read_text())
    m = d.get("metrics", {}) or {}

    tok_in  = (m.get("input_tokens_estimate") or m.get("total_estimated_input_tokens") or
               m.get("total_input_tokens") or (m.get("token_tracking") or {}).get("total_input_tokens"))
    tok_out = (m.get("output_tokens_estimate") or m.get("total_estimated_output_tokens") or
               m.get("estimated_output_tokens") or (m.get("token_tracking") or {}).get("estimated_output_tokens"))
    tok_in  = tok_in  if isinstance(tok_in,  (int, float)) else None
    tok_out = tok_out if isinstance(tok_out, (int, float)) else None

    tc = m.get("total_tool_calls")
    if tc is None: tc = (m.get("time_tracking") or {}).get("total_tool_calls")
    if tc is None and isinstance(m.get("tool_calls"), list): tc = len(m["tool_calls"])

    tt = m.get("time_tracking") or {}
    time_s = (tt.get("total_elapsed_time_seconds") or tt.get("total_elapsed_seconds") or
              tt.get("elapsed_seconds"))

    cost = (tok_in * INPUT_RATE + tok_out * OUTPUT_RATE
            if tok_in is not None and tok_out is not None else None)

    return {"tool_calls": tc, "input_tokens": tok_in, "output_tokens": tok_out,
            "time_s": time_s, "cost_usd": cost}

# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    questions = sorted(os.listdir(MCP_BASE))
    rows = []
    for qid in questions:
        cat = "MIXED" if qid.startswith("MIXED") else "OBS"
        gt       = load_gt(qid)
        mcp_pred = extract_mcp_files(qid)
        nm_pred  = extract_nomcp_files(qid)
        mcp_m    = get_mcp_metrics(qid)
        nm_m     = get_nomcp_metrics(qid)

        mcp_tp = len(mcp_pred & gt)
        nm_tp  = len(nm_pred  & gt)

        rows.append({
            "qid": qid, "cat": cat, "gt_count": len(gt),
            "mcp_reported": len(mcp_pred), "mcp_true": mcp_tp,
            "mcp_tool_calls": mcp_m.get("tool_calls"),
            "nm_reported": len(nm_pred), "nm_true": nm_tp,
            "nm_tool_calls": nm_m.get("tool_calls"),
            "nm_input_tokens": nm_m.get("input_tokens"),
            "nm_output_tokens": nm_m.get("output_tokens"),
            "nm_time_s": nm_m.get("time_s"),
            "nm_cost": nm_m.get("cost_usd"),
        })
    return rows

# ── Report ─────────────────────────────────────────────────────────────────────

def fmt(v, dec=1):
    if v is None: return "N/A"
    if isinstance(v, float): return f"{v:.{dec}f}"
    return str(v)
def fmtc(v): return f"${v:.4f}" if v is not None else "N/A"
def fmttok(v): return f"{v:,.0f}" if v is not None else "N/A"
def avg(lst): return sum(lst)/len(lst) if lst else None
def tot(lst): return sum(lst) if lst else None

def build_report(rows):
    lines = []
    a = lines.append

    a("# KubeCluster45 Evaluation Report")
    a("")
    a("**Model:** Claude Opus 4.6  ")
    a("**Pricing:** $5.00 / M input · $25.00 / M output tokens  ")
    a("**Dataset:** 45 questions — 11 MIXED · 34 OBS  ")
    a("**Conditions:** MCP-assisted (knowledge graph tools) vs Unaided (no MCP, no web search)")
    a("")
    a("---")
    a("")

    # ── File reporting accuracy ───────────────────────────────────────────────
    a("## 1. Files Reported vs Files Correct")
    a("")
    a("*\"Reported\"* = number of files the model identified as impacted.  ")
    a("*\"True\"* = of those reported, how many were actually in the ground truth.  ")
    a("*\"Hit rate\"* = True / Reported (precision on reported files).")
    a("")

    mcp_rep_all = sum(r["mcp_reported"] for r in rows)
    mcp_tru_all = sum(r["mcp_true"]     for r in rows)
    nm_rep_all  = sum(r["nm_reported"]  for r in rows)
    nm_tru_all  = sum(r["nm_true"]      for r in rows)
    gt_all      = sum(r["gt_count"]     for r in rows)

    mcp_hit = mcp_tru_all / mcp_rep_all if mcp_rep_all else 0
    nm_hit  = nm_tru_all  / nm_rep_all  if nm_rep_all  else 0

    a("| | MCP | No-MCP |")
    a("|--|-----|--------|")
    a(f"| **Total files reported** | {mcp_rep_all:,} | {nm_rep_all:,} |")
    a(f"| **True (in GT)** | {mcp_tru_all:,} | {nm_tru_all:,} |")
    a(f"| **Hit rate (reported → true)** | {mcp_hit*100:.1f}% | {nm_hit*100:.1f}% |")
    a(f"| GT total files across all questions | {gt_all} | {gt_all} |")
    a(f"| Avg reported per question | {mcp_rep_all/45:.1f} | {nm_rep_all/45:.1f} |")
    a(f"| Avg true per question | {mcp_tru_all/45:.1f} | {nm_tru_all/45:.1f} |")
    a("")

    # ── Cost & time summary ───────────────────────────────────────────────────
    nm_cost_list = [r["nm_cost"]   for r in rows if r["nm_cost"]   is not None]
    nm_time_list = [r["nm_time_s"] for r in rows if r["nm_time_s"] is not None]
    nm_tc_list   = [r["nm_tool_calls"] for r in rows if r["nm_tool_calls"] is not None]
    nm_in_list   = [r["nm_input_tokens"]  for r in rows if r["nm_input_tokens"]  is not None]
    nm_out_list  = [r["nm_output_tokens"] for r in rows if r["nm_output_tokens"] is not None]
    mcp_tc_list  = [r["mcp_tool_calls"] for r in rows if r["mcp_tool_calls"] is not None]

    a("## 2. Cost & Time — No-MCP Run")
    a("")
    a(f"> Data from **{len(nm_cost_list)}/45** questions (cost) · **{len(nm_tc_list)}/45** (tools) · **{len(nm_time_list)}/45** (time)")
    a("")
    a("| Metric | Total | Avg / question |")
    a("|--------|-------|----------------|")
    a(f"| Input tokens  | {fmttok(tot(nm_in_list))}  | {fmttok(avg(nm_in_list))} |")
    a(f"| Output tokens | {fmttok(tot(nm_out_list))} | {fmttok(avg(nm_out_list))} |")
    a(f"| **Cost (USD)** | **{fmtc(tot(nm_cost_list))}** | **{fmtc(avg(nm_cost_list))}** |")
    a(f"| Tool calls | {fmt(tot(nm_tc_list), 0)} | {fmt(avg(nm_tc_list))} |")
    a(f"| Time (s)   | {fmt(tot(nm_time_list), 0)} | {fmt(avg(nm_time_list))} |")
    a(f"| Time (min) | {fmt(tot(nm_time_list)/60 if nm_time_list else None)} | {fmt(avg(nm_time_list)/60 if nm_time_list else None)} |")
    a("")

    # Input vs output cost split
    ic = tot(nm_in_list)  * INPUT_RATE  if nm_in_list  else 0
    oc = tot(nm_out_list) * OUTPUT_RATE if nm_out_list else 0
    tc_cost = ic + oc if (ic or oc) else None
    if tc_cost:
        a(f"**Cost split:** input = {fmtc(ic)} ({ic/tc_cost*100:.0f}%) · output = {fmtc(oc)} ({oc/tc_cost*100:.0f}%)")
        a("")

    # ── MCP tool calls ────────────────────────────────────────────────────────
    a("## 3. MCP Tool Calls")
    a("")
    a(f"> Token/cost data not recorded in MCP answer files. Tool call data from **{len(mcp_tc_list)}/45** questions.")
    a("")
    a("| Metric | Total | Avg / question |")
    a("|--------|-------|----------------|")
    a(f"| MCP tool calls | {fmt(tot(mcp_tc_list), 0)} | {fmt(avg(mcp_tc_list))} |")
    a("")

    # ── Category breakdown ────────────────────────────────────────────────────
    a("## 4. By Category")
    a("")
    a("| Category | Questions | MCP Reported | MCP True | MCP Hit% | NoMCP Reported | NoMCP True | NoMCP Hit% | NoMCP Cost | NoMCP Avg Time(s) |")
    a("|----------|-----------|-------------|---------|---------|---------------|-----------|-----------|-----------|-----------------|")
    for cat in ["MIXED", "OBS"]:
        cr = [r for r in rows if r["cat"] == cat]
        mr = sum(r["mcp_reported"] for r in cr)
        mt = sum(r["mcp_true"]     for r in cr)
        nr = sum(r["nm_reported"]  for r in cr)
        nt = sum(r["nm_true"]      for r in cr)
        nc = [r["nm_cost"] for r in cr if r["nm_cost"] is not None]
        ntm = [r["nm_time_s"] for r in cr if r["nm_time_s"] is not None]
        mhit = f"{mt/mr*100:.1f}%" if mr else "N/A"
        nhit = f"{nt/nr*100:.1f}%" if nr else "N/A"
        a(f"| {cat} | {len(cr)} | {mr} | {mt} | {mhit} | {nr} | {nt} | {nhit} | {fmtc(tot(nc))} | {fmt(avg(ntm))} |")
    a("")

    # ── Per-question table ────────────────────────────────────────────────────
    a("## 5. Per-Question Detail")
    a("")
    a("| # | Question | GT | MCP Rep | MCP True | MCP Hit% | MCP Tools | NoMCP Rep | NoMCP True | NoMCP Hit% | NoMCP Tools | NoMCP Time(s) | NoMCP Cost |")
    a("|---|----------|----|---------|---------|---------|----------|----------|-----------|-----------|------------|--------------|-----------|")
    for i, r in enumerate(rows, 1):
        mr, mt = r["mcp_reported"], r["mcp_true"]
        nr, nt = r["nm_reported"],  r["nm_true"]
        mhit = f"{mt/mr*100:.0f}%" if mr else "—"
        nhit = f"{nt/nr*100:.0f}%" if nr else "—"
        a(f"| {i} | {r['qid']} | {r['gt_count']} | "
          f"{mr} | {mt} | {mhit} | {fmt(r['mcp_tool_calls'], 0)} | "
          f"{nr} | {nt} | {nhit} | "
          f"{fmt(r['nm_tool_calls'], 0)} | {fmt(r['nm_time_s'], 0)} | {fmtc(r['nm_cost'])} |")
    a("")

    # ── Most expensive ────────────────────────────────────────────────────────
    a("## 6. Most Expensive Questions (No-MCP, top 10)")
    a("")
    a("| Question | Cost | Input Tok | Output Tok | Time(s) | Tools | GT Files | Reported | True |")
    a("|----------|------|-----------|-----------|---------|-------|----------|---------|------|")
    costed = sorted([r for r in rows if r["nm_cost"] is not None],
                    key=lambda r: r["nm_cost"], reverse=True)
    for r in costed[:10]:
        a(f"| {r['qid']} | {fmtc(r['nm_cost'])} | {fmttok(r['nm_input_tokens'])} | "
          f"{fmttok(r['nm_output_tokens'])} | {fmt(r['nm_time_s'], 0)} | {fmt(r['nm_tool_calls'], 0)} | "
          f"{r['gt_count']} | {r['nm_reported']} | {r['nm_true']} |")
    a("")

    a("---")
    a("*Prices: Claude Opus 4.6 — $5.00/M input · $25.00/M output (Anthropic, Feb 2026)*  ")
    a("*Ground truth: `results/KubeCluster45/question_*/ground_truth_enhanced.json`*  ")
    a("*Answers: `New_eval_kube45/Answers_with_mcp/` and `New_eval_kube45/Answers_without_mcp/`*")

    return "\n".join(lines)


if __name__ == "__main__":
    rows = main()
    report = build_report(rows)
    out = OUT_DIR / "kube45_eval_report.md"
    out.write_text(report)
    print(f"Report → {out}")

    mcp_rep = sum(r["mcp_reported"] for r in rows)
    mcp_tru = sum(r["mcp_true"] for r in rows)
    nm_rep  = sum(r["nm_reported"] for r in rows)
    nm_tru  = sum(r["nm_true"] for r in rows)
    nm_cost = [r["nm_cost"] for r in rows if r["nm_cost"] is not None]
    print(f"\nMCP:   reported={mcp_rep}  true={mcp_tru}  hit={mcp_tru/mcp_rep*100:.1f}%")
    print(f"NoMCP: reported={nm_rep}   true={nm_tru}   hit={nm_tru/nm_rep*100:.1f}%")
    print(f"NoMCP total cost: ${sum(nm_cost):.4f} ({len(nm_cost)} questions)")
