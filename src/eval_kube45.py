#!/usr/bin/env python3
"""
Evaluation script for KubeCluster45 — MCP vs No-MCP comparison.
Compares Claude Opus 4.6 answers (with and without MCP tools) against ground truth.
Pricing: $5/M input tokens, $25/M output tokens (Claude Opus 4.6).
"""

import json
import os
import re
from pathlib import Path
from collections import defaultdict
from typing import Optional

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE = Path("/Users/deadbytes/Documents/ByteBell/public_evaluations")
GT_BASE   = BASE / "results" / "KubeCluster45"
MCP_BASE  = BASE / "New_eval_kube45" / "Answers_with_mcp"
NOMCP_BASE = BASE / "New_eval_kube45" / "Answers_without_mcp"
OUT_DIR   = BASE / "docs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Opus 4.6 pricing
INPUT_COST_PER_TOKEN  = 5.0  / 1_000_000   # $5/M
OUTPUT_COST_PER_TOKEN = 25.0 / 1_000_000   # $25/M

# ── Repo name normalisation ────────────────────────────────────────────────────
REPO_MAP = {
    # GitHub org/repo → short name
    "prometheus/prometheus": "prometheus",
    "grafana/mimir": "mimir",
    "grafana/loki": "loki",
    "grafana/grafana": "grafana",
    "grafana/tempo": "tempo",
    "thanos-io/thanos": "thanos",
    "argoproj/argo-cd": "argo-cd",
    "kubernetes/ingress-nginx": "ingress-nginx",
    "external-secrets/external-secrets": "external-secrets",
    "helm/helm": "helm",
    "open-telemetry/opentelemetry-operator": "opentelemetry-operator",
    "open-telemetry/opentelemetry-collector": "opentelemetry-collector",
    "open-telemetry/opentelemetry-collector-contrib": "opentelemetry-collector-contrib",
    "jaegertracing/jaeger": "jaeger",
    # Short names already correct
    "prometheus": "prometheus",
    "mimir": "mimir",
    "loki": "loki",
    "grafana": "grafana",
    "tempo": "tempo",
    "thanos": "thanos",
    "argo-cd": "argo-cd",
    "argocd": "argo-cd",
    "ingress-nginx": "ingress-nginx",
    "external-secrets": "external-secrets",
    "helm": "helm",
    "opentelemetry-operator": "opentelemetry-operator",
    "opentelemetry-collector": "opentelemetry-collector",
    "opentelemetry-collector-contrib": "opentelemetry-collector-contrib",
    "jaeger": "jaeger",
}

def norm_repo(r: str) -> str:
    r = r.strip()
    if r in REPO_MAP:
        return REPO_MAP[r]
    # Try case-insensitive
    rl = r.lower()
    for k, v in REPO_MAP.items():
        if k.lower() == rl:
            return v
    # Extract last component e.g. "grafana/mimir" -> "mimir"
    parts = r.split("/")
    if len(parts) >= 2:
        candidate = "/".join(parts[-2:])
        if candidate in REPO_MAP:
            return REPO_MAP[candidate]
        candidate = parts[-1].lower()
        if candidate in REPO_MAP:
            return REPO_MAP[candidate]
    return r.lower()


# ── Ground truth extraction ────────────────────────────────────────────────────
def load_ground_truth(qid: str) -> set:
    """Return set of (repo, file) tuples from ground truth."""
    folder = GT_BASE / f"question_{qid}"
    path = folder / "ground_truth_enhanced.json"
    if not path.exists():
        return set()
    d = json.loads(path.read_text())
    result = set()
    for entry in d.get("impacted_files", []):
        repo = norm_repo(entry["repo"])
        file = entry["file"].strip()
        result.add((repo, file))
    return result


# ── File extraction helpers for MCP answers ───────────────────────────────────

KNOWN_REPO_KEYS = {"prometheus", "mimir", "loki", "thanos", "grafana", "tempo",
                   "helm", "argocd", "argo-cd", "opentelemetry-operator",
                   "opentelemetry-collector-contrib", "external-secrets",
                   "ingress-nginx", "jaeger"}

def _extract_from_list_of_obj(items, default_repo=None) -> set:
    """Extract (repo, file) from a list of dicts with 'file' and optional 'repo'."""
    result = set()
    for item in items:
        if isinstance(item, str):
            if ":" in item:
                r, f = item.split(":", 1)
                result.add((norm_repo(r), f.strip()))
            elif "/" in item:
                # Assume file path, use default_repo
                if default_repo:
                    result.add((norm_repo(default_repo), item.strip()))
        elif isinstance(item, dict):
            repo = item.get("repo") or item.get("source_repo") or default_repo
            file = item.get("file") or item.get("path") or item.get("filename")
            if file and repo:
                result.add((norm_repo(repo), file.strip()))
    return result


def _extract_from_dict_of_lists(d: dict) -> set:
    """Extract (repo, file) from {repo: [files]} or {repo: [{file:..., ...}]}."""
    result = set()
    for repo_key, files in d.items():
        if not isinstance(files, (list, dict)):
            continue
        if isinstance(files, list):
            for item in files:
                if isinstance(item, str):
                    result.add((norm_repo(repo_key), item.strip()))
                elif isinstance(item, dict):
                    f = item.get("file") or item.get("path") or item.get("filename")
                    if f:
                        result.add((norm_repo(repo_key), f.strip()))
        elif isinstance(files, dict):
            # {file: description}
            for f in files.keys():
                result.add((norm_repo(repo_key), f.strip()))
    return result


def _extract_files_recursive(obj, depth=0, parent_repo=None) -> set:
    """Recursively find all (repo, file) pairs in an arbitrary structure."""
    if depth > 6:
        return set()
    result = set()
    if isinstance(obj, dict):
        # If dict has repo/file at this level
        repo = obj.get("repo") or obj.get("source_repo") or parent_repo
        file = obj.get("file") or obj.get("path") or obj.get("filename")
        if file and repo:
            result.add((norm_repo(repo), str(file).strip()))

        # Check if dict keys are repo names → treat as {repo: [items]}
        repo_key_count = sum(1 for k in obj.keys() if norm_repo(k) in KNOWN_REPO_KEYS)
        if repo_key_count >= 1:
            for k, v in obj.items():
                if norm_repo(k) in KNOWN_REPO_KEYS:
                    result |= _extract_files_recursive(v, depth+1, parent_repo=k)
                elif k not in ("repo", "source_repo", "file", "path", "filename"):
                    result |= _extract_files_recursive(v, depth+1, parent_repo=parent_repo)
        else:
            for k, v in obj.items():
                result |= _extract_files_recursive(v, depth+1, parent_repo=parent_repo)
    elif isinstance(obj, list):
        for item in obj:
            result |= _extract_files_recursive(item, depth+1, parent_repo=parent_repo)
    return result


def extract_mcp_files(qid: str) -> set:
    """Extract predicted (repo, file) from MCP answer."""
    path = MCP_BASE / qid / "answer.json"
    if not path.exists():
        return set()
    d = json.loads(path.read_text())

    result = set()

    # Strategy 1: expected_files
    if "expected_files" in d:
        for entry in d["expected_files"]:
            repo = entry.get("repo", "")
            for f in entry.get("files", []):
                result.add((norm_repo(repo), f.strip()))
        if result:
            return result

    # Strategy 2: affected_files at top level
    if "affected_files" in d and isinstance(d["affected_files"], dict):
        result |= _extract_from_dict_of_lists(d["affected_files"])
        if result:
            return result

    # Strategy 3: answer field
    if "answer" not in d:
        return result

    answer = d["answer"]

    if isinstance(answer, str):
        # Nothing structured to extract from string MCP answers here
        return result

    if not isinstance(answer, dict):
        return result

    # Strategy 3a: files_list = ["repo:file"]
    if "files_list" in answer:
        for item in answer["files_list"]:
            if isinstance(item, str) and ":" in item:
                r, f = item.split(":", 1)
                result.add((norm_repo(r), f.strip()))
            elif isinstance(item, str):
                result.add(("unknown", item.strip()))
        if result:
            return result

    # Strategy 3b: affected_files inside answer
    if "affected_files" in answer and isinstance(answer["affected_files"], dict):
        result |= _extract_from_dict_of_lists(answer["affected_files"])
        if result:
            return result

    # Strategy 3c: files_to_modify / files_to_change / files_changed / impacted_files
    for key in ("files_to_modify", "files_to_change", "files_changed",
                "impacted_files", "breaking_files", "affected"):
        if key in answer and isinstance(answer[key], list):
            result |= _extract_from_list_of_obj(answer[key])

    if result:
        return result

    # Strategy 3d: answer keys are repo names
    if any(norm_repo(k) in KNOWN_REPO_KEYS for k in answer.keys()):
        repo_keys = {k: v for k, v in answer.items()
                     if norm_repo(k) in KNOWN_REPO_KEYS and isinstance(v, list)}
        if repo_keys:
            result |= _extract_from_dict_of_lists(repo_keys)
            if result:
                return result

    # Strategy 3e: recursive extraction (catches varied nested structures)
    result |= _extract_files_recursive(answer)

    return result


# ── File extraction helpers for non-MCP answers ───────────────────────────────

# Patterns for file paths in text: "repo/some/path.go" lines
FILE_LINE_PATTERN = re.compile(
    r"[-*•]\s*(?:`|``)?"                        # bullet + optional backtick
    r"([a-z][\w\-\.]+)/([a-zA-Z0-9_\-\./]+\.\w+)"  # repo/path.ext
    r"(?:`|``)?",                                  # optional closing backtick
)

SECTION_SPLIT = re.compile(r"\n[-*•]\s*")


def extract_files_from_text(text: str) -> set:
    """Extract (repo, file) pairs from free-form text."""
    result = set()
    for m in FILE_LINE_PATTERN.finditer(text):
        repo_candidate, file_path = m.group(1), m.group(2)
        r = norm_repo(repo_candidate)
        if r in KNOWN_REPO_KEYS or "/" in repo_candidate:
            result.add((r, file_path.strip()))
    return result


def extract_nomcp_files(qid: str) -> set:
    """Extract predicted (repo, file) from no-MCP answer."""
    path = NOMCP_BASE / qid / "answer.json"
    if not path.exists():
        return set()
    d = json.loads(path.read_text())
    result = set()

    # Strategy 1: llm_condensed_answer "FILES:" section
    condensed = d.get("llm_condensed_answer", "")
    if condensed:
        # Find FILES: section
        files_section = ""
        if "FILES:" in condensed:
            files_section = condensed.split("FILES:", 1)[1]
        elif "FILES\n" in condensed:
            files_section = condensed.split("FILES\n", 1)[1]
        target = files_section or condensed
        result |= extract_files_from_text(target)
        if result:
            return result

    # Strategy 2: answer as string
    answer = d.get("answer", "")
    if isinstance(answer, str) and answer:
        result |= extract_files_from_text(answer)
        if result:
            return result

    # Strategy 3: answer as dict → recursive extraction
    if isinstance(answer, dict):
        result |= _extract_files_recursive(answer)
        if result:
            return result

    return result


# ── Metrics extraction ─────────────────────────────────────────────────────────

def extract_mcp_metrics(qid: str) -> dict:
    path = MCP_BASE / qid / "answer.json"
    if not path.exists():
        return {}
    d = json.loads(path.read_text())

    # Tool calls
    tool_calls = (d.get("tool_calls_count") or
                  d.get("total_tool_calls") or
                  (d.get("answer", {}) or {}).get("total_tool_calls") if isinstance(d.get("answer"), dict) else None)

    # Try to count tool_calls list
    if tool_calls is None and "tool_calls" in d and isinstance(d["tool_calls"], list):
        tool_calls = len(d["tool_calls"])

    return {
        "tool_calls": tool_calls,
        "input_tokens": None,
        "output_tokens": None,
        "time_seconds": None,
        "cost_usd": None,
    }


def extract_nomcp_metrics(qid: str) -> dict:
    path = NOMCP_BASE / qid / "answer.json"
    if not path.exists():
        return {}
    d = json.loads(path.read_text())
    m = d.get("metrics", {})
    if not m:
        return {"tool_calls": None, "input_tokens": None, "output_tokens": None,
                "time_seconds": None, "cost_usd": None}

    # Input tokens
    in_tok = (m.get("input_tokens_estimate") or
              m.get("total_estimated_input_tokens") or
              m.get("total_input_tokens") or
              (m.get("token_tracking", {}) or {}).get("total_input_tokens"))

    # Output tokens
    out_tok = (m.get("output_tokens_estimate") or
               m.get("total_estimated_output_tokens") or
               m.get("estimated_output_tokens") or
               (m.get("token_tracking", {}) or {}).get("estimated_output_tokens"))

    # Tool calls
    tc = (m.get("total_tool_calls") or
          (m.get("time_tracking", {}) or {}).get("total_tool_calls"))
    if tc is None and "tool_calls" in m and isinstance(m["tool_calls"], list):
        tc = len(m["tool_calls"])

    # Time
    tt = m.get("time_tracking", {}) or {}
    time_s = (tt.get("total_elapsed_time_seconds") or
              tt.get("total_elapsed_seconds") or
              tt.get("elapsed_seconds"))

    # Guard: ensure numeric
    in_tok  = in_tok  if isinstance(in_tok,  (int, float)) else None
    out_tok = out_tok if isinstance(out_tok, (int, float)) else None

    cost = None
    if in_tok is not None and out_tok is not None:
        cost = in_tok * INPUT_COST_PER_TOKEN + out_tok * OUTPUT_COST_PER_TOKEN

    return {
        "tool_calls": tc,
        "input_tokens": in_tok,
        "output_tokens": out_tok,
        "time_seconds": time_s,
        "cost_usd": cost,
    }


# ── Scoring ───────────────────────────────────────────────────────────────────

def score(predicted: set, ground_truth: set) -> dict:
    tp = len(predicted & ground_truth)
    fp = len(predicted - ground_truth)
    fn = len(ground_truth - predicted)
    if not ground_truth:
        # GT=0: recall is trivially 1; precision 1 if pred=0 else 0
        precision = 1.0 if not predicted else 0.0
        recall    = 1.0
        f1        = 1.0 if not predicted else 0.0
        return {"precision": precision, "recall": recall, "f1": f1,
                "tp": 0, "fp": fp, "fn": 0, "gt_count": 0, "pred_count": len(predicted)}
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)
          if (precision + recall) > 0 else 0.0)
    return {"precision": precision, "recall": recall, "f1": f1,
            "tp": tp, "fp": fp, "fn": fn,
            "gt_count": len(ground_truth), "pred_count": len(predicted)}


# ── Main evaluation loop ───────────────────────────────────────────────────────

def main():
    questions = sorted([
        d.name.replace("question_", "")
        for d in GT_BASE.iterdir()
        if d.is_dir() and d.name.startswith("question_")
    ])

    results = []
    mcp_totals = defaultdict(list)
    nomcp_totals = defaultdict(list)

    for qid in questions:
        gt = load_ground_truth(qid)
        mcp_pred = extract_mcp_files(qid)
        nomcp_pred = extract_nomcp_files(qid)

        mcp_score   = score(mcp_pred, gt)
        nomcp_score = score(nomcp_pred, gt)

        mcp_metrics   = extract_mcp_metrics(qid)
        nomcp_metrics = extract_nomcp_metrics(qid)

        category = "MIXED" if qid.startswith("MIXED") else "OBS"

        row = {
            "qid": qid,
            "category": category,
            "gt_count": len(gt),
            "mcp": {
                "predicted": len(mcp_pred),
                **mcp_score,
                **mcp_metrics,
            },
            "nomcp": {
                "predicted": len(nomcp_pred),
                **nomcp_score,
                **nomcp_metrics,
            },
            # Raw sets for debugging
            "_gt": sorted(gt),
            "_mcp_pred": sorted(mcp_pred),
            "_nomcp_pred": sorted(nomcp_pred),
        }
        results.append(row)

        # Accumulate for averages
        for k in ("precision", "recall", "f1"):
            if mcp_score[k] is not None:
                mcp_totals[k].append(mcp_score[k])
            if nomcp_score[k] is not None:
                nomcp_totals[k].append(nomcp_score[k])

        for k in ("tool_calls", "input_tokens", "output_tokens", "time_seconds", "cost_usd"):
            if mcp_metrics.get(k) is not None:
                mcp_totals[k].append(mcp_metrics[k])
            if nomcp_metrics.get(k) is not None:
                nomcp_totals[k].append(nomcp_metrics[k])

    avg = lambda lst: sum(lst) / len(lst) if lst else None
    total_sum = lambda lst: sum(lst) if lst else None

    summary = {
        "total_questions": len(questions),
        "mcp_avg": {k: avg(mcp_totals[k]) for k in mcp_totals},
        "nomcp_avg": {k: avg(nomcp_totals[k]) for k in nomcp_totals},
        "mcp_total": {k: total_sum(mcp_totals[k]) for k in ("input_tokens", "output_tokens", "cost_usd", "tool_calls", "time_seconds")},
        "nomcp_total": {k: total_sum(nomcp_totals[k]) for k in ("input_tokens", "output_tokens", "cost_usd", "tool_calls", "time_seconds")},
    }

    return results, summary


# ── Report generation ─────────────────────────────────────────────────────────

def fmt(v, decimals=3):
    if v is None:
        return "N/A"
    if isinstance(v, float):
        return f"{v:.{decimals}f}"
    if isinstance(v, int):
        return str(v)
    return str(v)

def pct(v):
    if v is None:
        return "N/A"
    return f"{v*100:.1f}%"

def fmt_cost(v):
    if v is None:
        return "N/A"
    return f"${v:.4f}"

def fmt_tokens(v):
    if v is None:
        return "N/A"
    return f"{v:,.0f}"


def build_report(results, summary) -> str:
    lines = []
    a = lines.append

    a("# KubeCluster45 Evaluation Report")
    a("")
    a("**Model:** Claude Opus 4.6  ")
    a("**Pricing:** $5.00/M input tokens · $25.00/M output tokens  ")
    a("**Dataset:** 45 questions (11 MIXED cross-repo change impact · 34 OBS interface/type change impact)")
    a("**Evaluated:** MCP-assisted vs Unaided (no MCP, no web search)")
    a("")
    a("---")
    a("")

    # ── Overall accuracy table ────────────────────────────────────────────────
    a("## 1. Accuracy Summary (All 45 Questions)")
    a("")
    a("| Metric | MCP | No-MCP | Delta |")
    a("|--------|-----|--------|-------|")

    def delta_str(mcp_v, nomcp_v, higher_better=True):
        if mcp_v is None or nomcp_v is None:
            return "N/A"
        d = mcp_v - nomcp_v
        sign = "+" if d >= 0 else ""
        if higher_better:
            emoji = " ▲" if d > 0.001 else (" ▼" if d < -0.001 else " ≈")
        else:
            emoji = " ▼" if d > 0.001 else (" ▲" if d < -0.001 else " ≈")
        return f"{sign}{d*100:.1f}pp{emoji}"

    ma = summary["mcp_avg"]
    na = summary["nomcp_avg"]
    a(f"| **Precision** | {pct(ma.get('precision'))} | {pct(na.get('precision'))} | {delta_str(ma.get('precision'), na.get('precision'))} |")
    a(f"| **Recall**    | {pct(ma.get('recall'))} | {pct(na.get('recall'))} | {delta_str(ma.get('recall'), na.get('recall'))} |")
    a(f"| **F1 Score**  | {pct(ma.get('f1'))} | {pct(na.get('f1'))} | {delta_str(ma.get('f1'), na.get('f1'))} |")
    a("")

    # ── Accuracy by category ──────────────────────────────────────────────────
    a("## 2. Accuracy by Category")
    a("")
    for cat in ["MIXED", "OBS"]:
        cat_results = [r for r in results if r["category"] == cat]
        mcp_p  = [r["mcp"]["precision"] for r in cat_results if r["mcp"]["precision"] is not None]
        mcp_r  = [r["mcp"]["recall"]    for r in cat_results if r["mcp"]["recall"] is not None]
        mcp_f  = [r["mcp"]["f1"]        for r in cat_results if r["mcp"]["f1"] is not None]
        nm_p   = [r["nomcp"]["precision"] for r in cat_results if r["nomcp"]["precision"] is not None]
        nm_r   = [r["nomcp"]["recall"]    for r in cat_results if r["nomcp"]["recall"] is not None]
        nm_f   = [r["nomcp"]["f1"]        for r in cat_results if r["nomcp"]["f1"] is not None]
        avg_   = lambda lst: sum(lst)/len(lst) if lst else None
        a(f"### {cat} Questions ({len(cat_results)} total)")
        a("")
        a("| Metric | MCP | No-MCP |")
        a("|--------|-----|--------|")
        a(f"| Precision | {pct(avg_(mcp_p))} | {pct(avg_(nm_p))} |")
        a(f"| Recall    | {pct(avg_(mcp_r))} | {pct(avg_(nm_r))} |")
        a(f"| F1 Score  | {pct(avg_(mcp_f))} | {pct(avg_(nm_f))} |")
        a("")

    # ── Cost & efficiency ─────────────────────────────────────────────────────
    a("## 3. Cost & Efficiency (No-MCP)")
    a("")
    a("> Note: MCP answers did not consistently include token/cost metadata, so cost analysis focuses on the no-MCP run.")
    a("")

    nt = summary["nomcp_total"]
    na = summary["nomcp_avg"]
    n_with_cost = len([r for r in results if r["nomcp"].get("cost_usd") is not None])

    a("| Metric | Total | Per Question (avg) | Questions w/ data |")
    a("|--------|---------|--------------------|-------------------|")
    a(f"| Input tokens  | {fmt_tokens(nt.get('input_tokens'))} | {fmt_tokens(na.get('input_tokens'))} | {n_with_cost}/45 |")
    a(f"| Output tokens | {fmt_tokens(nt.get('output_tokens'))} | {fmt_tokens(na.get('output_tokens'))} | {n_with_cost}/45 |")
    a(f"| Estimated cost | {fmt_cost(nt.get('cost_usd'))} | {fmt_cost(na.get('cost_usd'))} | {n_with_cost}/45 |")
    a(f"| Tool calls    | {fmt(nt.get('tool_calls'))} | {fmt(na.get('tool_calls'), 1)} | {len([r for r in results if r['nomcp'].get('tool_calls') is not None])}/45 |")
    a(f"| Time (seconds) | {fmt(nt.get('time_seconds'))} | {fmt(na.get('time_seconds'), 1)} | {len([r for r in results if r['nomcp'].get('time_seconds') is not None])}/45 |")
    a("")

    mcp_tc_count = len([r for r in results if r["mcp"].get("tool_calls") is not None])
    mcp_tc_total = summary["mcp_total"].get("tool_calls")
    mcp_tc_avg   = summary["mcp_avg"].get("tool_calls")
    a("### MCP Tool Calls")
    a("")
    a("| Metric | Total | Per Question (avg) | Questions w/ data |")
    a("|--------|---------|--------------------|-------------------|")
    a(f"| MCP tool calls | {fmt(mcp_tc_total)} | {fmt(mcp_tc_avg, 1)} | {mcp_tc_count}/45 |")
    a("")

    # ── Cost per incorrect file ───────────────────────────────────────────────
    a("## 4. Cost per Incorrect Prediction (No-MCP)")
    a("")
    a("This metric measures the cost efficiency: how much does each false-positive file identification cost?")
    a("")

    nm_fp_list = [r["nomcp"]["fp"] for r in results]
    nm_cost_list = [r["nomcp"].get("cost_usd") for r in results if r["nomcp"].get("cost_usd") is not None]

    total_fp = sum(nm_fp_list)
    total_cost = sum(c for c in nm_cost_list) if nm_cost_list else None
    cost_per_fp = (total_cost / total_fp) if (total_cost and total_fp > 0) else None
    total_fn = sum(r["nomcp"]["fn"] for r in results)
    total_tp = sum(r["nomcp"]["tp"] for r in results)

    a(f"- **Total true positives (no-MCP):** {total_tp}")
    a(f"- **Total false positives (no-MCP):** {total_fp}")
    a(f"- **Total false negatives (no-MCP):** {total_fn}")
    a(f"- **Total estimated cost (no-MCP):** {fmt_cost(total_cost)}")
    a(f"- **Cost per false positive:** {fmt_cost(cost_per_fp)}")
    a("")

    # MCP fp/fn
    mcp_total_fp = sum(r["mcp"]["fp"] for r in results)
    mcp_total_fn = sum(r["mcp"]["fn"] for r in results)
    mcp_total_tp = sum(r["mcp"]["tp"] for r in results)
    a(f"- **Total true positives (MCP):** {mcp_total_tp}")
    a(f"- **Total false positives (MCP):** {mcp_total_fp}")
    a(f"- **Total false negatives (MCP):** {mcp_total_fn}")
    a("")

    # ── Per-question results table ────────────────────────────────────────────
    a("## 5. Per-Question Results")
    a("")
    a("| Question | GT Files | MCP Pred | MCP P | MCP R | MCP F1 | NoMCP Pred | NoMCP P | NoMCP R | NoMCP F1 | NoMCP Tools | NoMCP Time(s) | NoMCP Cost |")
    a("|----------|----------|---------|-------|-------|--------|-----------|---------|---------|---------|------------|--------------|------------|")

    for r in results:
        mcp  = r["mcp"]
        nm   = r["nomcp"]
        a(
            f"| {r['qid']} | {r['gt_count']} | {mcp['pred_count']} | "
            f"{pct(mcp['precision'])} | {pct(mcp['recall'])} | {pct(mcp['f1'])} | "
            f"{nm['pred_count']} | {pct(nm['precision'])} | {pct(nm['recall'])} | {pct(nm['f1'])} | "
            f"{fmt(nm.get('tool_calls'))} | {fmt(nm.get('time_seconds'), 0)} | {fmt_cost(nm.get('cost_usd'))} |"
        )

    a("")

    # ── False positive analysis ───────────────────────────────────────────────
    a("## 6. Worst-Case False Positives (No-MCP, top 10 by FP count)")
    a("")
    a("| Question | FP | FN | TP | GT |")
    a("|----------|-----|-----|-----|-----|")
    sorted_fp = sorted(results, key=lambda r: r["nomcp"]["fp"], reverse=True)[:10]
    for r in sorted_fp:
        nm = r["nomcp"]
        a(f"| {r['qid']} | {nm['fp']} | {nm['fn']} | {nm['tp']} | {r['gt_count']} |")
    a("")

    a("## 7. Worst-Case False Positives (MCP, top 10 by FP count)")
    a("")
    a("| Question | FP | FN | TP | GT |")
    a("|----------|-----|-----|-----|-----|")
    sorted_fp_mcp = sorted(results, key=lambda r: r["mcp"]["fp"], reverse=True)[:10]
    for r in sorted_fp_mcp:
        mcp = r["mcp"]
        a(f"| {r['qid']} | {mcp['fp']} | {mcp['fn']} | {mcp['tp']} | {r['gt_count']} |")
    a("")

    # ── Questions with perfect recall ─────────────────────────────────────────
    a("## 8. Perfect Recall Questions")
    a("")
    a("Questions where the model found all ground-truth files (recall = 100%).")
    a("")
    a("| Question | MCP Perfect? | NoMCP Perfect? |")
    a("|----------|-------------|----------------|")
    for r in results:
        mcp_perfect  = "✓" if r["mcp"]["recall"] == 1.0 else "✗"
        nm_perfect   = "✓" if r["nomcp"]["recall"] == 1.0 else "✗"
        if r["mcp"]["recall"] == 1.0 or r["nomcp"]["recall"] == 1.0:
            a(f"| {r['qid']} | {mcp_perfect} | {nm_perfect} |")
    a("")

    # ── Key findings ──────────────────────────────────────────────────────────
    a("## 9. Key Findings")
    a("")

    mcp_better_f1  = sum(1 for r in results if (r["mcp"]["f1"] or 0) > (r["nomcp"]["f1"] or 0))
    nomcp_better_f1 = sum(1 for r in results if (r["nomcp"]["f1"] or 0) > (r["mcp"]["f1"] or 0))
    tied = len(results) - mcp_better_f1 - nomcp_better_f1

    ma_f1 = summary["mcp_avg"].get("f1") or 0
    na_f1 = summary["nomcp_avg"].get("f1") or 0
    ma_p  = summary["mcp_avg"].get("precision") or 0
    na_p  = summary["nomcp_avg"].get("precision") or 0
    ma_r  = summary["mcp_avg"].get("recall") or 0
    na_r  = summary["nomcp_avg"].get("recall") or 0

    a(f"1. **MCP vs No-MCP F1:** MCP wins on {mcp_better_f1} questions, No-MCP wins on {nomcp_better_f1}, tied on {tied}.")
    a(f"2. **Average F1:** MCP = {pct(ma_f1)}, No-MCP = {pct(na_f1)} (delta = {(ma_f1-na_f1)*100:+.1f}pp).")
    a(f"3. **Precision:** MCP = {pct(ma_p)}, No-MCP = {pct(na_p)} — {'MCP is more precise' if ma_p > na_p else 'No-MCP is more precise'}.")
    a(f"4. **Recall:** MCP = {pct(ma_r)}, No-MCP = {pct(na_r)} — {'MCP has higher recall' if ma_r > na_r else 'No-MCP has higher recall'}.")

    if total_cost:
        a(f"5. **Cost (No-MCP):** ~{fmt_cost(total_cost)} total across 45 questions ({fmt_cost(total_cost/len(nm_cost_list))} avg per question with cost data).")

    a(f"6. **False positives:** MCP produced {mcp_total_fp} FP files total vs {total_fp} for No-MCP.")
    a(f"7. **Missed files (FN):** MCP missed {mcp_total_fn} GT files total vs {total_fn} for No-MCP.")
    a("")
    a("---")
    a("")
    a("*Report generated by `src/eval_kube45.py`. Ground truth: `results/KubeCluster45/question_*/ground_truth_enhanced.json`. Answers: `New_eval_kube45/`.*")

    return "\n".join(lines)


if __name__ == "__main__":
    results, summary = main()

    # Save raw results JSON
    raw_out = OUT_DIR / "kube45_eval_raw.json"
    raw_out.write_text(json.dumps({
        "summary": summary,
        "results": [{k: v for k, v in r.items() if not k.startswith("_")} for r in results],
    }, indent=2))
    print(f"Raw results → {raw_out}")

    # Build and save markdown report
    report = build_report(results, summary)
    report_out = OUT_DIR / "kube45_eval_report.md"
    report_out.write_text(report)
    print(f"Report → {report_out}")

    # Print quick summary
    ma = summary["mcp_avg"]
    na = summary["nomcp_avg"]
    print(f"\n{'='*60}")
    print(f"MCP  → P={pct(ma.get('precision'))} R={pct(ma.get('recall'))} F1={pct(ma.get('f1'))}")
    print(f"NoMCP→ P={pct(na.get('precision'))} R={pct(na.get('recall'))} F1={pct(na.get('f1'))}")
    total_cost = summary["nomcp_total"].get("cost_usd")
    print(f"NoMCP total cost: {fmt_cost(total_cost)}")
    print(f"{'='*60}")
