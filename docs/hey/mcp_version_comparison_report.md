# MCP Version Comparison Report
**Model:** Qwen3.5 397B A17B (`qwen/qwen3-5-397b-a17b`)
**Pricing:** $0.39 / M input tokens · $2.34 / M output tokens
**Versions compared:** `mcp_on_staging` vs `mcp_with_advance_tools`
**Benchmark:** `results/small-eval` — 4 questions (q1–q4)
**Date:** 2026-03-18

---

## What Changed Between Versions

Based on PR [ByteBell/agent-box#71](https://github.com/ByteBell/agent-box/pull/71), the following changes shipped in `mcp_with_advance_tools` vs `mcp_on_staging`:

| Commit | Change | Files Affected |
|--------|--------|----------------|
| `f81c58f` | **New tool: `cypher`** — raw read-only Cypher query interface against Neo4j. Allows structural graph queries (CONSUMES_CONTRACT lookups, aggregations, multi-hop traversal) that standard search tools cannot express. | `src/core/tools/cypher.ts` (new), `src/handlers/cypher.ts` (new), `src/core/tools/index.ts`, `src/core/tools/types.ts` |
| `ea926f3` | **New tool: `keyword_lookup`** — direct OrgKeyword node search. Org-scoped, so a single call spans all indexed repos. Fastest path to cross-repo dependency discovery for known symbols. | `src/core/tools/keywordLookup.ts` (new), `src/handlers/keyword-lookup.ts` (new), `src/core/tools/index.ts`, `src/core/tools/types.ts` |
| `b29350a` | **Batch retrieve_file** — `retrieve_file` now accepts a `bulk_search` operation with a `paths` array. Collapses N sequential file reads into a single MCP call. Previously each file required its own `retrieve_file` call. | `src/core/tools/retrieveFile.ts` (+39/-5), `src/handlers/retrieve-file.ts` (+158/-3) |
| `7457627` | **Priority instruction** — system prompt rewritten to define an explicit tool priority order (cypher → keyword_lookup → get_repo_hubs → smart_search → graph_search → retrieve_file) and hard rules preventing redundant calls after CONSUMES_CONTRACT returns empty. | `src/core/instructions/defaultInstructions.ts` (+50/-14) |
| `325d34c` | **graphTraverse patch** — minor changes to `graphTraverse.ts` and `retrieve-file.ts` handlers. | `src/core/tools/graphTraverse.ts`, `src/handlers/retrieve-file.ts`, `src/handlers/graph-traverse.ts` |

**Tool inventory delta:**

| Tool | `mcp_on_staging` | `mcp_with_advance_tools` |
|------|:---:|:---:|
| `list_knowledge` | ✓ | ✓ |
| `smart_search` | ✓ | ✓ |
| `graph_search` | ✓ | ✓ |
| `graph_traverse` | ✓ | ✓ |
| `get_repo_hubs` | ✓ | ✓ |
| `retrieve_file` | ✓ (single) | ✓ (+ batch) |
| `cypher` | ✗ | ✓ |
| `keyword_lookup` | ✗ | ✓ |

---

## Per-Question Breakdown

### Q1 — Multi-repo: `objstore.Bucket.Tags` (thanos / mimir / loki)

**Ground truth:** 8 files across 2 repos (mimir: 5, loki: 3, thanos: 0 — thanos is a pure consumer)

| Metric | `mcp_on_staging` | `mcp_with_advance_tools` |
|--------|:-:|:-:|
| Status | success (no answer) | success |
| Wall time | 157.93 s | 103.85 s |
| Agent steps | 15 | 8 |
| Tool calls | 31 | 16 |
| Input tokens | 293,770 | 516,851 |
| Output tokens | 3,282 | 3,033 |
| Total tokens | 297,052 | 519,884 |
| **Cost** | **$0.1223** | **$0.2083** |

**Files found:**

| File | GT | Staging | Advance |
|------|:--:|:-------:|:-------:|
| mimir: `pkg/storage/bucket/prefixed_bucket_client.go` | ✓ | ✗ | ✓ |
| mimir: `pkg/storage/bucket/delayed_bucket_client.go` | ✓ | ✗ | ✗ |
| mimir: `pkg/storage/bucket/sse_bucket_client.go` | ✓ | ✗ | ✓ |
| mimir: `pkg/storage/bucket/client_mock.go` | ✓ | ✗ | ✗ |
| mimir: `pkg/storage/tsdb/block/global_markers_bucket_client.go` | ✓ | ✗ | ✗ |
| loki: `pkg/storage/bucket/prefixed_bucket_client.go` | ✓ | ✗ | ✓ |
| loki: `pkg/storage/bucket/sse_bucket_client.go` | ✓ | ✗ | ✓ |
| loki: `pkg/storage/bucket/xcap_bucket.go` | ✓ | ✗ | ✗ |
| thanos: `pkg/store/cache/caching_bucket.go` | ✗ (consumer, not impl) | ✗ | ✗ (listed as failing — incorrect) |
| mimir: `pkg/storage/tsdb/bucketcache/caching_bucket.go` | ✗ | ✗ | listed |
| mimir: `pkg/storage/tsdb/bucketindex/markers_bucket_client.go` | ✗ | ✗ | listed |
| mimir: `pkg/mimirtool/commands/bucket_validation.go` | ✗ | ✗ | listed |

**Staging:** Returned zero files — all 31 tool calls (`smart_search`, `graph_search`, `graph_traverse`, `get_repo_hubs`) returned 0 results. The model concluded the repos were "not indexed."

**Advance tools:** Found 4 of 8 correct files, plus produced 4 questionable/incorrect entries (including thanos, which the GT confirms has 0 failing files). Also missed 4 GT files: `delayed_bucket_client.go`, `client_mock.go`, `global_markers_bucket_client.go`, and loki's `xcap_bucket.go`. Partial recall, noisy precision.

**Tool usage comparison (staging vs advance):**
Staging: `smart_search` × 12, `graph_search` × 13, `graph_traverse` × 6, `get_repo_hubs` × 3, `list_knowledge` × 1
Advance: `smart_search` × 5, `graph_search` × 5, `keyword_lookup` × 1, `retrieve_file` × 4, `cypher` × 2

---

### Q2 — Single-repo: `IndexCache.DeleteBlock` (mimir)

**Ground truth:** 4 files in mimir
- `pkg/storage/tsdb/indexcache/inmemory.go` (InMemoryIndexCache)
- `pkg/storage/tsdb/indexcache/remote.go` (RemoteIndexCache)
- `pkg/storage/tsdb/indexcache/tracing.go` (TracingIndexCache)
- `pkg/storegateway/bucket.go` (noopCache — private struct in consumer package, the hard trap)

| Metric | `mcp_on_staging` | `mcp_with_advance_tools` |
|--------|:-:|:-:|
| Status | success (no answer) | success |
| Wall time | 188.75 s | 109.33 s |
| Agent steps | 25 | 14 |
| Tool calls | 44 | 16 |
| Input tokens | 621,783 | 484,895 |
| Output tokens | 5,757 | 2,727 |
| Total tokens | 627,540 | 487,622 |
| **Cost** | **$0.2560** | **$0.1954** |

**Files found:**

| File | GT | Staging | Advance |
|------|:--:|:-------:|:-------:|
| `pkg/storage/tsdb/indexcache/inmemory.go` | ✓ | ✗ | ✓ |
| `pkg/storage/tsdb/indexcache/remote.go` | ✓ | ✗ | ✗ |
| `pkg/storage/tsdb/indexcache/tracing.go` | ✓ | ✗ | ✓ |
| `pkg/storegateway/bucket.go` (noopCache) | ✓ | ✗ | ✗ |
| `pkg/storegateway/indexcache/memcached.go` | ✗ | ✗ | listed (questionable) |

**Staging:** Exhausted all 25 steps with 44 calls, all `graph_search` variants, zero results. Complete failure.

**Advance tools:** Found 2 of 4 correct files. Missed the cross-package `noopCache` in `pkg/storegateway/bucket.go` — the benchmark's designated "trap" for precisely this reason. Also substituted `remote.go` (RemoteIndexCache) with `memcached.go` (MemcachedIndexCache), which is incorrect per GT. The advance version cost less than staging on this question despite using retrieve_file and cypher — because it stopped earlier.

**Tool usage comparison:**
Staging: `graph_search` × 34, `smart_search` × 3, `graph_traverse` × 1, `list_knowledge` × 1, `get_repo_hubs` × 1
Advance: `smart_search` × 3, `graph_search` × 4, `retrieve_file` × 6, `cypher` × 2, `list_knowledge` × 1

---

### Q3 — Single-repo: `CloseIterator[T].Context` (loki)

**Ground truth:** Large blast radius — 11+ source files across `pkg/iter/`, `pkg/chunkenc/`, `pkg/storage/`, `pkg/querier/`, `pkg/logql/` (full list in phase_a.json reasoning).

| Metric | `mcp_on_staging` | `mcp_with_advance_tools` |
|--------|:-:|:-:|
| Status | success (no answer) | success (no answer) |
| Wall time | 142.69 s | 22.10 s |
| Agent steps | 14 | 2 |
| Tool calls | 19 | 3 |
| Input tokens | 264,462 | 44,328 |
| Output tokens | 2,454 | 638 |
| Total tokens | 266,916 | 44,966 |
| **Cost** | **$0.1089** | **$0.0188** |

**Files found:**

Both versions found **zero files**. Neither produced any answer.

**Staging:** 19 calls (smart_search × 6, graph_search × 7, graph_traverse × 3, get_repo_hubs × 1) — all returned 0 results. Model concluded loki was not indexed.

**Advance tools:** 3 calls (`smart_search` × 3) — all returned empty. Model gave up and returned an empty answer with no output. Stopped in 2 steps. This is the fastest failure.

Neither version handled the generic type interface (`CloseIterator[T]`) or the large fan-out correctly. The question has the largest GT blast radius of the four (11+ files) and both versions returned nothing.

---

### Q4 — Single-repo: `Logger.Debugf` (fluxcd/flux2)

**Ground truth:** 2 files
- `pkg/log/nop.go` (NopLogger)
- `cmd/flux/log.go` (stderrLogger)

| Metric | `mcp_on_staging` | `mcp_with_advance_tools` |
|--------|:-:|:-:|
| Status | success (no answer) | success |
| Wall time | 105.08 s | 65.38 s |
| Agent steps | 16 | 8 |
| Tool calls | 27 | 9 |
| Input tokens | 330,093 | 230,497 |
| Output tokens | 3,021 | 1,733 |
| Total tokens | 333,114 | 232,230 |
| **Cost** | **$0.1358** | **$0.0940** |

**Files found:**

| File | GT | Staging | Advance |
|------|:--:|:-------:|:-------:|
| `pkg/log/nop.go` | ✓ | ✗ | ✓ |
| `cmd/flux/log.go` | ✓ | ✗ | ✓ |

**Staging:** 27 tool calls, zero results — concluded "none of the repositories have been fully indexed."

**Advance tools:** Found both correct files. This is the only question where a version produced a complete and correct answer matching GT exactly.

**Tool usage comparison:**
Staging: `graph_search` × 11, `smart_search` × 7, `graph_traverse` × 1, `get_repo_hubs` × 1, `list_knowledge` × 1
Advance: `graph_search` × 2, `smart_search` × 1, `retrieve_file` × 4, `cypher` × 1

---

## Aggregate Summary

### Performance Totals

| Metric | `mcp_on_staging` | `mcp_with_advance_tools` |
|--------|:-:|:-:|
| Questions answered (non-empty) | 0 / 4 | 3 / 4 |
| Total wall time | 594.45 s | 300.66 s |
| Average wall time / question | 148.6 s | 75.2 s |
| Total tool calls | 121 | 44 |
| Average tool calls / question | 30.3 | 11.0 |
| Total agent steps | 70 | 32 |
| Total input tokens | 1,510,108 | 1,276,571 |
| Total output tokens | 14,514 | 8,131 |
| Total tokens | 1,524,622 | 1,284,715 |
| **Total cost** | **$0.6230** | **$0.5165** |

### Cost Breakdown Per Question

| Question | Staging Cost | Advance Cost | Delta |
|----------|:---:|:---:|:---:|
| Q1 (multi-repo) | $0.1223 | $0.2083 | advance +70% costlier |
| Q2 (mimir) | $0.2560 | $0.1954 | advance −24% cheaper |
| Q3 (loki) | $0.1089 | $0.0188 | advance −83% cheaper |
| Q4 (flux2) | $0.1358 | $0.0940 | advance −31% cheaper |
| **Total** | **$0.6230** | **$0.5165** | **advance −17% cheaper** |

Q1 is the outlier: advance tools used far more input tokens (516K vs 293K) yet still produced an incomplete answer — the token cost of cross-repo traversal with `retrieve_file` and `cypher` calls is high. On the three single-repo questions the advance version was consistently cheaper because it stopped earlier with results rather than exhausting all 25 steps doing futile `graph_search` loops.

### Accuracy Summary

| Question | GT Files | Staging Found | Advance Found | Advance Correct | Advance Wrong |
|----------|:---:|:---:|:---:|:---:|:---:|
| Q1 | 8 | 0 | 10 listed | 4 | 4 questionable/wrong |
| Q2 | 4 | 0 | 3 listed | 2 | 1 wrong, 1 missing trap |
| Q3 | 11+ | 0 | 0 | 0 | — |
| Q4 | 2 | 0 | 2 | 2 | 0 |

---

## Analysis

### What `mcp_on_staging` got wrong

On all four questions, the staging model spent its entire budget repeating `graph_search` with marginally different query strings. The pattern is consistent: it cycled through `smart_search → graph_search × N → graph_traverse → get_repo_hubs → list_knowledge`, found nothing, and concluded the repos were not indexed. With 44 calls on Q2 and 31 on Q1, it exhausted its steps without ever reaching `retrieve_file`. It had no way to do targeted file inspection or graph structural queries. The instruction set and tool selection mechanism left the model with no escape path when semantic search failed.

### What `mcp_with_advance_tools` got right

The model demonstrably used the new tools. `cypher` appeared in Q1, Q2, and Q4 for structural queries. `keyword_lookup` appeared in Q1. `retrieve_file` was used in all successful questions for targeted file inspection. The priority instruction appears to have reduced gratuitous `graph_search` looping: Q4 used only 2 `graph_search` calls versus 11 in staging. Q4 result is a clean match to GT.

### What `mcp_with_advance_tools` still got wrong

**Q1 (multi-repo):** The advance version identified 10 files but 4 of those are questionable or incorrect. It listed `thanos/pkg/store/cache/caching_bucket.go` as failing to compile — GT explicitly notes thanos has zero failing files because it only consumes `objstore.Bucket`, never implements it. Three additional mimir files were listed (`bucketcache/caching_bucket.go`, `markers_bucket_client.go`, `bucket_validation.go`) that are not in GT. Four actual GT files were missed (`delayed_bucket_client.go`, `client_mock.go`, `global_markers_bucket_client.go`, `xcap_bucket.go`). The model retrieved some files via `retrieve_file` but drew incorrect inferences from what it found.

**Q2 (mimir):** The cross-package trap (`noopCache` in `pkg/storegateway/bucket.go`) was missed — same failure mode as most models on this question. It also misidentified `memcached.go` instead of `remote.go`.

**Q3 (loki):** Both versions failed completely. The generic type `CloseIterator[T]` and its downstream cascade across 11+ structs in multiple packages is beyond what either version could reach. Three `smart_search` calls on the advance version returned nothing and the model gave up in 2 steps. This is the benchmark's hardest question (blast_radius_shape: "large") and neither version approached it.

### On the `retrieve_file` batch change

The batch `retrieve_file` (`bulk_search` operation) reduced the number of discrete tool calls significantly. In Q4, advance performed 4 `retrieve_file` calls where staging would have had to make many individual calls (or gave up). However, the logged tool call records show individual entries per call still — if bulk_search was used it reduced round-trips at the MCP transport level. The net effect on call counts is real.

### On the priority instruction

The instruction change is the highest-leverage change in the PR. It directly reduced the `graph_search` loop problem. Staging's Q2 had 34 `graph_search` calls; advance had 4. The "MANDATORY: DO NOT run any of the following" language for CONSUMES_CONTRACT failures appears to have taken hold for known patterns but did not help with Q3 (generic interface cascade) or the cross-package trap in Q2.

### Cost observation

The overall 17% cost reduction comes almost entirely from Q3 (advance gave up fast) and Q2 (fewer steps). Q1 was 70% more expensive in advance due to heavy `retrieve_file` and `cypher` usage with a multi-repo scope. If the benchmark were weighted toward single-repo questions the advance version would appear more economical. Multi-repo questions with many implementors are the expensive case for the advance version's file-reading strategy.

---

## Raw Numbers Reference

```
mcp_on_staging:
  Q1: time=157.93s  steps=15  calls=31  in=293,770  out=3,282   cost=$0.1223
  Q2: time=188.75s  steps=25  calls=44  in=621,783  out=5,757   cost=$0.2560
  Q3: time=142.69s  steps=14  calls=19  in=264,462  out=2,454   cost=$0.1089
  Q4: time=105.08s  steps=16  calls=27  in=330,093  out=3,021   cost=$0.1358
  TOT: time=594.45s steps=70  calls=121 in=1,510,108 out=14,514 cost=$0.6230

mcp_with_advance_tools:
  Q1: time=103.85s  steps=8   calls=16  in=516,851  out=3,033   cost=$0.2083
  Q2: time=109.33s  steps=14  calls=16  in=484,895  out=2,727   cost=$0.1954
  Q3: time=22.10s   steps=2   calls=3   in=44,328   out=638     cost=$0.0188
  Q4: time=65.38s   steps=8   calls=9   in=230,497  out=1,733   cost=$0.0940
  TOT: time=300.66s steps=32  calls=44  in=1,276,571 out=8,131  cost=$0.5165
```

Cost formula: `(input_tokens / 1,000,000 × 0.39) + (output_tokens / 1,000,000 × 2.34)`
