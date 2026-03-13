#!/usr/bin/env python3
"""
Cross-Repository Blast Radius Pipeline — Components 3–8

Reads from discovery_results (repo_snapshot.sqlite + cloned repos) and produces:
  dependency_edges.parquet
  import_edges.parquet
  repo_graph.gpickle
  clusters.parquet
  blast_scores.parquet
  benchmark_candidates.parquet

Usage:
  python3 src/dependency_graph_pipeline.py [--results discovery_results]
"""

import os
import re
import ast
import sys
import json
import sqlite3
import pickle
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

import networkx as nx
import pandas as pd
import community as community_louvain  # python-louvain

try:
    import tomli
    def load_toml(path: str):
        with open(path, "rb") as f:
            return tomli.load(f)
except ImportError:
    def load_toml(path: str):
        return {}

# ─── Helpers ──────────────────────────────────────────────────────────────────

def norm_pkg(name: str) -> str:
    """Normalize a package name: lowercase, hyphens→underscores."""
    return re.sub(r"[-_. ]+", "_", name.strip().lower())

def pkg_from_spec(spec: str) -> str:
    """Strip version specifiers from a dependency string."""
    return re.split(r"[>=<!;\[\s@]", spec.strip())[0].strip()


# ─── Component 3: Dependency Extraction ───────────────────────────────────────

def parse_requirements_txt(path: str) -> List[str]:
    pkgs = []
    try:
        for line in open(path):
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            pkgs.append(pkg_from_spec(line))
    except Exception:
        pass
    return pkgs


def parse_pyproject_toml(path: str) -> List[str]:
    pkgs = []
    try:
        data = load_toml(path)
        # PEP 621
        for dep in data.get("project", {}).get("dependencies", []):
            pkgs.append(pkg_from_spec(dep))
        # Poetry
        for dep in data.get("tool", {}).get("poetry", {}).get("dependencies", {}).keys():
            if dep.lower() != "python":
                pkgs.append(pkg_from_spec(dep))
        # Hatch / flit optional-dependencies
        for group in data.get("project", {}).get("optional-dependencies", {}).values():
            for dep in group:
                pkgs.append(pkg_from_spec(dep))
    except Exception:
        pass
    return pkgs


def parse_setup_py(path: str) -> List[str]:
    """Best-effort static parse of setup.py install_requires."""
    pkgs = []
    try:
        src = open(path).read()
        # Find install_requires=[...]
        m = re.search(r"install_requires\s*=\s*\[([^\]]*)\]", src, re.DOTALL)
        if m:
            for item in re.findall(r'["\']([^"\']+)["\']', m.group(1)):
                pkgs.append(pkg_from_spec(item))
    except Exception:
        pass
    return pkgs


def parse_package_json(path: str) -> List[str]:
    pkgs = []
    try:
        data = json.load(open(path))
        for key in ("dependencies", "peerDependencies"):
            pkgs.extend(data.get(key, {}).keys())
    except Exception:
        pass
    return pkgs


def parse_go_mod(path: str) -> List[str]:
    pkgs = []
    try:
        in_require = False
        for line in open(path):
            line = line.strip()
            if line.startswith("require ("):
                in_require = True
                continue
            if in_require:
                if line == ")":
                    in_require = False
                    continue
                parts = line.split()
                if parts:
                    pkgs.append(parts[0])
            elif line.startswith("require "):
                parts = line.split()
                if len(parts) >= 2:
                    pkgs.append(parts[1])
    except Exception:
        pass
    return pkgs


def parse_cargo_toml(path: str) -> List[str]:
    pkgs = []
    try:
        data = load_toml(path)
        for section in ("dependencies", "dev-dependencies", "build-dependencies"):
            pkgs.extend(data.get(section, {}).keys())
    except Exception:
        pass
    return pkgs


def extract_declared_deps(repo_path: str) -> List[Tuple[str, str]]:
    """Return list of (pkg_name_normalized, manifest_file) for root manifests only."""
    results = []
    root = Path(repo_path)

    manifest_parsers = {
        "requirements.txt": parse_requirements_txt,
        "requirements-dev.txt": parse_requirements_txt,
        "pyproject.toml": parse_pyproject_toml,
        "setup.py": parse_setup_py,
        "package.json": parse_package_json,
        "go.mod": parse_go_mod,
        "Cargo.toml": parse_cargo_toml,
    }

    for fname, parser in manifest_parsers.items():
        fpath = root / fname
        if fpath.exists():
            for pkg in parser(str(fpath)):
                if pkg:
                    results.append((norm_pkg(pkg), fname))

    return results


# ─── Component 4: Import Usage Analyzer ───────────────────────────────────────

def extract_python_imports(path: str) -> List[str]:
    """Parse Python source with ast; return top-level module names."""
    imports = set()
    try:
        src = open(path, encoding="utf-8", errors="ignore").read()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])
    except Exception:
        pass
    return list(imports)


def extract_js_imports(path: str) -> List[str]:
    """Regex-based JS/TS import extraction."""
    imports = set()
    try:
        src = open(path, encoding="utf-8", errors="ignore").read()
        # import ... from 'pkg'  |  require('pkg')
        for m in re.finditer(r"""(?:from|require)\s*\(\s*['"]([^'"./][^'"]*)['"]\s*\)|from\s+['"]([^'"./][^'"]*)['"]""", src):
            pkg = m.group(1) or m.group(2)
            if pkg:
                # strip scoped package: @scope/name → scope/name, normalize to first segment
                imports.add(pkg.split("/")[0].lstrip("@"))
    except Exception:
        pass
    return list(imports)


def extract_go_imports(path: str) -> List[str]:
    imports = set()
    try:
        src = open(path, encoding="utf-8", errors="ignore").read()
        for m in re.finditer(r'"([^"]+)"', src):
            pkg = m.group(1)
            if "/" in pkg and not pkg.startswith("."):
                imports.add(pkg)
    except Exception:
        pass
    return list(imports)


LANG_EXT = {
    ".py": extract_python_imports,
    ".js": extract_js_imports,
    ".ts": extract_js_imports,
    ".tsx": extract_js_imports,
    ".jsx": extract_js_imports,
    ".go": extract_go_imports,
}


def extract_import_deps(repo_path: str, max_files: int = 500) -> List[Tuple[str, str]]:
    """Walk repo source files (skip vendor/.git) and collect imports."""
    results = []
    root = Path(repo_path)
    skip_dirs = {".git", "vendor", "node_modules", "__pycache__", ".tox", "dist", "build"}
    count = 0

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for fname in filenames:
            ext = Path(fname).suffix
            if ext not in LANG_EXT:
                continue
            if count >= max_files:
                break
            full = os.path.join(dirpath, fname)
            for imp in LANG_EXT[ext](full):
                if imp:
                    results.append((norm_pkg(imp), ext.lstrip(".")))
            count += 1

    return results


# ─── Resolution map ───────────────────────────────────────────────────────────

def build_resolution_map(repos: pd.DataFrame) -> Dict[str, str]:
    """Map normalized package names → full_name (org/repo)."""
    res = {}
    for _, row in repos.iterrows():
        full = row["full_name"]
        name = row["name"]
        # repo name variants
        for variant in [name, name.replace("-", "_"), name.replace("_", "-")]:
            res[norm_pkg(variant)] = full
        # org/name
        res[norm_pkg(full)] = full
        res[norm_pkg(full.replace("-", "_"))] = full
    return res


# ─── Main pipeline ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Dependency Graph Pipeline (Components 3–8)")
    parser.add_argument("--results", default="discovery_results", help="discovery_results directory")
    args = parser.parse_args()

    base = Path(args.results)
    db_path = base / "repo_snapshot.sqlite"
    repos_dir = base / "repos"

    # ── Load repo list from DB ──────────────────────────────────────────────
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        repos_raw = conn.execute("""
            SELECT r.*, s.commit_hash, s.local_path
            FROM repositories r
            JOIN snapshots s ON r.repo_id = s.repo_id
            WHERE s.status = 'cloned'
        """).fetchall()

    repos = pd.DataFrame([dict(r) for r in repos_raw])
    print(f"Loaded {len(repos)} cloned repositories from DB")

    resolution = build_resolution_map(repos)
    repo_set = set(repos["full_name"])

    # ── Component 3: Dependency Extraction ─────────────────────────────────
    print("\n[Component 3] Extracting declared dependencies from manifests...")
    dep_edges = []
    for _, row in repos.iterrows():
        src_repo = row["full_name"]
        local_path = row["local_path"]
        if not local_path or not os.path.isdir(local_path):
            continue
        for pkg_norm, manifest in extract_declared_deps(local_path):
            target = resolution.get(pkg_norm)
            if target and target != src_repo and target in repo_set:
                dep_edges.append({
                    "source": src_repo,
                    "target": target,
                    "edge_type": "declared",
                    "manifest": manifest,
                    "weight": 3,
                })

    dep_df = pd.DataFrame(dep_edges).drop_duplicates(subset=["source", "target", "edge_type"])
    dep_df.to_parquet(base / "dependency_edges.parquet", index=False)
    print(f"  Found {len(dep_df)} declared dependency edges")

    # ── Component 4: Import Usage Analyzer ─────────────────────────────────
    print("\n[Component 4] Scanning source imports...")
    import_edges = []
    for _, row in repos.iterrows():
        src_repo = row["full_name"]
        local_path = row["local_path"]
        if not local_path or not os.path.isdir(local_path):
            continue
        for pkg_norm, lang in extract_import_deps(local_path):
            target = resolution.get(pkg_norm)
            if target and target != src_repo and target in repo_set:
                import_edges.append({
                    "source": src_repo,
                    "target": target,
                    "edge_type": "import_usage",
                    "lang": lang,
                    "confidence": 1.0,
                    "weight": 2,
                })

    imp_df = pd.DataFrame(import_edges).drop_duplicates(subset=["source", "target", "edge_type"]) if import_edges else pd.DataFrame(columns=["source","target","edge_type","lang","confidence","weight"])
    imp_df.to_parquet(base / "import_edges.parquet", index=False)
    print(f"  Found {len(imp_df)} import usage edges")

    # ── Component 5: Graph Builder ──────────────────────────────────────────
    print("\n[Component 5] Building dependency graph...")
    G = nx.DiGraph()

    for _, row in repos.iterrows():
        G.add_node(row["full_name"],
                   language=row.get("language"),
                   stars=row.get("stars", 0),
                   updated_at=row.get("updated_at"))

    all_edges = pd.concat([dep_df[["source","target","edge_type","weight"]],
                           imp_df[["source","target","edge_type","weight"]]], ignore_index=True)

    for _, e in all_edges.iterrows():
        if G.has_edge(e["source"], e["target"]):
            existing = G[e["source"]][e["target"]]
            if e["weight"] > existing.get("weight", 0):
                G[e["source"]][e["target"]]["weight"] = e["weight"]
                G[e["source"]][e["target"]]["edge_type"] = e["edge_type"]
        else:
            G.add_edge(e["source"], e["target"],
                       edge_type=e["edge_type"],
                       weight=int(e["weight"]))

    # same_org edges
    org_map = defaultdict(list)
    for n in G.nodes:
        org = n.split("/")[0]
        org_map[org].append(n)
    for org, members in org_map.items():
        for i, a in enumerate(members):
            for b in members[i+1:]:
                if not G.has_edge(a, b) and not G.has_edge(b, a):
                    G.add_edge(a, b, edge_type="same_org", weight=1)

    with open(base / "repo_graph.gpickle", "wb") as f:
        pickle.dump(G, f)

    print(f"  Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # ── Component 6: Cluster Discovery ─────────────────────────────────────
    print("\n[Component 6] Running Louvain community detection...")
    G_undirected = G.to_undirected()
    partition = community_louvain.best_partition(G_undirected, weight="weight")

    cluster_map = defaultdict(list)
    for node, cid in partition.items():
        cluster_map[cid].append(node)

    cluster_rows = []
    for cid, members in cluster_map.items():
        subg = G_undirected.subgraph(members)
        n = len(members)
        possible_edges = n * (n - 1) / 2 if n > 1 else 1
        density = subg.number_of_edges() / possible_edges
        avg_degree = sum(dict(subg.degree()).values()) / n if n > 0 else 0
        langs = [G.nodes[m].get("language") for m in members if G.nodes[m].get("language")]
        primary_lang = max(set(langs), key=langs.count) if langs else "unknown"
        # top 5 by in-degree in directed graph
        in_degrees = {m: G.in_degree(m) for m in members}
        top5 = sorted(in_degrees, key=in_degrees.get, reverse=True)[:5]

        status = "valid"
        if n < 5:  # relaxed from 50 since we only have 50 repos total
            status = "filtered_size"
        elif density < 0.01:
            status = "filtered_density"

        cluster_rows.append({
            "cluster_id": cid,
            "size": n,
            "density": round(density, 4),
            "avg_degree": round(avg_degree, 2),
            "primary_language": primary_lang,
            "top_repos": ", ".join(top5),
            "status": status,
        })

    clusters_df = pd.DataFrame(cluster_rows).sort_values("size", ascending=False)
    clusters_df.to_parquet(base / "clusters.parquet", index=False)
    print(f"  Detected {len(clusters_df)} clusters ({(clusters_df['status']=='valid').sum()} valid)")

    # ── Component 7: Blast Radius Engine ───────────────────────────────────
    print("\n[Component 7] Computing blast radius scores...")
    G_reverse = G.reverse()

    valid_cluster_ids = set(clusters_df.loc[clusters_df["status"] == "valid", "cluster_id"])
    node_to_cluster = {node: cid for cid, members in cluster_map.items()
                       for node in members if cid in valid_cluster_ids}

    # Betweenness centrality on full graph
    betweenness = nx.betweenness_centrality(G, weight="weight", normalized=True)

    blast_rows = []
    for node in G.nodes:
        cid = node_to_cluster.get(node)
        if cid is None:
            continue

        cluster_members = set(cluster_map[cid])

        # BR1: direct dependents within cluster
        br1 = sum(1 for s in G_reverse.successors(node) if s in cluster_members)

        # BR2: 2-hop reachable within cluster
        two_hop = set()
        for s in G_reverse.successors(node):
            if s in cluster_members:
                two_hop.add(s)
                two_hop.update(t for t in G_reverse.successors(s) if t in cluster_members)
        br2 = len(two_hop)

        # BR-inf: all reachable within cluster
        reachable = set(nx.descendants(G_reverse, node)) & cluster_members
        br_inf = len(reachable)

        # Weighted blast score: sum of weight/hop for all reachable within cluster
        wbs = 0.0
        try:
            lengths = nx.single_source_shortest_path_length(G_reverse, node)
            for target, hops in lengths.items():
                if target != node and target in cluster_members and hops > 0:
                    edge_data = G.get_edge_data(target, node) or {}
                    w = edge_data.get("weight", 1)
                    wbs += w / hops
        except Exception:
            pass

        blast_rows.append({
            "full_name": node,
            "cluster_id": cid,
            "br1": br1,
            "br2": br2,
            "br_inf": br_inf,
            "weighted_blast_score": round(wbs, 4),
            "betweenness": round(betweenness.get(node, 0), 6),
            "in_degree": G.in_degree(node),
        })

    blast_df = pd.DataFrame(blast_rows)
    blast_df.to_parquet(base / "blast_scores.parquet", index=False)

    # ── Component 8: Dataset Generator + Output ────────────────────────────
    print("\n[Component 8] Ranking candidates...")

    # Merge cluster info and repo metadata
    merged = blast_df.merge(
        repos[["full_name", "stars", "language", "description", "updated_at"]],
        on="full_name", how="left"
    )

    # Normalize scores within cluster for ranking
    def norm_col(df, col):
        mx = df[col].max()
        return df[col] / mx if mx > 0 else df[col]

    ranked_parts = []
    for cid, grp in merged.groupby("cluster_id"):
        grp = grp.copy()
        grp["_br2_n"] = norm_col(grp, "br2")
        grp["_btw_n"] = norm_col(grp, "betweenness")
        # activity: use stars as proxy (no commit freq in shallow clone)
        grp["_act_n"] = norm_col(grp, "stars")
        grp["rank_score"] = (0.4 * grp["_br2_n"] +
                              0.3 * grp["_btw_n"] +
                              0.3 * grp["_act_n"])
        ranked_parts.append(grp)

    candidates = pd.concat(ranked_parts).sort_values("rank_score", ascending=False)
    candidates = candidates.drop(columns=["_br2_n", "_btw_n", "_act_n"])
    candidates.to_parquet(base / "benchmark_candidates.parquet", index=False)

    # Top-50 shortlist
    top50 = candidates.head(50)[["full_name", "cluster_id", "br1", "br2", "br_inf",
                                  "weighted_blast_score", "in_degree", "rank_score",
                                  "language", "stars"]]
    top50.to_parquet(base / "top50_candidates.parquet", index=False)
    top50.to_csv(base / "top50_candidates.csv", index=False)

    # ── Print dependency graph ──────────────────────────────────────────────
    print("\n" + "="*70)
    print("DEPENDENCY GRAPH SUMMARY")
    print("="*70)
    print(f"  Nodes (repos):  {G.number_of_nodes()}")
    print(f"  Edges (total):  {G.number_of_edges()}")
    print(f"  Declared deps:  {len(dep_df)}")
    print(f"  Import edges:   {len(imp_df)}")

    print("\n── Dependency Edges (A depends on B) ──")
    declared_only = [(e[0], e[1]) for e in G.edges(data=True) if e[2]["edge_type"] in ("declared","import_usage")]
    if declared_only:
        for src, tgt in sorted(declared_only):
            et = G[src][tgt]["edge_type"]
            marker = "  →" if et == "declared" else "  ⤳"
            print(f"  {src:40s} {marker}  {tgt}")
    else:
        print("  (no intra-corpus dependency edges found)")

    print("\n── Top 20 Repos by Blast Radius (BR2 within cluster) ──")
    top = candidates[["full_name", "cluster_id", "br1", "br2", "br_inf",
                       "weighted_blast_score", "in_degree", "rank_score"]].head(20)
    pd.set_option("display.max_colwidth", 40)
    pd.set_option("display.width", 120)
    print(top.to_string(index=False))

    print("\n── Cluster Summary ──")
    print(clusters_df[["cluster_id","size","density","avg_degree","primary_language","status","top_repos"]].to_string(index=False))

    print(f"\nArtifacts saved to: {base}/")
    for f in ["dependency_edges.parquet","import_edges.parquet","repo_graph.gpickle",
              "clusters.parquet","blast_scores.parquet","benchmark_candidates.parquet"]:
        print(f"  {f}")


if __name__ == "__main__":
    main()
