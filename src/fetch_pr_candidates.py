#!/usr/bin/env python3
"""
Fetch kubernetes/kubernetes merged PR candidates for single-repo benchmark construction.

Criteria:
  - Merged within the last N days (default 30) — keeps PRs out of model training data
  - size/XL or size/XXL
  - kind/bug, kind/feature, kind/cleanup, or kind/api-change
  - Skips vendor/, docs/, test-only PRs

Tier classification (heuristic, based on changed file paths):
  Black  — Zero-impact traps (bug/cleanup, no API surface change)
  Red    — Internal interface cascades (plugin/scheduler/admission interfaces)
  Orange — Struct/type mutations (types.go changes outside staging API)
  Yellow — Generated code boundary (staging/src/k8s.io/api types.go)
  Grey   — Feature-gate conditional impact

Usage:
  export GITHUB_TOKEN=ghp_...
  python src/fetch_pr_candidates.py
  python src/fetch_pr_candidates.py --days 30 --output pr_candidates.json
  python src/fetch_pr_candidates.py --no-files   # skip per-PR file fetch, faster
"""

import os
import re
import sys
import json
import time
import argparse
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Optional, Union

import requests

REPO = "kubernetes/kubernetes"
GITHUB_API = "https://api.github.com"

SIZE_LABELS = {"size/XL", "size/XXL"}
KIND_LABELS = {"kind/bug", "kind/feature", "kind/cleanup", "kind/api-change"}

# ── File-path heuristics for tier classification ──────────────────────────────

# Yellow: staging API types that feed code generation
STAGING_API_TYPES = "staging/src/k8s.io/api"

# Red: plugin / interface definition files
INTERFACE_FILE_HINTS = [
    "framework/interface",
    "framework/types",
    "plugin/interface",
    "admission/interface",
    "admission/plugin",
    "storage/backend",
    "scheduler/framework",
    "/interface.go",
    "/interfaces.go",
    "plugin/api",
]

# Orange: struct/type mutations in non-staging, non-generated files
STRUCT_TYPE_HINTS = [
    "types.go",
    "/api.go",
    "v1/",
    "v1alpha",
    "v1beta",
    "v2/",
    "core/v1",
]

# Grey: feature-gate registration or alpha/beta feature files
FEATUREGATE_HINTS = [
    "feature_gate",
    "featuregate",
    "features/",
    "pkg/features",
    "alpha_features",
    "beta_features",
]

# Files to exclude when deciding if a PR is test-only
TEST_INDICATORS = ["_test.go", "/test/", "/e2e/", "/testing/", "/testdata/"]

# Files to skip entirely when classifying
SKIP_PREFIXES = ["vendor/", "docs/", "OWNERS", "staging/vendor/"]

GENERATED_HINTS = ["zz_generated", "generated.go", "_generated.", "openapi_generated"]

# Labels that unconditionally mark a PR as test-only
TEST_LABELS = {"kind/testing", "area/test", "area/e2e-test-framework", "sig/testing"}

# Labels worth keeping in the output (everything else is noise)
MEANINGFUL_LABEL_PREFIXES = ("kind/", "size/", "area/", "sig/")

# Title patterns that identify test-only PRs regardless of file content.
# Applied even when --no-files is used.
_TEST_TITLE_RE = re.compile(
    r"(^test[\s:\(\[/]"           # "test: ..." / "test(hpa):" / "test[...]"
    r"|^e2e[\s:\-]"               # "E2E: ..." / "e2e-..."
    r"|\be2e\s+tests?\b"          # "... e2e test(s) ..."
    r"|^add\s+(missing\s+|more\s+|new\s+)?(unit\s+|e2e\s+|integration\s+)?tests?\s+(for|to|of)\b"
    r"|^revert\s+.*\btest\b"      # reverts of test PRs
    r")",
    re.IGNORECASE,
)


def title_looks_like_test(title: str) -> bool:
    return bool(_TEST_TITLE_RE.search(title.strip()))


# ── GitHub helpers ─────────────────────────────────────────────────────────────

def build_headers(token: Optional[str]) -> dict:
    h = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def gh_get(url: str, params: dict, headers: dict, retries: int = 3) -> Union[dict, list]:
    for attempt in range(retries):
        r = requests.get(url, params=params, headers=headers, timeout=30)
        if r.status_code == 403 and "rate limit" in r.text.lower():
            reset = int(r.headers.get("X-RateLimit-Reset", time.time() + 60))
            wait = max(reset - int(time.time()), 5)
            print(f"  Rate limited. Sleeping {wait}s ...", file=sys.stderr)
            time.sleep(wait)
            continue
        if r.status_code == 422:
            # Search index not available for very recent items — return empty
            return {"items": [], "total_count": 0}
        r.raise_for_status()
        return r.json()
    raise RuntimeError(f"Failed after {retries} retries: {url}")


def search_merged_prs(size: str, kind: str, since: str, headers: dict) -> list[dict]:
    """Use GitHub Search API to find merged PRs matching a label pair."""
    query = (
        f'repo:{REPO} is:pr is:merged '
        f'label:"{size}" label:"{kind}" '
        f'merged:>={since}'
    )
    url = f"{GITHUB_API}/search/issues"
    params = {"q": query, "per_page": 100, "sort": "updated", "order": "desc"}
    data = gh_get(url, params, headers)
    return data.get("items", [])


def get_pr_files(pr_number: int, headers: dict) -> list:
    """Fetch all changed file paths for a PR (handles pagination)."""
    url = f"{GITHUB_API}/repos/{REPO}/pulls/{pr_number}/files"
    files = []
    page = 1
    while True:
        data = gh_get(url, {"page": page, "per_page": 100}, headers)
        if not isinstance(data, list) or not data:
            break
        files.extend(f["filename"] for f in data)
        if len(data) < 100:
            break
        page += 1
        time.sleep(0.2)
    return files


# ── Tier classification ────────────────────────────────────────────────────────

def classify(labels: set, files: list) -> tuple:
    """Return (tier, description) based on labels and changed file paths."""
    sig_files = [
        f for f in files
        if not any(f.startswith(p) for p in SKIP_PREFIXES)
        and not any(h in f for h in GENERATED_HINTS)
    ]

    paths = " ".join(sig_files).lower()

    # Yellow: staging API types.go → code generation required
    if any(
        STAGING_API_TYPES in f and f.endswith("types.go")
        for f in sig_files
    ):
        return "Yellow", "Generated Code Boundary"

    # Grey: feature gate touched + feature PR
    if "kind/feature" in labels and any(h in paths for h in FEATUREGATE_HINTS):
        return "Grey", "Feature-Gate Conditional"

    # Red: an interface/plugin definition file changed
    if any(any(h in f.lower() for h in INTERFACE_FILE_HINTS) for f in sig_files):
        return "Red", "Interface Cascade"

    # Red: api-change label almost always means interface/type contract
    if "kind/api-change" in labels:
        return "Red", "Interface Cascade"

    # Black: bug fix or cleanup with no type/struct files touched
    if labels & {"kind/bug", "kind/cleanup"}:
        type_files = [f for f in sig_files if any(h in f for h in STRUCT_TYPE_HINTS)]
        if not type_files:
            return "Black", "Zero-Impact Trap"

    # Orange: struct/type mutation
    if any(any(h in f for h in STRUCT_TYPE_HINTS) for f in sig_files):
        return "Orange", "Struct/Type Mutation"

    # Default for anything else
    return "Orange", "Struct/Type Mutation"


def is_test_only(files: list) -> bool:
    """Return True if every significant file is test/e2e/docs."""
    sig = [
        f for f in files
        if not any(f.startswith(p) for p in SKIP_PREFIXES)
    ]
    if not sig:
        return False
    return all(any(t in f for t in TEST_INDICATORS) for f in sig)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Fetch kubernetes/kubernetes merged PR candidates for benchmark construction"
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("GITHUB_TOKEN"),
        help="GitHub personal access token (or set GITHUB_TOKEN env var)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Only include PRs merged within last N days (default: 30)",
    )
    parser.add_argument(
        "--output",
        default="pr_candidates.json",
        help="Output JSON file path (default: pr_candidates.json)",
    )
    parser.add_argument(
        "--no-files",
        action="store_true",
        help="Skip per-PR file fetch — faster but no tier classification",
    )
    parser.add_argument(
        "--min-files",
        type=int,
        default=5,
        help="Skip PRs with fewer than N significant changed files (default: 5)",
    )
    args = parser.parse_args()

    if not args.token:
        print(
            "ERROR: No GitHub token found.\n"
            "Set GITHUB_TOKEN env var or pass --token.\n"
            "Unauthenticated search is severely rate-limited.",
            file=sys.stderr,
        )
        sys.exit(1)

    headers = build_headers(args.token)
    cutoff_dt = datetime.now(timezone.utc) - timedelta(days=args.days)
    since_str = cutoff_dt.strftime("%Y-%m-%d")

    print(f"Repo       : {REPO}")
    print(f"Since      : {since_str} ({args.days} days ago)")
    print(f"Sizes      : {', '.join(sorted(SIZE_LABELS))}")
    print(f"Kinds      : {', '.join(sorted(KIND_LABELS))}")
    print()

    # ── Step 1: Collect all PRs via search ────────────────────────────────────
    seen: dict[int, dict] = {}

    for size in sorted(SIZE_LABELS):
        for kind in sorted(KIND_LABELS):
            items = search_merged_prs(size, kind, since_str, headers)
            print(f"  {size} + {kind:25s} → {len(items)} PRs")
            for pr in items:
                num = pr["number"]
                if num not in seen:
                    seen[num] = pr
            time.sleep(1.2)  # GitHub Search API: 30 req/min authenticated

    unique_prs = sorted(seen.values(), key=lambda x: x["number"], reverse=True)
    print(f"\nUnique candidate PRs (pre-filter): {len(unique_prs)}")
    if args.no_files:
        print("NOTE: --no-files mode — tiers will be Unknown, file counts will be 0.")
        print("      Run without --no-files for full classification (slower, ~1 API call/PR).")

    # ── Step 2: Enrich with file info and classify ────────────────────────────
    results = []
    skipped_test_only = 0
    skipped_too_small = 0

    for i, pr in enumerate(unique_prs):
        num = pr["number"]
        labels = {lbl["name"] for lbl in pr.get("labels", [])}
        files = []

        # ── Title + label filters — work even with --no-files ─────────────────
        if labels & TEST_LABELS:
            skipped_test_only += 1
            continue

        if title_looks_like_test(pr["title"]):
            skipped_test_only += 1
            continue

        if not args.no_files:
            try:
                files = get_pr_files(num, headers)
            except Exception as e:
                print(f"  PR #{num}: could not fetch files — {e}", file=sys.stderr)
            time.sleep(0.35)

        # Filter out skip prefixes for counting / classification
        sig_files = [
            f for f in files
            if not any(f.startswith(p) for p in SKIP_PREFIXES)
        ]

        # Drop test-only PRs (file-based, only when files were fetched)
        if sig_files and is_test_only(sig_files):
            skipped_test_only += 1
            continue

        # Drop tiny PRs (only enforced when files were fetched)
        if sig_files and len(sig_files) < args.min_files:
            skipped_too_small += 1
            continue

        tier, tier_desc = (
            classify(labels, files) if not args.no_files
            else ("Unknown", "File fetch skipped")
        )

        # Top non-vendor, non-generated, non-test key files for quick human review
        key_files = [
            f for f in sig_files
            if not any(h in f for h in GENERATED_HINTS)
            and not any(t in f for t in TEST_INDICATORS)
        ][:12]

        # Only keep labels that are meaningful for triage (strip noise like approved, lgtm, cncf-cla)
        meaningful_labels = sorted(
            l for l in labels
            if any(l.startswith(p) for p in MEANINGFUL_LABEL_PREFIXES)
        )

        results.append({
            "number": num,
            "title": pr["title"],
            "url": pr["html_url"],
            "merged_at": (pr.get("closed_at") or "")[:10],
            "labels": meaningful_labels,
            "tier": tier,
            "tier_description": tier_desc,
            "files_changed": len(sig_files),
            "key_files": key_files,
        })

        if (i + 1) % 20 == 0:
            print(f"  ... processed {i + 1}/{len(unique_prs)}")

    # ── Step 3: Sort by tier priority ─────────────────────────────────────────
    TIER_ORDER = {"Black": 0, "Red": 1, "Orange": 2, "Yellow": 3, "Grey": 4, "Unknown": 5}
    results.sort(key=lambda x: (TIER_ORDER.get(x["tier"], 5), -x["number"]))

    # ── Step 4: Write JSON ─────────────────────────────────────────────────────
    with open(args.output, "w") as fh:
        json.dump(results, fh, indent=2)

    # ── Step 5: Print summary table ───────────────────────────────────────────
    TIER_COLORS = {
        "Black":   "⬛",
        "Red":     "🟥",
        "Orange":  "🟧",
        "Yellow":  "🟨",
        "Grey":    "⬜",
        "Unknown": "❓",
    }

    print(f"\n{'─'*100}")
    print(f"{'#':>6}  {'Tier':<8}  {'Sig':>4}  {'Merged':>10}  {'Kind':>20}  Title")
    print(f"{'─'*100}")

    for pr in results:
        kind_labels = [l for l in pr["labels"] if l.startswith("kind/")]
        kind_str = ", ".join(kind_labels)
        merged = (pr["merged_at"] or "")[:10]
        icon = TIER_COLORS.get(pr["tier"], "❓")
        title = pr["title"][:55]
        print(f"#{pr['number']:>5}  {icon} {pr['tier']:<6}  {pr['files_changed']:>4}  {merged}  {kind_str:>20}  {title}")

    print(f"{'─'*100}")

    tier_counts = Counter(r["tier"] for r in results)
    print(f"\nKept    : {len(results)} PRs")
    print(f"Skipped : {skipped_test_only} test-only  |  {skipped_too_small} too small (<{args.min_files} sig files)")
    print("\nBy tier:")
    for tier in ["Black", "Red", "Orange", "Yellow", "Grey", "Unknown"]:
        count = tier_counts.get(tier, 0)
        if count:
            print(f"  {TIER_COLORS[tier]} {tier:<8} {count:>3}")

    print(f"\nFull details written to: {args.output}")


if __name__ == "__main__":
    main()
