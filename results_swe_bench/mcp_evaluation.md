# MCP SWE-Bench Evaluation Report

**Dataset:** princeton-nlp/SWE-bench_Verified — `astropy/astropy`
**Evaluated:** Top 5 tasks from `astropy_tasks.json`
**Date:** 2026-03-24
**Judge:** Claude Code (claude-sonnet-4-6)

---

## Scoring Rubric

Each task is scored out of **10 points**:

| Dimension | Weight | What is graded |
|-----------|--------|----------------|
| Root cause identification | 3 pts | Did the MCP correctly diagnose WHY the bug exists? |
| Correct file(s) | 2 pts | Did it identify the right file(s) to change? |
| Correct patch / code change | 3 pts | Does the code change match or functionally equivalent to ground truth? |
| Test awareness | 2 pts | Did it account for failing tests / propose test changes? |

---

## Task 1 — `astropy__astropy-12907`

**Issue:** `separability_matrix` does not compute separability correctly for nested `CompoundModels`
**Difficulty:** 15 min – 1 hour
**Failing tests:** `test_separable[compound_model6-result6]`, `test_separable[compound_model9-result9]`

### Ground Truth Patch
```diff
--- a/astropy/modeling/separable.py
+++ b/astropy/modeling/separable.py
@@ -242,7 +242,7 @@ def _cstack(left, right):
-        cright[-right.shape[0]:, -right.shape[1]:] = 1
+        cright[-right.shape[0]:, -right.shape[1]:] = right
```
A single character change: replace the literal `1` with the matrix `right`.

### MCP Answer
The MCP identified:
- **Root cause:** In `_cstack`, when `right` is already a numpy array (a recursive separability matrix), the code wrongly assigns `1` instead of copying the actual matrix values, discarding all separability structure.
- **File:** `astropy/modeling/separable.py`, function `_cstack`, line 245.
- **Fix:** `cright[-right.shape[0]:, -right.shape[1]:] = right` — **exact match** to ground truth.
- **Explanation:** Clear and accurate.
- **Test patch:** Proposed adding `compound_model6` and `compound_model9` parametrized test cases with correct expected matrices.

### Verdict

| Dimension | Score |
|-----------|-------|
| Root cause | 3/3 |
| Correct file | 2/2 |
| Correct patch | 3/3 |
| Test awareness | 2/2 |
| **Total** | **10/10** |

**Notes:** Perfect match on every dimension. The MCP nailed the one-character bug, gave a textbook-quality explanation, and proposed test additions that correctly cover both failing parametrized cases.

---

## Task 2 — `astropy__astropy-13033`

**Issue:** `TimeSeries` produces a misleading exception when a required column is removed
**Difficulty:** 15 min – 1 hour
**Failing tests:** `test_required_columns`

### Ground Truth Patch
Added a helper `as_scalar_or_list_str(obj)` and updated the `ValueError` message:
```diff
-  raise ValueError("{} object is invalid - expected '{}' "
-                   "as the first column{} but found '{}'"
-                   .format(self.__class__.__name__, required_columns[0], plural, self.colnames[0]))
+  raise ValueError("{} object is invalid - expected {} "
+                   "as the first column{} but found {}"
+                   .format(self.__class__.__name__, as_scalar_or_list_str(required_columns),
+                           plural, as_scalar_or_list_str(self.colnames[:len(required_columns)])))
```
Key details:
- Kept the word **"expected"** (not changed).
- Used a helper to produce `'time'` for single-column cases and `['time', 'flux']` for multi-column cases (no extra surrounding quotes on the list).

### MCP Answer
The MCP identified the correct file and location (`astropy/timeseries/core.py` lines 79–81). Its proposed fix:
```diff
-  raise ValueError("{} object is invalid - expected '{}' "
-                   "as the first column{} but found '{}'"
-                   .format(..., required_columns[0], plural, self.colnames[0]))
+  raise ValueError("{} object is invalid - required '{}' "
+                   "as the first column{} but found '{}'"
+                   .format(..., required_columns, plural, self.colnames[:len(required_columns)]))
```
Issues:
- Changed `"expected"` → `"required"` — the ground truth keeps "expected".
- Wraps the list in single quotes: `'['time', 'flux']'` — syntactically ugly and different from ground truth.
- Did not add the `as_scalar_or_list_str` helper, so single-column output (`'['time']'`) looks different from ground truth (`'time'`).
- The test assertions MCP proposed would not match the ground truth test assertions.

### Verdict

| Dimension | Score |
|-----------|-------|
| Root cause | 3/3 |
| Correct file | 2/2 |
| Correct patch | 1/3 |
| Test awareness | 1/2 |
| **Total** | **7/10** |

**Notes:** MCP correctly diagnosed the root cause and found the right location. The conceptual fix is also right (show full lists). However, the implementation diverges: wrong word ("required" vs "expected"), missing helper function, and the string formatting produces different output from what the ground truth tests expect. The fix would help readability but would **not pass** the ground truth test as-is.

---

## Task 3 — `astropy__astropy-13236`

**Issue:** Remove auto-transform of structured `np.ndarray` columns into `NdarrayMixin`
**Difficulty:** 15 min – 1 hour
**Failing tests:** `test_ndarray_mixin[False]`, `test_structured_masked_column`

### Ground Truth Patch
Remove a 6-line block from `astropy/table/table.py`:
```diff
-        # Structured ndarray gets viewed as a mixin unless already a valid
-        # mixin class
-        if (not isinstance(data, Column) and not data_is_mixin
-                and isinstance(data, np.ndarray) and len(data.dtype) > 1):
-            data = data.view(NdarrayMixin)
-            data_is_mixin = True
```

### MCP Answer
- **Root cause:** Correctly identified the exact 6-line block.
- **Fix strategy:** Remove the block so structured arrays fall through to normal `Column` creation.
- **Code change:** Matches ground truth exactly — the `old_code` field contains the precise block and `new_code` is empty (deleted).
- **Test changes:** Proposed parametrizing `test_ndarray_mixin` with `masked=[False, True]` and checking for `Column` instead of `NdarrayMixin`, which aligns with the spirit of the ground truth test changes.

### Verdict

| Dimension | Score |
|-----------|-------|
| Root cause | 3/3 |
| Correct file | 2/2 |
| Correct patch | 3/3 |
| Test awareness | 2/2 |
| **Total** | **10/10** |

**Notes:** The core fix is a perfect match. The test changes are slightly more elaborate than strictly required (ground truth only updates existing test assertions) but they are correct and sensible. No deductions — the essential code removal is identical to ground truth.

---

## Task 4 — `astropy__astropy-13398`

**Issue:** Add direct ITRS ↔ AltAz/HADec transforms that stay within ITRS (topocentric support)
**Difficulty:** 1–4 hours
**Failing tests:** `test_itrs_topo_to_altaz_with_refraction`, `test_itrs_topo_to_hadec_with_refraction`, `test_cirs_itrs_topo`, `test_itrs_straight_overhead`

### Ground Truth Patch (summary)
Six files changed:

| File | Change |
|------|--------|
| `builtin_frames/__init__.py` | Add `from . import itrs_observed_transforms` |
| `builtin_frames/itrs.py` | Add `EarthLocationAttribute location` (default `EARTH_CENTER`) + docstring update |
| `builtin_frames/intermediate_rotation_transforms.py` | Propagate `location` in TETE↔ITRS and CIRS↔ITRS; fix typo "siderial"→"sidereal" |
| `builtin_frames/itrs_observed_transforms.py` | **New file** — `itrs_to_altaz_mat`, `itrs_to_hadec_mat`, `altaz_to_hadec_mat`, `add_refraction`, `remove_refraction`, `itrs_to_observed`, `observed_to_itrs` |
| `earth.py` | (minor) |
| `tests/test_intermediate_transformations.py` | Add 4 test functions |

### MCP Answer
- **Root cause:** Correctly identified all 5 missing/broken pieces (no `location` on ITRS, missing `itrs_observed_transforms.py`, missing location propagation in CIRS/TETE transforms, missing tests).
- **Files:** Identified the exact same 6 file set including the new `itrs_observed_transforms.py`.
- **ITRS frame changes:** MCP's `itrs.py` diff adds `EarthLocationAttribute` with `EARTH_CENTER` default — matches ground truth.
- **`__init__.py`:** Import added correctly.
- **Intermediate transforms:** MCP identified the location propagation changes in `cirs_to_itrs`, `itrs_to_cirs`, `tete_to_itrs`, `itrs_to_tete` — correct.
- **`itrs_observed_transforms.py`:** MCP proposed creating the new file with the right transform registration pattern (`@frame_transform_graph.transform` for both ITRS→AltAz/HADec and reverse). The structure matches the ground truth's approach.

Minor gaps: The specific refraction algorithm implementation could diverge from ground truth in subtle ways (ERFA function calls, constants like `CELMIN`/`SELMIN`). Full confidence would require running the tests, but the high-level approach is correct.

### Verdict

| Dimension | Score |
|-----------|-------|
| Root cause | 3/3 |
| Correct file | 2/2 |
| Correct patch | 2/3 |
| Test awareness | 2/2 |
| **Total** | **9/10** |

**Notes:** Excellent answer on the hardest task (1–4 hour difficulty). Identified all correct files, the right attributes to add, and the right structure for the new transform file. Minor deduction because the exact implementation of refraction math cannot be fully verified without execution, and subtle differences in constants or ERFA call signatures could prevent tests from passing.

---

## Task 5 — `astropy__astropy-13453`

**Issue:** `ascii.write(..., format="html", formats={...})` ignores the `formats` argument
**Difficulty:** 15 min – 1 hour
**Failing tests:** `test_write_table_formatted_columns`

### Ground Truth Patch
Two lines added to `astropy/io/ascii/html.py`:
```diff
     self.data.header.cols = cols
+    self.data.cols = cols          # line ~351

     ...
     self.data._set_fill_values(cols)
+    self.data._set_col_formats()   # line ~356
```
Inserted **before** the `lines = []` declaration.

### MCP Answer
- **Root cause:** Correctly identified that the HTML writer calls `col.info.iter_str_vals()` directly without going through `_set_col_formats()`, bypassing the user-supplied formats.
- **Fix:** Same two lines (`self.data.cols = cols` + `self.data._set_col_formats()`).
- **Location difference:** MCP inserted the lines after `cols_escaped = [...]` (~line 364–367) rather than after `self.data.header.cols = cols` (~line 351). Both locations are after `cols` is assigned and before the cell iteration loop, so the fix is **functionally equivalent**.
- **Test:** Proposed `test_write_table_formatted_columns` with correct assertions checking that `1.24e-24` appears and `1.23875234858e-24` does not — matches ground truth test.

### Verdict

| Dimension | Score |
|-----------|-------|
| Root cause | 3/3 |
| Correct file | 2/2 |
| Correct patch | 2/3 |
| Test awareness | 2/2 |
| **Total** | **9/10** |

**Notes:** The fix is functionally correct. Minor deduction because the insertion point differs slightly from ground truth (after `cols_escaped` vs after `header.cols`). The ground truth places both lines earlier and more logically adjacent to the other `self.data.*` setup calls. The patch diff would not cleanly apply against ground truth but would still work at runtime.

---

## Summary Scorecard

| # | Instance ID | Difficulty | Score | Grade |
|---|-------------|------------|-------|-------|
| 1 | `astropy__astropy-12907` | 15min–1hr | **10/10** | ✅ Exact |
| 2 | `astropy__astropy-13033` | 15min–1hr | **7/10** | ⚠️ Partial |
| 3 | `astropy__astropy-13236` | 15min–1hr | **10/10** | ✅ Exact |
| 4 | `astropy__astropy-13398` | 1–4hrs | **9/10** | ✅ Near-perfect |
| 5 | `astropy__astropy-13453` | 15min–1hr | **9/10** | ✅ Functional match |
| | **Total** | | **45/50** | **90%** |

---

## Overall Assessment

**Score: 45/50 (90%)**

### Strengths
- **Root cause accuracy:** 5/5 tasks — the MCP correctly diagnosed the underlying bug in every case, including the tricky nested `CompoundModel` separability bug and the complex multi-file ITRS transform feature.
- **File identification:** Flawless across all tasks. The MCP never pointed at the wrong file.
- **Hard task performance:** Task 4 (the 1–4 hour, 6-file change with a new file) was handled impressively — the MCP identified the complete set of changes required.
- **Test awareness:** Strong in 4 of 5 tasks. It proposed appropriate test additions or updates.

### Weaknesses
- **Task 2 (message format):** The only significant failure. The MCP changed "expected" to "required" and did not add the `as_scalar_or_list_str` helper, producing a different message format that would not satisfy the ground truth test assertions. This is a small but impactful implementation detail that prevents the test from passing as-is.
- **Patch insertion point (Task 5):** Minor — the two lines were inserted at a slightly later position in the function than ground truth, but the fix is functionally identical.

### Conclusion
The MCP demonstrates strong SWE-bench performance at **90%**. It excels at root cause analysis and file localization even on complex multi-file changes. The primary failure mode is message-format precision on error-message wording bugs where exact string matching is required by tests.
