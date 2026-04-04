# GPT-5.4 Mini Raw on Kilo — SWE-Bench Evaluation Report

**Dataset:** `princeton-nlp/SWE-bench_Verified` — `astropy/astropy`
**Evaluated:** 22 tasks from `astropy_tasks.json`
**Date:** 2026-04-03
**Judge:** Claude Code (claude-sonnet-4-6)
**Ground truth source:** `results_swe_bench/astropy_tasks.json`
**Raw responses:** `results_swe_bench/auto_run_on_raw_kilo_openai_gpt-5.4-mini/*/answer.json`
**Mode:** Kilo agent with direct repo access (no MCP knowledge graph) · Model: `openai/gpt-5.4-mini`
**Pricing:** Input $0.75/M · Output $4.50/M · Cache read $0.075/M (90% off) · Cache write $4.50/M

> **Note on timeouts (tasks 1–11):** 7 of the first 11 tasks recorded ≈1306 s, consistent with a ~21-minute wall-clock limit. All produced a complete answer JSON.
>
> **Note on tasks 12–22:** These ran concurrently with a Qwen session; some manifests recorded the wrong model name. Token/cost metrics are extracted from the Kilo streaming JSON (step_finish events) which reflect actual gpt-5.4-mini usage, except task 22 (`8872`) whose stdout was routed to the nano output directory by a path bug — metrics there reflect a qwen-model session and should be treated as approximate.

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
| 1 | `astropy__astropy-12907` | 15m–1h | 2 | 2 | 1 | **5/8** | ⚠️ Partial | 259 | $0.069 |
| 2 | `astropy__astropy-13033` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 277 | $0.123 |
| 3 | `astropy__astropy-13236` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 1,307 | $0.029 |
| 4 | `astropy__astropy-13398` | 1–4h | 2 | 1 | 1 | **4/8** | ❌ Fail | 289 | $0.144 |
| 5 | `astropy__astropy-13453` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 1,307 | $0.048 |
| 6 | `astropy__astropy-13579` | 1–4h | 3 | 2 | 1 | **6/8** | ⚠️ Partial | 272 | $0.056 |
| 7 | `astropy__astropy-13977` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 1,306 | $0.026 |
| 8 | `astropy__astropy-14096` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 1,306 | $0.047 |
| 9 | `astropy__astropy-14182` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 338 | $0.155 |
| 10 | `astropy__astropy-14309` | <15m | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 1,306 | $0.054 |
| 11 | `astropy__astropy-14365` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 1,306 | $0.004 |
| 12 | `astropy__astropy-14369` | 1–4h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 46 | $0.057 |
| 13 | `astropy__astropy-14508` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 49 | $0.032 |
| 14 | `astropy__astropy-14539` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 17 | $0.014 |
| 15 | `astropy__astropy-14598` | 15m–1h | 2 | 2 | 1 | **5/8** | ⚠️ Partial | 40 | $0.069 |
| 16 | `astropy__astropy-14995` | <15m | 3 | 2 | 3 | **8/8** | ✅ Exact | 24 | $0.029 |
| 17 | `astropy__astropy-7166` | <15m | 3 | 2 | 3 | **8/8** | ✅ Exact | 10 | $0.021 |
| 18 | `astropy__astropy-7336` | <15m | 3 | 2 | 3 | **8/8** | ✅ Exact | 14 | $0.015 |
| 19 | `astropy__astropy-7606` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 4 | $0.010 |
| 20 | `astropy__astropy-7671` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 42 | $0.028 |
| 21 | `astropy__astropy-8707` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 21 | $0.027 |
| 22 | `astropy__astropy-8872` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 354 | $0.060 |
| | **TOTAL** | | **63/66** | **43/44** | **50/66** | **156/176** | **88.6%** | **9,895 s** | **$1.117** |
| | **AVERAGE** | | | | | **7.1/8** | | **450 s** | **$0.051** |

---

## Dimension Breakdown

| Dimension | Score | Max | % |
|-----------|-------|-----|---|
| Root cause identification | 63 | 66 | **95.5%** |
| Correct file(s) | 43 | 44 | **97.7%** |
| Correct patch / code change | 50 | 66 | **75.8%** |
| **Overall** | **156** | **176** | **88.6%** |

---

## Token & Cost Breakdown

| # | Instance ID | Input | Cache Read | Output | **Cost** | Requests | Time (s) |
|---|-------------|-------|------------|--------|----------:|----------|----------|
| 1 | `12907` | 49,482 | 237,056 | 3,091 | **$0.069** | 13 | 259 |
| 2 | `13033` | 112,081 | 356,352 | 2,774 | **$0.123** | 18 | 277 |
| 3 | `13236` | 26,124 | 76,800 | 892 | **$0.029** | 4 | 1,307 |
| 4 | `13398` | 96,698 | 713,728 | 3,995 | **$0.144** | 22 | 289 |
| 5 | `13453` | 18,389 | 333,824 | 1,942 | **$0.048** | 15 | 1,307 |
| 6 | `13579` | 29,398 | 275,968 | 2,836 | **$0.056** | 15 | 272 |
| 7 | `13977` | 24,226 | 57,856 | 743 | **$0.026** | 5 | 1,306 |
| 8 | `14096` | 16,240 | 294,400 | 2,835 | **$0.047** | 16 | 1,306 |
| 9 | `14182` | 97,355 | 845,824 | 4,225 | **$0.155** | 28 | 338 |
| 10 | `14309` | 37,133 | 232,960 | 1,857 | **$0.054** | 11 | 1,306 |
| 11 | `14365` | 2,279 | 20,480 | 273 | **$0.004** | 2 | 1,306 |
| 12 | `14369` | 53,040 | 130,560 | 1,577 | **$0.057** | 9 | 46 |
| 13 | `14508` | 20,842 | 132,096 | 1,481 | **$0.032** | 10 | 49 |
| 14 | `14539` | 11,373 | 44,032 | 566 | **$0.014** | 4 | 17 |
| 15 | `14598` | 38,852 | 390,144 | 2,310 | **$0.069** | 16 | 40 |
| 16 | `14995` | 26,179 | 76,800 | 762 | **$0.029** | 6 | 24 |
| 17 | `7166` | 18,535 | 67,584 | 464 | **$0.021** | 4 | 10 |
| 18 | `7336` | 11,643 | 51,200 | 524 | **$0.015** | 4 | 14 |
| 19 | `7606` | 10,226 | 18,432 | 266 | **$0.010** | 2 | 4 |
| 20 | `7671` | 17,870 | 120,320 | 1,168 | **$0.028** | 9 | 42 |
| 21 | `8707` | 13,464 | 140,800 | 1,301 | **$0.027** | 9 | 21 |
| 22 | `8872`* | 28,046 | 524,288 | 35,351 | **$0.060** | 22 | 354 |
| | **TOTAL** | **758,475** | **5,141,504** | **71,233** | **$1.117** | **244** | **9,895** |

> **Average per task:** 450 s · $0.051
>
> *Task 22 (`8872`) token counts are from a qwen-model session (stdout routed to wrong directory by a path bug). Cost and output tokens are anomalously high; treat as indicative only.

---

## Per-Task Answer Comparison

### Task 1 — `12907` — ⚠️ Partial (5/8)

**Issue:** `separability_matrix` wrong for nested `CompoundModels`

| | GT | Mini |
|---|---|---|
| File | `separable.py` | `separable.py` |
| GT fix | `cright[-right.shape[0]:, -right.shape[1]:] = right` (one-line in `_cstack`) | Makes `_separable` recurse through `&`/`|` nodes; tightens `_cdot`/`_coord_matrix` handling |

**−1 RC:** Correctly identifies the nested CompoundModel axis-ordering bug but targets `_separable` and `_cdot`/`_coord_matrix` rather than the actual `= 1` hardcode in `_cstack`.  
**−2 Patch:** More nuanced approach than nano (mentions `|` nodes and `_cdot`) but still a different function and a more complex rewrite vs the one-line GT fix.

---

### Task 2 — `13033` — ✅ Near-perfect (7/8)

**Issue:** `TimeSeries` misleading exception on required column removal

| | GT | Mini |
|---|---|---|
| File | `core.py` | `core.py` |
| GT fix | `as_scalar_or_list_str()` helper; used in both error paths | Reports full required list; shows columns still present after failed mutation |

**−1 Patch:** Achieves the same user-visible behavior (full-list error message with current columns), structural difference only — no helper function extracted.

---

### Task 3 — `13236` — ✅ Exact (8/8)

**Issue:** Remove auto-transform of structured ndarray into `NdarrayMixin`

| | GT | Mini |
|---|---|---|
| File | `table.py` | `table.py` |
| GT fix | Remove 6-line auto-view block in `_convert_data_to_col` | Stops auto-converting structured `np.ndarray` to `NdarrayMixin`; stores as `Column`/`MaskedColumn` |

Description matches the GT behavior precisely. Mini correctly identifies the file, the behavior to remove, and mentions test updates in both `test_mixin.py` and `test_table.py` — consistent with a full GT-equivalent fix.

---

### Task 4 — `13398` — ❌ Fail (4/8)

**Issue:** Add ITRS ↔ AltAz/HADec topocentric transforms

| | GT | Mini |
|---|---|---|
| Files | 5 files + new `itrs_observed_transforms.py` | `intermediate_rotation_transforms.py` + `cirs_observed_transforms.py` |
| GT fix | New direct ITRS↔AltAz/HADec transform module; `location` attr; `__init__.py` import | Hardens ITRS→ITRS self-transform to preserve `location`; hardens CIRS↔observed promotes location |

**−1 RC:** Understands the location-preservation problem in the transform chain but scopes the fix to patching existing transforms rather than recognising that new direct ITRS↔observed transforms are required.  
**−1 Files:** Touches 2 related files but misses `itrs.py`, `__init__.py`, and the new `itrs_observed_transforms.py` module.  
**−2 Patch:** A workaround approach — hardening existing CIRS paths instead of implementing the GT's direct transform. Likely passes some tests but not the full suite.

---

### Task 5 — `13453` — ✅ Exact (8/8)

**Issue:** HTML writer ignores `formats` argument

| | GT | Mini |
|---|---|---|
| File | `html.py` | `html.py` |
| GT fix | `self.data.cols = cols` + `self.data._set_col_formats()` | "reusing the existing ASCII formatting path"; "set per-column formats before HTML values are rendered, matching the behavior already used by other ASCII writers" |

Description is a textbook paraphrase of the GT fix: hooking into `_set_col_formats()` which is the same infrastructure used by all other ASCII writers. Full marks.

---

### Task 6 — `13579` — ⚠️ Partial (6/8)

**Issue:** `SlicedLowLevelWCS.world_to_pixel_values` uses hardcoded `1.0` for dropped dimensions

| | GT | Mini |
|---|---|---|
| File | `sliced_wcs.py` | `sliced_wcs.py` |
| GT fix | Compute `sliced_out_world_coords` at pixel `[0,…,0]`; substitute for `1.` | "uncoupled sliced axes use the FITS reference pixel coordinate `1` when reconstructing the full world vector" |

**−2 Patch:** The mini keeps `1` as the reference value for dropped world axes (interpreting it as the FITS 1-indexed reference pixel) rather than computing the actual world coordinate at the slice origin. For non-trivial coupled WCS this will still produce wrong results — the `1.` placeholder is exactly the bug, not a correct reference point.

---

### Task 7 — `13977` — ✅ Near-perfect (7/8)

**Issue:** `Quantity.__array_ufunc__` should return `NotImplemented` for duck types

| | GT | Mini |
|---|---|---|
| File | `quantity.py` | `quantity.py` |
| GT fix | Wrap entire `__array_ufunc__` body in try/except; return `NotImplemented` | Returns `NotImplemented` when `converters_and_unit(...)` cannot handle a duck-typed operand |

**−1 Patch:** Wrapping only the `converters_and_unit` call is narrower than GT's full-body try/except. Handles the primary duck-type dispatch failure but may miss operands that pass unit conversion but fail later in `check_output` or `_result_as_quantity`.

---

### Task 8 — `14096` — ✅ Exact (8/8)

**Issue:** `SkyCoord` subclass property gives misleading `AttributeError`

| | GT | Mini |
|---|---|---|
| File | `sky_coordinate.py` | `sky_coordinate.py` |
| GT fix | `return self.__getattribute__(attr)` — 2 lines | "`__getattr__` no longer masks an `AttributeError` raised inside a subclass property, preserving the original missing-name message" |

Precisely describes the GT behavior. "Accessing `c.prop` now reports `random_attr` as missing" — exactly the issue example. Full marks.

---

### Task 9 — `14182` — ✅ Near-perfect (7/8)

**Issue:** RST writer needs `header_rows` support

| | GT | Mini |
|---|---|---|
| File | `rst.py` | `rst.py` |
| GT fix | Remove `start_line = 3`; full `__init__` with dynamic `sep_line_index`; add `read()` | "accepts and forwards `header_rows`, while preserving rst-specific defaults (`delimiter_pad=''`, `bookend=False`)" |

**−1 Patch:** Mini implements `header_rows` forwarding with correct RST defaults — better than nano's bare `**kwargs` pass-through. However, the description doesn't mention removing `start_line = 3` from `SimpleRSTData` or adding `read()`, suggesting the implementation is partial and may not handle reading RST tables with header rows.

---

### Task 10 — `14309` — ✅ Near-perfect (7/8)

**Issue:** `is_fits` IndexError with empty args

| | GT | Mini |
|---|---|---|
| File | `connect.py` | `connect.py` |
| GT fix | Early `return filepath.lower().endswith(...)` making `args[0]` unreachable | "safely returns `False` when `identify_format` passes no extra args" |

**−1 Patch:** Both fix the crash and are functionally equivalent. GT restructures the logic so `args[0]` is never accessed without guards; mini adds an explicit empty-args guard. Different structure, same result.

---

### Task 11 — `14365` — ✅ Near-perfect (7/8)

**Issue:** QDP reader fails on lowercase commands

| | GT | Mini |
|---|---|---|
| File | `qdp.py` | `qdp.py` |
| GT fix | `re.IGNORECASE` on `_line_type_re` **+** `v.upper() == "NO"` in data loop | "relying on the existing case-insensitive command detection and keeping the command keyword normalized when building err_specs" |

**−1 Patch:** "Keeping the command keyword normalized" suggests uppercasing the matched command — likely adds `re.IGNORECASE` and normalizes the command token. However the description doesn't clearly address the `v.upper() == "NO"` fix in the data-value parsing loop. Regression test covers `read serr 1 2` (command parsing) but does not mention lowercase `no` data values.

---

### Task 12 — `14369` — ✅ Near-perfect (7/8)

**Issue:** Incorrect units read from MRT (CDS format) files

| | GT | Mini |
|---|---|---|
| File | `cds.py` | `cds.py` |
| GT fix | Grammar rule fix in `_make_parser`; `division_of_units` recurses through itself not `combined_units` | "`division_of_units` now recurses through `division_of_units` rather than `combined_units`, which keeps the parser from reordering divisors during reduction" |

Mini describes the exact structural change the GT makes in the grammar. Correctly identifies `cds.py`, the division-associativity bug, and the minimal fix. Test cases (`10+3J/m/s/kpc2`, `10-7J/s/kpc2`) match the issue examples.

**−1 Patch:** The GT diff also normalises a documentation URL; mini's description is limited to the grammar fix. Minor structural difference — may miss the URL update in the docstring and possibly some edge-case grammar tokens — but the core fix is correct.

---

### Task 13 — `14508` — ✅ Exact (8/8)

**Issue:** `io.fits.Card` uses unnecessarily large float string representation

| | GT | Mini |
|---|---|---|
| File | `card.py` | `card.py` |
| GT fix | Replace `_format_float` with Python's `str(value)` shortest representation, capped at 20 chars | "uses Python's compact `str(value)` representation before enforcing the 20-character FITS limit" |

Exact description of the GT fix. Mini correctly cites `str(value)`, the 20-char FITS limit, the specific failing example (`0.009125`), and the test file. Full marks.

---

### Task 14 — `14539` — ✅ Exact (8/8)

**Issue:** `io.fits.FITSDiff` reports false differences for identical files with VLA `Q`-format columns

| | GT | Mini |
|---|---|---|
| File | `diff.py` | `diff.py` |
| GT fix | `"P" in col.format or "Q" in col.format` | "variable-length array table columns using `Q` are compared like `P` columns" |

One-line fix, exactly described. GT changes `"P" in col.format` → `"P" in col.format or "Q" in col.format`; mini states the same semantics. Full marks.

---

### Task 15 — `14598` — ⚠️ Partial (5/8)

**Issue:** Inconsistency in double single-quote (`''`) management in FITS Card

| | GT | Mini |
|---|---|---|
| File | `card.py` | `card.py` |
| GT fix | Anchor `_strg_comment_RE` with trailing `$`: `re.compile(f"({_strg})? *{_comm_field}?$")` | "stripping a continuation ampersand at the very end of a parsed string, after normalizing `''` to `'`" |

**−1 RC:** Mini identifies the `''` sequence issue but attributes it to CONTINUE-card ampersand stripping rather than the anchoring failure in `_strg_comment_RE`.  
**−2 Patch:** The GT fix is a single-character addition (`$`) to the regex. Mini's approach targets CONTINUE card parsing logic — a different part of the codebase — and would not resolve the anchoring bug that causes `''` to be consumed mid-string.

---

### Task 16 — `14995` — ✅ Exact (8/8)

**Issue:** NDDataRef mask propagation fails when one operand has no mask

| | GT | Mini |
|---|---|---|
| File | `ndarithmetic.py` | `ndarithmetic.py` |
| GT fix | `elif operand is None:` → `elif operand.mask is None:` | "preserves an existing mask when the other operand has no mask, instead of forwarding `None` into the mask combiner" |

Mini's description maps precisely to `operand.mask is None` — the exact condition the GT changes. Full marks.

---

### Task 17 — `7166` — ✅ Exact (8/8)

**Issue:** `InheritDocstrings` metaclass doesn't copy docstrings to properties

| | GT | Mini |
|---|---|---|
| File | `misc.py` | `misc.py` |
| GT fix | Check for `property` (data descriptor) in addition to plain functions when copying docstrings | "properly handling data descriptors, which includes properties, when copying docstrings from base classes" |

Mini correctly identifies that `inspect.isfunction` excludes `property` objects and that adding data-descriptor handling is the fix. Full marks.

---

### Task 18 — `7336` — ✅ Exact (8/8)

**Issue:** `quantity_input` decorator fails for constructors annotated `-> None`

| | GT | Mini |
|---|---|---|
| File | `decorators.py` | `decorators.py` |
| GT fix | `return_annotation not in (inspect.Signature.empty, None)` | "skip return-unit conversion when the wrapped function returns `None`" |

Exact match. Mini correctly identifies the off-by-one check (`empty` but not `None`) and the failing constructor pattern. Full marks.

---

### Task 19 — `7606` — ✅ Near-perfect (7/8)

**Issue:** `unit == None` raises `TypeError` for `UnrecognizedUnit`

| | GT | Mini |
|---|---|---|
| File | `core.py` | `core.py` |
| GT fix | Return `NotImplemented` (not `False`) in the except clause of `__eq__` | "return `False` when compared with `None` before attempting `Unit(other, parse_strict='silent')`" |

**−1 Patch:** GT changes the except-clause `return False` to `return NotImplemented`, letting Python's comparison protocol try the other side — better semantics for general operand types. Mini adds an early `None` guard returning `False`, which fixes the `unit == None` crash but differs from GT's semantics: `NotImplemented` is the idiomatic choice when the type cannot be compared, while `False` forecloses reflexive equality.

---

### Task 20 — `7671` — ✅ Exact (8/8)

**Issue:** `minversion` failures when version strings contain `dev`/`rc` suffixes

| | GT | Mini |
|---|---|---|
| File | `introspection.py` | `introspection.py` |
| GT fix | Add `import re`; strip non-numeric suffixes from version strings before `LooseVersion` comparison | "restore regex-based normalization before `LooseVersion` comparison... avoids the `LooseVersion` bug triggered by cases like `1.14.3` vs `1.14dev`" |

Exact match. Mini correctly identifies the regex normalization approach, adds `import re`, and cites the precise failing comparison. Full marks.

---

### Task 21 — `8707` — ✅ Near-perfect (7/8)

**Issue:** `Header.fromstring` does not accept Python 3 `bytes`

| | GT | Mini |
|---|---|---|
| File | `card.py` | `card.py` |
| GT fix | `image.decode('latin1')` in `Card.fromstring` | "decodes Python 3 `bytes` input as ASCII before padding" |

**−1 Patch:** Correct location and approach, but mini specifies ASCII decoding while the GT uses `latin1`. Latin-1 is a superset of ASCII and handles bytes 0x80–0xFF without raising — the GT's choice is intentional to avoid `UnicodeDecodeError` on non-ASCII FITS bytes. Decoding as strict ASCII would raise on any byte above 0x7F.

---

### Task 22 — `8872` — ✅ Exact (8/8)

**Issue:** `float16` quantities silently upcast to `float64`

| | GT | Mini |
|---|---|---|
| File | `quantity.py` | `quantity.py` |
| GT fix | Preserve any `np.inexact` dtype (float16/float32/float64/complex); only convert integer and non-Quantity objects to float | "treat any inexact dtype as preservable instead of only `float32`, which keeps `float16` quantities from being upcast to `float64`" |

Mini exactly describes the GT's `np.inexact` check generalisation — preserving all floating-point dtypes including `float16`. Full marks.

---

## Grade Distribution

| Grade | Count | Tasks |
|-------|-------|-------|
| ✅ Exact (8/8) | 10 | 3, 5, 8, 13, 14, 16, 17, 18, 20, 22 |
| ✅ Near-perfect (7/8) | 8 | 2, 7, 9, 10, 11, 12, 19, 21 |
| ⚠️ Partial (6/8) | 1 | 6 |
| ⚠️ Partial (5/8) | 2 | 1, 15 |
| ❌ Fail (≤4/8) | 1 | 4 |

**Exact + Near-perfect: 18/22 (81.8%)**

---

## Comparison: GPT-5.4 Mini vs GPT-5.4 Nano vs Claude Sonnet 4.6

*11-task comparison uses the original shared task set (tasks 1–11). 22-task figures are mini-only.*

| Metric | GPT-5.4 Nano (11) | GPT-5.4 Mini (11) | GPT-5.4 Mini (22) | Sonnet 4.6 (11) | Mini-11 vs Nano | Mini-11 vs Sonnet |
|--------|:-----------------:|:-----------------:|:-----------------:|:---------------:|:---------------:|:-----------------:|
| Overall score | 64/88 (72.7%) | 74/88 (84.1%) | 156/176 (88.6%) | 83/88 (94.3%) | **+11.4 pp** | −10.2 pp |
| Exact (8/8) | 0 | 3 | 10 | 8 | +3 | −5 |
| Near-perfect (7/8) | 5 | 5 | 8 | 1 | 0 | +4 |
| Partial (6/8) | 3 | 1 | 1 | 1 | −2 | 0 |
| Partial (5/8) | 1 | 1 | 2 | 1 | 0 | 0 |
| Fail (≤4/8) | 2 | 1 | 1 | 0 | **−1** | +1 |
| Root cause % | 87.9% | 93.9% | 95.5% | 100% | +6.0 pp | −6.1 pp |
| File ID % | 95.5% | 95.5% | 97.7% | 100% | 0 pp | −4.5 pp |
| Patch quality % | 42.4% | 66.7% | 75.8% | 81.8% | **+24.3 pp** | −15.1 pp |
| Avg cost/task | $0.051 | $0.069 | $0.051 | $0.538 | +35% | −87% |
| Total cost | $0.558 | $0.755 | $1.117 | $5.92 | +35% | −87% |
| Avg time/task | 1,841 s | 843 s | 450 s | 310 s | **−54%** | +45% |

**Key observations:**

- **Mini on 22 tasks reaches 88.6%**, up from 84.1% on the first 11. The additional 11 tasks skewed easier (8 of 11 are Exact), pulling overall patch quality up by 9.1 pp (66.7% → 75.8%) and closing the gap to Sonnet to just 6 pp.

- **Mini is a substantial step up from nano.** The +11.4 pp gain (72.7% → 84.1%) on the shared 11 tasks is driven entirely by patch quality (+24.3 pp): mini produces exact or near-exact patches on 8/11 tasks versus nano's 5/11. Nano scored zero Exact grades; mini scores 3 on the same tasks.

- **Shared failure: task 4 (`13398`, ITRS transforms).** Both nano (2/8) and mini (4/8) under-scope this task. Mini shows deeper understanding but still doesn't produce the full GT solution (new `itrs_observed_transforms.py` module).

- **Shared weakness: task 1 (`12907`).** Both models target `_separable()` rather than the one-line `_cstack` fix. The incorrect-function pattern is consistent across model sizes.

- **Task 6 (`13579`) regression vs nano.** Nano scored 7/8 (Near-perfect); mini scores 6/8 (Partial). The mini explicitly states it uses `1` as the FITS reference pixel — the exact value the GT replaces.

- **New task 15 (`14598`) partial.** Mini targets the wrong mechanism: CONTINUE-card ampersand stripping rather than the single-character `$` anchor fix in `_strg_comment_RE`. A pattern of correct-area-wrong-fix similar to task 1 and task 4.

- **Mini is 54% faster than nano** on the 11-task comparison. On 22 tasks the average drops further to 450 s, as the new tasks were simpler and did not hit wall-clock limits.

- **Average cost/task equalises at $0.051** across 22 tasks (same as nano on 11 tasks), because the new tasks were shorter and cheaper. Mini delivers meaningfully better patch quality at the same per-task cost.

- **Sonnet remains the quality ceiling** at 94.3%, but at 10.5× the per-task cost of mini across 22 tasks. For bulk eval use mini closes most of the gap at a fraction of the price.
