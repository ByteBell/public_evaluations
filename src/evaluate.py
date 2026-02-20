#!/usr/bin/env python3
"""
Evaluate LLM answers by checking file paths against the actual dataset.

For each question folder in results/:
  - Reads question.json
  - Reads each model answer file
  - Extracts file paths mentioned in the answer
  - Checks if those files physically exist in dataset/<repo>/<path>
  - Computes:
      relevance_score (0-10): higher = more relevant
      hallucination_score (0-10): higher = more hallucination detected
  - Writes evaluation.json into the question folder
"""

import json
import os
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"
DATASET_DIR = BASE_DIR / "dataset" / "kubeCluster"

# All repos available in the dataset
DATASET_REPOS = sorted([d for d in os.listdir(DATASET_DIR) if (DATASET_DIR / d).is_dir()])

# Map various repo name variants to dataset folder names
REPO_NAME_MAP = {
    # Direct matches
    "kubernetes": "kubernetes",
    "helm": "helm",
    "argo-cd": "argo-cd",
    "argocd": "argo-cd",
    "cilium": "cilium",
    "crossplane": "crossplane",
    "istio": "istio",
    "kustomize": "kustomize",
    "karpenter": "karpenter",
    "autoscaler": "autoscaler",
    "gatekeeper": "gatekeeper",
    "flux2": "flux2",
    "flux": "flux2",
    "fluxcd": "flux2",
    "cert-manager": "cert-manager",
    "certmanager": "cert-manager",
    "ingress-nginx": "ingress-nginx",
    "external-dns": "external-dns",
    "external-secrets": "external-secrets",
    "grafana": "grafana",
    "jaeger": "jaeger",
    "loki": "loki",
    "mimir": "mimir",
    "opentelemetry-collector": "opentelemetry-collector",
    "opentelemetry-collector-contrib": "opentelemetry-collector-contrib",
    "opentelemetry-operator": "opentelemetry-operator",
    "otel-collector": "opentelemetry-collector",
    "otel-collector-contrib": "opentelemetry-collector-contrib",
    "otel-operator": "opentelemetry-operator",
    "prometheus": "prometheus",
    "tempo": "tempo",
    "thanos": "thanos",
    # GitHub org/repo format
    "kubernetes/kubernetes": "kubernetes",
    "helm/helm": "helm",
    "argoproj/argo-cd": "argo-cd",
    "cilium/cilium": "cilium",
    "crossplane/crossplane": "crossplane",
    "istio/istio": "istio",
    "kubernetes-sigs/kustomize": "kustomize",
    "kubernetes-sigs/karpenter": "karpenter",
    "kubernetes/autoscaler": "autoscaler",
    "open-policy-agent/gatekeeper": "gatekeeper",
    "fluxcd/flux2": "flux2",
    "cert-manager/cert-manager": "cert-manager",
    "kubernetes/ingress-nginx": "ingress-nginx",
    "kubernetes-sigs/external-dns": "external-dns",
    "external-secrets/external-secrets": "external-secrets",
    "grafana/grafana": "grafana",
    "jaegertracing/jaeger": "jaeger",
    "grafana/loki": "loki",
    "grafana/mimir": "mimir",
    "open-telemetry/opentelemetry-collector": "opentelemetry-collector",
    "open-telemetry/opentelemetry-collector-contrib": "opentelemetry-collector-contrib",
    "open-telemetry/opentelemetry-operator": "opentelemetry-operator",
    "prometheus/prometheus": "prometheus",
    "grafana/tempo": "tempo",
    "thanos-io/thanos": "thanos",
}


def normalize_repo_name(name: str) -> str | None:
    """Map a repo name variant to the dataset folder name."""
    name = name.strip().lower().rstrip("/")
    # Try direct lookup
    if name in REPO_NAME_MAP:
        return REPO_NAME_MAP[name]
    # Try partial match
    for key, val in REPO_NAME_MAP.items():
        if name.endswith(key) or key.endswith(name):
            return val
    # Try matching against dataset repo names directly
    for repo in DATASET_REPOS:
        if name == repo or name.endswith("/" + repo):
            return repo
    return None


def extract_table_file_entries(answer: str) -> list[dict]:
    """
    Extract (repo, filepath) pairs from markdown tables in the answer.
    Looks for tables with columns like: | Repo | File/Path | ... |
    """
    entries = []

    # Match markdown table rows: | repo_name | file/path.ext | ... |
    # The repo column can contain org/repo or just repo name
    table_row_pattern = re.compile(
        r'\|\s*'
        r'([a-zA-Z0-9_./-]+(?:/[a-zA-Z0-9_./-]+)?)'  # repo name (group 1)
        r'\s*\|\s*'
        r'`?([a-zA-Z0-9_./-]+\.[a-zA-Z]{1,10})`?'    # file path (group 2)
        r'\s*\|'
    )

    for match in table_row_pattern.finditer(answer):
        repo_raw = match.group(1).strip()
        filepath = match.group(2).strip()

        # Skip table headers
        if repo_raw.lower() in ("repo", "repository", "project", "---", "------", "--------"):
            continue
        if filepath.lower() in ("file", "file path", "filepath", "path", "---", "---------"):
            continue
        # Skip separator rows
        if set(repo_raw) <= {"-", " ", "|"}:
            continue

        repo = normalize_repo_name(repo_raw)
        if repo and "/" in filepath:
            entries.append({"repo": repo, "file": filepath, "repo_raw": repo_raw})

    return entries


def extract_inline_file_paths(answer: str) -> list[str]:
    """
    Extract file paths from inline backtick references and other patterns.
    Returns paths without repo association.
    """
    paths = set()

    # Pattern: backtick-wrapped file paths with extensions
    backtick_pattern = re.compile(r'`([a-zA-Z0-9_./\-]+\.[a-zA-Z]{1,10})`')
    for match in backtick_pattern.finditer(answer):
        p = match.group(1)
        if "/" in p and not p.startswith("http") and not p.startswith("v1.") and not p.startswith("v2."):
            paths.add(p)

    # Pattern: **bold** file paths
    bold_pattern = re.compile(r'\*\*([a-zA-Z0-9_./\-]+\.[a-zA-Z]{1,10})\*\*')
    for match in bold_pattern.finditer(answer):
        p = match.group(1)
        if "/" in p:
            paths.add(p)

    # Pattern: "File: path/to/file.go" or "file: path/to/file.go"
    file_label_pattern = re.compile(r'[Ff]ile[:\s]+`?([a-zA-Z0-9_./\-]+\.[a-zA-Z]{1,10})`?')
    for match in file_label_pattern.finditer(answer):
        p = match.group(1)
        if "/" in p:
            paths.add(p)

    return list(paths)


def file_exists_in_dataset(filepath: str, repo: str | None = None) -> tuple[bool, str | None]:
    """
    Check if a file path exists in the dataset.
    If repo is given, check only that repo. Otherwise try all repos.
    Returns (exists, matched_repo).
    """
    if repo:
        full = DATASET_DIR / repo / filepath
        if full.is_file():
            return True, repo
        return False, None

    # Try all repos
    for r in DATASET_REPOS:
        full = DATASET_DIR / r / filepath
        if full.is_file():
            return True, r
    return False, None


def evaluate_answer(question: dict, answer_data: dict) -> dict:
    """
    Evaluate a single model answer against the dataset.
    Returns evaluation dict with scores and details.
    """
    model = answer_data.get("model", "unknown")
    status = answer_data.get("status", "unknown")
    answer_text = answer_data.get("answer", "")

    # Handle error/empty answers
    if status == "error" or not answer_text or not answer_text.strip():
        return {
            "model": model,
            "status": status,
            "relevance_score": 0,
            "hallucination_score": 0,
            "files_mentioned": 0,
            "files_found": 0,
            "files_not_found": 0,
            "details": {
                "found_files": [],
                "hallucinated_files": [],
                "note": "Error or empty answer — no evaluation possible"
            }
        }

    # Extract file paths from the answer
    # 1. From structured markdown tables (with repo info)
    table_entries = extract_table_file_entries(answer_text)

    # 2. From inline references (without repo info)
    inline_paths = extract_inline_file_paths(answer_text)

    # Build a unified set of (file, repo_hint) pairs to check
    files_to_check = {}  # filepath -> repo_hint (or None)

    for entry in table_entries:
        files_to_check[entry["file"]] = entry["repo"]

    for p in inline_paths:
        if p not in files_to_check:
            files_to_check[p] = None  # no repo hint

    # Check each file against the dataset
    found_files = []
    hallucinated_files = []

    for filepath, repo_hint in files_to_check.items():
        # Try with repo hint first, then all repos
        exists, matched_repo = file_exists_in_dataset(filepath, repo_hint)
        if not exists and repo_hint:
            # Retry without repo hint (maybe wrong repo association)
            exists, matched_repo = file_exists_in_dataset(filepath, None)

        if exists:
            found_files.append({"file": filepath, "repo": matched_repo})
        else:
            hallucinated_files.append({"file": filepath, "repo_claimed": repo_hint})

    total_files = len(files_to_check)
    num_found = len(found_files)
    num_hallucinated = len(hallucinated_files)

    # --- Calculate Hallucination Score (0-10, higher = more hallucination) ---
    if total_files == 0:
        # No files mentioned at all — can't assess hallucination from files
        # Give a moderate score since we can't verify
        hallucination_score = 5.0
    else:
        hallucination_score = round((num_hallucinated / total_files) * 10, 1)

    # --- Calculate Relevance Score (0-10, higher = more relevant) ---
    # Components:
    #   1. File accuracy component (0-5): fraction of mentioned files that exist
    #   2. Answer substance component (0-3): based on answer length and structure
    #   3. File coverage component (0-2): based on number of real files found

    # File accuracy (0-5)
    if total_files == 0:
        file_accuracy = 0.0
    else:
        file_accuracy = (num_found / total_files) * 5.0

    # Answer substance (0-3)
    answer_len = len(answer_text.strip())
    if answer_len > 2000:
        substance = 3.0
    elif answer_len > 1000:
        substance = 2.0
    elif answer_len > 300:
        substance = 1.0
    else:
        substance = 0.0

    # File coverage (0-2): reward finding more real files (capped)
    if num_found >= 10:
        coverage = 2.0
    elif num_found >= 5:
        coverage = 1.5
    elif num_found >= 3:
        coverage = 1.0
    elif num_found >= 1:
        coverage = 0.5
    else:
        coverage = 0.0

    relevance_score = round(min(file_accuracy + substance + coverage, 10.0), 1)

    return {
        "model": model,
        "status": status,
        "relevance_score": relevance_score,
        "hallucination_score": hallucination_score,
        "files_mentioned": total_files,
        "files_found": num_found,
        "files_not_found": num_hallucinated,
        "details": {
            "found_files": found_files,
            "hallucinated_files": hallucinated_files,
        }
    }


def process_question_folder(folder_path: Path) -> dict | None:
    """Process a single question folder and return evaluation data."""
    question_file = folder_path / "question.json"
    if not question_file.exists():
        return None

    with open(question_file) as f:
        question = json.load(f)

    # Find all model answer files (everything except question.json and evaluation.json)
    answer_files = [
        f for f in sorted(folder_path.iterdir())
        if f.suffix == ".json" and f.name not in ("question.json", "evaluation.json")
    ]

    if not answer_files:
        return None

    evaluations = []
    for af in answer_files:
        try:
            with open(af) as f:
                answer_data = json.load(f)
            eval_result = evaluate_answer(question, answer_data)
            evaluations.append(eval_result)
        except (json.JSONDecodeError, KeyError) as e:
            evaluations.append({
                "model": af.stem,
                "status": "parse_error",
                "relevance_score": 0,
                "hallucination_score": 0,
                "files_mentioned": 0,
                "files_found": 0,
                "files_not_found": 0,
                "details": {"error": str(e)}
            })

    return {
        "question_id": question.get("id", folder_path.name),
        "question": question.get("question", ""),
        "model_evaluations": evaluations,
    }


def main():
    # Find all question folders
    question_folders = sorted([
        d for d in RESULTS_DIR.iterdir()
        if d.is_dir() and d.name.startswith("question_")
    ])

    print(f"Found {len(question_folders)} question folders")
    print(f"Dataset repos: {DATASET_REPOS}")
    print()

    total_evals = 0
    total_errors = 0

    for folder in question_folders:
        result = process_question_folder(folder)
        if result is None:
            print(f"  SKIP {folder.name} — no question.json or no answer files")
            continue

        # Write evaluation.json
        eval_path = folder / "evaluation.json"
        with open(eval_path, "w") as f:
            json.dump(result, f, indent=2)

        # Summary stats
        n_models = len(result["model_evaluations"])
        avg_rel = sum(e["relevance_score"] for e in result["model_evaluations"]) / max(n_models, 1)
        avg_hal = sum(e["hallucination_score"] for e in result["model_evaluations"]) / max(n_models, 1)
        n_errors = sum(1 for e in result["model_evaluations"] if e["status"] != "success")

        total_evals += n_models
        total_errors += n_errors

        print(f"  {folder.name}: {n_models} models | avg_relevance={avg_rel:.1f} | avg_hallucination={avg_hal:.1f} | errors={n_errors}")

    print()
    print(f"Done! Evaluated {total_evals} model answers across {len(question_folders)} questions ({total_errors} errors)")


if __name__ == "__main__":
    main()
