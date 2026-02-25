#!/usr/bin/env python3
"""
Rescore enhanced evaluations without hallucination penalties.

Reads existing enhanced_evaluation.json files (produced by evaluate_enhanced.py)
and recalculates scores as if the -5 hallucination penalty did not exist.
All other scoring (file_detection, breaking_pattern, severity, fix_quality,
false_positive_bonus) is left unchanged.

Output: <results_dir>/no_penalty_analysis_summary.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


def rescore_model(ms: dict) -> dict:
    """Return a copy of a model_score dict with hallucination_penalty zeroed out."""
    dim = ms.get("dimension_totals", {})

    fd   = dim.get("file_detection", 0)
    bp   = dim.get("breaking_pattern", 0)
    sev  = dim.get("severity", 0)
    fq   = dim.get("fix_quality", 0)
    fp_b = dim.get("false_positive_bonus", 0)
    # hallucination_penalty intentionally excluded

    raw_score   = fd + bp + sev + fq + fp_b
    max_possible = ms.get("max_possible", 0)

    if max_possible > 0:
        final_pct = round(raw_score / max_possible * 100, 2)
    elif raw_score == 0:
        final_pct = 100.0
    else:
        final_pct = round(100.0 + raw_score, 2)

    return {
        **ms,
        "raw_score":  raw_score,
        "final_pct":  final_pct,
        "dimension_totals": {
            **dim,
            "hallucination_penalty": 0,   # zeroed, kept for schema consistency
        },
    }


def write_question_file(folder: Path, data: dict) -> None:
    """Write per-question enhanced_evaluation_no_penalties.json."""
    rescored_scores = []
    for ms in data.get("model_scores", []):
        if ms.get("skipped"):
            rescored_scores.append(ms)
        else:
            rescored_scores.append(rescore_model(ms))

    out = {**data, "model_scores": rescored_scores}
    out_path = folder / "enhanced_evaluation_no_penalties.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)


def aggregate(results_dir: Path, question_folders: list[Path]) -> dict:
    model_agg: dict[str, dict] = defaultdict(lambda: {
        "scores":               [],
        "raw_scores":           [],
        "max_scores":           [],
        "input_tokens":         0,
        "output_tokens":        0,
        "total_tokens":         0,
        "cost_usd":             0.0,
        "files_found":          0,
        "files_missed":         0,
        "files_hallucinated":   0,
        "fp_correctly_omitted": 0,
        "dim":                  defaultdict(float),
    })

    per_question: list[dict] = []

    for folder in question_folders:
        ef = folder / "enhanced_evaluation.json"
        if not ef.exists():
            continue
        with open(ef) as f:
            data = json.load(f)

        write_question_file(folder, data)

        q_id     = data.get("question_id", folder.name)
        q_text   = data.get("question", "")
        gt_stats = data.get("gt_stats", {})

        row: dict = {
            "question_id": q_id,
            "question":    q_text[:120],
            "gt_stats":    gt_stats,
            "models":      {},
        }

        for ms in data.get("model_scores", []):
            if ms.get("skipped"):
                continue

            rms   = rescore_model(ms)
            model = rms["model"]

            row["models"][model] = {
                "final_pct":            rms["final_pct"],
                "raw_score":            rms["raw_score"],
                "max_possible":         rms["max_possible"],
                "files_found":          rms.get("files_found", 0),
                "files_missed":         rms.get("files_missed", 0),
                "files_hallucinated":   rms.get("files_hallucinated", 0),
                "fp_correctly_omitted": rms.get("fp_correctly_omitted", 0),
                "cost_usd":             rms.get("cost_usd", 0.0),
                "dimension_totals":     rms["dimension_totals"],
            }

            agg = model_agg[model]
            agg["scores"].append(rms["final_pct"])
            agg["raw_scores"].append(rms["raw_score"])
            agg["max_scores"].append(rms["max_possible"])
            agg["input_tokens"]         += rms.get("input_tokens", 0)
            agg["output_tokens"]        += rms.get("output_tokens", 0)
            agg["total_tokens"]         += rms.get("total_tokens", 0)
            agg["cost_usd"]             += rms.get("cost_usd", 0.0)
            agg["files_found"]          += rms.get("files_found", 0)
            agg["files_missed"]         += rms.get("files_missed", 0)
            agg["files_hallucinated"]   += rms.get("files_hallucinated", 0)
            agg["fp_correctly_omitted"] += rms.get("fp_correctly_omitted", 0)
            for dim, val in rms["dimension_totals"].items():
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
            "model":                        model,
            "avg_final_pct":                avg_pct,
            "weighted_pct":                 weighted_pct,
            "questions_scored":             len(scores),
            "total_files_found":            agg["files_found"],
            "total_files_missed":           agg["files_missed"],
            "total_files_hallucinated":     agg["files_hallucinated"],
            "total_fp_correctly_omitted":   agg["fp_correctly_omitted"],
            "dimension_totals":             dict(agg["dim"]),
            "input_tokens":                 agg["input_tokens"],
            "output_tokens":                agg["output_tokens"],
            "total_tokens":                 agg["total_tokens"],
            "total_cost_usd":               total_cost,
            "pct_per_dollar":               pct_per_dollar,
        })

    model_summaries.sort(key=lambda m: m["weighted_pct"], reverse=True)

    return {
        "scoring_version":        "enhanced_v1_no_penalty",
        "note":                   "Hallucination penalty (-5 per hallucinated file) removed. All other scoring unchanged.",
        "scoring":                "fact-based marking scheme without hallucination penalty",
        "dimensions": {
            "file_detection":       "4 marks — automated binary",
            "breaking_pattern":     "0-2 marks — LLM judge",
            "severity":             "0-1 marks — LLM judge",
            "fix_quality":          "0-3 marks — LLM judge",
            "hallucination_penalty": "0 (disabled in this variant)",
            "false_positive_bonus": "+2 marks each — automated",
        },
        "total_questions_scored": len(per_question),
        "model_summaries":        model_summaries,
        "per_question":           per_question,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Rescore enhanced evaluations without hallucination penalties (pure math, no LLM calls)")
    parser.add_argument("--results-dir", "-r", required=True,
                        help="Path to results folder (e.g. results/KubeCluster45)")
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    if not results_dir.exists():
        print(f"Error: results directory not found: {results_dir}")
        sys.exit(1)

    question_folders = sorted([
        d for d in results_dir.iterdir()
        if d.is_dir() and d.name.startswith("question_")
        and (d / "enhanced_evaluation.json").exists()
    ])

    if not question_folders:
        print("No enhanced_evaluation.json files found — run evaluate_enhanced.py first.")
        sys.exit(1)

    print(f"Rescoring {len(question_folders)} questions (no hallucination penalty)...\n"
          f"Writing per-question enhanced_evaluation_no_penalties.json files...")

    summary = aggregate(results_dir, question_folders)
    out_path = results_dir / "no_penalty_analysis_summary.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Written → {out_path}")

    model_summaries = summary["model_summaries"]
    if model_summaries:
        hdr = f"{'Model':<45} | {'Avg%':>7} | {'Wgt%':>7} | {'Found':>6} | {'Halluc':>6} | {'Cost$':>10}"
        sep = f"{'-'*45}-+-{'-'*7}-+-{'-'*7}-+-{'-'*6}-+-{'-'*6}-+-{'-'*10}"
        print(f"\n{hdr}")
        print(sep)
        for ms in model_summaries:
            print(
                f"{ms['model']:<45} | {ms['avg_final_pct']:>6.1f}% | "
                f"{ms['weighted_pct']:>6.1f}% | {ms['total_files_found']:>6} | "
                f"{ms['total_files_hallucinated']:>6} | ${ms['total_cost_usd']:>9.4f}"
            )

    print(f"\nDone — {summary['total_questions_scored']} questions rescored.")


if __name__ == "__main__":
    main()
