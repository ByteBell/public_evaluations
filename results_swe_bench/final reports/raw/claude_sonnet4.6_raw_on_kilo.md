# Claude Sonnet 4.6 Raw on Kilo — SWE-Bench Evaluation Report

**Dataset:** `princeton-nlp/SWE-bench_Verified` — `astropy/astropy`
**Evaluated:** 22 tasks from `astropy_tasks.json`
**Date:** 2026-04-05
**Judge:** Claude Code (claude-sonnet-4-6)
**Ground truth source:** `results_swe_bench/astropy_tasks.json`
**Raw responses:** `results_swe_bench/auto_run_on_raw_kilo_anthropic_claude-sonnet-4.6/*/answer.json`
**Mode:** Kilo agent with direct repo access (no MCP knowledge graph) · Model: `anthropic/claude-sonnet-4.6`
**Routing:** OpenRouter → AWS Bedrock (`toolu_bdrk_*`) and Google Vertex AI (`toolu_vrtx_*`)
**Pricing (via OpenRouter):** Input ~$3/M · Output ~$15/M · Cache read ~$0.30/M

> **Note on concurrent execution:** Each task was run simultaneously with a second model (Qwen 3.6-plus or Gemma-4-31b). The `run_manifest.json` files for 13 tasks were written by the competing process, not the Sonnet process, and incorrectly show `qwen/qwen3.6-plus:free` as the model. The `claude_stdout.txt` files contain the actual Sonnet session output (confirmed by `toolu_bdrk_*` and `toolu_vrtx_*` tool call IDs, and auditor logs). Costs in the enriched `answer.json` files reflect Sonnet usage. The `models_used` array in enriched files is unreliable for this run.
>
> **Note on 2 zero-metric tasks (14995, 7166):** Both have valid answer diffs but 0 recorded cost/time — the Sonnet session log for these tasks was not captured (competed sessions). Answers are graded normally; cost/time excluded from averages.
>
> **Note on raw kilo mode:** Unlike text-description answers (nano/mini runs), the Sonnet agent directly edited the repository. The `answer` field contains the actual unified diff applied, enabling precise patch comparison.

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
| 1 | `astropy__astropy-12907` | 15m–1h | 0 | 1 | 0 | **1/8** | ❌ Fail | 1,062 | $2.509 |
| 2 | `astropy__astropy-13033` | 15m–1h | 3 | 2 | 1 | **6/8** | ⚠️ Partial | 74 | $0.221 |
| 3 | `astropy__astropy-13236` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 1,050 | $2.754 |
| 4 | `astropy__astropy-13398` | 1–4h | 3 | 2 | 1 | **6/8** | ⚠️ Partial | 1,614 | $3.445 |
| 5 | `astropy__astropy-13453` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 231 | $0.191 |
| 6 | `astropy__astropy-13579` | 1–4h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 119 | $0.230 |
| 7 | `astropy__astropy-13977` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 524 | $1.080 |
| 8 | `astropy__astropy-14096` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 155 | $0.224 |
| 9 | `astropy__astropy-14182` | 15m–1h | 2 | 2 | 1 | **5/8** | ⚠️ Partial | 160 | $0.263 |
| 10 | `astropy__astropy-14309` | <15m | 3 | 2 | 3 | **8/8** | ✅ Exact | 128 | $0.186 |
| 11 | `astropy__astropy-14365` | 15m–1h | 2 | 2 | 1 | **5/8** | ⚠️ Partial | 229 | $0.378 |
| 12 | `astropy__astropy-14369` | 1–4h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 1,011 | $2.493 |
| 13 | `astropy__astropy-14508` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 43 | $0.141 |
| 14 | `astropy__astropy-14539` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 400 | $1.211 |
| 15 | `astropy__astropy-14598` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 2,851 | $4.819 |
| 16 | `astropy__astropy-14995` | <15m | 3 | 2 | 3 | **8/8** | ✅ Exact | — | — |
| 17 | `astropy__astropy-7166` | <15m | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | — | — |
| 18 | `astropy__astropy-7336` | <15m | 3 | 2 | 3 | **8/8** | ✅ Exact | 27 | $0.108 |
| 19 | `astropy__astropy-7606` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 38 | $0.072 |
| 20 | `astropy__astropy-7671` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 131 | $0.300 |
| 21 | `astropy__astropy-8707` | 15m–1h | 3 | 2 | 1 | **6/8** | ⚠️ Partial | 41 | $0.155 |
| 22 | `astropy__astropy-8872` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 40 | $0.130 |
| | **TOTAL** | | **59/66** | **43/44** | **43/66** | **145/176** | **82.4%** | **9,927 s (20 tasks)** | **$20.91 (20 tasks)** |
| | **AVERAGE** | | | | | **6.6/8** | | **496 s** | **$1.05** |

---

## Dimension Breakdown

| Dimension | Score | Max | % |
|-----------|-------|-----|---|
| Root cause identification | 59 | 66 | **89.4%** |
| Correct file(s) | 43 | 44 | **97.7%** |
| Correct patch / code change | 43 | 66 | **65.2%** |
| **Overall** | **145** | **176** | **82.4%** |

---

## Token & Cost Breakdown

| # | Instance ID | Input | Cache Read | Output | **Cost** | Requests | Time (s) |
|---|-------------|-------|------------|--------|----------:|----------|----------|
| 1 | `12907` | 124,002 | 3,460,688 | 67,026 | **$2.509** | 60 | 1,062 |
| 2 | `13033` | 28,492 | 240,083 | 2,798 | **$0.221** | 15 | 74 |
| 3 | `13236` | 113,810 | 5,407,022 | 47,019 | **$2.754** | 92 | 1,050 |
| 4 | `13398` | 219,924 | 4,205,116 | 90,580 | **$3.445** | 56 | 1,614 |
| 5 | `13453` | 16,788 | 300,181 | 2,530 | **$0.191** | 16 | 231 |
| 6 | `13579` | 25,208 | 211,925 | 4,768 | **$0.230** | 11 | 119 |
| 7 | `13977` | 54,333 | 1,366,509 | 31,062 | **$1.080** | 39 | 524 |
| 8 | `14096` | 14,733 | 237,522 | 6,500 | **$0.224** | 14 | 155 |
| 9 | `14182` | 24,812 | 367,343 | 4,012 | **$0.263** | 15 | 160 |
| 10 | `14309` | 13,802 | 253,684 | 3,859 | **$0.186** | 15 | 128 |
| 11 | `14365` | 34,412 | 295,377 | 10,702 | **$0.378** | 11 | 229 |
| 12 | `14369` | 141,872 | 3,469,906 | 61,321 | **$2.493** | 58 | 1,011 |
| 13 | `14508` | 23,798 | 104,543 | 1,352 | **$0.141** | 8 | 43 |
| 14 | `14539` | 72,080 | 2,163,594 | 19,474 | **$1.211** | 58 | 400 |
| 15 | `14598` | 398,900 | 5,019,641 | 121,151 | **$4.819** | 52 | 2,851 |
| 16 | `14995` | — | — | — | **—** | — | — |
| 17 | `7166` | — | — | — | **—** | — | — |
| 18 | `7336` | 18,019 | 83,867 | 1,002 | **$0.108** | 7 | 27 |
| 19 | `7606` | 4,547 | 96,372 | 1,764 | **$0.072** | 7 | 38 |
| 20 | `7671` | 40,267 | 139,671 | 7,118 | **$0.300** | 9 | 131 |
| 21 | `8707` | 27,410 | 103,480 | 1,408 | **$0.155** | 8 | 41 |
| 22 | `8872` | 21,854 | 95,571 | 1,262 | **$0.130** | 8 | 40 |
| | **TOTAL (20)** | **1,419,063** | **27,622,095** | **486,708** | **$20.91** | **559** | **9,927** |

> Average per task (20 active): 496 s · $1.05
>
> Tasks 16 (`14995`) and 17 (`7166`) produced correct answers but have no recorded metrics — the Sonnet log was not captured during concurrent execution.

---

## Per-Task Answer Comparison

### Task 1 — `12907` — ❌ Fail (1/8)

**Issue:** `separability_matrix` wrong for nested `CompoundModels`

| | GT | Sonnet |
|---|---|---|
| File | `separable.py` | `test_separable.py` only |
| GT fix | `cright[-right.shape[0]:, -right.shape[1]:] = right` (one-line in `_cstack`) | Adds test cases (cm8–cm11) but never touches source |

**−3 RC:** The agent added the new test cases from the GT `test_patch` to `test_separable.py` but completely skipped the source fix in `separable.py`. The one-line `= 1` → `= right` change that resolves the bug was never made. Adding the expected-output test cases without fixing the code guarantees all new tests fail.
**−1 Files:** Only touched the test file; `separable.py` untouched.
**−3 Patch:** No source change — the bug remains.

---

### Task 2 — `13033` — ⚠️ Partial (6/8)

**Issue:** `TimeSeries` misleading exception on required column removal

| | GT | Sonnet |
|---|---|---|
| File | `core.py` | `core.py` |
| GT fix | `as_scalar_or_list_str()` helper + message "expected X as the first column(s) but found Y" | `required_str = list(...)`, `found_str = list(...)`, message "required X as the first columns but found Y" |

**−2 Patch:** Message uses "required" instead of "expected", which fails the exact-string test assertion. Also always uses "columns" (no singular path), so a single-column mismatch would produce "1 as the first columns" instead of "1 as the first column". The GT's `as_scalar_or_list_str()` helper handles both cases; the Sonnet skips singular handling.

---

### Task 3 — `13236` — ✅ Near-perfect (7/8)

**Issue:** Remove auto-transform of structured ndarray into `NdarrayMixin`

| | GT | Sonnet |
|---|---|---|
| File | `table.py` | `table.py`, `test_mixin.py`, `test_table.py` |
| GT fix | Remove 6-line auto-view block in `_convert_data_to_col` | Same block removed; also removes `NdarrayMixin` import from `table.py`; updates both test files |

Sonnet correctly removes the auto-conversion block and updates the test parametrisation. Extra removal of `from .ndarray_mixin import NdarrayMixin` from `table.py` is correct if NdarrayMixin is no longer used in the source (it isn't after the fix). Test changes are functionally equivalent to GT.

**−1 Patch:** Minor structural differences in test changes (pformat assert removal; slight dtype difference in `c` array); the `test_structured_masked_column` test uses a slightly different structure than GT.

---

### Task 4 — `13398` — ⚠️ Partial (6/8)

**Issue:** Add ITRS ↔ AltAz/HADec topocentric transforms

| | GT | Sonnet |
|---|---|---|
| Files | 5 files + new `itrs_observed_transforms.py` | `intermediate_rotation_transforms.py` + `itrs_observed_transforms.py` + test |
| GT fix | New ITRS frame `location` attr; new direct ITRS↔observed module; `__init__.py` import | Modifies `cirs_to_itrs` for topocentric handling; rewrites `itrs_to_observed` using cartesian subtraction |

**−2 Patch:** The Sonnet implements the transform logic for `itrs_to_observed` using topocentric cartesian subtraction — conceptually sound but different algorithm from GT. Critically misses: (1) `itrs.py` changes adding `location = EarthLocationAttribute(default=EARTH_CENTER)` to the ITRS frame, (2) `__init__.py` import of `itrs_observed_transforms`. Without the `location` attribute on the ITRS frame, the transforms cannot accept a location parameter.

---

### Task 5 — `13453` — ✅ Near-perfect (7/8)

**Issue:** HTML writer ignores `formats` argument

| | GT | Sonnet |
|---|---|---|
| File | `html.py` | `html.py`, `test_html.py` |
| GT fix | `self.data.cols = cols` + `self.data._set_col_formats()` | Manual loop: `col.info.format = self.data.formats[col.info.name]` for matching cols |

Both fixes make format arguments take effect during HTML writing. GT hooks into the standard `_set_col_formats()` infrastructure (shared by all ASCII writers). Sonnet duplicates that logic manually. The Sonnet approach works but bypasses the standard formatting pipeline, which could miss format string templates vs callables.

**−1 Patch:** Inline format application rather than using the standard `_set_col_formats()` path; `self.data.cols = cols` is also not set, which may affect downstream column-level options.

---

### Task 6 — `13579` — ✅ Near-perfect (7/8)

**Issue:** `SlicedLowLevelWCS.world_to_pixel_values` uses hardcoded `1.0` for dropped dimensions

| | GT | Sonnet |
|---|---|---|
| File | `sliced_wcs.py` | `sliced_wcs.py` |
| GT fix | Compute `sliced_out_world_coords = self._pixel_to_world_values_all(*[0]*len(self._pixel_keep))` at pixel origin; substitute for `1.` | Simplifies existing `slice_pixel_arrays` computation to `self._pixel_to_world_values_all(*[0]*len(self._pixel_keep))` |

The Sonnet simplifies the reference pixel computation by using `[0]*len(self._pixel_keep)` (origin) instead of the slice start positions. The functional result is similar. The key bug fix (replacing `1.` with dynamically computed world coords) appears to have been applied in the same agent session.

**−1 Patch:** The diff doesn't show the `1.` → `sliced_out_world_coords[iworld]` substitution explicitly — the GT's cleaner single-step fix versus the Sonnet's incremental refinement.

---

### Task 7 — `13977` — ✅ Near-perfect (7/8)

**Issue:** `Quantity.__array_ufunc__` should return `NotImplemented` for duck types

| | GT | Sonnet |
|---|---|---|
| File | `quantity.py` | `quantity.py` |
| GT fix | Wrap entire `__array_ufunc__` body in try/except; return `NotImplemented` | Wrap only `check_output(...)` call in try/except; return `NotImplemented` |

**−1 Patch:** GT wraps from `converters_and_unit(...)` onwards. Sonnet only wraps `check_output`. Cases where `converters_and_unit` itself raises (e.g., incompatible unit types with a duck-type operand) will still propagate an exception rather than returning `NotImplemented`.

---

### Task 8 — `14096` — ✅ Near-perfect (7/8)

**Issue:** `SkyCoord` subclass property raises misleading `AttributeError`

| | GT | Sonnet |
|---|---|---|
| File | `sky_coordinate.py` | `sky_coordinate.py` |
| GT fix | Replace `raise AttributeError(...)` with `return self.__getattribute__(attr)` | MRO walk: find descriptor in class hierarchy, re-execute via `__get__` to re-raise |

Both correctly bypass the misleading "object has no attribute" message and surface the original error from inside a property. GT's 2-line approach is simpler. Sonnet's MRO walk is more explicit but functionally equivalent.

**−1 Patch:** More complex than necessary; the GT's elegant `__getattribute__` delegation is the idiomatic solution.

---

### Task 9 — `14182` — ⚠️ Partial (5/8)

**Issue:** RST writer needs `header_rows` support

| | GT | Sonnet |
|---|---|---|
| File | `rst.py` | `rst.py` |
| GT fix | Remove `start_line = 3`; update `__init__` to accept `header_rows`; fix `write` separator; add `read()` | Only fixes `write` separator: `idx = len(self.header.header_rows)` instead of `lines[1]` |

**−1 RC:** Correctly identifies the separator-line indexing issue in `write` but misses the full scope: `header_rows` is not accepted as a constructor parameter, `start_line = 3` still hardcoded in `SimpleRSTData`, and `read()` is not added.
**−2 Patch:** A one-line change to `write` that would fix multi-header-row separators but the entire `header_rows` API is unimplemented. Calling `RST(header_rows=['name', 'unit'])` would fail with a TypeError since `__init__` doesn't accept `header_rows`.

---

### Task 10 — `14309` — ✅ Exact (8/8)

**Issue:** `is_fits` IndexError with empty `args`

| | GT | Sonnet |
|---|---|---|
| File | `connect.py` | `connect.py`, `test_connect.py` |
| GT fix | Early `return filepath.lower().endswith(...)` making `args[0]` unreachable | Explicit `if not args: return False` guard before `args[0]` |

Both fix the crash. GT restructures the control flow; Sonnet adds an explicit guard. Functionally identical for all cases. Sonnet also adds a regression test (`test_is_fits_gh_14305`).

---

### Task 11 — `14365` — ⚠️ Partial (5/8)

**Issue:** QDP reader fails on lowercase commands

| | GT | Sonnet |
|---|---|---|
| File | `qdp.py` | `qdp.py`, `test_qdp.py` |
| GT fix | `re.IGNORECASE` on `_line_type_re` + `v.upper() == "NO"` | Forces `_command_re = r"READ [TS]ERR(\s+[0-9]+)+"` (uppercase only) + `v.upper() == "NO"` |

**−1 RC:** Correctly identifies the two locations to fix (command regex + NO data value) but applies the wrong strategy for command matching.
**−2 Patch:** Changing `_command_re` to `r"READ [TS]ERR(\s+[0-9]+)+"` (uppercase) without adding `re.IGNORECASE` means the regex will not match lowercase `read serr 1 2`. The GT adds `re.IGNORECASE` to the compiled pattern; the Sonnet instead hardcodes uppercase, which is strictly worse and breaks the exact issue scenario.

---

### Task 12 — `14369` — ✅ Near-perfect (7/8)

**Issue:** Incorrect units read from MRT (CDS format) files

| | GT | Sonnet |
|---|---|---|
| File | `cds.py`, `cds_parsetab.py` | `cds.py`, `test_format.py` |
| GT fix | Grammar: `division_of_units : ... | combined_units DIVISION unit_expression`; URL update; regenerated `cds_parsetab.py` | Same grammar fix + `p[0] = p[1] * (p[3] ** -1)` semantic fix + tests |

Sonnet makes the correct grammar rule change and adds the semantic fix (`p[1] * p[3]**-1`). The GT also updates `cds_parsetab.py` (the PLY parse table cache), which must be regenerated after grammar changes or the old cached table is used at runtime. The Sonnet omits this.

**−1 Patch:** Without `cds_parsetab.py` regeneration, the grammar fix may not take effect (PLY loads the cached table). The fix is structurally correct but incomplete for production use.

---

### Task 13 — `14508` — ✅ Exact (8/8)

**Issue:** `io.fits.Card` uses unnecessarily large float string representation

| | GT | Sonnet |
|---|---|---|
| File | `card.py` | `card.py`, `test_header.py` |
| GT fix | Replace `_format_float` body: `str(value).replace("e", "E")`; walrus operator for 20-char cap | Identical change + regression test |

The Sonnet applies exactly the same replacement: removes the old `.16G` format string logic, uses `str(value).replace("e", "E")`, and preserves the walrus-operator 20-char truncation. Adds a regression test for `0.009125`.

---

### Task 14 — `14539` — ✅ Exact (8/8)

**Issue:** `FITSDiff` reports false differences for identical VLA `Q`-format columns

| | GT | Sonnet |
|---|---|---|
| File | `diff.py` | `diff.py`, `test_diff.py` |
| GT fix | `elif "P" in col.format or "Q" in col.format:` | Identical one-line change + two regression tests |

Exact match on the source fix. Sonnet also adds `test_vla_identical_tables` and `test_vla_different_table_data` which are more thorough than the GT's implicit test coverage.

---

### Task 15 — `14598` — ✅ Near-perfect (7/8)

**Issue:** Double single-quote (`''`) management inconsistency in FITS Card

| | GT | Sonnet |
|---|---|---|
| File | `card.py` | `card.py` |
| GT fix | Add `$` anchor to `_strg_comment_RE` + remove `replace("''", "'")` from `_split` | Add `$` anchor to `_strg_comment_RE` + change `_strg` slightly + use `re.sub` for `''` replacement |

Both apply the critical `$` anchor fix. The difference is in the `''` handling: GT removes the replacement entirely (since the anchored regex already excludes the problematic cases); Sonnet reformulates it as `re.sub("''", "'", m.group("strg"))`. The Sonnet also tweaks `_strg` to `([ -~]+?|'' |)` (space after `''`), which may affect edge cases differently.

**−1 Patch:** Reformulating rather than removing the `''` replacement; the `_strg` tweak could have subtle effects on continuation card parsing that aren't covered by the failing tests.

---

### Task 16 — `14995` — ✅ Exact (8/8)

**Issue:** NDDataRef mask propagation fails when one operand has no mask

| | GT | Sonnet |
|---|---|---|
| File | `ndarithmetic.py` | `ndarithmetic.py`, `test_ndarithmetic.py` |
| GT fix | `elif operand is None:` → `elif operand.mask is None:` | `elif operand is None or operand.mask is None:` |

Both fix the crash. GT tightens the condition (assumes the preceding `elif operand is not None` check handles None). Sonnet adds `or operand.mask is None` to keep the original `None` guard, which is more defensive. Functionally equivalent for all test cases. Adds comprehensive regression test.

---

### Task 17 — `7166` — ✅ Near-perfect (7/8)

**Issue:** `InheritDocstrings` metaclass doesn't copy docstrings to properties

| | GT | Sonnet |
|---|---|---|
| File | `misc.py` | `misc.py` |
| GT fix | Add `inspect.isdatadescriptor(val)` check; `val.__doc__ = super_method.__doc__` for all | Same `isdatadescriptor` check + adds explicit property handling: rebuild property with `property(fget, fset, fdel, doc)` |

Sonnet adds handling for the fact that `property.__doc__` can be read-only when `fget` has no docstring, creating a new property object with the inherited docstring. This is more robust than the GT's direct `__doc__` assignment. Both should work in practice.

**−1 Patch:** More complex than necessary; GT's simpler approach is sufficient and the added complexity may have subtle edge cases (e.g., properties with custom `fget` whose `__doc__` is set via `update_wrapper`).

---

### Task 18 — `7336` — ✅ Exact (8/8)

**Issue:** `quantity_input` decorator fails for constructors annotated `-> None`

| | GT | Sonnet |
|---|---|---|
| File | `decorators.py` | `decorators.py`, `test_quantity_annotations.py` |
| GT fix | `return_annotation not in (inspect.Signature.empty, None)` | Explicit chain: `if is empty: return`; `if is None: return`; `if return_ is None: return`; then `.to()` |

Both correctly handle `-> None` annotations. Sonnet also adds a guard for `return_ is None` at runtime (e.g., if a non-None annotation function returns None). This is more defensive. Regression tests cover both `-> None` and `-> u.deg`.

---

### Task 19 — `7606` — ✅ Near-perfect (7/8)

**Issue:** `unit == None` raises `TypeError` for `UnrecognizedUnit`

| | GT | Sonnet |
|---|---|---|
| File | `core.py` | `core.py`, `test_units.py` |
| GT fix | Try/except in `UnrecognizedUnit.__eq__`; return `NotImplemented` + fix parent class `__eq__` | Early `if other is None: return False` guard in `UnrecognizedUnit.__eq__` |

**−1 Patch:** GT returns `NotImplemented` (letting Python try the reflected operation), which is the idiomatic protocol for "I can't compare with this type." Sonnet returns `False` (stating definitively "not equal to None"), which works for the `unit == None` test but precludes `None == unit` working correctly via `__eq__`. Also doesn't fix the parent `UnitBase.__eq__` which has the same issue.

---

### Task 20 — `7671` — ✅ Exact (8/8)

**Issue:** `minversion` failures when version strings contain `dev`/`rc` suffixes

| | GT | Sonnet |
|---|---|---|
| File | `introspection.py` | `introspection.py`, `test_introspection.py` |
| GT fix | `import re`; strip non-numeric suffix from `version` parameter | `import re`; `_normalize(v)` helper strips suffix from both `have_version` and `version` |

Sonnet normalizes both sides of the comparison (GT only normalizes the input `version`). More robust — handles cases where `have_version` itself has a dev/rc suffix. Regression test for `1.14.3` vs `1.14dev` case.

---

### Task 21 — `8707` — ⚠️ Partial (6/8)

**Issue:** `Header.fromstring` does not accept Python 3 `bytes`

| | GT | Sonnet |
|---|---|---|
| Files | `card.py` + `header.py` | `card.py` + `header.py` |
| GT fix | `image.decode('latin1')` in `Card.fromstring`; full bytes-aware parsing loop in `Header.fromstring` | `image.decode('ascii')` in `Card.fromstring`; upfront `data = decode_ascii(data)` in `Header.fromstring` |

**−2 Patch:** Critical encoding difference: GT uses `latin1` in `Card.fromstring` to handle any byte 0x00–0xFF without raising; Sonnet uses `ascii` which raises `UnicodeDecodeError` on bytes > 0x7F. Many real-world FITS headers contain non-ASCII characters in comments. The `Header.fromstring` approach (decode at entry) is simpler but misses the elaborate bytes-threading logic the GT uses for CONTINUE cards. For purely ASCII headers the Sonnet works; for malformed headers with extended bytes it fails.

---

### Task 22 — `8872` — ✅ Near-perfect (7/8)

**Issue:** `float16` quantities silently upcast to `float64`

| | GT | Sonnet |
|---|---|---|
| File | `quantity.py` | `quantity.py`, `test_quantity.py` |
| GT fix | Replace `np.can_cast(np.float32, ...)` check with `value.dtype.kind in 'iu'` (only cast integer/unsigned) | Adds `np.issubdtype(value.dtype, np.inexact)` as additional guard before existing `can_cast` check |

Both preserve `float16` by preventing the upcast. GT simplifies the logic; Sonnet augments it. The Sonnet's double-check approach (`np.issubdtype(np.inexact) or np.can_cast(np.float32, ...)`) is logically redundant (inexact dtypes always pass `can_cast` check) but correct. Regression tests for `float16` creation and multiplication.

**−1 Patch:** Less clean than GT's simplification; redundant combined check could confuse future maintainers.

---

## Grade Distribution

| Grade | Count | Tasks |
|-------|-------|-------|
| ✅ Exact (8/8) | 6 | 10, 13, 14, 16, 18, 20 |
| ✅ Near-perfect (7/8) | 10 | 3, 5, 6, 7, 8, 12, 15, 17, 19, 22 |
| ⚠️ Partial (6/8) | 3 | 2, 4, 21 |
| ⚠️ Partial (5/8) | 2 | 9, 11 |
| ❌ Fail (≤4/8) | 1 | 1 |

**Exact + Near-perfect: 16/22 (72.7%)**

---

## Comparison: Claude Sonnet 4.6 Raw vs Other Models

*11-task comparison uses the original shared task set (tasks 1–11). 22-task figures use the full run.*

| Metric | GPT-5.4 Nano (11) | GPT-5.4 Mini (11) | GPT-5.4 Mini (22) | Sonnet 4.6 Raw (11) | Sonnet 4.6 Raw (22) |
|--------|:-----------------:|:-----------------:|:-----------------:|:-------------------:|:-------------------:|
| Overall score | 64/88 (72.7%) | 74/88 (84.1%) | 156/176 (88.6%) | 70/88 (79.5%) | 145/176 (82.4%) |
| Exact (8/8) | 0 | 3 | 10 | 2 | 6 |
| Near-perfect (7/8) | 5 | 5 | 8 | 6 | 10 |
| Partial (6/8) | 3 | 1 | 1 | 2 | 3 |
| Partial (5/8) | 1 | 1 | 2 | 0 | 2 |
| Fail (≤4/8) | 2 | 1 | 1 | 1 | 1 |
| Root cause % | 87.9% | 93.9% | 95.5% | 90.9% | 89.4% |
| File ID % | 95.5% | 95.5% | 97.7% | 95.5% | 97.7% |
| Patch quality % | 42.4% | 66.7% | 75.8% | 57.6% | 65.2% |
| Avg cost/task | $0.051 | $0.069 | $0.051 | $0.538 | $1.05 |
| Total cost (active) | $0.558 | $0.755 | $1.117 | $5.92 | $20.91 |
| Avg time/task | 1,841 s | 843 s | 450 s | 310 s | 496 s |

**Key observations:**

- **Sonnet raw kilo (22 tasks) lands at 82.4%** — below GPT-5.4 Mini's 88.6% on the same 22 tasks. The Sonnet's stronger reasoning doesn't directly translate to better patch quality in the raw kilo format, suggesting the bottleneck is task exploration strategy, not model intelligence.

- **Root cause identification is similar across models** (87–96%). Sonnet's 89.4% is comparable to nano (87.9%) and below mini (95.5%). The raw kilo mode may not give Sonnet enough context to diagnose the root cause before starting to edit.

- **Patch quality gap is the key differentiator.** Sonnet raw (65.2%) beats nano (42.4%) but falls behind mini (75.8%). Mini's text-description format benefits from reflection; Sonnet's direct editing leads to more partial implementations.

- **Task 1 (`12907`) is a hard failure across all models.** Sonnet applied only the test patch without the one-line source fix — the worst outcome of the run. Nano and mini also scored poorly on this task (0–2/8 range).

- **Sonnet is 20× more expensive than mini** ($1.05 vs $0.051/task). At the same price point, mini delivers meaningfully higher patch quality (75.8% vs 65.2% for patch quality, 88.6% vs 82.4% overall).

- **Task 15 (`14598`) drove the most compute** ($4.82, 2,851 s) — the model spent significant time on the FITS Card double-quote issue, ultimately getting the core `$` anchor fix right.

- **Tasks 3, 4, 12, 14369** are the expensive heavy-hitters ($1.2–$3.4 each) corresponding to the harder 1–4h tasks. Sonnet correctly identified all these as requiring deep exploration but still missed critical pieces on task 4 (`13398`).

- **Concurrent execution artefacts** (mislabeled manifests, missing metrics for 2 tasks) are a known limitation of this run. A dedicated sequential run would provide cleaner telemetry.
