# GPT-5.4 Nano MCP on Kilo — SWE-Bench Evaluation Report

**Dataset:** `princeton-nlp/SWE-bench_Verified` — `astropy/astropy`
**Evaluated:** 22 tasks from `astropy_tasks.json`
**Date:** 2026-04-03
**Judge:** Claude Code (claude-sonnet-4-6)
**Ground truth source:** `results_swe_bench/astropy_tasks.json`
**Raw responses:** `results_swe_bench/auto_run_on_mcp_kilo_openai_gpt-5.4-nano/*/answer.json`
**Mode:** Kilo agent with ByteBell MCP knowledge graph (no local repo clone) · Orchestrator model: `qwen/qwen3.6-plus:free`

> **Note on model identity:** Despite the run directory name referencing `gpt-5.4-nano`, all OTel telemetry records `qwen/qwen3.6-plus:free` as the model making API calls. The ByteBell MCP orchestrator ran on Qwen; the kilo harness configuration named the target but the actual LLM in use was Qwen 3.6 Plus (free tier).

> **Note on MCP environment failure mode:** Several tasks received a "Cannot apply the minimal patch / apply_patch failed" response. In MCP mode the agent has no local checkout of the repository — only the knowledge graph is available. Any attempt to call `apply_patch` or write to the filesystem fails because the target files do not exist in the working directory. This is a structural limitation of the MCP approach as evaluated here and accounts for several outright failures.

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
| 1 | `astropy__astropy-12907` | 15m–1h | 0 | 0 | 0 | **0/8** | ❌ Fail | 66 | $0.027 |
| 2 | `astropy__astropy-13033` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 36 | $0.013 |
| 3 | `astropy__astropy-13236` | 15m–1h | 0 | 0 | 0 | **0/8** | ❌ Fail | 93 | $0.028 |
| 4 | `astropy__astropy-13398` | 1–4h | 1 | 0 | 0 | **1/8** | ❌ Fail | 59 | $0.038 |
| 5 | `astropy__astropy-13453` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 161 | $0.121 |
| 6 | `astropy__astropy-13579` | 1–4h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 46 | $0.022 |
| 7 | `astropy__astropy-13977` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 151 | $0.055 |
| 8 | `astropy__astropy-14096` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 24 | $0.006 |
| 9 | `astropy__astropy-14182` | 15m–1h | 3 | 2 | 1 | **6/8** | ⚠️ Partial | 64 | $0.036 |
| 10 | `astropy__astropy-14309` | <15m | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 74 | $0.049 |
| 11 | `astropy__astropy-14365` | 15m–1h | 3 | 2 | 1 | **6/8** | ⚠️ Partial | 74 | $0.026 |
| 12 | `astropy__astropy-14369` | 1–4h | 1 | 1 | 1 | **3/8** | ❌ Fail | 62 | $0.054 |
| 13 | `astropy__astropy-14508` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 126 | $0.069 |
| 14 | `astropy__astropy-14539` | 15m–1h | 3 | 2 | 3 | **8/8** | ✅ Exact | 150 | $0.078 |
| 15 | `astropy__astropy-14598` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 138 | $0.085 |
| 16 | `astropy__astropy-14995` | <15m | 3 | 2 | 3 | **8/8** | ✅ Exact | 13 | $0.007 |
| 17 | `astropy__astropy-7166` | <15m | 0 | 0 | 0 | **0/8** | ❌ Fail | 85 | $0.045 |
| 18 | `astropy__astropy-7336` | <15m | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 109 | $0.050 |
| 19 | `astropy__astropy-7606` | 15m–1h | 1 | 1 | 0 | **2/8** | ❌ Fail | 43 | $0.017 |
| 20 | `astropy__astropy-7671` | 15m–1h | 3 | 2 | 1 | **6/8** | ⚠️ Partial | 56 | $0.023 |
| 21 | `astropy__astropy-8707` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 51 | $0.022 |
| 22 | `astropy__astropy-8872` | 15m–1h | 3 | 2 | 2 | **7/8** | ✅ Near-perfect | 96 | $0.041 |
| | **TOTAL** | | **50/66** | **36/44** | **32/66** | **118/176** | **67.0%** | **1,779 s** | **$0.912** |
| | **AVERAGE** | | | | | **5.4/8** | | **81 s** | **$0.041** |

---

## Dimension Breakdown

| Dimension | Score | Max | % |
|-----------|-------|-----|---|
| Root cause identification | 50 | 66 | **75.8%** |
| Correct file(s) | 36 | 44 | **81.8%** |
| Correct patch / code change | 32 | 66 | **48.5%** |
| **Overall** | **118** | **176** | **67.0%** |

---

## Token & Cost Breakdown

| # | Instance ID | Input | Cache Read | Output | **Cost** | Requests | Time (s) |
|---|-------------|-------|------------|--------|----------:|----------|----------|
| 1 | `12907` | 62,400 | 562,176 | 2,659 | **$0.027** | 21 | 66 |
| 2 | `13033` | 36,147 | 207,360 | 1,065 | **$0.013** | 8 | 36 |
| 3 | `13236` | 64,004 | 609,280 | 2,355 | **$0.028** | 20 | 93 |
| 4 | `13398` | 114,898 | 636,928 | 1,945 | **$0.038** | 18 | 59 |
| 5 | `13453` | 330,825 | 2,398,720 | 5,858 | **$0.121** | 49 | 161 |
| 6 | `13579` | 46,531 | 481,792 | 2,122 | **$0.022** | 17 | 46 |
| 7 | `13977` | 66,914 | 1,767,936 | 4,914 | **$0.055** | 41 | 151 |
| 8 | `14096` | 5,385 | 91,648 | 2,155 | **$0.006** | 5 | 24 |
| 9 | `14182` | 82,513 | 814,080 | 2,691 | **$0.036** | 23 | 64 |
| 10 | `14309` | 150,892 | 779,264 | 2,954 | **$0.049** | 27 | 74 |
| 11 | `14365` | 58,373 | 511,488 | 3,495 | **$0.026** | 23 | 74 |
| 12 | `14369` | 179,988 | 710,144 | 2,925 | **$0.054** | 22 | 62 |
| 13 | `14508` | 180,648 | 1,352,704 | 4,484 | **$0.069** | 36 | 126 |
| 14 | `14539` | 225,672 | 1,290,240 | 5,810 | **$0.078** | 44 | 150 |
| 15 | `14598` | 229,244 | 1,639,424 | 5,029 | **$0.085** | 40 | 138 |
| 16 | `14995` | 15,253 | 116,736 | 1,029 | **$0.007** | 6 | 13 |
| 17 | `7166` | 131,877 | 763,392 | 3,052 | **$0.045** | 27 | 85 |
| 18 | `7336` | 120,170 | 1,017,856 | 4,798 | **$0.050** | 38 | 109 |
| 19 | `7606` | 50,535 | 244,736 | 1,344 | **$0.017** | 12 | 43 |
| 20 | `7671` | 52,164 | 416,256 | 3,419 | **$0.023** | 19 | 56 |
| 21 | `8707` | 53,394 | 356,864 | 3,104 | **$0.022** | 17 | 51 |
| 22 | `8872` | 83,490 | 944,640 | 4,028 | **$0.041** | 30 | 96 |
| | **TOTAL** | **2,341,317** | **17,713,664** | **71,235** | **$0.912** | **543** | **1,779** |

> **Average per task:** 81 s · $0.041

---

## Per-Task Answer Comparison

### Task 1 — `12907` — ❌ Fail (0/8)

**Issue:** `separability_matrix` wrong for nested `CompoundModels`

| | GT | MCP/Qwen |
|---|---|---|
| File | `separable.py` | — |
| GT fix | `cright[-right.shape[0]:, -right.shape[1]:] = right` (one line in `_cstack`) | Agent gave up — "working directory contains only kilo.json, astropy source tree not present" |

**−3 RC / −2 Files / −3 Patch:** Complete MCP environment failure. The agent retrieved relevant file content via the knowledge graph but couldn't apply any patch because the local filesystem has no repo checkout. The response explicitly says it cannot produce the required code change.

---

### Task 2 — `13033` — ✅ Near-perfect (7/8)

**Issue:** `TimeSeries` misleading exception on required column removal

| | GT | MCP/Qwen |
|---|---|---|
| File | `core.py` | `core.py` |
| GT fix | `as_scalar_or_list_str()` helper; used in both error paths to display `['time', 'a']` vs `['time', 'b']` | Update the `ValueError` to report the full `_required_columns` list; shows the corrected message format |

**−1 Patch:** GT extracts a `as_scalar_or_list_str()` helper for clean formatting in both paths. MCP correctly identifies the required format change but doesn't describe the helper function, implying a simpler inline approach.

---

### Task 3 — `13236` — ❌ Fail (0/8)

**Issue:** Remove auto-transform of structured ndarray into `NdarrayMixin`

| | GT | MCP/Qwen |
|---|---|---|
| File | `table.py` | — |
| GT fix | Remove 6-line auto-view block in `_convert_data_to_col` | "Failed to apply the minimal patch because the MCP apply_patch tool could not verify/read astropy/table/table.py" |

**−3 RC / −2 Files / −3 Patch:** Second MCP environment failure — same root cause as task 1. The agent couldn't read or write to the repo file.

---

### Task 4 — `13398` — ❌ Fail (1/8)

**Issue:** Add ITRS ↔ AltAz/HADec topocentric transforms

| | GT | MCP/Qwen |
|---|---|---|
| Files | 5 files + new `itrs_observed_transforms.py` | Could not retrieve enough context |
| GT fix | New transform module, `location` attr on ITRS, CIRS/TETE chain, `__init__.py` import | "Evidence retrieved shows existing ITRS frame lacks a location keyword; however, no further code context was retrieved" |

**−2 RC:** Correctly spotted the missing `location` attribute on ITRS, which is one of the GT changes. But failed to understand the full scope (new transform file, chain updates, `__init__.py`).  
**−2 Files:** No specific file identified.  
**−3 Patch:** No patch produced. The hardest task in the set — 5 files + a brand-new module required. MCP's knowledge graph lacked sufficient retrieval depth for this multi-file feature addition.

---

### Task 5 — `13453` — ✅ Near-perfect (7/8)

**Issue:** HTML writer ignores `formats` argument

| | GT | MCP/Qwen |
|---|---|---|
| File | `html.py` | `html.py` |
| GT fix | `self.data.cols = cols` + `self.data._set_col_formats()` after `_set_fill_values` | Call `self.data._set_col_formats()` after `_set_fill_values(cols)`; also apply `new_col.info.format` for multicolumn case |

**−1 Patch:** GT's two-line fix is minimal and clean. MCP also calls `_set_col_formats()` at the right place (better than raw nano which bypassed it entirely) but adds extra description about per-column `new_col` format assignment that complicates the picture slightly. Core approach matches GT.

---

### Task 6 — `13579` — ✅ Near-perfect (7/8)

**Issue:** `SlicedLowLevelWCS.world_to_pixel_values` uses hardcoded `1.0` for dropped dimensions

| | GT | MCP/Qwen |
|---|---|---|
| File | `sliced_wcs.py` | `sliced_wcs.py` (implied via class name) |
| GT fix | `sliced_out_world_coords = self._pixel_to_world_values_all(*[0]*len(self._pixel_keep))` at pixel origin | "replace the constant placeholder with world coordinates obtained by pixel_to_world at the sliced pixel start/representative values for dropped axes" |

**−1 Patch:** GT uses the pixel origin (all zeros) via `_pixel_to_world_values_all`. MCP describes the correct approach but says "sliced pixel start/representative values" which is vague — GT specifically uses zero for all kept pixels.

---

### Task 7 — `13977` — ✅ Near-perfect (7/8)

**Issue:** `Quantity.__array_ufunc__` should return `NotImplemented` for duck types

| | GT | MCP/Qwen |
|---|---|---|
| File | `quantity.py` | `quantity.py` |
| GT fix | Wrap entire `__array_ufunc__` body in try/except `(TypeError, ValueError)`; return `NotImplemented` if non-standard `__array_ufunc__` detected | (1) early guard for unrecognized input types; (2) wrap converter loop in try/except; return `NotImplemented` on failures |

**−1 Patch:** GT's approach is one clean try/except around the whole body with a check against `ignored_ufunc`. MCP describes two separate mechanisms (early guard + inner try/except) that achieve a similar outcome but don't match GT's unified structure.

---

### Task 8 — `14096` — ✅ Near-perfect (7/8)

**Issue:** `SkyCoord` subclass property gives misleading `AttributeError`

| | GT | MCP/Qwen |
|---|---|---|
| File | `sky_coordinate.py` | `sky_coordinate.py` |
| GT fix | Replace `raise AttributeError(...)` with `return self.__getattribute__(attr)` | Wrap descriptor access in try/except; if `AttributeError`, re-raise it directly |

**−1 Patch:** GT's `__getattribute__` is the cleanest and most idiomatic fix. MCP's try/except re-raise achieves the same observable behavior but is more verbose.

---

### Task 9 — `14182` — ⚠️ Partial (6/8)

**Issue:** RST writer needs `header_rows` support

| | GT | MCP/Qwen |
|---|---|---|
| File | `rst.py` | `rst.py` |
| GT fix | Removes `start_line = 3`; `__init__(header_rows=None)`; dynamic `write()` using `idx = len(self.header.header_rows)`; new `read()` | `__init__(self, header_rows=None): super().__init__(delimiter_pad=None, bookend=False, header_rows=header_rows)` |

**−2 Patch:** The MCP answer gets the `__init__` signature exactly right and it passes `header_rows` through to the parent — better than raw nano's `**kwargs` approach. However it misses three other required changes: removing `start_line = 3`, updating `write()` to use `idx` instead of `lines[1]`, and adding the `read()` method. Without those, the full test still fails.

---

### Task 10 — `14309` — ✅ Near-perfect (7/8)

**Issue:** `is_fits` IndexError with empty args

| | GT | MCP/Qwen |
|---|---|---|
| File | `connect.py` | `connect.py` |
| GT fix | Early `return` restructure makes `args[0]` unreachable when `filepath` is set | `if len(args) == 0: return False` guard before `args[0]` access |

**−1 Patch:** Both fix the bug. GT's restructuring is more elegant; MCP's guard is more explicit. Equivalent in behavior.

---

### Task 11 — `14365` — ⚠️ Partial (6/8)

**Issue:** QDP reader fails on lowercase commands

| | GT | MCP/Qwen |
|---|---|---|
| File | `qdp.py` | `qdp.py` |
| GT fix | `re.IGNORECASE` flag **+** `v.upper() == "NO"` in data value loop | Only `re.IGNORECASE` on command regex |

**−2 Patch:** MCP correctly identifies and applies `re.IGNORECASE` to the command parsing regex. But misses the second required fix: `v.upper() == "NO"` in the data-value loop, meaning lowercase `no` in data lines still fails. GT requires both changes for the test to pass.

---

### Task 12 — `14369` — ❌ Fail (3/8)

**Issue:** CDS unit parser right-recursive division (`a/b/c` → `a*c/b`)

| | GT | MCP/Qwen |
|---|---|---|
| Files | `cds.py` + `cds_parsetab.py` | `cds.py` |
| GT fix | Grammar rule swap: `unit_expression DIVISION combined_units` → `combined_units DIVISION unit_expression` (changes left/right associativity) + regenerated parsetab | Change `p[0] = p[1] / p[3]` → `p[0] = p[1] * (p[3] ** -1)` in `p_division_of_units` |

**−2 RC:** MCP identifies a division ordering/semantics issue but frames it as a computation problem (`/` vs `* inverse`) rather than the actual grammar associativity bug.  
**−1 Files:** Misses `cds_parsetab.py` — the regenerated parse table is required for the grammar change to take effect.  
**−2 Patch:** `p[1] * (p[3] ** -1)` is algebraically identical to `p[1] / p[3]` for a single division; it doesn't fix right-recursion for chained `/`. GT's grammar rule swap changes the *parse tree structure*, which is what's needed.

---

### Task 13 — `14508` — ✅ Near-perfect (7/8)

**Issue:** `_format_float` uses `.16G` expanding short floats

| | GT | MCP/Qwen |
|---|---|---|
| File | `card.py` | `card.py` |
| GT fix | `str(value).replace("e", "E")` — replaces entire old logic; Python's minimal repr naturally fits | `str(value)` instead of `.16G`, but says to also "keep existing logic for `.0` appending and exponent zero-padding" |

**−1 Patch:** Core insight (use `str(value)`) is exactly right. However MCP says to preserve the `.0`-appending and exponent zero-padding logic that GT actually removes — those are replaced by `str(value)` which handles them inherently. Minor structural divergence.

---

### Task 14 — `14539` — ✅ Exact (8/8)

**Issue:** FITS diff fails for VLA columns with Q format descriptor

| | GT | MCP/Qwen |
|---|---|---|
| File | `diff.py` | `diff.py` |
| GT fix | `elif "P" in col.format or "Q" in col.format:` | Identical condition |

The MCP answer nails the exact one-line change. Full marks.

---

### Task 15 — `14598` — ✅ Near-perfect (7/8)

**Issue:** FITS CONTINUE cards lose quotes from double un-escaping

| | GT | MCP/Qwen |
|---|---|---|
| Files | `card.py` (two changes) | `card.py` |
| GT fix | (1) Add `$` anchor to `_strg_comment_RE`; (2) remove `.replace("''", "'")` in `_split()` | Remove `.replace("''", "'")` in `_split()` so `''` is preserved |

**−1 Patch:** MCP correctly identifies and describes removing the `.replace("''", "'")` from `_split()` — exactly GT change #2. Misses the regex anchor (`$` appended to `_strg_comment_RE`) which is GT change #1. Better than raw nano (which proposed a wrong workaround), worse than a full fix.

---

### Task 16 — `14995` — ✅ Exact (8/8)

**Issue:** `_arithmetic_mask` has `operand is None` instead of `operand.mask is None`

| | GT | MCP/Qwen |
|---|---|---|
| File | `ndarithmetic.py` | `ndarithmetic.py` |
| GT fix | `elif operand.mask is None:` | Correctly identifies `operand.mask is None` vs `operand is None`; deepcopy the other operand's mask |

MCP correctly diagnoses the exact one-character bug and proposes the right fix. Full marks.

---

### Task 17 — `7166` — ❌ Fail (0/8)

**Issue:** `InheritDocstrings` doesn't work for properties

| | GT | MCP/Qwen |
|---|---|---|
| File | `misc.py` | — |
| GT fix | `inspect.isfunction(val) or inspect.isdatadescriptor(val)` | "Unable to access repository source at commit 26d147... indexed commits do not include the requested hash" |

**−3 RC / −2 Files / −3 Patch:** Third MCP environment failure — this time due to a commit hash not indexed in the ByteBell knowledge graph rather than a filesystem issue. The knowledge graph only indexes certain commits; the specific commit required for this task wasn't available.

---

### Task 18 — `7336` — ✅ Near-perfect (7/8)

**Issue:** `@quantity_input` fails with `-> None` annotation

| | GT | MCP/Qwen |
|---|---|---|
| File | `decorators.py` | `decorators.py` |
| GT fix | `not in (inspect.Signature.empty, None)` | Extend the check to include `None` (and also `NoneType`, `typing.NoReturn`) |

**−1 Patch:** Core fix (include `None` in the empty-annotation check) is exactly right. GT uses `(inspect.Signature.empty, None)` while MCP also adds `NoneType` and `typing.NoReturn` — overly broad but not harmful. Structural difference only.

---

### Task 19 — `7606` — ❌ Fail (2/8)

**Issue:** `Unit.__eq__` returns `False` instead of `NotImplemented`

| | GT | MCP/Qwen |
|---|---|---|
| Files | `core.py` — both `UnitBase.__eq__` and `UnrecognizedUnit.__eq__` | `core.py` — `UnrecognizedUnit.__eq__` only |
| GT fix | `return NotImplemented` in the except block of both classes | Guard `other is None` in `UnrecognizedUnit.__eq__`, return `False` |

**−2 RC:** Identifies the `UnrecognizedUnit.__eq__` issue but misses the primary `UnitBase.__eq__` fix. Returns `False` instead of `NotImplemented` — a semantic error. `NotImplemented` is required so Python can try the reflected operator.  
**−1 Files:** Only `UnrecognizedUnit`; misses `UnitBase.__eq__` in the same file.  
**−3 Patch:** Returning `False` for `None` is wrong semantically; GT returns `NotImplemented`. `UnitBase.__eq__` fix is entirely absent.

---

### Task 20 — `7671` — ⚠️ Partial (6/8)

**Issue:** `minversion` fails with `TypeError` on pre-release version strings

| | GT | MCP/Qwen |
|---|---|---|
| File | `introspection.py` | `introspection.py` |
| GT fix | PEP 440 regex to extract only the dotted-numeric prefix from `version`; compare with `LooseVersion` | "normalize version strings... convert trailing dev/rc tokens (e.g., '1.14dev' → '1.14.dev0')" |

**−2 Patch:** GT's approach extracts only the numeric prefix (`1.14`) using a PEP 440 regex and compares that against `have_version`. MCP proposes transforming `1.14dev` into `1.14.dev0` by inserting a dot — but `1.14.dev0` would still cause a `TypeError` in `LooseVersion` since `dev` is a non-numeric component. The correct fix is to strip pre-release entirely (to `1.14`), not transform it into another form that still contains non-numeric parts.

---

### Task 21 — `8707` — ✅ Near-perfect (7/8)

**Issue:** `Card.fromstring` / `Header.fromstring` don't accept bytes

| | GT | MCP/Qwen |
|---|---|---|
| Files | `card.py` + `header.py` | `card.py` + `header.py` |
| GT fix | `Card.fromstring`: decode as `latin-1`. `Header.fromstring`: extensive bytes-aware parsing throughout | Both files: `if isinstance(image, bytes): image = image.decode('ascii')` at entry |

**−1 Patch:** MCP correctly identifies both files (better than raw nano which missed `card.py`). Uses `ascii` codec vs GT's `latin-1` — FITS spec allows 8-bit chars, so `latin-1` is more correct. For `header.py` GT does a full bytes-aware parse rather than upfront decode; MCP's simplistic decode-at-entry approach may fail for byte-string separators and CONTINUE cards.

---

### Task 22 — `8872` — ✅ Near-perfect (7/8)

**Issue:** `np.float16` quantities upgraded to float64

| | GT | MCP/Qwen |
|---|---|---|
| File | `quantity.py` | `quantity.py` |
| GT fix | `value.dtype.kind in 'iu'` — cast only integer/unsigned; all floating types preserved | Add `np.can_cast(np.float16, value.dtype)` to both gate conditions |

**−1 Patch:** MCP's approach (adding float16 to the cast exemption) works for float16 specifically. GT's approach (`dtype.kind in 'iu'`) is more general and cleaner — it checks for integer/unsigned kinds rather than enumerating float types. Both fix the test case.

---

## Grade Distribution

| Grade | Count | Tasks |
|-------|-------|-------|
| ✅ Exact (8/8) | 2 | 14, 16 |
| ✅ Near-perfect (7/8) | 11 | 2, 5, 6, 7, 8, 10, 13, 15, 18, 21, 22 |
| ⚠️ Partial (6/8) | 3 | 9, 11, 20 |
| ❌ Fail (3/8) | 1 | 12 |
| ❌ Fail (2/8) | 1 | 19 |
| ❌ Fail (1/8) | 1 | 4 |
| ❌ Fail (0/8) | 3 | 1, 3, 17 |

**Exact + Near-perfect: 13/22 (59.1%)**

---

## Comparison: GPT-5.4 Nano MCP vs Raw (same 22 tasks)

| Metric | MCP (Qwen 3.6+) | Raw (Nano direct) | Delta |
|--------|-----------------|-------------------|-------|
| Overall score | 118/176 (67.0%) | 129/176 (73.3%) | **−6.3 pp** |
| Exact (8/8) | 2 | 4 | −2 |
| Near-perfect (7/8) | 11 | 7 | +4 |
| Partial (≤6/8) | 3 | 4 | −1 |
| Fail (≤4/8) | 6 | 7 | −1 |
| Root cause % | 75.8% | 87.9% | −12.1 pp |
| File ID % | 81.8% | 90.9% | −9.1 pp |
| Patch quality % | 48.5% | 47.0% | +1.5 pp |
| Avg time per task | **81 s** | 979 s | **−91.7%** |
| Avg cost per task | $0.041 | **$0.037** | +$0.004 |
| Total cost | $0.912 | **$0.808** | +$0.104 |
| Total time | **1,779 s** | 21,544 s | **−91.7%** |

**Key observations:**

- **3 complete failures (0/8) caused by MCP environment limitations.** Tasks 1 (`12907`), 3 (`13236`), and 17 (`7166`) produced zero information because either (a) the repo filesystem wasn't available for `apply_patch` or (b) the specific commit hash wasn't indexed in the ByteBell knowledge graph. These are structural failures, not reasoning failures. In a system where the agent could describe the fix without needing to apply it, these would likely score 5–7/8 each.

- **Dramatically faster.** MCP mode averaged 81 s/task vs 979 s for raw — a 12× speedup. No long timeouts (raw nano saw many 2684 s timeout cases). The MCP agent queries the knowledge graph rather than browsing the repo file-by-file.

- **Patch quality nearly identical** to raw nano (48.5% vs 47.0%). Among tasks where MCP produced an answer, the fix quality is comparable or slightly better than raw nano. MCP is not inferior at reasoning about fixes — it's inferior at *having access to the data* in edge cases.

- **MCP recovers well on near-perfects.** 11 near-perfect scores vs 7 for raw nano. Several tasks where raw nano struggled with approach (e.g., `14598` raw: 4/8, MCP: 7/8; `14182` raw: 4/8, MCP: 6/8) show MCP's knowledge graph retrieval providing better code context for understanding the required pattern.

- **Root cause regression is driven by the 3 zero-score failures.** If those 3 tasks are excluded from RC scoring, MCP's RC% on the remaining 19 tasks is 50/57 = 87.7% — matching raw nano's overall 87.9%. The environment failures artificially suppress the RC metric.

- **Cost slightly higher for MCP.** $0.912 vs $0.808 for raw. The MCP orchestrator (qwen3.6-plus) makes many more API requests per task (avg 24.7 vs 22.4 for raw nano) because it iterates over knowledge graph tool calls. The Qwen free-tier cost structure also differs from nano's.

- **The `14369` CDS grammar task remains hard for both modes.** Both raw nano and MCP nano misidentify it as a semantics problem rather than a grammar associativity issue. This suggests the root cause is a reasoning limitation, not an access limitation.

- **MCP-mode best use case:** When speed matters more than completeness and most tasks are self-contained bug fixes in a single well-indexed file. The 3 failures all involve either uncommitted/unindexed commits or filesystem write requirements — both solvable by better harness integration.
