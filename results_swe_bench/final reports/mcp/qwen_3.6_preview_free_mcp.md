# Qwen 3.6 Plus (Free) MCP on Kilo — SWE-Bench Evaluation Report

**Dataset:** `princeton-nlp/SWE-bench_Verified` — `astropy/astropy`
**Evaluated:** 22 tasks from `astropy_tasks.json`
**Date:** 2026-04-03
**Judge:** Claude Code (claude-sonnet-4-6)
**Ground truth source:** `results_swe_bench/astropy_tasks.json`
**MCP responses:** `results_swe_bench/auto_run_on_mcp_kilo_qwen_qwen3.6-plus:free/*/answer.json`
**Mode:** Kilo agent with ByteBell MCP knowledge graph (no direct repo access) · Model: `qwen/qwen3.6-plus:free`
**Cost:** $0.00 — free tier; reported as $0.000 for all tasks.

---

## Scoring Rubric

| Dimension | Weight | What is graded |
|-----------|--------|----------------|
| Root cause identification | 3 pts | Did the model correctly diagnose *why* the bug exists? |
| Correct file(s) | 2 pts | Did it identify the right file(s) to change? |
| Correct patch / code change | 3 pts | Does the proposed code change match the ground truth or produce functionally equivalent output? |

**Grade tiers:** ✅ Exact (8/8) · ✅ Near-perfect (7/8) · ⚠️ Partial (5–6/8) · ❌ Fail (≤4/8)

---

## Combined Per-Question: Score · Time · Tokens

| # | Instance ID | Difficulty | RC | Files | Patch | **Score** | Grade | Time (s) | Steps | Input Tok | Output Tok | Reasoning Tok |
|---|-------------|------------|----|-------|-------|-----------|-------|----------|-------|-----------|------------|---------------|
| 1 | `astropy__astropy-12907` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 797 | 30 | 1,433,130 | 35,977 | 20,827 |
| 2 | `astropy__astropy-13033` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 418 | 16 | 483,569 | 12,129 | 9,802 |
| 3 | `astropy__astropy-13236` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 284 | 36 | 1,488,960 | 5,710 | 996 |
| 4 | `astropy__astropy-13398` | 1–4h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 741 | 29 | 1,659,393 | 29,039 | 3,416 |
| 5 | `astropy__astropy-13453` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 269 | 29 | 1,649,235 | 7,828 | 169 |
| 6 | `astropy__astropy-13579` | 1–4h | 3 | 2 | 1 | **6/8** | ⚠️ Partial | 187 | 15 | 375,633 | 6,927 | 2,425 |
| 7 | `astropy__astropy-13977` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 399 | 26 | 962,892 | 7,569 | 2,028 |
| 8 | `astropy__astropy-14096` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 174 | 20 | 630,414 | 4,462 | 2,089 |
| 9 | `astropy__astropy-14182` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 122 | 21 | 524,594 | 4,128 | 1,170 |
| 10 | `astropy__astropy-14309` | <15m | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 134 | 12 | 297,881 | 3,324 | 1,744 |
| 11 | `astropy__astropy-14365` | 15m–1h | 3 | 2 | 1 | **6/8** | ⚠️ Partial | 283 | 21 | 786,408 | 10,476 | 5,914 |
| 12 | `astropy__astropy-14369` | 1–4h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 321 | 9 | 351,714 | 14,791 | 112 |
| 13 | `astropy__astropy-14508` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 80 | 13 | 340,723 | 1,518 | 197 |
| 14 | `astropy__astropy-14539` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 88 | 12 | 428,702 | 3,424 | 1,511 |
| 15 | `astropy__astropy-14598` | 15m–1h | 2 | 2 | 1 | **5/8** | ⚠️ Partial | 997 | 31 | 1,448,876 | 39,928 | 22,983 |
| 16 | `astropy__astropy-14995` | <15m | 3 | 2 | 3 | **8/8** | ✅ Exact | 41 | 6 | 118,039 | 509 | 49 |
| 17 | `astropy__astropy-7166` | <15m | 3 | 2 | 3 | **8/8** | ✅ Exact | 44 | 7 | 122,176 | 707 | 107 |
| 18 | `astropy__astropy-7336` | <15m | 3 | 2 | 3 | **8/8** | ✅ Exact | 56 | 5 | 108,600 | 445 | 110 |
| 19 | `astropy__astropy-7606` | 15m–1h | 2 | 2 | 2 | **6/8** | ⚠️ Partial | 94 | 8 | 246,597 | 1,477 | 604 |
| 20 | `astropy__astropy-7671` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 117 | 8 | 143,580 | 1,537 | 540 |
| 21 | `astropy__astropy-8707` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 175 | 18 | 559,647 | 4,934 | 941 |
| 22 | `astropy__astropy-8872` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 99 | 10 | 261,666 | 3,112 | 814 |
| | **TOTAL** | | **64/66** | **44/44** | **52/66** | **160/176** | **90.9%** | **5,919 s** | **382** | **14,422,429** | **199,951** | **78,548** |
| | **AVERAGE** | | | | | **7.3/8** | | **269 s** | **17** | **655,565** | **9,089** | **3,570** |

---

## Dimension Breakdown

| Dimension | Score | Max | % |
|-----------|-------|-----|---|
| Root cause identification | 64 | 66 | **97.0%** |
| Correct file(s) | 44 | 44 | **100.0%** |
| Correct patch / code change | 52 | 66 | **78.8%** |
| **Overall** | **160** | **176** | **90.9%** |

> Perfect file identification across all 22 tasks. MCP knowledge graph access eliminated both hallucinated-code-state failures from the raw run — `8707` and `14369` both jump to near-perfect or better. Patch quality is the remaining gap.

---

## Token Usage Summary

| Metric | Total | Avg/task |
|--------|-------|----------|
| Input tokens | 14,422,429 | 655,565 |
| Output tokens | 199,951 | 9,089 |
| Reasoning tokens | 78,548 | 3,570 |
| Cache read | 0 | — |
| Cache write | 0 | — |
| API steps | 329 | 15 |
| Tool calls | 382 | 17 |
| Total time | 5,919 s | 269 s |
| **Cost** | **$0.00** | **$0.00** |

> MCP mode is dramatically more efficient than raw: average input tokens drop from 1,320,956 (raw) to 655,565 (MCP) — a 50% reduction. Average time drops from 859 s to 269 s — a 69% reduction. The knowledge graph lets the model navigate to the right files in fewer hops without exhaustive repo traversal. `14598` remains the heaviest task at 997 s and 1.4M input tokens.

---

## Per-Task Answer Comparison

### Task 1 — `12907` — ✅ Exact (8/8)

**Issue:** `separability_matrix` wrong for nested `CompoundModels`

| | GT | Qwen MCP |
|---|---|---|
| File | `separable.py` | `separable.py` |
| Fix | `cright[-right.shape[0]:, -right.shape[1]:] = right` | **Identical one-line diff** |

Correct diagnosis of the `= 1` typo in `_cstack`. Proposes the exact fix with clear reasoning. MCP took 797 s and 26 API calls vs raw's 3,015 s and 79 steps — 73% faster on an identical result.

---

### Task 2 — `13033` — ✅ Exact (8/8)

**Issue:** `TimeSeries` misleading exception on required column removal

| | GT | Qwen MCP |
|---|---|---|
| File | `core.py` | `core.py` |
| GT fix | `as_scalar_or_list_str()` helper; used in both error paths | **Same helper, same two-path usage; `self.colnames[:len(required_columns)]` for found-columns message** |

MCP produces the exact same structural approach as GT: adds `as_scalar_or_list_str()` helper and updates both error blocks. The raw run achieved only 7/8 (different branching approach, "expected" vs "required" wording). MCP gets credit for matching GT's architecture including the helper function name.

---

### Task 3 — `13236` — ✅ Exact (8/8)

**Issue:** Remove auto-transform of structured ndarray into `NdarrayMixin`

| | GT | Qwen MCP |
|---|---|---|
| File | `table.py` | `table.py` |
| GT fix | Remove 6-line auto-view block in `_convert_data_to_col` | Removes same block; additionally updates test assertions to expect `Column` instead of `NdarrayMixin` |

Exact match on the core fix. The test file guidance is a bonus — GT doesn't update tests but Qwen's test changes are correct and needed.

---

### Task 4 — `13398` — ✅ Near-perfect (7/8)

**Issue:** Add ITRS ↔ AltAz/HADec topocentric transforms

| | GT | Qwen MCP |
|---|---|---|
| Files | 4 files + new `itrs_observed_transforms.py` | Same 4 files + new `itrs_observed_transforms.py` |
| Fix | Full implementation with rotation matrices, refraction functions, registered transforms | Correct architectural plan: `location` attr on ITRS, new module structure, `EarthLocation.get_itrs()` topocentric mode; no executable code |

**−1 Patch:** MCP correctly identifies all four affected files and the correct design — `location` frame attribute on ITRS, rotation matrix builders, refraction handling, both transforms registered on the frame graph, `EarthLocation.get_itrs()` update. Root cause understanding is complete. However, the answer is a design plan rather than executable code; the raw run provided actual implementation. Structurally equivalent in intent, short on code.

---

### Task 5 — `13453` — ✅ Exact (8/8)

**Issue:** HTML writer ignores `formats` argument

| | GT | Qwen MCP |
|---|---|---|
| File | `html.py` | `html.py` |
| GT fix | `self.data.cols = cols` + `self.data._set_col_formats()` | **Identical two-line fix; additionally propagates format to multicolumn splits** |

MCP exactly matches GT. The raw run got only 7/8 by inlining the format loop instead of calling `_set_col_formats()` and missing `self.data.cols = cols`. MCP correctly identifies both missing calls. The bonus `new_col.info.format = col.info.format` for multicol handling is correct and not present in GT.

---

### Task 6 — `13579` — ⚠️ Partial (6/8)

**Issue:** `SlicedLowLevelWCS.world_to_pixel_values` uses hardcoded `1.0` for dropped dimensions

| | GT | Qwen MCP |
|---|---|---|
| File | `sliced_wcs.py` | `sliced_wcs.py` |
| GT fix | Compute `sliced_out_world_coords` at pixel `[0,…,0]`; substitute for `1.` placeholder | Build `world_arrays_full` with 0-filled dropped dims → approximate pixel via `world_to_pixel_values` → compute `sliced_out_world_coords` via `pixel_to_world_values` |

**−2 Patch:** MCP's approach is more ambitious — it tries to find the actual pixel position for the input world coordinates rather than using a fixed zero reference. However, the round-trip (`world→pixel→world`) uses a `world_arrays_full` with zero placeholders for dropped dimensions, making the approximation no better than GT's constant reference in the general case, while introducing potential circularity for non-trivial WCS projections. GT's stable zero reference is simpler and correct. Root cause diagnosis is accurate; file is correct; the patch mechanism diverges too far.

---

### Task 7 — `13977` — ✅ Near-perfect (7/8)

**Issue:** `Quantity.__array_ufunc__` should return `NotImplemented` for duck types

| | GT | Qwen MCP |
|---|---|---|
| File | `quantity.py` | `quantity.py` |
| GT fix | Wrap entire `__array_ufunc__` body in one try/except; return `NotImplemented` | Three separate try/except blocks: around `converters_and_unit()`, around `check_output()`, and around each converter call |

**−1 Patch:** MCP's three-point protection is broader than the raw run's single-converter wrapping and covers the primary failure path (`converters_and_unit()`). However, it still fragments what GT handles in one catch — any exception path between the three guards that Qwen missed would fall through. GT's whole-body wrap is the correct, complete fix. Still a significant improvement over the raw 6/8.

---

### Task 8 — `14096` — ✅ Near-perfect (7/8)

**Issue:** `SkyCoord` subclass property gives misleading `AttributeError`

| | GT | Qwen MCP |
|---|---|---|
| File | `sky_coordinate.py` | `sky_coordinate.py` |
| GT fix | `return self.__getattribute__(attr)` — 2 lines | MRO walk; `return descriptor.fget(self)` for property descriptors |

**−1 Patch:** Same as raw run. Correct file, correct diagnosis. MRO walk approach handles `property` descriptors correctly — the `return` ensures the original AttributeError propagates — but is more complex than GT's 2-line `__getattribute__` call and only covers `property`, not `cached_property` or C-extension descriptors.

---

### Task 9 — `14182` — ✅ Exact (8/8)

**Issue:** RST writer needs `header_rows` support

| | GT | Qwen MCP |
|---|---|---|
| File | `rst.py` | `rst.py` |
| GT fix | `__init__(header_rows=None)` + forward to `FixedWidth.__init__()`; dynamic `start_line` | `def __init__(self, header_rows=None): super().__init__(delimiter_pad=None, bookend=False, header_rows=header_rows)` |

MCP produces the minimal correct fix: add `header_rows=None` and delegate to `FixedWidth.__init__()`, which already handles everything. The raw run rewrote the entire class unnecessarily. MCP's one-method change is actually cleaner and matches GT's structural intent.

---

### Task 10 — `14309` — ✅ Near-perfect (7/8)

**Issue:** `is_fits` IndexError with empty args

| | GT | Qwen MCP |
|---|---|---|
| File | `connect.py` | `connect.py` |
| GT fix | Early `return filepath.lower().endswith(...)` making `args[0]` unreachable | `len(args) > 0 and isinstance(args[0], ...)` inline guard |

**−1 Patch:** Guard approach is functionally correct for all inputs; structurally different from GT's logic restructure. Equivalent to raw's approach and result.

---

### Task 11 — `14365` — ⚠️ Partial (6/8)

**Issue:** QDP reader fails on lowercase commands

| | GT | Qwen MCP |
|---|---|---|
| File | `qdp.py` | `qdp.py` |
| GT fix | `re.IGNORECASE` on `_line_type_re` **+** `v.upper() == "NO"` in data loop | `re.IGNORECASE` on `_line_type_re` only |

**−2 Patch:** Adds the `IGNORECASE` flag correctly. Entirely misses the `v.upper() == "NO"` fix needed in the data-value parsing loop, meaning lowercase `no` in numeric data columns still causes errors. Identical gap to the raw run — persistent cross-mode blind spot on this task.

---

### Task 12 — `14369` — ✅ Near-perfect (7/8)

**Issue:** CDS/MRT unit parser wrong associativity for chained division (`J/m/s/kpc2`)

| | GT | Qwen MCP |
|---|---|---|
| Files | `cds.py` + `cds_parsetab.py` | `cds.py` + note to regenerate `cds_parsetab.py` |
| GT fix | Change grammar rule operand order in `p_division_of_units`; regenerate table | Add explicit left-recursive rule `division_of_units DIVISION unit_expression`; use `product_of_units` on left side |

**Dramatic improvement over raw (3/8 → 7/8).** The raw run hallucinated that `cds.py` was already fixed and only deleted the parsetab cache. MCP correctly reads the grammar, identifies the right-associativity bug, and proposes a grammar change in `cds.py`. The specific grammar rewrite differs from GT (GT flips operand order; MCP adds explicit left-recursion rules), but both target left-associativity. MCP's multi-rule approach is more elaborate but logically correct.

---

### Task 13 — `14508` — ✅ Exact (8/8)

**Issue:** FITS float formatting: `:.16G` expands `0.009125` to `0.009124999999999999`

| | GT | Qwen MCP |
|---|---|---|
| File | `card.py` | `card.py` |
| Fix | Replace `f"{value:.16G}"` with `str(value).replace("e","E")` | **Identical replacement** |

MCP produces the exact fix in 80 s with 11 API calls — the most efficient solve in this set. Correctly identifies `_format_float` and the rationale (David Gay's shortest-repr algorithm in Python 3.1+).

---

### Task 14 — `14539` — ✅ Exact (8/8)

**Issue:** `FITSDiff` misses variable-length array columns with format `Q`

| | GT | Qwen MCP |
|---|---|---|
| File | `diff.py` | `diff.py` |
| Fix | `elif "P" in col.format or "Q" in col.format:` | **Identical one-line diff; complete analysis of P vs Q format semantics** |

Exact match with thorough root cause analysis explaining the 32-bit vs 64-bit VLA descriptor distinction.

---

### Task 15 — `14598` — ⚠️ Partial (5/8)

**Issue:** FITS CONTINUE card round-trip corrupts values containing `''`

| | GT | Qwen MCP |
|---|---|---|
| File | `card.py` | `card.py` |
| GT fix | 1) Add `$` anchor to `_strg_comment_RE`; 2) Remove `.replace("''", "'")` in `_split` | Restructure `_strg` regex from `[ -~]+?` to `[^']+` to exclude single quotes from main match group |

**−3 Patch:** MCP identifies the file and the regex as the problem site, but proposes a fix to the wrong regex (`_strg` at line 67) rather than adding a `$` anchor to `_strg_comment_RE`. MCP's `[^']+ `change would affect how the value regex matches but doesn't address the cross-card boundary matching problem GT fixes with the `$` anchor. The `.replace("''", "'")` / `re.sub` unescaping distinction is also mishandled — MCP keeps the unescaping via `re.sub` where GT removes it from `_split`. Highest effort task (997 s, 28 API calls) with a partial result.

---

### Task 16 — `14995` — ✅ Exact (8/8)

**Issue:** `NDDataArithmetic` mask arithmetic crashes with `TypeError` when one operand has no mask

| | GT | Qwen MCP |
|---|---|---|
| File | `ndarithmetic.py` | `ndarithmetic.py` |
| GT fix | Replace `elif operand is None:` with `elif operand.mask is None:` | **Identical one-line fix with precise explanation** |

MCP solves this in 41 s with 4 API calls — the fastest solve in this set. The knowledge graph immediately surfaces the right method and the stale guard that was never triggered.

---

### Task 17 — `7166` — ✅ Exact (8/8)

**Issue:** `InheritDocstrings` metaclass does not inherit docstrings for properties

| | GT | Qwen MCP |
|---|---|---|
| File | `misc.py` | `misc.py` |
| Fix | `(inspect.isfunction(val) or inspect.isdatadescriptor(val))` | **Identical condition** |

43 s, 4 API calls. MCP correctly identifies that `property` is a data descriptor and adds `inspect.isdatadescriptor()` alongside `inspect.isfunction()`.

---

### Task 18 — `7336` — ✅ Exact (8/8)

**Issue:** `@quantity_input` crashes on functions annotated `-> None`

| | GT | Qwen MCP |
|---|---|---|
| File | `decorators.py` | `decorators.py` |
| GT fix | Single condition: `not in (inspect.Signature.empty, None)` | **Identical condition; additionally notes NoneType/NoReturn edge cases** |

MCP produces the exact GT fix in 56 s. The raw run got 7/8 by adding redundant extra guards; MCP keeps it to the single in-place condition change.

---

### Task 19 — `7606` — ⚠️ Partial (6/8)

**Issue:** `UnrecognizedUnit.__eq__` raises `TypeError` when compared to `None`

| | GT | Qwen MCP |
|---|---|---|
| File | `core.py` | `core.py` |
| GT fix | 1) `UnitBase.__eq__`: `return False` → `return NotImplemented`; 2) `UnrecognizedUnit.__eq__`: try/except returning `NotImplemented`; `isinstance(other, type(self))` | `UnrecognizedUnit.__eq__`: try/except catching `TypeError`, returning `NotImplemented` |

**−2 Patch:** MCP correctly wraps `UnrecognizedUnit.__eq__` with try/except and returns `NotImplemented` — better than raw's `if other is None: return False` guard (which returns `False` instead of the protocol-correct `NotImplemented`). However, MCP still misses the `UnitBase.__eq__` change and the `isinstance(other, type(self))` refinement. RC partial since the broader fix location in `UnitBase` is missed.

---

### Task 20 — `7671` — ✅ Near-perfect (7/8)

**Issue:** `minversion()` raises `TypeError` for dev/rc version strings like `1.14dev`

| | GT | Qwen MCP |
|---|---|---|
| File | `introspection.py` | `introspection.py` |
| GT fix | Inline regex strip of non-numeric suffix from `version` only | Module-level `_normalize_version()` helper; normalises both `version` and `have_version` |

**−1 Patch:** MCP normalises both arguments where GT only normalises `version`. More defensive but over-engineered relative to GT. The regex (numeric prefix extraction) is correct. Same assessment as raw run.

---

### Task 21 — `8707` — ✅ Exact (8/8)

**Issue:** `Card.fromstring` and `Header.fromstring` should accept `bytes` input

| | GT | Qwen MCP |
|---|---|---|
| Files | `card.py` + `header.py` | `card.py` + `header.py` |
| GT fix | `if isinstance(image, bytes): image = image.decode('latin1')` in both `fromstring` methods | **Identical fix in both methods; correct `latin1` rationale (FITS ASCII superset, no decode errors)** |

**Biggest MCP gain: 2/8 → 8/8.** The raw run hallucinated that the implementation already handled bytes and only proposed a test. MCP correctly reads both `Card.fromstring` and `Header.fromstring`, identifies neither has a bytes check, and produces the exact GT fix for both. The `latin1` encoding choice and rationale matches GT precisely.

---

### Task 22 — `8872` — ✅ Near-perfect (7/8)

**Issue:** `Quantity` casts `float16`/`float32` arrays to `float64`

| | GT | Qwen MCP |
|---|---|---|
| File | `quantity.py` | `quantity.py` |
| GT fix | Replace `np.can_cast(np.float32, value.dtype)` with `value.dtype.kind in 'iu'` at two locations | Replace with `value.dtype.kind in 'fc'` at two locations |

**−1 Patch:** Both approaches correctly preserve `float16`/`float32`. GT uses `kind in 'iu'` (only promote integers/unsigned); MCP uses `kind in 'fc'` (preserve floats/complex). Semantically equivalent outcome for the failing case; MCP's condition is the complement direction. Correct fix, different guard expression.

---

## Grade Distribution

| Grade | Count | Tasks |
|-------|-------|-------|
| ✅ Exact (8/8) | 11 | 1, 2, 3, 5, 9, 13, 14, 16, 17, 18, 21 |
| ✅ Near-perfect (7/8) | 7 | 4, 7, 8, 10, 12, 20, 22 |
| ⚠️ Partial (5–6/8) | 4 | 6, 11, 15, 19 |
| ❌ Fail (≤4/8) | 0 | — |

**Exact + Near-perfect: 18/22 (81.8%)**

---

## MCP vs Raw: Head-to-Head Comparison (22 tasks)

| Metric | Raw (22 tasks) | MCP (22 tasks) | Delta |
|--------|---------------|----------------|-------|
| Overall score | 146/176 (83.0%) | **160/176 (90.9%)** | **+7.9 pp** |
| Exact (8/8) | 7 | **11** | +4 |
| Near-perfect (7/8) | 9 | 7 | −2 |
| Partial (5–6/8) | 4 | 4 | 0 |
| Fail (≤4/8) | 2 | **0** | **−2** |
| Root cause % | 92.4% | **97.0%** | +4.6 pp |
| File ID % | 95.5% | **100.0%** | +4.5 pp |
| Patch quality % | 65.2% | **78.8%** | +13.6 pp |
| Total time | 18,894 s | **5,919 s** | **−68.7%** |
| Avg time/task | 859 s | **269 s** | −68.7% |
| Avg input tok/task | 1,320,956 | **655,565** | **−50.4%** |
| Avg output tok/task | 32,371 | **9,089** | −71.9% |
| Cost | $0.00 | $0.00 | — |

---

## Cross-Model Comparison: Shared 11-Task Subset

*Tasks 12907, 13033, 13236, 13398, 13453, 13579, 13977, 14096, 14182, 14309, 14365. Sonnet/GPT figures from raw reports.*

| Metric | Qwen MCP (11) | Qwen Raw (11) | GPT-5.4 Mini | GPT-5.4 Nano | Sonnet 4.6 |
|--------|--------------|--------------|-------------|-------------|------------|
| Overall score | **80/88 (90.9%)** | 79/88 (89.8%) | 74/88 (84.1%) | 64/88 (72.7%) | 83/88 (94.3%) |
| Exact (8/8) | **5** | 4 | 3 | 0 | 8 |
| Near-perfect (7/8) | 4 | 5 | 5 | 5 | 1 |
| Partial (5–6/8) | 2 | 2 | 1 | 3 | 1 |
| Fail (≤4/8) | 0 | 0 | 1 | 2 | 0 |
| Root cause % | **100%** | 100% | 93.9% | 87.9% | **100%** |
| File ID % | **100%** | 100% | 95.5% | 95.5% | **100%** |
| Patch quality % | **75.8%** | 72.7% | 66.7% | 42.4% | 81.8% |
| Avg cost/task | **$0.00** | $0.00 | $0.069 | $0.051 | $0.538 |
| Avg time/task | **346 s** | 1,016 s | 843 s | 1,841 s | 310 s |
| Avg input tok/task | **935,646** | 1,706,354 | 46,310 | 93,142 | ~97,000† |

*† Sonnet uses Anthropic-side cache — raw token counts not directly comparable.*

---

## Key Observations

**MCP eliminates both raw hallucination failures.** Tasks `8707` and `14369` were the two raw failures, both caused by Qwen incorrectly asserting the implementation already contained the fix. With MCP, Qwen reads the actual graph-indexed file contents, correctly identifies the missing bytes-decode in both `fromstring` methods (`8707`) and the true grammar associativity bug in `cds.py` (`14369`). Both jump to 7–8/8.

**50% token reduction with higher accuracy.** MCP mode halves input token consumption while improving overall score by 7.9 pp. The knowledge graph's targeted file retrieval replaces exhaustive repo crawling — the average task uses 655K input tokens vs 1.3M raw.

**3× faster wall-clock time.** Average task time drops from 859 s to 269 s. The fastest MCP task (`14995`) completes in 41 s with 4 API calls. The raw equivalent took 1,560 s and 20 steps.

**Perfect file identification.** 100% (44/44) file accuracy vs 95.5% raw. The graph's semantic indexing guides the model to the right files without trial-and-error reads.

**Persistent partial failures unchanged.** Tasks `14365` (missing `v.upper()`) and `14598` (wrong regex fix) remain at the same difficulty level in both modes. These are structural traps — the fix requires a non-obvious second change that the model consistently overlooks across all modes tested.

**MCP narrows the gap to Sonnet.** On the shared 11-task subset, Qwen MCP (90.9%) vs Sonnet (94.3%) is a 3.4 pp gap, down from 4.5 pp raw. Qwen MCP leads GPT-5.4 Mini by 6.8 pp at zero cost — the strongest free-tier result across all runs evaluated.

**Task `13453` promotion highlights MCP's code-reading advantage.** The raw run inlined the format loop instead of calling `_set_col_formats()` because it couldn't read the base class deeply. MCP retrieved `core.py`'s `BaseData` implementation via the graph, identified the exact two missing calls, and matched GT precisely.
