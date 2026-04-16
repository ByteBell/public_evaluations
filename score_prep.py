#!/usr/bin/env python3
"""score_prep.py — Pre-processing for SWE-Pro LLM evaluation.

For each instance in a run directory, reads answer.json + the official JSONL
and writes score_input.json containing:

  score_A          — exact file-coverage score out of 30 (computed, never judged)
  file_hits        — gold files the model touched
  file_misses      — gold files the model missed
  extra_files      — files model touched that aren't in the gold patch
  fail_to_pass     — test names that must pass after the fix (from official dataset)
  pass_to_pass_count — number of regression tests
  test_patch       — actual test code added/changed (from official dataset)
  gold_patch       — reference diff
  model_answer     — model's raw answer text

The judge only needs to evaluate Dimensions B and C using this file.
Dimension A is already computed here.

Usage:
    # Single run
    python score_prep.py \\
        --run_dir results_on_swe_pro/auto_run_on_swe_pro_mcp_claude-sonnet-4-6

    # All auto_run_* dirs under results_on_swe_pro/
    python score_prep.py --all

    # Re-generate even if score_input.json already exists
    python score_prep.py --all --force
"""

import argparse
import ast
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

JSONL_URL = (
    "https://raw.githubusercontent.com/scaleapi/SWE-bench_Pro-os/main/"
    "helper_code/sweap_eval_full_v2.jsonl"
)
DEFAULT_JSONL_PATH = Path("results_on_swe_pro/sweap_eval_full_v2.jsonl")
DEFAULT_TASKS_PATH = Path("results_on_swe_pro/swe_pro_tasks.json")
DEFAULT_RESULTS_DIR = Path("results_on_swe_pro")


# ── Diff parsing ──────────────────────────────────────────────────────────────

def _extract_files_diff_git(diff_text: str) -> list:
    """Parse files from a `diff --git a/X b/Y` style patch."""
    files = []
    sections = re.split(r"(?=^diff --git )", diff_text, flags=re.MULTILINE)
    for section in sections:
        if not section.strip():
            continue
        m = re.match(r"^diff --git a/(.*?) b/(.*?)$", section, re.MULTILINE)
        if not m:
            continue
        a_path, b_path = m.group(1), m.group(2)
        if re.search(r"^new file mode", section, re.MULTILINE):
            op, path = "created", b_path
        elif re.search(r"^deleted file mode", section, re.MULTILINE):
            op, path = "deleted", a_path
        elif re.search(r"^rename to ", section, re.MULTILINE):
            op, path = "renamed", b_path
        else:
            op, path = "modified", b_path
        added = len(re.findall(r"^\+(?!\+\+)", section, re.MULTILINE))
        removed = len(re.findall(r"^-(?!--)", section, re.MULTILINE))
        files.append({"path": path, "op": op, "added": added, "removed": removed})
    return files


def _extract_files_unified(diff_text: str) -> list:
    """Fallback: parse files from `+++ b/X` lines (no diff --git header)."""
    paths = set()
    for m in re.finditer(r"^\+\+\+ b/(.+)$", diff_text, re.MULTILINE):
        p = m.group(1).strip()
        if p != "/dev/null":
            paths.add(p)
    for m in re.finditer(r"^--- a/(.+)$", diff_text, re.MULTILINE):
        p = m.group(1).strip()
        if p != "/dev/null":
            paths.add(p)
    return [{"path": p, "op": "modified", "added": 0, "removed": 0} for p in sorted(paths)]


def extract_files(diff_text: str) -> list:
    """Extract file list from any diff format."""
    if not diff_text or not diff_text.strip():
        return []
    if "diff --git" in diff_text:
        return _extract_files_diff_git(diff_text)
    return _extract_files_unified(diff_text)


def extract_diff_from_answer(text: str) -> str:
    """
    Pull diff content out of a mixed prose + diff model answer.

    Handles:
      1. ```diff ... ``` or ``` ... ``` fenced blocks containing diff syntax
      2. Bare diff --git / --- a/ / +++ b/ lines in plain text
    """
    if not text:
        return ""

    # Try fenced code blocks first
    fenced = re.findall(r"```(?:diff|patch)?\s*\n(.*?)```", text, re.DOTALL)
    if fenced:
        diff_blocks = [
            b for b in fenced
            if re.search(r"^(?:diff --git|---|^\+\+\+|^@@)", b, re.MULTILINE)
        ]
        if diff_blocks:
            return "\n".join(diff_blocks)

    # Fallback: collect lines that look like diff syntax
    lines = text.splitlines()
    collected = []
    in_diff = False
    for line in lines:
        if re.match(r"^(?:diff --git |\+\+\+ b/|--- a/)", line):
            in_diff = True
        if in_diff:
            collected.append(line)
    return "\n".join(collected)


# ── Score A computation ───────────────────────────────────────────────────────

def compute_score_a(gold_files: list, model_files: list):
    """
    Returns (score_A, hits, misses, extras).

    Formula (out of 25 pts — A is 25 in the 4-dimension rubric):
      raw      = (|hits| / |gold|) * 25
      deduction = min(|extras|, |hits|) * (25 / |gold|)
      score_A  = max(0, raw - deduction), rounded to 1 decimal
    """
    gold_paths = {f["path"] for f in gold_files}
    model_paths = {f["path"] for f in model_files}

    if not gold_paths:
        # No reference files — model gets full score if it also touched nothing
        score = 25.0 if not model_paths else 0.0
        return score, [], [], sorted(model_paths)

    hits = sorted(gold_paths & model_paths)
    misses = sorted(gold_paths - model_paths)
    extras = sorted(model_paths - gold_paths)

    total = len(gold_paths)
    raw = (len(hits) / total) * 25
    deduction = min(len(extras), len(hits)) * (25 / total)
    score = round(max(0.0, raw - deduction), 1)

    return score, hits, misses, extras


# ── Test signal extraction ───────────────────────────────────────────────────

def extract_test_signals(test_patch: str) -> dict:
    """
    Parse the test_patch diff to give the judge structured test data:
      - test_functions : every new test function name added in the patch
      - assert_samples : first 15 assert/expect lines from the new test code
    These map directly to Dimension C (Test Coverage) scoring.
    """
    if not test_patch:
        return {"test_functions": [], "assert_samples": []}

    # Collect only added lines (lines prefixed with + but not the +++ header)
    added_lines = re.findall(r"^\+(?!\+\+)(.*)$", test_patch, re.MULTILINE)
    added_text = "\n".join(added_lines)

    # Test function names (Python: def test_xxx, JS: it('...') / test('...') / describe('...'))
    py_funcs = re.findall(r"\bdef (test_\w+)", added_text)
    js_tests = re.findall(
        r"""(?:it|test)\s*\(\s*['"`]([^'"`]{3,80})['"`]""", added_text
    )
    test_functions = py_funcs + js_tests

    # Assert / expect lines (first 15 unique ones, stripped)
    assert_lines = []
    seen = set()
    for line in added_lines:
        stripped = line.strip()
        if stripped and re.match(
            r"(assert |self\.assert|expect\(|assert_|pytest\.raises|\.toBe|\.toEqual|\.toContain)",
            stripped,
        ):
            if stripped not in seen:
                assert_lines.append(stripped)
                seen.add(stripped)
            if len(assert_lines) >= 15:
                break

    return {
        "test_functions": test_functions,
        "assert_samples": assert_lines,
    }


# ── Normalise FAIL_TO_PASS / PASS_TO_PASS ────────────────────────────────────

def _parse_test_list(value) -> list:
    """Handle the various forms this field arrives in (list, JSON string, Python repr)."""
    if isinstance(value, list):
        return value
    if not value:
        return []
    # Try JSON first
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return parsed
    except (json.JSONDecodeError, TypeError):
        pass
    # Fall back to ast.literal_eval (handles Python list repr)
    try:
        parsed = ast.literal_eval(value)
        if isinstance(parsed, list):
            return parsed
    except Exception:
        pass
    return []


# ── Data loading ─────────────────────────────────────────────────────────────

def download_jsonl(dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading sweap_eval_full_v2.jsonl → {dest} …", flush=True)
    urllib.request.urlretrieve(JSONL_URL, dest)
    size_mb = dest.stat().st_size / 1e6
    print(f"  Downloaded {size_mb:.1f} MB", flush=True)


def load_jsonl(path: Path) -> dict:
    data = {}
    with open(path) as f:
        for line in f:
            row = json.loads(line)
            data[row["instance_id"]] = row
    print(f"Loaded {len(data)} instances from {path.name}", flush=True)
    return data


def load_tasks(path: Path) -> dict:
    with open(path) as f:
        rows = json.load(f)
    return {r["instance_id"]: r for r in rows}


# ── Core per-task logic ───────────────────────────────────────────────────────

def process_task(
    instance_id: str,
    answer_data: dict,
    task_data,
    jsonl_row,
) -> dict:
    """Build the score_input dict for one task."""
    model_answer_text = answer_data.get("answer", "")

    # Gold patch: prefer JSONL (it also carries test_patch), fall back to tasks JSON
    gold_patch = ""
    if jsonl_row:
        gold_patch = jsonl_row.get("patch", "")
    elif task_data:
        gold_patch = task_data.get("answer", "")

    # Extract the diff portion from the model answer
    model_diff = extract_diff_from_answer(model_answer_text)

    # Parse file lists
    gold_files = extract_files(gold_patch)
    model_files = extract_files(model_diff)

    # Dimension A — exact computation (out of 25 pts)
    score_a, hits, misses, extras = compute_score_a(gold_files, model_files)
    total = len(gold_files)
    formula = f"{len(hits)}/{total} files × 25" + (
        f" − {len(extras)}×(25/{total}) spurious deduction" if extras else ""
    )

    # Test signals from JSONL
    fail_to_pass = []
    pass_to_pass = []
    test_patch = ""
    if jsonl_row:
        fail_to_pass = _parse_test_list(jsonl_row.get("FAIL_TO_PASS", []))
        pass_to_pass = _parse_test_list(jsonl_row.get("PASS_TO_PASS", []))
        test_patch = jsonl_row.get("test_patch", "")

    # Structured test signals for Dimension C (extracted from test_patch)
    test_signals = extract_test_signals(test_patch)

    return {
        "instance_id": instance_id,
        "repo": (task_data or jsonl_row or {}).get("repo", ""),
        "language": (task_data or {}).get("language", ""),
        # Dimension A — precomputed (out of 25)
        "score_A": score_a,
        "score_A_formula": formula,
        "file_hits": hits,
        "file_misses": misses,
        "extra_files": extras,
        "gold_file_count": total,
        "model_file_count": len(model_files),
        "is_prose_only": not bool(model_diff.strip()),
        # Dimension C inputs — test coverage signals
        "fail_to_pass": fail_to_pass,
        "fail_to_pass_count": len(fail_to_pass),
        "pass_to_pass_count": len(pass_to_pass),
        "test_patch": test_patch,
        "test_functions": test_signals["test_functions"],
        "assert_samples": test_signals["assert_samples"],
        # Raw content for the judge (B, C, D)
        "gold_patch": gold_patch,
        "model_answer": model_answer_text,
    }


# ── Run-level processing ──────────────────────────────────────────────────────

def process_run(
    run_dir: Path,
    tasks_by_id: dict,
    jsonl_by_id: dict,
    force: bool = False,
) -> dict:
    """Process all instance_* folders in run_dir. Returns {instance_id: score_A}."""
    scores = {}
    instance_dirs = sorted(
        d for d in run_dir.iterdir()
        if d.is_dir() and d.name.startswith("instance_")
    )

    if not instance_dirs:
        print(f"  No instance_* dirs found in {run_dir}", flush=True)
        return scores

    processed = skipped = missing = no_ref = 0

    for inst_dir in instance_dirs:
        instance_id = inst_dir.name
        out_path = inst_dir / "score_input.json"

        if out_path.exists() and not force:
            skipped += 1
            try:
                scores[instance_id] = json.loads(out_path.read_text()).get("score_A", 0.0)
            except Exception:
                pass
            continue

        answer_path = inst_dir / "answer.json"
        if not answer_path.exists():
            missing += 1
            continue

        answer_data = json.loads(answer_path.read_text())
        task_data = tasks_by_id.get(instance_id)
        jsonl_row = jsonl_by_id.get(instance_id)

        if task_data is None and jsonl_row is None:
            no_ref += 1
            print(f"  WARN: no reference data for {instance_id}", flush=True)

        result = process_task(instance_id, answer_data, task_data, jsonl_row)
        out_path.write_text(json.dumps(result, indent=2))
        scores[instance_id] = result["score_A"]
        processed += 1

    total = len(instance_dirs)
    parts = [f"{processed} processed", f"{skipped} skipped (already done)"]
    if missing:
        parts.append(f"{missing} missing answer.json")
    if no_ref:
        parts.append(f"{no_ref} no reference data")
    print(f"  {run_dir.name}: {', '.join(parts)}  [{total} total]", flush=True)
    return scores


# ── Summary ───────────────────────────────────────────────────────────────────

def print_summary(run_dir: Path, scores: dict) -> None:
    if not scores:
        return
    vals = list(scores.values())
    n = len(vals)
    avg = sum(vals) / n
    full = sum(1 for v in vals if v >= 22.5)   # ≥90% of 25 pts
    partial = sum(1 for v in vals if 1.0 <= v < 22.5)
    zero = sum(1 for v in vals if v == 0.0)

    prose_count = 0
    for iid, score in scores.items():
        si_path = run_dir / iid / "score_input.json"
        if si_path.exists():
            try:
                if json.loads(si_path.read_text()).get("is_prose_only"):
                    prose_count += 1
            except Exception:
                pass

    print(f"\n  ── {run_dir.name} ──")
    print(f"  Tasks scored        : {n}")
    print(f"  Avg score_A         : {avg:.1f} / 25")
    print(f"  Full coverage (≥90%): {full}  ({full/n*100:.0f}%)")
    print(f"  Partial coverage    : {partial}  ({partial/n*100:.0f}%)")
    print(f"  Zero coverage       : {zero}  ({zero/n*100:.0f}%)")
    print(f"  Prose-only answers  : {prose_count}  ({prose_count/n*100:.0f}%)")


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(
        description="Pre-process SWE-Pro run results for LLM evaluation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument(
        "--run_dir",
        type=Path,
        help="Path to a single run directory",
    )
    g.add_argument(
        "--all",
        action="store_true",
        help="Process all auto_run_* dirs under --results_dir",
    )
    p.add_argument(
        "--results_dir",
        type=Path,
        default=DEFAULT_RESULTS_DIR,
        help=f"Root results directory for --all (default: {DEFAULT_RESULTS_DIR})",
    )
    p.add_argument(
        "--tasks_path",
        type=Path,
        default=DEFAULT_TASKS_PATH,
        help=f"Path to swe_pro_tasks.json (default: {DEFAULT_TASKS_PATH})",
    )
    p.add_argument(
        "--jsonl_path",
        type=Path,
        default=DEFAULT_JSONL_PATH,
        help=f"Path to sweap_eval_full_v2.jsonl (downloaded if missing)",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Re-generate score_input.json even if it already exists",
    )
    return p.parse_args()


def main():
    args = parse_args()

    # Ensure JSONL is available
    if not args.jsonl_path.exists():
        download_jsonl(args.jsonl_path)

    # Load reference data
    jsonl_by_id = load_jsonl(args.jsonl_path)

    tasks_by_id = {}
    if args.tasks_path.exists():
        tasks_by_id = load_tasks(args.tasks_path)
    else:
        print(f"WARN: tasks file not found at {args.tasks_path}", flush=True)

    # Collect run directories
    if args.all:
        run_dirs = sorted(
            d for d in args.results_dir.iterdir()
            if d.is_dir() and d.name.startswith("auto_run_")
        )
        if not run_dirs:
            print(f"No auto_run_* dirs found under {args.results_dir}", file=sys.stderr)
            sys.exit(1)
    else:
        run_dirs = [args.run_dir]

    # Process each run
    for run_dir in run_dirs:
        print(f"\nProcessing: {run_dir}", flush=True)
        scores = process_run(run_dir, tasks_by_id, jsonl_by_id, force=args.force)
        print_summary(run_dir, scores)

    print("\nDone. score_input.json written alongside each answer.json.", flush=True)


if __name__ == "__main__":
    main()
