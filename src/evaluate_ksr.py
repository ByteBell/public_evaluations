#!/usr/bin/env python3
"""
KubeSingle65 evaluation script.

Scores model answers in results/KubeSingle65/KSR_TC* folders against
ground_truth_enhanced.json using the fact-based marking scheme from evaluation.md.

Key differences from evaluate_enhanced.py:
  - Works with KSR_TC* folder naming (not question_*)
  - Handles all KubeSingle65 answer formats (MCP, direct Claude, direct Grok, Gemini)
  - No model overriding — judge/extractor models are CLI args with cheap defaults
  - --up-to  limit: process only up to a given question ID (e.g. KSR_TC020)

Scoring scheme (per evaluation.md):
  Per correct file (max +10):
    File Detection   4  — automated binary
    Breaking Pattern 0-2 — LLM judge
    Severity         0-1 — LLM judge
    Fix Quality      0-3 — LLM judge
  Per hallucinated file: -5 (automated)
  Per false positive correctly omitted: +2 (automated)

  max_possible = (total_impacted × 10) + (total_false_positives × 2)
  final_pct    = raw_score / max_possible × 100  (can go negative)

Output:
  <KSR_TCxxx>/enhanced_evaluation.json
  <results_dir>/enhanced_analysis_summary.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# ─── Defaults ─────────────────────────────────────────────────────────────────

DEFAULT_EXTRACTOR = "arcee-ai/trinity-mini"
DEFAULT_JUDGE     = "qwen/qwen3-30b-a3b-thinking-2507"

# ─── Repo alias normalisation ─────────────────────────────────────────────────

REPO_ALIASES: dict[str, str] = {
    "argocd":                          "argo-cd",
    "otel-collector":                  "opentelemetry-collector",
    "otel-collector-contrib":          "opentelemetry-collector-contrib",
    "k8s":                             "kubernetes",
    "otel-operator":                   "opentelemetry-operator",
    "oteloperator":                    "opentelemetry-operator",
    "opentelemetry-collector-contrib": "opentelemetry-collector-contrib",
}


def normalize_repo(repo: str) -> str:
    r = repo.lower().strip()
    return REPO_ALIASES.get(r, r)


def normalize_path(path: str) -> str:
    p = path.strip()
    if p.startswith("./"):
        p = p[2:]
    elif p.startswith("/"):
        p = p[1:]
    return p


# ─── Answer-format normalisation ──────────────────────────────────────────────

_SKIP_FILES = frozenset({
    "question.json",
    "evaluation.json",
    "analysis.json",
    "enhanced_evaluation.json",
    "analysis_summary.json",
    "enhanced_analysis_summary.json",
    "ground_truth.json",
    "ground_truth_enhanced.json",
})

# Maps filename stem patterns → friendly model identifier
_STEM_MODEL_MAP: list[tuple[re.Pattern, str]] = [
    (re.compile(r"claude[_.-]sonnet[_.-]4[_.-]6", re.I),   "anthropic/claude-sonnet-4.6"),
    (re.compile(r"claude[_.-]haiku",               re.I),   "anthropic/claude-haiku-4.5"),
    (re.compile(r"grok[_.-]code[_.-]fast",         re.I),   "x-ai/grok-code-fast-1"),
    (re.compile(r"gemini[_.-]pro[_.-]3",           re.I),   "google/gemini-pro-3.1"),
    (re.compile(r"gemini",                         re.I),   "google/gemini"),
    (re.compile(r"gpt[_.-]5",                      re.I),   "openai/gpt-5"),
    (re.compile(r"deepseek",                       re.I),   "deepseek/deepseek-chat"),
]


def _model_from_stem(stem: str) -> str:
    """Derive a model identifier from an answer filename stem."""
    for pat, name in _STEM_MODEL_MAP:
        if pat.search(stem):
            # If it's an MCP variant, append a suffix
            if stem.startswith("mcp_"):
                return name + " (mcp)"
            return name
    # Fall back: strip _answer suffix and humanise
    clean = re.sub(r"_answer$", "", stem, flags=re.I)
    if stem.startswith("mcp_"):
        clean = re.sub(r"^mcp_", "", clean, flags=re.I)
        return clean.replace("_", "/") + " (mcp)"
    return clean.replace("_", " ")


def _dict_answer_to_text(d: dict) -> str:
    """Convert a structured dict answer into a plain text string for extraction."""
    parts: list[str] = []

    # Common top-level explanation fields
    for key in ("explanation", "summary", "analysis", "reasoning"):
        if key in d and d[key]:
            parts.append(str(d[key]))

    # File lists — various key names used across direct answer formats
    file_list_keys = (
        "impacted_files",
        "files_that_fail_to_compile",
        "files_with_runtime_changes",
        "files_with_test_failures",
        "affected_files",
        "breaking_files",
    )
    for fkey in file_list_keys:
        if fkey not in d:
            continue
        val = d[fkey]
        if not val:
            continue
        if isinstance(val, list):
            parts.append(f"[{fkey}]")
            for item in val:
                if isinstance(item, dict):
                    path = item.get("path") or item.get("file") or item.get("repo_file") or ""
                    reason = (
                        item.get("reason")
                        or item.get("explanation")
                        or item.get("why")
                        or item.get("impact")
                        or ""
                    )
                    fix = item.get("fix") or item.get("fix_suggestion") or item.get("suggested_fix") or ""
                    severity = item.get("severity") or item.get("type") or ""
                    entry = path
                    if severity:
                        entry += f" [{severity}]"
                    if reason:
                        entry += f": {reason}"
                    if fix:
                        entry += f" Fix: {fix}"
                    parts.append(entry)
                else:
                    parts.append(str(item))
        elif isinstance(val, str):
            parts.append(f"[{fkey}] {val}")

    # If nothing found, just serialise the whole dict
    if not parts:
        parts.append(json.dumps(d, indent=2)[:6000])

    return "\n".join(parts)


def load_model_answers(folder: Path) -> list[dict]:
    """Load all model answer files from a KSR_TC folder.

    Handles three formats:
      1. MCP format: top-level `answer` string + nested `metadata` dict
      2. Direct dict format: top-level `answer` dict + `metadata` or `time_seconds`
      3. Simple format: top-level `answer` string + `tokens` dict
    """
    answer_files = sorted(
        f for f in folder.iterdir()
        if f.suffix == ".json" and f.name not in _SKIP_FILES
    )

    answers: list[dict] = []
    for af in answer_files:
        try:
            with open(af) as fh:
                raw = json.load(fh)
        except (json.JSONDecodeError, OSError) as e:
            answers.append({
                "model":       af.stem,
                "status":      "parse_error",
                "full_answer": "",
                "answer":      "",
                "error":       str(e),
            })
            continue

        meta   = raw.get("metadata", {})
        is_mcp = af.stem.startswith("mcp_")

        # ── Model name ────────────────────────────────────────────────────────
        model_id = (
            meta.get("model")           # MCP files store it here
            or raw.get("model")
            or _model_from_stem(af.stem)
        )
        # Tag MCP/agentic runs so they appear separately in the leaderboard
        if is_mcp and not model_id.endswith("(mcp)"):
            model_id = model_id + " (mcp)"

        # ── Status ────────────────────────────────────────────────────────────
        status = meta.get("status") or raw.get("status", "success")
        # Simple / direct files don't carry a status field — treat as success
        if status not in ("success", "error", "timeout", "parse_error"):
            status = "success"

        # ── Answer text ───────────────────────────────────────────────────────
        raw_answer = raw.get("answer") or raw.get("full_answer")

        # Handle formats where answer content is spread across top-level keys
        # e.g. Claude direct: {"answer": "...", "files_that_fail_to_compile": [...], "reasoning": "..."}
        # e.g. Grok direct: {"files": ["path1", "path2"], "time_taken_seconds": ...}
        _top_file_keys = (
            "files", "impacted_files",
            "files_that_fail_to_compile", "files_with_runtime_changes",
            "files_with_test_failures", "affected_files", "breaking_files",
        )
        _top_text_keys = ("reasoning", "explanation", "analysis", "summary")

        if raw_answer is None:
            # No answer/full_answer key — check for top-level file list (Grok TC005-style)
            top_files = None
            for k in _top_file_keys:
                if k in raw and raw[k]:
                    top_files = raw[k]
                    break
            if top_files is not None:
                # Build a pseudo-answer text from the top-level file list
                if isinstance(top_files, list):
                    file_lines = []
                    for item in top_files:
                        if isinstance(item, dict):
                            path = item.get("path") or item.get("file") or ""
                            reason = item.get("reason") or item.get("explanation") or ""
                            file_lines.append(f"{path}: {reason}" if reason else path)
                        else:
                            file_lines.append(str(item))
                    raw_answer = "The following files are impacted:\n" + "\n".join(file_lines)
                else:
                    raw_answer = str(top_files)
            else:
                raw_answer = ""

        if isinstance(raw_answer, dict):
            full_answer = _dict_answer_to_text(raw_answer)
        else:
            full_answer = str(raw_answer)

        # Append any supplementary top-level structured data
        # (e.g. when answer is a plain string but files_that_fail_to_compile is at top-level)
        if full_answer:
            extra_parts: list[str] = []
            for k in _top_file_keys:
                if k in raw and raw[k] and k != "answer":
                    val = raw[k]
                    if isinstance(val, list) and val:
                        extra_parts.append(f"[{k}]")
                        for item in val:
                            if isinstance(item, dict):
                                path = item.get("path") or item.get("file") or ""
                                reason = item.get("reason") or item.get("explanation") or ""
                                fix = item.get("fix") or item.get("suggested_fix") or ""
                                sev = item.get("severity") or item.get("type") or ""
                                entry = path
                                if sev:
                                    entry += f" [{sev}]"
                                if reason:
                                    entry += f": {reason}"
                                if fix:
                                    entry += f" Fix: {fix}"
                                extra_parts.append(entry)
                            else:
                                extra_parts.append(str(item))
            for k in _top_text_keys:
                if k in raw and raw[k] and k not in full_answer[:100]:
                    extra_parts.append(f"[{k}] {raw[k]}")
            if extra_parts:
                full_answer = full_answer + "\n\n" + "\n".join(extra_parts)

        # ── Tokens / cost ─────────────────────────────────────────────────────
        tok_src = meta.get("tokens") or raw.get("tokens") or {}
        input_tokens  = tok_src.get("input")  or tok_src.get("input_tokens")  or tok_src.get("input_tokens_estimate",  0)
        output_tokens = tok_src.get("output") or tok_src.get("output_tokens") or tok_src.get("output_tokens_estimate", 0)
        total_tokens  = tok_src.get("total")  or tok_src.get("total_tokens")  or tok_src.get("total_tokens_estimate",  0)
        if total_tokens == 0 and (input_tokens or output_tokens):
            total_tokens = (input_tokens or 0) + (output_tokens or 0)

        cost_src = raw.get("cost") or meta.get("cost") or {}
        cost_usd = cost_src.get("cost_usd", 0.0)

        answers.append({
            "model":            model_id,
            "status":           status,
            "full_answer":      full_answer,
            "answer":           full_answer,
            "tool_calls_count": meta.get("tool_calls_count", 0) or raw.get("tool_calls_count", 0),
            "input_tokens":     int(input_tokens or 0),
            "output_tokens":    int(output_tokens or 0),
            "total_tokens":     int(total_tokens or 0),
            "cost_usd":         float(cost_usd),
            "_source_file":     af.name,
        })

    return answers


def load_ground_truth_enhanced(folder: Path) -> dict | None:
    gt_file = folder / "ground_truth_enhanced.json"
    if not gt_file.exists():
        return None
    with open(gt_file) as f:
        return json.load(f)


# ─── Step 1: extract structured claims from model answer ──────────────────────


def extract_model_claims(
    answer_text: str,
    question: str,
    api_key: str,
    model: str,
) -> list[dict]:
    """Use cheap LLM to parse a model's answer into a structured file list."""
    answer_trunc = answer_text[:12_000]

    prompt = (
        "You are a JSON extractor for a code-impact-analysis benchmark.\n\n"
        "Extract ALL files the model claims are impacted by the code change described in the question.\n"
        "For each file extract:\n"
        "  - repo: the repository name (e.g. 'kubernetes', 'argo-cd', 'cert-manager')\n"
        "  - file: the file path within that repo (e.g. 'pkg/apis/v1/register.go')\n"
        "  - breaking_explanation: the model's explanation of WHY this file breaks "
        "(what code pattern is affected — be as specific as the answer allows)\n"
        "  - severity: map to exactly one of: 'compile_error', 'runtime_behavior_change', "
        "'test_failure', 'test_only', 'unknown'\n"
        "  - fix_suggestion: the specific fix the model recommends for this file "
        "(empty string '' if not mentioned)\n\n"
        f"QUESTION:\n{question}\n\n"
        f"MODEL ANSWER:\n{answer_trunc}\n\n"
        "Return ONLY valid JSON — no markdown fences, no commentary:\n"
        '{"files": [{"repo": "...", "file": "...", "breaking_explanation": "...", '
        '"severity": "...", "fix_suggestion": "..."}]}\n\n'
        "If the model explicitly states nothing breaks or lists no files, return {\"files\": []}."
    )

    for attempt in range(1, 4):
        try:
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0,
                    "max_tokens": 8000,
                },
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                timeout=90,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"      [extract] request failed (attempt {attempt}/3): {e}")
            if attempt < 3:
                time.sleep(attempt * 3)
                continue
            return []

        content = (
            resp.json()
            .get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )

        # Strip markdown fences if present
        if content.startswith("```"):
            content = "\n".join(content.split("\n")[1:])
        if content.endswith("```"):
            content = content[:-3].rstrip()

        try:
            parsed = json.loads(content)
            valid = []
            for fitem in parsed.get("files", []):
                if isinstance(fitem, dict) and fitem.get("repo") and fitem.get("file"):
                    valid.append({
                        "repo":                 str(fitem.get("repo", "")),
                        "file":                 str(fitem.get("file", "")),
                        "breaking_explanation": str(fitem.get("breaking_explanation", "")),
                        "severity":             str(fitem.get("severity", "unknown")),
                        "fix_suggestion":       str(fitem.get("fix_suggestion", "")),
                    })
            return valid
        except (json.JSONDecodeError, ValueError, AttributeError):
            if attempt < 3:
                time.sleep(attempt * 3)
                continue
            return []

    return []


# ─── Step 2: LLM judge — score per-file dimensions ────────────────────────────

_FALLBACK_SCORE = {
    "breaking_pattern": 0,
    "severity":         0,
    "fix_quality":      0,
    "notes":            "judge failed",
}


def _judge_batch(
    batch: list[dict],
    gt_patterns: list[dict],
    api_key: str,
    judge_model: str,
) -> list[dict]:
    pattern_descs = "\n".join(
        f"  - {p['id']}: {p.get('example', '')[:200]} — {p.get('why_breaks', '')[:200]}"
        for p in gt_patterns
    )

    files_to_score = []
    for item in batch:
        gt = item["gt_file"]
        m  = item["model_file"]
        files_to_score.append({
            "repo":              gt["repo"],
            "file":              gt["file"],
            "gt_patterns":       gt.get("breaking_patterns", []),
            "gt_severity":       gt.get("severity", "unknown"),
            "gt_fix":            gt.get("suggested_fix", ""),
            "model_explanation": m.get("breaking_explanation", ""),
            "model_severity":    m.get("severity", "unknown"),
            "model_fix":         m.get("fix_suggestion", ""),
        })

    prompt = (
        "You are a code-impact-analysis scoring judge.\n\n"
        f"Breaking patterns defined for this change:\n{pattern_descs}\n\n"
        "Score each file on 3 dimensions:\n"
        "1. BREAKING_PATTERN (integer 0-2): fraction of GT patterns the model correctly identified\n"
        "   2 = all GT patterns identified  |  1 = some/partial  |  0 = none/wrong\n"
        "2. SEVERITY (integer 0-1): did the model correctly classify the severity?\n"
        "   1 = matches (or logically equivalent)  |  0 = wrong or missing\n"
        "3. FIX_QUALITY (integer 0-3): how specific and correct is the model's fix vs GT?\n"
        "   3 = semantically equivalent to GT fix\n"
        "   2 = directionally correct but missing details\n"
        "   1 = mentions right concept but vague or partially wrong\n"
        "   0 = no fix stated, or completely wrong\n\n"
        f"FILES TO SCORE (JSON):\n{json.dumps(files_to_score, indent=2)}\n\n"
        "Return ONLY a JSON array with exactly one object per file, IN THE SAME ORDER:\n"
        '[{"repo":"...","file":"...","breaking_pattern":0-2,"severity":0-1,'
        '"fix_quality":0-3,"notes":"<20 words max>"}]'
    )

    for attempt in range(1, 4):
        try:
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json={
                    "model": judge_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0,
                    "max_tokens": 4000,
                },
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                timeout=120,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"      [judge] request failed (attempt {attempt}/3): {e}")
            if attempt < 3:
                time.sleep(attempt * 5)
                continue
            return [_FALLBACK_SCORE.copy() for _ in batch]

        content = (
            resp.json()
            .get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )
        if content.startswith("```"):
            content = "\n".join(content.split("\n")[1:])
        if content.endswith("```"):
            content = content[:-3].rstrip()

        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                parsed = parsed.get("scores", parsed.get("files", []))

            results = []
            for idx, item in enumerate(batch):
                gt = item["gt_file"]
                if idx < len(parsed) and isinstance(parsed[idx], dict):
                    s = parsed[idx]
                    results.append({
                        "repo":             gt["repo"],
                        "file":             gt["file"],
                        "breaking_pattern": max(0, min(2, int(round(s.get("breaking_pattern", 0))))),
                        "severity":         max(0, min(1, int(round(s.get("severity", 0))))),
                        "fix_quality":      max(0, min(3, int(round(s.get("fix_quality", 0))))),
                        "notes":            str(s.get("notes", ""))[:120],
                    })
                else:
                    results.append({"repo": gt["repo"], "file": gt["file"], **_FALLBACK_SCORE})
            return results

        except (json.JSONDecodeError, ValueError, TypeError):
            if attempt < 3:
                time.sleep(attempt * 5)
                continue
            return [
                {"repo": item["gt_file"]["repo"], "file": item["gt_file"]["file"], **_FALLBACK_SCORE}
                for item in batch
            ]

    return [
        {"repo": item["gt_file"]["repo"], "file": item["gt_file"]["file"], **_FALLBACK_SCORE}
        for item in batch
    ]


def score_matched_files(
    matched: list[dict],
    gt_patterns: list[dict],
    api_key: str,
    judge_model: str,
    batch_size: int = 10,
) -> dict[tuple, dict]:
    if not matched:
        return {}
    all_scores: dict[tuple, dict] = {}
    for i in range(0, len(matched), batch_size):
        batch = matched[i : i + batch_size]
        for s in _judge_batch(batch, gt_patterns, api_key, judge_model):
            key = (normalize_repo(s["repo"]), normalize_path(s["file"]))
            all_scores[key] = s
    return all_scores


# ─── Step 3: main per-model scoring ───────────────────────────────────────────


def score_model_answer(
    gt_data: dict,
    question_text: str,
    model_answer: dict,
    api_key: str,
    extractor_model: str,
    judge_model: str,
) -> dict:
    model  = model_answer["model"]
    status = model_answer.get("status", "unknown")

    if status != "success":
        return {
            "model":        model,
            "status":       status,
            "skipped":      True,
            "raw_score":    0,
            "max_possible": 0,
            "final_pct":    0.0,
        }

    gt_impacted      = gt_data.get("impacted_files", [])
    gt_false_positives = gt_data.get("false_positives", [])
    gt_patterns      = gt_data.get("breaking_patterns", [])
    total_impacted   = len(gt_impacted)
    total_fp         = len(gt_false_positives)
    max_possible     = total_impacted * 10 + total_fp * 2

    # GT lookup
    gt_lookup: dict[tuple, dict] = {}
    for f in gt_impacted:
        key = (normalize_repo(f["repo"]), normalize_path(f["file"]))
        gt_lookup[key] = f

    gt_fp_set: set[tuple] = set()
    for fp in gt_false_positives:
        repo = fp.get("repo", "")
        file = fp.get("file", fp.get("path", ""))
        if repo and file:
            gt_fp_set.add((normalize_repo(repo), normalize_path(file)))

    answer_text = model_answer.get("full_answer", "").strip()
    if not answer_text:
        return {
            "model":        model,
            "status":       "empty_answer",
            "skipped":      True,
            "raw_score":    0,
            "max_possible": max_possible,
            "final_pct":    0.0,
        }

    # Extract claims
    print(f"      extracting {model.split('/')[-1]}...", end=" ", flush=True)
    raw_claims = extract_model_claims(answer_text, question_text, api_key, extractor_model)
    print(f"{len(raw_claims)} claimed")

    # Deduplicate
    seen_keys: set[tuple] = set()
    model_files: list[dict] = []
    for mf in raw_claims:
        key = (normalize_repo(mf.get("repo", "")), normalize_path(mf.get("file", "")))
        if key == ("", ""):
            continue
        if key not in seen_keys:
            seen_keys.add(key)
            model_files.append(mf)

    # Match against GT
    matched: list[dict]       = []
    hallucinated: list[dict]  = []
    matched_gt_keys: set[tuple] = set()
    model_file_keys: set[tuple] = set()

    for mf in model_files:
        key = (normalize_repo(mf.get("repo", "")), normalize_path(mf.get("file", "")))
        model_file_keys.add(key)
        if key in gt_lookup and key not in matched_gt_keys:
            matched.append({"gt_file": gt_lookup[key], "model_file": mf})
            matched_gt_keys.add(key)
        else:
            hallucinated.append(mf)

    # LLM judge
    if matched:
        print(f"      judging {len(matched)} matched files...", end=" ", flush=True)
    judge_scores = score_matched_files(matched, gt_patterns, api_key, judge_model)
    if matched:
        print("done")

    # Per-file breakdown
    per_file_breakdown: list[dict] = []
    total_fd = total_bp = total_sev = total_fq = 0

    for item in matched:
        gt  = item["gt_file"]
        key = (normalize_repo(gt["repo"]), normalize_path(gt["file"]))
        js  = judge_scores.get(key, {})

        fd  = 4
        bp  = js.get("breaking_pattern", 0)
        sev = js.get("severity", 0)
        fq  = js.get("fix_quality", 0)

        total_fd  += fd
        total_bp  += bp
        total_sev += sev
        total_fq  += fq

        per_file_breakdown.append({
            "repo":    gt["repo"],
            "file":    gt["file"],
            "matched": True,
            "gt_severity":          gt.get("severity", ""),
            "gt_breaking_patterns": gt.get("breaking_patterns", []),
            "model_severity":    item["model_file"].get("severity", ""),
            "model_explanation": item["model_file"].get("breaking_explanation", ""),
            "model_fix":         item["model_file"].get("fix_suggestion", ""),
            "scores": {
                "file_detection":   fd,
                "breaking_pattern": bp,
                "severity":         sev,
                "fix_quality":      fq,
                "total":            fd + bp + sev + fq,
            },
            "judge_notes": js.get("notes", ""),
        })

    # Missed files
    for gt in gt_impacted:
        key = (normalize_repo(gt["repo"]), normalize_path(gt["file"]))
        if key not in matched_gt_keys:
            per_file_breakdown.append({
                "repo":    gt["repo"],
                "file":    gt["file"],
                "matched": False,
                "gt_severity":          gt.get("severity", ""),
                "gt_breaking_patterns": gt.get("breaking_patterns", []),
                "scores": {
                    "file_detection":   0,
                    "breaking_pattern": 0,
                    "severity":         0,
                    "fix_quality":      0,
                    "total":            0,
                },
                "judge_notes": "not found by model",
            })

    hallucination_penalty = len(hallucinated) * -5

    fp_correctly_omitted: list[str] = []
    for fp in gt_false_positives:
        repo = fp.get("repo", "")
        file = fp.get("file", fp.get("path", ""))
        fp_key = (normalize_repo(repo), normalize_path(file))
        if fp_key not in model_file_keys:
            fp_correctly_omitted.append(f"{repo}/{file}")

    fp_bonus  = len(fp_correctly_omitted) * 2
    raw_score = total_fd + total_bp + total_sev + total_fq + hallucination_penalty + fp_bonus

    if max_possible > 0:
        final_pct = round(raw_score / max_possible * 100, 2)
    elif raw_score == 0:
        final_pct = 100.0
    else:
        final_pct = round(100.0 + raw_score, 2)

    return {
        "model":            model,
        "status":           "scored",
        "source_file":      model_answer.get("_source_file", ""),
        "input_tokens":     model_answer.get("input_tokens", 0),
        "output_tokens":    model_answer.get("output_tokens", 0),
        "total_tokens":     model_answer.get("total_tokens", 0),
        "cost_usd":         model_answer.get("cost_usd", 0.0),
        "tool_calls_count": model_answer.get("tool_calls_count", 0),
        "raw_score":        raw_score,
        "max_possible":     max_possible,
        "final_pct":        final_pct,
        "dimension_totals": {
            "file_detection":        total_fd,
            "breaking_pattern":      total_bp,
            "severity":              total_sev,
            "fix_quality":           total_fq,
            "hallucination_penalty": hallucination_penalty,
            "false_positive_bonus":  fp_bonus,
        },
        "files_found":              len(matched),
        "files_missed":             total_impacted - len(matched),
        "files_hallucinated":       len(hallucinated),
        "fp_total":                 total_fp,
        "fp_correctly_omitted":     len(fp_correctly_omitted),
        "per_file_breakdown":       per_file_breakdown,
        "hallucinated_files": [
            f"{m.get('repo', '')}/{m.get('file', '')}" for m in hallucinated
        ],
        "fp_correctly_omitted_list": fp_correctly_omitted,
    }


# ─── Question-level processing ────────────────────────────────────────────────


def process_question(
    folder: Path,
    api_key: str,
    extractor_model: str,
    judge_model: str,
    force: bool = False,
) -> dict | None:
    gt_data = load_ground_truth_enhanced(folder)
    if gt_data is None:
        return None

    enhanced_eval_path = folder / "enhanced_evaluation.json"
    if enhanced_eval_path.exists() and not force:
        print(f"  {folder.name}: enhanced_evaluation.json exists — skipping (use --force to re-run)")
        with open(enhanced_eval_path) as f:
            return json.load(f)

    # Load question text
    question_text = ""
    question_file = folder / "question.json"
    if question_file.exists():
        with open(question_file) as f:
            q_json = json.load(f)
        question_text = q_json.get("question", "")
    if not question_text:
        question_text = gt_data.get("question", "")
    if question_text and not gt_data.get("question"):
        gt_data["question"] = question_text

    gt_impacted = gt_data.get("impacted_files", [])
    gt_fp       = gt_data.get("false_positives", [])
    max_possible = len(gt_impacted) * 10 + len(gt_fp) * 2
    q_id = gt_data.get("id") or gt_data.get("question_id") or folder.name

    print(f"  {folder.name}: GT={len(gt_impacted)} files, FP={len(gt_fp)}, max={max_possible}")

    answers = load_model_answers(folder)
    active  = [a for a in answers if a.get("status") == "success"]

    if not active:
        print(f"    no successful model answers — skipping")
        return None

    model_results: list[dict] = []
    for ma in active:
        label = ma["model"]
        src   = ma.get("_source_file", "")
        print(f"    [{label}] ({src})")
        result = score_model_answer(
            gt_data, question_text, ma, api_key, extractor_model, judge_model,
        )
        model_results.append(result)

    output = {
        "question_id": q_id,
        "question":    question_text[:200],
        "gt_stats": {
            "total_impacted_files":  len(gt_impacted),
            "total_false_positives": len(gt_fp),
            "max_possible_score":    max_possible,
            "repos_affected":        (gt_data.get("impact_summary") or {}).get("repos_affected", []),
            "by_pattern":            (gt_data.get("impact_summary") or {}).get("by_pattern", {}),
            "by_severity":           (gt_data.get("impact_summary") or {}).get("by_severity", {}),
        },
        "model_scores": model_results,
    }

    with open(enhanced_eval_path, "w") as fh:
        json.dump(output, fh, indent=2)
    print(f"    → written {enhanced_eval_path.name}")
    return output


# ─── Aggregation ──────────────────────────────────────────────────────────────


def aggregate_summary(
    results_dir: Path,
    question_folders: list[Path],
    judge_model: str,
    extractor_model: str,
) -> dict:
    model_agg: dict[str, dict] = defaultdict(lambda: {
        "scores":             [],
        "raw_scores":         [],
        "max_scores":         [],
        "input_tokens":       0,
        "output_tokens":      0,
        "total_tokens":       0,
        "cost_usd":           0.0,
        "files_found":        0,
        "files_missed":       0,
        "files_hallucinated": 0,
        "fp_correctly_omitted": 0,
        "dim":                defaultdict(float),
    })

    per_question: list[dict] = []

    for folder in question_folders:
        ef = folder / "enhanced_evaluation.json"
        if not ef.exists():
            continue
        with open(ef) as f:
            data = json.load(f)

        q_id    = data.get("question_id", folder.name)
        q_text  = data.get("question", "")
        gt_stats = data.get("gt_stats", {})

        row: dict = {
            "question_id": q_id,
            "question":    q_text[:120],
            "gt_stats":    gt_stats,
            "models":      {},
        }

        for ms in data.get("model_scores", []):
            model = ms.get("model", "")
            if ms.get("skipped"):
                continue

            row["models"][model] = {
                "final_pct":            ms.get("final_pct", 0.0),
                "raw_score":            ms.get("raw_score", 0),
                "max_possible":         ms.get("max_possible", 0),
                "files_found":          ms.get("files_found", 0),
                "files_missed":         ms.get("files_missed", 0),
                "files_hallucinated":   ms.get("files_hallucinated", 0),
                "fp_correctly_omitted": ms.get("fp_correctly_omitted", 0),
                "cost_usd":             ms.get("cost_usd", 0.0),
                "dimension_totals":     ms.get("dimension_totals", {}),
                "source_file":          ms.get("source_file", ""),
            }

            agg = model_agg[model]
            agg["scores"].append(ms.get("final_pct", 0.0))
            agg["raw_scores"].append(ms.get("raw_score", 0))
            agg["max_scores"].append(ms.get("max_possible", 0))
            agg["input_tokens"]        += ms.get("input_tokens", 0)
            agg["output_tokens"]       += ms.get("output_tokens", 0)
            agg["total_tokens"]        += ms.get("total_tokens", 0)
            agg["cost_usd"]            += ms.get("cost_usd", 0.0)
            agg["files_found"]         += ms.get("files_found", 0)
            agg["files_missed"]        += ms.get("files_missed", 0)
            agg["files_hallucinated"]  += ms.get("files_hallucinated", 0)
            agg["fp_correctly_omitted"] += ms.get("fp_correctly_omitted", 0)
            for dim, val in ms.get("dimension_totals", {}).items():
                agg["dim"][dim] += val

        per_question.append(row)

    model_summaries: list[dict] = []
    for model, agg in sorted(model_agg.items()):
        scores       = agg["scores"]
        avg_pct      = round(sum(scores) / len(scores), 2) if scores else 0.0
        total_raw    = sum(agg["raw_scores"])
        total_max    = sum(agg["max_scores"])
        weighted_pct = round(total_raw / total_max * 100, 2) if total_max > 0 else avg_pct
        total_cost   = round(agg["cost_usd"], 4)
        pct_per_dollar = round(avg_pct / total_cost, 2) if total_cost > 0 else 0.0

        model_summaries.append({
            "model":                      model,
            "avg_final_pct":              avg_pct,
            "weighted_pct":               weighted_pct,
            "questions_scored":           len(scores),
            "total_files_found":          agg["files_found"],
            "total_files_missed":         agg["files_missed"],
            "total_files_hallucinated":   agg["files_hallucinated"],
            "total_fp_correctly_omitted": agg["fp_correctly_omitted"],
            "dimension_totals":           dict(agg["dim"]),
            "input_tokens":               agg["input_tokens"],
            "output_tokens":              agg["output_tokens"],
            "total_tokens":               agg["total_tokens"],
            "total_cost_usd":             total_cost,
            "pct_per_dollar":             pct_per_dollar,
        })

    model_summaries.sort(key=lambda m: m["weighted_pct"], reverse=True)

    return {
        "scoring_version":        "ksr_v1",
        "judge_model":            judge_model,
        "extractor_model":        extractor_model,
        "scoring":                "fact-based marking scheme (evaluation.md)",
        "questions_range":        f"{question_folders[0].name} – {question_folders[-1].name}" if question_folders else "",
        "dimensions": {
            "file_detection":        "4 marks — automated binary",
            "breaking_pattern":      "0-2 marks — LLM judge",
            "severity":              "0-1 marks — LLM judge",
            "fix_quality":           "0-3 marks — LLM judge",
            "hallucination_penalty": "-5 marks each — automated",
            "false_positive_bonus":  "+2 marks each — automated",
        },
        "total_questions_scored": len(per_question),
        "model_summaries":        model_summaries,
        "per_question":           per_question,
    }


# ─── Main ─────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate KSR_TC* question folders against ground_truth_enhanced.json.\n"
            "Implements the fact-based marking scheme from evaluation.md."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--results-dir", "-r", required=True,
        help="Path to results folder, e.g. results/KubeSingle65",
    )
    parser.add_argument(
        "--up-to", "-u", default=None, metavar="QUESTION_ID",
        help=(
            "Only evaluate questions up to and including this ID "
            "(e.g. --up-to KSR_TC020). Folders are processed in sorted order."
        ),
    )
    parser.add_argument(
        "--from", "-s", dest="from_id", default=None, metavar="QUESTION_ID",
        help="Start from this question ID (inclusive). Default: first folder.",
    )
    parser.add_argument(
        "--only", "-n", default=None, metavar="ID[,ID,...]",
        help="Comma-separated specific question IDs to evaluate (e.g. KSR_TC003,KSR_TC007).",
    )
    parser.add_argument(
        "--force", "-f", action="store_true",
        help="Re-evaluate even if enhanced_evaluation.json already exists.",
    )
    parser.add_argument(
        "--workers", "-w", type=int, default=1,
        help="Parallel workers for question processing (default: 1).",
    )
    parser.add_argument(
        "--judge-model", default=DEFAULT_JUDGE,
        help=f"OpenRouter model ID for the LLM judge (default: {DEFAULT_JUDGE}).",
    )
    parser.add_argument(
        "--extractor-model", default=DEFAULT_EXTRACTOR,
        help=f"OpenRouter model ID for claim extraction (default: {DEFAULT_EXTRACTOR}).",
    )
    parser.add_argument(
        "--api-key", "-k", default=None,
        help="OpenRouter API key. Falls back to OPENROUTER_API_KEY env var / .env file.",
    )
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    if not results_dir.exists():
        print(f"Error: results directory not found: {results_dir}", file=sys.stderr)
        sys.exit(1)

    load_dotenv()
    api_key = args.api_key or os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        print("Error: no API key — pass --api-key or set OPENROUTER_API_KEY in .env", file=sys.stderr)
        sys.exit(1)

    judge_model     = args.judge_model
    extractor_model = args.extractor_model

    print(f"Results dir:     {results_dir}")
    print(f"Judge model:     {judge_model}")
    print(f"Extractor model: {extractor_model}")
    print()

    # Discover KSR_TC* folders (sorted lexicographically = numerically)
    all_folders = sorted(
        d for d in results_dir.iterdir()
        if d.is_dir() and re.match(r"KSR_TC\d+", d.name)
    )

    # Apply --only filter
    if args.only:
        requested = {q.strip() for q in args.only.split(",")}
        all_folders = [f for f in all_folders if f.name in requested]
        missing = requested - {f.name for f in all_folders}
        if missing:
            print(f"Warning: question IDs not found: {', '.join(sorted(missing))}", file=sys.stderr)
    else:
        # Apply --from / --up-to range
        if args.from_id:
            all_folders = [f for f in all_folders if f.name >= args.from_id]
        if args.up_to:
            all_folders = [f for f in all_folders if f.name <= args.up_to]

    # Keep only folders that have ground_truth_enhanced.json
    question_folders = [f for f in all_folders if (f / "ground_truth_enhanced.json").exists()]

    if not question_folders:
        print("No KSR_TC* folders with ground_truth_enhanced.json found. Nothing to evaluate.")
        sys.exit(0)

    range_str = f"{question_folders[0].name} – {question_folders[-1].name}"
    print(f"Evaluating {len(question_folders)} questions ({range_str})\n")

    def _run(folder: Path) -> dict | None:
        return process_question(folder, api_key, extractor_model, judge_model, args.force)

    if args.workers > 1:
        n = min(args.workers, len(question_folders))
        print(f"Using {n} parallel workers\n")
        with ThreadPoolExecutor(max_workers=n) as pool:
            futures = {pool.submit(_run, f): f.name for f in question_folders}
            for future in as_completed(futures):
                future.result()
    else:
        for folder in question_folders:
            _run(folder)

    # Aggregate summary
    summary      = aggregate_summary(results_dir, question_folders, judge_model, extractor_model)
    summary_path = results_dir / "enhanced_analysis_summary.json"
    with open(summary_path, "w") as fh:
        json.dump(summary, fh, indent=2)
    print(f"\nSummary → {summary_path}")

    # Leaderboard
    model_summaries = summary.get("model_summaries", [])
    if model_summaries:
        hdr = (
            f"{'Model':<55} | {'Avg%':>7} | {'Wgt%':>7} | "
            f"{'Qs':>4} | {'Found':>6} | {'Halluc':>6} | {'Cost$':>10}"
        )
        sep = f"{'-'*55}-+-{'-'*7}-+-{'-'*7}-+-{'-'*4}-+-{'-'*6}-+-{'-'*6}-+-{'-'*10}"
        print(f"\n{hdr}")
        print(sep)
        for ms in model_summaries:
            print(
                f"{ms['model']:<55} | {ms['avg_final_pct']:>6.1f}% | "
                f"{ms['weighted_pct']:>6.1f}% | {ms['questions_scored']:>4} | "
                f"{ms['total_files_found']:>6} | {ms['total_files_hallucinated']:>6} | "
                f"${ms['total_cost_usd']:>9.4f}"
            )

    print(f"\nDone — {summary['total_questions_scored']} questions evaluated.")


if __name__ == "__main__":
    main()
