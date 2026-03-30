# GitNexus Analysis Report
*Prepared: 2026-03-16 | Analyst: Claude Sonnet 4.6 via ByteBell Evaluation Framework*

---

## 1. What Was Analyzed

**Repository:** `comparison_repo/GitNexus` — the GitNexus tool itself, indexed against its own engine.
**Tool version:** GitNexus v1.4.0 (globally installed as v1.4.1)
**Tagline:** *"Graph-powered code intelligence for AI agents. Index any codebase, query via MCP or CLI."*

Three repositories were indexed during this session:

| Repository | Files | Symbols (nodes) | Relationships (edges) | Clusters | Execution Flows | Index Time |
|---|---|---|---|---|---|---|
| `grafana-operator` | 552 | 1,966 | 4,206 | 53 | 129 | 2.5s |
| `prometheus-operator` | 1,457 | 8,823 | 19,744 | 181 | 300 | 3.9s |
| **GitNexus** (self) | 340 | 1,998 | 5,457 | 166 | 151 | **2.9s** |

---

## 2. How It Works — The Ingestion Pipeline

When `gitnexus analyze` runs, it executes a multi-phase pipeline:

### Phase 1 — Repository Ingestion
1. **File extraction** (`Scanning files`) — walks the git root, skips files >512KB (generated/vendored), collects TypeScript/Go/Python/JS source files.
2. **Structure building** (`Building structure`) — maps directory hierarchy and module boundaries.
3. **Code parsing** (`Parsing code`) — extracts all symbols: Functions, Classes, Methods, Interfaces, Variables.
4. **Import resolution** (`Resolving imports`) — builds the dependency graph (who imports whom).
5. **Call tracing** (`Tracing calls`) — tracks function and method invocations across files.
6. **Inheritance extraction** (`Extracting inheritance`) — resolves `extends`/`implements` chains.

### Phase 2 — Graph Construction
7. **Community detection** (`Detecting communities`) — applies the Leiden algorithm (bundled in `vendor/`) to cluster symbols into functional modules based on call density.
8. **Process detection** (`Detecting processes`) — identifies cross-cutting execution flows (e.g., `AppStateProvider → CreateKnowledgeGraph`, `CreateServer → CheckStaleness`).

### Phase 3 — Storage
9. **KuzuDB load** (`Loading into LadybugDB`) — the entire graph (nodes + edges) is persisted to KuzuDB, an embedded columnar graph database stored in `.gitnexus/` per repo.
10. **Full-text search index** (`Creating search indexes`) — FTS index built over symbol names and file paths for keyword queries.
11. **Embeddings** (optional, `--embeddings` flag) — semantic vector index generated and stored (details below).

### Heap Safety
The analyzer automatically re-executes itself with `--max-old-space-size=8192` (8 GB heap) if Node's heap is below that threshold. This prevents OOM kills on large repos.

---

## 3. Embedding Mode — Deep Dive

### What Gets Embedded
Only semantically meaningful code nodes receive vectors:
- `Function`, `Class`, `Method`, `Interface`, `File`

Each node is converted to a natural-language text representation by `text-generator.ts` (name + signature + code snippet, capped at 500 chars), then fed to the embedding model.

### The Model
| Property | Value |
|---|---|
| Model | `Snowflake/snowflake-arctic-embed-xs` |
| Source | HuggingFace Hub (downloaded on first use) |
| Runtime | `@huggingface/transformers` + `onnxruntime-node` |
| Vector dimensions | 384 |
| Batch size | 16 nodes per inference call |
| Compute | `auto` — tries GPU (CUDA/DirectML) first, falls back to CPU |
| Cost | **$0 — fully local, no API calls** |

The model is downloaded once and cached. The onnxruntime-node binary is loaded **lazily** (dynamic import) so non-embedding runs have zero overhead from it.

### Embedding Timing (grafana-operator)

| Phase | Time |
|---|---|
| KuzuDB load | 1.2s |
| FTS index | 1.2s |
| Embeddings | **42.1s** |
| **Total** | **44.7s** |

Without embeddings the same repo indexes in **2.5s** — a **17.9× slowdown**. The bottleneck is ONNX inference on CPU across ~1,966 nodes in batches of 16 (~123 inference calls).

> **Note:** On first run the model weights must be downloaded (~23MB for `arctic-embed-xs`). Subsequent runs skip this. The analyzer also caches existing embeddings across `--force` re-indexes to avoid re-embedding unchanged nodes.

### Auto-Skip Threshold
Embeddings are automatically skipped if the repo exceeds **50,000 nodes** (`EMBEDDING_NODE_LIMIT`) to prevent runaway runtimes on very large monorepos.

---

## 5. Graph-Only vs. Graph + Embeddings — Comparison

| Capability | Graph Only | Graph + Embeddings |
|---|---|---|
| **Keyword search** | Full-text index (exact/prefix) | Full-text index (exact/prefix) |
| **Semantic search** | No | Yes — finds conceptually similar code even with different naming |
| **Blast-radius analysis** | Yes (structural graph traversal) | Yes (same) |
| **Call-chain tracing** | Yes | Yes |
| **Community detection** | Yes | Yes |
| **"Find code that does X"** | Only if X appears in names/paths | Natural language → nearest neighbors |
| **Cross-language concept search** | Weak | Strong — model is language-agnostic |
| **Index time** | ~2.5–4s | ~44s (CPU) / ~7s (GPU) |
| **Storage overhead** | ~5–15 MB | ~8–25 MB (extra `CodeEmbedding` nodes in KuzuDB) |
| **First-run model download** | None | ~23 MB (one-time) |
| **Offline capable** | Yes | Yes (after first download) |
| **API dependency** | None | None |

### When Graph-Only is Sufficient
- Impact analysis and blast-radius queries (pure structural traversal).
- Call-chain tracing: "Who calls `AddNamespacedResource`?"
- Community/cluster inspection.
- CI-speed indexing (sub-5s re-indexes after every commit).
- Repos where symbol names are already descriptive and consistent.

### When Embeddings Add Real Value
- Conceptual search: *"find all places that handle rate limiting"* — even if the code doesn't use the word "rate limit".
- Cross-language or polyglot repos where naming conventions vary.
- AI agent assistants that accept natural language queries from users unfamiliar with the codebase.
- Onboarding: *"show me authentication-related functions"* in an unfamiliar repo.
- Detecting semantically duplicate logic scattered across files with different names.

---

## 6. Architecture Summary

```
gitnexus analyze
      │
      ├─ ingestion/pipeline.ts  ← AST parsing, call graph, imports
      │
      ├─ core/lbug/lbug-adapter.ts  ← KuzuDB (LadybugDB) graph store
      │       └─ .gitnexus/{repo-hash}/kuzu/  ← on-disk graph DB
      │
      ├─ core/fts  ← Full-text search index
      │
      └─ core/embeddings/  (--embeddings only)
              ├─ text-generator.ts  ← code → text representation
              ├─ embedder.ts        ← transformers.js singleton
              └─ embedding-pipeline.ts  ← batch ONNX inference
                      └─ CodeEmbedding nodes in KuzuDB
```

MCP server (`gitnexus mcp`) exposes the graph to AI agents via tools:
- `gitnexus_query` — flow-aware semantic/keyword search
- `gitnexus_context` — 360° symbol view (callers, callees, clusters)
- `gitnexus_impact` — upstream blast-radius analysis
- `gitnexus_rename` — graph-aware multi-file rename
- `gitnexus_detect_changes` — pre-commit scope verification
- `gitnexus_cypher` — raw Cypher queries against KuzuDB

---



*Generated by analyzing `comparison_repo/GitNexus` (340 files, 1,998 symbols, 5,457 edges) with GitNexus v1.4.1 on 2026-03-16.*
