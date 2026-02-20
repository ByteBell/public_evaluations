#!/usr/bin/env python3
"""Count errored answer files per model."""
import json
from pathlib import Path

results = Path("results")
errored = {}

for qdir in sorted(results.iterdir()):
    if not qdir.is_dir() or not qdir.name.startswith("question_"):
        continue
    for f in qdir.iterdir():
        skip = f.name in ("question.json", "evaluation.json")
        if skip or f.suffix != ".json":
            continue
        try:
            data = json.loads(f.read_text())
            status = data.get("status", "")
            answer = data.get("answer", "")
            if status != "success" or not answer.strip():
                model = data.get("model", f.stem)
                errored.setdefault(model, []).append((qdir.name, f.name, status, data.get("error", "")[:80]))
        except Exception:
            pass

print("ERRORED ANSWER FILES PER MODEL:")
print("-" * 60)
total = 0
for model in sorted(errored, key=lambda m: -len(errored[m])):
    count = len(errored[model])
    total += count
    print(f"  {model:45s} | {count}")
print("-" * 60)
print(f"  TOTAL errored files to retry: {total}")
