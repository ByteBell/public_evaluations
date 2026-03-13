Full pipeline — start to visualisation
Step 1 — Discovery (already done)

export GITHUB_TOKEN=ghp_...
python3 src/cross_repo_discovery.py --seeds seed_repos.txt
# → Finds 1041 repos into discovery_results/repo_snapshot.sqlite
Step 2 — API Graph (running now, no cloning needed)

python3 src/build_api_graph.py --workers 8
# → Queries GitHub SBOM API for all 1041 repos
# → Builds full dependency graph, blast radius scores
# → Writes discovery_results/top200_to_clone.txt (ranked by centrality)
Step 3 — Clone top 200 (highest centrality, not just stars)

python3 src/cross_repo_discovery.py \
  --seeds discovery_results/top200_to_clone.txt \
  --skip-discovery
# → Clones exactly the 200 repos that matter most to the graph
Step 4 — Deep dependency analysis on cloned repos

python3 src/dependency_graph_pipeline.py
# → Parses manifests + AST imports from cloned repos
# → Refines graph, outputs blast_scores + top50_candidates.csv
Step 5 — Visualise

python3 src/visualize_graph.py
# → Opens interactive HTML graph in browser
# → Saves graph_static.png
Why this order matters:

Step 2 builds the full 1041-node graph cheaply via API — no disk needed
Step 3 clones only the 200 most central repos (guaranteed richest subgraph)
Step 4 adds AST-level import edges on top of manifest-declared ones for the cloned set
The final top 50 is chosen by blast radius, not by stars
Monitor Step 2:


tail -f /private/tmp/claude-501/-Users-deadbytes-Documents-ByteBell-public_evaluations/tasks/bcy7658i6.output