#!/usr/bin/env python3
"""
Aggregate per-model metrics across all questions into a final metrics.json.
"""

import json
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"

# Collect per-model data across all questions
model_data = defaultdict(lambda: {
    "relevance_scores": [],
    "hallucination_scores": [],
    "total_files_mentioned": 0,
    "total_files_found": 0,
    "total_files_not_found": 0,
    "questions_answered": 0,
    "questions_errored": 0,
})

eval_files = sorted(RESULTS_DIR.glob("question_*/evaluation.json"))

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

# Build final metrics
models_metrics = []
for model, d in sorted(model_data.items()):
    n = d["questions_answered"]
    avg_rel = round(sum(d["relevance_scores"]) / n, 2) if n else 0
    avg_hal = round(sum(d["hallucination_scores"]) / n, 2) if n else 0
    total_mentioned = d["total_files_mentioned"]
    file_accuracy_pct = round((d["total_files_found"] / total_mentioned) * 100, 1) if total_mentioned else 0

    models_metrics.append({
        "model": model,
        "avg_relevance_score": avg_rel,
        "avg_hallucination_score": avg_hal,
        "questions_answered": n,
        "questions_errored": d["questions_errored"],
        "total_files_mentioned": total_mentioned,
        "total_files_found": d["total_files_found"],
        "total_files_not_found": d["total_files_not_found"],
        "file_accuracy_pct": file_accuracy_pct,
    })

# Sort by relevance descending
models_metrics.sort(key=lambda m: m["avg_relevance_score"], reverse=True)

output = {
    "total_questions": len(eval_files),
    "total_models": len(models_metrics),
    "models": models_metrics,
}

out_path = RESULTS_DIR / "metrics.json"
with open(out_path, "w") as f:
    json.dump(output, f, indent=2)

print(json.dumps(output, indent=2))
