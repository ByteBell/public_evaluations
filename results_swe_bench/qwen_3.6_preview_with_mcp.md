# Qwen 3.6 Plus Preview + MCP — SWE-Bench Evaluation Report

**Dataset:** `princeton-nlp/SWE-bench_Verified` — `astropy/astropy`
**Evaluated:** 14 of 22 tasks (8 tasks have no `answer.json` — listed below)
**Date:** 2026-04-02
**Judge:** Claude Code (claude-sonnet-4-6)
**Ground truth source:** `results_swe_bench/astropy_tasks.json`
**Raw responses:** `results_swe_bench/mcp_run_on_qwen3.6_plus_preview_with_mcp/*/answer.json`
**Mode:** Qwen 3.6 Plus Preview via OpenRouter + ByteBell MCP knowledge graph (no direct repo access)

---

## Skipped Tasks (no answer.json)

| Instance ID | Difficulty |
|-------------|------------|
| `astropy__astropy-12907` | 15m–1h |
| `astropy__astropy-13236` | 15m–1h |
| `astropy__astropy-13398` | 1–4h |
| `astropy__astropy-14096` | 15m–1h |
| `astropy__astropy-14598` | 15m–1h |
| `astropy__astropy-7166` | <15m |
| `astropy__astropy-7336` | <15m |
| `astropy__astropy-7671` | 15m–1h |

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
| 1 | `astropy__astropy-13033` | 15m–1h | 3 | 2 | 1 | **6/8** | ⚠️ Partial | 329 | $2.736 |
| 2 | `astropy__astropy-13453` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 921 | $6.621 |
| 3 | `astropy__astropy-13579` | 1–4h | 3 | 2 | 1 | **6/8** | ⚠️ Partial | 1,986 | $3.621 |
| 4 | `astropy__astropy-13977` | 15m–1h | 3 | 2 | 1 | **6/8** | ⚠️ Partial | 1,164 | $10.835 |
| 5 | `astropy__astropy-14182` | 15m–1h | 3 | 2 | 1 | **6/8** | ⚠️ Partial | 340 | $3.902 |
| 6 | `astropy__astropy-14309` | <15m | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 241 | $1.697 |
| 7 | `astropy__astropy-14365` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 1,280 | $3.441 |
| 8 | `astropy__astropy-14369` | 1–4h | 3 | 2 | 3 | **8/8** | ✅ Exact | 3,603 | $6.439 |
| 9 | `astropy__astropy-14508` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 148 | $0.895 |
| 10 | `astropy__astropy-14539` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 158 | $1.691 |
| 11 | `astropy__astropy-14995` | <15m | 3 | 2 | 3 | **8/8** | ✅ Exact | 293 | $3.248 |
| 12 | `astropy__astropy-7606` | 15m–1h | 3 | 2 | 0 | **5/8** | ⚠️ Partial | 176 | $1.813 |
| 13 | `astropy__astropy-8707` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 765 | $4.182 |
| 14 | `astropy__astropy-8872` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 119 | $1.083 |
| | **TOTAL** | | **42/42** | **28/28** | **27/42** | **97/112** | **86.6%** | **11,523 s** | **$52.20** |
| | **AVERAGE** | | | | | **6.9/8** | | **823 s** | **$3.73** |

---

## Dimension Breakdown

| Dimension | Score | Max | % |
|-----------|-------|-----|---|
| Root cause identification | 42 | 42 | **100%** |
| Correct file(s) | 28 | 28 | **100%** |
| Correct patch / code change | 27 | 42 | **64.3%** |
| **Overall** | **97** | **112** | **86.6%** |

---

## Token & Cost Breakdown

| # | Instance ID | Input | Output | Cost | Requests | Models |
|---|-------------|-------|--------|-----:|----------|--------|
| 1 | `13033` | 870,867 | 8,254 | **$2.736** | 21 | Qwen only |
| 2 | `13453` | 2,137,855 | 13,850 | **$6.621** | 32 | Qwen only |
| 3 | `13579` | 888,990 | 63,580 | **$3.621** | 20 | Qwen only |
| 4 | `13977` | 3,446,846 | 32,945 | **$10.835** | 49 | Qwen only |
| 5 | `14182` | 1,269,134 | 6,311 | **$3.902** | 24 | Qwen only |
| 6 | `14309` | 532,687 | 6,608 | **$1.697** | 13 | Qwen only |
| 7 | `14365` | 979,506 | 33,502 | **$3.441** | 17 | Qwen only |
| 8 | `14369` | 1,665,164 | 108,262 | **$6.439** | 37 | Qwen + Haiku |
| 9 | `14508` | 276,573 | 4,365 | **$0.895** | 8 | Qwen only |
| 10 | `14539` | 548,470 | 3,070 | **$1.691** | 13 | Qwen only |
| 11 | `14995` | 1,049,173 | 6,698 | **$3.248** | 23 | Qwen only |
| 12 | `7606` | 582,242 | 4,426 | **$1.813** | 15 | Qwen only |
| 13 | `8707` | 1,335,374 | 11,714 | **$4.182** | 29 | Qwen only |
| 14 | `8872` | 344,293 | 3,328 | **$1.083** | 9 | Qwen only |
| | **TOTAL** | **15,927,174** | **306,913** | **$52.20** | **310** | |

> **Note:** No prompt caching — all tokens billed as input. Task `14369` is the only run where the harness fell back to Claude Haiku (8 requests, $0.13 of the $6.44 total). Average per task: 823 s · $3.73.

---

## Per-Task Answer Comparison

### Task 1 — `13033` — ⚠️ Partial

**Issue:** `TimeSeries` misleading exception on required column removal

| | GT | Qwen MCP |
|---|---|---|
| File | `core.py` | `core.py` |
| GT fix | Use `as_scalar_or_list_str(required_columns)` in the empty-column error branch | Use `repr(required_columns)` and `repr(self.colnames[:len(required_columns)])` |

**-2:** Uses `repr()` instead of the existing `as_scalar_or_list_str()` helper. This produces `['time']` (with brackets) for single-element lists instead of GT's `'time'` (unquoted scalar). The message format diverges from GT and from the non-empty branch which already calls `as_scalar_or_list_str()`. Also proposes modifying test assertions rather than matching existing format.

---

### Task 2 — `13453` — ✅ Near-perfect

**Issue:** HTML writer ignores `formats` argument

| | GT | Qwen MCP |
|---|---|---|
| File | `html.py` | `html.py` |
| GT fix | `self.data.cols = cols` + `self.data._set_col_formats()` | After `_set_fill_values()`, loop cols and directly set `col.info.format` if name is in `self.data.formats` |

**-1:** Bypasses `_set_col_formats()` in favor of direct `col.info.format` assignment. Functionally equivalent for the common case but misses any format-normalization logic inside `_set_col_formats()`. The approach works for the reported issue.

---

### Task 3 — `13579` — ⚠️ Partial

**Issue:** `SlicedLowLevelWCS.world_to_pixel_values` uses hardcoded `1.0` for dropped dimensions

| | GT | Qwen MCP |
|---|---|---|
| File | `sliced_wcs.py` | `sliced_wcs.py` |
| GT fix | Compute `pixel_to_world_values_all` at pixel origin (pixel=0) for dropped dims | Two-pass iterative refinement: initial pixel=0 guess → pixel estimate → refine sliced-out world coords from actual pixels → re-run |

**-2:** The two-pass refinement is unnecessary and introduces incorrect logic. The GT fix is correct with a single evaluation at pixel=0. Qwen's added "refinement" uses `self._wcs.pixel_to_world_values` (the full WCS, not the slice-aware helper) on the intermediate pixel estimate, which doesn't guarantee convergence and is mathematically unjustified. The simpler single-pass fix (same as Qwen raw task 4) is the correct approach.

---

### Task 4 — `13977` — ⚠️ Partial

**Issue:** `Quantity.__array_ufunc__` should return `NotImplemented` for duck types

| | GT | Qwen MCP |
|---|---|---|
| File | `quantity.py` | `quantity.py` |
| GT fix | Wrap entire `__array_ufunc__` body; check `__array_ufunc__` on all inputs/outputs | Only wraps the input-conversion loop with `try/except ValueError: return NotImplemented` |

**-2:** Same partial fix as Qwen raw. Only the converter call in the input loop is guarded. Duck types failing earlier (in `converters_and_unit`) or later (in `_result_as_quantity`) will still raise instead of returning `NotImplemented`. Task 13977 consumed the most resources in this run (49 requests, $10.84).

---

### Task 5 — `14182` — ⚠️ Partial

**Issue:** RST writer needs `header_rows` support

| | GT | Qwen MCP |
|---|---|---|
| File | `rst.py` | `rst.py` |
| GT fix | `__init__(header_rows=None)`, dynamic `sep_line_index` in `write()`, dynamic `start_line` in `read()` | Only adds `__init__(header_rows=None)` passing through to `super()` |

**-2:** The MCP run correctly identifies that `RST.__init__` needs `header_rows=None` and that it should pass to `super().__init__`. However, it leaves `write()` with hardcoded `lines[1]` and `read()` with hardcoded `start_line = 3`. The fix removes the `TypeError` on construction but produces incorrect output for any `header_rows` value other than the default single-row case.

---

### Task 6 — `14309` — ✅ Near-perfect

**Issue:** `is_fits` IndexError with empty args

| | GT | Qwen MCP |
|---|---|---|
| File | `connect.py` | `connect.py` |
| GT fix | Restructure elif so it always returns without accessing `args[0]` | `len(args) > 0 and isinstance(args[0], ...)` |

**-1:** Both fix the crash. Functionally identical for all inputs.

---

### Task 7 — `14365` — ✅ Near-perfect

**Issue:** QDP reader fails on lowercase commands

| | GT | Qwen MCP |
|---|---|---|
| File | `qdp.py` | `qdp.py` |
| GT fix | `re.IGNORECASE` on `_line_type_re` + `v.upper() == "NO"` in data parsing | Only `re.IGNORECASE` on `_line_type_re` |

**-1:** Missing `v.upper() == "NO"` fix for data-line `NO` values. Handles lowercase command keywords but not lowercase `NO` in data lines. Same gap as Qwen raw.

---

### Task 8 — `14369` — ✅ Exact

**Issue:** CDS unit parser right-recursive division (`a/b/c` → `a*c/b`)

| | GT | Qwen MCP |
|---|---|---|
| Files | `cds.py` + `cds_parsetab.py` | `cds.py` + `cds_parsetab.py` |
| GT fix | Grammar rule swap in `p_division_of_units` + regenerated parsetab | Identical: swap `unit_expression DIVISION combined_units` → `combined_units DIVISION unit_expression`; regenerate parsetab |

This is the most complex task in the set (1–4h). Qwen MCP correctly identified the left-vs-right associativity grammar issue and the need to regenerate the parse table. This task used two models — the harness fell back to Claude Haiku for 8 requests alongside 29 Qwen requests.

---

### Task 9 — `14508` — ✅ Near-perfect

**Issue:** `_format_float` uses `.16G` expanding short floats

| | GT | Qwen MCP |
|---|---|---|
| File | `card.py` | `card.py` |
| GT fix | `str(value).replace("e", "E")` | `str(value)` only — missing `.replace("e", "E")` |

**-1:** Correctly replaces `f"{value:.16G}"` with `str(value)`, fixing the over-precision expansion. However, does not add `.replace("e", "E")` to normalize exponent case. FITS requires uppercase `E` in scientific notation; `str(float)` in CPython uses lowercase `e` (e.g. `1.5e+10`). Missing this normalization would produce invalid FITS headers for values requiring scientific notation.

---

### Task 10 — `14539` — ✅ Exact

**Issue:** FITS diff fails for VLA columns with Q format descriptor

| | GT | Qwen MCP |
|---|---|---|
| File | `diff.py` | `diff.py` |
| GT fix | `elif "P" in col.format or "Q" in col.format:` | Identical |

---

### Task 11 — `14995` — ✅ Exact

**Issue:** `_arithmetic_mask` has `operand is None` instead of `operand.mask is None`

| | GT | Qwen MCP |
|---|---|---|
| File | `ndarithmetic.py` | `ndarithmetic.py` |
| GT fix | `elif operand.mask is None:` | Identical — clean minimal one-line fix |

---

### Task 12 — `7606` — ⚠️ Partial

**Issue:** `Unit.__eq__` returns `False` instead of `NotImplemented`

| | GT | Qwen MCP |
|---|---|---|
| Files | `core.py` — both `UnitBase.__eq__` and `UnrecognizedUnit.__eq__` | `core.py` — only `UnrecognizedUnit.__eq__` |
| GT fix | `return NotImplemented` in both classes | `try/except TypeError: return False` in `UnrecognizedUnit.__eq__` only |

**-3:** Two critical errors: (1) Returns `False` instead of `NotImplemented` — semantically wrong, breaks Python's reflected-operator fallback protocol. When `a == b` returns `False`, Python accepts it as the final answer. When it returns `NotImplemented`, Python then tries `b.__eq__(a)`. (2) Misses `UnitBase.__eq__` entirely — the primary class used in practice. Compared to Qwen raw (6/8), the MCP run is actually worse here because Qwen raw correctly returned `NotImplemented`.

---

### Task 13 — `8707` — ✅ Exact

**Issue:** `Card.fromstring` / `Header.fromstring` don't accept bytes

| | GT | Qwen MCP |
|---|---|---|
| Files | `card.py`, `header.py` | `card.py`, `header.py` |
| GT fix | `Card.fromstring`: decode latin-1. `Header.fromstring`: bytes-aware refactor | Identical: both `decode('latin1')`, clean placement before the main loop in `Header.fromstring` |

Best answer in this run — correctly uses `latin-1` (not `ascii`) for both decoding sites, matching the FITS spec's 8-bit character allowance.

---

### Task 14 — `8872` — ✅ Exact

**Issue:** `np.float16` quantities upgraded to float64

| | GT | Qwen MCP |
|---|---|---|
| File | `quantity.py` | `quantity.py` |
| GT fix | Replace `np.can_cast(np.float32, value.dtype)` with `np.issubdtype(value.dtype, np.inexact)` | Identical at both locations (lines 299–300 and 380–381) |

---

## Grade Distribution

| Grade | Count | Tasks |
|-------|-------|-------|
| ✅ Exact (8/8) | 5 | 8, 10, 11, 13, 14 |
| ✅ Near-perfect (7/8) | 4 | 2, 6, 7, 9 |
| ⚠️ Partial (6/8) | 4 | 1, 3, 4, 5 |
| ⚠️ Partial (5/8) | 1 | 12 |
| ❌ Fail (≤4/8) | 0 | — |

**Exact + Near-perfect: 9/14 (64.3%)**

---

## Notable Observations

- **Root cause and file identification: perfect (100%).** The MCP knowledge graph successfully guided the model to the correct files on every task, including multi-file tasks (`14369`, `8707`).
- **Patch quality is the weakest dimension (64.3%).** Four tasks scored partial (6/8) due to incomplete scope or wrong approach. The common failure mode is stopping at the most obvious change without checking whether downstream code also needs updating (e.g. `14182` fixes `__init__` but not `write()`/`read()`).
- **Task 13033 regression vs. raw run.** The raw run used `as_scalar_or_list_str()` (correct), the MCP run used `repr()` (different format). The MCP graph may have surfaced the method but the model chose a different implementation path.
- **Task 13579 over-engineering.** The MCP run produced a two-pass iterative refinement for `world_to_pixel_values` when a single pixel=0 evaluation is sufficient. Increased output tokens (63,580) reflect exploratory drift.
- **Task 7606 is worse than Qwen raw.** Qwen raw returned `NotImplemented` (semantically correct); the MCP run returns `False` (wrong). Both miss `UnitBase.__eq__`. The MCP run's additional context did not help and may have misdirected toward a quick `TypeError`-silencing pattern.
- **Task 14369 (CDS grammar) is the strongest MCP result.** The hardest task (1–4h, grammar + parsetab) was solved correctly. The knowledge graph likely provided targeted pointers to `cds.py` and `cds_parsetab.py` that would otherwise require deep repo exploration.
- **Cost remains high.** At $3.73/task average ($52.20 total for 14 tasks), the MCP mode does not reduce cost compared to raw mode ($3.95/task for 16 tasks). Task 13977 alone cost $10.84 (49 requests) for a partial fix.
- **Task 14508 fastest run (148 s, $0.895, 8 requests).** The MCP graph delivered the exact file location immediately, allowing a quick targeted fix — the clearest example of MCP providing value on a well-indexed file.
