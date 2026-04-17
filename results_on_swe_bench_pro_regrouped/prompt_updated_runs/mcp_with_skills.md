# Evaluation Report: mcp_with_skills (prompt_updated_runs / run_5)

**Run**: `auto_run_on_swe_pro_mcp_skills_claude-sonnet-4-6_run_5`  
**Rubric**: 4-dimension scoring (A=File Coverage 25, B=Patch Completeness 25, C=Test Coverage 25, D=Code Correctness 25), max 100  
**Repo**: internetarchive/openlibrary (all 10 tasks)  
**Condition**: MCP + Skills, prompt-updated run (single run, no pass@k selection)

---

## Score Summary

| # | Short ID | Task | A | B | C | D | **Total** |
|---|----------|------|---|---|---|---|-----------|
| 1 | 00bec1e7 | import_validator two-stage validation | 0.0 | 10.0 | 25.0 | 18.0 | **53.0** |
| 2 | 111347e9 | MARC catalog subjects refactor | 0.0 | 0.0 | 0.0 | 0.0 | **0.0** |
| 3 | 11838fad | MARC parse.py author fixes | 0.0 | 12.5 | 5.0 | 15.0 | **32.5** |
| 4 | 25858f9f | Solr utils.py extraction | 18.8 | 12.5 | 0.0 | 12.0 | **43.3** |
| 5 | 4a5d2a7d | wikidata get_statement_values | 0.0 | 6.3 | 0.0 | 10.0 | **16.3** |
| 6 | 5069b09e | db.py ALLOW_DELETE_ON_CONFLICT | 4.2 | 4.2 | 0.0 | 6.0 | **14.4** |
| 7 | 5c6c22f3 | importapi IA record helpers | 0.0 | 6.3 | 0.0 | 6.0 | **12.3** |
| 8 | 8a5a63af | monitoring OlAsyncIOScheduler rename | 0.0 | 5.0 | 0.0 | 6.0 | **11.0** |
| 9 | b4f7c185 | Solr update_key tuple return | 0.0 | 3.6 | 0.0 | 12.0 | **15.6** |
| 10 | dbbd9d53 | ListRecord.from_input seeds parsing | 12.5 | 16.7 | 25.0 | 18.0 | **72.2** |
| — | **Avg** | | **3.6** | **7.7** | **5.5** | **10.3** | **27.1** |

---

## Aggregate Metrics

| Metric | Value |
|--------|-------|
| Mean total score | 27.1 / 100 |
| Mean A (File Coverage) | 3.6 / 25 |
| Mean B (Patch Completeness) | 7.7 / 25 |
| Mean C (Test Coverage) | 5.5 / 25 |
| Mean D (Code Correctness) | 10.3 / 25 |
| Full patch rate (score ≥ 90) | 0% (0/10) |
| Partial patch rate (0 < score < 90) | 80% (8/10) |
| Zero-score rate | 10% (1/10) |
| Prose-only answers | 0% (0/10) |
| Pass@1 equivalent (C = 25) | 20% (2/10) |

---

## Per-Task Scoring Sheets

---

### Task 1 — `00bec1e7` | import_validator two-stage validation
**Score: 53.0/100** (A=0, B=10, C=25, D=18)

**Task**: Add `StrongIdentifierBookPlus` fallback validator + rename `Book` → `CompleteBookPlus` + variable renames in `code.py`.

**Dimension A — 0.0/25**: Produces a unified diff. Hits `import_validator.py` (1/2 gold files), misses `code.py`. Also adds `tests/test_import_validator.py` as an extra file. Formula: raw=12.5, deduction=min(1,1)×12.5=12.5, score=**0.0**. The extra test file completely offsets the file hit.

**Dimension B — 10.0/25**: Gold has ~5 hunks.
- `code.py` variable renames (`required_fields` → `minimum_complete_fields`): **Missing** (0)
- Import changes (adds `Final`, `model_validator`): **Partial** (1) — model adds `Optional`, `model_validator` but not `Final`, missing `STRONG_IDENTIFIERS` constant
- Rename `Book` → `CompleteBookPlus`: **Missing** (0)
- Add `StrongIdentifierBookPlus`: **Partial** (1) — model adds `DifferentiableBook` with identical logic, uses `Optional[...]` instead of `... | None`
- Rewrite `validate()` two-stage logic: **Present** (2) — try/except chain is functionally correct

Score: (0+1+0+1+2)/(5×2) × 25 = 4/10 × 25 = **10.0**

**Dimension C — 25.0/25**: Three FAIL_TO_PASS tests. Model's `DifferentiableBook` accepts records with `title + source_records + isbn_13/isbn_10/lccn`:
- `test_validate_strong_identifier_minimal`: `{"title": "Beowulf", "source_records": [...], "isbn_13": [...]}` → DifferentiableBook validates → **passes** ✓
- `test_validate_multiple_strong_identifiers[isbn_10]` and `[lccn]`: same pattern with additional identifier fields → **pass** ✓

Score: **25.0**

**Dimension D — 18.0/25**: Core two-stage logic fully correct. `DifferentiableBook.must_have_strong_identifier` validator logic identical to gold. Naming deductions: `DifferentiableBook` vs `StrongIdentifierBookPlus` (name not called by tests, no runtime impact), `Book` not renamed to `CompleteBookPlus`, `code.py` missed. Score: **18**

---

### Task 2 — `111347e9` | MARC catalog subjects refactor
**Score: 0.0/100** — cosmetic-only changes

**Task**: Fix 880 Alternate Graphic Representation pipeline: move `get_linkage` to `marc_base.py`, add `MarcFieldBase`, fix `marc_xml.py` `read_fields` decode-on-yield, remove double-`decode_field` in `get_subjects.py`, fix `parse.py` (range 595→590, remove stray `decode_field`, reorder `read_title`).

**Dimension A — 0.0/25**: Produces a large diff touching 4/5 gold files (get_subjects.py, marc_binary.py, marc_xml.py, parse.py). Misses marc_base.py. Also creates many extra test files (test_parse.py, test_get_subjects.py, test_marc_binary.py, test_marc_html.py) and ~50 `.json` test data files. Formula: raw=(4/5)×25=20, deduction=min(50+, 4)×5=20, score=**0.0**.

**Dimension B — 0.0/25**: All gold changes are absent; the model only makes cosmetic changes:
- `get_subjects.py`: Import reordering only — **no** `decode_field` removal (the critical fix). Missing (0)
- `marc_base.py`: Not touched — no `MarcFieldBase` class, no `get_linkage` method. Missing (0)
- `marc_binary.py`: Import reordering only — no substantive changes. Missing (0)
- `marc_xml.py`: Import reordering only — no `read_fields` decode-on-yield fix. Missing (0)
- `parse.py`: Adds deprecated lang_map entries (not in gold), no `range(500, 590)` fix, no `decode_field` removal. Missing (0)

Score: 0/10 × 25 = **0.0**

**Dimension C — 0.0/25**: Neither FAIL_TO_PASS test (`test_xml[nybc200247]`, `test_binary[880_arabic_french_many_linkages.mrc]`) can pass. The core 880 decode pipeline is untouched — `read_fields` in `marc_xml.py` still doesn't decode fields, `get_subjects.py` still double-decodes, `marc_base.py` still lacks `get_linkage`. Score: **0**

**Dimension D — 0.0/25**: Model made purely cosmetic changes (import reordering, lang_map additions for deprecated codes). None of these address the double-decode pipeline or 880 linkage mechanism. The root cause was not identified or fixed. Score: **0**

---

### Task 3 — `11838fad` | MARC parse.py author fixes
**Score: 32.5/100** (A=0, B=12.5, C=5, D=15)

**Task**: Multiple bugs in `parse.py` — asymmetric 7xx classification, 880 alternate-script linkage missing for 110/111, redundant `personal_name`, trailing period in role subfield `e`. 54 FAIL_TO_PASS tests.

**Dimension A — 0.0/25**: Produces a diff for `parse.py` (the only gold file = 1/1 hit), but also adds `tests/test_parse.py` as an extra file. Formula: raw=25, deduction=min(1,1)×25=25, score=**0.0**.

**Dimension B — 12.5/25**: Gold has ~4 distinct hunk groups in `parse.py`.
- `name_from_list` `strip_trailing_dot` parameter: **Partial** (1) — model achieves the role-strip effect inline in `read_author_person` (`_STRIP = ' /,;:[]'`) rather than adding a bool parameter to `name_from_list`
- `read_author_person` changes (personal_name dedup, fuller_name from q, 880 linkage, strip role): **Partial** (1) — model has personal_name dedup ✓, fuller_name from `q` ✓, role strip ✓, 880 linkage for tag 100 ✓. Misses the `return dict not None` sentinel change; 880 logic adds `alternate_names` whereas gold swaps `name`/`alternate_names`
- `read_authors` restructuring (100+700 combined, dedup by name): **Partial** (1) — model adds 880 linkage for 110/111 (partial coverage of gold), but doesn't do the full 100+700 combined reading
- `read_contributions` restructuring: **Partial** (1) — model does major rewrite (always appends to `authors`), structurally different from gold but addresses the asymmetric 7xx issue

Score: (1+1+1+1)/(4×2) × 25 = 4/8 × 25 = **12.5**

**Dimension C — 5.0/25**: 54 FAIL_TO_PASS tests covering full XML and binary record parsing. Model addresses multiple underlying bugs (personal_name dedup, role strip, 880 for 110/111) which would make a subset of tests pass. However, the restructured `read_contributions` (always adds 7xx to `authors`) changes behavior for many tests that previously passed, and the model's JSON expectation file edits are misaligned with the gold test_patch expectations. Estimated ~10% coverage. Score: **5.0**

**Dimension D — 15.0/25**: Correctly identifies 4 bugs with valid fixes for 3 of them (`personal_name` dedup, role strip, 880 linkage for 110/111, fuller_name from `q`). The `read_contributions` restructuring takes a fundamentally different (and simpler) approach than gold. Score: **15**

---

### Task 4 — `25858f9f` | Solr utils.py extraction
**Score: 43.3/100** (A=18.8, B=12.5, C=0, D=12)

**Task**: Extract shared Solr infrastructure from `update_work.py` into `openlibrary/solr/utils.py`: globals, `load_config`, `get/set_solr_base_url`, `get/set_solr_next`, `SolrUpdateState` dataclass, `solr_update()`, `solr_insert_documents()`. Fix import in `update_edition.py`. Update `index_subjects.py`.

**Dimension A — 18.8/25**: Produces a unified diff. Hits `utils.py` (new), `update_work.py`, `index_subjects.py` (3/4 gold files). Misses `update_edition.py`. No extra test files. Formula: 3/4 × 25 = **18.8**.

**Dimension B — 12.5/25**: Gold has 4 major file changes.
- `update_edition.py` (fix local import of `get_solr_next`): **Missing** (0)
- `update_work.py` (comprehensive removal of extracted code, rewire imports, fix `update_keys`, `AuthorSolrUpdater`): **Partial** (1) — model removes the globals and functions correctly, adds imports from utils, but doesn't import `SolrUpdateState` (since it created `SolrUpdateRequest` instead), potentially leaving remaining callers broken
- `utils.py` (new file with all extracted infrastructure): **Partial** (1) — model creates the file with all functions correctly (`load_config`, `get/set_solr_base_url`, `get/set_solr_next`, `solr_update` with full retry, `solr_insert_documents`, `str_to_key`), but names the dataclass `SolrUpdateRequest` instead of `SolrUpdateState` and omits the `keys` field
- `index_subjects.py` (updates import, moves `build_subject_doc`/`subject_name_to_key` locally): **Present** (2) — model moves these functions locally and updates imports correctly ✓

Score: (0+1+1+2)/(4×2) × 25 = 4/8 × 25 = **12.5**

**Dimension C — 0.0/25**: All 6 FAIL_TO_PASS tests do `from openlibrary.solr.utils import SolrUpdateState, solr_update`. Model exports `SolrUpdateRequest` → `ImportError` on all 6 tests. Score: **0**

**Dimension D — 12.0/25**: `utils.py` is structurally excellent — all 6 functions present with correct retry logic. Critical error: `SolrUpdateRequest` vs required `SolrUpdateState`, and missing `keys` field. `index_subjects.py` migration is perfect. Missing `update_edition.py` fix. Score: **12**

---

### Task 5 — `4a5d2a7d` | wikidata get_statement_values
**Score: 16.3/100** (A=0, B=6.3, C=0, D=10)

**Task**: Add `get_statement_values(property_id)` to `WikidataEntity`, add `SOCIAL_PROFILES` constant, `get_profiles_to_render()`, update `infobox.html`, update `messages.pot`.

**Dimension A — 0.0/25**: Produces a diff. Hits `wikidata.py` (1/3 gold files). Also adds `tests/core/test_wikidata.py` as an extra file. Formula: raw=8.3, deduction=min(1,1)×8.3=8.3, score=**0.0**.

**Dimension B — 6.3/25**: Gold has ~6 hunks.
- Fix `statements` type annotation: **Partial** (1) — model doesn't change the annotation
- Add `SOCIAL_PROFILES` constant: **Missing** (0)
- Add `get_statement_values()` (public): **Present** (2) — **improvement from run_3**: method is now public (`get_statement_values` not `_get_statement_values`)
- Add `get_profiles_to_render()`: **Missing** (0)
- `messages.pot` and `infobox.html`: **Missing** (0)

Score: (0+0+2+0+0)/(6×2) × 25 ≈ **6.3** (slight rounding adjustment from annotation partial)

**Dimension C — 0.0/25**: FAIL_TO_PASS test uses `entity.statements = {'P2038': [{'value': {'content': 'Chris-Wiggins'}}]}`. The model's implementation checks `value.get('type') == 'value'` — since the test data has no `'type'` key, `None == 'value'` is `False` → returns `[]` instead of `['Chris-Wiggins']`. **Same logic bug as previous run** despite fixing the public/private naming. Score: **0**

**Dimension D — 10.0/25**: Method name is now correct (public), matching the test call site — improvement. Root cause partially understood. But the extra `type == 'value'` guard introduces a regression that breaks the specific test. Score: **10**

---

### Task 6 — `5069b09e` | db.py ALLOW_DELETE_ON_CONFLICT
**Score: 14.4/100** (A=4.2, B=4.2, C=0, D=6)

Same result as mcp_skills_pass_at_3. The model adds only `t_update.rollback()` — the correct root-cause fix — but misses all the supporting infrastructure.

**Dimension A — 4.2/25**: Hits `db.py` only (1/6 gold files). No extra files. Score: **4.2**

**Dimension B — 4.2/25**: Gold has ~9 hunks across 6 files.
- `t_update.rollback()` before delete block: **Present** (2)
- `ALLOW_DELETE_ON_CONFLICT` check + `failed_deletes` in db.py: **Missing** (0) — model doesn't add these
- Dict return from `update_work_id`: **Missing** (0)
- booknotes.py, bookshelves.py, observations.py, ratings.py, admin/code.py class attributes: **Missing** (all 0)

Score: 2/18 × 25 ≈ **4.2**

**Dimension C — 0.0/25**: Test asserts `resp == {'rows_changed': 0, 'rows_deleted': 0, 'failed_deletes': 1}`. Without `Booknotes.ALLOW_DELETE_ON_CONFLICT = False` defined, `cls.ALLOW_DELETE_ON_CONFLICT` → `AttributeError`. Return type still tuple not dict. Score: **0**

**Dimension D — 6.0/25**: Correctly identifies unresolved savepoint as root cause. The single-line fix is correct. Score: **6**

---

### Task 7 — `5c6c22f3` | importapi IA record helpers
**Score: 12.3/100** (A=0, B=6.3, C=0, D=6)  *(improvement from 0 — was prose-only)*

**Task**: Add `get_isbn_10_and_13()` and `get_publisher_and_place()` to `upstream/utils.py`, refactor `get_ia_record()` in `importapi/code.py` to use them.

**Dimension A — 0.0/25**: Produces a diff. Hits `upstream/utils.py` (1/2 gold files). Misses `importapi/code.py`. Also adds `importapi/tests/test_code.py` as an extra file. Formula: raw=12.5, deduction=min(1,1)×12.5=12.5, score=**0.0**.

**Dimension B — 6.3/25**: Gold has 2 major file changes.
- `importapi/code.py` (add imports of new helpers, refactor `get_ia_record`): **Missing** (0)
- `upstream/utils.py` (add `get_isbn_10_and_13`, `get_publisher_and_place`): **Partial** (1) — model modifies the existing `get_location_and_publisher` to accept `str | list[str]`, which is conceptually related to `get_publisher_and_place` but is the wrong function and does not add `get_isbn_10_and_13`

Score: (0+1)/(2×2) × 25 = **6.3**

**Dimension C — 0.0/25**: 
- `test_get_publisher_and_place`: calls `utils.get_publisher_and_place(...)` — function doesn't exist in model's answer → `AttributeError`
- `test_get_isbn_10_and_13`: calls `utils.get_isbn_10_and_13(...)` — not added → `AttributeError`
- `test_get_ia_record` and variants: `code.py` unchanged, still returns old `publisher`/`isbn` format → assertion failures

All 8 FAIL_TO_PASS tests fail. Score: **0**

**Dimension D — 6.0/25**: Model extends `get_location_and_publisher` to handle list input — correct concept but wrong target function. Missing `get_isbn_10_and_13` entirely. `code.py` untouched. Score: **6**

---

### Task 8 — `8a5a63af` | monitoring OlAsyncIOScheduler rename
**Score: 11.0/100** (A=0, B=5, C=0, D=6)

Same result as mcp_skills_pass_at_3. Model still creates `OLBlockingScheduler(BlockingScheduler)` instead of `OlAsyncIOScheduler(AsyncIOScheduler)`.

**Dimension A — 0.0/25**: Hits `scripts/monitoring/utils.py`, `scripts/monitoring/monitor.py` (2/5 gold files). Creates 3 extra files (`__init__.py`, `tests/__init__.py`, `tests/test_utils_py.py`). Formula: raw=10, deduction=min(3,2)×5=10, score=**0.0**.

**Dimension B — 5.0/25**: 
- `utils.py` (rename class, change base, add `get_service_ip`, `[OL-MONITOR]` prefix): **Partial** (1) — has `bash_run`, `limit_server`, scheduling logic, but wrong class/base name, missing `get_service_ip`, missing `[OL-MONITOR]` prefix
- `monitor.py` (import rename, async main, `[OL-MONITOR]` prefix): **Partial** (1)
- `haproxy_monitor.py` (new 149-line file): **Missing** (0)
- `requirements.txt` (add requests): **Missing** (0)
- `compose.production.yaml` (network_mode: host): **Missing** (0)

Score: 2/10 × 25 = **5.0**

**Dimension C — 0.0/25**: Tests import `from scripts.monitoring.utils import OlAsyncIOScheduler, bash_run, limit_server`. Model exports `OLBlockingScheduler` → `ImportError` on both tests. Score: **0**

**Dimension D — 6.0/25**: `bash_run`, `limit_server`, host-matching logic structurally correct. Class is wrong type (`OLBlockingScheduler`/`BlockingScheduler` vs `OlAsyncIOScheduler`/`AsyncIOScheduler`). Missing `get_service_ip`, async main, `[OL-MONITOR]` prefix. Score: **6**

---

### Task 9 — `b4f7c185` | Solr update_key tuple return
**Score: 15.6/100** (A=0, B=3.6, C=0, D=12)  *(improvement from 0 — was prose-only)*

**Task**: `AuthorSolrUpdater.update_key` and `WorkSolrUpdater.update_key` return bare `SolrUpdateRequest` instead of `tuple[SolrUpdateRequest, list[str]]`.

**Dimension A — 0.0/25**: Produces a diff touching `openlibrary/solr/updater/author.py` and `openlibrary/solr/updater/work.py`. These files do **not** exist at this commit's gold file set. Gold modifies `update_work.py` and `utils.py`. file_hits=0. Score: **0.0**

**Dimension B — 3.6/25**: Gold has ~7 hunks in `update_work.py` + 1 in `utils.py`.
- `AuthorSolrUpdater.update_key` return fix: **Partial** (1) — logic is `return SolrUpdateRequest(adds=[doc]), []` which is correct, but applied to wrong file path
- `WorkSolrUpdater.update_key` return fix: **Partial** (1) — same situation
- All other update_work.py and utils.py changes: **Missing** (0)

Score: (1+1+0+0+0+0+0)/(8×2) × 25 = 2/14 × 25 ≈ **3.6**

**Dimension C — 0.0/25**: Model targets `updater/author.py` and `updater/work.py` which don't exist in this codebase version. The actual code in `update_work.py` remains unchanged. Tests that unpack `req, _ = await AuthorSolrUpdater().update_key(...)` still fail with `TypeError`. Score: **0**

**Dimension D — 12.0/25**: Correctly identifies the fix (`return ..., []`). Correct logic applied to wrong file paths. A significant improvement over prose-only (was 0). Score: **12**

---

### Task 10 — `dbbd9d53` | ListRecord.from_input seeds parsing
**Score: 72.2/100** (A=12.5, B=16.7, C=25, D=18)

Same as mcp_skills_pass_at_3.

**Task**: `ListRecord.from_input()` crashes when POST body uses `parse_qs` — seeds parsed as a string.

**Dimension A — 12.5/25**: Hits `lists.py` (1/2 gold files). Misses `utils.py`. No extra files. Score: **12.5**

**Dimension B — 16.7/25**: Gold has ~3 hunks.
- `from urllib.parse import parse_qs` import: **Present** (2)
- `from_input()` rewrite with DEFAULTS dict + `parse_qs` branch: **Present** (2)
- `utils.py` `setvalue()` "don't overwrite" removal: **Missing** (0)

Score: (2+2+0)/(3×2) × 25 = 4/6 × 25 = **16.7**

**Dimension C — 25.0/25**: FAIL_TO_PASS test uses `seeds--0--key=/books/OL1M&seeds--1--key=/books/OL2M` (nested format). Model's conditional `isinstance(DEFAULTS.get(k), list)` — since `seeds--0--key` is not in DEFAULTS, takes `v[0]` = `/books/OL1M`. After `utils.unflatten`, produces `[{'key': '/books/OL1M'}, {'key': '/books/OL2M'}]`. No key conflicts during unflatten (unique `--0--` and `--1--` prefixes), so `setvalue()` "don't overwrite" bug is never triggered. Test **passes**. Score: **25**

**Dimension D — 18.0/25**: Core logic correct. `isinstance(DEFAULTS.get(k), list)` is a slightly different but equivalent approach for the tested scenario. Missing `utils.py` change is benign for this specific test. Score: **18**

---

## Key Failure Patterns

### 1. Test file penalty wipes out file-coverage scores (Tasks 1, 3, 5, 7)
The prompt-updated runs show a consistent pattern: the model now adds test files alongside its implementation, but this triggers the extra-file penalty in Dimension A. In all cases where the model touched a test file alongside 1 gold file, the deduction exactly nullifies the raw score (A=0).

- **00bec1e7**: 1 hit (import_validator.py) + 1 extra (tests/test_import_validator.py) → A=0 (was 12.5)
- **11838fad**: 1 hit (parse.py) + 1 extra (tests/test_parse.py) → A=0
- **4a5d2a7d**: 1 hit (wikidata.py) + 1 extra (tests/core/test_wikidata.py) → A=0 (was 8.3)
- **5c6c22f3**: 1 hit (upstream/utils.py) + 1 extra (tests/test_code.py) → A=0

### 2. Same persistent logic bug in wikidata (Task 5)
The `get_statement_values` method now has the correct public name, but the model continues to add `if isinstance(value, dict) and value.get('type') == 'value':` — a guard that fails the gold test data, which uses `{'value': {'content': '...'}}` without a `'type'` key. This bug persists across multiple runs.

### 3. Purely cosmetic changes (Task 2)
Task 111347e9 regressed from 15.5 to 0. The model made only import-reordering and lang_map additions across all 4 touched files, completely missing the decode pipeline root cause. The score_A is also 0 due to a large number of extra test data json files.

### 4. Wrong file targeting (Task 9)
Task b4f7c185 moved from prose-only (0) to an actual diff but targets `updater/author.py` and `updater/work.py` — files that only exist in a later version of the repo. The actual code at this commit lives in `update_work.py`. The fix logic is correct but applied to non-existent files.

### 5. Major improvement in Solr extraction (Task 4)
Task 25858f9f went from 28.7 to 43.3. The model now creates a comprehensive `utils.py` with all functions correctly implemented, comprehensively cleans up `update_work.py`, and correctly migrates `index_subjects.py`. The only failure is the class name (`SolrUpdateRequest` vs `SolrUpdateState`) which blocks all 6 tests via ImportError.

---

## Comparison vs mcp_skills_pass_at_3

| Metric | mcp_skills_run_5 | mcp_skills_pass_at_3 | Δ |
|--------|-----------------|----------------------|---|
| Mean total | **27.1** | 26.1 | +1.0 |
| Mean A | 3.6 | 4.4 | **−0.8** |
| Mean B | 7.7 | 7.9 | −0.2 |
| Mean C | 5.5 | 5.0 | +0.5 |
| Mean D | 10.3 | 8.8 | **+1.5** |
| Prose-only | **0%** | 20% | **−20%** |
| Pass@1 equiv. | 20% | 20% | 0% |
| Zero-score | 10% | 20% | −10% |

### Per-task deltas

| Short ID | run_5 | pass_at_3 | Δ | Notes |
|----------|-------|-----------|---|-------|
| 00bec1e7 | 53.0 | 63.8 | **−10.8** | Extra test file wipes A; B improved slightly |
| 111347e9 | 0.0 | 15.5 | **−15.5** | Catastrophic regression: purely cosmetic changes |
| 11838fad | 32.5 | 34.8 | −2.3 | Actual diff vs prose-only, A wipes due to test file |
| 25858f9f | 43.3 | 28.7 | **+14.6** | Comprehensive Solr extraction; A=18.8 vs 6.2 |
| 4a5d2a7d | 16.3 | 20.6 | −4.3 | Public name fixed but same logic bug; A wipes |
| 5069b09e | 14.4 | 14.4 | 0.0 | Unchanged |
| 5c6c22f3 | 12.3 | 0.0 | **+12.3** | Was prose-only; now actual diff |
| 8a5a63af | 11.0 | 11.0 | 0.0 | Same wrong class name |
| b4f7c185 | 15.6 | 0.0 | **+15.6** | Was prose-only; now actual diff (wrong files) |
| dbbd9d53 | 72.2 | 72.2 | 0.0 | Stable top performer |

### Key takeaway
The prompt update eliminated prose-only responses (0% vs 20%) and improved D scores (+1.5), suggesting more confident code generation. However, the new tendency to write test files alongside implementations is a regression on Dimension A, and one task (111347e9) produced purely cosmetic changes that scored 0. The two C=25 passes remain stable (00bec1e7 and dbbd9d53). The primary bottleneck remains: correct analysis that either targets wrong files (b4f7c185), uses wrong class names (25858f9f, 8a5a63af), or adds a logic guard that breaks the specific test case (4a5d2a7d).
