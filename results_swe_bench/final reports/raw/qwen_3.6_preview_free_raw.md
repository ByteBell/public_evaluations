# Qwen 3.6 Plus (Free) Raw on Kilo — SWE-Bench Evaluation Report

**Dataset:** `princeton-nlp/SWE-bench_Verified` — `astropy/astropy`
**Evaluated:** 22 tasks from `astropy_tasks.json`
**Date:** 2026-04-03
**Judge:** Claude Code (claude-sonnet-4-6)
**Ground truth source:** `results_swe_bench/astropy_tasks.json`
**Raw responses:** `results_swe_bench/auto_run_on_raw_kilo_qwen_qwen3.6-plus:free/*/answer.json`
**Mode:** Kilo agent with direct repo access (no MCP knowledge graph) · Model: `qwen/qwen3.6-plus:free`
**Cost:** $0.00 — free tier; reported as $0.000 for all tasks. Evaluation focuses on quality, time, and token usage.

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
| 1 | `astropy__astropy-12907` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 3,015 | 79 | 5,406,948 | 68,714 | 51,874 |
| 2 | `astropy__astropy-13033` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 228 | 8 | 230,619 | 9,644 | 7,650 |
| 3 | `astropy__astropy-13236` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 1,123 | 50 | 1,760,658 | 28,198 | 18,516 |
| 4 | `astropy__astropy-13398` | 1–4h | 3 | 2 | 3 | **8/8** | ✅ Exact | 1,599 | 90 | 6,370,312 | 26,089 | 6,085 |
| 5 | `astropy__astropy-13453` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 1,089 | 46 | 2,736,007 | 12,970 | 3,550 |
| 6 | `astropy__astropy-13579` | 1–4h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 81 | 7 | 200,000 | 3,653 | 2,306 |
| 7 | `astropy__astropy-13977` | 15m–1h | 3 | 2 | 1 | **6/8** | ⚠️ Partial | 1,301 | 25 | 706,552 | 41,960 | 36,246 |
| 8 | `astropy__astropy-14096` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 1,842 | 18 | 363,359 | 21,973 | 18,136 |
| 9 | `astropy__astropy-14182` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 142 | 9 | 275,836 | 7,027 | 4,464 |
| 10 | `astropy__astropy-14309` | <15m | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 285 | 13 | 426,776 | 16,366 | 14,026 |
| 11 | `astropy__astropy-14365` | 15m–1h | 3 | 2 | 1 | **6/8** | ⚠️ Partial | 472 | 11 | 292,824 | 19,674 | 17,464 |
| 12 | `astropy__astropy-14369` | 1–4h | 2 | 1 | 0 | **3/8** | ❌ Fail | 650 | 43 | 2,116,053 | 32,459 | 22,896 |
| 13 | `astropy__astropy-14508` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 140 | 18 | 347,359 | 5,539 | 2,917 |
| 14 | `astropy__astropy-14539` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 56 | 7 | 266,137 | 2,402 | 1,478 |
| 15 | `astropy__astropy-14598` | 15m–1h | 2 | 2 | 1 | **5/8** | ⚠️ Partial | 2,027 | 27 | 1,307,115 | 140,854 | 134,556 |
| 16 | `astropy__astropy-14995` | <15m | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 1,560 | 20 | 475,210 | 120,912 | 117,438 |
| 17 | `astropy__astropy-7166` | <15m | 3 | 2 | 3 | **8/8** | ✅ Exact | 661 | 28 | 668,175 | 32,525 | 26,900 |
| 18 | `astropy__astropy-7336` | <15m | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 755 | 28 | 716,988 | 31,024 | 25,118 |
| 19 | `astropy__astropy-7606` | 15m–1h | 2 | 2 | 1 | **5/8** | ⚠️ Partial | 170 | 12 | 201,422 | 6,040 | 4,240 |
| 20 | `astropy__astropy-7671` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 356 | 19 | 483,562 | 12,086 | 7,386 |
| 21 | `astropy__astropy-8707` | 15m–1h | 1 | 1 | 0 | **2/8** | ❌ Fail | 416 | 28 | 765,621 | 14,412 | 8,830 |
| 22 | `astropy__astropy-8872` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 926 | 50 | 2,943,499 | 57,650 | 46,958 |
| | **TOTAL** | | **61/66** | **42/44** | **43/66** | **146/176** | **83.0%** | **18,894 s** | **636** | **29,061,032** | **712,171** | **579,034** |
| | **AVERAGE** | | | | | **6.6/8** | | **859 s** | **29** | **1,320,956** | **32,371** | **26,320** |

---

## Dimension Breakdown

| Dimension | Score | Max | % |
|-----------|-------|-----|---|
| Root cause identification | 61 | 66 | **92.4%** |
| Correct file(s) | 42 | 44 | **95.5%** |
| Correct patch / code change | 43 | 66 | **65.2%** |
| **Overall** | **146** | **176** | **83.0%** |

> The first 11 tasks showed 100% RC and file accuracy. The expanded 22-task set reveals two failure cases (`8707`, `14369`) that pull these numbers down. Patch quality remains the primary gap.

---

## Token Usage Summary

| Metric | Total | Avg/task |
|--------|-------|----------|
| Input tokens | 29,061,032 | 1,320,956 |
| Output tokens | 712,171 | 32,371 |
| Reasoning tokens | 579,034 | 26,320 |
| Cache read | 0 | — |
| Cache write | 0 | — |
| API steps | 636 | 29 |
| Total time | 18,894 s | 859 s |
| **Cost** | **$0.00** | **$0.00** |

> No prompt caching throughout. `14598` consumed 134K reasoning tokens in 27 steps for a 2-line fix. `8872` used 2.9M input tokens across 50 steps. The new batch averages fewer input tokens per task (937K vs 1.7M in the first 11), suggesting the newer tasks were simpler in scope.

---

## Per-Task Answer Comparison

### Task 1 — `12907` — ✅ Exact (8/8)

**Issue:** `separability_matrix` wrong for nested `CompoundModels`

| | GT | Qwen |
|---|---|---|
| File | `separable.py` | `separable.py` |
| Fix | `cright[-right.shape[0]:, -right.shape[1]:] = right` | **Identical one-line diff** |

Qwen correctly identifies the `= 1` typo in `_cstack` and produces the exact GT patch — despite taking 3,015 s and 79 steps (5.4M input tokens) to arrive at a change that is literally one character.

---

### Task 2 — `13033` — ✅ Near-perfect (7/8)

**Issue:** `TimeSeries` misleading exception on required column removal

| | GT | Qwen |
|---|---|---|
| File | `core.py` | `core.py` |
| GT fix | `as_scalar_or_list_str()` helper; used in both error paths | Singular/plural branching with `column_word` variable; uses "expected" instead of "required" in message |

**−1 Patch:** Achieves the correct user-visible behavior (full-list message, singular vs plural form) but uses a different structural approach: explicit if/else branches per path vs a reusable helper. Also uses "expected" wording where GT uses "required".

---

### Task 3 — `13236` — ✅ Exact (8/8)

**Issue:** Remove auto-transform of structured ndarray into `NdarrayMixin`

| | GT | Qwen |
|---|---|---|
| File | `table.py` | `table.py` |
| GT fix | Remove 6-line auto-view block in `_convert_data_to_col` | Removes the exact same block; additionally removes the `NdarrayMixin` import |

Exact match on the core fix. Qwen also removes the `NdarrayMixin` import which is a reasonable cleanup not present in GT but does not break anything.

---

### Task 4 — `13398` — ✅ Exact (8/8)

**Issue:** Add ITRS ↔ AltAz/HADec topocentric transforms

| | GT | Qwen |
|---|---|---|
| Files | 4 files + new `itrs_observed_transforms.py` | Same 4 files + complete new `itrs_observed_transforms.py` |
| Fix | New transform module; CIRS/TETE chain simplification; `__init__.py` import | Full new module with rotation matrices, refraction functions, `itrs_to_observed`/`observed_to_itrs` transforms registered on the frame graph |

**Best answer in this evaluation set.** Qwen produces a complete, architecturally correct implementation: `itrs_to_altaz_mat`, `itrs_to_hadec_mat`, `altaz_to_hadec_mat`, `add_refraction`, `remove_refraction`, and both transform functions registered with `FunctionTransformWithFiniteDifference` — matching the GT's approach in every structural respect. Also correctly simplifies `intermediate_rotation_transforms.py`, `cirs_observed_transforms.py`, and adds the `__init__.py` import. Took 90 steps and 6.4M input tokens to get there.

---

### Task 5 — `13453` — ✅ Near-perfect (7/8)

**Issue:** HTML writer ignores `formats` argument

| | GT | Qwen |
|---|---|---|
| File | `html.py` | `html.py` |
| GT fix | `self.data.cols = cols` + `self.data._set_col_formats()` | Iterates cols and sets `col.info.format = self.data.formats[col.info.name]` directly |

**−1 Patch:** Qwen inlines the format-setting loop rather than delegating to `_set_col_formats()`. This replicates what `_set_col_formats()` does internally but misses `self.data.cols = cols`, which may be needed for other parts of the write path. Functionally similar for simple cases.

---

### Task 6 — `13579` — ✅ Near-perfect (7/8)

**Issue:** `SlicedLowLevelWCS.world_to_pixel_values` uses hardcoded `1.0` for dropped dimensions

| | GT | Qwen |
|---|---|---|
| File | `sliced_wcs.py` | `sliced_wcs.py` |
| GT fix | Compute `sliced_out_world_coords` at pixel `[0,…,0]`; substitute for `1.` placeholder | Build `slice_pixel_arrays` using `slice.start or 0` per pixel axis; use to reconstruct reference world coords |

**−1 Patch:** Qwen's reference pixel (`slice.start or 0`) is a reasonable choice but differs from GT's constant zero reference across all kept axes. For non-zero-based slices the results will diverge from GT. The structural approach (using a pixel reference to compute world coords for dropped dimensions) is correct; only the reference value differs.

---

### Task 7 — `13977` — ⚠️ Partial (6/8)

**Issue:** `Quantity.__array_ufunc__` should return `NotImplemented` for duck types

| | GT | Qwen |
|---|---|---|
| File | `quantity.py` | `quantity.py` |
| GT fix | Wrap entire `__array_ufunc__` body in try/except; return `NotImplemented` | Wraps individual `converter(input_)` calls in a per-element try/except inside the inputs loop |

**−2 Patch:** Wrapping at the individual converter call level catches the primary failure but leaves later code paths (unit validation in `check_output`, `_result_as_quantity`) unprotected. GT requires wrapping the full body. Same partial pattern as Opus raw and Sonnet MCP — consistent cross-model failure on this task.

---

### Task 8 — `14096` — ✅ Near-perfect (7/8)

**Issue:** `SkyCoord` subclass property gives misleading `AttributeError`

| | GT | Qwen |
|---|---|---|
| File | `sky_coordinate.py` | `sky_coordinate.py` |
| GT fix | `return self.__getattribute__(attr)` — 2 lines | MRO walk; `return descriptor.__get__(self, type(self))` for property descriptors |

**−1 Patch:** Qwen's MRO walk correctly uses `return` — unlike some other models' versions of this approach, the AttributeError from the property WILL propagate since the path exits via `return`. However, the solution is more complex than needed and only handles `property` descriptors (not `cached_property` or C-extension descriptors). GT's `__getattribute__` handles all cases in 2 lines.

---

### Task 9 — `14182` — ✅ Exact (8/8)

**Issue:** RST writer needs `header_rows` support

| | GT | Qwen |
|---|---|---|
| File | `rst.py` | `rst.py` |
| GT fix | Remove `start_line = 3`; `__init__(header_rows=None)`; dynamic write/read | Complete class rewrite: `__init__(header_rows=None)`, `write` using `idx = len(self.header.header_rows)`, `read` with dynamic `start_line = 2 + len(self.header.header_rows)` |

Full implementation. Qwen provides a complete fixed class with all three required changes plus restores `ends[-1] = None` in `SimpleRSTHeader.get_fixedwidth_params`. Minor: uses `delimiter_pad=None` vs GT's `delimiter_pad=""`, but the overall architecture is correct.

---

### Task 10 — `14309` — ✅ Near-perfect (7/8)

**Issue:** `is_fits` IndexError with empty args

| | GT | Qwen |
|---|---|---|
| File | `connect.py` | `connect.py` |
| GT fix | Early `return filepath.lower().endswith(...)` making `args[0]` unreachable | `if not args: return False` guard before `isinstance(args[0], …)` |

**−1 Patch:** Guard approach works correctly; structurally different from GT's logic restructure. Equivalent for all test inputs.

---

### Task 11 — `14365` — ⚠️ Partial (6/8)

**Issue:** QDP reader fails on lowercase commands

| | GT | Qwen |
|---|---|---|
| File | `qdp.py` | `qdp.py` |
| GT fix | `re.IGNORECASE` on `_line_type_re` **+** `v.upper() == "NO"` in data loop | `re.IGNORECASE` on `_line_type_re`; `_command_re` written in lowercase |

**−2 Patch:** Adds `re.IGNORECASE` correctly (and correctly suggests lowercase `_command_re` to be consistent), but entirely misses the `v.upper() == "NO"` fix needed in the data-value parsing loop. Lowercase `no` in data lines will still cause errors. Same gap as nano and mini.

---

### Task 12 — `14369` — ❌ Fail (3/8)

**Issue:** CDS/MRT unit parser wrong associativity for chained division (`J/m/s/kpc2`)

| | GT | Qwen |
|---|---|---|
| Files | `cds.py` + `cds_parsetab.py` | `cds_parsetab.py` only |
| GT fix | Change grammar rule from `unit_expression DIVISION combined_units` → `combined_units DIVISION unit_expression` in `cds.py`; regenerate `cds_parsetab.py` | Delete `cds_parsetab.py` to force regeneration; claims `cds.py` already has the correct grammar |

**−5 Patch:** Qwen incorrectly asserts that `cds.py` already contains the corrected grammar rule and only the cached parsetab is stale. In reality, the grammar rule in `cds.py` still needs to be changed. Deleting the parsetab without fixing the source would regenerate the same broken grammar. The root cause (division associativity) is partially understood but the diagnosis of code state is wrong.

---

### Task 13 — `14508` — ✅ Exact (8/8)

**Issue:** FITS float formatting: `:.16G` expands `0.009125` to `0.009124999999999999`

| | GT | Qwen |
|---|---|---|
| File | `card.py` | `card.py` |
| Fix | Replace `f"{value:.16G}"` with `str(value).replace("e","E")`; remove old `.0` and exponent normalisation code | Identical replacement; same truncation logic retained |

Qwen produces the exact same function body as GT. The only difference is Qwen omits the inline comments added by GT — functionally identical.

---

### Task 14 — `14539` — ✅ Exact (8/8)

**Issue:** `FITSDiff` misses variable-length array columns with format `Q`

| | GT | Qwen |
|---|---|---|
| File | `diff.py` | `diff.py` |
| Fix | `elif "P" in col.format or "Q" in col.format:` | Identical one-line diff |

Qwen produces the exact patch, presented as a proper unified diff.

---

### Task 15 — `14598` — ⚠️ Partial (5/8)

**Issue:** FITS CONTINUE card round-trip corrupts values containing `''`

| | GT | Qwen |
|---|---|---|
| File | `card.py` | `card.py` |
| GT fix | 1) Add `$` anchor to `_strg_comment_RE` regex; 2) Remove `.replace("''", "'")` in `_split` | Remove `if value.endswith("''"): value = value[:-2] + "'"` block in `_split` |

**−3 Patch:** Qwen identifies the double-unescaping issue in `_split` but the code it proposes removing (`if value.endswith(...)`) does not match the actual offending line in GT (`.replace("''","'")` chained to `rstrip()`). More critically, Qwen entirely misses the `$` anchor fix to the `_strg_comment_RE` regex, which is required to prevent the regex from matching across continuation boundaries.

---

### Task 16 — `14995` — ✅ Near-perfect (7/8)

**Issue:** `NDDataArithmetic` mask arithmetic crashes with `TypeError` when one operand has no mask

| | GT | Qwen |
|---|---|---|
| File | `ndarithmetic.py` | `ndarithmetic.py` |
| GT fix | Replace `elif operand is None:` with `elif operand.mask is None:` | `elif operand is None or operand.mask is None:` |

**−1 Patch:** Qwen's OR condition is defensive but redundant — the `operand is None` branch is already handled earlier in the method. GT removes the stale guard and replaces it cleanly. Both fix the crash; Qwen's version is slightly over-specified.

---

### Task 17 — `7166` — ✅ Exact (8/8)

**Issue:** `InheritDocstrings` metaclass does not inherit docstrings for properties

| | GT | Qwen |
|---|---|---|
| File | `misc.py` | `misc.py` |
| Fix | `(inspect.isfunction(val) or inspect.isdatadescriptor(val))` | Identical condition |

Qwen produces the exact fix. Also adds a clarifying comment (`# inspect.isfunction returns False for properties`) which is reasonable but not in GT.

---

### Task 18 — `7336` — ✅ Near-perfect (7/8)

**Issue:** `@quantity_input` crashes on functions annotated `-> None`

| | GT | Qwen |
|---|---|---|
| File | `decorators.py` | `decorators.py` |
| GT fix | Single condition change: `is not inspect.Signature.empty` → `not in (inspect.Signature.empty, None)` | Two separate `if` guards after the existing empty-check: `if … is None: return return_` and `if return_ is None: return return_` |

**−1 Patch:** Both fix the `-> None` annotation crash. Qwen's approach adds an extra `if return_ is None: return return_` guard not in GT, which is redundant for correct code. The GT's in-place condition change is cleaner and idiomatic.

---

### Task 19 — `7606` — ⚠️ Partial (5/8)

**Issue:** `UnrecognizedUnit.__eq__` raises `TypeError` when compared to `None`

| | GT | Qwen |
|---|---|---|
| File | `core.py` | `core.py` |
| GT fix | 1) `UnitBase.__eq__`: change `return False` → `return NotImplemented`; 2) `UnrecognizedUnit.__eq__`: wrap with try/except returning `NotImplemented`; use `isinstance(other, type(self))` | Add `if other is None: return False` guard before `Unit(other, ...)` in `UnrecognizedUnit.__eq__` only |

**−3 Patch:** Qwen addresses only `UnrecognizedUnit.__eq__` and only for `None` specifically, returning `False` rather than `NotImplemented`. This misses the broader fix in `UnitBase.__eq__` and the semantic distinction between `False` and `NotImplemented` in Python's comparison protocol (the latter allows the reflected operation to be tried). The `isinstance(other, type(self))` change is also missed.

---

### Task 20 — `7671` — ✅ Near-perfect (7/8)

**Issue:** `minversion()` raises `TypeError` for dev/rc version strings like `1.14dev`

| | GT | Qwen |
|---|---|---|
| File | `introspection.py` | `introspection.py` |
| GT fix | Inline regex strip of non-numeric suffix from `version` only | Module-level `_ver_expr` + `_normalize()` helper; normalises both `version` and `have_version` |

**−1 Patch:** Qwen normalises both arguments where GT only normalises `version`. More defensive but structurally over-engineered relative to GT. The regex (PEP 440 Appendix B) is identical. Core fix is correct.

---

### Task 21 — `8707` — ❌ Fail (2/8)

**Issue:** `Card.fromstring` and `Header.fromstring` should accept `bytes` input

| | GT | Qwen |
|---|---|---|
| Files | `card.py` + `header.py` | Test file only |
| GT fix | Add `if isinstance(image, bytes): image = image.decode('latin1')` to both `fromstring` methods; update docstrings and `__doctest_skip__` | Adds only a test; claims the implementation already handles bytes (incorrect) |

**−6 Patch:** Qwen incorrectly asserts that `Card.fromstring` already handles bytes. The implementation does not — that is the entire bug. The proposed "fix" is only a new test with no implementation change. Root cause is vaguely identified (bytes decoding needed) but the code-state diagnosis is wrong.

---

### Task 22 — `8872` — ✅ Near-perfect (7/8)

**Issue:** `Quantity` casts `float16`/`float32` arrays to `float64`

| | GT | Qwen |
|---|---|---|
| File | `quantity.py` | `quantity.py` |
| GT fix | Replace `np.can_cast(np.float32, value.dtype)` with `value.dtype.kind in 'iu'` at two locations | Add `np.issubdtype(value.dtype, np.inexact)` to the OR condition at both locations |

**−1 Patch:** Both approaches correctly preserve `float16`/`float32`. GT's `kind in 'iu'` is elegant (only cast integer/unsigned types to float); Qwen's `issubdtype(..., np.inexact)` is logically equivalent but more verbose and keeps the legacy `can_cast` condition alongside. Correct fix, over-specified structure.

---

## Grade Distribution

| Grade | Count | Tasks |
|-------|-------|-------|
| ✅ Exact (8/8) | 7 | 1, 3, 4, 9, 13, 14, 17 |
| ✅ Near-perfect (7/8) | 9 | 2, 5, 6, 8, 10, 16, 18, 20, 22 |
| ⚠️ Partial (5–6/8) | 4 | 7, 11, 15, 19 |
| ❌ Fail (≤4/8) | 2 | 12, 21 |

**Exact + Near-perfect: 16/22 (72.7%)**

---

## Comparison: Qwen 3.6 Free vs GPT-5.4 Mini vs GPT-5.4 Nano vs Claude Sonnet 4.6

*Shared 11-task subset for apples-to-apples comparison. Sonnet figures recomputed for the 11-task subset.*

| Metric | Qwen 3.6 Free (11) | GPT-5.4 Mini | GPT-5.4 Nano | Sonnet 4.6 |
|--------|-------------------|-------------|-------------|------------|
| Overall score | **79/88 (89.8%)** | 74/88 (84.1%) | 64/88 (72.7%) | 83/88 (94.3%) |
| Exact (8/8) | **4** | 3 | 0 | 8 |
| Near-perfect (7/8) | 5 | 5 | 5 | 1 |
| Partial (6/8) | 2 | 1 | 3 | 1 |
| Fail (≤4/8) | **0** | 1 | 2 | 0 |
| Root cause % | **100%** | 93.9% | 87.9% | **100%** |
| File ID % | **100%** | 95.5% | 95.5% | **100%** |
| Patch quality % | **72.7%** | 66.7% | 42.4% | 81.8% |
| Avg cost/task | **$0.00** | $0.069 | $0.051 | $0.538 |
| Avg time/task | 1,016 s | 843 s | 1,841 s | 310 s |
| Avg input tok/task | 1,706,354 | 46,310 | 93,142 | ~97,000† |
| Avg output tok/task | 23,297 | 2,315 | 12,719 | ~39,000† |

*† Sonnet uses Anthropic-side cache — raw token counts not directly comparable.*

### Qwen Full 22-Task Summary

| Metric | 11 tasks | 22 tasks (full) |
|--------|----------|-----------------|
| Overall score | 79/88 (89.8%) | **146/176 (83.0%)** |
| Exact (8/8) | 4 | **7** |
| Near-perfect (7/8) | 5 | **9** |
| Partial (5–6/8) | 2 | **4** |
| Fail (≤4/8) | 0 | **2** |
| Root cause % | 100% | **92.4%** |
| File ID % | 100% | **95.5%** |
| Patch quality % | 72.7% | **65.2%** |
| Avg time/task | 1,016 s | **859 s** |
| Avg input tok/task | 1,706,354 | **1,320,956** |

**Key observations:**

- **Strong first batch, harder second batch.** The first 11 tasks scored 89.8% with no fails. The second 11 tasks scored 76.1% with 2 fails — pulling the full-set average to 83.0%. The new tasks include harder code-state-diagnosis problems (`8707`, `14369`) where Qwen confidently misread what was already in the source.

- **Two distinct failure patterns.** Both fails (`8707`, `14369`) share the same root cause: Qwen asserts that the implementation already contains the fix, then only proposes a test or a cache-invalidation. This is a hallucination of code state — the model "sees" what it expects rather than what's there.

- **Exact match rate jumped.** 7 exact matches across 22 tasks, including trivially clean one-liners (`14539`, `7166`) and a structurally equivalent float formatter rewrite (`14508`).

- **`14598` is the hardest new task.** 2,027 s and 134K reasoning tokens — more reasoning than any other task — yet Qwen misses the regex `$` anchor and partially misidentifies the offending code line. High effort, partial result.

- **Qwen remains the best free model on the shared 11.** At 89.8% on the common subset it sits 4.5 pp behind Sonnet and 5.7 pp ahead of GPT-5.4 Mini — at zero cost.

- **Token footprint normalising.** The second batch averages 937K input tokens/task vs 1.7M in the first, suggesting Qwen is more efficient on simpler tasks and only burns tokens when the problem requires broad exploration.

- **Shared weaknesses persist.** Task `13977` (partial try/except) and `14365` (missing `v.upper()`) remain unfixed — both are structural traps that affect all models tested.
