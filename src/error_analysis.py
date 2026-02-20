#!/usr/bin/env python3
"""Analyze error types across all failed answer files."""
import json
from collections import Counter
from pathlib import Path

results = Path("results")
error_types = Counter()
model_errors = {}

for qdir in sorted(results.iterdir()):
    if not qdir.is_dir() or not qdir.name.startswith("question_"):
        continue
    for f in qdir.iterdir():
        if f.name in ("question.json", "evaluation.json") or f.suffix != ".json":
            continue
        try:
            data = json.loads(f.read_text())
            status = data.get("status", "")
            answer = data.get("answer", "")
            if status != "success" or not answer.strip():
                model = data.get("model", f.stem)
                error_msg = data.get("error", "no error field")
                # Classify error
                e_lower = error_msg.lower()
                if "402" in error_msg:
                    etype = "402 Payment Required"
                elif "429" in error_msg:
                    etype = "429 Rate Limited"
                elif "timeout" in e_lower or "timed out" in e_lower:
                    etype = "Timeout"
                elif "readtimeout" in e_lower:
                    etype = "ReadTimeout"
                elif "500" in error_msg or "502" in error_msg or "503" in error_msg:
                    etype = "5xx Server Error"
                elif "no error field" in e_lower and not answer.strip():
                    etype = "Blank answer (no error)"
                elif error_msg.strip() == "":
                    etype = "Empty error field"
                else:
                    etype = error_msg[:60]

                error_types[etype] += 1
                model_errors.setdefault(model, Counter())[etype] += 1
        except Exception:
            pass

print("ERROR TYPE BREAKDOWN (all models):")
print("-" * 60)
for etype, count in error_types.most_common():
    print(f"  {count:>4}  {etype}")

print("\n\nPER-MODEL ERROR BREAKDOWN:")
print("-" * 60)
for model in sorted(model_errors):
    print(f"\n  {model}:")
    for etype, count in model_errors[model].most_common():
        print(f"    {count:>4}  {etype}")
