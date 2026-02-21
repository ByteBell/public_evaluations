#!/usr/bin/env python3
"""
Aggregate per-model metrics across all questions into a final metrics.json.

Combines:
  - File-existence scores from evaluation.json
  - LLM judge scores from analysis.json (if available)
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate per-model metrics into metrics.json")
    parser.add_argument("--results-dir", "-r", required=True,
                        help="Path to results folder (e.g. results/KubeCluster40)")
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    if not results_dir.exists():
        print(f"Error: results directory not found: {results_dir}")
        sys.exit(1)

    # Collect per-model data from evaluation.json files
    model_data = defaultdict(lambda: {
        "relevance_scores": [],
        "hallucination_scores": [],
        "total_files_mentioned": 0,
        "total_files_found": 0,
        "total_files_not_found": 0,
        "questions_answered": 0,
        "questions_errored": 0,
        "llm_judge_scores": [],
    })

    eval_files = sorted(results_dir.glob("question_*/evaluation.json"))

    for ef in eval_files:
        with open(ef) as f:
            data = json.load(f)

        for me in data["model_evaluations"]:
            model = me["model"]
            d = model_data[model]

            if me["status"] == "success":
                d["relevance_scores"].append(me["relevance_score"])
                d["hallucination_scores"].append(me["hallucination_score"])
                d["total_files_mentioned"] += me["files_mentioned"]
                d["total_files_found"] += me["files_found"]
                d["total_files_not_found"] += me["files_not_found"]
                d["questions_answered"] += 1
            else:
                d["questions_errored"] += 1

    # Collect LLM judge scores from analysis.json files
    analysis_files = sorted(results_dir.glob("question_*/analysis.json"))
    for af in analysis_files:
        with open(af) as f:
            data = json.load(f)

        for ma in data.get("model_analyses", []):
            model = ma.get("model", "")
            score = ma.get("relevance", 0)
            if model in model_data and score > 0:
                model_data[model]["llm_judge_scores"].append(score)

    # Build final metrics
    models_metrics = []
    for model, d in sorted(model_data.items()):
        n = d["questions_answered"]
        avg_rel = round(sum(d["relevance_scores"]) / n, 2) if n else 0
        avg_hal = round(sum(d["hallucination_scores"]) / n, 2) if n else 0
        total_mentioned = d["total_files_mentioned"]
        file_accuracy_pct = round((d["total_files_found"] / total_mentioned) * 100, 1) if total_mentioned else 0

        judge_scores = d["llm_judge_scores"]
        avg_judge = round(sum(judge_scores) / len(judge_scores), 2) if judge_scores else None

        entry = {
            "model": model,
            "avg_relevance_score": avg_rel,
            "avg_hallucination_score": avg_hal,
            "avg_llm_judge_score": avg_judge,
            "questions_answered": n,
            "questions_errored": d["questions_errored"],
            "questions_judged": len(judge_scores),
            "total_files_mentioned": total_mentioned,
            "total_files_found": d["total_files_found"],
            "total_files_not_found": d["total_files_not_found"],
            "file_accuracy_pct": file_accuracy_pct,
        }
        models_metrics.append(entry)

    # Sort by LLM judge score (if available), then by relevance
    models_metrics.sort(
        key=lambda m: (m["avg_llm_judge_score"] or 0, m["avg_relevance_score"]),
        reverse=True,
    )

    output = {
        "total_questions": len(eval_files),
        "total_analyses": len(analysis_files),
        "total_models": len(models_metrics),
        "models": models_metrics,
    }

    out_path = results_dir / "metrics.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    print(json.dumps(output, indent=2))
    print(f"\nSaved to: {out_path}")


if __name__ == "__main__":
    main()
