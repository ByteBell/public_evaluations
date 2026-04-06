# MCP v2 vs Raw v3 — SWE-Bench Comparison Report

**Dataset:** `princeton-nlp/SWE-bench_Verified` — `astropy/astropy`
**Tasks:** 22 (both runs now cover the same 22 tasks)
**Date:** 2026-04-01
**MCP run:** `results_swe_bench/claude_opus_4.6_mcp_v2/`
**Raw run:** `results_swe_bench/claude-opus-4.6-v3-raw/`
**Scoring:** Answer-vs-GT (RC 3 + Files 2 + Patch 3 = 8 pts max, no test execution)

---

## Executive Summary

| Metric | MCP v2 | Raw v3 | Winner |
|--------|--------|--------|--------|
| **Score (22 tasks)** | **163/176 (92.6%)** | 162/176 (92.0%) | **MCP +1 pt** |
| Avg cost/task | **$0.52** | $0.73 | **MCP 1.4x cheaper** |
| Avg time/task | **249 s** | 251 s | ~Tie |
| Avg Eff Weighted Input | **78,088** | 130,288 | **MCP 1.7x leaner** |
| Avg Eff Input | **392,212** | 723,514 | **MCP 1.8x leaner** |
| Root cause % | **97.0%** | **97.0%** | Tie |
| File ID % | **100%** | **100%** | Tie |
| Patch % | **83.3%** | 81.8% | **MCP** |
| Exact matches (8/8) | 13 | 14 | **Raw** |
| Fails (≤4/8) | 0 | 1 | **MCP** |

**MCP edges Raw by 1 point (163 vs 162) at 29% lower cost per task.** Both achieve >92% accuracy. MCP eliminates all outright failures; Raw produces more perfect 8/8 scores.

---

## Per-Task Head-to-Head

| # | Instance ID | Difficulty | MCP v2 | Raw v3 | Delta | Key Difference |
|---|-------------|------------|--------|--------|-------|----------------|
| 1 | `12907` | 15m–1h | **8/8** ✅ | **8/8** ✅ | Tie | Both exact |
| 2 | `13033` | 15m–1h | **8/8** ✅ | **8/8** ✅ | Tie | Both exact |
| 3 | `13236` | 15m–1h | **8/8** ✅ | **8/8** ✅ | Tie | Both exact |
| 4 | `13398` | 1–4h | **8/8** ✅ | **8/8** ✅ | Tie | Both comprehensive (MCP description, Raw diff) |
| 5 | `13453` | 15m–1h | **7/8** ✅ | **8/8** ✅ | **Raw +1** | MCP slightly off insertion point. Raw includes prerequisite line. |
| 6 | `13579` | 1–4h | **6/8** ⚠️ | **8/8** ✅ | **Raw +2** | MCP over-engineers a two-pass approach. Raw matches GT exactly. |
| 7 | `13977` | 15m–1h | **8/8** ✅ | **6/8** ⚠️ | **MCP +2** | MCP matches GT (full try/except). Raw wraps only 3 lines — too narrow. |
| 8 | `14096` | 15m–1h | **7/8** ✅ | **7/8** ✅ | Tie | Both use MRO walk instead of GT's simpler `__getattribute__` |
| 9 | `14182` | 15m–1h | **8/8** ✅ | **8/8** ✅ | Tie | Both exact |
| 10 | `14309` | <15m | **7/8** ✅ | **7/8** ✅ | Tie | Both use `bool(args)` guard instead of GT's `return` fix |
| 11 | `14365` | 15m–1h | **7/8** ✅ | **7/8** ✅ | Tie | Both miss `v.upper() == "NO"` |
| 12 | `14369` | 1–4h | **8/8** ✅ | **8/8** ✅ | Tie | Both exact grammar rule fix |
| 13 | `14508` | 15m–1h | **8/8** ✅ | **8/8** ✅ | Tie | Both exact |
| 14 | `14539` | 15m–1h | **8/8** ✅ | **8/8** ✅ | Tie | Both exact |
| 15 | `14598` | 15m–1h | **5/8** ⚠️ | **8/8** ✅ | **Raw +3** | MCP fixes writer side (`_format_long_image`). GT fix is parser side (`_split` + regex). |
| 16 | `14995` | <15m | **8/8** ✅ | **8/8** ✅ | Tie | Both exact |
| 17 | `7166` | <15m | **8/8** ✅ | **8/8** ✅ | Tie | Both exact |
| 18 | `7336` | <15m | **8/8** ✅ | **8/8** ✅ | Tie | Both exact |
| 19 | `7606` | 15m–1h | **6/8** ⚠️ | **3/8** ❌ | **MCP +3** | MCP fixes UnrecognizedUnit (half fix). Raw returns only filename. |
| 20 | `7671` | 15m–1h | **7/8** ✅ | **7/8** ✅ | Tie | Both strip pre-release tags; different regex approach |
| 21 | `8707` | 15m–1h | **8/8** ✅ | **6/8** ⚠️ | **MCP +2** | MCP produces full patch (both files). Raw gives description only. |
| 22 | `8872` | 15m–1h | **7/8** ✅ | **7/8** ✅ | Tie | Both functionally equivalent dtype check |
| | **TOTAL** | | **163/176** | **162/176** | **MCP +1** | |

**16 tasks tie. 6 tasks diverge — MCP +7, Raw +6 → net MCP +1.**

---

## Dimension Breakdown (22 Tasks)

| Dimension | MCP v2 | Raw v3 | Delta | Notes |
|-----------|--------|--------|-------|-------|
| Root cause | 64/66 (97.0%) | 64/66 (97.0%) | Tie | MCP: -1 on 14598 (wrong side), -1 on 7606 (incomplete). Raw: -1 on 7606 (no diagnosis), -1 on 13977 (narrow scope implied). |
| Correct file(s) | 44/44 (100%) | 44/44 (100%) | Tie | Both perfect |
| Correct patch | 55/66 (83.3%) | 54/66 (81.8%) | MCP +1 | MCP wins on 13977, 7606, 8707. Raw wins on 13453, 13579, 14598. |
| **Overall** | **163/176 (92.6%)** | **162/176 (92.0%)** | **MCP +1** | |

Root cause is now identical. The overall difference comes entirely from the patch dimension.

---

## Full Metrics Dashboard (22 Tasks)

### Aggregated Totals

|  | Input | Cache Write | Cache Read | Output | Eff Weighted Input | Eff Input | Time (s) | Cost (USD) | Score |
|--|-------|-------------|------------|--------|--------------------|-----------|---------:|-----------:|------:|
| **MCP v2** | 50,518 | 704,002 | 7,874,141 | 126,060 | 1,717,935 | 8,628,661 | 5,474 | $11.53 | **163/176** |
| **Raw v3** | 65,038 | 1,057,447 | 14,794,821 | 276,939 | 2,866,329 | 15,917,306 | 5,528 | $16.16 | **162/176** |
| **Ratio (Raw/MCP)** | 1.3x | 1.5x | **1.9x** | **2.2x** | **1.7x** | **1.8x** | 1.0x | **1.4x** | MCP +1 |

### Per-Task Averages

|  | Input | Cache Write | Cache Read | Output | Eff Weighted Input | Eff Input | Time (s) | Cost (USD) | Score |
|--|-------|-------------|------------|--------|--------------------|-----------|---------:|-----------:|------:|
| **MCP v2** | 2,296 | 32,000 | 357,915 | 5,730 | 78,088 | 392,212 | 249 | $0.52 | **7.4/8** |
| **Raw v3** | 2,956 | 48,066 | 672,492 | 12,588 | 130,288 | 723,514 | 251 | $0.73 | **7.4/8** |

### Efficiency per Score Point

|  | EW/pt | EI/pt | Time/pt | Cost/pt |
|--|-------|-------|---------|---------|
| **MCP v2** | **10,540** | **52,937** | **33.6 s** | **$0.071** |
| **Raw v3** | 17,694 | 98,255 | 34.1 s | $0.100 |

> **Effective Weighted Input** = Input + (1.25 x Cache Write) + (0.1 x Cache Read)
>
> **Effective Input** = Input + Cache Write + Cache Read

### Why 1.9x Fewer Cache Reads ≠ 1.4x Lower Cost

The raw token ratios (1.9x cache read, 2.2x output) exceed the cost ratio (1.4x) because the extra tokens in Raw are disproportionately **cheap haiku tokens**.

Raw v3 uses multi-agent exploration where Haiku sub-agents do file search, directory listing, and code reading. These generate the bulk of Raw's cache reads/writes at haiku rates ($0.10/MTok cache read) — 5x cheaper than Opus rates. MCP v2 routes almost all work through Opus directly via MCP tool calls.

| Metric | Ratio (Raw/MCP) | Why it differs from cost |
|--------|:---------------:|--------------------------|
| Cache Read tokens | 1.9x | CReads are 10x cheaper than input |
| Effective Input (unweighted) | 1.8x | Treats all input-side tokens as equal cost |
| **Eff Weighted Input** | **1.7x** | **Weights by pricing tier — closest to actual cost** |
| Actual cost | 1.4x | Includes output-side costs + haiku/opus model mix |

The EW metric (1.7x) tracks closest to actual cost because it encodes Anthropic's pricing tiers. The remaining gap to 1.4x is the haiku model-mix discount.

---

## Per-Task Comparison — All Metrics Side-by-Side

### MCP v2 — Per Task

| Instance ID | Input | CWrite | CRead | Output | EW Input | Eff Input | Time (s) | Cost | Score |
|-------------|------:|-------:|------:|-------:|---------:|----------:|---------:|-----:|------:|
| `12907` | 2,131 | 30,555 | 130,811 | 1,538 | 53,406 | 163,497 | 43 | $0.30 | 8/8 |
| `13033` | 3,254 | 16,973 | 133,478 | 2,535 | 37,818 | 153,705 | 66 | $0.24 | 8/8 |
| `13236` | 1,471 | 29,232 | 600,599 | 4,535 | 98,071 | 631,302 | 131 | $0.60 | 8/8 |
| `13398` | 6,210 | 53,735 | 473,428 | 4,746 | 120,722 | 533,373 | 281 | $0.70 | **8/8** |
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
| `14598` | 2,099 | 65,498 | 1,183,061 | 18,837 | 202,278 | 1,250,658 | 547 | $1.47 | **5/8** |
| `14995` | 3,411 | 23,534 | 245,911 | 1,536 | 57,420 | 272,856 | 55 | $0.31 | 8/8 |
| `7166` | 928 | 38,233 | 352,957 | 7,514 | 84,015 | 392,118 | 145 | $0.60 | 8/8 |
| `7336` | 1,208 | 25,656 | 248,706 | 3,019 | 58,149 | 275,570 | 83 | $0.36 | 8/8 |
| `7606` | 1,040 | 20,800 | 319,079 | 2,456 | 58,948 | 340,919 | 94 | $0.35 | **6/8** |
| `7671` | 1,442 | 29,278 | 265,732 | 7,008 | 64,613 | 296,452 | 785 | $0.49 | 7/8 |
| `8707` | 840 | 25,915 | 301,708 | 3,231 | 63,405 | 328,463 | 84 | $0.39 | **8/8** |
| `8872` | 1,169 | 23,986 | 295,209 | 3,554 | 60,673 | 320,364 | 187 | $0.39 | 7/8 |

### Raw v3 — Per Task

| Instance ID | Input | CWrite | CRead | Output | EW Input | Eff Input | Time (s) | Cost | Score |
|-------------|------:|-------:|------:|-------:|---------:|----------:|---------:|-----:|------:|
| `12907` | 1,221 | 64,472 | 596,225 | 7,764 | 141,434 | 661,918 | 259 | $0.40 | 8/8 |
| `13033` | 3,215 | 26,150 | 427,022 | 11,575 | 78,605 | 456,387 | 191 | $0.67 | 8/8 |
| `13236` | 6,774 | 78,105 | 1,286,732 | 26,238 | 233,079 | 1,371,611 | 422 | $1.40 | 8/8 |
| `13398` | 6,339 | 110,391 | 1,725,316 | 35,047 | 316,859 | 1,842,046 | 612 | $1.77 | **8/8** |
| `13453` | 6,598 | 24,324 | 691,323 | 5,240 | 106,135 | 722,245 | 123 | $0.64 | **8/8** |
| `13579` | 2,981 | 33,322 | 394,326 | 13,334 | 84,066 | 430,629 | 223 | $0.74 | **8/8** |
| `13977` | 3,301 | 30,819 | 717,343 | 9,324 | 113,559 | 751,463 | 212 | $0.79 | **6/8** |
| `14096` | 1,293 | 55,280 | 631,445 | 8,982 | 133,538 | 688,018 | 175 | $0.62 | 7/8 |
| `14182` | 4,568 | 72,724 | 763,280 | 10,494 | 171,801 | 840,572 | 232 | $0.57 | 8/8 |
| `14309` | 2,438 | 11,740 | 72,880 | 1,655 | 24,401 | 87,058 | 171 | $0.15 | 7/8 |
| `14365` | 1,724 | 27,761 | 275,153 | 7,338 | 63,941 | 304,638 | 141 | $0.50 | 7/8 |
| `14369` | 2,428 | 51,941 | 762,750 | 31,353 | 143,629 | 817,119 | 475 | $1.49 | 8/8 |
| `14508` | 2,890 | 45,807 | 468,976 | 5,353 | 107,046 | 517,673 | 100 | $0.39 | 8/8 |
| `14539` | 1,552 | 21,935 | 436,492 | 6,156 | 72,620 | 459,979 | 123 | $0.51 | 8/8 |
| `14598` | 2,189 | 55,668 | 1,207,244 | 32,586 | 192,498 | 1,265,101 | 600 | $1.77 | **8/8** |
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
| `13453` | 7 | 8 | Raw +1 | $0.34 | $0.64 | 62K | 106K | 71s | 123s |
| `13579` | 6 | 8 | Raw +2 | $0.50 | $0.74 | 74K | 84K | 472s | 223s |
| `14598` | 5 | 8 | Raw +3 | $1.47 | $1.77 | 202K | 192K | 547s | 600s |
| `13977` | 8 | 6 | MCP +2 | $0.48 | $0.79 | 74K | 114K | 392s | 212s |
| `7606` | 6 | 3 | MCP +3 | $0.35 | $0.39 | 59K | 96K | 94s | 181s |
| `8707` | 8 | 6 | MCP +2 | $0.39 | $1.14 | 63K | 320K | 84s | 372s |
| **Net** | | | **MCP +1** | | | | | | |

---

## Where They Diverge: The 6 Disagreement Tasks

### Task 15 (`14598`) — Raw +3

**Issue:** FITS CONTINUE cards lose quotes from double un-escaping (15m–1h)

| | MCP v2 (5/8) | Raw v3 (8/8) |
|---|---|---|
| Patch | Proposes fixing `_format_long_image` (writer side) to not split `''` pairs | GT's parser-side fix: add `$` anchor to `_strg_comment_RE` + remove `.replace("''", "'")` in `_split()` |
| Why | MCP correctly identified the symptom but misattributed the root cause (writer vs parser) | Raw found the correct root cause on the parser side |

**Takeaway:** MCP's knowledge graph surfaced the CONTINUE card code but led the model down the wrong causal path. Raw's direct file reading allowed tracing the actual double-unescaping flow.

### Task 6 (`13579`) — Raw +2

**Issue:** `SlicedLowLevelWCS.world_to_pixel_values` hardcoded `1.0` for dropped dimensions (1–4h)

| | MCP v2 (6/8) | Raw v3 (8/8) |
|---|---|---|
| Patch | Over-engineered two-pass iterative approach | GT's simple one-line: `_pixel_to_world_values_all(*[0]*len(self._pixel_keep))` |
| Why | MCP diagnosed correctly but proposed complex solution | Raw found the minimal fix |

**Takeaway:** MCP sometimes over-thinks simple fixes. The GT is a one-line addition; MCP proposed a multi-step iterative approach.

### Task 5 (`13453`) — Raw +1

**Issue:** HTML writer ignores `formats` argument (15m–1h)

| | MCP v2 (7/8) | Raw v3 (8/8) |
|---|---|---|
| Patch | Both lines identified, slightly different insertion point | Both `self.data.cols = cols` + `_set_col_formats()` in correct position |
| Why | MCP answer functionally equivalent but minor positioning difference | Raw places both lines exactly per GT |

**Takeaway:** Minor difference — both approaches understand the fix; Raw's direct file access gives more precise insertion context.

### Task 7 (`13977`) — MCP +2

**Issue:** `Quantity.__array_ufunc__` should return `NotImplemented` for duck types (15m–1h)

| | MCP v2 (8/8) | Raw v3 (6/8) |
|---|---|---|
| Patch | Wrap entire body in try/except, check other operands' `__array_ufunc__` — matches GT | Only wraps input conversion loop (3 lines) — too narrow |
| Why | MCP's knowledge graph retrieved the full method context | Raw's fix was conceptually correct but incomplete in scope |

**Takeaway:** MCP's broader context retrieval led to a more complete fix. Raw's narrow focus missed the full scope of the GT refactor.

### Task 19 (`7606`) — MCP +3

**Issue:** `Unit.__eq__` returns `False` instead of `NotImplemented` (15m–1h)

| | MCP v2 (6/8) | Raw v3 (3/8) |
|---|---|---|
| Patch | Fixes `UnrecognizedUnit.__eq__` with try/except + NotImplemented (half the GT) | Only returns filename — no patch, no root cause |
| Why | MCP found and fixed one of two locations | Raw failed to produce any answer content |

**Takeaway:** Both missed the `UnitBase.__eq__` location, but MCP at least produced a working half-fix. Raw's complete failure here is its worst result.

### Task 21 (`8707`) — MCP +2

**Issue:** `Card.fromstring` / `Header.fromstring` should accept bytes (15m–1h)

| | MCP v2 (8/8) | Raw v3 (6/8) |
|---|---|---|
| Patch | Full code: Card decode latin1 + Header bytes-aware CONTINUE/END/sep | Description only — says what to do but no actual diff |
| Why | MCP synthesized complete code with correct encoding | Raw described the fix in prose but stopped short of code |

**Takeaway:** MCP produced a complete, correct patch. Raw understood the fix but didn't generate code.

---

## Shared Strengths & Weaknesses

### Both Get Right (16 tasks tie)

16 of 22 tasks produce identical scores. On these tasks:
- **13 score 8/8** — both approaches reliably solve standard single-file bugs
- **3 tie at 7/8** with the *same* implementation divergence from GT (14309, 14365, 8872)
- **2 more tie at 7/8** with equivalent alternative approaches (14096, 7671)

### Both Get Wrong the Same Way

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
| Wrong causal path (writer vs parser) | Task 15 — 14598 (5/8) | — |
| Over-engineering a simple fix | Task 6 — 13579 (6/8) | — |
| File-only / description-only answer (no code) | — | Task 19 — 7606 (3/8), Task 21 — 8707 (6/8) |
| Too-narrow patch scope | — | Task 7 — 13977 (6/8) |

MCP fails when it follows the wrong causal thread or over-engineers. Raw fails when it can't finalize exploration into code. **A hypothetical ensemble taking the best of each would score 170/176 (96.6%).**

---

## Verdict

| Dimension | Winner | Detail |
|-----------|--------|--------|
| **Overall accuracy** | **MCP** | 163/176 (92.6%) vs 162/176 (92.0%) |
| Root cause | Tie | Both 97.0% (64/66) |
| File identification | Tie | Both 100% (44/44) |
| Patch correctness | **MCP** | 83.3% vs 81.8% |
| Exact matches | **Raw** | 14 vs 13 perfect 8/8 scores |
| Failures | **MCP** | 0 fails vs 1 fail |
| Cost | **MCP** | $11.53 vs $16.16 (1.4x cheaper) |
| Time | Tie | 5,474s vs 5,528s (~identical) |
| Eff Weighted Input | **MCP** | 1.72M vs 2.87M (1.7x leaner) |
| Eff Input | **MCP** | 8.63M vs 15.92M (1.8x leaner) |
| Cost per point | **MCP** | $0.071 vs $0.100 (1.4x better) |
| EW per point | **MCP** | 10,540 vs 17,694 (1.7x better) |

**MCP edges Raw by 1 point (163 vs 162) at 29% lower cost per task. Both achieve >92% accuracy with identical root-cause and file-identification performance. The 1-point gap comes entirely from patch quality — MCP's broader context retrieval produces slightly better patches on average, while Raw produces more individual perfect scores.**

**The optimal strategy depends on constraints:**
- **Cost-sensitive:** MCP v2 — higher accuracy at 1.4x fewer dollars
- **Maximum accuracy:** Ensemble best-of-both — projected 96.6% (170/176)
- **Maximum perfect scores:** Raw v3 — 14 exact matches vs 13
