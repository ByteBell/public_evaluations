#!/usr/bin/env python3
"""
API-based Dependency Graph Builder (no cloning required)

Queries the GitHub SBOM API for every repo in the DB, builds the full
cross-org dependency graph across all discovered repos, runs blast radius
analysis, and outputs:

  discovery_results/api_dependency_edges.parquet
  discovery_results/api_repo_graph.gpickle
  discovery_results/api_clusters.parquet
  discovery_results/api_blast_scores.parquet
  discovery_results/api_benchmark_candidates.parquet
  discovery_results/top200_to_clone.txt   ← ranked list for next clone step

Usage:
  export GITHUB_TOKEN=ghp_...
  python3 src/build_api_graph.py [--results discovery_results] [--workers 8]
"""

import os
import sys
import time
import pickle
import sqlite3
import argparse
import threading
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import networkx as nx
import pandas as pd
import community as community_louvain
from tqdm import tqdm

GITHUB_API = "https://api.github.com"


# ── GitHub SBOM fetcher ───────────────────────────────────────────────────────

class RateLimitedSession:
    """Thread-safe requests session with GitHub rate-limit handling."""

    def __init__(self, token: Optional[str]):
        self._lock = threading.Lock()
        self._session = requests.Session()
        self._session.headers.update({
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        })
        if token:
            self._session.headers["Authorization"] = f"Bearer {token}"

    def get(self, url: str, **kwargs) -> Optional[dict]:
        for attempt in range(3):
            try:
                resp = self._session.get(url, timeout=20, **kwargs)
                if resp.status_code == 404:
                    return None  # repo deleted / no dependency graph enabled
                if resp.status_code in (403, 429):
                    reset = int(resp.headers.get("X-RateLimit-Reset", time.time() + 60))
                    wait = max(reset - int(time.time()), 10)
                    print(f"\n  Rate limited — waiting {wait}s", file=sys.stderr)
                    time.sleep(wait)
                    continue
                if resp.status_code == 401:
                    print("\n  401 Bad credentials — check GITHUB_TOKEN", file=sys.stderr)
                    return None
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                if attempt == 2:
                    print(f"\n  Failed {url}: {e}", file=sys.stderr)
                time.sleep(2 ** attempt)
        return None


def fetch_sbom(session: RateLimitedSession, full_name: str) -> List[str]:
    """Return normalized package names declared as dependencies of `full_name`."""
    data = session.get(f"{GITHUB_API}/repos/{full_name}/dependency-graph/sbom")
    if not data:
        return []
    packages = data.get("sbom", {}).get("packages", [])
    # Skip the first entry (it describes the repo itself)
    result = []
    for pkg in packages[1:]:
        name = pkg.get("name", "")
        # SBOM names look like "pip:transformers", "npm:langchain", "go:github.com/..."
        if ":" in name:
            _, pkg_name = name.split(":", 1)
        else:
            pkg_name = name
        # Strip scoped npm @scope/pkg → pkg
        pkg_name = pkg_name.lstrip("@").split("/")[-1] if pkg_name.startswith("@") else pkg_name
        normalized = _norm(pkg_name)
        if normalized:
            result.append(normalized)
    return result


def _norm(s: str) -> str:
    import re
    return re.sub(r"[-_. ]+", "_", s.strip().lower())


# ── Resolution map ────────────────────────────────────────────────────────────

def build_resolution_map(repos: pd.DataFrame) -> Dict[str, str]:
    res = {}
    for _, row in repos.iterrows():
        full = row["full_name"]
        name = row["name"]
        for variant in [name, name.replace("-", "_"), name.replace("_", "-")]:
            res[_norm(variant)] = full
        res[_norm(full)] = full
        res[_norm(full.replace("-", "_"))] = full
    return res


# ── Graph analysis (shared with dependency_graph_pipeline) ───────────────────

def build_graph(repos: pd.DataFrame, edges: List[dict]) -> nx.DiGraph:
    G = nx.DiGraph()
    for _, row in repos.iterrows():
        G.add_node(row["full_name"], language=row.get("language"), stars=row.get("stars", 0))

    for e in edges:
        src, tgt = e["source"], e["target"]
        if not G.has_edge(src, tgt):
            G.add_edge(src, tgt, edge_type="declared", weight=3)

    # Same-org structural edges (weight=1, don't count as dependencies)
    org_map = defaultdict(list)
    for n in G.nodes:
        org_map[n.split("/")[0]].append(n)
    for members in org_map.values():
        for i, a in enumerate(members):
            for b in members[i + 1:]:
                if not G.has_edge(a, b) and not G.has_edge(b, a):
                    G.add_edge(a, b, edge_type="same_org", weight=1)

    return G


def run_clustering(G: nx.DiGraph, min_size: int = 5) -> Tuple[pd.DataFrame, dict]:
    partition = community_louvain.best_partition(G.to_undirected(), weight="weight")
    cluster_map = defaultdict(list)
    for node, cid in partition.items():
        cluster_map[cid].append(node)

    rows = []
    for cid, members in cluster_map.items():
        subg = G.to_undirected().subgraph(members)
        n = len(members)
        density = subg.number_of_edges() / max(n * (n - 1) / 2, 1)
        avg_deg = sum(dict(subg.degree()).values()) / n
        langs = [G.nodes[m].get("language") for m in members if G.nodes[m].get("language")]
        primary = max(set(langs), key=langs.count) if langs else "unknown"
        in_deg = {m: G.in_degree(m) for m in members}
        top5 = sorted(in_deg, key=in_deg.get, reverse=True)[:5]
        status = "valid" if n >= min_size else "filtered_size"
        rows.append(dict(cluster_id=cid, size=n, density=round(density, 4),
                         avg_degree=round(avg_deg, 2), primary_language=primary,
                         top_repos=", ".join(top5), status=status))

    return pd.DataFrame(rows).sort_values("size", ascending=False), dict(cluster_map)


def run_blast_radius(G: nx.DiGraph, cluster_map: dict, clusters_df: pd.DataFrame) -> pd.DataFrame:
    G_rev = G.reverse()
    valid_cids = set(clusters_df.loc[clusters_df["status"] == "valid", "cluster_id"])
    node_to_cid = {n: cid for cid, members in cluster_map.items()
                   for n in members if cid in valid_cids}
    betweenness = nx.betweenness_centrality(G, weight="weight", normalized=True)

    rows = []
    for node in tqdm(G.nodes, desc="  Blast radius", leave=False):
        cid = node_to_cid.get(node)
        if cid is None:
            continue
        cm = set(cluster_map[cid])
        br1 = sum(1 for s in G_rev.successors(node) if s in cm)
        two_hop = set()
        for s in G_rev.successors(node):
            if s in cm:
                two_hop.add(s)
                two_hop.update(t for t in G_rev.successors(s) if t in cm)
        br2 = len(two_hop)
        br_inf = len(set(nx.descendants(G_rev, node)) & cm)
        wbs = 0.0
        try:
            for tgt, hops in nx.single_source_shortest_path_length(G_rev, node).items():
                if tgt != node and tgt in cm and hops > 0:
                    w = G.get_edge_data(tgt, node, {}).get("weight", 1)
                    wbs += w / hops
        except Exception:
            pass
        rows.append(dict(full_name=node, cluster_id=cid,
                         br1=br1, br2=br2, br_inf=br_inf,
                         weighted_blast_score=round(wbs, 4),
                         betweenness=round(betweenness.get(node, 0), 6),
                         in_degree=G.in_degree(node)))
    return pd.DataFrame(rows)


def rank_candidates(blast: pd.DataFrame, repos: pd.DataFrame) -> pd.DataFrame:
    merged = blast.merge(repos[["full_name", "stars", "language", "description"]], on="full_name", how="left")
    parts = []
    for _, grp in merged.groupby("cluster_id"):
        grp = grp.copy()

        def norm(col):
            mx = grp[col].max()
            return grp[col] / mx if mx > 0 else grp[col]

        grp["rank_score"] = 0.4 * norm("br2") + 0.3 * norm("betweenness") + 0.3 * norm("in_degree")
        parts.append(grp)
    return pd.concat(parts).sort_values("rank_score", ascending=False)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", default="discovery_results")
    parser.add_argument("--workers", type=int, default=8,
                        help="Parallel SBOM fetch threads")
    parser.add_argument("--top", type=int, default=200,
                        help="How many top repos to write to top{N}_to_clone.txt")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("ERROR: set GITHUB_TOKEN before running")

    base = Path(args.results)
    db_path = base / "repo_snapshot.sqlite"

    # Load all repos from DB
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM repositories").fetchall()
    repos = pd.DataFrame([dict(r) for r in rows])
    print(f"Loaded {len(repos)} repos from DB")

    resolution = build_resolution_map(repos)
    repo_set = set(repos["full_name"])

    # ── Fetch SBOM for every repo in parallel ─────────────────────────────
    print(f"\n[Component 3-API] Fetching SBOM for {len(repos)} repos ({args.workers} workers)...")
    session = RateLimitedSession(token)
    edges: List[dict] = []
    edge_lock = threading.Lock()
    no_sbom = 0

    def fetch_one(full_name: str):
        pkgs = fetch_sbom(session, full_name)
        local_edges = []
        for pkg in pkgs:
            target = resolution.get(pkg)
            if target and target != full_name and target in repo_set:
                local_edges.append({"source": full_name, "target": target,
                                    "edge_type": "declared", "weight": 3})
        return full_name, local_edges, len(pkgs)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(fetch_one, fn): fn for fn in repos["full_name"]}
        with tqdm(total=len(futures), desc="  Fetching SBOMs") as bar:
            for fut in as_completed(futures):
                fn, local_edges, pkg_count = fut.result()
                if pkg_count == 0:
                    no_sbom += 1
                with edge_lock:
                    edges.extend(local_edges)
                bar.update(1)

    print(f"  Repos with no SBOM data: {no_sbom}")
    dep_df = pd.DataFrame(edges).drop_duplicates(subset=["source", "target"])
    dep_df.to_parquet(base / "api_dependency_edges.parquet", index=False)
    print(f"  Intra-corpus dependency edges: {len(dep_df)}")

    # ── Build graph ────────────────────────────────────────────────────────
    print("\n[Component 5] Building graph...")
    G = build_graph(repos, edges)
    print(f"  {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    with open(base / "api_repo_graph.gpickle", "wb") as f:
        pickle.dump(G, f)

    # ── Cluster ────────────────────────────────────────────────────────────
    print("\n[Component 6] Clustering...")
    clusters_df, cluster_map = run_clustering(G)
    clusters_df.to_parquet(base / "api_clusters.parquet", index=False)
    valid = clusters_df[clusters_df["status"] == "valid"]
    print(f"  {len(clusters_df)} clusters, {len(valid)} valid")
    print(clusters_df[["cluster_id","size","primary_language","status","top_repos"]].head(10).to_string(index=False))

    # ── Blast radius ───────────────────────────────────────────────────────
    print("\n[Component 7] Computing blast radius...")
    blast_df = run_blast_radius(G, cluster_map, clusters_df)
    blast_df.to_parquet(base / "api_blast_scores.parquet", index=False)

    # ── Rank & output ──────────────────────────────────────────────────────
    print("\n[Component 8] Ranking candidates...")
    candidates = rank_candidates(blast_df, repos)
    candidates.to_parquet(base / "api_benchmark_candidates.parquet", index=False)

    top_n = candidates.head(args.top)

    print(f"\n{'='*70}")
    print(f"TOP {args.top} REPOS BY BLAST RADIUS (across {len(repos)} candidates)")
    print(f"{'='*70}")
    pd.set_option("display.max_colwidth", 45)
    pd.set_option("display.width", 130)
    print(top_n[["full_name", "cluster_id", "br1", "br2", "br_inf",
                  "in_degree", "rank_score", "language"]].head(30).to_string(index=False))

    # Write clone list
    clone_list_path = base / f"top{args.top}_to_clone.txt"
    with open(clone_list_path, "w") as f:
        for fn in top_n["full_name"]:
            f.write(fn + "\n")
    print(f"\n  Wrote {args.top} repos to clone → {clone_list_path}")
    print("  Run: python3 src/cross_repo_discovery.py --seeds discovery_results/top200_to_clone.txt --skip-discovery")


if __name__ == "__main__":
    main()
