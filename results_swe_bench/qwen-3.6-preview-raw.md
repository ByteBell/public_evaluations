# Qwen 3.6 Plus Preview — SWE-Bench Evaluation Report

**Dataset:** `princeton-nlp/SWE-bench_Verified` — `astropy/astropy`
**Evaluated:** 16 of 22 tasks (6 tasks have no `answer.json` — listed below)
**Date:** 2026-04-02
**Judge:** Claude Code (claude-sonnet-4-6)
**Ground truth source:** `results_swe_bench/astropy_tasks.json`
**Raw responses:** `results_swe_bench/auto_run_on_qwen3.6_plus_preview/*/answer.json`
**Mode:** Qwen 3.6 Plus Preview via OpenRouter (no MCP knowledge graph, direct repo access)

---

## Skipped Tasks (no answer.json)

| Instance ID | Difficulty |
|-------------|------------|
| `astropy__astropy-13398` | 1–4h |
| `astropy__astropy-13453` | 15m–1h |
| `astropy__astropy-14369` | 1–4h |
| `astropy__astropy-7166` | <15m |
| `astropy__astropy-7336` | <15m |
| `astropy__astropy-8707` | 15m–1h |

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
| 1 | `astropy__astropy-12907` | 15m–1h | 3 | 2 | 1 | **6/8** | ⚠️ Partial | 1,862 | $4.369 |
| 2 | `astropy__astropy-13033` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 703 | $1.995 |
| 3 | `astropy__astropy-13236` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 718 | $7.525 |
| 4 | `astropy__astropy-13579` | 1–4h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 522 | $1.409 |
| 5 | `astropy__astropy-13977` | 15m–1h | 3 | 2 | 1 | **6/8** | ⚠️ Partial | 832 | $6.472 |
| 6 | `astropy__astropy-14096` | 15m–1h | 3 | 2 | 1 | **6/8** | ⚠️ Partial | 401 | $1.519 |
| 7 | `astropy__astropy-14182` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 537 | $2.133 |
| 8 | `astropy__astropy-14309` | <15m | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 275 | $1.792 |
| 9 | `astropy__astropy-14365` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 690 | $6.502 |
| 10 | `astropy__astropy-14508` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 512 | $3.889 |
| 11 | `astropy__astropy-14539` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 232 | $1.686 |
| 12 | `astropy__astropy-14598` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 4,781 | $15.837 |
| 13 | `astropy__astropy-14995` | <15m | 3 | 2 | 3 | **8/8** | ✅ Exact | 212 | $1.589 |
| 14 | `astropy__astropy-7606` | 15m–1h | 3 | 2 | 1 | **6/8** | ⚠️ Partial | 418 | $2.403 |
| 15 | `astropy__astropy-7671` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 460 | $2.293 |
| 16 | `astropy__astropy-8872` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 206 | $1.711 |
| | **TOTAL** | | **48/48** | **32/32** | **35/48** | **115/128** | **89.8%** | **13,361 s** | **$63.12** |
| | **AVERAGE** | | | | | **7.2/8** | | **835 s** | **$3.95** |

---

## Dimension Breakdown

| Dimension | Score | Max | % |
|-----------|-------|-----|---|
| Root cause identification | 48 | 48 | **100%** |
| Correct file(s) | 32 | 32 | **100%** |
| Correct patch / code change | 35 | 48 | **72.9%** |
| **Overall** | **115** | **128** | **89.8%** |

---

## Token & Cost Breakdown

| # | Instance ID | Input | Output | Cost | Requests |
|---|-------------|-------|--------|-----:|----------|
| 1 | `12907` | 1,211,158 | 49,023 | **$4.369** | 26 |
| 2 | `13033` | 610,060 | 10,976 | **$1.995** | 15 |
| 3 | `13236` | 2,431,844 | 15,287 | **$7.525** | 43 |
| 4 | `13579` | 445,645 | 4,829 | **$1.409** | 12 |
| 5 | `13977` | 2,064,730 | 18,493 | **$6.472** | 35 |
| 6 | `14096` | 475,811 | 6,118 | **$1.519** | 13 |
| 7 | `14182` | 636,194 | 14,972 | **$2.133** | 16 |
| 8 | `14309` | 566,322 | 6,177 | **$1.792** | 13 |
| 9 | `14365` | 2,088,828 | 15,681 | **$6.502** | 34 |
| 10 | `14508` | 1,257,383 | 7,797 | **$3.889** | 27 |
| 11 | `14539` | 545,149 | 3,396 | **$1.686** | 14 |
| 12 | `14598` | 4,578,635 | 140,090 | **$15.837** | 65 |
| 13 | `14995` | 510,855 | 3,740 | **$1.589** | 13 |
| 14 | `7606` | 777,073 | 4,804 | **$2.403** | 20 |
| 15 | `7671` | 722,167 | 8,446 | **$2.293** | 16 |
| 16 | `8872` | 545,442 | 4,976 | **$1.711** | 14 |
| | **TOTAL** | **19,467,296** | **314,805** | **$63.12** | **376** |

> **Note:** Qwen 3.6 Plus Preview has no prompt caching — all tokens are billed as input tokens. Cache read/write tokens = 0 for all tasks. Average per task: 835 s · $3.95.

---

## Per-Task Answer Comparison

### Task 1 — `12907` — ⚠️ Partial

**Issue:** `separability_matrix` wrong for nested `CompoundModels`

| | GT | Qwen |
|---|---|---|
| File | `separable.py` | `separable.py` |
| GT fix | Change `cright[...] = 1` → `cright[...] = right` in `_separable` | Add `_separable` preprocessing for left/right before `_coord_matrix` in `_cstack` |

**-2:** Qwen modifies `_cstack` by pre-calling `_separable` on nested CompoundModel operands before they enter `_coord_matrix`. The root cause is correctly identified. However, the fix only patches `_cstack` (used by the `&` operator) and leaves `_cdot` (used by `|`) unaddressed. The GT fixes `_separable` directly — a smaller, more general change. Partial fix for compound chaining via `&`.

---

### Task 2 — `13033` — ✅ Exact

**Issue:** `TimeSeries` misleading exception on required column removal

| | GT | Qwen |
|---|---|---|
| File | `core.py` | `core.py` |
| GT fix | Use `as_scalar_or_list_str(required_columns)` in both error paths | Identical: replaces `required_columns[0]` with `as_scalar_or_list_str(required_columns)` |

---

### Task 3 — `13236` — ✅ Exact

**Issue:** Remove auto-transform of structured ndarray into `NdarrayMixin`

| | GT | Qwen |
|---|---|---|
| File | `table.py` | `table.py` |
| GT fix | Remove 6-line auto-view block in `_convert_data_to_col` | Identical removal; correct fallthrough analysis for Column and MaskedColumn paths |

---

### Task 4 — `13579` — ✅ Near-perfect

**Issue:** `SlicedLowLevelWCS.world_to_pixel_values` uses hardcoded `1.0` for dropped dimensions

| | GT | Qwen |
|---|---|---|
| File | `sliced_wcs.py` | `sliced_wcs.py` |
| GT fix | Compute `pixel_to_world_values_all` at pixel origin lazily (only when a dropped dim is encountered) | Eagerly computes `sliced_out_world` at method entry, then uses `sliced_out_world[iworld]` for dropped dims |

**-1:** Functionally correct for all inputs. GT computes the dropped world values lazily (inside the loop, only if needed). Qwen computes them eagerly at method entry — a minor inefficiency when no dimensions are dropped, but produces identical results.

---

### Task 5 — `13977` — ⚠️ Partial

**Issue:** `Quantity.__array_ufunc__` should return `NotImplemented` for duck types

| | GT | Qwen |
|---|---|---|
| File | `quantity.py` | `quantity.py` |
| GT fix | Wrap entire `__array_ufunc__` body in `try/except`; check `__array_ufunc__` on all inputs/outputs | Only wraps the input-conversion loop; `try/except (TypeError, ValueError)` returns `NotImplemented` |

**-2:** GT wraps the full body including `converters_and_unit`, `check_output`, and `_result_as_quantity` — handling all failure modes of duck-type dispatch. Qwen only guards the converter call inside the input loop. Duck types that fail earlier (in `converters_and_unit`) or later (in `_result_as_quantity`) would still raise instead of returning `NotImplemented`.

---

### Task 6 — `14096` — ⚠️ Partial

**Issue:** `SkyCoord` subclass property gives misleading `AttributeError`

| | GT | Qwen |
|---|---|---|
| File | `sky_coordinate.py` | `sky_coordinate.py` |
| GT fix | `return self.__getattribute__(attr)` — 2 lines | `try: __getattribute__; except AttributeError: if property, call fget directly; raise` |

**-2:** Qwen's approach is more complex than the GT's clean 2-line solution. The fix attempts to call `fget(self)` inside the `except AttributeError` block when the failing attr is a property, intending to surface the real inner error. However, the approach is fragile: calling `fget(self)` inside an exception handler can produce confusing exception chaining. The GT's use of `__getattribute__` directly is correct and minimal.

---

### Task 7 — `14182` — ✅ Exact

**Issue:** RST writer needs `header_rows` support

| | GT | Qwen |
|---|---|---|
| File | `rst.py` | `rst.py` |
| GT fix | `__init__(header_rows=None)`, dynamic `sep_line_index`, add `read()` | Identical: `header_rows=None` in `__init__`, `idx = len(self.header.header_rows)` in `write()`, `start_line = 2 + len(...)` in `read()` |

---

### Task 8 — `14309` — ✅ Near-perfect

**Issue:** `is_fits` IndexError with empty args

| | GT | Qwen |
|---|---|---|
| File | `connect.py` | `connect.py` |
| GT fix | `return filepath.lower().endswith(...)` — restructures elif flow so it always returns | `len(args) > 0 and isinstance(args[0], ...)` — guards the access |

**-1:** Both fix the crash. GT restructures the logic flow; Qwen guards the list access. Functionally equivalent for all test cases.

---

### Task 9 — `14365` — ✅ Near-perfect

**Issue:** QDP reader fails on lowercase commands

| | GT | Qwen |
|---|---|---|
| File | `qdp.py` | `qdp.py` |
| GT fix | `re.IGNORECASE` on `_line_type_re` + `v.upper() == "NO"` in data parsing | Only `re.IGNORECASE` on `_line_type_re` |

**-1:** Missing the `v.upper() == "NO"` fix. Handles lowercase command keywords (e.g. `read serr`) but not lowercase `NO` values in data lines. Partial fix for the stated issue.

---

### Task 10 — `14508` — ✅ Exact

**Issue:** `_format_float` uses `.16G` expanding short floats

| | GT | Qwen |
|---|---|---|
| File | `card.py` | `card.py` |
| GT fix | Replace `f"{value:.16G}"` with `str(value).replace("e", "E")` unconditionally | Same: `str(value).replace("e", "E")` + truncation guard if `len > 20` using walrus operator |

Qwen's walrus-operator truncation is a safe safety net (`str(float)` almost never exceeds 20 chars) and does not reintroduce `.16G` expansion. Functionally equivalent to GT.

---

### Task 11 — `14539` — ✅ Exact

**Issue:** FITS diff fails for VLA columns with Q format descriptor

| | GT | Qwen |
|---|---|---|
| File | `diff.py` | `diff.py` |
| GT fix | `elif "P" in col.format or "Q" in col.format:` | Identical |

---

### Task 12 — `14598` — ✅ Near-perfect

**Issue:** FITS CONTINUE cards lose quotes from double un-escaping

| | GT | Qwen |
|---|---|---|
| File | `card.py` | `card.py` |
| GT fix | (1) Add `$` anchor to `_strg_comment_RE`; (2) remove `.replace("''", "'")` in `_split()` | Only (2): removes `.replace("''", "'")` in `_split()` |

**-1:** Correctly identifies and removes the double-unescaping call in `_split()`, which is the primary cause of the quote corruption. Does not add the `$` anchor to `_strg_comment_RE`, which is a secondary hardening against over-greedy regex matching on malformed CONTINUE cards. Task `14598` consumed the most resources by far (4,781 s, 65 requests, $15.84).

---

### Task 13 — `14995` — ✅ Exact

**Issue:** `_arithmetic_mask` has `operand is None` instead of `operand.mask is None`

| | GT | Qwen |
|---|---|---|
| File | `ndarithmetic.py` | `ndarithmetic.py` |
| GT fix | `elif operand.mask is None:` | `elif operand is None or operand.mask is None:` |

Qwen keeps the `operand is None` guard in addition to adding the `.mask is None` check. The extra guard is harmless — if `operand is None`, `operand.mask` would raise `AttributeError` anyway, so Qwen's version is more defensive. Functionally identical for all real inputs.

---

### Task 14 — `7606` — ⚠️ Partial

**Issue:** `Unit.__eq__` returns `False` instead of `NotImplemented`

| | GT | Qwen |
|---|---|---|
| Files | `core.py` — both `UnitBase.__eq__` and `UnrecognizedUnit.__eq__` | `core.py` — only `UnrecognizedUnit.__eq__` |
| GT fix | `return NotImplemented` in both classes | `try/except (ValueError, UnitsError, TypeError): return NotImplemented` in `UnrecognizedUnit.__eq__` only |

**-2:** Qwen correctly returns `NotImplemented` (unlike returning `False`) and wraps with appropriate exception types. However, it misses `UnitBase.__eq__` entirely, which is the primary class used in practice. The issue description mentions `UnrecognizedUnit` prominently, misdirecting the model away from the parent class fix.

---

### Task 15 — `7671` — ✅ Near-perfect

**Issue:** `minversion` fails with `TypeError` when version strings contain pre-release suffixes

| | GT | Qwen |
|---|---|---|
| File | `introspection.py` | `introspection.py` |
| GT fix | PEP440 regex to strip pre-release from `version` only; keep `LooseVersion`; wrap with `try/except TypeError` fallback | Replace `LooseVersion` / `distutils.version` entirely with `packaging.version.Version` |

**-1:** Qwen's approach is functionally correct for PEP 440 compliant version strings and avoids the deprecated `distutils.version`. However, `LooseVersion` was used precisely because it tolerates non-PEP-440 strings (e.g. vendor-specific version formats). Strict `packaging.version.Version` raises `InvalidVersion` on non-conforming strings, which could break existing users. The GT's minimal regex strip is a safer, more conservative fix.

---

### Task 16 — `8872` — ✅ Exact

**Issue:** `np.float16` quantities upgraded to float64

| | GT | Qwen |
|---|---|---|
| File | `quantity.py` | `quantity.py` |
| GT fix | `value.dtype.kind in 'iu'` (cast only integers/unsigned) | `np.issubdtype(value.dtype, np.inexact)` at both locations — preserve all floating-point types |

Both fix `np.can_cast(np.float32, np.float16)` returning `False`. `np.inexact` covers float16/32/64/128 and complex types — functionally identical to GT intent.

---

## Grade Distribution

| Grade | Count | Tasks |
|-------|-------|-------|
| ✅ Exact (8/8) | 7 | 2, 3, 7, 10, 11, 13, 16 |
| ✅ Near-perfect (7/8) | 5 | 4, 8, 9, 12, 15 |
| ⚠️ Partial (6/8) | 4 | 1, 5, 6, 14 |
| ❌ Fail (≤4/8) | 0 | — |

**Exact + Near-perfect: 12/16 (75.0%)**

---

## Notable Observations

- **Root cause is perfect (100%).** Qwen correctly diagnosed every bug across all 16 tasks, even on the partial fixes. It never pointed at the wrong module or described a wrong root cause.
- **File identification is perfect (100%).** Always landed on the right file(s), including multi-file tasks (14598, 7606).
- **Patch quality is the weak point (72.9%).** All 4 partial scores stem from incomplete scope: `_cstack` only (12907), input-loop only (13977), missing parent class (7606), or over-engineered approach (14096). A consistent pattern of fixing the immediately obvious path while missing a broader enclosing scope.
- **Cost is very high relative to output quality.** At $3.95/task average and $63.12 total for 16 tasks, Qwen consumed substantially more tokens per task than Claude Sonnet 4.6 raw ($0.54/task for 22 tasks). Qwen has no prompt caching, so every context re-read pays full input token cost. Task 14598 alone cost $15.84.
- **Task 14598 is a significant outlier.** 4,781 seconds and 65 API requests for a task that ultimately produced only a partial fix (missing the `$` anchor). This suggests Qwen took many exploratory loops without converging.
- **Tasks 13977 and 12907 are the shared weaknesses with other models.** Both require understanding the full call chain rather than just the immediate failure point — a depth-of-reasoning limitation seen across multiple models.
