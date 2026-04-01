# MCP v2 vs Raw v3 — SWE-Bench Comparison Report

**Dataset:** `princeton-nlp/SWE-bench_Verified` — `astropy/astropy`
**Common tasks:** 21 (MCP v2 has 21; Raw v3 has 22 — task `14598` is Raw-only)
**Date:** 2026-04-01
**MCP run:** `results_swe_bench/claude_opus_4.6_mcp_v2/`
**Raw run:** `results_swe_bench/claude-opus-4.6-v3-raw/`
**Scoring:** Answer-vs-answer (RC 3 + Files 2 + Patch 3 = 8 pts max, no test evaluation)

---

## Executive Summary

| Metric | MCP v2 | Raw v3 | Winner |
|--------|--------|--------|--------|
| **Score (21 common)** | **152/168 (90.5%)** | **152/168 (90.5%)** | **Tie** |
| Avg cost/task | **$0.47** | $0.71 | **MCP 1.5x cheaper** |
| Avg time/task | **233 s** | 299 s | **MCP 1.3x faster** |
| Avg Eff Weighted Input | **71,113** | 141,427 | **MCP 2.0x leaner** |
| Avg Eff Input | **340,751** | 788,782 | **MCP 2.3x leaner** |
| Root cause % | 93.7% | **96.8%** | **Raw** |
| File ID % | **100%** | **100%** | Tie |
| Patch % | **81.0%** | 77.8% | **MCP** |
| Exact matches (8/8) | 12 | 12 | Tie |
| Fails (≤4/8) | 1 | 1 | Tie |

**The two approaches tie at exactly 152/168.** Each has distinct failure modes that cancel out perfectly. MCP achieves this at half the effective token cost.

---

## Per-Task Head-to-Head

| # | Instance ID | Difficulty | MCP v2 | Raw v3 | Delta | Key Difference |
|---|-------------|------------|--------|--------|-------|----------------|
| 1 | `12907` | 15m–1h | **8/8** ✅ | **8/8** ✅ | Tie | Both exact |
| 2 | `13033` | 15m–1h | **8/8** ✅ | **8/8** ✅ | Tie | Both exact |
| 3 | `13236` | 15m–1h | **8/8** ✅ | **8/8** ✅ | Tie | Both exact |
| 4 | `13398` | 1–4h | **2/8** ❌ | **7/8** ✅ | **Raw +5** | MCP returns file-list only, no patch. Raw full patch minus TETE. |
| 5 | `13453` | 15m–1h | **7/8** ✅ | **7/8** ✅ | Tie | Both missing one patch detail |
| 6 | `13579` | 1–4h | **6/8** ⚠️ | **8/8** ✅ | **Raw +2** | MCP over-engineers a two-pass approach. Raw matches GT exactly. |
| 7 | `13977` | 15m–1h | **8/8** ✅ | **6/8** ⚠️ | **MCP +2** | MCP matches GT (full try/except). Raw wraps only 3 lines — too narrow. |
| 8 | `14096` | 15m–1h | **7/8** ✅ | **7/8** ✅ | Tie | Both use MRO walk instead of GT's simpler `__getattribute__` |
| 9 | `14182` | 15m–1h | **8/8** ✅ | **8/8** ✅ | Tie | Both exact |
| 10 | `14309` | <15m | **7/8** ✅ | **7/8** ✅ | Tie | Both use `bool(args)` guard instead of GT's `return` fix |
| 11 | `14365` | 15m–1h | **7/8** ✅ | **7/8** ✅ | Tie | Both miss `v.upper() == "NO"` |
| 12 | `14369` | 1–4h | **8/8** ✅ | **8/8** ✅ | Tie | Both exact grammar rule fix |
| 13 | `14508` | 15m–1h | **8/8** ✅ | **8/8** ✅ | Tie | Both exact |
| 14 | `14539` | 15m–1h | **8/8** ✅ | **8/8** ✅ | Tie | Both exact |
| 15 | `14995` | <15m | **8/8** ✅ | **8/8** ✅ | Tie | Both exact |
| 16 | `7166` | <15m | **8/8** ✅ | **8/8** ✅ | Tie | Both exact |
| 17 | `7336` | <15m | **8/8** ✅ | **8/8** ✅ | Tie | Both exact |
| 18 | `7606` | 15m–1h | **6/8** ⚠️ | **3/8** ❌ | **MCP +3** | MCP fixes UnrecognizedUnit (half fix). Raw returns only filename. |
| 19 | `7671` | 15m–1h | **7/8** ✅ | **7/8** ✅ | Tie | Both strip pre-release tags; different regex approach |
| 20 | `8707` | 15m–1h | **8/8** ✅ | **6/8** ⚠️ | **MCP +2** | MCP produces full patch (both files). Raw gives description only. |
| 21 | `8872` | 15m–1h | **7/8** ✅ | **7/8** ✅ | Tie | Both functionally equivalent dtype check |
| | **TOTAL** | | **152/168** | **152/168** | **Tie** | |

**16 tasks tie. 5 tasks diverge — and the deltas cancel exactly (MCP +7, Raw +7).**

---

## Dimension Breakdown (21 Common Tasks)

| Dimension | MCP v2 | Raw v3 | Delta | Notes |
|-----------|--------|--------|-------|-------|
| Root cause | 59/63 (93.7%) | 61/63 (96.8%) | Raw +2 | MCP=0 on 13398 (file-list-only), Raw=1 on 7606 (file-only) |
| Correct file(s) | 42/42 (100%) | 42/42 (100%) | Tie | Both perfect |
| Correct patch | 51/63 (81.0%) | 49/63 (77.8%) | MCP +2 | MCP wins on 13977, 7606, 8707; Raw wins on 13398, 13579 |
| **Overall** | **152/168 (90.5%)** | **152/168 (90.5%)** | **Tie** | |

The net-zero delta hides opposing strengths: MCP produces better patches on average (+2), but Raw has stronger root cause analysis (+2). These cancel perfectly.

---

## Full Metrics Dashboard (21 Common Tasks)

### Aggregated Totals

|  | Input | Cache Write | Cache Read | Output | Eff Weighted Input | Eff Input | Time (s) | Cost (USD) | Score |
|--|-------|-------------|------------|--------|--------------------|-----------|---------:|-----------:|------:|
| **MCP v2** | 48,622 | 638,282 | 6,468,873 | 115,813 | 1,493,366 | 7,155,777 | 4,890 | $9.91 | **152/168** |
| **Raw v3** | 57,587 | 1,097,130 | 15,409,700 | 325,482 | 2,969,970 | 16,564,417 | 6,282 | $15.00 | **152/168** |
| **Ratio (Raw/MCP)** | 1.2x | 1.7x | **2.4x** | **2.8x** | **2.0x** | **2.3x** | 1.3x | 1.5x | **Tie** |

### Per-Task Averages

|  | Input | Cache Write | Cache Read | Output | Eff Weighted Input | Eff Input | Time (s) | Cost (USD) | Score |
|--|-------|-------------|------------|--------|--------------------|-----------|---------:|-----------:|------:|
| **MCP v2** | 2,315 | 30,395 | 308,042 | 5,515 | 71,113 | 340,751 | 233 | $0.47 | **7.2/8** |
| **Raw v3** | 2,742 | 52,244 | 733,795 | 15,499 | 141,427 | 788,782 | 299 | $0.71 | **7.2/8** |

### Efficiency per Score Point

|  | Input/pt | CWrite/pt | CRead/pt | Output/pt | EW/pt | EI/pt | Time/pt | Cost/pt |
|--|----------|-----------|----------|-----------|-------|-------|---------|---------|
| **MCP v2** | 320 | 4,199 | 42,558 | 762 | **9,825** | **47,077** | **32.2 s** | **$0.065** |
| **Raw v3** | 379 | 7,218 | 101,380 | 2,142 | 19,539 | 109,003 | 41.3 s | $0.099 |

> **Effective Weighted Input** = Input + (1.25 x Cache Write) + (0.1 x Cache Read)
>
> **Effective Input** = Input + Cache Write + Cache Read

---

## Per-Task Comparison — All Metrics Side-by-Side

### MCP v2 — Per Task

| Instance ID | Input | CWrite | CRead | Output | EW Input | Eff Input | Time (s) | Cost | Score |
|-------------|------:|-------:|------:|-------:|---------:|----------:|---------:|-----:|------:|
| `12907` | 2,131 | 30,555 | 130,811 | 1,538 | 53,406 | 163,497 | 43 | $0.30 | 8/8 |
| `13033` | 3,254 | 16,973 | 133,478 | 2,535 | 37,818 | 153,705 | 66 | $0.24 | 8/8 |
| `13236` | 1,567 | 31,938 | 318,828 | 10,628 | 73,373 | 352,333 | 233 | $0.38 | 8/8 |
| `13398` | 6,317 | 50,807 | 532,992 | 7,243 | 123,125 | 590,116 | 142 | $0.77 | **2/8** |
| `13453` | 6,660 | 20,717 | 290,438 | 2,395 | 61,600 | 317,815 | 71 | $0.34 | 7/8 |
| `13579` | 2,947 | 30,727 | 327,086 | 5,706 | 74,065 | 360,760 | 472 | $0.50 | **6/8** |
| `13977` | 3,256 | 34,130 | 285,049 | 4,665 | 74,424 | 322,435 | 392 | $0.48 | **8/8** |
| `14096` | 1,222 | 26,933 | 301,371 | 4,799 | 65,025 | 329,526 | 134 | $0.44 | 7/8 |
| `14182` | 1,357 | 39,765 | 290,420 | 3,213 | 80,105 | 331,542 | 82 | $0.48 | 8/8 |
| `14309` | 2,409 | 18,743 | 229,002 | 1,696 | 48,738 | 250,154 | 52 | $0.28 | 7/8 |
| `14365` | 1,695 | 29,961 | 370,038 | 2,868 | 76,150 | 401,694 | 96 | $0.45 | 7/8 |
| `14369` | 2,394 | 74,331 | 706,010 | 35,852 | 165,909 | 782,735 | 845 | $1.72 | 8/8 |
| `14508` | 1,863 | 20,531 | 283,103 | 2,194 | 55,837 | 305,497 | 413 | $0.33 | 8/8 |
| `14539` | 1,512 | 24,769 | 240,945 | 2,163 | 56,568 | 267,226 | 416 | $0.33 | 8/8 |
| `14995` | 3,411 | 23,534 | 245,911 | 1,536 | 57,420 | 272,856 | 55 | $0.31 | 8/8 |
| `7166` | 928 | 38,233 | 352,957 | 7,514 | 84,015 | 392,118 | 145 | $0.60 | 8/8 |
| `7336` | 1,208 | 25,656 | 248,706 | 3,019 | 58,149 | 275,570 | 83 | $0.36 | 8/8 |
| `7606` | 1,040 | 20,800 | 319,079 | 2,456 | 58,948 | 340,919 | 94 | $0.35 | **6/8** |
| `7671` | 1,442 | 29,278 | 265,732 | 7,008 | 64,613 | 296,452 | 785 | $0.49 | 7/8 |
| `8707` | 840 | 25,915 | 301,708 | 3,231 | 63,405 | 328,463 | 84 | $0.39 | **8/8** |
| `8872` | 1,169 | 23,986 | 295,209 | 3,554 | 60,673 | 320,364 | 187 | $0.39 | 7/8 |

### Raw v3 — Per Task (21 Common)

| Instance ID | Input | CWrite | CRead | Output | EW Input | Eff Input | Time (s) | Cost | Score |
|-------------|------:|-------:|------:|-------:|---------:|----------:|---------:|-----:|------:|
| `12907` | 1,221 | 64,472 | 596,225 | 7,764 | 141,434 | 661,918 | 259 | $0.40 | 8/8 |
| `13033` | 3,217 | 43,028 | 527,844 | 21,233 | 109,786 | 574,089 | 443 | $0.64 | 8/8 |
| `13236` | 1,519 | 64,182 | 1,173,095 | 35,853 | 199,056 | 1,238,796 | 547 | $1.13 | 8/8 |
| `13398` | 6,314 | 142,489 | 2,262,850 | 64,862 | 410,710 | 2,411,653 | 1,077 | $1.83 | **7/8** |
| `13453` | 6,614 | 84,622 | 1,988,727 | 37,281 | 311,264 | 2,079,963 | 636 | $1.48 | 7/8 |
| `13579` | 2,981 | 33,322 | 394,326 | 13,334 | 84,066 | 430,629 | 223 | $0.74 | **8/8** |
| `13977` | 3,301 | 30,819 | 717,343 | 9,324 | 113,559 | 751,463 | 212 | $0.79 | **6/8** |
| `14096` | 1,293 | 55,280 | 631,445 | 8,982 | 133,538 | 688,018 | 175 | $0.62 | 7/8 |
| `14182` | 4,568 | 72,724 | 763,280 | 10,494 | 171,801 | 840,572 | 232 | $0.57 | 8/8 |
| `14309` | 2,438 | 11,740 | 72,880 | 1,655 | 24,401 | 87,058 | 171 | $0.15 | 7/8 |
| `14365` | 1,724 | 27,761 | 275,153 | 7,338 | 63,941 | 304,638 | 141 | $0.50 | 7/8 |
| `14369` | 2,428 | 51,941 | 762,750 | 31,353 | 143,629 | 817,119 | 475 | $1.49 | 8/8 |
| `14508` | 2,890 | 45,807 | 468,976 | 5,353 | 107,046 | 517,673 | 100 | $0.39 | 8/8 |
| `14539` | 1,552 | 21,935 | 436,492 | 6,156 | 72,620 | 459,979 | 123 | $0.51 | 8/8 |
| `14995` | 3,566 | 53,401 | 617,511 | 6,820 | 132,068 | 674,478 | 153 | $0.51 | 8/8 |
| `7166` | 4,320 | 55,079 | 484,355 | 7,370 | 121,604 | 543,754 | 151 | $0.39 | 8/8 |
| `7336` | 1,244 | 14,944 | 272,887 | 3,052 | 47,213 | 289,075 | 291 | $0.31 | 8/8 |
| `7606` | 568 | 42,044 | 431,878 | 6,891 | 96,311 | 474,490 | 181 | $0.39 | **3/8** |
| `7671` | 1,475 | 38,816 | 245,557 | 12,617 | 74,551 | 285,848 | 202 | $0.68 | 7/8 |
| `8707` | 3,112 | 98,341 | 1,943,124 | 20,747 | 320,351 | 2,044,577 | 372 | $1.14 | **6/8** |
| `8872` | 1,242 | 44,383 | 343,002 | 7,003 | 91,021 | 388,627 | 119 | $0.35 | 7/8 |

### Delta View (diverging tasks only)

| Instance ID | MCP Score | Raw Score | Delta | MCP Cost | Raw Cost | MCP EW | Raw EW | MCP Time | Raw Time |
|-------------|-----------|-----------|-------|----------|----------|--------|--------|----------|----------|
| `13398` | 2 | 7 | Raw +5 | $0.77 | $1.83 | 123K | 411K | 142s | 1,077s |
| `13579` | 6 | 8 | Raw +2 | $0.50 | $0.74 | 74K | 84K | 472s | 223s |
| `13977` | 8 | 6 | MCP +2 | $0.48 | $0.79 | 74K | 114K | 392s | 212s |
| `7606` | 6 | 3 | MCP +3 | $0.35 | $0.39 | 59K | 96K | 94s | 181s |
| `8707` | 8 | 6 | MCP +2 | $0.39 | $1.14 | 63K | 320K | 84s | 372s |
| **Net** | | | **0** | | | | | | |

---

## Where They Diverge: The 5 Disagreement Tasks

### Task 4 (`13398`) — Raw +5

**Issue:** Add ITRS ↔ AltAz/HADec topocentric transforms (1–4h, 6-file change)

| | MCP v2 (2/8) | Raw v3 (7/8) |
|---|---|---|
| Answer | Comma-separated file list — no root cause, no patch | Full patch: new 146-line transform file, ITRS location attr, CIRS propagation |
| Why | 30 tool calls, highest cost ($0.77), but synthesis failed completely | Multi-agent exploration produced complete patch minus TETE |

**Takeaway:** MCP's knowledge graph identified all 5 files correctly but the answer synthesis step collapsed on this complex multi-file task. Raw's multi-turn approach produced a near-complete patch.

### Task 6 (`13579`) — Raw +2

**Issue:** `SlicedLowLevelWCS.world_to_pixel_values` hardcoded `1.0` for dropped dimensions (1–4h)

| | MCP v2 (6/8) | Raw v3 (8/8) |
|---|---|---|
| Patch | Over-engineered two-pass approach | GT's simple one-line: `_pixel_to_world_values_all(*[0]*len(self._pixel_keep))` |
| Why | MCP correctly diagnosed the bug but proposed a more complex iterative solution | Raw found the minimal fix |

**Takeaway:** MCP sometimes over-thinks simple fixes. The GT is a one-line addition; MCP proposed a multi-step iterative approach.

### Task 7 (`13977`) — MCP +2

**Issue:** `Quantity.__array_ufunc__` should return `NotImplemented` for duck types (15m–1h)

| | MCP v2 (8/8) | Raw v3 (6/8) |
|---|---|---|
| Patch | Wrap entire body in try/except, check other operands' `__array_ufunc__` — matches GT | Only wraps input conversion loop (3 lines) — too narrow |
| Why | MCP's knowledge graph retrieved the full method context | Raw's fix was conceptually correct but incomplete |

**Takeaway:** MCP's broader context retrieval led to a more complete fix. Raw's narrow focus missed the full scope of the GT refactor.

### Task 18 (`7606`) — MCP +3

**Issue:** `Unit.__eq__` returns `False` instead of `NotImplemented` (15m–1h)

| | MCP v2 (6/8) | Raw v3 (3/8) |
|---|---|---|
| Patch | Fixes `UnrecognizedUnit.__eq__` with try/except + NotImplemented (half the GT) | Only returns filename — no patch, no root cause |
| Why | MCP found and fixed one of two locations | Raw failed to produce any answer content |

**Takeaway:** Both missed the `UnitBase.__eq__` location, but MCP at least produced a working half-fix. Raw's complete failure here is its worst result.

### Task 20 (`8707`) — MCP +2

**Issue:** `Card.fromstring` / `Header.fromstring` should accept bytes (15m–1h)

| | MCP v2 (8/8) | Raw v3 (6/8) |
|---|---|---|
| Patch | Full code: Card decode latin1 + Header bytes-aware CONTINUE/END/sep | Description only — says what to do but no actual diff |
| Why | MCP synthesized complete code with correct encoding | Raw described the fix in prose but stopped short of code |

**Takeaway:** MCP produced a complete, correct patch. Raw understood the fix but didn't generate code.

---

## Shared Strengths & Weaknesses

### Both Get Right (16 tasks tie)

16 of 21 tasks produce identical scores. On these tasks:
- **14 score 8/8 or 7/8** — both approaches reliably solve standard single-file bugs
- **Tasks 14309, 14365, 8872** tie at 7/8 with the *same* implementation divergence from GT
- **Tasks 14096, 7671** tie at 7/8 with *different* but equivalent alternative approaches

### Both Get Wrong

| Task | MCP | Raw | Shared Issue |
|------|-----|-----|-------------|
| `14365` | 7/8 | 7/8 | Both add `re.IGNORECASE` but miss `v.upper() == "NO"` in data parsing |
| `14309` | 7/8 | 7/8 | Both use `bool(args)` guard instead of GT's structural `return` fix |
| `14096` | 7/8 | 7/8 | Both walk the MRO instead of GT's simpler `__getattribute__` |

These shared misses suggest both approaches find the *same* alternative implementation when the GT's approach is non-obvious.

---

## Complementary Failure Modes

| Failure type | MCP v2 | Raw v3 |
|---|---|---|
| Complex multi-file synthesis collapse | Task 4 (2/8) | — |
| Over-engineering a simple fix | Task 6 (6/8) | — |
| File-only / description-only answer (no code) | — | Tasks 18 (3/8), 20 (6/8) |
| Too-narrow patch scope | — | Task 7 (6/8) |

MCP fails when it can't synthesize across many files. Raw fails when it can't finalize exploration into code. **A hypothetical ensemble taking the best of each would score 159/168 (94.6%).**

---

## Verdict

| Dimension | Winner | Detail |
|-----------|--------|--------|
| **Overall accuracy** | **Tie** | 152/168 (90.5%) each |
| Root cause | Raw (+2 pts) | 96.8% vs 93.7% |
| File identification | Tie | Both 100% |
| Patch correctness | MCP (+2 pts) | 81.0% vs 77.8% |
| Cost | **MCP** | $9.91 vs $15.00 (1.5x cheaper) |
| Time | **MCP** | 4,890s vs 6,282s (1.3x faster) |
| Eff Weighted Input | **MCP** | 1.49M vs 2.97M (2.0x leaner) |
| Eff Input | **MCP** | 7.16M vs 16.56M (2.3x leaner) |
| Cost per point | **MCP** | $0.065 vs $0.099 (1.5x better) |
| EW per point | **MCP** | 9,825 vs 19,539 (2.0x better) |
| Hard tasks (1–4h) | Split | Raw wins 13398 (+5), 13579 (+2). MCP wins 14369 (tie at 8/8). |
| Catastrophic failures | Split | MCP: 13398 (2/8). Raw: 7606 (3/8). |

**Both approaches achieve 90.5% accuracy on the same 21-task benchmark. MCP does it at half the token cost. Their failure modes are complementary — MCP struggles with multi-file synthesis, Raw struggles with answer finalization.**

**The optimal strategy depends on constraints:**
- **Cost-sensitive:** MCP v2 — same accuracy, 2x fewer effective tokens
- **Maximum accuracy:** Ensemble best-of-both — projected 94.6% (159/168)
- **Hard multi-file tasks:** Raw v3 — avoids MCP's synthesis collapse on task 4
