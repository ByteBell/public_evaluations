# SWE-Pro Evaluation Guide

**Dataset**: `results_on_swe_pro/swe_pro_tasks.json`
**Reference format**: Unified git diff stored in the `answer` field (the gold patch)
**Model answer format**: `answer.json` → `{"answer": "<patch or explanation>"}`
**Official metric**: Binary Pass@1 — patch must make all `FAIL_TO_PASS` tests pass while keeping all `PASS_TO_PASS` tests passing. Top frontier models (GPT-5, Claude Opus 4.1) score ~23% on the public set.

Our rubric is a structured approximation that decomposes pass/fail into four measurable dimensions so we can diagnose *why* a model fails, not just *that* it fails.

**Scoring dimensions**

| Dim | Name | Points | Who computes |
|---|---|---|---|
| A | File Coverage | 25 | `score_prep.py` — never judged |
| B | Patch Completeness | 25 | LLM judge |
| C | Test Coverage | 25 | LLM judge |
| D | Code Correctness | 25 | LLM judge |
| | **Total** | **100** | |

---

## 0. Before Judging — Run score_prep.py

**Required before any LLM evaluation.** The script computes Dimension A exactly and bundles all test signals from Scale's official JSONL into a single `score_input.json` per task.

```bash
# Process all run directories at once
python score_prep.py --all

# Or a single run
python score_prep.py --run_dir results_on_swe_pro/auto_run_on_swe_pro_mcp_claude-sonnet-4-6

# Re-generate if you need to refresh
python score_prep.py --all --force
```

Downloads `sweap_eval_full_v2.jsonl` (25 MB, one-time) on first run. Writes `score_input.json` next to each `answer.json`:

```json
{
  "instance_id":         "instance_...",
  "repo":                "internetarchive/openlibrary",
  "language":            "python",

  "score_A":             8.0,
  "score_A_formula":     "2/5 files × 25",
  "file_hits":           ["openlibrary/catalog/marc/marc_base.py", "..."],
  "file_misses":         ["openlibrary/catalog/marc/marc_xml.py", "..."],
  "extra_files":         [],
  "is_prose_only":       false,

  "fail_to_pass":        ["tests/test_parse.py::TestParseMARCXML::test_xml"],
  "fail_to_pass_count":  3,
  "pass_to_pass_count":  14,
  "test_patch":          "diff --git a/tests/test_parse.py ...",
  "test_functions":      ["test_xml", "test_xml_empty_subfields"],
  "assert_samples":      ["assert record.title() == 'Expected Title'", "..."],

  "gold_patch":          "diff --git a/...",
  "model_answer":        "..."
}
```

The judge only evaluates **B, C, and D**. Everything in `score_A` is already done.

---

## 1. Dimension A — File Coverage (25 pts) — PRECOMPUTED

**Do not ask the judge to score this.** Read `score_A` directly from `score_input.json`.

**Formula**:

```
raw       = (hits / gold_total) × 25
deduction = min(extra_files, hits) × (25 / gold_total)
score_A   = max(0, raw − deduction)   [rounded to 1 decimal]
```

**Reading the output**:

| Field | Meaning |
|---|---|
| `score_A` | The final Dimension A score (0–25) |
| `file_hits` | Gold patch files the model correctly touched |
| `file_misses` | Gold patch files the model missed |
| `extra_files` | Files the model touched not in the gold patch |
| `is_prose_only` | `true` → model wrote no diff → all dimensions = 0 |

Touching test files counts as an extra and is penalised proportionally — models should not modify test files; those changes come from `test_patch` separately.

---

## 2. Dimension B — Patch Completeness (25 pts)

*Did the model address all the structural changes required by the gold patch?*

**Reference**: `gold_patch` from `score_input.json`.

Score each distinct change in the gold patch as **Present** (2), **Partial** (1), or **Missing** (0), then normalise to 25.

```
score_B = round((sum_of_hunk_scores / (total_hunks × 2)) × 25, 1)
```

**Hunk-level checklist** — for each gold patch change, verify:

- [ ] New function/method introduced: present in model answer with correct name?
- [ ] Deleted function/method: removed or correctly superseded?
- [ ] New parameter added: present with same default value?
- [ ] New file created: does model create an equivalent file?
- [ ] Relocated symbol: does model move it to the correct module?
- [ ] Guard clause / conditional change: logically equivalent?
- [ ] Data structure (constant, list, dict) added: present with right shape?
- [ ] Config/i18n/schema files updated (`.json`, `.yaml`, `.pot`)?
- [ ] Cascade call-sites updated (all files that call a renamed/moved function)?


---

## 3. Dimension C — Test Coverage (25 pts)

*Would the model's implementation cause the official FAIL_TO_PASS tests to pass?*

This is the dimension closest to the official binary metric. The official eval runs the tests — we reason about whether the model's code satisfies what those tests assert.

**Reference**: `fail_to_pass`, `test_functions`, `assert_samples`, and `test_patch` from `score_input.json`.

**How to judge**:

1. Read `fail_to_pass` — each entry is a test name, e.g.:
   `"tests/test_wikidata.py::test_get_statement_values"`

2. For each test, find it in `test_functions` and locate the relevant `assert_samples` lines. Read the full test in `test_patch` if needed.

3. Ask: **does the model's code satisfy what this test asserts?**
   - Does the function/method the test calls exist in the model's answer?
   - Does it return the type/value the assertions check for?
   - Does it handle the edge cases covered by the test (null, empty, expired, etc.)?

4. Score each test: **Passes** (full), **Partial** (half), **Fails** (0).

```
score_C = round((covered_points / (fail_to_pass_count × full_points)) × 25, 1)
```


**Key signals to check per test:**

- Function/method name called in the test — does that name exist in the model's answer?
- Return type — does the model return what the assertion checks? (list vs dict, bool, None)
- Edge case guard — does the model handle the empty/null/expired case the test covers?
- Side effects — if a test checks for DB writes, log messages, or state changes, does the model produce them?

**When `fail_to_pass` is empty**: use `assert_samples` and `test_patch` directly to infer what tests check, and score proportionally.

---

## 4. Dimension D — Code Correctness (25 pts)

*Are the specific code facts right — names, parameter defaults, logic conditions, imports?*

**Reference**: `assert_samples` (exact values asserted), `test_functions` (exact names called), and `gold_patch` from `score_input.json`.

| Score | Criteria |
|---|---|
| 25 | All symbol names match gold exactly. Logic satisfies all test assertions. Parameter defaults correct. Imports present. |
| 18 | Minor name divergence (e.g. `get_statement_values` vs `getStatementValues`) but logic correct. 1 import missing. |
| 12 | Names largely wrong but approach is correct — right file, structurally similar fix, most assertions would pass. |
| 6 | Some correct elements but significant logic errors — inverted condition, wrong default value, wrong scope. |
| 0 | Wrong logic throughout. Names entirely made up. Assertions would all fail. |

**Correctness facts to verify explicitly:**

1. **Function/method names** — compare model's symbol names against `test_functions` (what the tests call)
2. **Parameter defaults** — e.g., `use_netrc=True` vs `use_netrc=False`; test assertions often check the default behaviour
3. **Exact values in assertions** — e.g., if `assert_samples` shows `assert result['expires'] > 0`, the model must set `expires`
4. **Module placement** — if a symbol is moved, is it in the correct module? (test imports reveal this)
5. **All call-sites updated** — if gold updates N call-sites for a renamed function, did model update all of them?
6. **Language idioms** — JS: async/await, promise chains; Python: context managers, type annotations

---

## 5. Scoring Sheet Template

```
Task: <instance_id>
Repo: <org/repo>
Language: <python|js|...>

--- From score_input.json (no judging needed) ---
score_A        : __._/25   (auto-computed)
file_hits      : [list]
file_misses    : [list]
extra_files    : [list]
is_prose_only  : true/false
fail_to_pass   : [N tests listed]
test_functions : [list of test function names]
assert_samples : [first 15 assert lines]

--- Dimension B: Patch Completeness ---
Gold patch changes:
  [ ] <change 1> : present / partial / missing
  [ ] <change 2> : present / partial / missing
  ...
Coverage: X/Y changes = Z%

--- Dimension C: Test Coverage ---
For each fail_to_pass test:
  [ ] <test_name_1> : passes / partial / fails  — reason
  [ ] <test_name_2> : passes / partial / fails  — reason
  ...
Coverage: X/N tests = Z%

--- Dimension D: Code Correctness ---
Symbol names vs test call sites: [match|mismatch]
Parameter defaults: [correct|wrong]
Logic vs assert_samples: [correct|partial|wrong]
Imports: [present|partial|missing]

--- Scores ---
A. File Coverage   : __._/25   (from score_input.json)
B. Completeness    : __._/25
C. Test Coverage   : __._/25
D. Correctness     : __._/25
TOTAL              : ___._/100

--- Notes ---
[Extra files added, wrong approach, test files modified, etc.]
```

---

## 6. Special Cases

### 6.1 Prose-Only Answers

If `is_prose_only: true` in `score_input.json`: A=0, B=0, C=0, D=0, Total=0.
Flag as `answer_type: description_only`. Do not evaluate further.

### 6.2 New File Creation Tasks

When gold creates a new file:
- Dimension A: hit only if model creates a file at a similar path/module name
- Dimension B: check exported function/class names match gold
- Dimension C: test_patch will import from that new file — check the import succeeds
- Dimension D: check wiring (import in index, register in router)

### 6.3 Symbol Relocation Tasks

When gold moves a symbol from file A to file B:
- Model must: (1) remove from A, (2) add to B, (3) update all call-sites
- `test_functions` will call the symbol — which file does the test import it from? That's where it must end up
- Score each step in B independently; C checks if the tests would pass in the new location

### 6.4 Multi-File Cascade Tasks

When gold touches 5+ files:
- `file_misses` directly shows which propagation steps were skipped
- Each missed cascade file likely causes one or more `fail_to_pass` tests to fail — track this for C
- Score B on each missed file; C drops proportionally with missed test coverage

### 6.5 Model Touches Test Files

If `extra_files` contains test paths (`tests/`, `test_`, `_test.`):
- A is already penalised by the extra-file deduction
- For C: check if the model modified assertions to make itself pass (gaming) vs adding legitimately needed fixtures — flag if gaming

### 6.6 Correct Approach, Different Mechanism

Model finds right file and concept but implements differently from gold:
- A = full (file_hits)
- B = partial (different structure from gold)
- C = focus score here — does the alternative implementation satisfy the test assertions?
- D = 10–15 (diverges from gold but may be valid)

---

## 7. Aggregate Metrics Per Run

| Metric | Formula |
|---|---|
| `answer_rate` | Tasks with non-prose answer / total |
| `avg_score_A` | Mean `score_A` / 25 — from script, no judge |
| `avg_score` | Mean of A+B+C+D totals |
| `full_patch_rate` | Tasks scoring ≥ 85/100 / total |
| `partial_rate` | Tasks scoring 40–84/100 / total |
| `zero_rate` | Tasks scoring 0–39/100 / total |
| `avg_completeness` | Mean B / 25 |
| `avg_test_coverage` | Mean C / 25 |
| `avg_correctness` | Mean D / 25 |

Report broken down by: **repo**, **language**, **run_mode** (mcp, mcp_skills).

`score_prep.py --all` already prints `avg_score_A`, coverage breakdown, and prose-only rate per run without any LLM.

---

## 8. Failure Patterns

| Pattern | Signal in score_input.json | Dimension hit |
|---|---|---|
| Prose-only answer | `is_prose_only: true` | All = 0 |
| Correct file, missed cascade | `file_misses` has call-site files | A partial; B and C drop |
| Wrong module placement | `extra_files` has wrong file, `file_misses` has right one | A low; D −5 to −10 |
| Inverted condition / wrong default | Logic fails `assert_samples` checks | C fails; D = 0–5 |
| Made-up symbol names | Mismatch vs `test_functions` call sites | C partial; D −10 |
| Touches test files | `extra_files` has `tests/` paths | A deducted |
| Skips config/i18n files | `file_misses` has `.json`/`.pot`/`.yaml` | B −5 to −10 |
| Context overflow / no diff | Long prose, `is_prose_only: true` (Sonnet 4 pattern) | All = 0 |

---

## 9. How to Run a Scoring Session

```
Step 1 — Preprocess (once per run set):
    python score_prep.py --all
    → Downloads sweap_eval_full_v2.jsonl (first time only)
    → Writes score_input.json in every instance folder
    → Prints Dimension A stats immediately (no judge needed)

Step 2 — For each task where is_prose_only = false:
    a. Open score_input.json
    b. Read fail_to_pass + test_functions + assert_samples  ← Dimension C reference
    c. Read gold_patch changes                              ← Dimension B reference
    d. Read model_answer
    e. Fill scoring sheet (Section 5)
    f. Record A (precomputed), judge B, C, D

Step 3 — Aggregate (Section 7)

Step 4 — Write report
```

---

## 10. Worked Example

**Task**: `instance_internetarchive__openlibrary-4a5d2a7d…`

**`score_input.json` after `score_prep.py`:**
```json
{
  "score_A":          6.7,
  "score_A_formula":  "1/3 files × 25",
  "file_hits":        ["openlibrary/core/wikidata.py"],
  "file_misses":      ["openlibrary/i18n/messages.pot", "openlibrary/templates/authors/infobox.html"],
  "extra_files":      [],
  "is_prose_only":    false,
  "fail_to_pass":     ["tests/test_wikidata.py::test_get_statement_values",
                       "tests/test_wikidata.py::test_get_external_profiles"],
  "test_functions":   ["test_get_statement_values", "test_get_external_profiles"],
  "assert_samples":   [
    "assert entity._get_statement_values('P1960') == ['some-scholar-id']",
    "assert any(p['label'] == 'Google Scholar' for p in profiles)"
  ]
}
```

**Model answer scenarios:**

| Model Output | A /25 | B /25 | C /25 | D /25 | Total |
|---|---|---|---|---|---|
| Adds `_get_statement_values` + `SOCIAL_PROFILE_CONFIGS` in `wikidata.py`, updates template + i18n | 3/3 → **25.0** | all changes → **25** | both tests pass → **25** | names + logic exact → **25** | **100** |
| Adds `_get_statement_values` in `wikidata.py` only | 1/3 → **8.3** | 1/3 changes → **8** | 1/2 tests → **12** | correct name + logic → **18** | **46.3** |
| Adds method with wrong guard, only in `wikidata.py` | 1/3 → **8.3** | 1/3 changes → **8** | 0/2 tests (guard wrong, assertions fail) → **3** | wrong logic → **6** | **25.3** |
| Prose only | `is_prose_only` → **0** | **0** | **0** | **0** | **0** |
