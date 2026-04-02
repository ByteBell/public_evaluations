# Claude Sonnet 4.6 Raw — SWE-Bench Evaluation Report

**Dataset:** `princeton-nlp/SWE-bench_Verified` — `astropy/astropy`
**Evaluated:** 22 tasks from `astropy_tasks.json`
**Date:** 2026-04-02
**Judge:** Claude Code (claude-sonnet-4-6)
**Ground truth source:** `results_swe_bench/astropy_tasks.json`
**Raw responses:** `results_swe_bench/auto_run_on_claude_sonnet_4_6_raw/*/answer.json`
**Mode:** Claude Code direct repo access (no MCP knowledge graph)

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
| 1 | `astropy__astropy-12907` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 87 | $0.187 |
| 2 | `astropy__astropy-13033` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 372 | $0.601 |
| 3 | `astropy__astropy-13236` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 236 | $0.577 |
| 4 | `astropy__astropy-13398` | 1–4h | 3 | 2 | 3 | **8/8** | ✅ Exact | 881 | $1.849 |
| 5 | `astropy__astropy-13453` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 98 | $0.227 |
| 6 | `astropy__astropy-13579` | 1–4h | 3 | 2 | 3 | **8/8** | ✅ Exact | 204 | $0.374 |
| 7 | `astropy__astropy-13977` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 247 | $0.531 |
| 8 | `astropy__astropy-14096` | 15m–1h | 3 | 2 | 1 | **6/8** | ⚠️ Partial | 209 | $0.312 |
| 9 | `astropy__astropy-14182` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 371 | $0.654 |
| 10 | `astropy__astropy-14309` | <15m | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 130 | $0.156 |
| 11 | `astropy__astropy-14365` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 168 | $0.273 |
| 12 | `astropy__astropy-14369` | 1–4h | 3 | 2 | 3 | **8/8** | ✅ Exact | 836 | $1.300 |
| 13 | `astropy__astropy-14508` | 15m–1h | 3 | 2 | 1 | **6/8** | ⚠️ Partial | 141 | $0.262 |
| 14 | `astropy__astropy-14539` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 22 | $0.053 |
| 15 | `astropy__astropy-14598` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 1,637 | $2.381 |
| 16 | `astropy__astropy-14995` | <15m | 3 | 2 | 3 | **8/8** | ✅ Exact | 53 | $0.128 |
| 17 | `astropy__astropy-7166` | <15m | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 112 | $0.212 |
| 18 | `astropy__astropy-7336` | <15m | 3 | 2 | 3 | **8/8** | ✅ Exact | 55 | $0.104 |
| 19 | `astropy__astropy-7606` | 15m–1h | 3 | 2 | 0 | **5/8** | ⚠️ Partial | 100 | $0.183 |
| 20 | `astropy__astropy-7671` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 512 | $0.939 |
| 21 | `astropy__astropy-8707` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 261 | $0.371 |
| 22 | `astropy__astropy-8872` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 94 | $0.155 |
| | **TOTAL** | | **66/66** | **44/44** | **54/66** | **164/176** | **93.2%** | **6,826 s** | **$11.83** |
| | **AVERAGE** | | | | | **7.5/8** | | **310 s** | **$0.54** |

---

## Dimension Breakdown

| Dimension | Score | Max | % |
|-----------|-------|-----|---|
| Root cause identification | 66 | 66 | **100%** |
| Correct file(s) | 44 | 44 | **100%** |
| Correct patch / code change | 54 | 66 | **81.8%** |
| **Overall** | **164** | **176** | **93.2%** |

---

## Token & Cost Breakdown

| # | Instance ID | Input | Cache Write | Cache Read | Output | **Cost** | Score |
|---|-------------|-------|-------------|------------|--------|----------:|-------|
| 1 | `12907` | 65 | 44,825 | 697,679 | 6,060 | **$0.187** | 8/8 |
| 2 | `13033` | 18 | 25,798 | 382,530 | 25,946 | **$0.601** | 7/8 |
| 3 | `13236` | 88 | 78,084 | 1,139,669 | 15,071 | **$0.577** | 8/8 |
| 4 | `13398` | 166 | 159,299 | 2,669,208 | 63,505 | **$1.849** | 8/8 |
| 5 | `13453` | 15 | 19,368 | 266,801 | 4,920 | **$0.227** | 8/8 |
| 6 | `13579` | 13 | 25,491 | 260,575 | 13,366 | **$0.374** | 8/8 |
| 7 | `13977` | 99 | 76,161 | 1,075,115 | 13,919 | **$0.531** | 8/8 |
| 8 | `14096` | 256 | 18,437 | 209,684 | 11,929 | **$0.312** | 6/8 |
| 9 | `14182` | 64 | 86,326 | 1,158,926 | 23,440 | **$0.654** | 8/8 |
| 10 | `14309` | 13 | 11,684 | 173,360 | 4,008 | **$0.156** | 7/8 |
| 11 | `14365` | 48 | 38,957 | 408,408 | 6,154 | **$0.273** | 7/8 |
| 12 | `14369` | 108 | 109,520 | 1,253,653 | 55,933 | **$1.300** | 8/8 |
| 13 | `14508` | 14 | 21,764 | 201,687 | 8,011 | **$0.262** | 6/8 |
| 14 | `14539` | 6 | 5,419 | 58,178 | 1,013 | **$0.053** | 8/8 |
| 15 | `14598` | 110 | 139,268 | 2,288,723 | 107,959 | **$2.381** | 8/8 |
| 16 | `14995` | 11 | 10,862 | 151,354 | 2,756 | **$0.128** | 8/8 |
| 17 | `7166` | 47 | 27,806 | 318,129 | 7,678 | **$0.212** | 7/8 |
| 18 | `7336` | 252 | 9,201 | 125,118 | 2,049 | **$0.104** | 8/8 |
| 19 | `7606` | 256 | 13,160 | 192,462 | 5,004 | **$0.183** | 5/8 |
| 20 | `7671` | 26 | 43,071 | 778,825 | 36,225 | **$0.939** | 8/8 |
| 21 | `8707` | 121 | 38,223 | 1,030,693 | 12,614 | **$0.371** | 7/8 |
| 22 | `8872` | 10 | 11,904 | 122,970 | 4,883 | **$0.155** | 8/8 |
| | **TOTAL** | **1,806** | **1,015,628** | **14,963,747** | **432,443** | **$11.83** | **164/176** |

> **Average per task:** 310 s · $0.54

---

## Per-Model Token Usage

### Sonnet (claude-sonnet-4-6)

| # | Instance ID | Input | Cache Write | Cache Read | Output | **Cost** | Requests |
|---|-------------|-------|-------------|------------|--------|----------:|----------|
| 1 | `12907` | 5 | 2,519 | 48,416 | 1,447 | **$0.046** | 4 |
| 2 | `13033` | 18 | 25,798 | 382,530 | 25,946 | **$0.601** | 17 |
| 3 | `13236` | 23 | 31,447 | 492,749 | 11,237 | **$0.434** | 22 |
| 4 | `13398` | 35 | 79,726 | 1,635,926 | 53,860 | **$1.598** | 34 |
| 5 | `13453` | 15 | 19,368 | 266,801 | 4,920 | **$0.227** | 14 |
| 6 | `13579` | 13 | 25,491 | 260,575 | 13,366 | **$0.374** | 12 |
| 7 | `13977` | 17 | 35,620 | 382,484 | 9,294 | **$0.388** | 16 |
| 8 | `14096` | 256 | 18,437 | 209,684 | 11,929 | **$0.312** | 13 |
| 9 | `14182` | 12 | 34,272 | 242,781 | 17,861 | **$0.469** | 11 |
| 10 | `14309` | 13 | 11,684 | 173,360 | 4,008 | **$0.156** | 12 |
| 11 | `14365` | 15 | 22,245 | 255,770 | 4,563 | **$0.229** | 14 |
| 12 | `14369` | 22 | 65,484 | 768,673 | 44,080 | **$1.137** | 21 |
| 13 | `14508` | 14 | 21,764 | 201,687 | 8,011 | **$0.262** | 13 |
| 14 | `14539` | 6 | 5,419 | 58,178 | 1,013 | **$0.053** | 5 |
| 15 | `14598` | 24 | 88,686 | 1,078,633 | 100,026 | **$2.157** | 23 |
| 16 | `14995` | 11 | 10,862 | 151,354 | 2,756 | **$0.128** | 10 |
| 17 | `7166` | 7 | 13,889 | 85,345 | 5,480 | **$0.160** | 6 |
| 18 | `7336` | 252 | 9,201 | 125,118 | 2,049 | **$0.104** | 9 |
| 19 | `7606` | 256 | 13,160 | 192,462 | 5,004 | **$0.183** | 13 |
| 20 | `7671` | 26 | 43,071 | 778,825 | 36,225 | **$0.939** | 25 |
| 21 | `8707` | 14 | 16,858 | 222,493 | 7,075 | **$0.236** | 13 |
| 22 | `8872` | 10 | 11,904 | 122,970 | 4,883 | **$0.155** | 9 |
| | **TOTAL** | **1,064** | **606,905** | **8,136,814** | **375,034** | **$10.351** | **316** |

### Haiku (claude-haiku-4-5)

| # | Instance ID | Input | Cache Write | Cache Read | Output | **Cost** | Requests |
|---|-------------|-------|-------------|------------|--------|----------:|----------|
| 1 | `12907` | 60 | 42,306 | 649,263 | 4,613 | **$0.141** | 20 |
| 2 | `13033` | — | — | — | — | — | — |
| 3 | `13236` | 65 | 46,637 | 646,920 | 3,834 | **$0.142** | 21 |
| 4 | `13398` | 131 | 79,573 | 1,033,282 | 9,645 | **$0.251** | 30 |
| 5 | `13453` | — | — | — | — | — | — |
| 6 | `13579` | — | — | — | — | — | — |
| 7 | `13977` | 82 | 40,541 | 692,631 | 4,625 | **$0.143** | 24 |
| 8 | `14096` | — | — | — | — | — | — |
| 9 | `14182` | 52 | 52,054 | 916,145 | 5,579 | **$0.185** | 26 |
| 10 | `14309` | — | — | — | — | — | — |
| 11 | `14365` | 33 | 16,712 | 152,638 | 1,591 | **$0.044** | 6 |
| 12 | `14369` | 86 | 44,036 | 484,980 | 11,853 | **$0.163** | 16 |
| 13 | `14508` | — | — | — | — | — | — |
| 14 | `14539` | — | — | — | — | — | — |
| 15 | `14598` | 86 | 50,582 | 1,210,090 | 7,933 | **$0.224** | 33 |
| 16 | `14995` | — | — | — | — | — | — |
| 17 | `7166` | 40 | 13,917 | 232,784 | 2,198 | **$0.052** | 8 |
| 18 | `7336` | — | — | — | — | — | — |
| 19 | `7606` | — | — | — | — | — | — |
| 20 | `7671` | — | — | — | — | — | — |
| 21 | `8707` | 107 | 21,365 | 808,200 | 5,539 | **$0.135** | 26 |
| 22 | `8872` | — | — | — | — | — | — |
| | **TOTAL** | **742** | **407,723** | **6,826,933** | **57,410** | **$1.480** | **210** |

### Model Split Summary

| Metric | Sonnet | Haiku | Total | Sonnet % |
|--------|--------|-------|-------|----------|
| Input tokens | 1,064 | 742 | 1,806 | 58.9% |
| Cache Write tokens | 606,905 | 407,723 | 1,015,628 | 59.7% |
| Cache Read tokens | 8,136,814 | 6,826,933 | 14,963,747 | 54.4% |
| Output tokens | 375,034 | 57,410 | 432,443 | 86.7% |
| Cost (USD) | $10.351 | $1.480 | $11.830 | 87.5% |
| API requests | 316 | 210 | 526 | 60.1% |

> Sonnet dominates output generation (86.7%) and cost (87.5%), handling all reasoning and patch generation. Haiku is invoked as a triage/routing layer on ~half the tasks; on simpler tasks Sonnet runs alone from request 1.

---

## Per-Task Answer Comparison

### Task 1 — `12907` — ✅ Exact

**Issue:** `separability_matrix` wrong for nested `CompoundModels`

| | GT | Raw |
|---|---|---|
| File | `separable.py` | `separable.py` |
| Fix | `cright[...] = right` instead of `= 1` | Identical one-line diff |

---

### Task 2 — `13033` — ✅ Near-perfect

**Issue:** `TimeSeries` misleading exception on required column removal

| | GT | Raw |
|---|---|---|
| File | `core.py` | `core.py` |
| GT fix | Add `as_scalar_or_list_str()` helper; use it in both error paths | Branch on `len(required_columns) > 1`: two separate raise statements, no helper |

**-1:** Different structure, no helper extracted. Both raise the correct full-list message. GT is cleaner.

---

### Task 3 — `13236` — ✅ Exact

**Issue:** Remove auto-transform of structured ndarray into `NdarrayMixin`

| | GT | Raw |
|---|---|---|
| File | `table.py` | `table.py` |
| Fix | Remove 6-line auto-view block | Identical removal + parametrized test update |

---

### Task 4 — `13398` — ✅ Exact

**Issue:** Add ITRS ↔ AltAz/HADec topocentric transforms

| | GT | Raw |
|---|---|---|
| Files | 5 files + 1 new transform file | Same 5 files + new `itrs_observed_transforms.py` |
| Fix | ITRS `location` attr, new transform file, CIRS+TETE propagation | Full unified diff — all 6 files, identical to GT |

---

### Task 5 — `13453` — ✅ Exact

**Issue:** HTML writer ignores `formats` argument

| | GT | Raw |
|---|---|---|
| File | `html.py` | `html.py` |
| Fix | `self.data.cols = cols` + `self.data._set_col_formats()` | Identical |

---

### Task 6 — `13579` — ✅ Exact

**Issue:** `SlicedLowLevelWCS.world_to_pixel_values` uses hardcoded `1.0` for dropped dimensions

| | GT | Raw |
|---|---|---|
| File | `sliced_wcs.py` | `sliced_wcs.py` |
| Fix | Compute `pixel_to_world_values_all` at pixel origin for dropped dims | Identical logic with lazy `dropped_world_values` guard |

---

### Task 7 — `13977` — ✅ Exact

**Issue:** `Quantity.__array_ufunc__` should return `NotImplemented` for duck types

| | GT | Raw |
|---|---|---|
| File | `quantity.py` | `quantity.py` |
| Fix | Wrap entire `__array_ufunc__` body in try/except; check `__array_ufunc__` on all inputs/outputs | Identical: full body in `try/except (TypeError, ValueError, AttributeError)`; checks `inputs_and_outputs` against `ignored_ufunc`; returns `NotImplemented` or re-raises |

> This is the task where Opus raw and Sonnet MCP both scored 6/8 (only wrapping the input-conversion loop). Sonnet raw wraps the full body including `converters_and_unit`, `check_output`, and `_result_as_quantity` — matching the GT requirement exactly.

---

### Task 8 — `14096` — ⚠️ Partial

**Issue:** `SkyCoord` subclass property gives misleading `AttributeError`

| | GT | Raw |
|---|---|---|
| File | `sky_coordinate.py` | `sky_coordinate.py` |
| GT fix | `return self.__getattribute__(attr)` — 2 lines | MRO walk, find descriptor, call `desc.__get__(self, type(self))` — 9 lines; falls through to original misleading raise |

**-2:** The descriptor `__get__` is called and would raise the real error, but execution continues to the original `raise AttributeError(...)` below — the fix doesn't actually intercept it. GT's `__getattribute__` is simpler and correct.

---

### Task 9 — `14182` — ✅ Exact

**Issue:** RST writer needs `header_rows` support

| | GT | Raw |
|---|---|---|
| File | `rst.py` | `rst.py` |
| Fix | `__init__(header_rows=None)`, dynamic `sep_line_index`, add `read()` | Identical in every change |

---

### Task 10 — `14309` — ✅ Near-perfect

**Issue:** `is_fits` IndexError with empty args

| | GT | Raw |
|---|---|---|
| File | `connect.py` | `connect.py` |
| GT fix | `return filepath.lower().endswith(...)` — elif always returns | `elif len(args) > 0: return isinstance(...); return False` guard |

**-1:** Both fix the crash. GT restructures logic flow; Sonnet guards the access. Equivalent for all test cases.

---

### Task 11 — `14365` — ✅ Near-perfect

**Issue:** QDP reader fails on lowercase commands

| | GT | Raw |
|---|---|---|
| File | `qdp.py` | `qdp.py` |
| GT fix | `re.IGNORECASE` + `v.upper() == "NO"` in data parsing | Only `re.IGNORECASE` on the type regex |

**-1:** Missing the `v.upper() == "NO"` fix. Handles lowercase command keywords but not lowercase `NO` values in data lines.

---

### Task 12 — `14369` — ✅ Exact

**Issue:** CDS unit parser right-recursive division (`a/b/c` → `a*c/b`)

| | GT | Raw |
|---|---|---|
| File | `cds.py` + `cds_parsetab.py` | `cds.py` + `cds_parsetab.py` |
| Fix | Grammar rule swap + regenerated parsetab | Identical grammar change + fully regenerated parsetab tables |

---

### Task 13 — `14508` — ⚠️ Partial

**Issue:** `_format_float` uses `.16G` expanding short floats

| | GT | Raw |
|---|---|---|
| File | `card.py` | `card.py` |
| GT fix | `str(value).replace("e", "E")` — always uses Python's minimal repr | `str(value)` + uppercase `E`, then fallback to `f"{value:.16G}"` if `len > 20` |

**-2:** The `len > 20` fallback to `.16G` reintroduces the original precision-expansion bug for floats whose `str()` representation exceeds 20 characters. Python's `str(float)` already gives the shortest round-trip repr unconditionally — the fallback is incorrect.

---

### Task 14 — `14539` — ✅ Exact

**Issue:** FITS diff fails for VLA columns with Q format descriptor

| | GT | Raw |
|---|---|---|
| File | `diff.py` | `diff.py` |
| Fix | `elif "P" in col.format or "Q" in col.format:` | Identical |

---

### Task 15 — `14598` — ✅ Exact

**Issue:** FITS CONTINUE cards lose quotes from double un-escaping

| | GT | Raw |
|---|---|---|
| File | `card.py` | `card.py` |
| Fix | (1) Add `$` anchor to `_strg_comment_RE`; (2) remove `.replace("''", "'")` in `_split()` | Both changes identical |

---

### Task 16 — `14995` — ✅ Exact

**Issue:** `_arithmetic_mask` has `operand is None` instead of `operand.mask is None`

| | GT | Raw |
|---|---|---|
| File | `ndarithmetic.py` | `ndarithmetic.py` |
| Fix | `elif operand.mask is None:` | Identical |

---

### Task 17 — `7166` — ✅ Near-perfect

**Issue:** `InheritDocstrings` doesn't work for properties

| | GT | Raw |
|---|---|---|
| File | `misc.py` | `misc.py` |
| GT fix | `inspect.isfunction(val) or inspect.isdatadescriptor(val)` | `inspect.isfunction(val) or isinstance(val, property)` |

**-1:** `isinstance(val, property)` is narrower than `inspect.isdatadescriptor` — misses `cached_property` and C-extension descriptors. Both fix the standard `property` case.

---

### Task 18 — `7336` — ✅ Exact

**Issue:** `@quantity_input` fails with `-> None` annotation

| | GT | Raw |
|---|---|---|
| File | `decorators.py` | `decorators.py` |
| Fix | `not in (inspect.Signature.empty, None)` | `is not empty and is not None` — functionally identical |

---

### Task 19 — `7606` — ⚠️ Partial

**Issue:** `Unit.__eq__` returns `False` instead of `NotImplemented`

| | GT | Raw |
|---|---|---|
| Files | `core.py` — both `UnitBase.__eq__` and `UnrecognizedUnit.__eq__` | `core.py` — only `UnrecognizedUnit.__eq__` |
| GT fix | `return NotImplemented` in both classes | `if other is None: return False` + `try/except TypeError: return False` in `UnrecognizedUnit.__eq__` only |

**-3:** (1) Returns `False` instead of `NotImplemented` — semantically wrong, breaks Python's reflected-operator fallback protocol. (2) Misses `UnitBase.__eq__` entirely, which is the primary class used in practice.

---

### Task 20 — `7671` — ✅ Exact

**Issue:** `minversion` fails with `TypeError` when version strings contain pre-release suffixes

| | GT | Raw |
|---|---|---|
| File | `introspection.py` | `introspection.py` |
| GT fix | PEP440 regex to strip pre-release from `version` only | Same regex, strips `version` only; wraps with `try/except TypeError` fallback |

---

### Task 21 — `8707` — ✅ Near-perfect

**Issue:** `Card.fromstring` / `Header.fromstring` don't accept bytes

| | GT | Raw |
|---|---|---|
| Files | `card.py`, `header.py` | `card.py`, `header.py` |
| GT fix | `Card.fromstring`: decode latin-1. `Header.fromstring`: bytes-aware refactor | `Card.fromstring`: `decode('ascii')`. `Header.fromstring`: prepend `decode_ascii(data)` |

**-1:** Uses `ascii` codec instead of GT's `latin-1`. FITS allows 8-bit characters per spec; `latin-1` is technically correct. Both work for standard ASCII FITS headers.

---

### Task 22 — `8872` — ✅ Exact

**Issue:** `np.float16` quantities upgraded to float64

| | GT | Raw |
|---|---|---|
| File | `quantity.py` | `quantity.py` |
| GT fix | `value.dtype.kind in 'iu'` (cast only integers/unsigned) | `np.issubdtype(value.dtype, np.inexact)` (preserve all floating-point types) — functionally identical |

---

## Grade Distribution

| Grade | Count | Tasks |
|-------|-------|-------|
| ✅ Exact (8/8) | 14 | 1, 3, 4, 5, 6, 7, 9, 12, 14, 15, 16, 18, 20, 22 |
| ✅ Near-perfect (7/8) | 5 | 2, 10, 11, 17, 21 |
| ⚠️ Partial (6/8) | 2 | 8, 13 |
| ⚠️ Partial (5/8) | 1 | 19 |
| ❌ Fail (≤4/8) | 0 | — |

**Exact + Near-perfect: 19/22 (86.4%)**

---

## Comparison: Sonnet 4.6 Raw vs Opus 4.6 v3-Raw

| Metric | Opus v3-Raw | Sonnet Raw | Delta |
|--------|-------------|------------|-------|
| Overall score | 162/176 (92.0%) | 164/176 (93.2%) | **+1.2 pp** |
| Exact (8/8) | 14 | 14 | 0 |
| Near-perfect (7/8) | 5 | 5 | 0 |
| Partial (6/8) | 2 | 2 | 0 |
| Partial (5/8) | 0 | 1 | +1 |
| Fail (≤4/8) | 1 | **0** | **−1** |
| Root cause % | 97.0% | **100%** | +3.0 pp |
| Patch % | 81.8% | 81.8% | 0 |
| Avg time per task | 251 s | 310 s | +59 s |
| Avg cost per task | $0.734 | $0.538 | **−27%** |
| Total cost | $16.16 | $11.83 | **−27%** |

**Key observations:**

- **Sonnet raw scores 1.2 pp higher overall** (164 vs 162). The gain is entirely task 7 (`13977`): Sonnet wraps the full `__array_ufunc__` body correctly (8/8 Exact), while Opus scored 6/8 (wrapped only the input-conversion loop). Sonnet MCP also scored 6/8 on this task — the correct full-body fix appears to require direct repo access and sufficient exploration budget.
- **Sonnet eliminates outright failures.** Opus had one 3/8 fail on task 19 (`7606`, no patch proposed). Sonnet scores 5/8 — wrong return value and missing class, but at least proposes a working partial fix.
- **Root cause is perfect at 100%.** Opus missed the root cause on task 19 (1/3 RC). Sonnet correctly diagnoses the issue on every task, even the ones where the patch is incomplete.
- **Patch quality is identical at 81.8%** (54/66). The tasks where they lose points differ slightly (Sonnet aces task 7; Opus aces task 20 at same score) but the aggregate is the same.
- **Sonnet is 27% cheaper per task** ($0.538 vs $0.734). Sonnet generates substantially fewer output tokens on reasoning-heavy tasks and has a lower per-token rate than Opus.
- **Sonnet is 23% slower** (310 s vs 251 s avg). Task 15 (`14598`) dominates at 1,637 s and 107,959 output tokens — Sonnet produced an unusually verbose answer on that task.
- **Shared weakness: task 8 (`14096`)** — both Opus and Sonnet use an over-engineered MRO-walk approach instead of GT's 2-line `__getattribute__` fix. Consistent failure of over-engineering on a problem that looks more complex than it is.
- **Shared weakness: task 19 (`7606`)** — both miss `UnitBase.__eq__`. The issue description mentions `UnrecognizedUnit` prominently, misdirecting both models away from the parent class fix.
