# Qwen 3.6 Plus Preview — Raw vs MCP Comparison Report

**Model:** `qwen/qwen3.6-plus-preview:free` via OpenRouter
**Dataset:** `princeton-nlp/SWE-bench_Verified` — `astropy/astropy`
**Date:** 2026-04-02
**Judge:** Claude Code (claude-sonnet-4-6)

| | Raw | MCP |
|---|---|---|
| Tasks evaluated | 16 of 22 | 14 of 22 |
| Mode | Direct repo access, no knowledge graph | ByteBell MCP knowledge graph, no direct repo access |
| Source | `auto_run_on_qwen3.6_plus_preview/` | `mcp_run_on_qwen3.6_plus_preview_with_mcp/` |

---

## Top-Line Summary

| Metric | Raw | MCP | Delta |
|--------|-----|-----|-------|
| Tasks evaluated | 16 | 14 | — |
| Overall score | 115/128 | 97/112 | — |
| Overall % | **89.8%** | **86.6%** | Raw +3.2 pp |
| Avg score per task | 7.2/8 | 6.9/8 | Raw +0.3 |
| Root cause % | 100% | 100% | Tie |
| File identification % | 100% | 100% | Tie |
| Patch quality % | **72.9%** | **64.3%** | Raw +8.6 pp |
| Exact (8/8) | 7 | 5 | Raw +2 |
| Near-perfect (7/8) | 5 | 4 | Raw +1 |
| Partial (6/8) | 4 | 4 | Tie |
| Partial (5/8) | 0 | 1 | MCP worse |
| Fail (≤4/8) | 0 | 0 | Tie |
| Exact + Near-perfect | **12/16 (75.0%)** | **9/14 (64.3%)** | Raw +10.7 pp |
| Total time | 13,361 s | 11,523 s | — |
| Avg time / task | 835 s | 823 s | Tie (~1%) |
| Total cost | $63.12 | $52.20 | — |
| Avg cost / task | **$3.95** | **$3.73** | MCP -5.6% |

> **Verdict: Raw wins clearly on quality (+3.2 pp overall, +8.6 pp patch), at comparable speed and marginally higher cost (+5.6%). MCP adds unique task coverage (14369, 8707, 13453) but produces measurably worse patches on tasks both runs share.**

---

## Task Coverage

### Tasks unique to Raw (5) — MCP had no answer.json

| Instance ID | Difficulty | Raw Score | Raw Grade |
|-------------|------------|-----------|-----------|
| `12907` | 15m–1h | 6/8 | ⚠️ Partial |
| `13236` | 15m–1h | 8/8 | ✅ Exact |
| `14096` | 15m–1h | 6/8 | ⚠️ Partial |
| `14598` | 15m–1h | 7/8 | ✅ Near-perfect |
| `7671` | 15m–1h | 7/8 | ✅ Near-perfect |

### Tasks unique to MCP (3) — Raw had no answer.json

| Instance ID | Difficulty | MCP Score | MCP Grade |
|-------------|------------|-----------|-----------|
| `13453` | 15m–1h | 7/8 | ✅ Near-perfect |
| `14369` | 1–4h | 8/8 | ✅ Exact |
| `8707` | 15m–1h | 8/8 | ✅ Exact |

> **MCP unlocked 2 of the 3 hardest skipped tasks** — `14369` (1–4h CDS grammar) and `8707` (multi-file bytes handling) — both solved at 8/8. Raw in turn covered 5 tasks MCP did not, scoring a combined 34/40 on them. Unique coverage is the MCP's most concrete advantage.

---

## Head-to-Head: 11 Shared Tasks

Both runs evaluated these tasks. Direct score comparison on identical problems.

| Instance ID | Difficulty | Raw Score | Raw Grade | MCP Score | MCP Grade | Winner |
|-------------|------------|-----------|-----------|-----------|-----------|--------|
| `13033` | 15m–1h | **8/8** | ✅ Exact | 6/8 | ⚠️ Partial | **Raw +2** |
| `13579` | 1–4h | **7/8** | ✅ Near-perfect | 6/8 | ⚠️ Partial | **Raw +1** |
| `13977` | 15m–1h | 6/8 | ⚠️ Partial | 6/8 | ⚠️ Partial | Tie |
| `14182` | 15m–1h | **8/8** | ✅ Exact | 6/8 | ⚠️ Partial | **Raw +2** |
| `14309` | <15m | 7/8 | ✅ Near-perfect | 7/8 | ✅ Near-perfect | Tie |
| `14365` | 15m–1h | 7/8 | ✅ Near-perfect | 7/8 | ✅ Near-perfect | Tie |
| `14508` | 15m–1h | **8/8** | ✅ Exact | 7/8 | ✅ Near-perfect | **Raw +1** |
| `14539` | 15m–1h | 8/8 | ✅ Exact | 8/8 | ✅ Exact | Tie |
| `14995` | <15m | 8/8 | ✅ Exact | 8/8 | ✅ Exact | Tie |
| `7606` | 15m–1h | **6/8** | ⚠️ Partial | 5/8 | ⚠️ Partial | **Raw +1** |
| `8872` | 15m–1h | 8/8 | ✅ Exact | 8/8 | ✅ Exact | Tie |
| **TOTAL** | | **81/88** | **92.0%** | **74/88** | **84.1%** | **Raw +7.9 pp** |

**Raw wins: 5 tasks · MCP wins: 0 tasks · Ties: 6 tasks**

On the 11 tasks both runs completed, Raw is unambiguously better — it never scores lower than MCP on any individual task, and is strictly higher on five.

---

## Per-Task Deltas (shared tasks)

### `13033` — Raw 8/8, MCP 6/8 — Raw +2

**Issue:** `TimeSeries` misleading exception on required column removal

| | Raw | MCP |
|---|---|---|
| Fix | Uses existing `as_scalar_or_list_str(required_columns)` helper | Uses `repr(required_columns)` — wrong format, proposes test rewrites |

Raw correctly calls the helper already present in the file, matching GT exactly. MCP chose a different formatting approach producing `['time']` instead of GT's `'time'` for single-column cases, and diverges from the existing non-empty branch format.

---

### `13579` — Raw 7/8, MCP 6/8 — Raw +1

**Issue:** `SlicedLowLevelWCS` hardcoded `1.0` for dropped world dimensions

| | Raw | MCP |
|---|---|---|
| Fix | Single eager call to `_pixel_to_world_values_all(*[0]*n)` at method entry | Two-pass iterative refinement with a second `self._wcs.pixel_to_world_values` call |

Raw correctly computes the dropped world values at pixel=0 once and uses them. MCP adds a mathematically unnecessary "refinement" pass that uses the full WCS (not the slice-aware helper), introducing incorrect logic. More output (63,580 tokens vs 4,829 for raw) indicates MCP spent far more time going in circles.

---

### `13977` — Raw 6/8, MCP 6/8 — Tie

**Issue:** `Quantity.__array_ufunc__` should return `NotImplemented` for duck types

Both runs wrap only the input-conversion loop instead of the full method body. Identical partial fix — a consistent Qwen limitation regardless of mode.

---

### `14182` — Raw 8/8, MCP 6/8 — Raw +2

**Issue:** RST writer needs `header_rows` support

| | Raw | MCP |
|---|---|---|
| Fix | All 3 changes: `__init__`, dynamic `write()`, dynamic `read()` | Only `__init__` — write() and read() remain hardcoded |

Raw delivers the complete 3-change fix identical to GT. MCP stops at `__init__`, removes the `TypeError` on construction but leaves `write()` and `read()` broken for multi-row headers.

---

### `14508` — Raw 8/8, MCP 7/8 — Raw +1

**Issue:** `_format_float` uses `.16G` expanding short floats

| | Raw | MCP |
|---|---|---|
| Fix | `str(value).replace("e", "E")` + truncation guard | `str(value)` only — missing `.replace("e", "E")` |

Raw adds both the `str(value)` replacement and the required uppercase-E normalization for FITS spec compliance. MCP forgets the case conversion — exponents like `1.5e+10` would produce invalid FITS headers.

---

### `7606` — Raw 6/8, MCP 5/8 — Raw +1

**Issue:** `Unit.__eq__` returns `False` instead of `NotImplemented`

| | Raw | MCP |
|---|---|---|
| Fix | `return NotImplemented` in `UnrecognizedUnit.__eq__` (missing `UnitBase`) | `return False` in `UnrecognizedUnit.__eq__` (missing `UnitBase`, wrong return value) |

Both miss `UnitBase.__eq__`. Raw at least returns the semantically correct `NotImplemented`. MCP returns `False`, which breaks Python's reflected-operator protocol entirely — a regression vs raw.

---

## Cost and Time: Shared Tasks Only

| Instance ID | Raw Time | MCP Time | Raw Cost | MCP Cost |
|-------------|----------|----------|----------|----------|
| `13033` | 703 s | 329 s | $1.995 | $2.736 |
| `13579` | 522 s | 1,986 s | $1.409 | $3.621 |
| `13977` | 832 s | 1,164 s | $6.472 | $10.835 |
| `14182` | 537 s | 340 s | $2.133 | $3.902 |
| `14309` | 275 s | 241 s | $1.792 | $1.697 |
| `14365` | 690 s | 1,280 s | $6.502 | $3.441 |
| `14508` | 512 s | 148 s | $3.889 | $0.895 |
| `14539` | 232 s | 158 s | $1.686 | $1.691 |
| `14995` | 212 s | 293 s | $1.589 | $3.248 |
| `7606` | 418 s | 176 s | $2.403 | $1.813 |
| `8872` | 206 s | 119 s | $1.711 | $1.083 |
| **TOTAL** | **5,139 s** | **6,234 s** | **$31.58** | **$34.96** |
| **AVG** | **467 s** | **566 s** | **$2.87** | **$3.18** |

> On shared tasks, MCP is **21% slower** (566 s vs 467 s avg) and **11% more expensive** ($3.18 vs $2.87 avg) — despite being the mode that performs *worse*. The MCP graph adds navigation overhead without consistently reducing exploration time or cost.

**Per-task efficiency inversions (MCP faster AND cheaper):**

| Task | MCP faster by | MCP cheaper by | MCP quality |
|------|--------------|----------------|-------------|
| `14508` | −72% (148 vs 512 s) | −77% ($0.895 vs $3.889) | 7/8 vs 8/8 |
| `8872` | −42% (119 vs 206 s) | −37% ($1.083 vs $1.711) | 8/8 = 8/8 |
| `7606` | −58% (176 vs 418 s) | −25% ($1.813 vs $2.403) | 5/8 vs 6/8 |
| `14309` | −12% (241 vs 275 s) | −5% ($1.697 vs $1.792) | 7/8 = 7/8 |

`14508` is the clearest MCP efficiency win: the knowledge graph immediately surfaced `card.py`, enabling an 8-request answer. But quality slipped slightly (missing `.replace("e", "E")`). `8872` is the only case where MCP is both faster, cheaper, and equally correct.

---

## Grade Distribution Comparison

| Grade | Raw (16 tasks) | MCP (14 tasks) | Raw on shared (11) | MCP on shared (11) |
|-------|----------------|----------------|-------------------|-------------------|
| ✅ Exact (8/8) | 7 (43.8%) | 5 (35.7%) | 6 (54.5%) | 3 (27.3%) |
| ✅ Near-perfect (7/8) | 5 (31.2%) | 4 (28.6%) | 3 (27.3%) | 3 (27.3%) |
| ⚠️ Partial (6/8) | 4 (25.0%) | 4 (28.6%) | 2 (18.2%) | 4 (36.4%) |
| ⚠️ Partial (5/8) | 0 | 1 (7.1%) | 0 | 1 (9.1%) |
| ❌ Fail (≤4/8) | 0 | 0 | 0 | 0 |

On the shared 11 tasks, Raw produces Exact results 54.5% of the time; MCP only 27.3%. MCP converts more Exact results to Partial — a clear downgrade in implementation quality.

---

## Key Findings

### 1. MCP hurts patch quality on shared tasks (−7.9 pp)
The MCP knowledge graph reliably points Qwen to the right file but does not improve — and sometimes actively harms — the implementation quality. Three of the five Raw wins are tasks where MCP produced an *incomplete* fix (13033: wrong helper, 14182: missing 2 of 3 changes, 13579: over-engineered two-pass loop). The MCP graph surfaces *where* to look, but Qwen still fails to read the surrounding context carefully enough to produce a complete fix.

### 2. MCP unlocks coverage on genuinely hard tasks
The two tasks where MCP adds unique value are also among the hardest: `14369` (1–4h, PLY grammar + regenerated parse table) scored 8/8 Exact, and `8707` (multi-file bytes decoding) scored 8/8 Exact. Raw missed both entirely (no answer.json). For tasks where locating the right files is the primary challenge, MCP clearly delivers.

### 3. `13977` is Qwen's universal blind spot
Both modes score 6/8 on task `13977` (`__array_ufunc__` NotImplemented). The failure is identical: both wrap only the input-conversion loop instead of the full method body. MCP spent $10.84 and 49 requests on this task, vs $6.47 and 35 requests for raw — more exploration, same wrong answer. This is a model-level limitation: Qwen stops at the most immediately visible failure point without reading the GT's broader scope requirement.

### 4. `7606` is Qwen's consistent weak point — MCP makes it worse
Both modes miss `UnitBase.__eq__`. Raw at least returns `NotImplemented` (correct). MCP returns `False` (wrong). MCP's extra context on `UnrecognizedUnit` may have reinforced focus on the subclass and away from the base class.

### 5. Cost advantage of MCP is illusory on shared tasks
MCP is 5.6% cheaper overall ($3.73 vs $3.95/task) because it has fewer total tasks and the unique MCP tasks happen to be cheaper on average. On the 11 shared tasks, MCP is **11% more expensive** at lower quality. The navigation efficiency of the knowledge graph is offset by the model taking more conversational turns to converge.

### 6. Speed is essentially identical (−1% overall, +21% on shared)
Neither mode has a meaningful wall-clock advantage. The MCP overhead (graph lookups, format conversion) does not save proportional exploration time.

---

## Why This Is the Opposite of the Claude Results

The Claude comparison reports (`comparison_v2.md`, `claude_sonnet_4.6.md`) show MCP winning or tying on quality **and** winning significantly on cost and speed. This report shows Raw winning on quality at comparable cost. That is not a contradiction — it is explained by three structural differences.

### 1. Prompt caching: the entire cost story for Claude, absent for Qwen

Claude (Sonnet and Opus) supports **prompt caching**. When the MCP knowledge graph delivers pre-indexed file summaries and keyword lookups, that context gets cached — subsequent API calls within the same session reuse it at ~0.1× the input token cost. This is why MCP cuts Claude's cost by 29–44%:

| Model | Raw cost/task | MCP cost/task | MCP saving |
|-------|--------------|--------------|------------|
| Claude Opus 4.6 | $0.73 | $0.52 | **−29%** |
| Claude Sonnet 4.6 | $0.54 | $0.30 | **−44%** |
| **Qwen 3.6 Plus Preview** | **$3.95** | **$3.73** | **−5% (noise)** |

Qwen has **no prompt caching**. Every token in every request is billed at full input price. MCP graph lookups add extra API round-trips without any caching offset — so the cost advantage that Claude gets from MCP simply does not exist for Qwen.

### 2. Raw-mode architecture: Sonnet+Haiku vs Qwen-only

Claude's raw mode uses a **Sonnet+Haiku multi-agent** setup. Haiku handles cheap file search and directory listing at $0.10/MTok cache-read (5× cheaper than Opus). The expensive Sonnet/Opus model is used only for reasoning and patch generation. This is why Claude raw is surprisingly affordable despite reading large codebases.

Qwen raw mode is a single model doing all exploration directly. There is no cheap sub-agent for file traversal. The cost is uniformly high per token.

### 3. Model capability and MCP sensitivity

Claude is better at using MCP context precisely: it extracts the relevant piece and stops. Qwen with MCP shows a pattern of over-engineering (two-pass refinement for `13579`, iterative loops where one line suffices) and incomplete implementation (only `__init__` for `14182`, missing `write()`/`read()`). The MCP graph surfaces the right file but Qwen then produces a noisier patch than it would with direct access.

In the Claude reports, MCP *improves or maintains* patch quality because the model is capable enough to use the compressed graph context as a reliable signal. For Qwen, the compressed representation sometimes misdirects rather than guides.

### Summary

| Factor | Claude MCP effect | Qwen MCP effect |
|--------|------------------|-----------------|
| Prompt caching | **Large cost/speed saving** | No effect (no caching) |
| Context compression | Helps on hard multi-file tasks | Sometimes misdirects |
| Patch quality | Maintained or improved | Degraded on shared tasks |
| Unique task coverage | Comparable both modes | MCP unlocks 3 hard tasks Raw missed |

**The MCP knowledge graph is a multiplier on model capability and infrastructure support. For Claude with caching, it is unambiguously efficient. For Qwen without caching, it provides targeted file discovery but does not compensate for the cost overhead or patch quality regression on tasks both modes cover.**

---

## When to Use Each Mode

| Situation | Recommendation |
|-----------|---------------|
| Bug is in a well-known astropy subsystem (FITS, units, coordinates) | **Raw** — Qwen navigates effectively without MCP, produces better patches |
| Bug requires understanding deeply nested call chains (`__array_ufunc__`, `_separable`) | Neither mode handles these well; both need a stronger reasoning model |
| Bug involves a parser/grammar file with a generated artifact (`cds_parsetab.py`) | **MCP** — knowledge graph correctly identifies the grammar file pair |
| Bug is a multi-file change in a less-indexed area (`Header.fromstring` + `Card.fromstring`) | **MCP** — correctly identified both files at first attempt |
| Task coverage matters more than per-task quality | **Run both** — their unique task sets are complementary (5 raw-only, 3 MCP-only) |
