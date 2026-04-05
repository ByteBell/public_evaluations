# Claude Opus 4.6 v3-Raw — SWE-Bench Evaluation Report

**Dataset:** `princeton-nlp/SWE-bench_Verified` — `astropy/astropy`
**Evaluated:** 22 tasks from `astropy_tasks.json`
**Date:** 2026-03-31
**Judge:** Claude Code (claude-opus-4-6)
**Ground truth source:** `results_swe_bench/astropy_tasks.json`
**Raw responses:** `results_swe_bench/claude-opus-4.6-v3-raw/*/answer.json`
**Mode:** Claude Code direct repo access (no MCP knowledge graph)

---

## Scoring Rubric

| Dimension | Weight | What is graded |
|-----------|--------|----------------|
| Root cause identification | 3 pts | Did the model correctly diagnose *why* the bug exists? |
| Correct file(s) | 2 pts | Did it identify the right file(s) to change? |
| Correct patch / code change | 3 pts | Does the proposed code change match the ground truth or produce functionally equivalent output? |

**Grade tiers:** ✅ Exact (8/8) · ✅ Near-perfect (7/8) · ⚠️ Partial (5–6/8) · ❌ Fail (≤4/8)

---

## Combined Per-Question: Score · Time · Cost

| # | Instance ID | Difficulty | RC | Files | Patch | **Score** | Grade | Time (s) | Cost (USD) |
|---|-------------|------------|----|-------|-------|-----------|-------|----------|------------|
| 1 | `astropy__astropy-12907` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 259 | $0.400 |
| 2 | `astropy__astropy-13033` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 191 | $0.669 |
| 3 | `astropy__astropy-13236` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 422 | $1.395 |
| 4 | `astropy__astropy-13398` | 1–4h | 3 | 2 | 3 | **8/8** | ✅ Exact | 612 | $1.772 |
| 5 | `astropy__astropy-13453` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 123 | $0.635 |
| 6 | `astropy__astropy-13579` | 1–4h | 3 | 2 | 3 | **8/8** | ✅ Exact | 223 | $0.741 |
| 7 | `astropy__astropy-13977` | 15m–1h | 3 | 2 | 1 | **6/8** | ⚠️ Partial | 212 | $0.787 |
| 8 | `astropy__astropy-14096` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 175 | $0.619 |
| 9 | `astropy__astropy-14182` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 232 | $0.565 |
| 10 | `astropy__astropy-14309` | <15m | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 171 | $0.153 |
| 11 | `astropy__astropy-14365` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 141 | $0.496 |
| 12 | `astropy__astropy-14369` | 1–4h | 3 | 2 | 3 | **8/8** | ✅ Exact | 475 | $1.492 |
| 13 | `astropy__astropy-14508` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 100 | $0.385 |
| 14 | `astropy__astropy-14539` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 123 | $0.511 |
| 15 | `astropy__astropy-14598` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 600 | $1.768 |
| 16 | `astropy__astropy-14995` | <15m | 3 | 2 | 3 | **8/8** | ✅ Exact | 153 | $0.510 |
| 17 | `astropy__astropy-7166` | <15m | 3 | 2 | 3 | **8/8** | ✅ Exact | 151 | $0.393 |
| 18 | `astropy__astropy-7336` | <15m | 3 | 2 | 3 | **8/8** | ✅ Exact | 291 | $0.307 |
| 19 | `astropy__astropy-7606` | 15m–1h | 1 | 2 | 0 | **3/8** | ❌ Fail | 181 | $0.392 |
| 20 | `astropy__astropy-7671` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 202 | $0.682 |
| 21 | `astropy__astropy-8707` | 15m–1h | 3 | 2 | 1 | **6/8** | ⚠️ Partial | 372 | $1.135 |
| 22 | `astropy__astropy-8872` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 119 | $0.353 |
| | **TOTAL** | | **64/66** | **44/44** | **54/66** | **162/176** | **92.0%** | **5,528 s** | **$16.16** |
| | **AVERAGE** | | | | | **7.4/8** | | **251 s** | **$0.73** |

---

## Dimension Breakdown

| Dimension | Score | Max | % |
|-----------|-------|-----|---|
| Root cause identification | 64 | 66 | **97.0%** |
| Correct file(s) | 44 | 44 | **100%** |
| Correct patch / code change | 54 | 66 | **81.8%** |
| **Overall** | **162** | **176** | **92.0%** |

---

## Token & Cost Breakdown

| # | Instance ID | Input | Cache Write | Cache Read | Output | Eff Weighted Input | Eff Input | **Cost** | Score |
|---|-------------|-------|-------------|------------|--------|--------------------|-----------|---------:|-------|
| 1 | `12907` | 1,221 | 64,472 | 596,225 | 7,764 | 141,434 | 661,918 | **$0.400** | 8/8 |
| 2 | `13033` | 3,215 | 26,150 | 427,022 | 11,575 | 78,605 | 456,387 | **$0.669** | 8/8 |
| 3 | `13236` | 6,774 | 78,105 | 1,286,732 | 26,238 | 233,079 | 1,371,611 | **$1.395** | 8/8 |
| 4 | `13398` | 6,339 | 110,391 | 1,725,316 | 35,047 | 316,859 | 1,842,046 | **$1.772** | 8/8 |
| 5 | `13453` | 6,598 | 24,324 | 691,323 | 5,240 | 106,135 | 722,245 | **$0.635** | 8/8 |
| 6 | `13579` | 2,981 | 33,322 | 394,326 | 13,334 | 84,066 | 430,629 | **$0.741** | 8/8 |
| 7 | `13977` | 3,301 | 30,819 | 717,343 | 9,324 | 113,559 | 751,463 | **$0.787** | 6/8 |
| 8 | `14096` | 1,293 | 55,280 | 631,445 | 8,982 | 133,538 | 688,018 | **$0.619** | 7/8 |
| 9 | `14182` | 4,568 | 72,724 | 763,280 | 10,494 | 171,801 | 840,572 | **$0.565** | 8/8 |
| 10 | `14309` | 2,438 | 11,740 | 72,880 | 1,655 | 24,401 | 87,058 | **$0.153** | 7/8 |
| 11 | `14365` | 1,724 | 27,761 | 275,153 | 7,338 | 63,941 | 304,638 | **$0.496** | 7/8 |
| 12 | `14369` | 2,428 | 51,941 | 762,750 | 31,353 | 143,629 | 817,119 | **$1.492** | 8/8 |
| 13 | `14508` | 2,890 | 45,807 | 468,976 | 5,353 | 107,046 | 517,673 | **$0.385** | 8/8 |
| 14 | `14539` | 1,552 | 21,935 | 436,492 | 6,156 | 72,620 | 459,979 | **$0.511** | 8/8 |
| 15 | `14598` | 2,189 | 55,668 | 1,207,244 | 32,586 | 192,498 | 1,265,101 | **$1.768** | 8/8 |
| 16 | `14995` | 3,566 | 53,401 | 617,511 | 6,820 | 132,068 | 674,478 | **$0.510** | 8/8 |
| 17 | `7166` | 4,320 | 55,079 | 484,355 | 7,370 | 121,604 | 543,754 | **$0.393** | 8/8 |
| 18 | `7336` | 1,244 | 14,944 | 272,887 | 3,052 | 47,213 | 289,075 | **$0.307** | 8/8 |
| 19 | `7606` | 568 | 42,044 | 431,878 | 6,891 | 96,311 | 474,490 | **$0.392** | 3/8 |
| 20 | `7671` | 1,475 | 38,816 | 245,557 | 12,617 | 74,551 | 285,848 | **$0.682** | 7/8 |
| 21 | `8707` | 3,112 | 98,341 | 1,943,124 | 20,747 | 320,351 | 2,044,577 | **$1.135** | 6/8 |
| 22 | `8872` | 1,242 | 44,383 | 343,002 | 7,003 | 91,021 | 388,627 | **$0.353** | 7/8 |
| | **TOTAL** | **65,038** | **1,057,447** | **14,794,821** | **276,939** | **2,866,329** | **15,917,306** | **$16.16** | **162/176** |

> **Effective Weighted Input** = Input + (1.25 × Cache Write) + (0.1 × Cache Read)
>
> **Effective Input** = Input + Cache Write + Cache Read
>
> **Average per task:** 251 s · $0.73 · Eff Weighted 130,288 · Eff Input 723,514

---

## Per-Model Token Usage

### Opus (claude-opus-4-6)

| # | Instance ID | Input | Cache Write | Cache Read | Output | **Cost** | Requests |
|---|-------------|-------|-------------|------------|--------|----------:|----------|
| 1 | `12907` | 10 | 20,414 | 174,671 | 2,405 | **$0.275** | 8 |
| 2 | `13033` | 18 | 26,150 | 427,022 | 11,558 | **$0.666** | 16 |
| 3 | `13236` | 30 | 44,710 | 943,499 | 21,489 | **$1.289** | 28 |
| 4 | `13398` | 27 | 73,497 | 1,143,306 | 22,737 | **$1.600** | 21 |
| 5 | `13453` | 26 | 24,324 | 691,323 | 5,223 | **$0.628** | 24 |
| 6 | `13579` | 17 | 33,322 | 394,326 | 13,308 | **$0.738** | 15 |
| 7 | `13977` | 26 | 30,819 | 717,343 | 9,301 | **$0.784** | 24 |
| 8 | `14096` | 22 | 25,075 | 444,207 | 6,849 | **$0.550** | 18 |
| 9 | `14182` | 15 | 20,798 | 310,165 | 5,638 | **$0.426** | 13 |
| 10 | `14309` | 6 | 11,740 | 72,880 | 1,634 | **$0.151** | 4 |
| 11 | `14365` | 13 | 27,761 | 275,153 | 7,323 | **$0.494** | 11 |
| 12 | `14369` | 22 | 51,941 | 762,750 | 31,338 | **$1.490** | 20 |
| 13 | `14508` | 15 | 14,567 | 282,574 | 3,241 | **$0.313** | 13 |
| 14 | `14539` | 21 | 21,935 | 436,492 | 6,138 | **$0.509** | 19 |
| 15 | `14598` | 101 | 55,668 | 1,207,244 | 32,568 | **$1.766** | 30 |
| 16 | `14995` | 19 | 22,067 | 376,499 | 4,156 | **$0.430** | 15 |
| 17 | `7166` | 11 | 17,947 | 142,893 | 4,364 | **$0.293** | 7 |
| 18 | `7336` | 15 | 14,944 | 272,887 | 3,035 | **$0.306** | 13 |
| 19 | `7606` | 12 | 14,801 | 207,495 | 5,200 | **$0.326** | 10 |
| 20 | `7671` | 13 | 38,816 | 245,557 | 12,600 | **$0.680** | 11 |
| 21 | `8707` | 57 | 37,311 | 793,588 | 10,326 | **$0.888** | 22 |
| 22 | `8872` | 10 | 14,237 | 161,187 | 4,555 | **$0.284** | 8 |
| | **TOTAL** | **506** | **642,844** | **10,483,061** | **224,986** | **$14.886** | **350** |

### Haiku (claude-haiku-4-5)

| # | Instance ID | Input | Cache Write | Cache Read | Output | **Cost** | Requests |
|---|-------------|-------|-------------|------------|--------|----------:|----------|
| 1 | `12907` | 1,211 | 44,058 | 421,554 | 5,359 | **$0.125** | 18 |
| 2 | `13033` | 3,197 | 0 | 0 | 17 | **$0.003** | 1 |
| 3 | `13236` | 6,744 | 33,395 | 343,233 | 4,749 | **$0.107** | 15 |
| 4 | `13398` | 6,312 | 36,894 | 582,010 | 12,310 | **$0.172** | 18 |
| 5 | `13453` | 6,572 | 0 | 0 | 17 | **$0.007** | 1 |
| 6 | `13579` | 2,964 | 0 | 0 | 26 | **$0.003** | 1 |
| 7 | `13977` | 3,275 | 0 | 0 | 23 | **$0.003** | 1 |
| 8 | `14096` | 1,271 | 30,205 | 187,238 | 2,133 | **$0.068** | 9 |
| 9 | `14182` | 4,553 | 51,926 | 453,115 | 4,856 | **$0.139** | 15 |
| 10 | `14309` | 2,432 | 0 | 0 | 21 | **$0.003** | 1 |
| 11 | `14365` | 1,711 | 0 | 0 | 15 | **$0.002** | 1 |
| 12 | `14369` | 2,406 | 0 | 0 | 15 | **$0.002** | 1 |
| 13 | `14508` | 2,875 | 31,240 | 186,402 | 2,112 | **$0.071** | 9 |
| 14 | `14539` | 1,531 | 0 | 0 | 18 | **$0.002** | 1 |
| 15 | `14598` | 2,088 | 0 | 0 | 18 | **$0.002** | 1 |
| 16 | `14995` | 3,547 | 31,334 | 241,012 | 2,664 | **$0.080** | 11 |
| 17 | `7166` | 4,309 | 37,132 | 341,462 | 3,006 | **$0.100** | 13 |
| 18 | `7336` | 1,229 | 0 | 0 | 17 | **$0.001** | 1 |
| 19 | `7606` | 556 | 27,243 | 224,383 | 1,691 | **$0.066** | 11 |
| 20 | `7671` | 1,462 | 0 | 0 | 17 | **$0.002** | 1 |
| 21 | `8707` | 3,055 | 61,030 | 1,149,536 | 10,421 | **$0.246** | 39 |
| 22 | `8872` | 1,232 | 30,146 | 181,815 | 2,448 | **$0.069** | 9 |
| | **TOTAL** | **64,532** | **414,603** | **4,311,760** | **51,953** | **$1.274** | **178** |

### Model Split Summary

| Metric | Opus | Haiku | Total | Opus % |
|--------|------|-------|-------|--------|
| Input tokens | 506 | 64,532 | 65,038 | 0.8% |
| Cache Write tokens | 642,844 | 414,603 | 1,057,447 | 60.8% |
| Cache Read tokens | 10,483,061 | 4,311,760 | 14,794,821 | 70.9% |
| Output tokens | 224,986 | 51,953 | 276,939 | 81.2% |
| Cost (USD) | $14.886 | $1.274 | $16.160 | 92.1% |
| API requests | 350 | 178 | 528 | 66.3% |

> Opus dominates cost (92.1%) and output generation (81.2%). Haiku handles the bulk of initial input tokens (99.2%) — acting as a triage/routing layer — while Opus does the heavy reasoning and patch generation.

---

## Per-Task Answer Comparison

### Task 1 — `12907` — ✅ Exact

**Issue:** `separability_matrix` wrong for nested `CompoundModels`

| | GT | Raw |
|---|---|---|
| File | `separable.py` | `separable.py` |
| Fix | `cright[...] = right` instead of `= 1` | Identical |

---

### Task 2 — `13033` — ✅ Exact

**Issue:** `TimeSeries` misleading exception on required column removal

| | GT | Raw |
|---|---|---|
| File | `core.py` | `core.py` |
| Fix | Add `as_scalar_or_list_str()` helper, use full column lists in error message | Identical helper logic, f-string vs `.format()` — same output |

---

### Task 3 — `13236` — ✅ Exact

**Issue:** Remove auto-transform of structured ndarray into `NdarrayMixin`

| | GT | Raw |
|---|---|---|
| File | `table.py` | `table.py` |
| Fix | Remove 6-line auto-view block | Identical |

---

### Task 4 — `13398` — ✅ Exact

**Issue:** Add ITRS ↔ AltAz/HADec topocentric transforms

| | GT | Raw |
|---|---|---|
| Files | 5 files + 1 new file | Same 5 files + new file |
| Fix | ITRS `location` attr, new transform file, CIRS+TETE propagation | Identical: ITRS location attr, full transform file, CIRS+TETE location propagation |

---

### Task 5 — `13453` — ✅ Exact

**Issue:** HTML writer ignores `formats` argument

| | GT | Raw |
|---|---|---|
| File | `html.py` | `html.py` |
| Fix | `self.data.cols = cols` + `self.data._set_col_formats()` | Identical |

---

### Task 6 — `13579` — ✅ Exact

**Issue:** `SlicedLowLevelWCS.world_to_pixel_values` uses hardcoded `1.0` for dropped dimensions

| | GT | Raw |
|---|---|---|
| File | `sliced_wcs.py` | `sliced_wcs.py` |
| GT fix | `sliced_out_world_coords = self._pixel_to_world_values_all(*[0]*len(self._pixel_keep))` then use for dropped dims | Identical logic, variable named `world_at_slice` |

---

### Task 7 — `13977` — ⚠️ Partial

**Issue:** `Quantity.__array_ufunc__` should return `NotImplemented` for duck types

| | GT | Raw |
|---|---|---|
| File | `quantity.py` | `quantity.py` |
| GT fix | Wrap **entire** `__array_ufunc__` body in try/except; check other operands' `__array_ufunc__` before returning NotImplemented | Only wraps input conversion loop (3 lines) in try/except |

**-2:** Misses errors from `converters_and_unit()` and `check_output()`. Doesn't check other operands' `__array_ufunc__`.

---

### Task 8 — `14096` — ✅ Near-perfect

**Issue:** `SkyCoord` subclass property gives misleading `AttributeError`

| | GT | Raw |
|---|---|---|
| File | `sky_coordinate.py` | `sky_coordinate.py` |
| GT fix | Replace `raise AttributeError(...)` with `return self.__getattribute__(attr)` (2 lines) | MRO walk to detect descriptor and re-invoke `__get__` (10 lines) |

**-1:** Functionally equivalent but over-engineered. GT's `__getattribute__` is simpler.

---

### Task 9 — `14182` — ✅ Exact

**Issue:** RST writer needs `header_rows` support

| | GT | Raw |
|---|---|---|
| File | `rst.py` | `rst.py` |
| Fix | Remove `start_line=3`, accept `header_rows`, dynamic `idx`, add `read()` | Identical in every change |

---

### Task 10 — `14309` — ✅ Near-perfect

**Issue:** `is_fits` IndexError with empty args

| | GT | Raw |
|---|---|---|
| File | `connect.py` | `connect.py` |
| GT fix | `return filepath.lower().endswith(...)` — make elif always return | `bool(args) and isinstance(args[0], ...)` — guard the downstream crash |

**-1:** Patches symptom instead of fixing the logic flow. Both correct for the test.

---

### Task 11 — `14365` — ✅ Near-perfect

**Issue:** QDP reader fails on lowercase commands

| | GT | Raw |
|---|---|---|
| File | `qdp.py` | `qdp.py` |
| GT fix | `re.IGNORECASE` + `v.upper() == "NO"` in data parsing | Only `re.IGNORECASE` |

**-1:** Missing `v.upper() == "NO"` for data line parsing.

---

### Task 12 — `14369` — ✅ Exact

**Issue:** CDS unit parser right-recursive division (`a/b/c` → `a*c/b`)

| | GT | Raw |
|---|---|---|
| File | `cds.py` | `cds.py` |
| Fix | `unit_expression DIVISION combined_units` → `combined_units DIVISION unit_expression` | Identical grammar rule change |

---

### Task 13 — `14508` — ✅ Exact

**Issue:** `_format_float` uses `.16G` expanding short floats

| | GT | Raw |
|---|---|---|
| File | `card.py` | `card.py` |
| Fix | Replace `f"{value:.16G}"` with `str(value).replace("e", "E")` | Identical |

---

### Task 14 — `14539` — ✅ Exact

**Issue:** FITS diff fails for VLA columns with Q format descriptor

| | GT | Raw |
|---|---|---|
| File | `diff.py` | `diff.py` |
| Fix | `elif "P" in col.format or "Q" in col.format:` | Identical |

---

### Task 15 — `14598` — ✅ Exact

**Issue:** FITS CONTINUE cards lose quotes from double un-escaping

| | GT | Raw |
|---|---|---|
| File | `card.py` | `card.py` |
| Fix | (1) Add `$` anchor to `_strg_comment_RE`, (2) remove `.replace("''", "'")` in `_split()` | Both changes identical |

---

### Task 16 — `14995` — ✅ Exact

**Issue:** `_arithmetic_mask` has `operand is None` instead of `operand.mask is None`

| | GT | Raw |
|---|---|---|
| File | `ndarithmetic.py` | `ndarithmetic.py` |
| Fix | `elif operand.mask is None:` | Identical |

---

### Task 17 — `7166` — ✅ Exact

**Issue:** `InheritDocstrings` doesn't work for properties

| | GT | Raw |
|---|---|---|
| File | `misc.py` | `misc.py` |
| Fix | Add `inspect.isdatadescriptor(val)` alongside `inspect.isfunction(val)` | Identical |

---

### Task 18 — `7336` — ✅ Exact

**Issue:** `@quantity_input` fails with `-> None` annotation

| | GT | Raw |
|---|---|---|
| File | `decorators.py` | `decorators.py` |
| GT fix | `not in (inspect.Signature.empty, None)` | `is not empty and is not None` — functionally identical |

---

### Task 19 — `7606` — ❌ Fail

**Issue:** `Unit.__eq__` returns `False` instead of `NotImplemented`

| | GT | Raw |
|---|---|---|
| Files | `core.py` (2 locations) | `core.py` (file only — no patch) |
| GT fix | `return NotImplemented` in both `UnitBase.__eq__` and `UnrecognizedUnit.__eq__` | No fix proposed |

**-5:** Only returned filename. No root cause, no patch.

---

### Task 20 — `7671` — ✅ Near-perfect

**Issue:** `minversion` fails with `TypeError` when version strings contain pre-release suffixes (`dev`, `rc1`)

| | GT | Raw |
|---|---|---|
| File | `introspection.py` | `introspection.py` |
| GT fix | PEP440 regex to extract numeric part from `version` only | `re.sub(r'(a\|b\|rc\|dev)\d*', '', ...)` on both `have_version` and `version` |

**-1:** Different regex approach. Strips both versions (GT only strips `version`). Functionally equivalent for all test cases.

---

### Task 21 — `8707` — ⚠️ Partial

**Issue:** `Card.fromstring` / `Header.fromstring` don't accept bytes

| | GT | Raw |
|---|---|---|
| Files | `card.py`, `header.py` | `card.py`, `header.py` |
| GT fix | `Card.fromstring`: decode latin1. `Header.fromstring`: bytes-aware refactor (CONTINUE/END as bytes, sep encode) | Description only — says to add decode('ascii'), no actual diff |

**-2:** Concept correct but no actual patch. Missing Header.fromstring restructuring. Wrong encoding (ascii vs latin1).

---

### Task 22 — `8872` — ✅ Near-perfect

**Issue:** `np.float16` quantities upgraded to float64

| | GT | Raw |
|---|---|---|
| File | `quantity.py` | `quantity.py` |
| GT fix | `value.dtype.kind in 'iu'` (cast only integers) | `value.dtype.kind in ('f', 'c')` (preserve floats/complex) — functionally equivalent |

**-1:** Equivalent logic but retains more complex condition structure that GT simplifies away.

---

## Grade Distribution

| Grade | Count | Tasks |
|-------|-------|-------|
| ✅ Exact (8/8) | 14 | 1, 2, 3, 4, 5, 6, 9, 12, 13, 14, 15, 16, 17, 18 |
| ✅ Near-perfect (7/8) | 5 | 8, 10, 11, 20, 22 |
| ⚠️ Partial (5–6/8) | 2 | 7, 21 |
| ❌ Fail (≤4/8) | 1 | 19 |

**Exact + Near-perfect: 19/22 (86.4%)**
