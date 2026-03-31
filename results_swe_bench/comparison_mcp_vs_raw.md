# Claude Opus 4.6 — MCP vs Raw Comparison Report

**Dataset:** `princeton-nlp/SWE-bench_Verified` — `astropy/astropy`
**Date:** 2026-03-31

---

## High-Level Summary

`14995` (MCP) and `14595` (Raw) are the **same question** (identical bug in `ndarithmetic.py`). This gives **21 common tasks**; only `14598` is Raw-exclusive.

| Metric | MCP (21 tasks) | Raw (21 common) | Raw (all 22) | Winner (common) |
|--------|---------------|-----------------|-------------|-----------------|
| Score | 199/210 (94.8%) | 201/210 (95.7%) | 211/220 (95.9%) | Raw (+2 pts) |
| Root Cause | 63/63 (100%) | 63/63 (100%) | 66/66 (100%) | Tie |
| Correct Files | 42/42 (100%) | 42/42 (100%) | 44/44 (100%) | Tie |
| Correct Patch | 53/63 (84.1%) | 55/63 (87.3%) | 57/66 (86.4%) | Raw |
| Test Awareness | 41/42 (97.6%) | 42/42 (100%) | 44/44 (100%) | Raw |

---

## Token, Time, Cost & Accuracy Table

### Per-Task Comparison (21 common tasks)

> `14995` (MCP) and `14595` (Raw) are the same question — shown on row 21.
>
> **Pricing:** $5/M input, $25/M thinking, $25/M output.
>
> **Thinking token methodology:** JSON `thinking_tokens` fields are unreliable (57–68% fabricated as `elapsed × 150`). Adjusted formula:
> - **MCP:** `(elapsed - 3s × tool_calls) × 150 t/s` — subtracts ~3s per MCP tool call for knowledge graph network/retrieval latency
> - **Raw:** `elapsed × 150 t/s` — Raw tools are local `grep`/`fgrep` with negligible latency, so elapsed ≈ thinking time

| # | Instance ID | MCP Score | Raw Score | MCP Time (s) | Raw Time (s) | MCP Tool Calls | Raw Tool Calls | MCP Cost | Raw Cost | Winner |
|---|-------------|-----------|-----------|---------------|---------------|----------------|----------------|----------|----------|--------|
| 1 | `12907` | **10/10** | **10/10** | 74 | 71 | 8 | 7 | $0.378 | $0.310 | Tie |
| 2 | `13033` | **7/10** | **10/10** | 169 | 77 | 5 | 17 | $0.674 | $0.331 | **Raw** |
| 3 | `13236` | **10/10** | **10/10** | 241 | 184 | 15 | 26 | $0.972 | $0.754 | Tie |
| 4 | `13398` | **9/10** | **9/10** | 157 | 151 | 21 | 29 | $0.723 | $0.692 | Tie |
| 5 | `13453` | **9/10** | **10/10** | 62 | 55 | 7 | 17 | $0.219 | $0.258 | **Raw** |
| 6 | `13579` | **10/10** | **10/10** | 167 | 91 | 7 | 17 | $0.675 | $0.397 | Tie (Raw cheaper) |
| 7 | `13977` | **9/10** | **9/10** | 73 | 91 | 10 | 25 | $0.338 | $0.405 | Tie (MCP cheaper) |
| 8 | `14096` | **9/10** | **10/10** | 100 | 62 | 6 | 12 | $0.403 | $0.276 | **Raw** |
| 9 | `14182` | **10/10** | **10/10** | 193 | 85 | 9 | 15 | $0.858 | $0.373 | Tie (Raw cheaper) |
| 10 | `14309` | **9/10** | **10/10** | 19 | 69 | 7 | 17 | $0.050 | $0.293 | **Raw** |
| 11 | `14365` | **9/10** | **10/10** | 131 | 63 | 9 | 7 | $0.581 | $0.292 | **Raw** |
| 12 | `14369` | **10/10** | **10/10** | 415 | 159 | 11 | 14 | $1.669 | $0.663 | Tie (Raw cheaper) |
| 13 | `14508` | **10/10** | **10/10** | 102 | 81 | 9 | 22 | $0.377 | $0.349 | Tie |
| 14 | `14539` | **10/10** | **10/10** | 50 | 44 | 10 | 17 | $0.205 | $0.204 | Tie |
| 15 | `7166` | **10/10** | **10/10** | 196 | 49 | 24 | 13 | $0.763 | $0.227 | Tie (Raw cheaper) |
| 16 | `7336` | **10/10** | **10/10** | 23 | 84 | 5 | 9 | $0.094 | $0.366 | Tie (MCP cheaper) |
| 17 | `7606` | **9/10** | **9/10** | 62 | 72 | 6 | 21 | $0.246 | $0.307 | Tie (MCP cheaper) |
| 18 | `7671` | **10/10** | **9/10** | 177 | 45 | 7 | 19 | $0.718 | $0.209 | **MCP** |
| 19 | `8707` | **9/10** | **10/10** | 67 | 122 | 11 | 26 | $0.325 | $0.522 | **Raw** |
| 20 | `8872` | **10/10** | **8/10** | 58 | 48 | 5 | 13 | $0.254 | $0.216 | **MCP** |
| 21 | `14995` | **10/10** | **9/10** | 34 | 48 | 8 | 20 | $0.145 | $0.220 | **MCP** |
| | **COMMON (21)** | **199/210** | **201/210** | **2,570 s** | **1,751 s** | **200** | **353** | **$10.67** | **$7.66** | **Raw +2 pts** |

### Raw-Only Task (not covered by MCP)

| Instance ID | Score | Time (s) | Tool Calls | Cost |
|-------------|-------|----------|------------|------|
| `14598` | 10/10 | 164 | 16 | $0.679 |

---

## Aggregate Statistics (21 Common Tasks)

> Raw times from `claude_opus_4.6_raw_v2/` JSON files (a separate, faster run than the original raw eval report).

| Metric | MCP (21) | Raw v2 (21 common) | Ratio | Winner |
|--------|----------|---------------------|-------|--------|
| Accuracy | 199/210 (94.8%) | 201/210 (95.7%) | 0.99× | Raw |
| Total time | 2,570 s (42.8 min) | **1,751 s (29.2 min)** | 1.47× | **Raw** |
| Avg time/task | 122.4 s | **83.4 s** | 1.47× | **Raw** |
| Total tool calls | **200** | 353 | 0.57× | **MCP** |
| Avg tool calls/task | **9.5** | 16.8 | **0.57×** | **MCP** |
| Fastest task | 19 s (`14309`) | 44 s (`14539`) | — | MCP |
| Slowest task | 415 s (`14369`) | 184 s (`13236`) | — | Raw |

### Data Integrity Warning: Fabricated Thinking Tokens

Cross-checking `thinking_tokens` against `elapsed_seconds × 150` reveals systematic fabrication:

| Dataset | Total Tasks | EXACT match (`thinking = elapsed × 150`) | Fabrication Rate |
|---------|-------------|------------------------------------------|------------------|
| MCP | 21 | **12** | 57% |
| Raw v2 | 22 | **15** | 68% |

The `thinking_tokens` field was **computed from elapsed time** (`elapsed_seconds × 150`), not measured from actual API usage.

**Critical asymmetry:** Raw's tools are near-instant (`grep`, `fgrep` on local files — negligible latency), so `elapsed ≈ thinking time` is a **reasonable approximation** for Raw. MCP's tools go through a knowledge graph server with network + retrieval latency per call, so `elapsed × 150` **overcounts MCP thinking** by including tool call overhead.

This means MCP's reported thinking tokens ($7.65) are inflated — the real thinking cost is lower. Raw's reported thinking tokens ($4.66) are closer to reality. The true cost gap between MCP and Raw is likely **smaller** than the as-reported figures suggest, but MCP is still more expensive due to its 7× input token overhead.

### Token Breakdown (21 common tasks)

| Token Type | MCP | Raw | Reliability |
|------------|-----|-----|-------------|
| Input (tool reads, prompts) | 438,540 | 62,041 | **Estimated** (round numbers in JSONs) |
| Thinking (from JSON) | 306,000 | 186,450 | **Unreliable** (fabricated) |
| Output | 43,100 | 31,500 | **Verified** |
| Elapsed time | 2,570 s | 1,751 s | **Verified** |

> MCP averages **2,193 tokens/tool call** vs Raw's **217 tokens/call** (10× per call). MCP knowledge graph returns richer responses, but all per-call counts in both JSONs are rounded estimates (e.g., 4000, 6000), not exact API measurements. The 7× aggregate gap is directionally correct but imprecise.

### Cost Comparison (3-Tier: $5/M input, $25/M thinking, $25/M output)

> **Adjusted thinking:** MCP `(elapsed − 3s × tool_calls) × 150 t/s`, Raw `elapsed × 150 t/s`

| Token Type | MCP Tokens | MCP Cost | Raw Tokens (21) | Raw Cost (21) |
|------------|-----------|----------|-----------------|---------------|
| Input ($5/M) | 438,540 | $2.193 | 62,041 | $0.310 |
| Thinking ($25/M) | 295,800 | $7.395 | 262,650 | $6.566 |
| Output ($25/M) | 43,100 | $1.078 | 31,500 | $0.788 |
| **Total** | **777,440** | **$10.67** | **356,191** | **$7.66** |

| Metric | MCP (21) | Raw (21 common) | Raw (all 22) |
|--------|----------|-----------------|--------------|
| Total cost | **$10.67** | **$7.66** | **$8.34** |
| Avg cost/task | **$0.508** | **$0.365** | **$0.379** |
| Cost per correct point | $0.054/pt | $0.038/pt | $0.040/pt |

> **Raw is 28% cheaper** on 21 common tasks ($7.66 vs $10.67). The gap comes from MCP's 7× input token overhead (438K vs 62K, +$1.88) and 13% more adjusted thinking tokens (296K vs 263K, +$0.83).

---

## Score Differential Analysis (21 Common Tasks)

### Where Raw Beat MCP (6 tasks, −8 points)

| Instance | MCP | Raw | MCP Issue |
|----------|-----|-----|-----------|
| `13033` | 7 | 10 | Missing `as_scalar_or_list_str` helper; single-column format produces `['time']` not `'time'` — **worst MCP failure** |
| `13453` | 9 | 10 | Manual loop instead of calling `_set_col_formats()` — MCP duplicated logic |
| `14096` | 9 | 10 | MRO loop instead of GT's elegant `self.__getattribute__(attr)` one-liner |
| `14309` | 9 | 10 | Guarded `args[0]` (symptom) vs Raw completed `elif` branch (root fix) |
| `14365` | 9 | 10 | Missing `v.upper() == "NO"` for lowercase data values — incomplete fix |
| `8707` | 9 | 10 | Only `Card.fromstring` patched; `Header.fromstring` described but not concretized |

### Where MCP Beat Raw (3 tasks, +4 points)

| Instance | MCP | Raw | Raw Issue |
|----------|-----|-----|-----------|
| `14995`/`14595` | 10 | 9 | Raw used `operand is None or operand.mask is None` (broader than GT's minimal `operand.mask is None`) |
| `7671` | 10 | 9 | Raw applied regex to only `version`, not `have_version` — partial fix |
| `8872` | 10 | 8 | Raw used `kind in 'iu'` instead of `np.issubdtype(np.inexact)` — wrong semantic approach |

### Net on 21 Common Tasks: Raw +2 (201 vs 199)

---

## What Worked Well with MCP

### 1. Fewer Tool Calls
- **43% fewer tool calls** (9.5 vs 16.8 average) — the knowledge graph returns more context per call
- However, MCP is **47% slower overall** (2,570s vs 1,751s) because each MCP tool call has ~3s of network/retrieval latency vs Raw's near-instant grep

### 2. Root Cause Analysis is Flawless
- 21/21 tasks (100%) — identical to raw. The MCP's pre-indexed summaries and keyword lookups help the model zero in on the bug mechanism quickly

### 3. Strong on Complex Multi-File Tasks
- Task `13398` (1–4 hour difficulty, 6-file change): MCP scored 9/10 with 157s, vs Raw's 9/10 with 151s — same accuracy, comparable time

### 4. Improved on Three Tasks Raw Got Wrong
- `14995`/`14595` (NDData mask): MCP produced exact match `operand.mask is None`. Raw used broader `operand is None or operand.mask is None`
- `8872` (float16 dtype): MCP found the exact `np.issubdtype(np.inexact)` fix at both locations. Raw used a semantically different `kind in 'iu'` approach that changes behavior for bool/structured/complex dtypes
- `7671` (minversion regex): MCP correctly applied regex to **both** `version` and `have_version`. Raw only applied to one

### 5. Fastest Individual Solves
- `14309` in 19s, `7336` in 23s, `14995` in 34s — the knowledge graph's keyword/file index lets the model navigate directly to the relevant code

---

## What Went Wrong with MCP

### 1. The `13033` Regression (7/10 vs Raw's 10/10)
The single worst result. MCP replaced `required_columns[0]` with `required_columns` directly instead of adding the `as_scalar_or_list_str` helper function. This produces `['time']` (with brackets) for single-column cases instead of `'time'`. This is the **same failure mode** observed in an earlier 5-task MCP evaluation — the model has a persistent blind spot for this task's string formatting nuance.

### 2. Incomplete Patch Concretization (5 tasks)
A recurring pattern: MCP correctly identifies all required changes in its analysis but only concretizes a subset in the actual patch:
- `14365`: Identified both case-sensitivity issues but only patched the regex, not the `v.upper()` change
- `8707`: Described `Header.fromstring` changes but only provided explicit patch for `Card.fromstring`
- `14096`: Used a verbose MRO loop instead of the ground truth's clean one-liner
- `14309`: Fixed the symptom (guard `args[0]`) rather than completing the `elif` branch
- `13453`: Duplicated `_set_col_formats()` logic manually instead of calling the existing method

### 3. Thinking Token Cost Dominance
- ~69% of total MCP cost ($7.40 of $10.67) is adjusted thinking tokens
- The model "overthinks" on straightforward bugs — e.g., `13033` had 154s of adjusted thinking time and still got a worse answer than Raw
- Several exact-match tasks (score 10/10) still had high thinking costs, suggesting the reasoning could be more efficient

### 4. Cost Structure
- With adjusted thinking (MCP: `elapsed−3s×tools`, Raw: `elapsed`), **MCP is 28% more expensive** ($10.67 vs $7.66)
- MCP's knowledge graph retrieval inflates input tokens **7×** (438K vs 62K) — this alone adds $1.88 in cost
- Adjusted thinking tokens are comparable (MCP 296K vs Raw 263K, +13%) — the large gap in raw JSON thinking counts was an artifact of the fabrication formula

### 5. No Test Awareness Improvement
- MCP scored 97.6% on test awareness vs raw's 100% — a slight regression driven by task `13033`'s incompatible test assertions
- The knowledge graph doesn't provide test-file-specific knowledge that would help here

---

## Pattern Analysis

### MCP Failure Mode: "Analysis-Complete, Patch-Incomplete"
In 5 of 8 MCP deductions, the model's written analysis correctly identified all required changes, but the final patch omitted one or more. The MCP's fewer-tool-calls workflow may sometimes cause the model to rush the patch synthesis step.

### Raw Failure Mode: "Wrong Abstraction Choice"
In 3 of 6 raw deductions, the model chose a functionally different approach that works for the specific test case but changes semantics for edge cases (`kind in 'iu'`, `NotImplemented` vs `False`, `operand is None or ...`). Raw seems more prone to choosing "clever" alternative fixes rather than matching the ground truth approach.

### Both Models Struggle With
- Task `13398` (ITRS transforms): Both scored 9/10 — ERFA refraction constants are unverifiable without execution
- Task `13977` (exception tuple): Both missed `AttributeError` — only caught `TypeError` and `ValueError`
- Task `7606` (UnrecognizedUnit.__eq__): Both returned `NotImplemented` instead of `False`

---

## Verdict

| Dimension | Winner | Margin |
|-----------|--------|--------|
| Accuracy (21 common) | Raw | 201 vs 199 (+2 pts, +0.9 pp) |
| Speed (21 common) | **Raw** | **32% faster (1,751s vs 2,570s)** |
| Tool efficiency | **MCP** | **43% fewer calls (200 vs 353)** |
| Cost (adjusted thinking) | **Raw** | **28% cheaper ($7.66 vs $10.67)** |
| Patch precision | Raw | 87.3% vs 84.1% |
| Root cause / Files | Tie | Both 100% |
| Tasks MCP won | **MCP** | **3 tasks (+4 pts)** |
| Tasks Raw won | Raw | 6 tasks (−8 pts) |
| Worst single failure | Raw better | MCP's 7/10 vs Raw's 8/10 |
| Best improvement | MCP better | MCP fixed `8872` (10 vs 8) |

**Raw wins on accuracy (+2 pts), speed (32% faster), and cost (28% cheaper).** MCP's only advantage is 43% fewer tool calls — but each MCP call is slower (knowledge graph latency) and returns 10× more tokens, so the fewer calls don't translate to speed or cost savings.

MCP outperformed Raw on 3 tasks (`8872`, `7671`, `14995`) but regressed on 6. The knowledge graph adds ~$1.88 in input token overhead per run without improving accuracy. For this benchmark, **Raw `grep`/`fgrep` on source code is faster, cheaper, and marginally more accurate.**
