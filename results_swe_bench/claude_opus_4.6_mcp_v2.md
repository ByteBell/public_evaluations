# Claude Opus 4.6 MCP v2 — SWE-Bench Evaluation Report

**Dataset:** `princeton-nlp/SWE-bench_Verified` — `astropy/astropy`
**Evaluated:** 22 tasks from `astropy_tasks.json`
**Date:** 2026-04-01
**Judge:** Claude Code (claude-opus-4-6)
**Ground truth source:** `results_swe_bench/astropy_tasks.json`
**Raw MCP responses:** `results_swe_bench/claude_opus_4.6_mcp_v2/*/answer.json`

---

## Scoring Rubric

| Dimension | Weight | What is graded |
|-----------|--------|----------------|
| Root cause identification | 3 pts | Did the model correctly diagnose *why* the bug exists? |
| Correct file(s) | 2 pts | Did it identify the right file(s) to change? |
| Correct patch / code change | 3 pts | Does the code change match or is functionally equivalent to ground truth? |

**Grade tiers:** ✅ Exact (8/8) · ✅ Near-perfect (7/8) · ⚠️ Partial (5–6/8) · ❌ Fail (≤4/8)

---

## Combined Per-Question: Score · Time · Cost

| # | Instance ID | Difficulty | RC | Files | Patch | **Score** | Grade | Time (s) | Cost (USD) |
|---|-------------|------------|----|-------|-------|-----------|-------|----------|------------|
| 1 | `astropy__astropy-12907` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 43 | $0.297 |
| 2 | `astropy__astropy-13033` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 66 | $0.239 |
| 3 | `astropy__astropy-13236` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 131 | $0.598 |
| 4 | `astropy__astropy-13398` | 1–4h | 3 | 2 | 3 | **8/8** | ✅ Exact | 281 | $0.697 |
| 5 | `astropy__astropy-13453` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 71 | $0.341 |
| 6 | `astropy__astropy-13579` | 1–4h | 3 | 2 | 1 | **6/8** | ⚠️ Partial | 472 | $0.501 |
| 7 | `astropy__astropy-13977` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 392 | $0.475 |
| 8 | `astropy__astropy-14096` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 134 | $0.440 |
| 9 | `astropy__astropy-14182` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 82 | $0.475 |
| 10 | `astropy__astropy-14309` | <15m | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 52 | $0.276 |
| 11 | `astropy__astropy-14365` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 96 | $0.445 |
| 12 | `astropy__astropy-14369` | 1–4h | 3 | 2 | 3 | **8/8** | ✅ Exact | 845 | $1.716 |
| 13 | `astropy__astropy-14508` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 413 | $0.326 |
| 14 | `astropy__astropy-14539` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 416 | $0.331 |
| 15 | `astropy__astropy-14598` | 15m–1h | 2 | 2 | 1 | **5/8** | ⚠️ Partial | 547 | $1.474 |
| 16 | `astropy__astropy-14995` | <15m | 3 | 2 | 3 | **8/8** | ✅ Exact | 55 | $0.312 |
| 17 | `astropy__astropy-7166` | <15m | 3 | 2 | 3 | **8/8** | ✅ Exact | 145 | $0.604 |
| 18 | `astropy__astropy-7336` | <15m | 3 | 2 | 3 | **8/8** | ✅ Exact | 83 | $0.361 |
| 19 | `astropy__astropy-7606` | 15m–1h | 2 | 2 | 2 | **6/8** | ⚠️ Partial | 94 | $0.352 |
| 20 | `astropy__astropy-7671` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 785 | $0.492 |
| 21 | `astropy__astropy-8707` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 84 | $0.394 |
| 22 | `astropy__astropy-8872` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 187 | $0.387 |
| | **TOTAL** | | **64/66** | **44/44** | **55/66** | **163/176** | **92.6%** | **5,474 s** | **$11.53** |
| | **AVERAGE** | | | | | **7.4/8** | | **249 s** | **$0.52** |

---

## Dimension Breakdown

| Dimension | Score | Max | % |
|-----------|-------|-----|---|
| Root cause identification | 64 | 66 | **97.0%** |
| Correct file(s) | 44 | 44 | **100%** |
| Correct patch / code change | 55 | 66 | **83.3%** |
| **Overall** | **163** | **176** | **92.6%** |

---

## Token & Cost Breakdown

| # | Instance ID | Input | Cache Write | Cache Read | Output | Eff Weighted Input | Eff Input | **Cost** | Score |
|---|-------------|-------|-------------|------------|--------|--------------------|-----------|---------:|-------|
| 1 | `12907` | 2,131 | 30,555 | 130,811 | 1,538 | 53,406 | 163,497 | **$0.297** | 8/8 |
| 2 | `13033` | 3,254 | 16,973 | 133,478 | 2,535 | 37,818 | 153,705 | **$0.239** | 8/8 |
| 3 | `13236` | 1,471 | 29,232 | 600,599 | 4,535 | 98,071 | 631,302 | **$0.598** | 8/8 |
| 4 | `13398` | 6,210 | 53,735 | 473,428 | 4,746 | 120,722 | 533,373 | **$0.697** | 8/8 |
| 5 | `13453` | 6,660 | 20,717 | 290,438 | 2,395 | 61,600 | 317,815 | **$0.341** | 7/8 |
| 6 | `13579` | 2,947 | 30,727 | 327,086 | 5,706 | 74,065 | 360,760 | **$0.501** | 6/8 |
| 7 | `13977` | 3,256 | 34,130 | 285,049 | 4,665 | 74,424 | 322,435 | **$0.475** | 8/8 |
| 8 | `14096` | 1,222 | 26,933 | 301,371 | 4,799 | 65,025 | 329,526 | **$0.440** | 7/8 |
| 9 | `14182` | 1,357 | 39,765 | 290,420 | 3,213 | 80,105 | 331,542 | **$0.475** | 8/8 |
| 10 | `14309` | 2,409 | 18,743 | 229,002 | 1,696 | 48,738 | 250,154 | **$0.276** | 7/8 |
| 11 | `14365` | 1,695 | 29,961 | 370,038 | 2,868 | 76,150 | 401,694 | **$0.445** | 7/8 |
| 12 | `14369` | 2,394 | 74,331 | 706,010 | 35,852 | 165,909 | 782,735 | **$1.716** | 8/8 |
| 13 | `14508` | 1,863 | 20,531 | 283,103 | 2,194 | 55,837 | 305,497 | **$0.326** | 8/8 |
| 14 | `14539` | 1,512 | 24,769 | 240,945 | 2,163 | 56,568 | 267,226 | **$0.331** | 8/8 |
| 15 | `14598` | 2,099 | 65,498 | 1,183,061 | 18,837 | 202,278 | 1,250,658 | **$1.474** | 5/8 |
| 16 | `14995` | 3,411 | 23,534 | 245,911 | 1,536 | 57,420 | 272,856 | **$0.312** | 8/8 |
| 17 | `7166` | 928 | 38,233 | 352,957 | 7,514 | 84,015 | 392,118 | **$0.604** | 8/8 |
| 18 | `7336` | 1,208 | 25,656 | 248,706 | 3,019 | 58,149 | 275,570 | **$0.361** | 8/8 |
| 19 | `7606` | 1,040 | 20,800 | 319,079 | 2,456 | 58,948 | 340,919 | **$0.352** | 6/8 |
| 20 | `7671` | 1,442 | 29,278 | 265,732 | 7,008 | 64,613 | 296,452 | **$0.492** | 7/8 |
| 21 | `8707` | 840 | 25,915 | 301,708 | 3,231 | 63,405 | 328,463 | **$0.394** | 8/8 |
| 22 | `8872` | 1,169 | 23,986 | 295,209 | 3,554 | 60,673 | 320,364 | **$0.387** | 7/8 |
| | **TOTAL** | **50,518** | **704,002** | **7,874,141** | **126,060** | **1,717,935** | **8,628,661** | **$11.53** | **163/176** |

> **Effective Weighted Input** = Input + (1.25 × Cache Write) + (0.1 × Cache Read)
>
> **Effective Input** = Input + Cache Write + Cache Read
>
> **Average per task:** 249 s · $0.52 · Eff Weighted 78,088 · Eff Input 392,212

---

## Per-Model Token Usage

### Opus (claude-opus-4-6)

| # | Instance ID | Input | Cache Write | Cache Read | Output | **Cost** | Requests |
|---|-------------|-------|-------------|------------|--------|----------:|----------|
| 1 | `12907` | 9 | 30,555 | 130,811 | 1,520 | **$0.294** | 5 |
| 2 | `13033` | 10 | 16,973 | 133,478 | 2,518 | **$0.236** | 6 |
| 3 | `13236` | 29 | 29,232 | 600,599 | 4,514 | **$0.596** | 21 |
| 4 | `13398` | 24 | 53,735 | 473,428 | 4,726 | **$0.691** | 12 |
| 5 | `13453` | 17 | 20,717 | 290,438 | 2,381 | **$0.334** | 11 |
| 6 | `13579` | 20 | 30,727 | 327,086 | 5,679 | **$0.498** | 12 |
| 7 | `13977` | 18 | 34,130 | 285,049 | 4,642 | **$0.472** | 10 |
| 8 | `14096` | 20 | 26,933 | 301,371 | 4,781 | **$0.439** | 12 |
| 9 | `14182` | 20 | 39,765 | 290,420 | 3,195 | **$0.474** | 10 |
| 10 | `14309` | 16 | 18,743 | 229,002 | 1,674 | **$0.274** | 10 |
| 11 | `14365` | 21 | 29,961 | 370,038 | 2,850 | **$0.444** | 13 |
| 12 | `14369` | 27 | 74,331 | 706,010 | 35,836 | **$1.714** | 17 |
| 13 | `14508` | 20 | 20,531 | 283,103 | 2,177 | **$0.324** | 12 |
| 14 | `14539` | 18 | 24,769 | 240,945 | 2,143 | **$0.329** | 10 |
| 15 | `14598` | 37 | 65,498 | 1,183,061 | 18,820 | **$1.472** | 25 |
| 16 | `14995` | 16 | 23,534 | 245,911 | 1,517 | **$0.308** | 10 |
| 17 | `7166` | 20 | 38,233 | 352,957 | 7,495 | **$0.603** | 12 |
| 18 | `7336` | 16 | 25,656 | 248,706 | 3,002 | **$0.360** | 10 |
| 19 | `7606` | 21 | 20,800 | 319,079 | 2,442 | **$0.351** | 13 |
| 20 | `7671` | 19 | 29,278 | 265,732 | 6,991 | **$0.491** | 11 |
| 21 | `8707` | 20 | 25,915 | 301,708 | 3,213 | **$0.393** | 12 |
| 22 | `8872` | 20 | 23,986 | 295,209 | 3,538 | **$0.386** | 12 |
| | **TOTAL** | **438** | **704,002** | **7,874,141** | **125,654** | **$11.481** | **266** |

### Haiku (claude-haiku-4-5)

| # | Instance ID | Input | Cache Write | Cache Read | Output | **Cost** | Requests |
|---|-------------|-------|-------------|------------|--------|----------:|----------|
| 1 | `12907` | 2,122 | 0 | 0 | 18 | **$0.002** | 1 |
| 2 | `13033` | 3,244 | 0 | 0 | 17 | **$0.003** | 1 |
| 3 | `13236` | 1,442 | 0 | 0 | 21 | **$0.002** | 1 |
| 4 | `13398` | 6,186 | 0 | 0 | 20 | **$0.006** | 1 |
| 5 | `13453` | 6,643 | 0 | 0 | 14 | **$0.007** | 1 |
| 6 | `13579` | 2,927 | 0 | 0 | 27 | **$0.003** | 1 |
| 7 | `13977` | 3,238 | 0 | 0 | 23 | **$0.003** | 1 |
| 8 | `14096` | 1,202 | 0 | 0 | 18 | **$0.001** | 1 |
| 9 | `14182` | 1,337 | 0 | 0 | 18 | **$0.001** | 1 |
| 10 | `14309` | 2,393 | 0 | 0 | 22 | **$0.003** | 1 |
| 11 | `14365` | 1,674 | 0 | 0 | 18 | **$0.002** | 1 |
| 12 | `14369` | 2,367 | 0 | 0 | 16 | **$0.002** | 1 |
| 13 | `14508` | 1,843 | 0 | 0 | 17 | **$0.002** | 1 |
| 14 | `14539` | 1,494 | 0 | 0 | 20 | **$0.002** | 1 |
| 15 | `14598` | 2,062 | 0 | 0 | 17 | **$0.002** | 1 |
| 16 | `14995` | 3,395 | 0 | 0 | 19 | **$0.003** | 1 |
| 17 | `7166` | 908 | 0 | 0 | 19 | **$0.001** | 1 |
| 18 | `7336` | 1,192 | 0 | 0 | 17 | **$0.001** | 1 |
| 19 | `7606` | 1,019 | 0 | 0 | 14 | **$0.001** | 1 |
| 20 | `7671` | 1,423 | 0 | 0 | 17 | **$0.002** | 1 |
| 21 | `8707` | 820 | 0 | 0 | 18 | **$0.001** | 1 |
| 22 | `8872` | 1,149 | 0 | 0 | 16 | **$0.001** | 1 |
| | **TOTAL** | **50,080** | **0** | **0** | **406** | **$0.052** | **22** |

### Model Split Summary

| Metric | Opus | Haiku | Total | Opus % |
|--------|------|-------|-------|--------|
| Input tokens | 438 | 50,080 | 50,518 | 0.9% |
| Cache Write tokens | 704,002 | 0 | 704,002 | 100% |
| Cache Read tokens | 7,874,141 | 0 | 7,874,141 | 100% |
| Output tokens | 125,654 | 406 | 126,060 | 99.7% |
| Cost (USD) | $11.481 | $0.052 | $11.533 | 99.5% |
| API requests | 266 | 22 | 288 | 92.4% |

> In the MCP workflow, Haiku makes exactly **one** request per task (22 of 22 tasks) with zero cache activity — a pure triage/routing call. **All** codebase exploration, cache reads, and patch generation are handled by Opus, which accounts for 99.6% of total cost.

---

## Per-Task Answer Comparison

### Task 1 — `12907` — ✅ Exact

**Issue:** `separability_matrix` wrong for nested `CompoundModels`

| | GT | MCP v2 |
|---|---|---|
| File | `separable.py` | `separable.py` |
| Fix | `cright[...] = right` instead of `= 1` | Identical |

---

### Task 2 — `13033` — ✅ Exact

**Issue:** `TimeSeries` misleading exception on required column removal

| | GT | MCP v2 |
|---|---|---|
| File | `core.py` | `core.py` |
| Fix | Add `as_scalar_or_list_str()` helper, use full column lists | Identical helper and error message format |

---

### Task 3 — `13236` — ✅ Exact

**Issue:** Remove auto-transform of structured ndarray into `NdarrayMixin`

| | GT | MCP v2 |
|---|---|---|
| File | `table.py` | `table.py` |
| Fix | Remove 6-line auto-view block | Identical removal, includes full diff |

---

### Task 4 — `13398` — ✅ Exact

**Issue:** Add ITRS ↔ AltAz/HADec topocentric transforms

| | GT | MCP v2 |
|---|---|---|
| Files | 5 files + 1 new file | 6 files identified + 1 new file |
| Fix | ITRS `location` attr, new transform file, CIRS+TETE propagation | Comprehensive description: ITRS/CIRS location attrs, new transform file with rotation matrices + refraction, GCRS↔CIRS/TETE location propagation, earth.py topocentric support |

---

### Task 5 — `13453` — ✅ Near-perfect

**Issue:** HTML writer ignores `formats` argument

| | GT | MCP v2 |
|---|---|---|
| File | `html.py` | `html.py` |
| GT fix | `self.data.cols = cols` + `self.data._set_col_formats()` | Both lines identified, slightly different insertion point |

**-1:** Functionally equivalent but would not apply cleanly as a diff at GT location.

---

### Task 6 — `13579` — ⚠️ Partial

**Issue:** `SlicedLowLevelWCS.world_to_pixel_values` uses hardcoded `1.0` for dropped dimensions

| | GT | MCP v2 |
|---|---|---|
| File | `sliced_wcs.py` | `sliced_wcs.py` |
| GT fix | `sliced_out_world_coords = self._pixel_to_world_values_all(*[0]*len(self._pixel_keep))` | Proposes a two-pass iterative approach — over-engineered |

**-2:** Correctly identifies the hardcoded value problem. But instead of the GT's simple one-line addition, proposes a complex two-pass approach (preliminary world_to_pixel, then recompute). The GT fix works correctly for the test; the MCP answer over-engineers the solution.

---

### Task 7 — `13977` — ✅ Exact

**Issue:** `Quantity.__array_ufunc__` should return `NotImplemented` for duck types

| | GT | MCP v2 |
|---|---|---|
| File | `quantity.py` | `quantity.py` |
| Fix | Wrap entire body in try/except, check other operands' `__array_ufunc__` | Identical approach described: wrap body, check `ignored_ufunc`, return NotImplemented |

---

### Task 8 — `14096` — ✅ Near-perfect

**Issue:** `SkyCoord` subclass property gives misleading `AttributeError`

| | GT | MCP v2 |
|---|---|---|
| File | `sky_coordinate.py` | `sky_coordinate.py` |
| GT fix | `return self.__getattribute__(attr)` (2 lines) | MRO walk to find property, re-invoke `fget` (4 lines) |

**-1:** Functionally equivalent but more complex. GT's `__getattribute__` approach is simpler.

---

### Task 9 — `14182` — ✅ Exact

**Issue:** RST writer needs `header_rows` support

| | GT | MCP v2 |
|---|---|---|
| File | `rst.py` | `rst.py` |
| Fix | Accept `header_rows`, dynamic `idx`, add `read()` | All three changes described with correct code |

---

### Task 10 — `14309` — ✅ Near-perfect

**Issue:** `is_fits` IndexError with empty args

| | GT | MCP v2 |
|---|---|---|
| File | `connect.py` | `connect.py` |
| GT fix | `return filepath.lower().endswith(...)` | `bool(args) and isinstance(args[0], ...)` |

**-1:** Symptom-level guard instead of structural logic fix. Both correct.

---

### Task 11 — `14365` — ✅ Near-perfect

**Issue:** QDP reader fails on lowercase commands

| | GT | MCP v2 |
|---|---|---|
| File | `qdp.py` | `qdp.py` |
| GT fix | `re.IGNORECASE` + `v.upper() == "NO"` | Only `re.IGNORECASE` |

**-1:** Missing `v.upper() == "NO"` for data value parsing.

---

### Task 12 — `14369` — ✅ Exact

**Issue:** CDS unit parser right-recursive division

| | GT | MCP v2 |
|---|---|---|
| File | `cds.py` | `cds.py` |
| Fix | `combined_units DIVISION unit_expression` | Identical grammar rule change |

---

### Task 13 — `14508` — ✅ Exact

**Issue:** `_format_float` uses `.16G` expanding short floats

| | GT | MCP v2 |
|---|---|---|
| File | `card.py` | `card.py` |
| Fix | `str(value).replace("e", "E")` | Identical, includes complete replacement function |

---

### Task 14 — `14539` — ✅ Exact

**Issue:** FITS diff fails for VLA columns with Q format

| | GT | MCP v2 |
|---|---|---|
| File | `diff.py` | `diff.py` |
| Fix | `elif "P" in col.format or "Q" in col.format:` | Identical |

---

### Task 15 — `14598` — ⚠️ Partial

**Issue:** FITS CONTINUE cards lose quotes from double un-escaping

| | GT | MCP v2 |
|---|---|---|
| File | `card.py` | `card.py` |
| GT fix | (1) Add `$` anchor to `_strg_comment_RE`, (2) remove `.replace("''", "'")` in `_split()` | Proposes fixing `_format_long_image` to not split `''` pairs across CONTINUE boundaries |

**-3:** Correctly identifies the escaped-quote loss symptom but misattributes the root cause to the writer (`_format_long_image`) instead of the parser (`_split` double un-escaping + regex over-matching). Proposes a writer-side fix rather than the GT's parser-side fix.

---

### Task 16 — `14995` — ✅ Exact

**Issue:** `_arithmetic_mask` has `operand is None` instead of `operand.mask is None`

| | GT | MCP v2 |
|---|---|---|
| File | `ndarithmetic.py` | `ndarithmetic.py` |
| Fix | `elif operand.mask is None:` | Identical, even identifies the commit that introduced the bug |

---

### Task 17 — `7166` — ✅ Exact

**Issue:** `InheritDocstrings` doesn't work for properties

| | GT | MCP v2 |
|---|---|---|
| File | `misc.py` | `misc.py` |
| GT fix | `inspect.isdatadescriptor(val)` | `isinstance(val, property)` — functionally equivalent |

---

### Task 18 — `7336` — ✅ Exact

**Issue:** `@quantity_input` fails with `-> None` annotation

| | GT | MCP v2 |
|---|---|---|
| File | `decorators.py` | `decorators.py` |
| Fix | `not in (inspect.Signature.empty, None)` | Identical condition |

---

### Task 19 — `7606` — ⚠️ Partial

**Issue:** `Unit.__eq__` returns `False` instead of `NotImplemented`

| | GT | MCP v2 |
|---|---|---|
| Files | `core.py` — 2 locations: `UnitBase.__eq__` + `UnrecognizedUnit.__eq__` | Only `UnrecognizedUnit.__eq__` |

**-2:** Correctly fixes `UnrecognizedUnit.__eq__` (try/except + NotImplemented) but misses the `UnitBase.__eq__` change (`return False` → `return NotImplemented`).

---

### Task 20 — `7671` — ✅ Near-perfect

**Issue:** `minversion` fails with pre-release version suffixes

| | GT | MCP v2 |
|---|---|---|
| File | `introspection.py` | `introspection.py` |
| GT fix | PEP440 regex on `version` only | `re.match(r'([0-9.]+)', ...)` on both `have_version` and `version` |

**-1:** Different regex, strips both versions (GT only strips `version`). Functionally equivalent.

---

### Task 21 — `8707` — ✅ Exact

**Issue:** `Card.fromstring` / `Header.fromstring` don't accept bytes

| | GT | MCP v2 |
|---|---|---|
| Files | `card.py`, `header.py` | `card.py`, `header.py` |
| Fix | Card: decode latin1. Header: bytes-aware CONTINUE/END/sep/empty | Both changes with correct code and correct encoding (latin1) |

---

### Task 22 — `8872` — ✅ Near-perfect

**Issue:** `np.float16` quantities upgraded to float64

| | GT | MCP v2 |
|---|---|---|
| File | `quantity.py` | `quantity.py` |
| GT fix | `value.dtype.kind in 'iu'` | `np.issubdtype(value.dtype, np.inexact)` — functionally equivalent |

**-1:** Different predicate, same effect: preserve all float/complex dtypes including float16.

---

## Grade Distribution

| Grade | Count | Tasks |
|-------|-------|-------|
| ✅ Exact (8/8) | 13 | 1, 2, 3, 4, 7, 9, 12, 13, 14, 16, 17, 18, 21 |
| ✅ Near-perfect (7/8) | 6 | 5, 8, 10, 11, 20, 22 |
| ⚠️ Partial (5–6/8) | 3 | 6, 15, 19 |
| ❌ Fail (≤4/8) | 0 | — |

**Exact + Near-perfect: 19/22 (86.4%)**
