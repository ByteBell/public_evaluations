#!/usr/bin/env python3
"""
Cross-Repository Blast Radius Discovery System - Component 1 & 2
Implementation of the Repository Discovery and Cloning & Snapshotting stages.

Usage:
  export GITHUB_TOKEN=ghp_...
  python src/cross_repo_discovery.py --seeds seed_repos.txt
"""

import os
import sys
import json
import sqlite3
import subprocess
import argparse
import time
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

import requests
from tqdm import tqdm

GITHUB_API = "https://api.github.com"

class DiscoveryEngine:
    def __init__(self, token: Optional[str], output_dir: str = "discovery_results"):
        self.token = token
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
        
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.repos_dir = os.path.join(output_dir, "repos")
        os.makedirs(self.repos_dir, exist_ok=True)
        
        self.db_path = os.path.join(output_dir, "repo_snapshot.sqlite")
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS repositories (
                    repo_id TEXT PRIMARY KEY,
                    full_name TEXT,
                    org TEXT,
                    name TEXT,
                    html_url TEXT,
                    description TEXT,
                    stars INTEGER,
                    language TEXT,
                    updated_at TEXT,
                    pushed_at TEXT,
                    archived BOOLEAN,
                    discovery_method TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS snapshots (
                    repo_id TEXT PRIMARY KEY,
                    commit_hash TEXT,
                    snapshot_date TEXT,
                    status TEXT,
                    local_path TEXT,
                    FOREIGN KEY(repo_id) REFERENCES repositories(repo_id)
                )
            """)

    def gh_get(self, url: str, params: Optional[Dict] = None) -> Any:
        while True:
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            if response.status_code == 403 and "rate limit" in response.text.lower():
                reset = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
                wait = max(reset - int(time.time()), 5)
                print(f"Rate limited. Waiting {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            response.raise_for_status()
            return response.json()

    def discover_org_repos(self, org: str) -> List[Dict]:
        """Method A: Organization Expansion"""
        print(f"Expanding organization: {org}")
        repos = []
        page = 1
        while True:
            url = f"{GITHUB_API}/orgs/{org}/repos"
            data = self.gh_get(url, {"page": page, "per_page": 100, "type": "public"})
            if not data:
                break
            repos.extend(data)
            if len(data) < 100:
                break
            page += 1
        return repos

    def discover_by_topic(self, topic: str) -> List[Dict]:
        """Method B: Topic Expansion"""
        print(f"Searching by topic: {topic}")
        url = f"{GITHUB_API}/search/repositories"
        # Filter for active, non-archived, high-star repos
        query = f"topic:{topic} archived:false stars:>50 is:public"
        data = self.gh_get(url, {"q": query, "per_page": 100, "sort": "stars", "order": "desc"})
        return data.get("items", [])

    def discover_by_reverse_dependency(self, repo_full_name: str) -> List[Dict]:
        """Method C: Dependency Reverse Search (Simplified)
        In a real scenario, this would search for import statements.
        Here we search for the repo name in code.
        """
        print(f"Reverse searching for dependents of: {repo_full_name}")
        # This is very limited by GitHub Search API constraints
        # Just an example of how it might look
        url = f"{GITHUB_API}/search/code"
        query = f'"{repo_full_name}" in:file'
        try:
            data = self.gh_get(url, {"q": query, "per_page": 50})
            # Map code hits back to repositories
            repo_ids = set()
            repos = []
            for item in data.get("items", []):
                r = item["repository"]
                if r["id"] not in repo_ids:
                    repo_ids.add(r["id"])
                    repos.append(r)
            return repos
        except Exception as e:
            print(f"Code search failed (likely too broad or rate limited): {e}", file=sys.stderr)
            return []

    def filter_and_save(self, repos: List[Dict], method: str):
        valid_repos = []
        cutoff = datetime.now(timezone.utc) - timedelta(days=180) # 6 months
        
        with sqlite3.connect(self.db_path) as conn:
            for r in repos:
                # Basic criteria from plan
                if r.get("archived"): continue
                
                updated_at_str = r.get("updated_at")
                if not updated_at_str:
                    continue
                updated_at = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
                if updated_at < cutoff: continue
                
                if r.get("stargazers_count", 0) < 50: continue
                
                # Supported languages check (simplified)
                lang = r.get("language")
                if lang not in ["Python", "JavaScript", "TypeScript", "Go", "Rust"]:
                    continue

                repo_data = (
                    str(r["id"]),
                    r["full_name"],
                    r["owner"]["login"],
                    r["name"],
                    r["html_url"],
                    r.get("description"),
                    r.get("stargazers_count"),
                    lang,
                    r["updated_at"],
                    r["pushed_at"],
                    r["archived"],
                    method
                )
                
                conn.execute("""
                    INSERT OR IGNORE INTO repositories 
                    (repo_id, full_name, org, name, html_url, description, stars, language, updated_at, pushed_at, archived, discovery_method)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, repo_data)
                valid_repos.append(r)
        
        return valid_repos

    def clone_and_snapshot(self, repo_limit: int = 100, per_org_limit: int = 50):
        """Component 2: Cloning and Snapshotting"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            # Sort by stars descending so highest-quality repos are cloned first
            repos = conn.execute("""
                SELECT * FROM repositories
                WHERE repo_id NOT IN (SELECT repo_id FROM snapshots)
                ORDER BY stars DESC
            """).fetchall()

            # Apply per-org cap to ensure org diversity
            org_counts: Dict[str, int] = {}
            selected = []
            for row in repos:
                org = row["org"]
                if org_counts.get(org, 0) >= per_org_limit:
                    continue
                org_counts[org] = org_counts.get(org, 0) + 1
                selected.append(row)
                if len(selected) >= repo_limit:
                    break

            org_summary = ", ".join(f"{o}:{c}" for o, c in sorted(org_counts.items()))
            print(f"Cloning {len(selected)} repos (org caps: {org_summary})")
            for row in tqdm(selected, desc="Cloning"):
                repo_id = row["repo_id"]
                full_name = row["full_name"]
                html_url = row["html_url"]
                
                target_path = os.path.join(self.repos_dir, full_name)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                
                status = "cloned"
                commit_hash = None
                
                try:
                    if not os.path.exists(target_path):
                        subprocess.run(
                            ["git", "clone", "--depth", "1", html_url, target_path],
                            check=True, capture_output=True
                        )
                    
                    # Get HEAD commit hash
                    result = subprocess.run(
                        ["git", "-C", target_path, "rev-parse", "HEAD"],
                        check=True, capture_output=True, text=True
                    )
                    commit_hash = result.stdout.strip()
                except subprocess.CalledProcessError as e:
                    print(f"Failed to clone {full_name}: {e}")
                    status = "failed"
                
                conn.execute("""
                    INSERT OR REPLACE INTO snapshots (repo_id, commit_hash, snapshot_date, status, local_path)
                    VALUES (?, ?, ?, ?, ?)
                """, (repo_id, commit_hash, datetime.now(timezone.utc).isoformat(), status, target_path))
                conn.commit()

def main():
    parser = argparse.ArgumentParser(description="Cross-Repository Blast Radius Discovery")
    parser.add_argument("--seeds", help="File with seed repositories (one per line, org/repo)")
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"), help="GitHub Token")
    parser.add_argument("--limit", type=int, default=200, help="Limit number of clones")
    parser.add_argument("--per-org-limit", type=int, default=50, help="Max repos to clone per org")
    parser.add_argument("--output", default="discovery_results", help="Output directory")
    parser.add_argument("--skip-discovery", action="store_true",
                        help="Skip discovery phase; only clone repos already in the DB")
    args = parser.parse_args()

    if not args.token:
        print("Warning: No GITHUB_TOKEN provided. Rate limits will be strict.", file=sys.stderr)

    engine = DiscoveryEngine(args.token, args.output)

    if not args.skip_discovery and args.seeds and os.path.exists(args.seeds):
        with open(args.seeds, "r") as f:
            seeds = [line.strip() for line in f if line.strip()]
        
        for seed in seeds:
            print(f"\nProcessing seed: {seed}")
            if "/" not in seed: continue
            org, name = seed.split("/", 1)
            
            # Method A: Org expansion
            org_repos = engine.discover_org_repos(org)
            engine.filter_and_save(org_repos, "org_expansion")
            
            # Method B: Topic expansion (using repo name as a hint for topic if possible)
            # This is heuristic.
            topics = [
                # Kubernetes / cloud-native ecosystem
                "kubernetes", "cloud-native", "observability",
                "service-mesh", "gitops", "helm",
                # ML / AI ecosystem
                "machine-learning", "deep-learning", "llm",
                "generative-ai", "transformers", "mlops",
                # GPU / CUDA ecosystem
                "cuda", "gpu", "nvidia",
            ]
            for topic in topics:
                topic_repos = engine.discover_by_topic(topic)
                engine.filter_and_save(topic_repos, "topic_expansion")
            
            # Method C: Reverse Dependency
            dep_repos = engine.discover_by_reverse_dependency(seed)
            engine.filter_and_save(dep_repos, "reverse_dep")

    # Component 2
    engine.clone_and_snapshot(repo_limit=args.limit, per_org_limit=args.per_org_limit)
    print("\nDiscovery and Snapshotting complete.")
    print(f"Results stored in: {args.output}")

if __name__ == "__main__":
    main()
