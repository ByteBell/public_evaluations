# Evaluation Report — mcp_average_at_3

**Run**: `results_on_swe_bench_pro_regrouped/best_showcase_results/mcp_average_at_3`
**Repo**: internetarchive/openlibrary (all 10 tasks)
**Language**: Python
**Evaluator**: Claude Sonnet 4.6 (LLM judge)
**Date**: 2026-04-16
**Rubric**: evaluation_guide.md — Dimensions A (precomputed), B/C/D (LLM judged)

---

## Task Scores

| # | Instance (short) | A /25 | B /25 | C /25 | D /25 | Total /100 | Failure Pattern |
|---|------------------|-------|-------|-------|-------|------------|-----------------|
| 1 | 00bec1e7 | 0.0 | 14.6 | 25.0 | 15.0 | **54.6** | Prose format; correct logic; wrong class names |
| 2 | 111347e9 | 10.0 | 5.0 | 6.0 | 6.0 | **27.0** | Wrong fix target; 3/5 files missed |
| 3 | 11838fad | 0.0 | 4.2 | 3.0 | 3.0 | **10.2** | Wrong root cause; touched test file; 54 tests unaddressed |
| 4 | 25858f9f | 0.0 | 23.2 | 0.0 | 18.0 | **41.2** | `SolrUpdateRequest` vs `SolrUpdateState` — one rename kills all 6 tests |
| 5 | 4a5d2a7d | 8.3 | 6.3 | 0.0 | 12.0 | **26.6** | `_get_statement_values` (private prefix) vs `get_statement_values` |
| 6 | 5069b09e | 0.0 | 0.0 | 0.0 | 0.0 | **0.0** | Prose only |
| 7 | 5c6c22f3 | 0.0 | 0.0 | 0.0 | 0.0 | **0.0** | Prose only |
| 8 | 8a5a63af | 0.0 | 5.6 | 0.0 | 8.0 | **13.6** | Wrong class name/base; 3 spurious files wipe A |
| 9 | b4f7c185 | 0.0 | 4.2 | 0.0 | 6.0 | **10.2** | Changes in wrong files (`updater/` vs `update_work.py`) |
| 10 | dbbd9d53 | 12.5 | 6.3 | 0.0 | 6.0 | **24.8** | Missing `utils.py` setvalue fix |

---

## Aggregate Metrics

| Metric | Value |
|--------|-------|
| `avg_score` | **20.9 / 100** |
| `avg_score_A` | 3.1 / 25 (12.4%) |
| `avg_completeness (B)` | 7.0 / 25 (28.0%) |
| `avg_test_coverage (C)` | 3.4 / 25 (13.6%) |
| `avg_correctness (D)` | 7.4 / 25 (29.6%) |
| `full_patch_rate (≥85)` | 0 / 10 (0%) |
| `partial_rate (40–84)` | 2 / 10 (20%) |
| `zero_rate (0–39)` | 8 / 10 (80%) |
| `prose_only_rate` | 2 / 10 (20%) |
| `answer_rate` | 8 / 10 (80%) |

---

## Per-Task Scoring Sheets

---

### Task 1 — `instance_internetarchive__openlibrary-00bec1e7…`
**Topic**: import_validator — strong-identifier validation path

```
--- From score_input.json ---
score_A        : 0.0/25   (0/2 files × 25 — answer in prose/code-block format)
file_hits      : []
file_misses    : [openlibrary/plugins/importapi/code.py,
                  openlibrary/plugins/importapi/import_validator.py]
extra_files    : []
is_prose_only  : false
fail_to_pass   : [test_validate_strong_identifier_minimal,
                  test_validate_multiple_strong_identifiers[isbn_10],
                  test_validate_multiple_strong_identifiers[lccn]]
test_functions : [test_validate_strong_identifier_minimal,
                  test_validate_multiple_strong_identifiers,
                  test_validate_not_complete_no_strong_identifier]
assert_samples : assert validator.validate(valid_values_strong_identifier) is True
                 assert validator.validate(multiple_valid_values) is True

--- Dimension B: Patch Completeness ---
Gold patch changes:
  [x] code.py variable rename (required_fields→minimum_complete_fields) : missing  (0)
  [x] STRONG_IDENTIFIERS constant                                         : present  (2)
  [x] Book renamed to CompleteBookPlus                                    : missing  (0)
  [x] StrongIdentifierBookPlus with @model_validator                      : partial  (1)
       (model has DifferentiableBook with inline check instead)
  [x] validate() tries CompleteBookPlus then StrongIdentifierBookPlus     : present  (2)
  [x] validate() return type → bool                                       : present  (2)
Coverage: 7/12 raw score

--- Dimension C: Test Coverage ---
  [x] test_validate_strong_identifier_minimal  : passes
       Model: Book fails (no authors/publishers/publish_date) → has_strong_identifier=True
       (isbn_13 present) → DifferentiableBook (title+source_records) validates → True
  [x] test_validate_multiple_strong_identifiers[isbn_10] : passes
       isbn_13+isbn_10 → strong identifier found → passes
  [x] test_validate_multiple_strong_identifiers[lccn]    : passes
       isbn_13+lccn → strong identifier found → passes
Coverage: 3/3 tests

--- Dimension D: Code Correctness ---
Symbol names vs test call sites : validator.validate() ✓; STRONG_IDENTIFIERS ✓
Parameter defaults               : correct
Logic vs assert_samples         : correct — all three assertions satisfied
Class names                     : DifferentiableBook ≠ StrongIdentifierBookPlus; Book not renamed
@model_validator                : absent (inline check used instead — functionally equivalent)
Imports                         : Final / model_validator missing from imports

--- Scores ---
A. File Coverage   : 0.0/25
B. Completeness    : 14.6/25
C. Test Coverage   : 25.0/25
D. Correctness     : 15.0/25
TOTAL              : 54.6/100

--- Notes ---
Correct approach and logic; passes all FAIL_TO_PASS tests. Answer in prose/code-block format
(no git diff) so score_A=0. Class names diverge from gold (DifferentiableBook vs
StrongIdentifierBookPlus; Book not renamed to CompleteBookPlus). Missing code.py cosmetic
rename. If submitted as a proper diff it would likely pass all 3 tests.
```

---

### Task 2 — `instance_internetarchive__openlibrary-111347e9…`
**Topic**: MARC 880 alternate-script linkage (5-file pipeline refactor)

```
--- From score_input.json ---
score_A        : 10.0/25  (2/5 files × 25)
file_hits      : [openlibrary/catalog/marc/marc_base.py,
                  openlibrary/catalog/marc/parse.py]
file_misses    : [get_subjects.py, marc_binary.py, marc_xml.py]
extra_files    : []
is_prose_only  : false
fail_to_pass   : [TestParseMARCXML::test_xml[nybc200247],
                  TestParseMARCBinary::test_binary[880_arabic_french_many_linkages.mrc]]
assert_samples : assert sorted(edition_marc_xml) == sorted(j), msg
                 assert len(value) == len(j[key]), msg + key
                 assert item in value, msg + key

--- Dimension B: Patch Completeness ---
  [x] get_subjects.py  — remove all rec.decode_field() calls  : missing  (0)
  [x] marc_base.py     — MarcFieldBase class + get_fields()
                         refactor + get_linkage() move         : partial  (1)
       (model adds only a defensive guard to get_linkage;
        misses MarcFieldBase, get_fields() rewrite)
  [x] marc_binary.py   — extends MarcFieldBase, remove
                         get_linkage() (moved to base)         : missing  (0)
  [x] marc_xml.py      — extends MarcFieldBase, read_fields()
                         yields decoded DataField objects       : missing  (0)
  [x] parse.py         — update_edition reorder, read_
                         contributions fix, read_notes range   : partial  (1)
       (model adds read_other_titles $6 handling — orthogonal
        to the actual gold parse.py changes)
Coverage: 2/10 raw score

--- Dimension C: Test Coverage ---
  [x] test_xml[nybc200247]    : fails
       Requires: Yiddish script as primary title (title field swapped to Hebrew script),
       alternate_names added to Dubnow author dict. Model doesn't address title swap or
       author alternate_names at all.
  [x] test_binary[880_arabic_french_many_linkages] : partial
       Model adds $6 linkage in read_other_titles for 246 fields; BinaryDataField has
       correct API so logic could work for binary MARC. However gold's approach routes
       through the refactored get_fields pipeline, not a parse.py patch-on. Partial credit.
Coverage: 0.5/2 tests

--- Dimension D: Code Correctness ---
Symbol names     : get_linkage() guard correct in isolation
API calls        : get_contents() is valid API for DataField/BinaryDataField
Core pipeline    : MarcFieldBase hierarchy entirely absent; read_fields decode absent
Root cause       : Misidentified — model targets read_other_titles/$6 as the fix;
                   actual gold fix is pipeline-level (read_fields returns decoded objects)

--- Scores ---
A. File Coverage   : 10.0/25
B. Completeness    : 5.0/25
C. Test Coverage   : 6.0/25
D. Correctness     : 6.0/25
TOTAL              : 27.0/100

--- Notes ---
Model attacks the symptom (missing $6 linkage in title readers) rather than the root cause
(get_fields returns raw elements, not decoded DataField objects). Gold's actual fix is a deep
pipeline refactor across 5 files; model only patches 2 with a surface-level fix. The 3 missed
files (get_subjects.py, marc_binary.py, marc_xml.py) contain the core changes.
```

---

### Task 3 — `instance_internetarchive__openlibrary-11838fad…`
**Topic**: MARC parse.py — role trailing dot, personal_name dedup, alternate_names swap (54 tests)

```
--- From score_input.json ---
score_A        : 0.0/25   (1/1 file hit BUT 1 extra test file → full deduction)
file_hits      : [openlibrary/catalog/marc/parse.py]
file_misses    : []
extra_files    : [openlibrary/catalog/marc/tests/test_parse.py]  ← PENALIZED
is_prose_only  : false
fail_to_pass   : 54 tests (full TestParseMARCXML + TestParseMARCBinary suites)
assert_samples : assert sorted(edition_marc_bin) == sorted(j), msg
                 assert result['name'] == 'Rein, Wilhelm'

--- Dimension B: Patch Completeness ---
  [x] name_from_list gains strip_trailing_dot=True param        : missing  (0)
  [x] read_author_person role — name_from_list(..., False)       : partial  (1)
       (model removes role from subfields list differently;
        does not preserve trailing dot via strip_trailing_dot)
  [x] personal_name dedup (del if == name)                       : missing  (0)
  [x] alternate_names swap (880 script → primary name;
       romanized → alternate_names)                              : missing  (0)  ← CRITICAL
  [x] read_authors major refactor                                : missing  (0)
  [x] read_contributions cleanup                                 : partial  (1)
Coverage: 2/12 raw score

--- Dimension C: Test Coverage ---
  54 tests depend on the deep parse.py refactor. Missing the alternate_names swap
  (gold makes 880-linked script the primary name), personal_name dedup, and read_authors
  refactor means the majority of test fixtures would still mismatch. Model also modifies
  test_parse.py, introducing potential assertion gaming risk.
Coverage: ~3/54 (very few from contributions partial fix)

--- Dimension D: Code Correctness ---
Root cause     : Wrong — model targets 880 $6 linkage in work/other titles; actual gold
                 targets name handling in read_author_person
alternate_names: Missing the swap logic (most critical change in gold)
Test file      : Modified — penalized in A; gaming risk flagged

--- Scores ---
A. File Coverage   : 0.0/25
B. Completeness    : 4.2/25
C. Test Coverage   : 3.0/25
D. Correctness     : 3.0/25
TOTAL              : 10.2/100

--- Notes ---
Model misidentifies the problem as 880 linkage in title readers; gold's actual fix is in
read_author_person (role dot preservation, personal_name dedup, alternate_names swap where
the 880 script becomes the primary name). Touches test file (penalizes A fully). With 54
failing tests, this answer would not come close to passing.
```

---

### Task 4 — `instance_internetarchive__openlibrary-25858f9f…`
**Topic**: Solr utils.py extraction — SolrUpdateState, solr_update

```
--- From score_input.json ---
score_A        : 0.0/25   (0/4 files — answer in prose/code-block format, no diff)
file_hits      : []
file_misses    : [update_edition.py, update_work.py, utils.py,
                  scripts/solr_builder/solr_builder/index_subjects.py]
extra_files    : []
is_prose_only  : false
fail_to_pass   : [test_successful_response, test_non_json_solr_503,
                  test_solr_offline, test_invalid_solr_request,
                  test_bad_apple_in_solr_request, test_other_non_ok_status]
assert_samples : assert mock_post.call_count == 1
                 assert mock_post.call_count > 1

--- Dimension B: Patch Completeness ---
  [x] New utils.py — load_config, get/set_solr_base_url,
                     get/set_solr_next                           : present  (2)
  [x] New utils.py — SolrUpdateState dataclass                  : partial  (1)
       (model creates SolrUpdateRequest — identical structure,
        wrong name)
  [x] New utils.py — solr_update()                              : present  (2)
  [x] New utils.py — solr_insert_documents()                    : present  (2)
  [x] update_work.py — remove all globals/functions/class,
                        update imports from utils               : present  (2)
  [x] update_edition.py — fix import from utils                 : present  (2)
  [x] index_subjects.py — fix import from utils                 : present  (2)
Coverage: 13/14 raw score

--- Dimension C: Test Coverage ---
  All 6 tests:  from openlibrary.solr.utils import SolrUpdateState, solr_update
  Model creates SolrUpdateRequest not SolrUpdateState → ImportError on all 6 tests.
  solr_update() is present and correct but unreachable due to import failure.
Coverage: 0/6 tests

--- Dimension D: Code Correctness ---
solr_update() logic  : exact match to gold (retry strategy, 400/indiv/global error handling)
SolrUpdateState      : identical fields and methods, only name differs (SolrUpdateRequest)
Other utils          : all present and correct
Fatal issue          : one class rename (SolrUpdateRequest → SolrUpdateState) is all that
                       separates this from a perfect score on C

--- Scores ---
A. File Coverage   : 0.0/25
B. Completeness    : 23.2/25
C. Test Coverage   : 0.0/25
D. Correctness     : 18.0/25
TOTAL              : 41.2/100

--- Notes ---
Outstanding structural work — nearly all gold changes present and correctly implemented.
Single fatal error: class named SolrUpdateRequest instead of SolrUpdateState. Tests import
SolrUpdateState by name → ImportError → all 6 fail. One rename from a near-perfect answer.
```

---

### Task 5 — `instance_internetarchive__openlibrary-4a5d2a7d…`
**Topic**: WikidataEntity.get_statement_values() + social profiles

```
--- From score_input.json ---
score_A        : 8.3/25   (1/3 files × 25)
file_hits      : [openlibrary/core/wikidata.py]
file_misses    : [openlibrary/i18n/messages.pot,
                  openlibrary/templates/authors/infobox.html]
extra_files    : []
is_prose_only  : false
fail_to_pass   : [tests/core/test_wikidata.py::test_get_statement_values]
test_functions : [test_get_statement_values]
assert_samples : assert entity.get_statement_values('P2038') == ['Chris-Wiggins']
                 assert entity.get_statement_values('P2038') == ['Value1', 'Value2', 'Value3']
                 assert entity.get_statement_values('P9999') == []
                 assert entity.get_statement_values('P2038') == ['Valid']

--- Dimension B: Patch Completeness ---
  [x] statements type annotation fix (dict[str,dict] → dict[str,list[dict]]) : present (2)
  [x] SOCIAL_PROFILES list constant                                            : missing (0)
  [x] get_statement_values() method                                            : partial (1)
       (model implements _get_statement_values with underscore prefix)
  [x] get_profiles_to_render() method                                          : missing (0)
  [x] i18n/messages.pot update                                                 : missing (0)
  [x] infobox.html template — render social icons                              : missing (0)
Coverage: 3/12 raw score

--- Dimension C: Test Coverage ---
  [x] test_get_statement_values : fails
       Test calls entity.get_statement_values('P2038') — no underscore.
       Model implements _get_statement_values('P2038') — with underscore.
       AttributeError: 'WikidataEntity' object has no attribute 'get_statement_values'
Coverage: 0/1 tests

--- Dimension D: Code Correctness ---
Method logic    : exactly correct (property guard, list comprehension with 'value'/'content'
                  guards, returns [] for missing property)
Method name     : _get_statement_values ≠ get_statement_values (underscore prefix error)
statements type : correctly fixed
SOCIAL_PROFILES : entirely absent
Template/i18n   : entirely absent

--- Scores ---
A. File Coverage   : 8.3/25
B. Completeness    : 6.3/25
C. Test Coverage   : 0.0/25
D. Correctness     : 12.0/25
TOTAL              : 26.6/100

--- Notes ---
Correct implementation logic for the core method — the list comprehension, edge case guards,
and return type all match gold exactly. Single error: private _get_statement_values vs public
get_statement_values. One underscore character causes AttributeError. SOCIAL_PROFILES list
and template changes entirely missing (scope of work narrower than gold).
```

---

### Task 6 — `instance_internetarchive__openlibrary-5069b09e…`
**Topic**: Booknotes ALLOW_DELETE_ON_CONFLICT flag

```
--- From score_input.json ---
is_prose_only  : true  →  ALL DIMENSIONS = 0

--- Scores ---
A. File Coverage   : 0.0/25
B. Completeness    : 0.0/25
C. Test Coverage   : 0.0/25
D. Correctness     : 0.0/25
TOTAL              : 0.0/100

--- Notes ---
Model produced a description-only answer explaining the root cause and fix without providing
any code patch. gold touches 6 files (booknotes.py, bookshelves.py, db.py, observations.py,
ratings.py, admin/code.py).
```

---

### Task 7 — `instance_internetarchive__openlibrary-5c6c22f3…`
**Topic**: importapi — split isbn_10/isbn_13, split publisher/publish_places

```
--- From score_input.json ---
is_prose_only  : true  →  ALL DIMENSIONS = 0

--- Scores ---
A. File Coverage   : 0.0/25
B. Completeness    : 0.0/25
C. Test Coverage   : 0.0/25
D. Correctness     : 0.0/25
TOTAL              : 0.0/100

--- Notes ---
Model produced a description-only answer. Gold creates get_isbn_10_and_13() and
get_publisher_and_place() in upstream/utils.py, wires them into importapi/code.py.
8 fail_to_pass tests would remain unaddressed.
```

---

### Task 8 — `instance_internetarchive__openlibrary-8a5a63af…`
**Topic**: monitoring — OlBlockingScheduler → OlAsyncIOScheduler rename

```
--- From score_input.json (run_3, swapped from prose-only base run) ---
score_A        : 0.0/25   (2/5 gold files hit, 3 spurious → deduction wipes score)
file_hits      : [scripts/monitoring/utils.py, scripts/monitoring/monitor.py]
extra_files    : [scripts/monitoring/__init__.py,
                  scripts/monitoring/tests/__init__.py,
                  scripts/monitoring/tests/test_utils_py.py]  ← PENALIZED
is_prose_only  : false
cost           : $1.083  |  time: 489s  |  eff_in: 220k  |  out: 28k
fail_to_pass   : [test_bash_run, test_limit_server]
                 (tests import OlAsyncIOScheduler → ImportError with this answer)

--- Dimension B: Patch Completeness ---
Gold has 9 hunks across 5 files.
  [x] AsyncIOScheduler import in utils.py              : missing  (0)
       (model imports BlockingScheduler instead)
  [x] class OlAsyncIOScheduler(AsyncIOScheduler)       : missing  (0)
       (model uses OLBlockingScheduler(BlockingScheduler) — wrong name AND wrong base)
  [x] [OL-MONITOR] prefix in job_listener              : missing  (0)
       (model has logging but different format)
  [x] limit_server() function                          : partial  (1)
       (correct wildcard hostname logic; tied to wrong class)
  [x] bash_run() function                              : present  (2)
       (subprocess.run with source_file support — matches gold intent)
  [x] get_service_ip() function                        : missing  (0)
  [x] compose.production.yaml                          : missing  (0)
  [x] haproxy_monitor.py                               : missing  (0)
  [x] monitor.py — job scheduling setup                : partial  (1)
       (model creates new monitor.py with scheduler.add_job calls using limit_server)
Coverage: 4/18 raw score

--- Dimension C: Test Coverage ---
  [x] test_bash_run    : fails
       Test suite imports OlAsyncIOScheduler; model defines OLBlockingScheduler
       → ImportError before any test runs.
  [x] test_limit_server : fails (same import failure)
Coverage: 0/2 tests

--- Dimension D: Code Correctness ---
bash_run()     : correct implementation (subprocess, source_file support) ✓
limit_server() : correct wildcard pattern logic ✓
Class name     : OLBlockingScheduler ≠ OlAsyncIOScheduler (wrong name)
Base class     : BlockingScheduler ≠ AsyncIOScheduler (wrong base)
monitor.py     : structurally correct (jobs + limit_server) ✓
Missing        : get_service_ip(), haproxy_monitor.py, requirements.txt, compose.yaml

--- Scores ---
A. File Coverage   : 0.0/25
B. Completeness    : 5.6/25
C. Test Coverage   : 0.0/25
D. Correctness     : 8.0/25
TOTAL              : 13.6/100

--- Notes ---
Swapped from prose-only base run (0/100) to run_3 which produces an actual diff.
Model gets bash_run and limit_server right but misses the core rename (OLBlockingScheduler
vs OlAsyncIOScheduler) and wrong base class (BlockingScheduler vs AsyncIOScheduler).
Adding 3 spurious files (__init__.py, tests/) wipes the A score despite hitting 2/5 gold
files. Tests import OlAsyncIOScheduler by name → ImportError → C=0.
```

---

### Task 9 — `instance_internetarchive__openlibrary-b4f7c185…`
**Topic**: AbstractSolrUpdater.update_key() → tuple return type

```
--- From score_input.json ---
score_A        : 0.0/25   (0/2 gold files; extra file updater/author.py in wrong path)
file_hits      : []
file_misses    : [openlibrary/solr/update_work.py, openlibrary/solr/utils.py]
extra_files    : [openlibrary/solr/updater/author.py]
is_prose_only  : false
fail_to_pass   : [TestAuthorUpdater::test_workless_author,
                  TestWorkSolrUpdater::test_no_title,
                  TestWorkSolrUpdater::test_work_no_title]
assert_samples : (from test_patch: req, _ = await ...update_key(...))

--- Dimension B: Patch Completeness ---
  [x] AbstractSolrUpdater.update_key() → tuple[SolrUpdateRequest, list[str]] : missing (0)
       (model targets updater/author.py not update_work.py)
  [x] EditionSolrUpdater.update_key() → returns (update, new_keys)            : missing (0)
  [x] WorkSolrUpdater.update_key() → returns (update, [])                     : partial (1)
       (model changes updater/work.py — wrong file)
  [x] AuthorSolrUpdater.update_key() → wraps update_author in tuple           : partial (1)
       (model changes updater/author.py — wrong file)
  [x] update_keys() caller unpacks tuple: new_update_state, new_keys = ...    : missing (0)
  [x] SolrUpdateRequest — remove keys field; __add__ drops keys concat        : missing (0)
Coverage: 2/12 raw score

--- Dimension C: Test Coverage ---
  Tests import WorkSolrUpdater, AuthorSolrUpdater from openlibrary.solr.update_work.
  Model's changes are in openlibrary/solr/updater/author.py and updater/work.py.
  update_work.py is unchanged → update_key() still returns bare SolrUpdateRequest →
  req, _ = await ...update_key(...) → ValueError: not enough values to unpack → all 3 fail.
Coverage: 0/3 tests

--- Dimension D: Code Correctness ---
Concept         : correct — returning (SolrUpdateRequest, []) is right
File placement  : entirely wrong — model invents updater/ subdirectory that doesn't match
                  actual code structure; tests import from update_work not updater/

--- Scores ---
A. File Coverage   : 0.0/25
B. Completeness    : 4.2/25
C. Test Coverage   : 0.0/25
D. Correctness     : 6.0/25
TOTAL              : 10.2/100

--- Notes ---
Right concept (return tuple), entirely wrong files. Model creates openlibrary/solr/updater/
author.py and work.py which don't exist in the codebase — the classes live in update_work.py.
Tests import from update_work and get a bare SolrUpdateRequest → unpacking error.
```

---

### Task 10 — `instance_internetarchive__openlibrary-dbbd9d53…`
**Topic**: ListRecord.from_input() — parse POST body, fix setvalue overwrite

```
--- From score_input.json ---
score_A        : 12.5/25  (1/2 files × 25)
file_hits      : [openlibrary/plugins/openlibrary/lists.py]
file_misses    : [openlibrary/plugins/upstream/utils.py]
extra_files    : []
is_prose_only  : false
fail_to_pass   : [TestListRecord::test_from_input_with_data]
test_functions : [test_from_input_no_data, test_from_input_with_data, test_from_input_seeds]
assert_samples : assert ListRecord.from_input() == ListRecord(...)

--- Dimension B: Patch Completeness ---
  [x] lists.py — from_input() rewritten to parse web.data() via parse_qs,
                 dict-based access (i['name'] not i.name)       : partial (1)
       (model has parse_qs and dict access but different seeds
        handling mechanism; misses key parts of the rewrite)
  [x] utils.py — setvalue() remove "don't overwrite" guard      : missing (0)
Coverage: 1/4 raw score

--- Dimension C: Test Coverage ---
  [x] test_from_input_with_data : fails
       POST body: key=/lists/OL1L&name=foo+data&seeds--0--key=/books/OL1M&seeds--1--key=/books/OL2M
       Without utils.py fix: setvalue() hits "don't overwrite" guard when processing
       seeds--1--key (seeds key already set from seeds--0--key) → only first seed stored
       → seeds=[{'key': '/books/OL1M'}] not both → assertion fails.
Coverage: 0/1 tests

--- Dimension D: Code Correctness ---
parse_qs approach     : correct (same as gold)
dict-based access     : correct (same as gold)
seeds-as-list logic   : works for flat seeds=value format; irrelevant for seeds--N--key format
setvalue guard        : absent — this is the actual root cause of the test failure
Critical missing fix  : utils.py setvalue() "if k not in data" guard must be removed

--- Scores ---
A. File Coverage   : 12.5/25
B. Completeness    : 6.3/25
C. Test Coverage   : 0.0/25
D. Correctness     : 6.0/25
TOTAL              : 24.8/100

--- Notes ---
Model correctly identifies parse_qs approach for reading POST body and switches to dict-based
access. The implementation works for simple cases but fails the actual test because the
utils.py setvalue() "don't overwrite" guard prevents the second seed from being stored when
using seeds--N--key nested format. One missing file change causes the test to fail.
```

---

## Key Failure Patterns

| Pattern | Tasks Affected | Impact |
|---------|----------------|--------|
| **Prose-only** — model explains but produces no code | 6, 7 | 2 × 0/100 |
| **One-symbol naming error** kills all tests | 4 (`SolrUpdateRequest`), 5 (`_get_statement_values`) | C=0 despite correct logic |
| **Wrong file targeting** — right concept, wrong path | 9 (`updater/` vs `update_work.py`) | C=0 |
| **Missing second file** — partial fix only | 10 (missing `utils.py`) | C=0 |
| **Wrong root cause** — addresses symptom not source | 2, 3 | Low B+C |
| **Prose-format code** — code blocks not diffs | 1, 4 | A=0 |

## Observations

1. **Naming precision is the biggest single failure point**: Tasks 4 and 5 have near-perfect implementations that score 0 on test coverage because of a single wrong name (`SolrUpdateRequest` vs `SolrUpdateState`, `_get_statement_values` vs `get_statement_values`). Together they represent ~68 points left on the table.

2. **Prose-only rate is 20%**: 2 tasks produced no code at all (5069b09e, 5c6c22f3). Task 8 (8a5a63af) was upgraded from a prose-only base run to run_3 which produces a real diff.

3. **Answer format matters**: Tasks 1 and 4 produced correct code in markdown code-blocks rather than git diff format. This gives A=0 even though the code addresses the right files.

4. **B scores are relatively higher than C scores** (avg B=6.4 vs avg C=3.4): the model often identifies the right approach and touches the right areas but fails on precision details that tests check — naming, exact file choice, or a missed companion change.

5. **Multi-file cascade tasks are hard**: Tasks 2, 3, 9, 10 all require coordinated changes across 2–5 files. The model consistently misses at least one critical file, and that missing file is usually the one the tests depend on.
