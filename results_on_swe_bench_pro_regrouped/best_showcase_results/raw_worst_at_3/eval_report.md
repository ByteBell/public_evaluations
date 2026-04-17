# Evaluation Report: raw_worst_at_3

**Rubric**: 4-dimension scoring (A=File Coverage 25, B=Patch Completeness 25, C=Test Coverage 25, D=Code Correctness 25), max 100  
**Repo**: internetarchive/openlibrary (all 10 tasks)  
**Condition**: Raw Claude Code (no MCP), Worst-of-3 runs selected

---

## Score Summary

| # | Short ID | Task | A | B | C | D | **Total** |
|---|----------|------|---|---|---|---|-----------|
| 1 | 00bec1e7 | import_validator two-stage validation | 0.0 | 14.6 | 12.5 | 12.0 | **39.1** |
| 2 | 111347e9 | MARC catalog subjects refactor | 0.0 | 4.2 | 0.0 | 3.0 | **7.2** |
| 3 | 11838fad | MARC parse.py author fixes | 0.0 | 14.1 | 6.0 | 12.0 | **32.1** |
| 4 | 25858f9f | Solr utils.py extraction | 18.8 | 10.0 | 3.0 | 10.0 | **41.8** |
| 5 | 4a5d2a7d | wikidata get_statement_values | 0.0 | 10.4 | 0.0 | 6.0 | **16.4** |
| 6 | 5069b09e | db.py ALLOW_DELETE_ON_CONFLICT | 4.2 | 4.2 | 0.0 | 6.0 | **14.4** |
| 7 | 5c6c22f3 | importapi IA record helpers | 0.0 | 4.2 | 0.0 | 6.0 | **10.2** |
| 8 | 8a5a63af | monitoring OlBlockingScheduler rename | 5.0 | 11.1 | 0.0 | 12.0 | **28.1** |
| 9 | b4f7c185 | Solr update_key tuple return | 25.0 | 25.0 | 25.0 | 25.0 | **100.0** |
| 10 | dbbd9d53 | ListRecord.from_input seeds parsing | 0.0 | 4.2 | 0.0 | 6.0 | **10.2** |
| — | **Avg** | | **5.3** | **10.2** | **4.7** | **9.8** | **30.0** |

---

## Aggregate Metrics

| Metric | Value |
|--------|-------|
| Mean total score | 30.0 / 100 |
| Mean A (File Coverage) | 5.3 / 25 |
| Mean B (Patch Completeness) | 10.2 / 25 |
| Mean C (Test Coverage) | 4.7 / 25 |
| Mean D (Code Correctness) | 9.8 / 25 |
| Full patch rate (score ≥ 90) | 10% (1/10) |
| Partial patch rate (0 < score < 90) | 90% (9/10) |
| Zero-score rate | 0% (0/10) |
| Prose-only answers | 0% (0/10) |
| Pass@1 equivalent (C = 25) | 10% (1/10) |

---

## Per-Task Scoring Sheets

---

### Task 1 — `00bec1e7` | import_validator two-stage validation
**Score: 39.1/100** (A=0, B=14.6, C=12.5, D=12)

**Task**: Add `CompleteBookPlus` (renamed `Book`) + `StrongIdentifierBookPlus` classes to support validating records with strong identifiers (ISBN-10/13, LCCN) as an alternative to full bibliographic completeness.

**Dimension A — 0/25**: Model touches `import_validator.py` (file hit, 1/2 gold) but ALSO modifies `openlibrary/catalog/add_book/__init__.py` (spurious, adds SUSPECT_DATE constants) and `openlibrary/plugins/importapi/tests/test_import_validator.py` (spurious). Extra penalty: 1/2×25 − 2×(25/2) = 12.5 − 25 = **0** (clamped).

**Dimension B — 14.6/25**: Gold has ~6 hunks (5 import_validator.py + 1 code.py).
- Imports (add `Final`, `model_validator`): **Partial** (model adds `Final` ✓, `model_validator` ✓, but also adds `root_validator` and spurious `add_book` imports)
- `STRONG_IDENTIFIERS: Final = {"isbn_10", "isbn_13", "lccn"}`: **Present** (exact match ✓)
- Rename `Book` → `CompleteBookPlus`: **Partial** (model renames to `CompleteBook`, omits "Plus" suffix)
- Add `StrongIdentifierBookPlus` class with `model_validator`: **Partial** (model adds a similar class but uses Pydantic v1 `root_validator`)
- Rewrite `validate()` with two-stage logic: **Present** ✓
- code.py variable renames: **Missing**
Score: (1+2+1+1+2+0)/(6×2) × 25 = 7/12 × 25 = **14.6**

**Dimension C — 12.5/25**: The model adds two extra `@root_validator(pre=True)` validators to `CompleteBook` that filter out "suspect" dates and authors. These validators don't affect the fail_to_pass test data (which uses valid dates/authors). The `StrongIdentifierBookPlus`-equivalent class covers the isbn_10/13/lccn fields. Two-stage validate() is present. Pydantic v2 supports `root_validator` with deprecation warnings in compatibility mode, so validation likely functions. Tests have a reasonable probability of passing. Score: **12.5** (estimated; uncertain due to Pydantic v1/v2 compatibility)

**Dimension D — 12/25**: Extra `root_validators` add unintended complexity. Wrong class name suffix (`CompleteBook` vs `CompleteBookPlus`). Spurious imports from `add_book/__init__.py` create unnecessary coupling. Core logic correct. Score: **12**

---

### Task 2 — `111347e9` | MARC catalog subjects refactor
**Score: 7.2/100** (A=0, B=4.2, C=0, D=3)

**Task**: Refactor MARC subjects and language handling across 5 files (get_subjects.py, marc_base.py, marc_binary.py, marc_xml.py, parse.py).

**Dimension A — 0/25**: Model hits parse.py (1/5) but creates 56 extra JSON test fixture files + test_parse.py → formula: 1/5×25 − 56×(25/5) = 5 − 280 → clamped to **0**.

**Dimension B — 4.2/25**: Gold modifies 5 files. Model only modifies parse.py with: language map updates (adding deprecated code mappings like `cam→khm`, `esp→epo`, etc.), import reorganization, adds `logger`. The parse.py language-map changes are partially relevant to gold changes. All other files missed. B: **4.2**

**Dimension C — 0/25**: Gold requires changes across 4 missed files. Model also modifies 56 JSON test fixture files — these fixtures conflict with the gold test expectations (gold's test_patch uses gold fixtures, not model's modified ones). Score: **0**

**Dimension D — 3/25**: Language map additions are partly correct but incomplete. Approach of modifying test fixture files (instead of fixing logic) is wrong. Score: **3**

---

### Task 3 — `11838fad` | MARC parse.py author fixes
**Score: 32.1/100** (A=0, B=14.1, C=6, D=12)

**Task**: Fix `read_author_person` (role trailing dot, personal_name dedup, return type) and `read_authors` (880 linkage for 110/111 fields) in parse.py. 54 FAIL_TO_PASS tests.

**Dimension A — 0/25**: Model hits parse.py (1/1 gold file) but creates 57 extra JSON test fixture files + test_parse.py → formula: 1/1×25 − min(57,1)×25 = 25 − 25 = **0**.

**Dimension B — 14.1/25**: Gold has ~8 hunks in parse.py.
- `name_from_list` signature (`strip_trailing_dot` param): **Missing** (model uses different approach)
- `read_author_person` return type `dict[str, Any]`: **Missing**
- Return `{}` instead of `None` for missing 'a'/'c': **Missing**
- Role handling (preserve trailing period): **Partial** (model handles 'e' separately; gold uses `strip_trailing_dot=False`)
- `personal_name` dedup (remove if equals `name`): **Present** ✓
- Remove `count = 0` from `read_authors`: **Present** ✓
- 880 linkage for 110 fields (alternate_names): **Present** ✓
- 880 linkage for 111 fields (alternate_names): **Present** ✓
Score: (0+0+0+1+2+2+2+2)/(8×2) × 25 = 9/16 × 25 = **14.1**

**Dimension C — 6/25**: Model's parse.py changes are real and applicable (actual git diff, not prose). The 880 linkage improvements directly address many of the 54 alternate-script tests (`880_arabic_french`, `880_Nihon_no_chasho`, etc.). Role and personal_name fixes address other tests. However, the model also modifies 57 JSON fixtures, which conflict with gold test data — significantly limiting which tests pass cleanly. Score: **6** (some tests pass via legitimate code changes)

**Dimension D — 12/25**: Real applicable diff with correct logic for personal_name dedup and 880 linkage. Different (but reasonable) approach to role handling. Missing the return type annotation change and `name_from_list` parameter approach. Score: **12**

---

### Task 4 — `25858f9f` | Solr utils.py extraction
**Score: 41.8/100** (A=18.8, B=10, C=3, D=10)

**Task**: Extract utility functions (`get_solr_base_url`, `solr_update`, `SolrUpdateState`, etc.) from `update_work.py` into a new `utils.py`. Update imports in `update_edition.py`, `update_work.py`, `index_subjects.py`. Tests in `TestSolrUpdate` move to new `test_utils.py`.

**Dimension A — 18.8/25**: Model hits 3/4 gold files (`utils.py` new, `update_work.py`, `index_subjects.py`). Misses `update_edition.py`. No extra files. Formula: 3/4×25 = **18.8**

**Dimension B — 10/25**: Gold creates utils.py with shared utilities + modifies 3 other files.
- `utils.py` creation: **Partial** — model creates it from scratch with similar content (`get_solr_base_url`, `set_solr_base_url`, `get_solr_next`, `solr_update`, helper classes) but uses `SolrUpdateRequest` instead of gold's `SolrUpdateState` for the main update class, and content differs in structure
- `update_work.py` refactor (remove moved functions, add imports): **Partial**
- `index_subjects.py` (import changes): **Partial**
- `update_edition.py`: **Missing**
Score: **10.0**

**Dimension C — 3/25**: The 6 fail_to_pass tests are in `TestSolrUpdate` (moved to new `test_utils.py`). They test retry behavior via `mock_post.call_count`. The model's `solr_update()` includes retry logic (`make_request()` inner function), but the tested class name (`SolrUpdateState` in tests vs `SolrUpdateRequest` in model) causes `ImportError` for some test imports. `test_successful_response` might pass if `solr_update` is importable; retry tests likely fail. Score: **3**

**Dimension D — 10/25**: Model creates substantial, plausible utils.py content. Wrong class name (`SolrUpdateRequest` vs `SolrUpdateState`). Partial retry logic implementation. Score: **10**

---

### Task 5 — `4a5d2a7d` | wikidata get_statement_values
**Score: 16.4/100** (A=0, B=10.4, C=0, D=6)

**Task**: Add public `get_statement_values(property_id)` to `WikidataEntity`, add `SOCIAL_PROFILES` constant (5 entries), add `get_profiles_to_render()`, update `infobox.html` and `messages.pot`.

**Dimension A — 0/25**: Model hits wikidata.py (1/3 gold files) but adds extra `test_wikidata.py` → formula: 1/3×25 − min(1,1)×(25/3) = 8.3 − 8.3 = **0**.

**Dimension B — 10.4/25**: 
- Fix `statements` type annotation (`dict[str, dict]` → `dict[str, list[dict]]`): **Present** ✓
- `SOCIAL_PROFILES` constant with 5 entries: **Partial** (model adds `SOCIAL_PROFILE_CONFIGS` with only 1 entry: Google Scholar)
- `get_statement_values()` public method: **Partial** (model adds `_get_statement_values()` private — underscore prefix mismatch)
- `get_profiles_to_render()`: **Partial** (model adds `get_external_profiles()` with different approach including `_get_wiki_profiles()`)
- `messages.pot` updates: **Missing**
- `infobox.html` changes: **Missing**
Score: (2+1+1+1+0+0)/(6×2) × 25 = 5/12 × 25 = **10.4**

**Dimension C — 0/25**: Test calls `entity.get_statement_values('P2038')` (public, no underscore). Model implements `_get_statement_values` (private) → `AttributeError`. Score: **0**

**Dimension D — 6/25**: Incomplete SOCIAL_PROFILE_CONFIGS (1 of 5 entries). Private vs public method name. Otherwise correct logic structure. Score: **6**

---

### Task 6 — `5069b09e` | db.py ALLOW_DELETE_ON_CONFLICT
**Score: 14.4/100** (A=4.2, B=4.2, C=0, D=6)

**Task**: Add `ALLOW_DELETE_ON_CONFLICT` flag to 4 model classes, add `t_update.rollback()`, add `failed_deletes` counter, return dict from `update_work_id`.

**Dimension A — 4.2/25**: Model hits db.py (1/6 gold files). No extra files. Formula: 1/6×25 = **4.2**

**Dimension B — 4.2/25**: The model's diff targets code that ALREADY includes `ALLOW_DELETE_ON_CONFLICT` logic (hallucinated codebase state) — it removes gold-added code and replaces with a cleaner version. The diff cannot be applied to the original code (lines being removed don't exist there). The conceptual fix (add `t_update.rollback()`, make delete conditional on `cls.ALLOW_DELETE_ON_CONFLICT`) partially overlaps with gold's db.py changes. Missing all 5 other files. Score: **4.2**

**Dimension C — 0/25**: Diff targets non-existent lines in the original codebase → fails to apply → no tests pass. Score: **0**

**Dimension D — 6/25**: Conceptually correct db.py logic, but applied to wrong starting state. Missing ALLOW_DELETE_ON_CONFLICT attribute definitions on Booknotes/Bookshelves/etc. Score: **6**

---

### Task 7 — `5c6c22f3` | importapi IA record helpers
**Score: 10.2/100** (A=0, B=4.2, C=0, D=6)

**Task**: Extract `get_isbn_10_and_13()` and `get_publisher_and_place()` to `upstream/utils.py`; refactor `get_ia_record()` in `importapi/code.py` to use them; handle list-type publisher metadata.

**Dimension A — 0/25**: Model hits `upstream/utils.py` (1/2 gold) but adds `test_utils.py` as spurious extra → formula: 1/2×25 − 12.5 = **0**.

**Dimension B — 4.2/25**: Gold primarily modifies code.py (main import/refactor) + utils.py. Model only modifies utils.py (adds list handling to `get_location_and_publisher`) and test_utils.py (spurious change). Model misses adding `get_isbn_10_and_13()` and `get_publisher_and_place()` to utils.py, and misses all code.py changes. B: **4.2**

**Dimension C — 0/25**: All 4 `test_get_ia_record_*` tests require code.py changes (not made). `test_get_isbn_10_and_13` requires a new function (not added). Model also modifies test_utils.py (changes test expectations), conflicting with gold test application. Score: **0**

**Dimension D — 6/25**: List handling for `get_location_and_publisher` is a legitimate and correct addition, but addresses only a small part of the required changes. Score: **6**

---

### Task 8 — `8a5a63af` | monitoring OlBlockingScheduler rename
**Score: 28.1/100** (A=5.0, B=11.1, C=0, D=12)

**Task**: Rename `OlBlockingScheduler` → `OlAsyncIOScheduler` (switch from BlockingScheduler to AsyncIOScheduler), add `get_service_ip()` to utils.py, create `haproxy_monitor.py`, update `monitor.py`, add `requests` to requirements.

**Dimension A — 5.0/25**: Model hits `scripts/monitoring/utils.py` (1/5 gold files). No extra files. Formula: 1/5×25 = **5.0**

**Dimension B — 11.1/25**: Model creates a new-file diff for utils.py (treating it as new rather than a modification). Content is substantially correct:
- `from apscheduler.schedulers.asyncio import AsyncIOScheduler`: **Present** ✓
- `class OlAsyncIOScheduler(AsyncIOScheduler)`: **Present** ✓ (correct class name!)
- `[OL-MONITOR]` prefix in `job_listener`: **Present** ✓
- `limit_server` with `AsyncIOScheduler` type: **Present** ✓
- `get_service_ip()` function: **Missing**
- compose.production.yaml, haproxy_monitor.py, monitor.py, requirements.txt: **Missing**
Score: 4 present / 9 total hunks → (4×2)/(9×2) × 25 = **11.1**

**Dimension C — 0/25**: The model's diff uses `new file mode` (`--- /dev/null`) for an existing file. `git apply` would fail when the file already exists at that path (cannot create a new file over an existing one without force). With the original `OlBlockingScheduler` still intact, the tests (`test_bash_run`, `test_limit_server`) import `OlAsyncIOScheduler` → `ImportError`. Score: **0**

**Dimension D — 12/25**: Model correctly identifies and implements `OlAsyncIOScheduler` (the exact right class name and base class). `bash_run` and `limit_server` implementations appear functionally correct. Only flaw: wrong diff format (new vs modify) and missing `get_service_ip`. Score: **12**

---

### Task 9 — `b4f7c185` | Solr update_key tuple return
**Score: 100.0/100** (A=25, B=25, C=25, D=25)

**Task**: Change `update_key()` return type from `SolrUpdateRequest` to `tuple[SolrUpdateRequest, list[str]]` in `AbstractSolrUpdater`, `EditionSolrUpdater`, `WorkSolrUpdater`, `AuthorSolrUpdater`; move `update.keys` to separate `new_keys` list; update `utils.py` accordingly.

**Dimension A — 25/25**: Model hits BOTH gold files (`update_work.py` and `utils.py`). Zero extra files. Formula: 2/2×25 = **25**

**Dimension B — 25/25**: The model's diff carries the same git index hashes as the gold patch (`f8cc5bba683..2de793f317e`), indicating the model reproduced the exact gold content. All gold hunks are present: `AbstractSolrUpdater.update_key` return type annotation, `EditionSolrUpdater` refactor with `new_keys` list, `WorkSolrUpdater` returns `update, []`, `AuthorSolrUpdater` returns tuple, corresponding `utils.py` changes. Score: **25**

**Dimension C — 25/25**: With the gold patch reproduced exactly, all 3 FAIL_TO_PASS tests pass (`test_workless_author`, `test_no_title`, `test_work_no_title`). Score: **25**

**Dimension D — 25/25**: Perfect match to gold. Score: **25**

**Note**: The model's diff reproduces the gold patch exactly (matching git index hashes). This may reflect the model's training data including this patch.

---

### Task 10 — `dbbd9d53` | ListRecord.from_input seeds parsing
**Score: 10.2/100** (A=0, B=4.2, C=0, D=6)

**Task**: Fix `ListRecord.from_input()` in `lists.py` (add `parse_qs` branch for POST body, fix seeds iteration) and fix `utils.py` `setvalue()` "don't overwrite" guard.

**Dimension A — 0/25**: Model hits `lists.py` (1/2 gold) but adds `test_lists.py` as spurious extra → formula: 1/2×25 − 12.5 = **0**.

**Dimension B — 4.2/25**: Model proposes adding `if isinstance(i['seeds'], str): i['seeds'] = [...]` normalization. However, this targets a codebase where the `if data := web.data():` branch already exists — a code state that only exists AFTER the gold patch is applied. The model is hallucinating the starting state. Missing: the core `if data := web.data()` branch addition, the `parse_qs` import, and the `utils.py` setvalue fix. Score: **4.2**

**Dimension C — 0/25**: The diff targets non-existent lines in the original codebase (post-patch hallucination) → fails to apply → test `test_from_input_with_data` fails. Score: **0**

**Dimension D — 6/25**: Correct diagnosis of the seeds-as-string bug. The isinstance check is a valid defensive fix but misses the core POST body parsing problem. Score: **6**

---

## Key Failure Patterns

### 1. Spurious test fixture modifications (Tasks 2, 3, 8-file 11838fad, 111347e9)
The raw model frequently modifies test data JSON files (expected MARC output fixtures) to match its code's output. This is a "gaming the benchmark" behavior that:
- Causes heavy score_A penalties (56–57 extra files for MARC tasks → A=0 despite hitting the right source file)
- Conflicts with gold test expectations at evaluation time
- Explains why these tasks score A=0 despite the model making real code changes

### 2. Hallucinated codebase state (Tasks 6, 10)
Two tasks (`5069b09e`, `dbbd9d53`) show the model working from a hallucinated post-patch version of the code:
- `5069b09e`: Diff removes `ALLOW_DELETE_ON_CONFLICT` logic that doesn't exist yet (it's the gold addition)
- `dbbd9d53`: Adds isinstance check to a `web.data()` branch that only exists after gold is applied
- Both diffs fail to apply → C=0 despite partially correct concepts

### 3. "New file" mode for existing files (Task 8)
`8a5a63af`: Model creates `scripts/monitoring/utils.py` with correct content (`OlAsyncIOScheduler`, `bash_run`, `limit_server`, `[OL-MONITOR]` prefix) but uses `new file mode` diff format (`--- /dev/null`). Since utils.py already exists, the diff fails to apply. The model actually identified the right fix (correct class name) but the diff format prevents it from working.

### 4. Private vs public method naming (Tasks 5, previous runs)
`4a5d2a7d`: Model consistently implements `_get_statement_values` (private, underscore prefix) across all three conditions. Test calls `entity.get_statement_values` (public) → `AttributeError` → C=0.

### 5. One memorized correct answer (Task 9)
`b4f7c185` (Solr update_key tuple return) scores 100/100 with identical git index hashes to the gold patch. The model appears to have memorized this specific fix from training data.

---

## Observations

### vs mcp_average_at_3 and mcp_skills_pass_at_3

| Metric | raw_worst_at_3 | mcp_skills_pass_at_3 | mcp_average_at_3 | Best |
|--------|---------------|----------------------|-------------------|------|
| Mean total | **30.0** | 20.0 | 19.5 | raw |
| Mean A | **5.3** | 4.3 | 3.1 | raw |
| Mean B | **10.2** | 4.4 | 6.4 | raw |
| Mean C | 4.7 | **5.3** | 3.4 | skills |
| Mean D | **9.8** | 6.0 | 6.6 | raw |
| Prose-only | **0%** | 30% | 30% | raw |
| Pass@1 equiv. | 10% | **20%** | 0% | skills |

**The raw model outperforms on most dimensions.** Despite being the "worst" of 3 raw runs, raw_worst_at_3 scores 30.0/100 — significantly higher than both MCP conditions. The raw model:
- Never produces prose-only answers (all diffs)
- Achieves the highest B and D scores (more complete patches, better code quality)
- Gets the highest A score (5.3/25)

**The MCP skills condition gets the best pass@1** (20% vs 10%). When a model passes a test in the skills condition, it tends to get the implementation exactly right (tasks 00bec1e7 and dbbd9d53). The raw model's one pass (b4f7c185) appears to be memorization.

**Key structural differences:**
- Raw model produces actual diffs for ALL tasks → no prose-only penalty
- Raw model modifies test files as spurious extras (MARC tasks) → heavy score_A penalties but code changes present
- Raw model occasionally hallucinates the post-patch codebase state (tasks 5069b09e, dbbd9d53)
- b4f7c185 gold patch memorization inflates the raw score significantly (+70 points on one task)

### Headline findings
- **Best task**: `b4f7c185` (100/100) — memorized correct patch
- **Best genuine solve**: `25858f9f` (41.8/100) — creates new utils.py with correct content, hits 3/4 files
- **Most interesting failure**: `8a5a63af` (28.1/100) — correct class name and implementation, wrong diff format prevents application
- **Consistent failure**: `4a5d2a7d` (0/25 C across all 3 conditions) — underscore prefix naming error in all three runs
