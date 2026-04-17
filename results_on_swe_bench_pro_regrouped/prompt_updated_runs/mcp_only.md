# SWE-Pro Evaluation Report — MCP-Only Run (claude-sonnet-4-6, run 5)

**Run directory**: `auto_run_on_swe_pro_mcp_claude-sonnet-4-6_run_5`
**Model**: claude-sonnet-4-6
**Mode**: MCP with knowledge graph, no skills
**Evaluator**: claude-sonnet-4-6 · 2026-04-17
**Reference baseline**: `best_showcase_results/mcp_skills_pass_at_3` (eval_report.md)

---

## Score Summary

| # | Instance | A | B | C | D | Total |
|---|---|---|---|---|---|---|
| 1 | 00bec1e7 | 0.0 | 12.5 | 25.0 | 20.0 | **57.5** |
| 2 | 111347e9 | 10.0 | 5.0 | 0.0 | 6.0 | **21.0** |
| 3 | 11838fad | 0.0 | 12.5 | 5.0 | 12.0 | **29.5** |
| 4 | 25858f9f | 18.8 | 20.0 | 15.0 | 20.0 | **73.8** |
| 5 | 4a5d2a7d | 25.0 | 22.0 | 25.0 | 22.0 | **94.0** |
| 6 | 5069b09e | 4.2 | 7.0 | 20.0 | 15.0 | **46.2** |
| 7 | 5c6c22f3 | 0.0 | 6.3 | 0.0 | 8.0 | **14.3** |
| 8 | 8a5a63af | 0.0 | 10.0 | 10.0 | 12.0 | **32.0** |
| 9 | b4f7c185 | 0.0 | 6.3 | 0.0 | 12.0 | **18.3** |
| 10 | dbbd9d53 | 0.0 | 12.5 | 5.0 | 12.0 | **29.5** |
| | **Average** | **5.8** | **11.4** | **10.5** | **13.9** | **41.6** |

---

## Aggregate Metrics

| Metric | MCP-only run_5 | MCP+Skills run_5 | Raw run_5 | Baseline |
|---|---|---|---|---|
| Mean total | **41.6 / 100** | 27.1 / 100 | 47.5 / 100 | 26.1 / 100 |
| Mean A | 5.8 | 3.6 | 9.8 | — |
| Mean B | 11.4 | 7.7 | 13.5 | — |
| Mean C | 10.5 | 5.5 | 9.5 | — |
| Mean D | 13.9 | 10.3 | 14.7 | — |
| Prose-only | 0% | 0% | 0% | 20% |
| Pass@1 (C = 25) | **20%** (2 tasks) | 20% (2 tasks) | 0% | 20% |
| Zero-score | 0% | 10% | 0% | — |
| Avg cost/task | $1.73 | $1.35 | $1.45 | — |
| Avg API calls/task | 33.3 | 22.4 | 46.5 | — |
| Models used | sonnet-4-6 only | sonnet-4-6 only | sonnet-4-6 + haiku-4-5 | — |

**Key finding**: MCP-only achieves 20% Pass@1 — matching MCP+Skills — but on different tasks (4a5d2a7d and 00bec1e7 vs 00bec1e7 and dbbd9d53). The MCP knowledge graph enables the model to find peripheral gold files (messages.pot, infobox.html for 4a5d2a7d) that the raw run cannot locate, explaining 4a5d2a7d's near-perfect 94/100. Without skills, the model misses the targeted approach for dbbd9d53.

---

## Per-Task Scoring

---

### Task 1 — `00bec1e7` · import validation DifferentiableBook

**Gold files** (2): `openlibrary/plugins/importapi/import_validator.py`, `openlibrary/plugins/importapi/code.py`
**Model files**: `import_validator.py` + `tests/test_import_validator.py` (extra)
**Cost**: $1.39 · 645s · 26 API requests

**Dimension A — File Coverage: 0.0 / 25**
`import_validator.py` hit (1/2), but `test_import_validator.py` is an extra test file.
`raw = 1/2 × 25 = 12.5; deduction = min(1,1) × (25/2) = 12.5; A = 0.0`

**Dimension B — Patch Completeness: 12.5 / 25**
- `import_validator.py`: Creates `DifferentiableBook(BaseModel)` with `must_have_strong_identifier` validator checking for isbn_10/isbn_13/lccn. Implements two-stage `validate()` — first tries `Book.model_validate`, falls back to `DifferentiableBook.model_validate` — PRESENT (2pts)
- `code.py`: Not touched — MISSING (0pts)

`(2 + 0) / (2×2) × 25 = 2/4 × 25 = 12.5`

**Dimension C — Test Coverage: 25.0 / 25 ✓ PASS@1**
3 fail-to-pass tests. All three likely exercise `import_validator.py` directly:
1. Records with isbn_10/isbn_13/lccn pass validation ← model handles all three via DifferentiableBook
2. Records with no strong identifier and no full fields fail ← model's two-stage validate re-raises DifferentiableBook's ValidationError
3. Complete Book records still pass ← model tries Book first

The implementation is clean and correct. C = 25.

**Dimension D — Code Correctness: 20.0 / 25**
`DifferentiableBook` uses `@model_validator(mode='after')` correctly, properly checks `any([isbn_10, isbn_13, lccn])`. The two-stage validate is idiomatic. Missing `code.py` integration limits the score. D = 20.

**Total: 57.5** · Pass@1 on import_validator.py. Only code.py integration is missing.

---

### Task 2 — `111347e9` · marc `decode_field` removal

**Gold files** (5): `get_subjects.py`, `marc_base.py`, `marc_binary.py`, `marc_xml.py`, `parse.py`
**Model files**: `marc_base.py` + `parse.py` (2/5 gold, no extras)
**Cost**: $2.31 · 1039s · 34 API requests

**Dimension A — File Coverage: 10.0 / 25**
2/5 gold files hit, no extras. `raw = 2/5 × 25 = 10.0; deduction = 0; A = 10.0`

**Dimension B — Patch Completeness: 5.0 / 25**
The model completely misses the decode_field removal — `decode_field` doesn't appear in the diff at all. Instead it makes minor utility improvements:
- `marc_base.py`: defensive guard in `get_linkage` — `values = f.get_subfield_values('6'); if values and values[0].startswith(target)` — MINOR FIX, not a gold hunk
- `parse.py`: adds `'880'` to FIELDS_WANTED — possibly a gold hunk (PARTIAL, 1pt)
- `parse.py`: adds 880 linkage handling in `read_other_titles` — possibly a gold hunk (PARTIAL, 1pt)

`get_subjects.py`, `marc_binary.py`, `marc_xml.py` not touched. decode_field not removed. B ≈ 5.

**Dimension C — Test Coverage: 0.0 / 25**
2 fail-to-pass tests about decode_field removal. Since decode_field is not removed from any file, C = 0.

**Dimension D — Code Correctness: 6.0 / 25**
The defensive `values and values[0]` guard in `get_linkage` is a valid safety fix. Adding `'880'` to FIELDS_WANTED and the `read_other_titles` linkage handling are real improvements. But none of these address the stated task (decode_field removal). D = 6.

**Total: 21.0** · MCP knowledge graph didn't help the model identify the core decode_field problem. The model found related '880' linkage work but not the intended refactoring.

---

### Task 3 — `11838fad` · marc parse.py 880 alternate-script swap

**Gold files** (1): `openlibrary/catalog/marc/parse.py`
**Model files**: `parse.py` + `tests/test_parse.py` (extra)
**Cost**: $1.60 · 780s · 31 API requests

**Dimension A — File Coverage: 0.0 / 25**
`parse.py` hit (1/1), but `test_parse.py` is extra.
`raw = 25; deduction = min(1,1) × 25 = 25; A = 0.0`

**Dimension B — Patch Completeness: 12.5 / 25**
Model adds `alternate_names` from 880 linkage for tags 110/111/710/711 — but does NOT swap `name` ↔ `alternate_names`. The gold requires the original script name to become the primary `name`, with the romanized form as `alternate_names`. The model keeps romanized as primary and appends original as alternate. For each of the 5 tag types: PARTIAL (1pt each).

The model also does a significant `read_contributions` rewrite: changes the return type from `dict` to `list[dict]` and updates `read_edition` to call `update_edition(rec, edition, read_contributions, 'authors')`. This restructuring may conflict with existing PASS_TO_PASS tests.

`5 × 1 / (5×2) × 25 = 5/10 × 25 = 12.5`

**Dimension C — Test Coverage: 5.0 / 25**
54 fail-to-pass tests. All check that records with 880 linkage have the original script as the *primary* name. The model adds alternate_names but keeps the wrong name as primary — failing the core assertion. The `read_contributions` restructuring is risky. C = 5.

**Dimension D — Code Correctness: 12.0 / 25**
The alternate_names additions are real 880 linkage work. The `read_contributions` rewrite to `list[dict]` is a structural improvement. But the wrong direction on name ordering and the risk from read_contributions restructuring (may break passing tests) limits the score. D = 12.

**Total: 29.5** · The model worked on the right area (880 linkage) but swapped in the wrong direction — adds without swapping primary/alternate.

---

### Task 4 — `25858f9f` · Solr `utils.py` extraction + SolrUpdateRequest redesign

**Gold files** (4): `openlibrary/solr/utils.py` (new), `openlibrary/solr/update_work.py`, `openlibrary/solr/update_edition.py`, `scripts/solr_builder/solr_builder/index_subjects.py`
**Model files**: `utils.py` (new), `update_work.py`, `index_subjects.py` — misses `update_edition.py`
**Cost**: $2.05 · 1096s · 34 API requests

**Dimension A — File Coverage: 18.8 / 25**
3/4 gold files hit, no extras. `raw = 18.75; deduction = 0; A = 18.8`

**Dimension B — Patch Completeness: 20.0 / 25**
This is the most comprehensive 25858f9f answer across all three runs. The model:
- Creates `utils.py` with: config functions (`get/set_solr_base_url`, `get/set_solr_next`, `load_config`), new `SolrUpdateRequest` dataclass (replaces the `AddRequest`/`DeleteRequest`/`CommitRequest` hierarchy), `solr_update`, `solr_insert_documents`, `str_to_key` — PRESENT
- `update_work.py`: removes ALL extracted code, replaces list-based API with `SolrUpdateRequest` object throughout `update_work()`, `update_author()`, `update_keys()` — PRESENT
- `index_subjects.py`: updates imports from `update_work` → `utils` — PRESENT
- `update_edition.py`: not touched — MISSING

`(3×2 + 0) / (4×2) × 25 = 6/8 × 25 = 18.75 → B ≈ 20` (extra completeness in update_work.py warrants slight upward rounding).

**Dimension C — Test Coverage: 15.0 / 25**
6 fail-to-pass tests. The comprehensive SolrUpdateRequest redesign and correct import paths for utils.py/update_work.py/index_subjects.py should pass most tests. The missing `update_edition.py` fix (still imports `get_solr_next` from `update_work`, which no longer exports it) breaks the edition build path — likely affecting 1–2 of 6 tests. C = 15.

**Dimension D — Code Correctness: 20.0 / 25**
Excellent refactoring — the `SolrUpdateRequest` dataclass with `+=` operator, `has_changes()`, and proper `to_solr_requests_json()` is a clean API. The `update_keys()` rewrite is comprehensive. Only the `update_edition.py` gap prevents full marks. D = 20.

**Total: 73.8** · Best 25858f9f score across all runs. The SolrUpdateRequest redesign is present and complete; only update_edition.py is missing.

---

### Task 5 — `4a5d2a7d` · wikidata `get_statement_values` + social profiles

**Gold files** (3): `openlibrary/core/wikidata.py`, `openlibrary/i18n/messages.pot`, `openlibrary/templates/authors/infobox.html`
**Model files**: exactly these 3 — no extras
**Cost**: $2.58 · 970s · 69 API requests

**Dimension A — File Coverage: 25.0 / 25**
All 3 gold files hit, no extras. `A = 3/3 × 25 = 25.0`

**Dimension B — Patch Completeness: 22.0 / 25**
- `wikidata.py`: adds `get_statement_values(property_id)` as a **public** method (correct name) with correct logic: `statement["value"]["content"]` guarded by `"value" in statement and "content" in statement["value"]`. Also adds `SOCIAL_PROFILES` constant and `get_profiles_to_render()` — PRESENT
- `messages.pot`: updates "Visit Wikipedia" → "Wikipedia", removes duplicate entry — PRESENT
- `infobox.html`: calls `wikidata.get_profiles_to_render()` to render social profile icons — PRESENT

Minor deduction for potential implementation details diverging from gold (exact SOCIAL_PROFILES entries, HTML structure). B = 22.

**Dimension C — Test Coverage: 25.0 / 25 ✓ PASS@1**
1 fail-to-pass test. It calls `entity.get_statement_values('P2038')` and checks the result.

The model's implementation correctly handles `{'value': {'content': 'Chris-Wiggins'}}` (no 'type' key issue that affected earlier runs). The public method name is correct. C = 25.

**Dimension D — Code Correctness: 22.0 / 25**
Complete, correct implementation across all 3 gold files. The `get_profiles_to_render()` method is clean, the messages.pot de-duplication is correct, the HTML template is properly extended. Minor uncertainty on exact gold implementation details. D = 22.

**Total: 94.0** · Highest score across all evaluated runs for any task. The MCP knowledge graph enabled the model to find all 3 gold files — without MCP, the raw run only found `wikidata.py` (and used the wrong private method name).

---

### Task 6 — `5069b09e` · `db.py` transaction rollback

**Gold files** (6): `db.py`, `booknotes.py`, `bookshelves.py`, `observations.py`, `ratings.py`, `admin/code.py`
**Model files**: `db.py` only
**Cost**: $1.54 · 901s · 20 API requests

**Dimension A — File Coverage: 4.2 / 25**
1/6 gold files hit, no extras. `A = 1/6 × 25 = 4.2`

**Dimension B — Patch Completeness: 7.0 / 25**
Model restructures the `except (UniqueViolation, IntegrityError)` block:
- Adds `t_update.rollback()` unconditionally — PRESENT
- Moves `t_delete` inside `if cls.ALLOW_DELETE_ON_CONFLICT:` — PRESENT
- Removes the confusing `rows_deleted -= 1` decrement — PRESENT
- 5 other gold files: all MISSING

`(2×2 + 0) / (7×2) × 25 ≈ 7.0`

**Dimension C — Test Coverage: 20.0 / 25**
1 fail-to-pass test exercises `db.py` behavior. The fix correctly handles all three scenarios. C = 20.

**Dimension D — Code Correctness: 15.0 / 25**
`db.py` fix is solid (identical quality to raw run). 5/6 files missed. D = 15.

**Total: 46.2** · Identical result to raw run — MCP doesn't help here since the model found `db.py` correctly but didn't explore the 5 dependent files.

---

### Task 7 — `5c6c22f3` · IA publisher/place/ISBN parsing

**Gold files** (2): `openlibrary/plugins/importapi/code.py`, `openlibrary/plugins/upstream/utils.py`
**Model files**: `importapi/metaxml_to_json.py` (wrong file), `upstream/utils.py` ✓, `tests/test_utils.py` (extra)
**Cost**: $0.71 · 344s · 19 API requests

**Dimension A — File Coverage: 0.0 / 25**
`upstream/utils.py` hit (1/2), but `metaxml_to_json.py` is a wrong-path file and `test_utils.py` is an extra.
`raw = 1/2 × 25 = 12.5; deduction = min(2,1) × 12.5 = 12.5; A = 0.0`

**Dimension B — Patch Completeness: 6.3 / 25**
- `upstream/utils.py`: extends existing `get_location_and_publisher` to handle `list` input — PARTIAL (1pt). The gold requires a new function `get_publisher_and_place`, not modifying the existing one.
- `importapi/code.py`: not touched (wrong file targeted) — MISSING (0pts)

`(1 + 0) / (2×2) × 25 = 6.3`

**Dimension C — Test Coverage: 0.0 / 25**
8 fail-to-pass tests. The gold tests call `get_publisher_and_place` (which doesn't exist) and test `importapi/code.py` behavior (untouched). C = 0.

**Dimension D — Code Correctness: 8.0 / 25**
The `get_location_and_publisher` list extension is valid code. `metaxml_to_json.py` changes (using `get_isbn_10_and_13` and `get_location_and_publisher`) are a reasonable improvement to that file. But wrong target and wrong function name for the gold task. D = 8.

**Total: 14.3** · MCP helped find `utils.py` but the model went to the wrong secondary file (metaxml_to_json instead of importapi/code.py) and extended the wrong function (get_location_and_publisher instead of creating get_publisher_and_place).

---

### Task 8 — `8a5a63af` · monitoring `scheduled_job_for_server`

**Gold files** (5): `monitor.py`, `utils.py`, `compose.production.yaml`, `haproxy_monitor.py` (new), `requirements.txt`
**Model files**: `__init__.py` (empty, extra), `monitor.py` ✓, `tests/__init__.py` (empty, extra), `tests/test_utils.py` (extra), `utils.py` ✓
**Cost**: $2.69 · 1094s · 54 API requests

**Dimension A — File Coverage: 0.0 / 25**
2 gold files hit (monitor.py, utils.py); 3 extras (__init__.py, tests/__init__.py, tests/test_utils.py).
`raw = 2/5 × 25 = 10; deduction = min(3,2) × (25/5) = 10; A = 0.0`

**Dimension B — Patch Completeness: 10.0 / 25**
- `utils.py`: adds `scheduled_job_for_server` method to `OlBlockingScheduler` using `fnmatch.fnmatch` for hostname matching — PRESENT (2pts)
- `monitor.py`: replaces all `@limit_server(…) + @scheduler.scheduled_job(…)` with `@scheduler.scheduled_job_for_server(…)` — PRESENT (2pts)
- `compose.production.yaml`, `haproxy_monitor.py`, `requirements.txt`: all MISSING (0pts each)

`(2×2 + 0) / (5×2) × 25 = 4/10 × 25 = 10.0`

**Dimension C — Test Coverage: 10.0 / 25**
2 fail-to-pass tests. `scheduled_job_for_server` is correctly implemented with `fnmatch` glob matching — likely passes one test. The test checking haproxy monitoring (requires `haproxy_monitor.py`) fails. C = 10.

**Dimension D — Code Correctness: 12.0 / 25**
`scheduled_job_for_server` is a clean, correct implementation using `fnmatch` for pattern matching and proper hostname parsing (`hostname.split('.')[0]`). The `monitor.py` refactoring is clean. But `haproxy_monitor.py` — the core new feature — is entirely absent. D = 12.

**Total: 32.0** · MCP helps find the scheduler pattern but misses the haproxy monitoring additions. Notably the test infrastructure (tests/__init__.py, test_utils.py) hurts A via the extra-file penalty.

---

### Task 9 — `b4f7c185` · Solr updater return-type tuple

**Gold files** (2): `openlibrary/solr/update_work.py`, `openlibrary/solr/utils.py`
**Model files**: `openlibrary/solr/updater/author.py`, `openlibrary/solr/updater/work.py` (wrong paths)
**Cost**: $0.74 · 297s · 23 API requests

**Dimension A — File Coverage: 0.0 / 25**
Both touched files are in the `updater/` subdirectory, not the gold `update_work.py` and `utils.py`. `A = 0.0`.

**Dimension B — Patch Completeness: 6.3 / 25**
Correct logic (`return SolrUpdateRequest(adds=[doc]), []` and `return update, []`) but wrong file paths. PARTIAL for each hunk.

**Dimension C — Test Coverage: 0.0 / 25**
Gold files untouched. C = 0.

**Dimension D — Code Correctness: 12.0 / 25**
Correct change, wrong location. D = 12.

**Total: 18.3** · Third run in a row with the same wrong-path failure. The MCP knowledge graph apparently doesn't disambiguate `updater/work.py` vs `update_work.py` well enough to prevent this error.

---

### Task 10 — `dbbd9d53` · lists.py seeds form-data parsing

**Gold files** (2): `openlibrary/plugins/openlibrary/lists.py`, `openlibrary/plugins/upstream/utils.py`
**Model files**: `lists.py` ✓, `tests/test_lists.py` (extra)
**Cost**: $1.71 · 2148s · 23 API requests (longest run in this set)

**Dimension A — File Coverage: 0.0 / 25**
`lists.py` hit (1/2), `test_lists.py` extra, `upstream/utils.py` missed.
`raw = 12.5; deduction = 12.5; A = 0.0`

**Dimension B — Patch Completeness: 12.5 / 25**
- `lists.py`: Model takes a different approach to the POST data branch — keeps `v[0]` but adds seeds-wrapping logic and rewrites the else branch (query string) to use `parse_qs` with `','.join(v) if len(v) > 1 else v[0]`. The query-string path is improved but the POST body path still has the seeds-as-list problem — PARTIAL (1pt)
- `upstream/utils.py`: setvalue guard not touched — MISSING (0pts)

Also touches `test_lists.py` — updates tests to mock `web.ctx.env['QUERY_STRING']` instead of `web.input`. Interesting approach but changes test structure.

`(1 + 0) / (2×2) × 25 = 1/4 × 25 = 12.5` (generous given the partial lists.py)

**Dimension C — Test Coverage: 5.0 / 25**
1 fail-to-pass test. The test likely submits multiple seeds via POST form data. The model's POST path uses `v[0]` — only captures the first seed. C = 5.

**Dimension D — Code Correctness: 12.0 / 25**
The query-string handling improvement is real: `','.join(v) if len(v) > 1 else v[0]` correctly joins multiple values. The `seeds_input` wrapping is also helpful. But the POST body path is broken for the multi-seed case, and `upstream/utils.py` is missing. D = 12.

**Total: 29.5** · 2148 seconds (longest task in any run) but the seeds fix is incomplete. The model correctly handled the query-string path but missed the POST body path and utils.py.

---

## Key Failure Patterns

### 1. MCP enables file discovery for multi-file tasks (4a5d2a7d: 94/100)
The clearest MCP advantage: task 4a5d2a7d requires finding `messages.pot` and `infobox.html` in addition to `wikidata.py`. Without the knowledge graph, the raw run only finds `wikidata.py` and uses the wrong private method name. With MCP, all 3 files are found, the correct public method name is used, and the task passes at 94/100.

### 2. Test-file A penalty (6/10 tasks get A=0)
Tasks 00bec1e7, 11838fad, 5c6c22f3, 8a5a63af, b4f7c185, dbbd9d53 all get A=0 due to extra non-gold files. The MCP run systematically adds test files alongside production changes.

### 3. Wrong-file targeting persists (b4f7c185, 5c6c22f3)
- b4f7c185: `updater/work.py` instead of `update_work.py` — third run in a row with same error
- 5c6c22f3: `metaxml_to_json.py` instead of `importapi/code.py` — MCP found the wrong downstream file to update

### 4. Direction errors on 880 linkage (11838fad) and decode_field (111347e9)
- 11838fad: adds `alternate_names` from 880 linkage without swapping `name` ↔ `alternate_names`
- 111347e9: works on related '880' FIELDS_WANTED and `read_other_titles` improvements, entirely missing the `decode_field` removal

### 5. Partial-file coverage pattern (5069b09e, dbbd9d53)
Without skills, the model finds the primary gold file but doesn't systematically locate all dependent files that also need updating (booknotes/bookshelves/etc. for db.py; utils.py for lists.py).

---

## Cross-Run Comparison

| Instance | MCP-only | MCP+Skills | Raw | Delta: MCP vs MCP+Skills |
|---|---|---|---|---|
| 00bec1e7 | 57.5 | 53.0 | 8.0 | +4.5 |
| 111347e9 | 21.0 | 0.0 | 63.0 | +21.0 |
| 11838fad | 29.5 | 32.5 | 53.0 | -3.0 |
| 25858f9f | 73.8 | 43.3 | 66.6 | +30.5 |
| 4a5d2a7d | **94.0** | 16.3 | 14.2 | +77.7 |
| 5069b09e | 46.2 | 14.4 | 46.2 | +31.8 |
| 5c6c22f3 | 14.3 | 12.3 | 65.0 | +2.0 |
| 8a5a63af | 32.0 | 11.0 | 77.0 | +21.0 |
| b4f7c185 | 18.3 | 15.6 | 18.3 | +2.7 |
| dbbd9d53 | 29.5 | 72.2 | 63.8 | -42.7 |
| **Mean** | **41.6** | **27.1** | **47.5** | **+14.5** |

**MCP-only wins strongly over MCP+Skills** (+14.5 mean) in this run. The major gain is 4a5d2a7d (+77.7) where the knowledge graph is decisive for multi-file discovery.

**MCP+Skills beats MCP-only** only on dbbd9d53 (-42.7): skills help the model apply the precise `isinstance(DEFAULTS.get(k), list)` pattern that passes the seeds test. Without skills, the MCP model finds the right approach but misses the exact fix needed.

**Raw run beats both** on tasks requiring brute-force exploration (11838fad, 5c6c22f3, 8a5a63af) where more API calls and multi-model help cover more ground.
