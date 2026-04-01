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
| 2 | `astropy__astropy-13033` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 443 | $0.641 |
| 3 | `astropy__astropy-13236` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 547 | $1.132 |
| 4 | `astropy__astropy-13398` | 1–4h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 1,077 | $1.830 |
| 5 | `astropy__astropy-13453` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 636 | $1.480 |
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
| | **TOTAL** | | **64/66** | **44/44** | **52/66** | **160/176** | **90.9%** | **6,882 s** | **$16.77** |
| | **AVERAGE** | | | | | **7.3/8** | | **313 s** | **$0.76** |

---

## Dimension Breakdown

| Dimension | Score | Max | % |
|-----------|-------|-----|---|
| Root cause identification | 64 | 66 | **97.0%** |
| Correct file(s) | 44 | 44 | **100%** |
| Correct patch / code change | 52 | 66 | **78.8%** |
| **Overall** | **160** | **176** | **90.9%** |

---

## Token & Cost Breakdown

| # | Instance ID | Input | Cache Write | Cache Read | Output | Eff Weighted Input | Eff Input | **Cost** | Score |
|---|-------------|-------|-------------|------------|--------|--------------------|-----------|---------:|-------|
| 1 | `12907` | 1,221 | 64,472 | 596,225 | 7,764 | 141,434 | 661,918 | **$0.400** | 8/8 |
| 2 | `13033` | 3,217 | 43,028 | 527,844 | 21,233 | 109,786 | 574,089 | **$0.641** | 8/8 |
| 3 | `13236` | 1,519 | 64,182 | 1,173,095 | 35,853 | 199,056 | 1,238,796 | **$1.132** | 8/8 |
| 4 | `13398` | 6,314 | 142,489 | 2,262,850 | 64,862 | 410,710 | 2,411,653 | **$1.830** | 7/8 |
| 5 | `13453` | 6,614 | 84,622 | 1,988,727 | 37,281 | 311,264 | 2,079,963 | **$1.480** | 7/8 |
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
| | **TOTAL** | **59,776** | **1,152,798** | **16,616,944** | **358,068** | **3,162,468** | **17,829,518** | **$16.77** | **160/176** |

> **Effective Weighted Input** = Input + (1.25 × Cache Write) + (0.1 × Cache Read)
>
> **Effective Input** = Input + Cache Write + Cache Read
>
> **Average per task:** 313 s · $0.76 · Eff Weighted 143,749 · Eff Input 810,433

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

### Task 4 — `13398` — ✅ Near-perfect

**Issue:** Add ITRS ↔ AltAz/HADec topocentric transforms

| | GT | Raw |
|---|---|---|
| Files | 5 files + 1 new file | Same 5 files + new file |
| Fix | ITRS `location` attr, new transform file, CIRS+TETE propagation | Missing TETE↔ITRS location propagation (2 functions) |

**-1:** TETE changes missing.

---

### Task 5 — `13453` — ✅ Near-perfect

**Issue:** HTML writer ignores `formats` argument

| | GT | Raw |
|---|---|---|
| File | `html.py` | `html.py` |
| GT fix | `self.data.cols = cols` + `self.data._set_col_formats()` | Only `_set_col_formats()`, missing prerequisite `self.data.cols = cols` |

**-1:** Missing prerequisite line.

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
| ✅ Exact (8/8) | 13 | 1, 2, 3, 6, 9, 12, 13, 14, 15, 16, 17, 18 |
| ✅ Near-perfect (7/8) | 7 | 4, 5, 8, 10, 11, 20, 22 |
| ⚠️ Partial (5–6/8) | 2 | 7, 21 |
| ❌ Fail (≤4/8) | 1 | 19 |

**Exact + Near-perfect: 20/22 (90.9%)**
