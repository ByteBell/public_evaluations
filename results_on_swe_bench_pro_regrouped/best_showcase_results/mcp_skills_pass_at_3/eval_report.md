# Evaluation Report: mcp_skills_pass_at_3

**Rubric**: 4-dimension scoring (A=File Coverage 25, B=Patch Completeness 25, C=Test Coverage 25, D=Code Correctness 25), max 100  
**Repo**: internetarchive/openlibrary (all 10 tasks)  
**Condition**: MCP + Skills, Pass@3 (best-of-3 run selected)

---

## Score Summary

| # | Short ID | Task | A | B | C | D | **Total** |
|---|----------|------|---|---|---|---|-----------|
| 1 | 00bec1e7 | import_validator two-stage validation | 12.5 | 8.3 | 25.0 | 18.0 | **63.8** |
| 2 | 111347e9 | MARC catalog subjects refactor | 0.0 | 7.5 | 0.0 | 8.0 | **15.5** |
| 3 | 11838fad | MARC parse.py author fixes | 0.0 | 18.8 | 0.0 | 16.0 | **34.8** |
| 4 | 25858f9f | Solr utils.py extraction | 6.2 | 12.5 | 0.0 | 10.0 | **28.7** |
| 5 | 4a5d2a7d | wikidata get_statement_values | 8.3 | 6.3 | 0.0 | 6.0 | **20.6** |
| 6 | 5069b09e | db.py ALLOW_DELETE_ON_CONFLICT | 4.2 | 4.2 | 0.0 | 6.0 | **14.4** |
| 7 | 5c6c22f3 | importapi IA record helpers | 0.0 | 0.0 | 0.0 | 0.0 | **0** |
| 8 | 8a5a63af | monitoring OlAsyncIOScheduler rename | 0.0 | 5.0 | 0.0 | 6.0 | **11.0** |
| 9 | b4f7c185 | Solr update_key tuple return | 0.0 | 0.0 | 0.0 | 0.0 | **0** |
| 10 | dbbd9d53 | ListRecord.from_input seeds parsing | 12.5 | 16.7 | 25.0 | 18.0 | **72.2** |
| — | **Avg** | | **4.4** | **7.9** | **5.0** | **8.8** | **26.1** |

---

## Aggregate Metrics

| Metric | Value |
|--------|-------|
| Mean total score | 26.1 / 100 |
| Mean A (File Coverage) | 4.4 / 25 |
| Mean B (Patch Completeness) | 7.9 / 25 |
| Mean C (Test Coverage) | 5.0 / 25 |
| Mean D (Code Correctness) | 8.8 / 25 |
| Full patch rate (score ≥ 90) | 0% (0/10) |
| Partial patch rate (0 < score < 90) | 80% (8/10) |
| Zero-score rate | 20% (2/10) |
| Prose-only answers | 20% (2/10) |
| Pass@1 equivalent (C = 25) | 20% (2/10) |

---

## Per-Task Scoring Sheets

---

### Task 1 — `00bec1e7` | import_validator two-stage validation
**Score: 63.8/100** (A=12.5, B=8.3, C=25, D=18)

**Task**: `import_validator.validate()` rejects records that have a strong identifier (ISBN-10/13, LCCN) but lack authors/publishers/publish_date. Add a `StrongIdentifierBookPlus` model as a fallback validator alongside the renamed `CompleteBookPlus`.

**Dimension A — 12.5/25**: Produces a unified diff. Hits `import_validator.py` (1/2 gold files). Misses `code.py` which renames `required_fields` → `minimum_complete_fields`. Formula: 1/2 × 25 = 12.5.

**Dimension B — 8.3/25**: Gold has ~6 hunks (5 in import_validator.py + 1 in code.py).
- Imports hunk (adds `model_validator`): **Partial** (also adds `Optional`, misses `Final` and `STRONG_IDENTIFIERS` constant)
- Rename `Book` → `CompleteBookPlus`: **Missing**
- Add `StrongIdentifierBookPlus`: **Partial** (model adds `BookDifferentiable` — same structure, different name, uses `Optional[...]` instead of `... | None`)
- Rewrite `validate()` with two-stage logic: **Present**
- code.py variable renames: **Missing**
Score: (1+0+1+2+0) / (6×2) × 25 = 4/12 × 25 = **8.3**

**Dimension C — 25/25**: Three FAIL_TO_PASS tests: `test_validate_strong_identifier_minimal`, `test_validate_multiple_strong_identifiers[isbn_10]`, `test_validate_multiple_strong_identifiers[lccn]`. The model's `BookDifferentiable` has the same required fields as `StrongIdentifierBookPlus` (`title`, `source_records` + at least one of isbn_10/isbn_13/lccn). Two-stage logic in `validate()` correctly falls back to `BookDifferentiable` when `Book` fails. All 3 tests **pass**. Score: **25**

**Dimension D — 18/25**: Core logic fully correct. Two-stage try/except structure is sound. Naming deductions: `Book` not renamed to `CompleteBookPlus` (existing class unchanged), `BookDifferentiable` vs `StrongIdentifierBookPlus`. Functional behavior is correct despite name differences. Score: **18**

---

### Task 2 — `111347e9` | MARC catalog subjects refactor
**Score: 15.5/100** (A=0, B=7.5, C=0, D=8) *(re-evaluated: answer updated from prose-only)*

**Task**: MARC 880 (Alternate Graphic Representation) fields not processed. Needs: move `get_linkage` from `marc_binary.py` → `marc_base.py`, add `MarcFieldBase` base class, fix `marc_xml.py`'s `read_fields` to yield decoded fields (not raw elements), remove double-`decode_field` calls in `get_subjects.py`, and fix `parse.py` (range 595→590, remove stray `decode_field`, reorder `read_title`, fix list append in `update_edition`).

**Dimension A — 0/25**: Model produces code blocks with diff syntax but they target no gold files and no formal `+++ b/filename.py` diff headers are produced. `model_file_count = 0`, `file_hits = []`. Score: **0**

**Dimension B — 7.5/25**: Gold has 5 distinct file hunks.
- `get_subjects.py` (pass `field` directly, remove ~15 `decode_field` calls): **Missing** (0) — model never mentions this file
- `marc_base.py` (add `MarcFieldBase`, refactor `get_fields`, add `get_linkage`): **Partial** (1) — model proposes `get_linkage` in `MarcBase` and names `MarcFieldBase`
- `marc_binary.py` (inherit `MarcFieldBase`, remove `get_linkage`, type hints): **Partial** (1) — model mentions type annotations and `BinaryDataField` but doesn't detail the inheritance or removal
- `marc_xml.py` (`DataField` inherits `MarcFieldBase`, fix `read_fields` to yield decoded fields): **Partial** (1) — model mentions inheritance but misses the critical `read_fields` decode-on-yield fix
- `parse.py` (range fix, remove `decode_field`, reorder `read_title`, list append): **Missing** (0) — model proposes different `parse.py` changes (alternate title handling via `get_linkage` in `read_title`)
Score: (0+1+1+1+0) / (5×2) × 25 = 3/10 × 25 = **7.5**

**Dimension C — 0/25**: No actual code changes applied (`model_file_count = 0`). Neither FAIL_TO_PASS test (`test_xml[nybc200247]`, `test_binary[880_arabic_french_many_linkages]`) can run. Score: **0**

**Dimension D — 8/25**: Model correctly identifies `MarcBase` as the home for `get_linkage` (matches gold). Correctly names `MarcFieldBase`. Proposes `link.replace('880', original)` logic that matches the gold implementation. However, the root fix (removing double-decode in `get_subjects.py` + fixing `read_fields` to decode in `marc_xml.py`) is missed entirely; model instead adds 880 linkage resolution to high-level parse functions (`read_title`, `read_author_person`, `read_publisher`) — a conceptually different approach. Score: **8**

---

### Task 3 — `11838fad` | MARC parse.py author fixes
**Score: 34.8/100** (A=0, B=18.8, C=0, D=16) *(re-evaluated: answer updated)*

**Task**: Multiple bugs in `openlibrary/catalog/marc/parse.py` — asymmetric 7xx classification, 880 alternate-script linkage missing for 110/111, redundant `personal_name` when equal to `name`, trailing period stripped from role subfield `e`. 54 FAIL_TO_PASS tests.

**Dimension A — 0/25**: Model produces Python code blocks but no git diff format. `is_prose_only = False`, `model_file_count = 0`. Score: **0**

**Dimension B — 18.8/25**: Gold has ~4 distinct parse.py hunk groups.
- `name_from_list` `strip_trailing_dot` parameter: **Present** (2) — model's Bug 4 exactly matches gold's approach
- `read_author_person` changes (return dict not None, `personal_name` dedup, `fuller_name` from `q`, 880 name-swap logic, `strip_trailing_dot` for role): **Partial** (1) — model covers personal_name dedup, strip_trailing_dot for role, 880 linkage; misses `fuller_name` from `q`; 880 logic differs (model adds `alternate_names`, gold swaps `name`/`alternate_names`)
- `read_authors` major refactoring (reads 100+700 together, dedup by name): **Partial** (1) — model focuses on `read_contributions` rewrite; gold's bigger structural change is in `read_authors`
- `read_contributions` restructuring: **Present** (2) — model's Bug 1 rewrites `read_contributions` to always emit structured dicts, matching gold intent
Score: (2+1+1+2) / (4×2) × 25 = 6/8 × 25 = **18.8**

**Dimension C — 0/25**: 54 tests, no actual diff applied. Score: **0**

**Dimension D — 16/25**: Model correctly identifies all 4 bugs with matching approaches for 3 of them (`strip_trailing_dot` for role, `personal_name` dedup, `read_contributions` rewrite, 880 linkage for 110/111). Misses `fuller_name` from subfield `q`. 880 name-swap logic differs from gold. Score: **16**

---

### Task 4 — `25858f9f` | Solr utils.py extraction
**Score: 28.7/100** (A=6.2, B=12.5, C=0, D=10) *(re-evaluated: answer updated from prose-only)*

**Task**: Extract shared Solr infrastructure out of the monolithic `update_work.py` into a new `openlibrary/solr/utils.py`: globals `solr_base_url`/`solr_next`, `load_config`, `get/set_solr_base_url`, `get/set_solr_next`, `SolrUpdateState` dataclass, `solr_update()`, `solr_insert_documents()`. Remove them from `update_work.py`. Fix import in `update_edition.py`. Update `index_subjects.py`.

**Dimension A — 6.2/25**: Produces a unified diff. Hits `index_subjects.py` (1/4 gold files). Misses `update_edition.py`, `update_work.py`, `utils.py` (new file). Formula: 1/4 × 25 = **6.2**

**Dimension B — 12.5/25**: Gold has 4 major file changes.
- `update_edition.py` (move `get_solr_next` import): **Missing** (0) — not mentioned
- `update_work.py` (remove all extracted code, add import from utils): **Partial** (1) — model describes the logic but doesn't detail the full removal
- `utils.py` (new file with all extracted code): **Partial** (1) — model creates this file with correct functions/globals but names the class `SolrUpdateRequest` instead of `SolrUpdateState`
- `index_subjects.py` (update import): **Present** (2) — file hit confirmed
Score: (0+1+1+2) / (4×2) × 25 = 4/8 × 25 = **12.5**

**Dimension C — 0/25**: All 6 FAIL_TO_PASS tests import `from openlibrary.solr.utils import SolrUpdateState, solr_update`. Model's `utils.py` exports `SolrUpdateRequest` (not `SolrUpdateState`) → `ImportError` on all 6 tests. Score: **0**

**Dimension D — 10/25**: `utils.py` content is structurally correct — all functions present (`load_config`, `get/set_solr_base_url`, `get/set_solr_next`, `solr_update` with full retry logic, `solr_insert_documents`). Critical error: class named `SolrUpdateRequest` vs required `SolrUpdateState`. Also misses `update_edition.py` import fix and the complete removal of old code from `update_work.py`. Score: **10**

---

### Task 5 — `4a5d2a7d` | wikidata get_statement_values
**Score: 20.6/100** (A=8.3, B=6.3, C=0, D=6)

**Task**: Add `get_statement_values(property_id)` to `WikidataEntity`, add `SOCIAL_PROFILES` constant, add `get_profiles_to_render()`, update `infobox.html`, update `messages.pot`.

**Dimension A — 8.3/25**: Produces a unified diff, hits `wikidata.py` (1/3 gold files). Misses `messages.pot` and `templates/authors/infobox.html`. Formula: 1/3 × 25 = **8.3**

**Dimension B — 6.3/25**: Gold has ~6 hunks (4 in wikidata.py + 1 in messages.pot + 1 in infobox.html).
- Fix `statements` type annotation: likely present or partial
- Add `SOCIAL_PROFILES` constant: **Missing**
- Add `get_statement_values()`: **Partial** (model adds `_get_statement_values()` — private name, different logic)
- Add `get_profiles_to_render()`: **Missing**
- messages.pot and infobox.html: **Missing**
Score: ~(1+0+1+0+0+0)/(6×2) × 25 ≈ **6.3**

**Dimension C — 0/25**: FAIL_TO_PASS test calls `entity.get_statement_values('P2038')` (public). Model implements `_get_statement_values` (private, underscore prefix) → `AttributeError`. Additionally, model adds `if statement['value']['type'] == 'value':` check; test data lacks `'type'` key → `KeyError` → caught → empty list returned instead of valid values. **Double bug: wrong name + wrong logic**. Score: **0**

**Dimension D — 6/25**: Root cause diagnosis partially correct (need `get_statement_values`), but method name is wrong (private vs public) and logic has an extra condition that breaks the test case. Score: **6**

---

### Task 6 — `5069b09e` | db.py ALLOW_DELETE_ON_CONFLICT
**Score: 14.4/100** (A=4.2, B=4.2, C=0, D=6)

**Task**: When `Booknotes.update_work_id` hits a conflict, it incorrectly deletes the existing booknote. Fix: add `ALLOW_DELETE_ON_CONFLICT = False` to Booknotes, wire it into `update_work_ids_individually`, add `failed_deletes` counter, return a dict from `update_work_id`, update 4 other model classes and `admin/code.py`.

**Dimension A — 4.2/25**: Produces a unified diff for `db.py` only (1/6 gold files). Formula: 1/6 × 25 = **4.2**

**Dimension B — 4.2/25**: Gold has ~9 hunks across 6 files.
- `t_update.rollback()` in `update_work_ids_individually`: **Present** (formal diff)
- `ALLOW_DELETE_ON_CONFLICT` check + `failed_deletes` in db.py: **Partial** (described in "full corrected excerpt" prose, not in formal diff)
- `failed_deletes=0` + dict return in `update_work_id`: **Missing**
- booknotes.py, bookshelves.py, observations.py, ratings.py, admin/code.py: **Missing** (all 5 files)
Score: (2+1+0+0+0+0+0+0+0)/(9×2) × 25 ≈ **4.2**

**Dimension C — 0/25**: Test asserts `resp == {'rows_changed': 0, 'rows_deleted': 0, 'failed_deletes': 1}`. The formal diff only adds `t_update.rollback()`. Without `Booknotes.ALLOW_DELETE_ON_CONFLICT = False` defined, `cls.ALLOW_DELETE_ON_CONFLICT` raises `AttributeError`. Return is still a tuple, not a dict. **Score: 0**

**Dimension D — 6/25**: Correctly identifies root cause (unresolved savepoint). Partial solution describing the right logic in prose. Missing the critical attribute definitions and return type change. Score: **6**

---

### Task 7 — `5c6c22f3` | importapi IA record helpers
**Score: 0/100** — `is_prose_only = True` *(re-evaluated: answer updated but remains prose-only)*

Model produced no code changes (`model_file_count = 0`, `is_prose_only = true`). Gold requires two new utility functions in `upstream/utils.py` (`get_isbn_10_and_13`, `get_publisher_and_place`) and a refactored `get_ia_record` in `importapi/code.py` that calls them. Model proposes modifying the existing `get_location_and_publisher` function (wrong target — gold adds new functions) and doesn't address `code.py`. All dimensions: **0**.

---

### Task 8 — `8a5a63af` | monitoring OlAsyncIOScheduler rename
**Score: 11.0/100** (A=0, B=5.0, C=0, D=6) *(re-evaluated: answer updated)*

**Task**: Rename `OlBlockingScheduler` → `OlAsyncIOScheduler` (switch from `BlockingScheduler` to `AsyncIOScheduler`), add `get_service_ip()` to utils.py, create `haproxy_monitor.py`, update `monitor.py` with async main, add `requests` to `requirements.txt`, update `compose.production.yaml` with `network_mode: host`.

**Dimension A — 0/25**: Produces a diff. Hits `scripts/monitoring/monitor.py` and `scripts/monitoring/utils.py` (2/5 gold files). Creates 3 spurious extra files (`__init__.py`, `tests/__init__.py`, `tests/test_utils_py.py`). Formula: 2/5 × 25 − 3 × (25/5) = 10 − 15 = **−5 → clamped to 0**

**Dimension B — 5.0/25**: Gold has 5 file hunks.
- `utils.py` (rename class, change base, add `[OL-MONITOR]` prefix, add `get_service_ip`): **Partial** (1) — model creates utils.py with `OLBlockingScheduler` (BlockingScheduler subclass, wrong name and wrong base class). Has `add_job` with hosts filtering and `bash_run` and `limit_server`, but misses `get_service_ip` and `[OL-MONITOR]` prefix. Class type mismatch is fundamental.
- `monitor.py` (import rename, async main, `[OL-MONITOR]` prefix, `monitor_haproxy`): **Partial** (1) — model creates monitor.py using OLBlockingScheduler, missing async main and haproxy job
- `haproxy_monitor.py` (new 149-line file): **Missing** (0)
- `requirements.txt`: **Missing** (0)
- `compose.production.yaml`: **Missing** (0)
Score: (1+1+0+0+0) / (5×2) × 25 = 2/10 × 25 = **5.0**

**Dimension C — 0/25**: Tests import `OlAsyncIOScheduler` from utils. Model exports `OLBlockingScheduler` → `ImportError` on both tests. Score: **0**

**Dimension D — 6/25**: `add_job` with hosts filtering and `_host_matches` wildcard logic structurally match gold's `limit_server`/host-check approach. `bash_run` is present. But class is `OLBlockingScheduler`/`BlockingScheduler` (should be `OlAsyncIOScheduler`/`AsyncIOScheduler`), missing `get_service_ip`, missing `[OL-MONITOR]` prefix, missing async main in monitor.py. Score: **6**

---

### Task 9 — `b4f7c185` | Solr update_key tuple return
**Score: 0/100** — `is_prose_only = True` *(re-evaluated: answer updated)*

**Task**: `AuthorSolrUpdater.update_key` and `WorkSolrUpdater.update_key` return bare `SolrUpdateRequest` instead of `tuple[SolrUpdateRequest, list[str]]`. Callers unpack two values; fix requires changing all 4 updater classes to return tuples + removing `keys` field from `SolrUpdateRequest` dataclass.

Model correctly identifies the fix (`return (SolrUpdateRequest(adds=[doc]), [])` / `return update, []`) and names the right files. However, the answer targets `openlibrary/solr/updater/author.py` and `openlibrary/solr/updater/work.py` (files that don't exist — gold modifies `update_work.py` and `utils.py`). No actual diff is produced. `is_prose_only = True`. All dimensions: **0**.

---

### Task 10 — `dbbd9d53` | ListRecord.from_input seeds parsing
**Score: 72.2/100** (A=12.5, B=16.7, C=25, D=18)

**Task**: `ListRecord.from_input()` crashes when POST body is parsed with `parse_qs` — seeds parsed as a string, iterated character-by-character. Fix requires: (1) preserving seeds as a list in form_data parsing in `lists.py`, (2) removing `setvalue()` "don't overwrite" guard in `utils.py`.

**Dimension A — 12.5/25**: Produces a unified diff. Hits `lists.py` (1/2 gold files). Misses `utils.py`. Formula: 1/2 × 25 = **12.5**

**Dimension B — 16.7/25**: Gold has ~3 hunks (2 in lists.py + 1 in utils.py).
- `from urllib.parse import parse_qs` import: **Present**
- Complete `from_input()` rewrite (DEFAULTS dict, if data: branch, else: branch, dict key access): **Present**
- utils.py `setvalue()` "don't overwrite" removal: **Missing**
Score: (2+2+0)/(3×2) × 25 = 4/6 × 25 = **16.7**

**Dimension C — 25/25**: FAIL_TO_PASS test `test_from_input_with_data` uses nested seed format (`seeds--0--key=/books/OL1M&seeds--1--key=/books/OL2M`). With the model's fix: `k: v if k == 'seeds' else v[0]` — since keys are `seeds--0--key` (not literally `seeds`), they all receive `v[0]` (same as gold). `utils.unflatten` processes `seeds--0--key` and `seeds--1--key` into `[{'key': '/books/OL1M'}, {'key': '/books/OL2M'}]` correctly. The `setvalue` "don't overwrite" bug is **not triggered** for this test (no key conflicts during unflatten). Test **passes**. Score: **25**

**Dimension D — 18/25**: Core logic correct and produces valid output. Model's `k == 'seeds'` conditional handles the direct seeds case (gold uses `v[0]` for all since nested format is assumed). Minor approach difference but functionally equivalent for the tested scenario. Missing utils.py change. Score: **18**

---

## Key Failure Patterns

### 1. Wrong class name / wrong base class (Tasks 4, 5, 8, 9)
- **25858f9f**: `SolrUpdateRequest` vs `SolrUpdateState` → `ImportError` on all 6 tests
- **4a5d2a7d**: `_get_statement_values` (private) vs `get_statement_values` (public) → `AttributeError`
- **8a5a63af**: `OLBlockingScheduler`/`BlockingScheduler` vs `OlAsyncIOScheduler`/`AsyncIOScheduler` → `ImportError` on both tests; additionally misses `get_service_ip`, `[OL-MONITOR]` prefix, and haproxy infrastructure
- **b4f7c185**: Prose-only; targets non-existent `updater/author.py` and `updater/work.py` instead of `update_work.py`
- Pattern: structurally correct implementations fail at C=0 due to a single naming mismatch

### 2. Correct analysis, no diff produced (Tasks 2, 3, 9)
- **111347e9**: Correctly names `get_linkage` and `MarcFieldBase` but produces no diff; also uses wrong approach (modifies `read_title`/`read_author_person` rather than fixing the decode pipeline in `get_subjects.py` and `marc_xml.py`)
- **11838fad**: Correctly identifies all 4 bugs with matching fixes, including `strip_trailing_dot` for role, `personal_name` dedup, `read_contributions` rewrite — but no diff produced
- **b4f7c185**: Correctly identifies tuple return fix but no diff produced

### 3. Prose-only responses (Tasks 7, 9)
- **5c6c22f3**: Produces no code changes; also misidentifies function locations (`get_isbn_10_and_13` in `utils/isbn.py` not `upstream/utils.py`) and function name (`get_location_and_publisher` not `get_publisher_and_place`)
- **b4f7c185**: Produces no code changes

### 4. Incomplete multi-file changes (Tasks 1, 6)
- **00bec1e7**: Correctly solves the import_validator logic but doesn't rename `Book` → `CompleteBookPlus` and misses `code.py`
- **5069b09e**: Adds `t_update.rollback()` (correct) but misses `ALLOW_DELETE_ON_CONFLICT = False` in `booknotes.py`, `failed_deletes` counter, and dict return format

---

## Observations

### vs mcp_average_at_3 (previous batch)
| Metric | mcp_skills_pass_at_3 | mcp_average_at_3 | Δ |
|--------|----------------------|-------------------|---|
| Mean total | **26.1** | 19.5 | +6.6 |
| Mean A | 4.4 | 3.1 | +1.3 |
| Mean B | 7.9 | 6.4 | +1.5 |
| Mean C | 5.0 | 3.4 | +1.6 |
| Mean D | 8.8 | 6.6 | +2.2 |
| Prose-only | 20% | 30% | -10% |
| Pass@1 equiv. | 20% | 0% | +20% |

With the latest answers, the MCP skills condition shows stronger B and D scores (+1.5, +2.2) reflecting more complete patch analysis and better code quality. Two tasks remain prose-only (b4f7c185, 5c6c22f3). The two C=25 passes (00bec1e7, dbbd9d53) are unchanged. The key bottleneck is that several answers with correct analyses fail at C=0 due to either no diff produced (11838fad, 111347e9) or a single naming error blocking the import (25858f9f `SolrUpdateRequest`, 8a5a63af `OLBlockingScheduler`).

### Highlights
- **dbbd9d53** (72.2): Best score in this batch. Model correctly parses form data and produces working fix for the specific test's seed format.
- **00bec1e7** (63.8): Two-stage validation logic is functionally correct even with different class names.
- **8a5a63af** (8.0): Diagnosed as a scheduler enhancement task rather than a rename task — a clean hallucination of a plausible feature.
- **4a5d2a7d** (20.6): Regression vs mcp_average_at_3 (26.6) — extra `type == 'value'` check introduced a new logic bug.
