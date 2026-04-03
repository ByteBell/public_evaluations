# GPT-5.4 Nano Raw on Kilo — SWE-Bench Evaluation Report

**Dataset:** `princeton-nlp/SWE-bench_Verified` — `astropy/astropy`
**Evaluated:** 11 tasks from `astropy_tasks.json`
**Date:** 2026-04-03
**Judge:** Claude Code (claude-sonnet-4-6)
**Ground truth source:** `results_swe_bench/astropy_tasks.json`
**Raw responses:** `results_swe_bench/auto_run_on_raw_kilo_openai_gpt-5.4-nano/*/answer.json`
**Mode:** Kilo agent with direct repo access (no MCP knowledge graph) · Model: `openai/gpt-5.4-nano`

> **Note on timeouts:** 5 of 11 tasks recorded ~2684–2685 s run time, consistent with a ~45-minute wall-clock limit imposed by the harness. All 5 still produced a complete answer JSON before exiting.

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
| | **TOTAL** | | **29/33** | **21/22** | **14/33** | **64/88** | **72.7%** | **20,249 s** | **$0.558** |
| | **AVERAGE** | | | | | **5.8/8** | | **1,841 s** | **$0.051** |

---

## Dimension Breakdown

| Dimension | Score | Max | % |
|-----------|-------|-----|---|
| Root cause identification | 29 | 33 | **87.9%** |
| Correct file(s) | 21 | 22 | **95.5%** |
| Correct patch / code change | 14 | 33 | **42.4%** |
| **Overall** | **64** | **88** | **72.7%** |

---

## Token & Cost Breakdown

| # | Instance ID | Input | Cache Read | Output | **Cost** | Requests |
|---|-------------|-------|------------|--------|----------:|----------|
| 1 | `12907` | 28,868 | 108,032 | 2,195 | **$0.011** | 9 |
| 2 | `13033` | 158,732 | 956,416 | 5,700 | **$0.058** | 44 |
| 3 | `13236` | 181,950 | 1,409,024 | 5,184 | **$0.071** | 42 |
| 4 | `13398` | 147,565 | 1,553,408 | 5,000 | **$0.067** | 50 |
| 5 | `13453` | 18,225 | 81,920 | 793 | **$0.006** | 6 |
| 6 | `13579` | 41,292 | 307,200 | 66,585 | **$0.098** | 20 |
| 7 | `13977` | 43,065 | 132,096 | 2,067 | **$0.014** | 10 |
| 8 | `14096` | 156,101 | 1,363,456 | 4,576 | **$0.064** | 37 |
| 9 | `14182` | 135,786 | 1,901,568 | 8,550 | **$0.076** | 54 |
| 10 | `14309` | 67,436 | 655,872 | 4,134 | **$0.032** | 31 |
| 11 | `14365` | 45,538 | 399,872 | 35,123 | **$0.061** | 27 |
| | **TOTAL** | **1,024,558** | **8,868,864** | **139,907** | **$0.558** | **330** |

> **Average per task:** 1,841 s · $0.051
> No cache-write tokens recorded (gpt-5.4-nano does not use Anthropic prompt-caching).

---

## Per-Task Answer Comparison

### Task 1 — `12907` — ⚠️ Partial (5/8)

**Issue:** `separability_matrix` wrong for nested `CompoundModels`

| | GT | Nano |
|---|---|---|
| File | `separable.py` | `separable.py` |
| GT fix | `cright[-right.shape[0]:, -right.shape[1]:] = right` (one-line, in `_cstack`) | Rewrites `_separable()` for `op == '&'`: recursively calls `_separable(child)`, places each child output slice into the parent matrix, then `np.hstack` |

**−1 RC:** Nano correctly identifies the nested `CompoundModel` axis-ordering bug, but attributes it to `_separable()` rather than the `_cstack()` function where the actual `= 1` hardcode lives.  
**−2 Patch:** Different function, over-engineered recursive composition approach vs GT's one-line fix in `_cstack`. Not functionally equivalent.

---

### Task 2 — `13033` — ✅ Near-perfect (7/8)

**Issue:** `TimeSeries` misleading exception on required column removal

| | GT | Nano |
|---|---|---|
| File | `core.py` | `core.py` |
| GT fix | Add `as_scalar_or_list_str()` helper; use it in both error paths | Updated `_check_required_columns` to report full list of required vs found columns; added multi-column test assertion |

**−1 Patch:** Achieves the same user-visible behavior (full-list error message) but without the `as_scalar_or_list_str` helper; structural difference only.

---

### Task 3 — `13236` — ⚠️ Partial (6/8)

**Issue:** Remove auto-transform of structured ndarray into `NdarrayMixin`

| | GT | Nano |
|---|---|---|
| File | `table.py` | `table.py` |
| GT fix | Remove 6-line auto-view block in `_convert_data_to_col` | Modifies `_convert_sequence_data_to_column` to force plain structured ndarrays to `Column` |

**−2 Patch:** Wrong method — GT targets `_convert_data_to_col`, nano targets `_convert_sequence_data_to_column`. The nano applies a conditional restriction rather than the clean removal GT uses. Different code path, different semantics.

---

### Task 4 — `13398` — ❌ Fail (2/8)

**Issue:** Add ITRS ↔ AltAz/HADec topocentric transforms

| | GT | Nano |
|---|---|---|
| Files | 5 files + new `itrs_observed_transforms.py` | `itrs.py` only |
| GT fix | New transform module, `location` attribute on ITRS frame, CIRS/TETE chain updates, `__init__.py` import | Adds `__init__` override in `itrs.py` that forwards `*args, **kwargs` to `BaseCoordinateFrame.__init__` |

**−2 RC:** Nano identifies that `ITRS` rejects the `location` keyword, but misses that the real requirement is a full bidirectional transform implementation across 6 files.  
**−1 Files:** Only touches `itrs.py`; misses 4+ required files.  
**−3 Patch:** Merely makes `ITRS(location=...)` not raise — no transform math, no new module, no routing through the actual coordinate transformation chain.

---

### Task 5 — `13453` — ✅ Near-perfect (7/8)

**Issue:** HTML writer ignores `formats` argument

| | GT | Nano |
|---|---|---|
| File | `html.py` | `html.py` |
| GT fix | `self.data.cols = cols` + `self.data._set_col_formats()` | Applies `self.data.formats[col.info.name]` to each column formatter before `iter_str_vals()`; iterates over sliced `new_col` for multicolumn case |

**−1 Patch:** Nano applies formats per-column inline rather than routing through the established `_set_col_formats()` pipeline. References `self.data.formats` (correct data source) but bypasses the standard infrastructure; functionally similar for simple cases.

---

### Task 6 — `13579` — ✅ Near-perfect (7/8)

**Issue:** `SlicedLowLevelWCS.world_to_pixel_values` uses hardcoded `1.0` for dropped dimensions

| | GT | Nano |
|---|---|---|
| File | `sliced_wcs.py` | `sliced_wcs.py` |
| GT fix | Compute `sliced_out_world_coords` at pixel `[0,0,…]` for all kept axes; substitute for `1.` placeholder | Build reference pixel array from `self._slices_pixel[ip].start` (falling back to `0`) for each kept axis |

**−1 Patch:** Nano uses `slice.start` as the reference pixel whereas GT uses `0` for all kept axes. The nano's per-axis slice-origin approach is a reasonable alternative but does not match the GT reference pixel computation and may produce different results for non-zero-based slices.

---

### Task 7 — `13977` — ⚠️ Partial (6/8)

**Issue:** `Quantity.__array_ufunc__` should return `NotImplemented` for duck types

| | GT | Nano |
|---|---|---|
| File | `quantity.py` | `quantity.py` |
| GT fix | Wrap entire `__array_ufunc__` body in `try/except`; check `__array_ufunc__` on all inputs/outputs; return `NotImplemented` on failure | Add early-exit guard: if any input has `hasattr(inp, 'unit')` but is not `Quantity`/`np.ndarray`/`Column`, immediately `return NotImplemented` |

**−2 Patch:** The early-guard approach is narrower than GT. It dispatches only for inputs with a `unit` attribute; GT's full try/except also handles duck types that expose `__array_ufunc__` without `unit`. Nano misses the case where inputs lack `unit` but still cannot be converted — the correct fix requires wrapping the full body.

---

### Task 8 — `14096` — ✅ Near-perfect (7/8)

**Issue:** `SkyCoord` subclass property gives misleading `AttributeError`

| | GT | Nano |
|---|---|---|
| File | `sky_coordinate.py` | `sky_coordinate.py` |
| GT fix | Replace final `raise AttributeError(...)` with `return self.__getattribute__(attr)` — 2 lines | When `__getattr__` is reached via a subclass property's `AttributeError`, re-raise the original exception immediately |

**−1 Patch:** Both approaches prevent the misleading generic message and surface the real error. Nano's description of "re-raise immediately" is behaviorally equivalent to GT's `__getattribute__` delegation, though the exact mechanism likely differs slightly. GT's `__getattribute__` is both simpler and more idiomatically correct.

---

### Task 9 — `14182` — ❌ Fail (4/8)

**Issue:** RST writer needs `header_rows` support

| | GT | Nano |
|---|---|---|
| File | `rst.py` | `rst.py` |
| GT fix | Remove `start_line = 3` from `SimpleRSTData`; full `__init__` with dynamic `sep_line_index`; add `read()` method | Change `__init__(self, header_rows=None)` → `__init__(self, header_rows=None, **kwargs)` |

**−1 RC:** Nano identifies that `RST.__init__` does not accept the keyword, but misses that the real requirement is implementing the full `header_rows` feature (dynamic separator positioning, read support).  
**−3 Patch:** Adding `**kwargs` only prevents the `TypeError`; it does not implement `header_rows` behavior. The resulting writer ignores the argument entirely.

---

### Task 10 — `14309` — ✅ Near-perfect (7/8)

**Issue:** `is_fits` IndexError with empty args

| | GT | Nano |
|---|---|---|
| File | `connect.py` | `connect.py` |
| GT fix | Convert filepath check to an early `return`; subsequent `isinstance(args[0], …)` is then only reached when args is non-empty | Add explicit `if not args: return False` guard before `isinstance(args[0], …)` |

**−1 Patch:** Both fix the crash. GT restructures the logic so `args[0]` access is unreachable without args; nano adds a defensive guard. Equivalent for all test cases, but nano's guard is less elegant.

---

### Task 11 — `14365` — ⚠️ Partial (6/8)

**Issue:** QDP reader fails on lowercase commands

| | GT | Nano |
|---|---|---|
| File | `qdp.py` | `qdp.py` |
| GT fix | `re.IGNORECASE` on `_line_type_re` **+** `v.upper() == "NO"` in `_get_tables_from_qdp_file` | Only `re.IGNORECASE` on `_line_type_re` |

**−2 Patch:** Nano correctly adds `re.IGNORECASE` for command-line recognition but misses the second fix: `v.upper() == "NO"` in the data-value parsing loop. Lowercase `no` in data lines will still be mishandled.

---

## Grade Distribution

| Grade | Count | Tasks |
|-------|-------|-------|
| ✅ Near-perfect (7/8) | 5 | 2, 5, 6, 8, 10 |
| ⚠️ Partial (6/8) | 3 | 3, 7, 11 |
| ⚠️ Partial (5/8) | 1 | 1 |
| ❌ Fail (4/8) | 1 | 9 |
| ❌ Fail (2/8) | 1 | 4 |

**Near-perfect or better: 5/11 (45.5%)**

---

## Comparison: GPT-5.4 Nano Raw vs Claude Sonnet 4.6 Raw

*Sonnet was evaluated on the full 22-task set; nano covers the overlapping 11 tasks. Sonnet figures below are recomputed for the same 11 tasks.*

| Metric | GPT-5.4 Nano (11 tasks) | Sonnet 4.6 (11 tasks) | Delta |
|--------|------------------------|----------------------|-------|
| Overall score | 64/88 (72.7%) | 83/88 (94.3%) | **−21.6 pp** |
| Near-perfect (7/8) | 5 | 8 | −3 |
| Partial (6/8) | 3 | 1 | +2 |
| Partial (5/8) | 1 | 1 | 0 |
| Fail (≤4/8) | 2 | 1 | +1 |
| Root cause % | 87.9% | 100% | −12.1 pp |
| File identification % | 95.5% | 100% | −4.5 pp |
| Patch quality % | 42.4% | 81.8% | **−39.4 pp** |
| Avg time per task | 1,841 s | 310 s | +1,531 s |
| Avg cost per task | $0.051 | $0.538 | **−90.5%** |
| Total cost (11 tasks) | $0.558 | $5.92 | **−90.6%** |

**Key observations:**

- **Patch quality is the decisive gap.** Nano scores 42.4% on patch correctness vs Sonnet's 81.8%. Root cause (87.9%) and file identification (95.5%) are reasonable, meaning nano understands the problem and finds the right file — it just proposes wrong or incomplete fixes.

- **Two outright fails on complex tasks.** Task 4 (`13398`, ITRS transforms) required a 6-file implementation; nano treated it as a one-line keyword-forwarding patch. Task 9 (`14182`, RST header_rows) required a full feature implementation; nano only widened the constructor signature. Both reveal a pattern of **under-scoping**: the model stops at the symptom (keyword rejection) rather than implementing the full solution.

- **Partial fixes are common.** Tasks 1, 3, 7, and 11 all show the correct file and a plausible approach, but the specific code change diverges from GT: wrong function (`12907`, `13236`), too narrow a guard (`13977`), or missing second fix (`14365`). This pattern is consistent with a model that explores the codebase, finds the general area, but cannot precisely reason about which minimal code change is sufficient.

- **Timeout pressure likely degraded some answers.** Five of 11 tasks ran for ~2684–2685 s (hitting the ~45-minute wall clock limit). Of these, `13579` output 66,585 tokens and scored 7/8 — extended exploration helped. `12907` timed out and scored 5/8 — timeout may have prevented the model from discovering the simpler one-line `_cstack` fix.

- **Cost is dramatically lower.** At $0.051/task, nano is 10.5× cheaper than Sonnet ($0.538/task). For tasks where the root cause is straightforward and a partial fix is acceptable, nano delivers reasonable RC+files scores at a fraction of the cost.

- **Speed is slower (not faster).** Nano averaged 1,841 s/task vs Sonnet's 310 s. The majority of nano's wall clock time is agent loop overhead and exploration iterations, not model latency per se — the token volumes processed are smaller, but the agent makes more round trips (avg 30 requests/task vs Sonnet's ~24).
