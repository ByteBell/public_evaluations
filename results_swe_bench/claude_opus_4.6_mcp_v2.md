# Claude Opus 4.6 MCP v2 — SWE-Bench Evaluation Report

**Dataset:** `princeton-nlp/SWE-bench_Verified` — `astropy/astropy`
**Evaluated:** 5 tasks from `astropy_tasks.json`
**Date:** 2026-03-31
**Judge:** Claude Code (claude-sonnet-4-6)
**Ground truth source:** `results_swe_bench/astropy_tasks.json`
**Raw MCP responses:** `results_swe_bench/claude_opus_4.6_mcp_v2/*/answer.json`

---

## Scoring Rubric

| Dimension | Weight | What is graded |
|-----------|--------|----------------|
| Root cause identification | 3 pts | Did the model correctly diagnose *why* the bug exists? |
| Correct file(s) | 2 pts | Did it identify the right file(s) to change? |
| Correct patch / code change | 3 pts | Does the code change match or is functionally equivalent to ground truth? |
| Test awareness | 2 pts | Did it identify failing tests, propose test changes, or describe test assertions? |

**Grade tiers:** ✅ Exact (10/10) · ✅ Near-perfect (9/10) · ⚠️ Partial (6–8/10) · ❌ Fail (≤5/10)

---

## Combined Per-Question: Score · Time · Cost

| # | Instance ID | Difficulty | RC | Files | Patch | Tests | **Score** | Grade | Time (s) | Tool Calls | Cost (USD) |
|---|-------------|------------|----|-------|-------|-------|-----------|-------|----------|------------|------------|
| 1 | `astropy__astropy-12907` | 15m–1h | 3 | 2 | 3 | 0 | **8/10** | ⚠️ Partial | 43.2 | 6 | $0.297 |
| 2 | `astropy__astropy-13033` | 15m–1h | 3 | 2 | 3 | 1 | **9/10** | ✅ Near-perfect | 65.9 | 7 | $0.239 |
| 3 | `astropy__astropy-13236` | 15m–1h | 3 | 2 | 3 | 2 | **10/10** | ✅ Exact | 232.6 | 15 | $0.376 |
| 4 | `astropy__astropy-13398` | 1–4h | 0 | 2 | 0 | 0 | **2/10** | ❌ Fail | 141.5 | 30 | $0.771 |
| 5 | `astropy__astropy-13453` | 15m–1h | 3 | 2 | 2 | 0 | **7/10** | ⚠️ Partial | 70.5 | 10 | $0.341 |
| | **TOTAL** | | **12/15** | **10/10** | **11/15** | **3/10** | **36/50** | **72%** | **553.7 s** | **68** | **$2.024** |
| | **AVERAGE** | | | | | | | | **110.7 s** | **13.6** | **$0.405** |

---

## Dimension Breakdown

| Dimension | Score | Max | % |
|-----------|-------|-----|---|
| Root cause identification | 12 | 15 | **80.0%** |
| Correct file(s) | 10 | 10 | **100.0%** |
| Correct patch / code change | 11 | 15 | **73.3%** |
| Test awareness | 3 | 10 | **30.0%** |
| **Overall** | **36** | **50** | **72.0%** |

File identification is perfect across all 5 tasks. Root cause identification is strong on 4/5 tasks (failed entirely on the hardest task). Test awareness is the dominant weakness — only 1 task out of 5 produced any test guidance.

---

## Per-Question Token & Cost Breakdown

| # | Instance ID | Time (s) | Tool Calls | Input Tokens | Output Tokens | Cache Read | Cache Write | API Req | **Total Cost** | Score | Models Used |
|---|-------------|----------|------------|--------------|---------------|------------|-------------|---------|----------------|-------|-------------|
| 1 | `12907` | 43.2 | 6 | 2,131 | 1,538 | 130,811 | 30,555 | 6 | **$0.297** | 8/10 | haiku-4-5 + opus-4-6 |
| 2 | `13033` | 65.9 | 7 | 3,254 | 2,535 | 133,478 | 16,973 | 7 | **$0.239** | 9/10 | haiku-4-5 + opus-4-6 |
| 3 | `13236` | 232.6 | 15 | 1,567 | 10,628 | 318,828 | 31,938 | 12 | **$0.376** | 10/10 | haiku-4-5 + **sonnet-4-6** |
| 4 | `13398` | 141.5 | 30 | 6,317 | 7,243 | 532,992 | 50,807 | 14 | **$0.771** | 2/10 | haiku-4-5 + opus-4-6 |
| 5 | `13453` | 70.5 | 10 | 6,660 | 2,395 | 290,438 | 20,717 | 12 | **$0.341** | 7/10 | haiku-4-5 + opus-4-6 |
| | **TOTAL** | **553.7** | **68** | **19,929** | **24,339** | **1,406,547** | **150,990** | **51** | **$2.024** | **36/50** | |
| | **AVERAGE** | **110.7** | **13.6** | **3,986** | **4,868** | **281,309** | **30,198** | **10.2** | **$0.405** | | |

---

## Task-by-Task Analysis

### Task 1 — `astropy__astropy-12907`

**Issue:** `separability_matrix` does not compute separability correctly for nested `CompoundModels`
**Difficulty:** 15 min – 1 hour
**Failing tests:** `test_separable[compound_model6-result6]`, `test_separable[compound_model9-result9]`

#### Ground Truth Patch
```diff
--- a/astropy/modeling/separable.py
+++ b/astropy/modeling/separable.py
@@ -242,7 +242,7 @@
-        cright[-right.shape[0]:, -right.shape[1]:] = 1
+        cright[-right.shape[0]:, -right.shape[1]:] = right
```

#### MCP v2 Answer
> "In `astropy/modeling/separable.py`, in the `_cstack` function (line 245), change `cright[-right.shape[0]:, -right.shape[1]:] = 1` to `cright[-right.shape[0]:, -right.shape[1]:] = right`. When the right operand of the `&` operator is already a computed separability matrix (from a nested CompoundModel), the code incorrectly fills the block with all 1s instead of preserving the actual separability values from the recursive call."

- **Root cause:** Perfect diagnosis — correctly identifies that the nested CompoundModel's computed matrix is discarded.
- **File:** `astropy/modeling/separable.py`, `_cstack` — exact match.
- **Fix:** Exact match to ground truth (`= right`).
- **Tests:** No mention of failing tests or proposed test additions.

#### Verdict

| Dimension | Score |
|-----------|-------|
| Root cause | 3/3 |
| Correct file | 2/2 |
| Correct patch | 3/3 |
| Test awareness | 0/2 |
| **Total** | **8/10** |

**Notes:** The one-line fix is exactly right. Deduction is solely for missing test awareness — v2 produces a shorter, more direct answer that omits any discussion of the two failing test cases or proposed test additions.

---

### Task 2 — `astropy__astropy-13033`

**Issue:** `TimeSeries` produces a misleading exception when a required column is removed
**Difficulty:** 15 min – 1 hour
**Failing tests:** `test_required_columns`

#### Ground Truth Patch (summary)
Add `as_scalar_or_list_str(obj)` helper inside `_check_required_columns` and update the `ValueError` to:
```python
raise ValueError("{} object is invalid - expected {} "
                 "as the first column{} but found {}"
                 .format(self.__class__.__name__,
                         as_scalar_or_list_str(required_columns),
                         plural,
                         as_scalar_or_list_str(self.colnames[:len(required_columns)])))
```

#### MCP v2 Answer
The model correctly proposes:
- Adding `as_scalar_or_list_str(obj)` helper that returns `'value'` for single items or `['a', 'b']` for lists
- Keeping the word **"expected"** (not changing it to "required")
- Using the helper for **both** `required_columns` and `self.colnames[:len(required_columns)]`
- Applying the same fix to the empty-table error case for consistency
- Expected output: `"expected ['time', 'flux'] as the first columns but found ['time']"` — matches ground truth test assertion

**Significant improvement over first eval (v1):** v1 changed "expected" to "required" and omitted the helper function. v2 nails both.

#### Verdict

| Dimension | Score |
|-----------|-------|
| Root cause | 3/3 |
| Correct file | 2/2 |
| Correct patch | 3/3 |
| Test awareness | 1/2 |
| **Total** | **9/10** |

**Notes:** Near-perfect. The fix matches ground truth in all important details: correct word ("expected"), correct helper, correct slicing of colnames. One test deduction: the model describes expected output implicitly but doesn't explicitly propose a test case or reference the failing test.

---

### Task 3 — `astropy__astropy-13236`

**Issue:** Remove auto-transform of structured `np.ndarray` columns into `NdarrayMixin`
**Difficulty:** 15 min – 1 hour
**Failing tests:** `test_ndarray_mixin[False]`, `test_structured_masked_column`

#### Ground Truth Patch (summary)
Remove 6-line block from `astropy/table/table.py`, parametrize `test_ndarray_mixin` with `as_ndarray_mixin`, add `test_structured_masked_column` to `test_table.py`.

#### MCP v2 Answer
The model produced a complete git diff:
- **`table.py`:** Removes the exact 6-line block — **identical to ground truth**.
- **`test_mixin.py`:** Adds `@pytest.mark.parametrize('masked', [True, False])` to `test_ndarray_mixin` (different parameter name than ground truth's `as_ndarray_mixin`, but covers the `[False]` FAIL_TO_PASS case correctly).
- **`test_table.py`:** Adds `test_structured_masked_column` checking `Column` vs `MaskedColumn` types — functionally equivalent to ground truth.

Note: Task 3 uniquely used **claude-sonnet-4-6** as the primary model (instead of opus-4-6). At 232.6s and 10,628 output tokens, it produced the most thorough answer in the set.

#### Verdict

| Dimension | Score |
|-----------|-------|
| Root cause | 3/3 |
| Correct file | 2/2 |
| Correct patch | 3/3 |
| Test awareness | 2/2 |
| **Total** | **10/10** |

**Notes:** Perfect score. The core 6-line deletion is exact. The test approach differs slightly (parameter name `masked` vs `as_ndarray_mixin`) but both FAIL_TO_PASS tests are covered with correct assertions.

---

### Task 4 — `astropy__astropy-13398`

**Issue:** Add direct ITRS ↔ AltAz/HADec transforms staying within ITRS (topocentric support)
**Difficulty:** 1–4 hours
**Failing tests:** `test_itrs_topo_to_altaz_with_refraction`, `test_itrs_topo_to_hadec_with_refraction`, `test_cirs_itrs_topo`, `test_itrs_straight_overhead`

#### Ground Truth Patch (summary)
Six files changed: new `itrs_observed_transforms.py`, add `location` attribute to `itrs.py`, propagate location in `intermediate_rotation_transforms.py`, update `__init__.py` import, minor `earth.py` change, 4 new test functions.

#### MCP v2 Answer
> "astropy/coordinates/builtin_frames/itrs.py, astropy/coordinates/builtin_frames/itrs_observed_transforms.py, astropy/coordinates/builtin_frames/__init__.py, astropy/coordinates/builtin_frames/intermediate_rotation_transforms.py, astropy/coordinates/earth.py"

**Critical failure:** The answer is only a comma-separated list of filenames. No root cause, no explanation, no code changes, no patch, no tests. Despite 141.5 seconds, 14 API requests, and 30 tool calls (the most tool calls in the set), the model performed extensive exploration but produced a content-free answer.

This is the most expensive task ($0.771) yet yielded the worst result.

#### Verdict

| Dimension | Score |
|-----------|-------|
| Root cause | 0/3 |
| Correct file | 2/2 |
| Correct patch | 0/3 |
| Test awareness | 0/2 |
| **Total** | **2/10** |

**Notes:** File identification is correct (all 5 source files match ground truth). Everything else scores zero. The model appears to have gotten lost in exploration — 30 tool calls with 532,992 cache read tokens suggests it read many files but never synthesized an answer. The high output token count (7,243) is misleading; the actual answer output is one line. This is the single biggest regression from prior evaluations.

---

### Task 5 — `astropy__astropy-13453`

**Issue:** `ascii.write(..., format="html", formats={...})` ignores the `formats` argument
**Difficulty:** 15 min – 1 hour
**Failing tests:** `test_write_table_formatted_columns`

#### Ground Truth Patch
```diff
     self.data.header.cols = cols
+    self.data.cols = cols
     ...
     self.data._set_fill_values(cols)
+    self.data._set_col_formats()
```
Both lines inserted **before** `lines = []`, after `self.data.header.cols = cols` (~line 351).

#### MCP v2 Answer
The model correctly identifies the two lines to add (`self.data.cols = cols` and `self.data._set_col_formats()`) after `self.data._set_fill_values(cols)` (~line 356). Root cause is accurately described: `iter_str_vals()` is called without going through `_set_col_formats()`, so user-supplied formats are bypassed.

- **Location difference:** After `_set_fill_values(cols)` vs after `header.cols = cols` — functionally equivalent, but the diff would not apply cleanly against ground truth.
- **Tests:** No test proposal. The ground truth test `test_write_table_formatted_columns` is not mentioned.

#### Verdict

| Dimension | Score |
|-----------|-------|
| Root cause | 3/3 |
| Correct file | 2/2 |
| Correct patch | 2/3 |
| Test awareness | 0/2 |
| **Total** | **7/10** |

**Notes:** Correct fix, slightly wrong insertion point. Functionally equivalent at runtime. No test awareness deduction same as task 1.

---

## Comparison: v2 vs Prior Evaluations

### Same 5 Tasks: v1 (mcp_evaluation.md) vs v2

| Task | v1 Score | v2 Score | Delta | Key Difference |
|------|----------|----------|-------|----------------|
| `12907` | **10/10** | **8/10** | −2 | v2 skips test proposals |
| `13033` | **7/10** | **9/10** | +2 | v2 keeps "expected", adds helper correctly |
| `13236` | **10/10** | **10/10** | 0 | Both exact |
| `13398` | **9/10** | **2/10** | −7 | v2 returns only file list, no patch |
| `13453` | **9/10** | **7/10** | −2 | v2 skips test proposals |
| **Total** | **45/50 (90%)** | **36/50 (72%)** | **−9 pts** | |

### Cost & Speed: v1 vs v2 (same 5 tasks)

| Metric | v1 (extended thinking) | v2 (cache-heavy) | Change |
|--------|------------------------|------------------|--------|
| Total cost | $3.476 | $2.024 | **−42%** |
| Total time | 703 s | 554 s | **−21%** |
| Total tool calls | 56 | 68 | +21% |
| Avg cost/task | $0.695 | $0.405 | **−42%** |
| Avg time/task | 140.6 s | 110.7 s | **−21%** |
| Score | 90% | 72% | **−18 pts** |
| Thinking tokens | Yes (large) | None | — |
| Cache read tokens | Low | 1,406,547 | Much higher |

v2 is dramatically cheaper and faster — driven by aggressive cache utilization instead of extended thinking. But accuracy drops correspondingly, with the test-awareness dimension nearly zeroed out and a catastrophic failure on the hardest task.

### vs. 21-Task Evaluation (claude_opus_4.6_mcp_evaluation_21.md)

| Metric | 21-task eval | v2 (5 tasks) |
|--------|-------------|--------------|
| Score | **199/210 (94.8%)** | **36/50 (72.0%)** |
| Avg cost/task | $0.520 | $0.405 |
| Avg time/task | 122.4 s | 110.7 s |
| Root cause % | 100% | 80.0% |
| File ID % | 100% | 100.0% |
| Patch % | 84.1% | 73.3% |
| Test awareness % | 97.6% | 30.0% |

The 21-task eval used extended thinking (up to 36k thinking tokens/task), yielding near-perfect test awareness. v2 uses no thinking tokens and the test awareness collapse (30%) is the main driver of the score gap.

---

## Summary Scorecard

| # | Instance ID | Difficulty | Score | Grade |
|---|-------------|------------|-------|-------|
| 1 | `astropy__astropy-12907` | 15m–1h | **8/10** | ⚠️ Partial |
| 2 | `astropy__astropy-13033` | 15m–1h | **9/10** | ✅ Near-perfect |
| 3 | `astropy__astropy-13236` | 15m–1h | **10/10** | ✅ Exact |
| 4 | `astropy__astropy-13398` | 1–4h | **2/10** | ❌ Fail |
| 5 | `astropy__astropy-13453` | 15m–1h | **7/10** | ⚠️ Partial |
| | **Total** | | **36/50** | **72%** |

---

## Overall Assessment

**Score: 36/50 (72%)**

### Strengths
- **File identification:** Perfect 10/10 across all tasks. The system correctly identifies the relevant source files every time, including the tricky multi-file task 4.
- **Root cause on simple tasks:** 4 of 5 tasks receive full root cause credit. The separation between symptom and cause is consistently clear.
- **Task 2 improvement:** The v2 answer for `13033` is meaningfully better than v1 — it correctly uses "expected" (not "required") and adds the `as_scalar_or_list_str` helper that v1 missed. This shows the search strategy is capable of finding the right implementation details.
- **Task 3 (exact):** The most comprehensive answer — full git diff with correct code removal and test updates. The sonnet-4-6 model on this task spent more tokens (10,628 output) and produced a complete patch.

### Weaknesses
- **Test awareness collapse (30%):** The dominant failure mode. Three of five tasks receive 0/2 for test awareness. The v2 answers are concise to a fault — they describe the fix but omit discussion of failing tests, test assertions, or proposed test patches. This suggests the answer-generation step does not include test-awareness in its output instructions.
- **Task 4 catastrophic failure (2/10):** The hardest task (1–4h, 6-file change with a new file) produced only a list of filenames. The model spent the most resources (30 tool calls, $0.771, 14 API requests) on exploration but failed to synthesize any patch content. This is the single largest score driver and likely reflects a context-window or output-budget problem during the answer synthesis step.
- **Patch precision on task 5:** Correct lines, slightly wrong insertion point. Functionally fine but would not apply cleanly as a diff.

### Key Finding: Thinking Tokens vs. Cache Reads Trade-off
v2 replaces extended thinking (the v1/21-task approach) with heavy cache utilization. This achieves a 42% cost reduction and 21% speed improvement but at significant accuracy cost (-18 points, -22.8 percentage points). The quality collapse is concentrated in:
1. **Test awareness** — extended thinking likely drove the model to consider test implications; without it, answers are code-only.
2. **Complex multi-file tasks** — task 4 suggests that without deep reasoning, the model's exploration phase cannot synthesize a coherent multi-file patch.

The optimal configuration likely requires thinking tokens for tasks rated 1+ hours difficulty, while cache-heavy operation is sufficient for ≤15 min tasks.
