# Cross-Repository Blast Radius Discovery System

## Purpose

This system automatically discovers repository ecosystems and identifies repositories where a change in one repo propagates across many dependent repositories (multi-hop impact). The output feeds directly into the benchmark question generation pipeline — telling us *where* to focus, before we ask *what changed*.

This is the upstream precursor to the KubeSingle pipeline. That pipeline operates on a known, bounded repository. This system answers the harder prior question: which ecosystems are worth benchmarking at all, and which repos inside them carry the most systemic risk?

---

## Problem Statement

Selecting benchmark candidates by hand does not scale. Intuition-based repo selection biases toward well-known projects and misses high-blast-radius nodes that are less visible. The system must discover ecosystems and rank candidate repos by their real structural centrality — not their GitHub star count.

Two failure modes to avoid:

- **Over-selection**: treating every downstream consumer as a high-blast-radius repo when most are leaf nodes with no dependents of their own.
- **Under-selection**: missing deeply embedded infrastructure repos that have low visibility but touch hundreds of dependents.

---

## Scope and Boundaries

The system targets:

- Ecosystems with **50 or more repositories** that share a dependency graph
- Languages: Python, JavaScript/TypeScript, Go, Rust (parsers required for each)
- Discovery window: repositories updated within the last 6 months, not archived, with more than 50 stars

Out of scope:

- Monorepos (a single repo containing multiple packages is treated as one node)
- Pure documentation, examples-only, or tutorial repositories
- Repositories whose only dependency relationship is via a fork (forks tracked as a separate edge type, not a dependency edge)
- Vendored dependencies within a repository

---

## Architecture Overview

The system is a linear pipeline of eight components. Each component reads from the previous stage's output and writes a structured artifact. Components do not share in-memory state — every artifact is a file on disk in a defined schema. This makes the pipeline resumable: if any stage fails, it restarts from its input artifact without re-running prior stages.

```
Seed Input
    |
    v
[1] Repository Discovery
    |
    v  repos_raw.parquet
[2] Repository Cloning & Snapshotting
    |
    v  repo_snapshot.sqlite  +  /repos/{org}/{repo}/
[3] Dependency Extraction Engine
    |
    v  dependency_edges.parquet
[4] Import Usage Analyzer
    |
    v  import_edges.parquet
[5] Graph Builder
    |
    v  repo_graph (serialized)
[6] Cluster Discovery
    |
    v  clusters.parquet
[7] Blast Radius Engine
    |
    v  blast_scores.parquet
[8] Dataset Generator
    |
    v  benchmark_candidates.parquet  +  dataset entries
```

---

## Component Specifications

### Component 1 — Repository Discovery

**Responsibility**: Produce the raw repository list from which all downstream work is drawn.

**Inputs**: `seed_repos.txt` — a small, human-curated list of seed repositories (organization/name format).

**Outputs**: `repos_raw.parquet`

**Discovery methods** (run in parallel, results merged and deduplicated):

**Method A — Organization Expansion**
For each seed repo, expand to all repositories under the same GitHub organization. Filter to repositories matching the scope criteria: non-archived, updated within 6 months, stars above threshold. This captures the core of a known ecosystem.

**Method B — Topic Expansion**
Query GitHub's topic search using the primary technology topic associated with each seed (e.g. `langchain`, `opentelemetry`, `nextjs`). This expands beyond the origin organization and captures third-party ecosystem participants.

**Method C — Dependency Reverse Search**
Search GitHub code for import statements referencing the seed package's canonical import path. This is the most important discovery method — it finds downstream consumers who depend on the seed but are not under the same organization and do not use the same topic tag. These are often the highest-blast-radius nodes because they are simultaneously a consumer and a provider to further dependents.

**Filtering rules**:
- Exclude forks unless the fork has diverged significantly (commit count divergence above a threshold)
- Exclude repositories whose primary language is not in the supported parser set
- Exclude repositories with zero activity in the last 6 months (stale dependents are not meaningful blast radius targets)

**Target output size**: 5,000–20,000 repositories per seed ecosystem

---

### Component 2 — Repository Cloning and Snapshotting

**Responsibility**: Create a frozen, reproducible snapshot of every repository for offline analysis.

**Inputs**: `repos_raw.parquet`

**Outputs**:
- `/repos/{org}/{name}/` — shallow clone directory per repository
- `repo_snapshot.sqlite` — commit hash and snapshot date per repository

**Design decisions**:

Shallow clones (`depth=1`) are used exclusively. Full history is not needed for dependency and import analysis, and full clones at this scale would require prohibitive storage.

Every clone records its HEAD commit hash in the snapshot database at clone time. This hash is the key that makes the dataset reproducible — any future re-analysis of a specific question can check out the exact commit that was used when the question was generated.

Cloning is parallelized with a configurable concurrency limit. Rate limiting against the GitHub API and against hosting bandwidth must be respected. Clones that fail (private repos, deleted repos, network errors) are recorded in the snapshot database with a `status` field; they are not retried automatically.

**Idempotency**: If a clone already exists in `/repos/{org}/{name}/` with a matching commit hash in the snapshot database, it is not re-cloned. Re-runs of this stage are safe.

---

### Component 3 — Dependency Extraction Engine

**Responsibility**: Extract explicitly declared dependency edges from package manifests.

**Inputs**: `/repos/{org}/{name}/` (cloned repositories)

**Outputs**: `dependency_edges.parquet`

**Supported manifest formats by language**:

| Language       | Manifest Files                        |
|----------------|---------------------------------------|
| Python         | requirements.txt, pyproject.toml, setup.cfg, setup.py |
| JavaScript/TS  | package.json                          |
| Go             | go.mod                                |
| Rust           | Cargo.toml                            |

**Edge schema**:

Each extracted edge records: source repository, dependency name (as declared in the manifest), dependency version range (if present), and edge type = `declared`.

**Important constraint**: Package names in manifests do not always map directly to repository names. A resolution step is required: given a package name (e.g. `langchain-core`), look up which repository in `repos_raw.parquet` publishes that package. Packages with no matching repository in the corpus are recorded but not added to the graph — they represent external dependencies outside the discovered ecosystem.

**Failure modes**:
- Malformed manifests: record parsing error, skip file, continue to next manifest in the same repo
- Repos with no supported manifest: record as `no_manifest`, skip dependency extraction for that repo (import analysis in Component 4 may still find implicit dependencies)

---

### Component 4 — Import Usage Analyzer

**Responsibility**: Detect dependency relationships that are not declared in package manifests by scanning source file imports at the AST level.

**Inputs**: `/repos/{org}/{name}/` (cloned repositories)

**Outputs**: `import_edges.parquet`

**Why this component exists**:

Manifest-declared dependencies undercount real coupling. A repository may vendor a package, copy source files directly, or import a package without declaring it as a dependency (common in Go with workspace mode, or in Python with PYTHONPATH hacks). These implicit relationships are real blast radius pathways. Any analysis that relies only on manifests will systematically undercount impact.

**Method**: Parse source files using a language-appropriate AST parser (tree-sitter for all languages). Extract all import statements. Map each import path to a repository in the corpus using the same resolution step as Component 3. Imports that resolve to a known corpus repository generate an edge with type = `import_usage`.

**Confidence scoring**: Import edges carry a confidence score between 0 and 1. A direct package path match scores 1.0. A partial match (matching the organization prefix but not the exact repository) scores lower and is flagged for human review. Only edges above a minimum confidence threshold are included in the graph.

**Deduplication**: If a `declared` edge already exists between repo A and repo B, an `import_usage` edge between the same pair is still recorded — both edges are kept in the parquet file. The graph builder (Component 5) uses both edge types with different weights.

---

### Component 5 — Graph Builder

**Responsibility**: Combine dependency and import edges into a single directed weighted multigraph.

**Inputs**: `dependency_edges.parquet`, `import_edges.parquet`, `repos_raw.parquet`, `repo_snapshot.sqlite`

**Outputs**: `repo_graph` (serialized graph file)

**Graph model**:

- **Nodes**: repositories (one node per repository in the corpus)
- **Node attributes**: language, star count, last activity date, cluster id (initially null)
- **Edges**: directed, from dependent to dependency (A → B means A depends on B)
- **Edge types and base weights**:

| Edge Type           | Base Weight | Meaning |
|---------------------|-------------|---------|
| `declared`          | 3           | Manifest-declared dependency |
| `import_usage`      | 2           | AST-detected import without manifest declaration |
| `same_org`          | 1           | Both repos are under the same GitHub organization |
| `fork`              | 1           | One repo is a fork of the other |

**Design decision on forks**: Fork edges are included in the graph but as a distinct type with low weight. They must not be conflated with dependency edges. A fork of a repo does not depend on it in the blast-radius sense — a change to the upstream does not automatically propagate to the fork. Fork edges are included only to allow cluster detection to group the upstream and its active forks together.

**Multi-edge handling**: When both a `declared` edge and an `import_usage` edge exist between the same pair, both are stored as parallel edges in the multigraph. The blast radius engine (Component 7) uses the maximum weight edge for score calculation but records all edge types in the output.

---

### Component 6 — Cluster Discovery

**Responsibility**: Automatically partition the graph into ecosystem clusters without prior knowledge of ecosystem boundaries.

**Inputs**: `repo_graph`

**Outputs**: `clusters.parquet` — one row per repository, with assigned cluster id and cluster-level metrics

**Algorithm**: Louvain community detection on the undirected projection of the graph. Louvain is chosen over alternatives (Girvan-Newman, spectral clustering) because:
- It scales to tens of thousands of nodes without modification
- It does not require the number of clusters as an input parameter
- It produces high-modularity partitions that correspond well to real ecosystem boundaries

**Post-detection filtering**:

Not all detected communities are valid ecosystem clusters. Apply these filters:

- **Size filter**: discard clusters with fewer than 50 repositories
- **Density filter**: discard clusters whose internal edge density is below a minimum threshold (prevents large but weakly connected clusters that are not real ecosystems)
- **Average degree filter**: discard clusters where the average node degree is below a minimum threshold (prevents star-topology clusters where one central repo connects to many unrelated repos)

Discarded clusters are recorded in the output with a `status = filtered` field. They are not passed to downstream components but are available for human review.

**Output fields per cluster**:

Cluster id, size (repository count), internal edge density, average node degree, primary language (majority language in the cluster), top 5 repositories by in-degree (likely core packages), and filter status.

---

### Component 7 — Blast Radius Engine

**Responsibility**: Compute blast radius scores for every repository in every valid cluster.

**Inputs**: `repo_graph`, `clusters.parquet`

**Outputs**: `blast_scores.parquet`

**Metrics computed per repository**:

| Metric | Definition |
|--------|------------|
| BR1 | Count of direct dependents (1-hop successors in the reverse dependency graph) |
| BR2 | Count of repositories reachable within 2 hops in the reverse dependency graph |
| BR-inf | Count of all transitively reachable repositories (full descendants in the reverse graph) |
| Weighted Blast Score | Sum of edge weights along all paths from the repo to all reachable descendants, decayed by hop distance |
| Betweenness Centrality | Standard graph centrality measure — high for repos that sit on many shortest paths between other repos |
| In-degree | Number of incoming dependency edges (raw count, not deduplicated) |

**Weighted Blast Score formula**:

The score accounts for both reach and the strength of dependency relationships. Each reachable node contributes to the score according to the maximum-weight edge type on the path to it, decayed by the hop distance. `declared` edges carry full weight; `import_usage` edges carry reduced weight; `fork` edges carry minimal weight.

**Scope**: Blast radius is computed within the cluster boundary. A repo's blast radius score reflects only the impact within its ecosystem cluster, not the entire corpus. This prevents large general-purpose utilities (e.g. `requests`, `lodash`) from dominating all rankings — their score reflects their role within a specific ecosystem cluster, not their global install count.

---

### Component 8 — Dataset Generator

**Responsibility**: Produce the final ranked candidate list and structured dataset entries for human review and downstream use.

**Inputs**: `blast_scores.parquet`, `clusters.parquet`, `repo_graph`, `repo_snapshot.sqlite`

**Outputs**:
- `benchmark_candidates.parquet` — ranked list of candidate repositories
- `dataset/{cluster_id}/{repo_id}/entry.json` — one structured entry per candidate repository

**Ranking formula**:

Each repository in a valid cluster receives a final ranking score composed of three weighted factors:

| Factor | Weight | Source |
|--------|--------|--------|
| BR2 score (2-hop impact normalized within cluster) | 0.4 | Blast Radius Engine |
| Betweenness centrality (normalized within cluster) | 0.3 | Blast Radius Engine |
| Activity score (recent commit frequency, normalized) | 0.3 | repo_snapshot.sqlite |

The activity score component prevents high-scoring dormant repos from ranking above active ones. A change to a dormant repo is unlikely to propagate quickly to downstream consumers; the ecosystem effect is real but less time-sensitive for benchmarking purposes.

**Dataset entry schema**:

Each entry captures the repository identity, its cluster membership, its blast radius metrics, the dependency paths that define its impact, and the commit snapshot used. This entry becomes the input for question generation — it tells the question generator where the impact starts and how far it can propagate, without prescribing what change to ask about.

---

## Storage Design

| Artifact | Format | Rationale |
|----------|--------|-----------|
| `repos_raw.parquet` | Parquet | Columnar, efficient filtering; compatible with pandas and polars |
| `repo_snapshot.sqlite` | SQLite | Relational lookups by repo id and commit hash; lightweight, no server |
| `dependency_edges.parquet` | Parquet | Large row count (millions of edges); columnar access patterns |
| `import_edges.parquet` | Parquet | Same as above |
| `repo_graph` | gpickle (initial) / Neo4j (scaled) | Start with in-process NetworkX for development; migrate to Neo4j when graph exceeds 100k nodes |
| `clusters.parquet` | Parquet | Same columnar access pattern |
| `blast_scores.parquet` | Parquet | Final ranked output; read by downstream systems |
| `/repos/{org}/{name}/` | Filesystem | Git working trees; accessed by language parsers |

**Migration trigger for Neo4j**: When the combined node and edge count exceeds a threshold where NetworkX operations (betweenness centrality, community detection) take longer than 4 hours on available hardware, migrate the graph to Neo4j. Community detection can then be offloaded to the GDS library.

---

## Concurrency Model

Two distinct concurrency strategies are used depending on the bottleneck:

**I/O-bound stages** (Discovery, Cloning): `asyncio`-based concurrency. GitHub API calls and git clone operations spend most time waiting on the network. Async coroutines with a concurrency cap and a per-domain rate limiter are appropriate.

**CPU-bound stages** (Dependency Extraction, Import Analysis): `multiprocessing`-based parallelism. AST parsing is CPU-bound. Each worker process handles a shard of the repository list independently. Results are written to a staging parquet file per shard and merged at the end of the stage.

**Graph operations** (Graph Builder, Blast Radius Engine): Single-process with NetworkX (initial). These operations are memory-bound at large scale. For the initial implementation targeting under 20k nodes, single-process is sufficient.

---

## Data Quality and Validation

Each stage must pass a validation check before the next stage begins:

| Stage | Validation |
|-------|------------|
| Discovery | Output contains at least 1,000 repositories; no duplicate repo ids |
| Cloning | Snapshot database entry exists for every repo in repos_raw.parquet with status = cloned or status = failed; no orphaned clone directories |
| Dependency Extraction | At least 10% of cloned repositories yielded at least one edge; no edges reference a repo not in repos_raw.parquet |
| Import Analysis | Confidence score distribution is not degenerate (not all scores at 0 or 1) |
| Graph Builder | Graph is connected (no isolated nodes from repos_raw.parquet); edge count exceeds node count |
| Cluster Discovery | At least one cluster passes all filters; no cluster contains a repo that does not exist in repos_raw.parquet |
| Blast Radius Engine | BR1 ≤ BR2 ≤ BR-inf for every repository; weighted blast score is non-negative |
| Dataset Generator | Output count matches the count of repositories in valid clusters; no entry references a commit hash not in repo_snapshot.sqlite |

---

## Key Engineering Constraints

**Reproducibility**: The dataset must be reproducible from the snapshot database alone. Any re-run of the blast radius engine or dataset generator on the same commit hashes must produce identical output. Non-determinism is only acceptable in the discovery and cloning stages, where the live state of GitHub changes over time.

**Forks are not dependencies**: This is the most important semantic constraint in the entire system. A fork relationship must never be treated equivalently to a dependency relationship when computing blast radius. The two edge types are tracked separately throughout and are never collapsed.

**Package name resolution is lossy**: Not every package name in a manifest resolves to a repository in the corpus. Missing resolutions are not errors — they represent external dependencies. The system must not halt or warn on unresolved packages; it must record the miss and continue.

**Activity recency is a first-class signal**: A repository that has not been updated in over 6 months is excluded from discovery. A repository that passes discovery but has low recent activity receives a lower activity score in the final ranking. Stale ecosystem participants produce misleading blast radius estimates.

---

## Relationship to Existing Benchmarks

This system is designed to feed two downstream uses:

1. **Benchmark candidate selection for multi-repo questions**: The blast radius scores and cluster structures produced here define which ecosystem clusters are worth building multi-repo benchmark questions around. The cluster must have at least 50 repositories and at least one repo with a BR2 score indicating meaningful 2-hop impact.

2. **Inspiration for single-repo question selection**: Within a cluster, the highest-blast-radius repos tend to be the ones where a single internal change (interface addition, struct mutation) has the broadest intra-ecosystem consequence. These are exactly the repos that the KubeSingle-style pipeline targets. The cross-repo system identifies which repos deserve a single-repo deep-dive treatment.

The output of this system does not directly generate questions. It generates a ranked candidate list that is reviewed by a human before being passed to a question generation pipeline.

---

## Rollout Phases

### Phase 1 — Foundation (Weeks 1–2)

Discovery, cloning, and snapshotting for one seed ecosystem. Validate the output schema and storage layout before building downstream components. Target: one ecosystem cluster, 200–500 repositories, fully snapshotted.

### Phase 2 — Extraction (Weeks 2–3)

Dependency extraction and import analysis for the Phase 1 corpus. Validate that the extraction recall is reasonable by spot-checking 20 randomly sampled repositories manually against their manifests and source files.

### Phase 3 — Graph and Clustering (Week 4)

Build the graph, run community detection, validate that the recovered clusters match known ecosystem boundaries. For a LangChain seed, the primary cluster should contain langchain-core, langchain-community, and major integration packages — if it does not, the edge weights or discovery methods need adjustment.

### Phase 4 — Blast Radius and Ranking (Week 5–6)

Run the blast radius engine and produce the first candidate list. Compare the top-10 ranked repos against expert intuition. The ranking should surface infrastructure packages (schema libraries, core abstractions), not application-layer repos.

### Phase 5 — Multi-Ecosystem Expansion (Week 7)

Add additional seed ecosystems and run the full pipeline in parallel. Validate that clusters from different seeds do not incorrectly merge (an OpenTelemetry repo should not appear in a LangChain cluster).

---

## Future Extension — Continuous Ecosystem Mining

The current design is a batch pipeline: it runs once, produces a snapshot, and stops. A continuous variant would monitor for new repositories entering the ecosystem, re-run import analysis on modified repositories, and update blast scores incrementally as the graph evolves.

This extension is deferred until the batch pipeline is validated. The artifact schemas and component boundaries defined here are chosen to make this extension tractable: because every stage reads and writes files in defined formats, a streaming variant can replace individual stages without modifying the rest of the pipeline.

A temporal propagation analysis layer — detecting upstream breaking commits and measuring how long downstream repositories take to adapt — is a distinct research contribution that can be built on top of the dataset this system produces. It requires commit history (not just shallow clones) and is therefore a separate pipeline that ingests the candidate list produced here.
