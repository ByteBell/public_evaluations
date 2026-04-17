# SWE-Pro Evaluation Report — Raw Run (claude-sonnet-4-6, run 5)

**Run directory**: `auto_run_on_swe_pro_raw_claude-sonnet-4-6_run_5`
**Model**: claude-sonnet-4-6 (+ claude-haiku-4-5 as subagent orchestration)
**Mode**: Raw (no MCP knowledge server, no skills)
**Evaluator**: claude-sonnet-4-6 · 2026-04-17
**Reference baseline**: `best_showcase_results/mcp_skills_pass_at_3` (eval_report.md)
**Comparison run**: `prompt_updated_runs/mcp_with_skills.md` (mcp+skills run_5)

---

## Score Summary

| # | Instance | A | B | C | D | Total |
|---|---|---|---|---|---|---|
| 1 | 00bec1e7 | 0.0 | 0.0 | 0.0 | 8.0 | **8.0** |
| 2 | 111347e9 | 25.0 | 15.0 | 8.0 | 15.0 | **63.0** |
| 3 | 11838fad | 0.0 | 20.0 | 15.0 | 18.0 | **53.0** |
| 4 | 25858f9f | 18.8 | 18.8 | 12.0 | 17.0 | **66.6** |
| 5 | 4a5d2a7d | 0.0 | 4.2 | 0.0 | 10.0 | **14.2** |
| 6 | 5069b09e | 4.2 | 7.0 | 20.0 | 15.0 | **46.2** |
| 7 | 5c6c22f3 | 0.0 | 25.0 | 20.0 | 20.0 | **65.0** |
| 8 | 8a5a63af | 25.0 | 20.0 | 15.0 | 17.0 | **77.0** |
| 9 | b4f7c185 | 0.0 | 6.3 | 0.0 | 12.0 | **18.3** |
| 10 | dbbd9d53 | 25.0 | 18.8 | 5.0 | 15.0 | **63.8** |
| | **Average** | **9.8** | **13.5** | **9.5** | **14.7** | **47.5** |

---

## Aggregate Metrics

| Metric | Raw run_5 | MCP+Skills run_5 | MCP+Skills pass@3 baseline |
|---|---|---|---|
| Mean total | **47.5 / 100** | 27.1 / 100 | 26.1 / 100 |
| Mean A | 9.8 | 3.6 | — |
| Mean B | 13.5 | 7.7 | — |
| Mean C | 9.5 | 5.5 | — |
| Mean D | 14.7 | 10.3 | — |
| Prose-only | 0% | 0% | 20% |
| Pass@1 (C = 25) | **0%** | 20% | 20% |
| Zero-score (Total = 0) | 0% | 10% | — |
| Avg cost/task | $1.45 | $1.35 | — |
| Avg API calls/task | 46.5 | 22.4 | — |
| Models used | sonnet-4-6 + haiku-4-5 | sonnet-4-6 only | sonnet-4-6 only |

**Key finding**: The raw run scores nearly 2× higher on overall total (47.5 vs 27.1) due to more compute (multi-model, ~46 API calls/task vs 22) and more complete implementations. However, it achieves 0% Pass@1 vs 20% for the MCP+Skills run — demonstrating that higher B/D scores do not translate to passing tests when correctness edge cases are missed.

---

## Per-Task Scoring

---

### Task 1 — `00bec1e7` · import validation (LCCN as strong identifier)

**Gold files** (2): `openlibrary/plugins/importapi/import_validator.py`, `openlibrary/plugins/importapi/code.py`
**Model files**: `openlibrary/catalog/utils/__init__.py`, `tests/catalog/test_utils.py`, `catalog/add_book/tests/test_add_book.py`
**Cost**: $2.87 · 1139s · 57 API requests

**Dimension A — File Coverage: 0.0 / 25**
The model touches none of the gold files. Instead it modifies `catalog/utils/__init__.py` to rename `has_isbn` → `has_strong_identifier` (adding LCCN support). Gold file `import_validator.py` is untouched.
`raw = 0/2 × 25 = 0; deduction = 0; A = 0.0`

**Dimension B — Patch Completeness: 0.0 / 25**
Gold patch creates a `DifferentiableBook` class in `import_validator.py` with a two-stage `validate()` method. The model implements a completely different change (expanding the ISBN check to include LCCN). No gold hunks are present or partial. B = 0.0.

**Dimension C — Test Coverage: 0.0 / 25**
Fail-to-pass tests exercise `DifferentiableBook` in `import_validator.py`. The model never touches that file. C = 0.0.

**Dimension D — Code Correctness: 8.0 / 25**
The LCCN-as-strong-identifier change is valid, well-structured code that correctly addresses LCCN exemptions from the ISBN requirement. It adds sensible test cases. However, it solves a *different problem* from the gold patch — this is an orthogonal improvement, not the targeted fix. D = 8.

**Total: 8.0** · Dominant failure: completely wrong target — model chose a different valid change rather than finding the actual requested change.

---

### Task 2 — `111347e9` · marc `decode_field` removal

**Gold files** (5): `get_subjects.py`, `marc_base.py`, `marc_binary.py`, `marc_xml.py`, `parse.py`
**Model files**: same 5 — all gold files hit, no extras
**Cost**: $1.14 · 359s · 62 API requests

**Dimension A — File Coverage: 25.0 / 25**
All 5 gold files touched, no extra files. `A = 5/5 × 25 = 25.0`.

**Dimension B — Patch Completeness: 15.0 / 25**
Model changes:
- `marc_base.py`: adds `MarcFieldBase` empty base class (PRESENT); updates `get_fields` to call `read_fields` instead of `decode_field` (PRESENT); moves `get_linkage` to `MarcBase` (PRESENT); but does NOT remove the `decode_field` method (MISSING)
- `marc_binary.py`: `BinaryDataField(MarcFieldBase)` (PRESENT); removes `get_linkage` from BinaryDataField since moved to base (PRESENT)
- `marc_xml.py`: `DataField(MarcFieldBase)` (PRESENT); but `read_fields` STILL calls `self.decode_field(f)` at the final yield (MISSING)
- `get_subjects.py`: removes all `rec.decode_field(field)` calls, uses `field` directly (PRESENT)
- `parse.py`: removes one `decode_field` call properly; *comments out* another rather than removing (PARTIAL)

~5 present, 1 partial, 2 missing hunks → `(5×2 + 1×1 + 2×0)/(8×2) × 25 = 11/16 × 25 = 17.2` → B ≈ 15.

**Dimension C — Test Coverage: 8.0 / 25**
2 fail-to-pass tests. The MarcFieldBase class hierarchy is correctly established — both `BinaryDataField` and `DataField` inherit from it. Tests checking `isinstance(field, MarcFieldBase)` would pass. But `marc_xml.py`'s `read_fields` still calls `decode_field`, and `decode_field` is never removed from `marc_base.py`, meaning tests checking for complete removal would fail. C = 8.

**Dimension D — Code Correctness: 15.0 / 25**
Real structural work: class hierarchy, `get_fields` refactoring, `get_linkage` moved to base, caller sites updated. This is the right direction but incomplete — `decode_field` survives in the codebase. D = 15.

**Total: 63.0** · Major improvement vs mcp_skills run_5 (which produced cosmetic changes for this task). Raw run achieves 25.0 on A (vs 0.0) and real structural work on B/D.

---

### Task 3 — `11838fad` · marc parse.py 880 alternate-script linkage

**Gold files** (1): `openlibrary/catalog/marc/parse.py`
**Model files**: `parse.py` + 5 test-data JSON fixtures (`bin_expect/710_org_name_in_direct_order.json`, `bin_expect/880_Nihon_no_chasho.json`, `bin_expect/880_alternate_script.json`, `bin_expect/880_arabic_french_many_linkages.json`, `xml_expect/nybc200247.json`)
**Cost**: $2.73 · 1210s · 91 API requests

**Dimension A — File Coverage: 0.0 / 25**
`parse.py` is correctly hit (1/1). But 5 test-data JSON fixture files are extras.
`raw = 25; deduction = min(5,1) × 25 = 25; A = 0.0`

**Dimension B — Patch Completeness: 20.0 / 25**
Model comprehensively addresses all 880-linkage code paths:
- `read_author_person` (tag 100): swaps `name`/`alternate_names` so original script is primary — PRESENT
- `read_authors` for 110 (org) and 111 (event): same swap — PRESENT
- `read_contributions` for 710 (org) and 711 (event): same swap — PRESENT
- Also updates `read_edition` to move `read_work_titles` earlier — EXTRA (not in gold, risky)

All 5 required tag-type fixes are present. The extra `read_edition` reordering is a minor risk. B = 20.

**Dimension C — Test Coverage: 15.0 / 25**
54 fail-to-pass tests covering both XML and binary parsing across many test records. The core 880-linkage fix is correct for all 5 tag types. The model also correctly updates the fixture JSON files so the test comparisons reflect the new primary/alternate ordering. However, the extra `read_edition` change (moving `read_work_titles` call earlier in the function) could perturb tests that exercise the full edition pipeline. Uncertainty is high with 54 tests. C = 15.

**Dimension D — Code Correctness: 18.0 / 25**
The name/alternate_names swap logic is clean and correct across all tag types (100/110/111/710/711). The fixture updates match the new expected behavior. The `read_edition` reordering is functionally equivalent for most paths but introduces risk. D = 18.

**Total: 53.0** · A=0 entirely due to fixture file penalty — the underlying parse.py fix is comprehensive.

---

### Task 4 — `25858f9f` · Solr `utils.py` extraction

**Gold files** (4): `openlibrary/solr/utils.py` (new), `openlibrary/solr/update_work.py`, `openlibrary/solr/update_edition.py`, `scripts/solr_builder/solr_builder/index_subjects.py`
**Model files**: `utils.py` (new), `update_work.py`, `update_edition.py` — misses `index_subjects.py`
**Cost**: $1.25 · 796s · 30 API requests

**Dimension A — File Coverage: 18.8 / 25**
3/4 gold files hit, no extras. `raw = 3/4 × 25 = 18.75; deduction = 0; A = 18.8`.

**Dimension B — Patch Completeness: 18.8 / 25**
- Creates `utils.py` with `get_solr_base_url`, `set_solr_base_url`, `get_solr_next`, `set_solr_next`, `load_config` — PRESENT
- `update_work.py`: removes all extracted functions, adds import from `utils.py` — PRESENT
- `update_edition.py`: updates import from `update_work` → `utils` for `get_solr_next` — PRESENT
- `index_subjects.py`: not touched — MISSING

`(3×2 + 0) / (4×2) × 25 = 6/8 × 25 = 18.75` → B = 18.8.

**Dimension C — Test Coverage: 12.0 / 25**
6 fail-to-pass tests. Tests checking utils.py extraction and update_work.py/update_edition.py import paths would pass. Tests that exercise `index_subjects.py` (which still imports from the old location) would fail. With 3/4 files covered, roughly half of the 6 tests likely pass. C = 12.

**Dimension D — Code Correctness: 17.0 / 25**
Clean extraction — correct function signatures, proper global state management, clean import updates in two of the three dependent files. Only the `index_subjects.py` import gap prevents a near-complete score. D = 17.

**Total: 66.6** · Solid 3/4 implementation. Higher than mcp_skills run_5 which got 43.3 (hit a different 3 files with wrong class names).

---

### Task 5 — `4a5d2a7d` · wikidata `get_statement_values`

**Gold files** (3): `openlibrary/core/wikidata.py`, `openlibrary/i18n/messages.pot`, `openlibrary/templates/authors/infobox.html`
**Model files**: `openlibrary/core/wikidata.py`, `openlibrary/tests/core/test_wikidata.py` (extra)
**Cost**: $1.39 · 672s · 30 API requests

**Dimension A — File Coverage: 0.0 / 25**
`wikidata.py` hit (1/3), but `test_wikidata.py` is an extra test file.
`raw = 1/3 × 25 = 8.33; deduction = min(1,1) × (25/3) = 8.33; A = 0.0`

**Dimension B — Patch Completeness: 4.2 / 25**
Model adds `_get_statement_values` (private, underscore-prefixed) to `WikidataEntity`. The gold requires `get_statement_values` (public, no underscore). Logic is correct but name is wrong — PARTIAL (1pt). Messages.pot and infobox.html are missing — MISSING (0pt each).
`(1 + 0 + 0) / (3×2) × 25 = 1/6 × 25 = 4.2`

**Dimension C — Test Coverage: 0.0 / 25**
1 fail-to-pass test calls `entity.get_statement_values(...)`. The method is `_get_statement_values` → `AttributeError`. C = 0.

**Dimension D — Code Correctness: 10.0 / 25**
The extraction logic is correct — `statement["value"]["content"]` with proper `"value" in statement and "content" in statement["value"]` guard (fixes the `value.get('type') == 'value'` bug from mcp_skills run_5). But private method name and missing template/i18n files reduce score. D = 10.

**Total: 14.2** · Same core bug as mcp_skills run_5 (test file extra kills A) plus a new bug: private vs public method name.

---

### Task 6 — `5069b09e` · `db.py` transaction rollback restructure

**Gold files** (6): `openlibrary/core/db.py`, `openlibrary/core/booknotes.py`, `openlibrary/core/bookshelves.py`, `openlibrary/core/observations.py`, `openlibrary/core/ratings.py`, `openlibrary/plugins/admin/code.py`
**Model files**: `openlibrary/core/db.py` only
**Cost**: $1.12 · 738s · 26 API requests

**Dimension A — File Coverage: 4.2 / 25**
1/6 gold files hit, no extras. `raw = 1/6 × 25 = 4.17; A = 4.2`.

**Dimension B — Patch Completeness: 7.0 / 25**
Model completely restructures the `except (UniqueViolation, IntegrityError)` block in `db.py`:
- Adds `t_update.rollback()` unconditionally — PRESENT
- Only creates `t_delete` when `cls.ALLOW_DELETE_ON_CONFLICT` is True — PRESENT
- Removes the confusing `rows_deleted -= 1` pattern — PRESENT
- booknotes/bookshelves/observations/ratings/admin/code.py: MISSING (5 files)

Estimating 2 hunks for db.py (comprehensive fix) + 1 hunk each for 5 other files = 7 total hunks.
`(2×2 + 0) / (7×2) × 25 = 4/14 × 25 = 7.1` → B = 7.

**Dimension C — Test Coverage: 20.0 / 25**
1 fail-to-pass test. The test likely exercises the `CommonExtras.update_item` path in `db.py`. The model's comprehensive restructure correctly handles all three outcomes: (1) successful update, (2) unique violation with delete allowed, (3) unique violation with delete not allowed. The logic is sound. C = 20.

**Dimension D — Code Correctness: 15.0 / 25**
The `db.py` fix is the most complete of any run examined — cleaner conditional structure, correct row counter management. However, missing 5/6 gold files means the fix is incomplete for the full task. D = 15.

**Total: 46.2** · db.py fix is excellent (better than mcp_skills run_5's minimal rollback addition). The 5 missing secondary files limit overall score.

---

### Task 7 — `5c6c22f3` · IA publisher/place/ISBN parsing

**Gold files** (2): `openlibrary/plugins/importapi/code.py`, `openlibrary/plugins/upstream/utils.py`
**Model files**: both gold files + `tests/test_code.py` + `tests/test_utils.py` (2 extras)
**Cost**: $1.70 · 950s · 42 API requests

**Dimension A — File Coverage: 0.0 / 25**
Both gold files hit (2/2), but both test files are extras.
`raw = 2/2 × 25 = 25; deduction = min(2,2) × (25/2) = 25; A = 0.0`

**Dimension B — Patch Completeness: 25.0 / 25**
Model adds:
- `upstream/utils.py`: `get_isbn_10_and_13(isbns)` → splits by length (10/13) — PRESENT (correct name)
- `upstream/utils.py`: `get_publisher_and_place(publishers)` → splits on ` : ` — PRESENT (correct name)
- `importapi/code.py`: uses `get_isbn_10_and_13` to populate `isbn_10`/`isbn_13` — PRESENT
- `importapi/code.py`: uses `get_publisher_and_place` to populate `publishers`/`publish_places` — PRESENT

All 4 gold hunks present with correct function names. B = 25.

**Dimension C — Test Coverage: 20.0 / 25**
8 fail-to-pass tests. The model creates both functions with the exact names the gold tests import (`get_publisher_and_place`, `get_isbn_10_and_13`). The implementations handle edge cases (string vs list input, ISBN length differentiation, publisher/place splitting). The updated `test_code.py` confirms the expected API. Risk: model modifies test files which may conflict with the test_patch applied by SWE-bench harness. C = 20.

**Dimension D — Code Correctness: 20.0 / 25**
Both utility functions are well-implemented:
- `get_isbn_10_and_13`: handles str/list input, strips whitespace, length-based classification
- `get_publisher_and_place`: handles str/list input, splits on ` : `, preserves publishers without place

`importapi/code.py` correctly replaces the old simplistic publisher handling. Comprehensive test coverage. D = 20.

**Total: 65.0** · This is the best correctness result in the raw run. The task was prose-only in both baseline runs; the raw model produces a complete, well-named implementation. A=0 purely from test file inclusion.

---

### Task 8 — `8a5a63af` · monitoring haproxy_monitor.py

**Gold files** (5): `scripts/monitoring/monitor.py`, `scripts/monitoring/utils.py`, `compose.production.yaml`, `scripts/monitoring/haproxy_monitor.py` (new), `scripts/monitoring/requirements.txt`
**Model files**: all 5 gold files — no extras
**Cost**: $0.86 · 498s · 53 API requests

**Dimension A — File Coverage: 25.0 / 25**
All 5 gold files hit, no extras. `A = 5/5 × 25 = 25.0`.

**Dimension B — Patch Completeness: 20.0 / 25**
- `compose.production.yaml`: adds `network_mode: host` and restructures `cap_add` — PRESENT
- `haproxy_monitor.py` (new): creates full HAProxy stats scraper with `GraphiteEvent`, `HaproxyCapture`, `fetch_events`, async `main()` — PRESENT
- `monitor.py`: adds `monitor_haproxy` async job using `get_service_ip`, updates logging prefixes, converts to async main — PRESENT
- `requirements.txt`: adds `requests==2.32.2` — PRESENT
- `utils.py`: renames `OlBlockingScheduler` → `OlAsyncIOScheduler(AsyncIOScheduler)`, adds `get_service_ip` function — PRESENT but uncertain (rename may conflict with gold if gold keeps `OlBlockingScheduler`)

~4.5/5 hunks present → `(4×2 + 1×1)/(5×2) × 25 = 9/10 × 25 = 22.5` → B = 20 (conservative for class rename risk).

**Dimension C — Test Coverage: 15.0 / 25**
2 fail-to-pass tests. The model creates `haproxy_monitor.py` with full async monitoring logic. The `OlAsyncIOScheduler` class correctly wraps `AsyncIOScheduler` with job filtering. If the gold also renames the scheduler for async support, both tests pass. If the gold keeps `OlBlockingScheduler`, any test that imports it by name fails. Given the async architecture of the new haproxy code, the rename is likely correct. C = 15.

**Dimension D — Code Correctness: 17.0 / 25**
`haproxy_monitor.py` is a complete, well-structured async HAProxy stats collector — proper dataclass models, CSV parsing, Graphite serialization, aggregation support. The async conversion of `monitor.py` is clean. The scheduler rename (if correct) properly supports `async def` jobs. D = 17.

**Total: 77.0** · Highest score in this run. Major improvement vs mcp_skills run_5 (which got 11.0 by only creating a simplistic `OlBlockingScheduler` subclass). Raw model creates all 5 gold files with substantive content.

---

### Task 9 — `b4f7c185` · Solr updater return-type tuple

**Gold files** (2): `openlibrary/solr/update_work.py`, `openlibrary/solr/utils.py`
**Model files**: `openlibrary/solr/updater/author.py`, `openlibrary/solr/updater/work.py` (wrong paths)
**Cost**: $0.89 · 445s · 46 API requests

**Dimension A — File Coverage: 0.0 / 25**
Both files touched are `updater/` subdirectory files, not the gold `update_work.py` and `utils.py`.
`raw = 0/2 × 25 = 0; A = 0.0`.

**Dimension B — Patch Completeness: 6.3 / 25**
Model applies exactly the right fix (`return SolrUpdateRequest(adds=[doc]), []` and `return update, []`) — but in the wrong files. Gold requires changes to `openlibrary/solr/update_work.py` and `openlibrary/solr/utils.py`, not `updater/author.py` / `updater/work.py`. The logic is correct but the location is wrong.
`(1×1 + 0×2) / (2×2) × 25 ≈ 6.3` (partial for logic present in wrong file).

**Dimension C — Test Coverage: 0.0 / 25**
Gold files untouched. Tests import from `update_work.py`. Fail-to-pass tests will not see the fix. C = 0.

**Dimension D — Code Correctness: 12.0 / 25**
The change itself is exactly correct — the tuple return `(request, [])` is the right fix. But it's applied to non-existent/wrong files. D = 12.

**Total: 18.3** · Identical failure mode as mcp_skills run_5 — both runs target `updater/work.py` instead of `update_work.py`. The model confuses the refactored `updater/` module structure with the pre-refactoring `update_work.py`.

---

### Task 10 — `dbbd9d53` · lists.py seeds form-data parsing

**Gold files** (2): `openlibrary/plugins/openlibrary/lists.py`, `openlibrary/plugins/upstream/utils.py`
**Model files**: both gold files — no extras
**Cost**: $0.53 · 242s · 28 API requests

**Dimension A — File Coverage: 25.0 / 25**
Both gold files hit, no extras. `A = 2/2 × 25 = 25.0`.

**Dimension B — Patch Completeness: 18.8 / 25**
- `lists.py`: model does a full refactor of `from_input()`:
  - Adds explicit `DEFAULTS` dict — PRESENT
  - Adds JSON content-type branch — PRESENT (extra, not in gold, but not wrong)
  - Uses `parse_qs` for form data — PRESENT
  - BUT: applies `v[0]` to ALL fields including `seeds`, so multiple seeds submitted as separate form values would collapse to just the first — PARTIAL (core seeds-list fix is incomplete)
- `upstream/utils.py`: removes the "don't overwrite if key exists" guard in `setvalue` — PRESENT

Gold hunks: lists.py seeds fix (PARTIAL) + utils.py setvalue fix (PRESENT) + DEFAULTS dict (PRESENT).
`(2×2 + 1×1 + 1×0) / (3×2) × 25 = 5/6 × 25 ≈ 20.8` → B = 18.8 (conservative for seeds incompleteness).

**Dimension C — Test Coverage: 5.0 / 25**
1 fail-to-pass test. The test likely submits multiple seeds as separate form fields (`seeds=k1&seeds=k2`) and checks all are captured. The model's `v[0]` approach captures only the first seed — test fails for multi-seed case. The JSON input path and utils.py fix are both correct. C = 5.

**Dimension D — Code Correctness: 15.0 / 25**
The approach is broadly correct: `DEFAULTS` dict, `parse_qs` usage, switching from attribute access to dict access, utils.py guard removal. The seeds-as-list gap is the key correctness hole. The mcp_skills run_5 handled this with `k: (v if isinstance(DEFAULTS.get(k), list) else v[0])`. D = 15.

**Total: 63.8** · Both gold files hit (A=25 vs mcp_skills's A=12.5). But the seeds-list fix — which mcp_skills passed correctly — fails here. A classic quality/coverage trade-off.

---

## Key Failure Patterns

### 1. Test-file A penalty (5/10 tasks: 00bec1e7, 11838fad, 4a5d2a7d, 5c6c22f3, dbbd9d53 partially)
Five tasks get A=0 due to extra files:
- 00bec1e7: touches test files, no gold files hit
- 11838fad: test-data JSON fixtures are extras that cancel the parse.py hit  
- 4a5d2a7d: test_wikidata.py extra cancels the wikidata.py hit
- 5c6c22f3: two test files cancel two gold file hits  

The raw run adds test files even more systematically than the MCP+Skills run (which also had this issue).

### 2. Wrong-file targeting persists (b4f7c185)
The `updater/work.py` vs `update_work.py` confusion appears in both the raw and mcp_skills runs. Without the knowledge graph (MCP), the model cannot resolve which of the two structurally similar file paths is the current gold target.

### 3. Zero Pass@1 despite high B/D scores
The raw run achieves 0% Pass@1 despite average B=13.5 and D=14.7. Correctness gaps:
- **dbbd9d53**: seeds handled as `v[0]` instead of preserving the list
- **4a5d2a7d**: private method name `_get_statement_values` instead of `get_statement_values`
- **111347e9**: `decode_field` not fully removed; `marc_xml.py` still calls it
- **5c6c22f3**: likely test_patch conflict from model modifying test files

MCP+Skills run achieves Pass@1 on exactly the tasks where the raw run comes close but doesn't quite make it.

### 4. Multi-model overhead vs outcome
The raw run uses claude-haiku-4-5 as an orchestration subagent (57–91 API calls/task vs 12–31 for MCP+Skills). The extra compute produces more complete implementations and higher B/D scores, but doesn't fix the edge-case correctness issues that determine Pass@1.

### 5. 00bec1e7: completely different problem solved
The raw model implements LCCN-as-strong-identifier in `needs_isbn_and_lacks_one` — a valid enhancement — but the gold patch creates a `DifferentiableBook` class in `import_validator.py`. Without the MCP knowledge graph to read the issue description and related code, the model found a plausible-sounding change in a different file.

---

## Comparison Table: Raw vs MCP+Skills

| Instance | Raw total | MCP+Skills total | Delta | Winner |
|---|---|---|---|---|
| 00bec1e7 | 8.0 | 53.0 | -45.0 | MCP+Skills |
| 111347e9 | 63.0 | 0.0 | +63.0 | Raw |
| 11838fad | 53.0 | 32.5 | +20.5 | Raw |
| 25858f9f | 66.6 | 43.3 | +23.3 | Raw |
| 4a5d2a7d | 14.2 | 16.3 | -2.1 | MCP+Skills |
| 5069b09e | 46.2 | 14.4 | +31.8 | Raw |
| 5c6c22f3 | 65.0 | 12.3 | +52.7 | Raw |
| 8a5a63af | 77.0 | 11.0 | +66.0 | Raw |
| b4f7c185 | 18.3 | 15.6 | +2.7 | Raw |
| dbbd9d53 | 63.8 | 72.2 | -8.4 | MCP+Skills |
| **Mean** | **47.5** | **27.1** | **+20.4** | **Raw** |

**MCP+Skills wins on Pass@1 tasks** (00bec1e7 and dbbd9d53): the smaller, focused MCP+Skills diffs are more precise. **Raw wins on coverage tasks** (111347e9, 8a5a63af, 5c6c22f3): the raw run's higher compute budget lets it find and modify all gold files. The MCP knowledge graph helps precision; the multi-model raw setup helps coverage.
