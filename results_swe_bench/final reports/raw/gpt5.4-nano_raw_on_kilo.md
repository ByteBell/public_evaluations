# GPT-5.4 Nano Raw on Kilo — SWE-Bench Evaluation Report

**Dataset:** `princeton-nlp/SWE-bench_Verified` — `astropy/astropy`
**Evaluated:** 22 tasks from `astropy_tasks.json`
**Date:** 2026-04-03
**Judge:** Claude Code (claude-sonnet-4-6)
**Ground truth source:** `results_swe_bench/astropy_tasks.json`
**Raw responses:** `results_swe_bench/auto_run_on_raw_kilo_openai_gpt-5.4-nano/*/answer.json`
**Mode:** Kilo agent with direct repo access (no MCP knowledge graph) · Model: `openai/gpt-5.4-nano`

> **Note on timeouts:** Several tasks recorded ~2684–2685 s, consistent with a ~45-minute wall-clock limit. All still produced a complete answer JSON.

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
| 1 | `astropy__astropy-12907` | 15m–1h | 2 | 2 | 1 | **5/8** | ⚠️ Partial | 2,685 | $0.011 |
| 2 | `astropy__astropy-13033` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 1,135 | $0.058 |
| 3 | `astropy__astropy-13236` | 15m–1h | 3 | 2 | 1 | **6/8** | ⚠️ Partial | 1,286 | $0.071 |
| 4 | `astropy__astropy-13398` | 1–4h | 1 | 1 | 0 | **2/8** | ❌ Fail | 1,120 | $0.067 |
| 5 | `astropy__astropy-13453` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 2,685 | $0.006 |
| 6 | `astropy__astropy-13579` | 1–4h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 2,685 | $0.098 |
| 7 | `astropy__astropy-13977` | 15m–1h | 3 | 2 | 1 | **6/8** | ⚠️ Partial | 2,684 | $0.014 |
| 8 | `astropy__astropy-14096` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 2,684 | $0.064 |
| 9 | `astropy__astropy-14182` | 15m–1h | 2 | 2 | 0 | **4/8** | ❌ Fail | 1,147 | $0.076 |
| 10 | `astropy__astropy-14309` | <15m | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 1,060 | $0.032 |
| 11 | `astropy__astropy-14365` | 15m–1h | 3 | 2 | 1 | **6/8** | ⚠️ Partial | 1,078 | $0.061 |
| 12 | `astropy__astropy-14369` | 1–4h | 2 | 2 | 1 | **5/8** | ⚠️ Partial | 240 | $0.057 |
| 13 | `astropy__astropy-14508` | 15m–1h | 3 | 2 | 1 | **6/8** | ⚠️ Partial | 345 | $0.061 |
| 14 | `astropy__astropy-14539` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 54 | $0.017 |
| 15 | `astropy__astropy-14598` | 15m–1h | 2 | 2 | 0 | **4/8** | ❌ Fail | 14 | $0.005 |
| 16 | `astropy__astropy-14995` | <15m | 3 | 2 | 3 | **8/8** | ✅ Exact | 14 | $0.005 |
| 17 | `astropy__astropy-7166` | <15m | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 34 | $0.006 |
| 18 | `astropy__astropy-7336` | <15m | 3 | 2 | 3 | **8/8** | ✅ Exact | 51 | $0.009 |
| 19 | `astropy__astropy-7606` | 15m–1h | 2 | 1 | 0 | **3/8** | ❌ Fail | 96 | $0.015 |
| 20 | `astropy__astropy-7671` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 45 | $0.005 |
| 21 | `astropy__astropy-8707` | 15m–1h | 3 | 1 | 1 | **5/8** | ⚠️ Partial | 50 | $0.010 |
| 22 | `astropy__astropy-8872` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 354 | $0.060 |
| | **TOTAL** | | **58/66** | **40/44** | **31/66** | **129/176** | **73.3%** | **21,544 s** | **$0.808** |
| | **AVERAGE** | | | | | **5.9/8** | | **979 s** | **$0.037** |

---

## Dimension Breakdown

| Dimension | Score | Max | % |
|-----------|-------|-----|---|
| Root cause identification | 58 | 66 | **87.9%** |
| Correct file(s) | 40 | 44 | **90.9%** |
| Correct patch / code change | 31 | 66 | **47.0%** |
| **Overall** | **129** | **176** | **73.3%** |

---

## Token & Cost Breakdown

| # | Instance ID | Input | Cache Read | Output | **Cost** | Requests | Time (s) |
|---|-------------|-------|------------|--------|----------:|----------|----------|
| 1 | `12907` | 28,868 | 108,032 | 2,195 | **$0.011** | 9 | 2,685 |
| 2 | `13033` | 158,732 | 956,416 | 5,700 | **$0.058** | 44 | 1,135 |
| 3 | `13236` | 181,950 | 1,409,024 | 5,184 | **$0.071** | 42 | 1,286 |
| 4 | `13398` | 147,565 | 1,553,408 | 5,000 | **$0.067** | 50 | 1,120 |
| 5 | `13453` | 18,225 | 81,920 | 793 | **$0.006** | 6 | 2,685 |
| 6 | `13579` | 41,292 | 307,200 | 66,585 | **$0.098** | 20 | 2,685 |
| 7 | `13977` | 43,065 | 132,096 | 2,067 | **$0.014** | 10 | 2,684 |
| 8 | `14096` | 156,101 | 1,363,456 | 4,576 | **$0.064** | 37 | 2,684 |
| 9 | `14182` | 135,786 | 1,901,568 | 8,550 | **$0.076** | 54 | 1,147 |
| 10 | `14309` | 67,436 | 655,872 | 4,134 | **$0.032** | 31 | 1,060 |
| 11 | `14365` | 45,538 | 399,872 | 35,123 | **$0.061** | 27 | 1,078 |
| 12 | `14369` | 112,952 | 1,354,752 | 5,536 | **$0.057** | 42 | 240 |
| 13 | `14508` | 44,778 | 411,648 | 34,834 | **$0.061** | 23 | 345 |
| 14 | `14539` | 65,024 | 123,392 | 1,102 | **$0.017** | 11 | 54 |
| 15 | `14598` | 15,961 | 59,392 | 431 | **$0.005** | 4 | 14 |
| 16 | `14995` | 17,551 | 41,472 | 426 | **$0.005** | 3 | 14 |
| 17 | `7166` | 16,086 | 78,848 | 1,208 | **$0.006** | 6 | 34 |
| 18 | `7336` | 19,804 | 198,144 | 1,185 | **$0.009** | 11 | 51 |
| 19 | `7606` | 27,982 | 315,392 | 2,573 | **$0.015** | 22 | 96 |
| 20 | `7671` | 10,885 | 83,456 | 1,021 | **$0.005** | 7 | 45 |
| 21 | `8707` | 27,917 | 166,912 | 1,118 | **$0.010** | 12 | 50 |
| 22 | `8872` | 28,046 | 524,288 | 35,351 | **$0.060** | 22 | 354 |
| | **TOTAL** | **1,413,544** | **12,226,560** | **224,692** | **$0.808** | **493** | **21,544** |

> **Average per task:** 979 s · $0.037

---

## Per-Task Answer Comparison

### Task 1 — `12907` — ⚠️ Partial (5/8)

**Issue:** `separability_matrix` wrong for nested `CompoundModels`

| | GT | Nano |
|---|---|---|
| File | `separable.py` | `separable.py` |
| GT fix | `cright[-right.shape[0]:, -right.shape[1]:] = right` (one-line, in `_cstack`) | Rewrites `_separable()` for `op == '&'`: recursively calls `_separable(child)`, places child output slices into parent matrix, then `np.hstack` |

**−1 RC:** Correctly identifies the nested `CompoundModel` axis-ordering bug but attributes it to `_separable()` rather than `_cstack()` where the `= 1` hardcode lives.  
**−2 Patch:** Different function, over-engineered recursive approach vs the one-line GT fix.

---

### Task 2 — `13033` — ✅ Near-perfect (7/8)

**Issue:** `TimeSeries` misleading exception on required column removal

| | GT | Nano |
|---|---|---|
| File | `core.py` | `core.py` |
| GT fix | `as_scalar_or_list_str()` helper; used in both error paths | Updated `_check_required_columns` to report full required vs found list; added test assertion |

**−1 Patch:** Same user-visible behavior, no helper extracted. Structural difference only.

---

### Task 3 — `13236` — ⚠️ Partial (6/8)

**Issue:** Remove auto-transform of structured ndarray into `NdarrayMixin`

| | GT | Nano |
|---|---|---|
| File | `table.py` | `table.py` |
| GT fix | Remove 6-line auto-view block in `_convert_data_to_col` | Modifies `_convert_sequence_data_to_column` to force structured ndarrays to `Column` |

**−2 Patch:** Wrong method — GT targets `_convert_data_to_col`, nano targets `_convert_sequence_data_to_column`. Different code path, different semantics.

---

### Task 4 — `13398` — ❌ Fail (2/8)

**Issue:** Add ITRS ↔ AltAz/HADec topocentric transforms

| | GT | Nano |
|---|---|---|
| Files | 5 files + new `itrs_observed_transforms.py` | `itrs.py` only |
| GT fix | New transform module, `location` attr on ITRS, CIRS/TETE chain, `__init__.py` import | Adds `__init__` override forwarding `*args, **kwargs` |

**−2 RC:** Misses that a full bidirectional transform implementation is required.  
**−1 Files:** Only `itrs.py`; misses 4+ required files.  
**−3 Patch:** Only prevents the keyword `TypeError`; no transform math whatsoever.

---

### Task 5 — `13453` — ✅ Near-perfect (7/8)

**Issue:** HTML writer ignores `formats` argument

| | GT | Nano |
|---|---|---|
| File | `html.py` | `html.py` |
| GT fix | `self.data.cols = cols` + `self.data._set_col_formats()` | Applies formats per-column inline; iterates over sliced `new_col` for multicolumn case |

**−1 Patch:** Bypasses `_set_col_formats()` pipeline. Functionally similar for simple cases.

---

### Task 6 — `13579` — ✅ Near-perfect (7/8)

**Issue:** `SlicedLowLevelWCS.world_to_pixel_values` uses hardcoded `1.0` for dropped dimensions

| | GT | Nano |
|---|---|---|
| File | `sliced_wcs.py` | `sliced_wcs.py` |
| GT fix | Compute `sliced_out_world_coords` at pixel `[0,…,0]` | Build reference pixel from `slice.start or 0` per axis |

**−1 Patch:** Reasonable alternative but differs from GT's zero-reference computation; may diverge on non-zero-based slices.

---

### Task 7 — `13977` — ⚠️ Partial (6/8)

**Issue:** `Quantity.__array_ufunc__` should return `NotImplemented` for duck types

| | GT | Nano |
|---|---|---|
| File | `quantity.py` | `quantity.py` |
| GT fix | Wrap entire `__array_ufunc__` body in try/except | Early-exit guard: if input `hasattr(unit)` but is not `Quantity`/`ndarray`/`Column`, return `NotImplemented` |

**−2 Patch:** Narrower than GT; misses duck types without a `unit` attribute that still cannot be converted.

---

### Task 8 — `14096` — ✅ Near-perfect (7/8)

**Issue:** `SkyCoord` subclass property gives misleading `AttributeError`

| | GT | Nano |
|---|---|---|
| File | `sky_coordinate.py` | `sky_coordinate.py` |
| GT fix | `return self.__getattribute__(attr)` — 2 lines | Re-raise original `AttributeError` from property immediately |

**−1 Patch:** Behaviorally equivalent; GT's `__getattribute__` is simpler and more idiomatic.

---

### Task 9 — `14182` — ❌ Fail (4/8)

**Issue:** RST writer needs `header_rows` support

| | GT | Nano |
|---|---|---|
| File | `rst.py` | `rst.py` |
| GT fix | Remove `start_line = 3`; full `__init__`; dynamic `write`/`read` | Change `__init__(header_rows=None)` → `__init__(header_rows=None, **kwargs)` |

**−1 RC:** Identifies the keyword rejection but misses the full feature requirement.  
**−3 Patch:** `**kwargs` prevents `TypeError` but ignores `header_rows` entirely.

---

### Task 10 — `14309` — ✅ Near-perfect (7/8)

**Issue:** `is_fits` IndexError with empty args

| | GT | Nano |
|---|---|---|
| File | `connect.py` | `connect.py` |
| GT fix | Early `return` restructures logic so `args[0]` is unreachable | Explicit `if not args: return False` guard |

**−1 Patch:** Equivalent fix, less elegant structure.

---

### Task 11 — `14365` — ⚠️ Partial (6/8)

**Issue:** QDP reader fails on lowercase commands

| | GT | Nano |
|---|---|---|
| File | `qdp.py` | `qdp.py` |
| GT fix | `re.IGNORECASE` **+** `v.upper() == "NO"` in data loop | Only `re.IGNORECASE` |

**−2 Patch:** Missing `v.upper() == "NO"` fix; lowercase `no` in data lines still fails.

---

### Task 12 — `14369` — ⚠️ Partial (5/8)

**Issue:** CDS unit parser right-recursive division (`a/b/c` → `a*c/b`)

| | GT | Nano |
|---|---|---|
| Files | `cds.py` + `cds_parsetab.py` | `cds.py` |
| GT fix | Grammar rule swap (`division_of_units : unit_expression DIVISION unit_expression` left-recursive) + regenerated parsetab | Change `p[0] = p[1] / p[3]` → `p[0] = p[1] * (p[3] ** -1)` in `p_division_of_units` |

**−1 RC:** Nano identifies the division chaining problem but attributes it to a semantics issue (`/` vs `* inverse`) rather than the actual grammar associativity bug.  
**−1 Files:** Misses `cds_parsetab.py` — the regenerated parse table is required to take effect.  
**−2 Patch:** `p[1] * (p[3] ** -1)` is algebraically equivalent to `p[1] / p[3]` for a single division; it does not fix the right-recursion associativity for chained `/`. GT's grammar rule change is required for `a/b/c` to parse left-recursively.

---

### Task 13 — `14508` — ⚠️ Partial (6/8)

**Issue:** `_format_float` uses `.16G` expanding short floats

| | GT | Nano |
|---|---|---|
| File | `card.py` | `card.py` |
| GT fix | `str(value).replace("e", "E")` — always uses Python's minimal repr | "keep using `str(value).replace('e', 'E')` and truncate to 20 chars as before" |

**−2 Patch:** The answer describes using `str(value)` (correct) but adds a 20-char truncation which is the old behavior. GT uses `str(float)` unconditionally — no truncation — because Python's `str` already gives the shortest round-trip representation. The truncation fallback can still expand short floats for edge cases.

---

### Task 14 — `14539` — ✅ Exact (8/8)

**Issue:** FITS diff fails for VLA columns with Q format descriptor

| | GT | Nano |
|---|---|---|
| File | `diff.py` | `diff.py` |
| GT fix | `elif "P" in col.format or "Q" in col.format:` | Identical condition; uses `np.allclose` with rtol/atol for comparison |

Note: nano uses `np.allclose` where GT uses a per-row loop — structurally different but the Q-format guard is exact. Full marks for identifying the missing `"Q"` check.

---

### Task 15 — `14598` — ❌ Fail (4/8)

**Issue:** FITS CONTINUE cards lose quotes from double un-escaping

| | GT | Nano |
|---|---|---|
| Files | `card.py` (two changes) | `card.py` |
| GT fix | (1) Add `$` anchor to `_strg_comment_RE`; (2) remove `.replace("''", "'")` in `_split()` | Describes preserving a `''&` → `'&` translation step before full un-escaping |

**−1 RC:** Nano identifies the `''` → `'` replacement as the culprit but incorrectly proposes a partial-translation workaround rather than the clean removal GT uses.  
**−1 Files:** Misses the `_strg_comment_RE` regex anchor fix which is the second required change.  
**−2 Patch:** The `''&` → `'&` approach is not in GT; correct fix is simply removing `.replace("''", "'")` from `_split()`. The anchor fix is entirely absent.

---

### Task 16 — `14995` — ✅ Exact (8/8)

**Issue:** `_arithmetic_mask` has `operand is None` instead of `operand.mask is None`

| | GT | Nano |
|---|---|---|
| File | `ndarithmetic.py` | `ndarithmetic.py` |
| GT fix | `elif operand.mask is None:` | Deepcopy operand mask when `self.mask is None`; correct `operand.mask is None` check |

Nano correctly identifies the `operand is None` vs `operand.mask is None` bug and the right fix. Full marks.

---

### Task 17 — `7166` — ✅ Near-perfect (7/8)

**Issue:** `InheritDocstrings` doesn't work for properties

| | GT | Nano |
|---|---|---|
| File | `misc.py` | `misc.py` |
| GT fix | `inspect.isfunction(val) or inspect.isdatadescriptor(val)` | Uses `inspect.isdatadescriptor(val)` check + corrects control flow for docstring assignment |

**−1 Patch:** Nano mentions `inspect.isdatadescriptor` (same as GT) — better than nano's initial description which only mentioned `property`. However the answer also mentions "correcting the control flow", suggesting additional changes beyond GT's minimal two-word addition. If the control flow changes are extra, that's a minor structural divergence.

---

### Task 18 — `7336` — ✅ Exact (8/8)

**Issue:** `@quantity_input` fails with `-> None` annotation

| | GT | Nano |
|---|---|---|
| File | `decorators.py` | `decorators.py` |
| GT fix | `not in (inspect.Signature.empty, None)` | Skip `.to()` when `return_annotation is None` |

Nano correctly identifies the `None` annotation case and applies the equivalent fix. Full marks.

---

### Task 19 — `7606` — ❌ Fail (3/8)

**Issue:** `Unit.__eq__` returns `False` instead of `NotImplemented`

| | GT | Nano |
|---|---|---|
| Files | `core.py` — both `UnitBase.__eq__` and `UnrecognizedUnit.__eq__` | `core.py` — `UnrecognizedUnit.__eq__` only |
| GT fix | `return NotImplemented` in both classes | Guard `other is None` in `UnrecognizedUnit.__eq__`, return `False` |

**−1 RC:** Nano identifies the issue is in `UnrecognizedUnit.__eq__` but misses the primary class `UnitBase.__eq__` and misunderstands the fix — returning `False` for `None` is not the same as returning `NotImplemented` for unknown types.  
**−1 Files:** Only touches `UnrecognizedUnit`; misses `UnitBase.__eq__`.  
**−3 Patch:** `return False` for `other is None` is semantically wrong — `NotImplemented` is required so Python can try the reflected operator. The `UnitBase.__eq__` fix (equally important) is absent.

---

### Task 20 — `7671` — ✅ Near-perfect (7/8)

**Issue:** `minversion` fails with `TypeError` on pre-release version strings

| | GT | Nano |
|---|---|---|
| File | `introspection.py` | `introspection.py` |
| GT fix | PEP 440 regex to strip pre-release from `version` only; then compare with `LooseVersion` | Normalizes by "stripping any trailing non-dotted numeric suffix"; uses `re` |

**−1 Patch:** Nano's description implies stripping from `have_version` as well as `version`, whereas GT strips only `version`. If both are stripped, pre-release `have_version` strings would compare incorrectly (e.g., a pre-release would appear as the release itself).

---

### Task 21 — `8707` — ⚠️ Partial (5/8)

**Issue:** `Card.fromstring` / `Header.fromstring` don't accept bytes

| | GT | Nano |
|---|---|---|
| Files | `card.py` + `header.py` | `header.py` only |
| GT fix | `Card.fromstring`: decode latin-1. `Header.fromstring`: bytes-aware | Only `Header.fromstring`: decode as ASCII |

**−1 Files:** Misses `card.py` — GT requires bytes support in `Card.fromstring` too.  
**−2 Patch:** Uses `ascii` codec vs GT's `latin-1`; FITS allows 8-bit chars per spec. Only patches `Header.fromstring`; `Card.fromstring` is unpatched.

---

### Task 22 — `8872` — ✅ Exact (8/8)

**Issue:** `np.float16` quantities upgraded to float64

| | GT | Nano |
|---|---|---|
| File | `quantity.py` | `quantity.py` |
| GT fix | `value.dtype.kind in 'iu'` (cast only integers/unsigned) | Treat any `np.inexact` dtype as eligible for preservation |

Both fix the float16 upcast. GT checks integer kinds; nano checks `np.inexact`. `np.inexact` covers float16/32/64/complex — a slightly broader fix that is functionally equivalent for all practical cases. Full marks.

---

## Grade Distribution

| Grade | Count | Tasks |
|-------|-------|-------|
| ✅ Exact (8/8) | 4 | 14, 16, 18, 22 |
| ✅ Near-perfect (7/8) | 7 | 2, 5, 6, 8, 10, 17, 20 |
| ⚠️ Partial (6/8) | 4 | 3, 7, 11, 13 |
| ⚠️ Partial (5/8) | 3 | 1, 12, 21 |
| ❌ Fail (4/8) | 2 | 9, 15 |
| ❌ Fail (3/8) | 1 | 19 |
| ❌ Fail (2/8) | 1 | 4 |

**Exact + Near-perfect: 11/22 (50.0%)**

---

## Comparison: GPT-5.4 Nano vs Claude Sonnet 4.6 Raw (full 22 tasks)

| Metric | GPT-5.4 Nano | Sonnet 4.6 | Delta |
|--------|-------------|------------|-------|
| Overall score | 129/176 (73.3%) | 164/176 (93.2%) | **−19.9 pp** |
| Exact (8/8) | 4 | 14 | −10 |
| Near-perfect (7/8) | 7 | 5 | +2 |
| Partial (6/8) | 4 | 2 | +2 |
| Partial (5/8) | 3 | 1 | +2 |
| Fail (≤4/8) | 4 | **0** | +4 |
| Root cause % | 87.9% | **100%** | −12.1 pp |
| File ID % | 90.9% | **100%** | −9.1 pp |
| Patch quality % | 47.0% | **81.8%** | −34.8 pp |
| Avg time per task | 979 s | 310 s | +669 s |
| Avg cost per task | **$0.037** | $0.538 | −93.1% |
| Total cost | **$0.808** | $11.83 | −93.2% |

**Key observations:**

- **Patch quality remains the decisive gap** (47% vs 82%). Nano finds the right file in ~91% of cases and identifies the root cause in ~88%, but the specific code fix is frequently wrong, incomplete, or targets the wrong function.

- **4 outright fails on 22 tasks.** `13398` (ITRS, under-scoped), `14182` (RST header_rows, feature not implemented), `14598` (FITS CONTINUE cards, missing anchor fix + wrong approach), `7606` (Unit.__eq__, returns `False` instead of `NotImplemented` and misses `UnitBase`). The `7606` failure is particularly telling: nano fixes `UnrecognizedUnit.__eq__` but returns `False` not `NotImplemented` — a semantic error not just an incomplete fix.

- **4 Exact scores on 22 tasks** (`14539`, `14995`, `7336`, `8872`) — all simple, focused bugs with one-line or two-line GT fixes. Nano handles these well. The pattern: the simpler the fix, the better nano performs.

- **Strong on simpler tasks.** The 11 new tasks (tasks 12–22) include several <15 min fixes where nano scores 7–8/8 consistently (`14995`, `7336`, `7671`, `8872`). The 11 original tasks were skewed toward harder problems.

- **Cost efficiency is dramatic.** At $0.037/task ($0.808 total), nano is 14.5× cheaper than Sonnet per task. For triage, root-cause identification, or file-finding tasks, nano delivers substantial value.

- **Timeout distribution shifted.** The new 11 tasks are mostly fast (14–354 s) because they are simpler — the agent finds the answer quickly rather than hitting the wall clock. Only the first 11 tasks saw frequent timeouts.
