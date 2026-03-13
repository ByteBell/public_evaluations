#!/usr/bin/env python3
"""
Visualize the dependency graph from the pipeline artifacts.

Produces:
  discovery_results/graph_interactive.html  — interactive (pyvis, open in browser)
  discovery_results/graph_static.png        — static layout (matplotlib)

Usage:
  python3 src/visualize_graph.py [--results discovery_results]
"""

import os
import pickle
import argparse
import webbrowser
from pathlib import Path
from collections import defaultdict

import networkx as nx
import pandas as pd

# ── Colour palette per blast-rank quartile ──────────────────────────────────
QUARTILE_COLORS = ["#e74c3c", "#e67e22", "#3498db", "#95a5a6"]  # high→low


def load_artifacts(base: Path):
    with open(base / "repo_graph.gpickle", "rb") as f:
        G = pickle.load(f)
    blast = pd.read_parquet(base / "blast_scores.parquet")
    clusters = pd.read_parquet(base / "clusters.parquet")
    return G, blast, clusters


def short(full_name: str) -> str:
    return full_name.split("/", 1)[-1]


def build_display_graph(G: nx.DiGraph, blast: pd.DataFrame):
    """Return a subgraph containing only real dependency edges (drop same_org)."""
    dep_G = nx.DiGraph()
    for n, data in G.nodes(data=True):
        dep_G.add_node(n, **data)
    for u, v, data in G.edges(data=True):
        if data.get("edge_type") in ("declared", "import_usage"):
            dep_G.add_edge(u, v, **data)
    return dep_G


# ── Interactive HTML (pyvis) ─────────────────────────────────────────────────

def make_interactive(G: nx.DiGraph, blast: pd.DataFrame, clusters: pd.DataFrame, out_path: str):
    from pyvis.network import Network

    net = Network(
        height="800px", width="100%", directed=True,
        bgcolor="#1a1a2e", font_color="#ecf0f1",
        notebook=False,
    )
    net.barnes_hut(gravity=-12000, central_gravity=0.3, spring_length=120)

    # Score lookup
    score_map = dict(zip(blast["full_name"], blast["rank_score"]))
    br2_map   = dict(zip(blast["full_name"], blast["br2"]))
    br_inf_map = dict(zip(blast["full_name"], blast["br_inf"]))
    cluster_map = dict(zip(blast["full_name"], blast["cluster_id"]))

    # Cluster colours
    unique_clusters = sorted(blast["cluster_id"].unique())
    cluster_palette = ["#e74c3c", "#2ecc71", "#3498db", "#f39c12", "#9b59b6"]
    cluster_color = {cid: cluster_palette[i % len(cluster_palette)]
                     for i, cid in enumerate(unique_clusters)}

    # Add nodes
    for node in G.nodes():
        score = score_map.get(node, 0)
        br2   = br2_map.get(node, 0)
        br_i  = br_inf_map.get(node, 0)
        cid   = cluster_map.get(node, -1)
        color = cluster_color.get(cid, "#7f8c8d")
        size  = max(10, int(score * 40) + 10)

        net.add_node(
            node,
            label=short(node),
            title=f"<b>{node}</b><br>Cluster: {cid}<br>BR2: {br2}  BR∞: {br_i}<br>Rank score: {score:.3f}",
            color=color,
            size=size,
            font={"size": 12, "color": "#ecf0f1"},
        )

    # Add edges
    edge_colors = {"declared": "#e74c3c", "import_usage": "#f39c12"}
    for u, v, data in G.edges(data=True):
        et = data.get("edge_type", "declared")
        net.add_edge(
            u, v,
            color=edge_colors.get(et, "#7f8c8d"),
            title=et,
            width=2 if et == "declared" else 1,
            arrows="to",
        )

    # Legend via heading
    net.set_options("""
    var options = {
      "edges": {
        "smooth": { "type": "dynamic" },
        "arrows": { "to": { "enabled": true, "scaleFactor": 0.5 } }
      },
      "physics": {
        "barnesHut": { "gravitationalConstant": -12000, "springLength": 120 },
        "stabilization": { "iterations": 150 }
      }
    }
    """)

    net.save_graph(out_path)
    print(f"  Interactive graph → {out_path}")
    return out_path


# ── Static PNG (matplotlib + networkx) ──────────────────────────────────────

def make_static(G: nx.DiGraph, blast: pd.DataFrame, out_path: str):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    score_map = dict(zip(blast["full_name"], blast["rank_score"]))
    cluster_map = dict(zip(blast["full_name"], blast["cluster_id"]))

    unique_clusters = sorted(blast["cluster_id"].unique())
    palette = ["#e74c3c", "#2ecc71", "#3498db", "#f39c12", "#9b59b6"]
    cluster_color = {cid: palette[i % len(palette)] for i, cid in enumerate(unique_clusters)}

    node_colors = [cluster_color.get(cluster_map.get(n, -1), "#7f8c8d") for n in G.nodes()]
    node_sizes  = [max(200, int(score_map.get(n, 0) * 2000) + 200) for n in G.nodes()]
    labels      = {n: short(n) for n in G.nodes()}

    edge_colors = []
    for u, v, data in G.edges(data=True):
        et = data.get("edge_type", "declared")
        edge_colors.append("#c0392b" if et == "declared" else "#e67e22")

    fig, ax = plt.subplots(figsize=(22, 16))
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#1a1a2e")

    pos = nx.spring_layout(G, k=2.5, seed=42, weight="weight")

    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, alpha=0.5,
                           arrows=True, arrowsize=12, width=1.2, ax=ax)
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, ax=ax)
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=7,
                             font_color="#ecf0f1", ax=ax)

    legend_patches = [mpatches.Patch(color=cluster_color[cid], label=f"Cluster {cid}")
                      for cid in unique_clusters]
    legend_patches += [
        mpatches.Patch(color="#c0392b", label="declared dep"),
        mpatches.Patch(color="#e67e22", label="import usage"),
    ]
    ax.legend(handles=legend_patches, loc="upper left",
              facecolor="#2c2c54", labelcolor="#ecf0f1", fontsize=9)

    ax.set_title("Dependency Graph — node size ∝ blast rank score",
                 color="#ecf0f1", fontsize=14, pad=12)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"  Static PNG        → {out_path}")


# ─── main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", default="discovery_results")
    parser.add_argument("--no-browser", action="store_true",
                        help="Don't auto-open the HTML file")
    args = parser.parse_args()

    base = Path(args.results)
    G, blast, clusters = load_artifacts(base)
    candidates = pd.read_parquet(base / "benchmark_candidates.parquet")
    # Merge rank_score into blast for convenience
    blast = blast.merge(candidates[["full_name", "rank_score"]], on="full_name", how="left")
    blast["rank_score"] = blast["rank_score"].fillna(0)
    dep_G = build_display_graph(G, blast)

    print(f"Visualizing: {dep_G.number_of_nodes()} nodes, {dep_G.number_of_edges()} dependency edges\n")

    html_path = str(base / "graph_interactive.html")
    png_path  = str(base / "graph_static.png")

    make_interactive(dep_G, blast, clusters, html_path)
    make_static(dep_G, blast, png_path)

    if not args.no_browser:
        webbrowser.open(f"file://{os.path.abspath(html_path)}")
        print("\n  Opened in browser.")


if __name__ == "__main__":
    main()
