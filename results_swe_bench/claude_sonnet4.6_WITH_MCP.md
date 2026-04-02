# Claude Sonnet 4.6 WITH MCP — SWE-Bench Evaluation Report

**Dataset:** `princeton-nlp/SWE-bench_Verified` — `astropy/astropy`
**Evaluated:** 22 tasks from `astropy_tasks.json`
**Date:** 2026-04-02
**Judge:** Claude Code (claude-sonnet-4-6)
**Ground truth source:** `results_swe_bench/astropy_tasks.json`
**Raw responses:** `results_swe_bench/auto_run_on_claude_sonnet_4_6_mcp/*/answer.json`
**Mode:** Claude Code with ByteBell MCP knowledge graph (no direct repo access)

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
| 1 | `astropy__astropy-12907` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 369 | $0.996 |
| 2 | `astropy__astropy-13033` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 331 | $0.497 |
| 3 | `astropy__astropy-13236` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 355 | $0.584 |
| 4 | `astropy__astropy-13398` | 1–4h | 3 | 2 | 3 | **8/8** | ✅ Exact | 51 | $0.128 |
| 5 | `astropy__astropy-13453` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 121 | $0.357 |
| 6 | `astropy__astropy-13579` | 1–4h | 3 | 2 | 3 | **8/8** | ✅ Exact | 89 | $0.203 |
| 7 | `astropy__astropy-13977` | 15m–1h | 3 | 2 | 1 | **6/8** | ⚠️ Partial | 66 | $0.147 |
| 8 | `astropy__astropy-14096` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 56 | $0.156 |
| 9 | `astropy__astropy-14182` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 142 | $0.299 |
| 10 | `astropy__astropy-14309` | <15m | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 45 | $0.121 |
| 11 | `astropy__astropy-14365` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 80 | $0.158 |
| 12 | `astropy__astropy-14369` | 1–4h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 80 | $0.203 |
| 13 | `astropy__astropy-14508` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 202 | $0.358 |
| 14 | `astropy__astropy-14539` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 269 | $0.432 |
| 15 | `astropy__astropy-14598` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 385 | $0.575 |
| 16 | `astropy__astropy-14995` | <15m | 3 | 2 | 3 | **8/8** | ✅ Exact | 100 | $0.254 |
| 17 | `astropy__astropy-7166` | <15m | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 63 | $0.154 |
| 18 | `astropy__astropy-7336` | <15m | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 89 | $0.211 |
| 19 | `astropy__astropy-7606` | 15m–1h | 2 | 2 | 1 | **5/8** | ⚠️ Partial | 65 | $0.168 |
| 20 | `astropy__astropy-7671` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 41 | $0.085 |
| 21 | `astropy__astropy-8707` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 172 | $0.258 |
| 22 | `astropy__astropy-8872` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 103 | $0.255 |
| | **TOTAL** | | **65/66** | **44/44** | **49/66** | **158/176** | **89.8%** | **3,273 s** | **$6.60** |
| | **AVERAGE** | | | | | **7.2/8** | | **149 s** | **$0.30** |

---

## Dimension Breakdown

| Dimension | Score | Max | % |
|-----------|-------|-----|---|
| Root cause identification | 65 | 66 | **98.5%** |
| Correct file(s) | 44 | 44 | **100%** |
| Correct patch / code change | 49 | 66 | **74.2%** |
| **Overall** | **158** | **176** | **89.8%** |

---

## Token & Cost Breakdown

| # | Instance ID | Input | Cache Write | Cache Read | Output | Eff Weighted Input | Eff Input | **Cost** | Score |
|---|-------------|-------|-------------|------------|--------|--------------------|-----------|---------:|-------|
| 1 | `12907` | 32 | 76,249 | 1,200,534 | 23,347 | 215,397 | 1,276,815 | **$0.996** | 8/8 |
| 2 | `13033` | 9 | 28,998 | 97,811 | 23,925 | 46,038 | 126,818 | **$0.497** | 7/8 |
| 3 | `13236` | 15 | 35,328 | 233,133 | 25,458 | 67,488 | 268,476 | **$0.584** | 8/8 |
| 4 | `13398` | 9 | 17,570 | 102,078 | 2,107 | 32,179 | 119,657 | **$0.128** | 8/8 |
| 5 | `13453` | 20 | 37,640 | 462,602 | 5,144 | 93,330 | 500,262 | **$0.357** | 7/8 |
| 6 | `13579` | 9 | 24,600 | 138,427 | 4,623 | 44,602 | 163,036 | **$0.203** | 8/8 |
| 7 | `13977` | 10 | 17,111 | 122,603 | 3,080 | 33,659 | 139,724 | **$0.147** | 6/8 |
| 8 | `14096` | 12 | 19,941 | 146,438 | 2,456 | 39,582 | 166,391 | **$0.156** | 7/8 |
| 9 | `14182` | 19 | 23,503 | 266,830 | 8,691 | 56,081 | 290,352 | **$0.299** | 8/8 |
| 10 | `14309` | 8 | 18,245 | 82,946 | 1,828 | 31,109 | 101,199 | **$0.121** | 7/8 |
| 11 | `14365` | 12 | 17,045 | 125,708 | 3,752 | 33,889 | 142,765 | **$0.158** | 7/8 |
| 12 | `14369` | 14 | 25,761 | 199,159 | 3,132 | 52,131 | 224,934 | **$0.203** | 7/8 |
| 13 | `14508` | 10 | 29,614 | 154,942 | 13,376 | 52,522 | 184,566 | **$0.358** | 7/8 |
| 14 | `14539` | 15 | 21,127 | 198,201 | 19,543 | 46,244 | 219,343 | **$0.432** | 8/8 |
| 15 | `14598` | 17 | 33,622 | 269,866 | 24,507 | 69,031 | 303,505 | **$0.575** | 7/8 |
| 16 | `14995` | 18 | 24,727 | 314,847 | 4,450 | 62,411 | 339,592 | **$0.254** | 8/8 |
| 17 | `7166` | 11 | 17,397 | 157,323 | 2,767 | 37,490 | 174,731 | **$0.154** | 7/8 |
| 18 | `7336` | 14 | 24,399 | 185,418 | 4,233 | 49,055 | 209,831 | **$0.211** | 7/8 |
| 19 | `7606` | 10 | 21,944 | 130,042 | 3,080 | 40,444 | 151,996 | **$0.168** | 5/8 |
| 20 | `7671` | 8 | 9,431 | 67,645 | 1,948 | 18,561 | 77,084 | **$0.085** | 7/8 |
| 21 | `8707` | 9 | 14,432 | 89,928 | 11,762 | 27,042 | 104,369 | **$0.258** | 7/8 |
| 22 | `8872` | 17 | 22,831 | 252,391 | 6,238 | 53,795 | 275,239 | **$0.255** | 7/8 |
| | **TOTAL** | **298** | **561,515** | **4,998,872** | **199,447** | **1,202,079** | **5,560,685** | **$6.598** | **158/176** |

> **Effective Weighted Input** = Input + (1.25 × Cache Write) + (0.1 × Cache Read)
>
> **Effective Input** = Input + Cache Write + Cache Read
>
> **Average per task:** 149 s · $0.300 · Eff Weighted 54,640 · Eff Input 252,759

---

## Per-Model Token Usage

### Sonnet (claude-sonnet-4-6) — sole model, no Haiku routing layer

| # | Instance ID | Input | Cache Write | Cache Read | Output | **Cost** | Requests |
|---|-------------|-------|-------------|------------|--------|----------:|----------|
| 1 | `12907` | 32 | 76,249 | 1,200,534 | 23,347 | **$0.996** | 23 |
| 2 | `13033` | 9 | 28,998 | 97,811 | 23,925 | **$0.497** | 6 |
| 3 | `13236` | 15 | 35,328 | 233,133 | 25,458 | **$0.584** | 10 |
| 4 | `13398` | 9 | 17,570 | 102,078 | 2,107 | **$0.128** | 6 |
| 5 | `13453` | 20 | 37,640 | 462,602 | 5,144 | **$0.357** | 13 |
| 6 | `13579` | 9 | 24,600 | 138,427 | 4,623 | **$0.203** | 6 |
| 7 | `13977` | 10 | 17,111 | 122,603 | 3,080 | **$0.147** | 7 |
| 8 | `14096` | 12 | 19,941 | 146,438 | 2,456 | **$0.156** | 7 |
| 9 | `14182` | 19 | 23,503 | 266,830 | 8,691 | **$0.299** | 12 |
| 10 | `14309` | 8 | 18,245 | 82,946 | 1,828 | **$0.121** | 5 |
| 11 | `14365` | 12 | 17,045 | 125,708 | 3,752 | **$0.158** | 7 |
| 12 | `14369` | 14 | 25,761 | 199,159 | 3,132 | **$0.203** | 9 |
| 13 | `14508` | 10 | 29,614 | 154,942 | 13,376 | **$0.358** | 7 |
| 14 | `14539` | 15 | 21,127 | 198,201 | 19,543 | **$0.432** | 10 |
| 15 | `14598` | 17 | 33,622 | 269,866 | 24,507 | **$0.575** | 12 |
| 16 | `14995` | 18 | 24,727 | 314,847 | 4,450 | **$0.254** | 13 |
| 17 | `7166` | 11 | 17,397 | 157,323 | 2,767 | **$0.154** | 8 |
| 18 | `7336` | 14 | 24,399 | 185,418 | 4,233 | **$0.211** | 9 |
| 19 | `7606` | 10 | 21,944 | 130,042 | 3,080 | **$0.168** | 7 |
| 20 | `7671` | 8 | 9,431 | 67,645 | 1,948 | **$0.085** | 5 |
| 21 | `8707` | 9 | 14,432 | 89,928 | 11,762 | **$0.258** | 6 |
| 22 | `8872` | 17 | 22,831 | 252,391 | 6,238 | **$0.255** | 12 |
| | **TOTAL** | **298** | **561,515** | **4,998,872** | **199,447** | **$6.598** | **200** |

> All 200 API requests were made to Sonnet. Unlike the Opus v3-raw run, there is no Haiku routing layer — MCP tool calls feed context directly into the single Sonnet model via cache.

---

## Per-Task Answer Comparison

### Task 1 — `12907` — ✅ Exact

**Issue:** `separability_matrix` wrong for nested `CompoundModels`

| | GT | MCP |
|---|---|---|
| File | `separable.py` | `separable.py` |
| Fix | `cright[...] = right` instead of `= 1` | Identical fix + extended test matrix entries |

---

### Task 2 — `13033` — ✅ Near-perfect

**Issue:** `TimeSeries` misleading exception on required column removal

| | GT | MCP |
|---|---|---|
| File | `core.py` | `core.py` |
| GT fix | Add `as_scalar_or_list_str()` helper, use full column lists in error message | Directly formats full lists inline; skips helper function |

**-1:** Omits the `as_scalar_or_list_str()` helper function; formats lists directly in the format string. Output is functionally identical but misses the clean utility extraction.

---

### Task 3 — `13236` — ✅ Exact

**Issue:** Remove auto-transform of structured ndarray into `NdarrayMixin`

| | GT | MCP |
|---|---|---|
| File | `table.py` | `table.py` |
| Fix | Remove 6-line auto-view block | Identical removal + adds `test_structured_masked_column` and updates `test_ndarray_mixin` |

---

### Task 4 — `13398` — ✅ Exact

**Issue:** Add ITRS ↔ AltAz/HADec topocentric transforms

| | GT | MCP |
|---|---|---|
| Files | 5 files + 1 new file | Same 5 files + new `itrs_observed_transforms.py` |
| Fix | ITRS `location` attr, new transform file, CIRS+TETE location propagation | Full diff output — new file and all 5 supporting changes identical to GT |

> Notable: completed in 51 s at $0.128 — the hardest task (1–4h estimated) solved fastest via MCP traversal. Sonnet retrieved the relevant coordinate transform files in a single pass.

---

### Task 5 — `13453` — ✅ Near-perfect

**Issue:** HTML writer ignores `formats` argument

| | GT | MCP |
|---|---|---|
| File | `html.py` | `html.py` |
| GT fix | `self.data.cols = cols` + `self.data._set_col_formats()` | Inlines equivalent `for col in cols` loop directly |

**-1:** Does not call `_set_col_formats()` via the existing helper. Inlines the equivalent logic instead. Functionally identical but bypasses the established pattern.

---

### Task 6 — `13579` — ✅ Exact

**Issue:** `SlicedLowLevelWCS.world_to_pixel_values` uses hardcoded `1.0` for dropped dimensions

| | GT | MCP |
|---|---|---|
| File | `sliced_wcs.py` | `sliced_wcs.py` |
| Fix | `sliced_out_world_coords = self._pixel_to_world_values_all(*[0]*len(self._pixel_keep))` | Identical logic and variable name |

---

### Task 7 — `13977` — ⚠️ Partial

**Issue:** `Quantity.__array_ufunc__` should return `NotImplemented` for duck types

| | GT | MCP |
|---|---|---|
| File | `quantity.py` | `quantity.py` |
| GT fix | Wrap **entire** `__array_ufunc__` body in try/except; check other operands' `__array_ufunc__` before returning NotImplemented | Only wraps the input-conversion loop (arrays list construction) |

**-2:** Misses errors raised by `converters_and_unit()` and `check_output()`. Doesn't check other operands' `__array_ufunc__`. Identical failure mode as Opus v3-raw.

---

### Task 8 — `14096` — ✅ Near-perfect

**Issue:** `SkyCoord` subclass property gives misleading `AttributeError`

| | GT | MCP |
|---|---|---|
| File | `sky_coordinate.py` | `sky_coordinate.py` |
| GT fix | Replace `raise AttributeError(...)` with `return self.__getattribute__(attr)` (2 lines) | MRO walk to detect descriptor and re-invoke `__get__` (10+ lines) |

**-1:** Over-engineered. GT's 2-line `__getattribute__` is simpler and sufficient. Both produce the correct error message.

---

### Task 9 — `14182` — ✅ Exact

**Issue:** RST writer needs `header_rows` support

| | GT | MCP |
|---|---|---|
| File | `rst.py` | `rst.py` |
| Fix | `__init__(self, header_rows=None)`, `sep_line_index = len(header_rows)` | Identical diff including test addition |

---

### Task 10 — `14309` — ✅ Near-perfect

**Issue:** `is_fits` IndexError with empty args

| | GT | MCP |
|---|---|---|
| File | `connect.py` | `connect.py` |
| GT fix | `return filepath.lower().endswith(...)` — make elif always return True/False | `return len(args) > 0 and isinstance(args[0], ...)` — guard downstream crash |

**-1:** Patches the symptom (guards `args[0]`) rather than fixing the logic flow (making the `elif` branch always return). Both prevent the crash for the failing test.

---

### Task 11 — `14365` — ✅ Near-perfect

**Issue:** QDP reader fails on lowercase commands

| | GT | MCP |
|---|---|---|
| File | `qdp.py` | `qdp.py` |
| GT fix | `re.IGNORECASE` + `v.upper() == "NO"` in data parsing | Only `re.IGNORECASE`; claims existing `.lower()` on line 300 handles the NO case |

**-1:** Missing `v.upper() == "NO"` for data line parsing. The existing `.lower()` handles the command keyword but not the value comparison.

---

### Task 12 — `14369` — ✅ Near-perfect

**Issue:** CDS unit parser right-recursive division (`a/b/c` → `a*c/b`)

| | GT | MCP |
|---|---|---|
| File | `cds.py` | `cds.py` |
| GT fix | `unit_expression DIVISION combined_units` → `combined_units DIVISION unit_expression` (single rule swap) | Adds explicit `precedence = (('left', 'PRODUCT'), ('left', 'DIVISION'))` + rewrites rule as `unit_expression DIVISION product_of_units \| division_of_units DIVISION product_of_units` |

**-1:** Different grammar approach. Both delete `cds_parsetab.py` and add regression tests. The precedence-based approach is arguably more principled, but diverges from the minimal GT change.

---

### Task 13 — `14508` — ✅ Near-perfect

**Issue:** `_format_float` uses `.16G` expanding short floats

| | GT | MCP |
|---|---|---|
| File | `card.py` | `card.py` |
| GT fix | `str(value).replace("e", "E")` | `str(value)` as primary path with manual scientific notation upper-casing, exponent zero-padding, and fallback to `.16G` for values >20 chars |

**-1:** Over-engineered. GT's one-liner handles all cases. Sonnet's multi-branch implementation adds unnecessary complexity while solving the same issue.

---

### Task 14 — `14539` — ✅ Exact

**Issue:** FITS diff fails for VLA columns with Q format descriptor

| | GT | MCP |
|---|---|---|
| File | `diff.py` | `diff.py` |
| Fix | `elif "P" in col.format or "Q" in col.format:` | Identical one-line fix + comprehensive test update with QD column |

---

### Task 15 — `14598` — ✅ Near-perfect

**Issue:** FITS CONTINUE cards lose quotes from double un-escaping

| | GT | MCP |
|---|---|---|
| File | `card.py` | `card.py` |
| GT fix | (1) Add `$` anchor to `_strg_comment_RE`; (2) remove `.replace("''", "'")` in `_split()` | Swap operation order in `_split()`: strip `&` first, then `.replace("''", "'")`  |

**-1:** Different approach. GT removes the replace and anchors the regex. Sonnet preserves the replace but corrects the order. Both fix the `''&` → `'` regression; Sonnet's `$` anchor is missing.

---

### Task 16 — `14995` — ✅ Exact

**Issue:** `_arithmetic_mask` has `operand is None` instead of `operand.mask is None`

| | GT | MCP |
|---|---|---|
| File | `ndarithmetic.py` | `ndarithmetic.py` |
| Fix | `elif operand.mask is None:` | Identical one-line change |

---

### Task 17 — `7166` — ✅ Near-perfect

**Issue:** `InheritDocstrings` doesn't work for properties

| | GT | MCP |
|---|---|---|
| File | `misc.py` | `misc.py` |
| GT fix | Add `inspect.isdatadescriptor(val)` alongside `inspect.isfunction(val)` | Uses `isinstance(val, property)` instead |

**-1:** `isinstance(val, property)` is narrower than `inspect.isdatadescriptor(val)` — the latter also covers `__slots__` and custom data descriptors. Both fix the reported issue for standard properties.

---

### Task 18 — `7336` — ✅ Near-perfect

**Issue:** `@quantity_input` fails with `-> None` annotation

| | GT | MCP |
|---|---|---|
| File | `decorators.py` | `decorators.py` |
| GT fix | `not in (inspect.Signature.empty, None)` — combined check | Nested: `if return_annotation is not empty: if return_annotation is None: return return_` |

**-1:** Different structure (nested ifs vs combined `not in` check). Functionally equivalent for all test cases; GT is more compact.

---

### Task 19 — `7606` — ⚠️ Partial

**Issue:** `Unit.__eq__` returns `False` instead of `NotImplemented`

| | GT | MCP |
|---|---|---|
| Files | `core.py` (2 locations) | `core.py` (1 location) |
| GT fix | `return NotImplemented` in both `UnitBase.__eq__` and `UnrecognizedUnit.__eq__` | `try/except TypeError: return False` in `UnrecognizedUnit.__eq__` only |

**-1 RC:** Root cause partially identified — focuses on `TypeError` from `None` input rather than the correct semantics (`NotImplemented` to enable Python's reflected operator fallback).

**-2 Patch:** (1) Returns `False` instead of `NotImplemented` — semantically different, breaks duck-type operator chaining. (2) Misses `UnitBase.__eq__` entirely.

> Better than the Opus v3-raw failure (which returned no patch at all), but wrong return value and incomplete coverage.

---

### Task 20 — `7671` — ✅ Near-perfect

**Issue:** `minversion` fails with `TypeError` when version strings contain pre-release suffixes

| | GT | MCP |
|---|---|---|
| File | `introspection.py` | `introspection.py` |
| GT fix | PEP440 regex to extract numeric part from `version` only | `try/except TypeError` fallback: `re.sub(r'[a-z].*', '', ...)` on **both** `have_version` and `version` |

**-1:** Strips pre-release suffixes from both versions (GT only strips `version`). Different regex approach. Functionally equivalent for all practical test cases.

---

### Task 21 — `8707` — ✅ Near-perfect

**Issue:** `Card.fromstring` / `Header.fromstring` don't accept bytes

| | GT | MCP |
|---|---|---|
| Files | `card.py`, `header.py` | `card.py`, `header.py` |
| GT fix | `Card.fromstring`: decode latin-1. `Header.fromstring`: bytes-aware refactor (CONTINUE/END as bytes, sep encode) | `Card.fromstring`: `decode('ascii')`. `Header.fromstring`: simple prepend `decode('ascii')` |

**-1:** Uses `ascii` codec instead of `latin-1` (FITS requires latin-1 for 8-bit byte values). `Header.fromstring` is simplified — no CONTINUE/END bytes handling. Works for typical ASCII-only FITS headers. Provides actual working code (vs Opus v3-raw which only described the fix).

---

### Task 22 — `8872` — ✅ Near-perfect

**Issue:** `np.float16` quantities upgraded to float64

| | GT | MCP |
|---|---|---|
| File | `quantity.py` | `quantity.py` |
| GT fix | `value.dtype.kind in 'iu'` (cast only integers/unsigned) | `np.issubdtype(value.dtype, np.inexact)` (preserve floating-point types) |

**-1:** Logically equivalent for float/integer dtypes but differs for `bool` dtype (`kind == 'b'`): GT would cast booleans to float, Sonnet would preserve them. Different expression of the same intent; both fix float16 preservation.

---

## Grade Distribution

| Grade | Count | Tasks |
|-------|-------|-------|
| ✅ Exact (8/8) | 7 | 1, 3, 4, 6, 9, 14, 16 |
| ✅ Near-perfect (7/8) | 13 | 2, 5, 8, 10, 11, 12, 13, 15, 17, 18, 20, 21, 22 |
| ⚠️ Partial (6/8) | 1 | 7 |
| ⚠️ Partial (5/8) | 1 | 19 |
| ❌ Fail (≤4/8) | 0 | — |

**Exact + Near-perfect: 20/22 (90.9%)**

---

## Comparison: Sonnet 4.6 WITH MCP vs Opus 4.6 v3-Raw

| Metric | Opus v3-Raw | Sonnet+MCP | Delta |
|--------|-------------|------------|-------|
| Overall score | 162/176 (92.0%) | 158/176 (89.8%) | −2.2 pp |
| Exact (8/8) | 14 | 7 | −7 |
| Near-perfect (7/8) | 5 | 13 | +8 |
| Partial (5–6/8) | 2 | 2 | 0 |
| Fail (≤4/8) | 1 | **0** | −1 |
| Avg time per task | 251 s | **149 s** | **−40%** |
| Avg cost per task | $0.734 | **$0.300** | **−59%** |
| Total cost | $16.16 | **$6.60** | **−59%** |
| API requests | 528 (Opus+Haiku) | **200 (Sonnet only)** | −62% |
| Zero fails | No (1 fail) | **Yes** | +1 |

**Key observations:**

- **Sonnet+MCP eliminates complete failures.** Opus had one task (7606) return no patch at all. Sonnet+MCP always produces a partial or better answer.
- **Sonnet+MCP is 59% cheaper and 40% faster.** The MCP knowledge graph enables targeted file retrieval with far fewer tokens — especially cache creation, which reflects the compressed graph traversal vs full repo scan.
- **Sonnet+MCP produces more Near-perfect scores than Exact.** The model tends to find functionally equivalent but slightly different solutions — over-engineering patches (14096, 14508), using alternative logic (7166, 8872), or taking different grammar/API routes (14369, 14598). Opus more often landed on the exact GT idiom.
- **The 1–4h task (13398) completed in 51 s at $0.128** — the fastest, cheapest task. MCP graph traversal found the five relevant coordinate-transform files in one pass, while Opus took 612 s at $1.772 exploring the repo directly.
- **Shared weakness: task 13977** (`__array_ufunc__` duck types). Both Opus and Sonnet only wrapped the input conversion loop, missing the wider fix. This suggests a fundamental ambiguity in how the issue is stated, not a model-specific gap.
