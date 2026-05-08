# Plan: Populating Enhanced Ground Truth for All Questions

## Context

We have a new ground truth schema (`ground_truth_enhanced.schema.json`) that replaces prose-based ground truths with structured, verifiable facts. We need to populate `ground_truth_enhanced.json` for every question across two datasets:

- **KubeCluster45** — 45 questions (11 MIXED + 34 OBS), all have existing `ground_truth.json`
- **KubeClusterTests** — 100 questions (all CRW/OBS/KM/SA/NK), none have any ground truth yet

Total: **145 questions** that need enhanced ground truth.

All 25 repos are cloned locally in `dataset/Kubecluster/`.

---

## The Core Challenge

The enhanced ground truth requires five things per question that the old ground truth doesn't have:

1. **The change block** — what module, what file, before/after signature
2. **Breaking patterns** — enumerated code patterns that break (with IDs)
3. **Impacted files with evidence** — actual greppable code snippets per file
4. **Severity classification** — compile_error vs runtime vs test_failure
5. **False positives** — files that look relevant but don't break

Items 1, 2, and 4 can be derived from reading the question + basic code understanding.
Item 3 requires searching the actual codebase.
Item 5 requires codebase search + judgment.

No single approach works for all of these. We need a pipeline.

---

## Approach: Three-Phase Pipeline

### Phase 1 — Extract the "Change Block" and "Breaking Patterns" (No codebase needed)

**What:** For each question, read `question.json` and produce the `change` object and `breaking_patterns` array.

**How:** This is a reading comprehension task on the question text itself. Every question follows the pattern: *"Add/Change/Modify X on interface/struct Y in repo Z. Which files across A, B, C would break?"*

From this we can extract:
- `module` — the interface/struct/field being changed (e.g. `metav1.ObjectMeta.Labels`)
- `source_repo` — where it's defined (e.g. `kubernetes`)
- `source_file` — find this by grepping the actual repo for the type/interface definition
- `before` / `after` — derive from the question's description of the change
- `breaking_patterns` — derive from the nature of the change (type change → direct access breaks, new method → implementations must add it, parameter change → all callers break)

**Who does this:** An LLM (Claude) reading each question + a single grep to find the source file. This is a structured extraction task, not a creative one — the answers are deterministic from the question text.

**Output:** A partial `ground_truth_enhanced.json` per question with `change` and `breaking_patterns` filled in, everything else empty.

**Validation:** Human spot-checks 5-10 questions to confirm the extraction is correct. The `source_file` can be validated by checking if it exists in `dataset/Kubecluster/<source_repo>/`.

---

### Phase 2 — Find Impacted Files with Evidence (Codebase search required)

**What:** For each question, search the target repos for files that match the breaking patterns identified in Phase 1.

**How:** This is the most labor-intensive phase. Two sub-approaches, used together:

#### Phase 2A — Automated grep pass

For each breaking pattern, construct grep queries against the target repos mentioned in the question.

Example for MIXED_TC007 (Labels change):
- Pattern `direct_index_write` → grep for `.Labels[` across argo-cd, cert-manager, etc.
- Pattern `range_iteration` → grep for `range.*\.Labels` across same repos
- Pattern `map_initialization` → grep for `Labels\s*=\s*make\(map\[string\]string\)` across same repos

This produces a candidate list of files with line numbers and matching code snippets. These become the `code_evidence` entries.

**Important:** The grep pass finds candidates, not confirmed impacts. A file might match `.Labels[` but be operating on a completely different struct's Labels field, not `ObjectMeta.Labels`. Filtering is needed.

#### Phase 2B — LLM verification of candidates

Take the grep candidates from 2A and have an LLM (Claude with direct file access) verify each one:
- Is this actually accessing `ObjectMeta.Labels` or some other Labels field?
- Does this file import the relevant package?
- Would this code actually break?

This is a focused, constrained judgment — the LLM is answering "does this specific 5-line code snippet break?" not "search the entire codebase." Much more reliable than open-ended search.

**Output:** The `impacted_files` array filled in with verified entries, each having `breaking_patterns`, `code_evidence`, `severity`, and `suggested_fix`.

**Validation:** For KubeCluster45 questions (which have existing `ground_truth.json`), cross-reference against the old ground truth. Any file in the old ground truth that doesn't appear in the new one should be investigated — it's either a false positive in the old ground truth or a miss in the new one.

---

### Phase 3 — Identify False Positives (Codebase search + judgment)

**What:** Find files that look relevant but don't actually break. These go into `false_positives`.

**How:** Two sources of false positive candidates:

1. **Grep near-misses from Phase 2A** — files that matched a grep pattern but were rejected in Phase 2B. These are natural false positives (they mention Labels but don't access ObjectMeta.Labels).

2. **Files that import the relevant package but don't use the changed module** — e.g. files that import `metav1` and use `ObjectMeta` but only access `.Name` or `.Namespace`, never `.Labels`. Find these by grepping for the import, then filtering out files already in `impacted_files`.

3. **Files from old ground truth that couldn't be verified** — if the old `ground_truth.json` listed a file that Phase 2B couldn't confirm, it becomes a false positive candidate worth documenting.

**Output:** The `false_positives` array filled in with `why_not_affected` explanations.

**Validation:** Human review of a sample. False positives are the hardest to get right — a file might break in a subtle way that grep doesn't catch.

---

## Execution Order

### Start with KubeCluster45 (45 questions)

These already have `ground_truth.json` from Claude Opus with direct data access. This gives us a cross-reference to validate against. Any discrepancy between old and new ground truth surfaces either:
- A flaw in the old ground truth (LLM missed something or hallucinated)
- A gap in our new pipeline (grep patterns too narrow, verification too strict)

Both are valuable findings.

### Then KubeClusterTests (100 questions)

These have no ground truth at all. By the time we reach these, the pipeline will be tested and refined from the KubeCluster45 run. The 100 questions are also simpler in structure (CRW questions tend to be more straightforward than OBS/MIXED).

---

## Tooling Needed

### A script to orchestrate the pipeline

Not writing code here, but describing what it should do:

1. **Read each `question.json`** and extract the change description
2. **Run targeted greps** against the repos mentioned in the question
3. **Feed candidates to an LLM** for verification (Claude via API or Claude Code)
4. **Assemble the `ground_truth_enhanced.json`** from verified results
5. **Compute `impact_summary`** counts automatically from the assembled data
6. **Validate against old ground truth** (for KubeCluster45 only) and flag discrepancies

### Human review checkpoints

- After Phase 1: spot-check 5 questions — are `change` and `breaking_patterns` correct?
- After Phase 2: review discrepancies between old and new ground truth
- After Phase 3: review false positive explanations for plausibility

---

## Estimated Scope

| Phase | Per Question | Total (145 questions) |
|-------|-------------|----------------------|
| Phase 1 — Change extraction | ~2 minutes (LLM + 1 grep) | ~5 hours |
| Phase 2A — Grep pass | ~5 minutes (multiple patterns × multiple repos) | ~12 hours |
| Phase 2B — LLM verification | ~10 minutes (verify each candidate) | ~24 hours |
| Phase 3 — False positives | ~5 minutes (filter near-misses) | ~12 hours |
| Human review checkpoints | ~3 minutes per question (sampling) | ~3 hours |

Most of this is machine time (grep + LLM calls), not human time. The human review checkpoints are the bottleneck for quality but only apply to a sample.

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Grep patterns too narrow — miss impacted files | Low recall in ground truth | Start broad, filter down. Compare against old ground truth for KubeCluster45. |
| Grep patterns too broad — too many candidates to verify | LLM verification becomes expensive | Limit to repos mentioned in the question, not all 25. |
| LLM verification makes mistakes | Wrong files in ground truth | Human spot-check + cross-reference with old ground truth. |
| Some questions are about runtime behavior, not compile errors | Breaking patterns don't fit neatly | Identify these questions early (Phase 1) and handle them as a separate category. |
| `source_file` doesn't exist in the cloned repo (version mismatch) | Change block is wrong | Verify every `source_file` exists in `dataset/Kubecluster/` before proceeding. |

---

## Definition of Done

A question's enhanced ground truth is complete when:

1. `ground_truth_enhanced.json` exists and validates against `ground_truth_enhanced.schema.json`
2. `change.source_file` physically exists in `dataset/Kubecluster/<source_repo>/`
3. Every `code_evidence` entry is greppable in the actual file
4. `impact_summary` counts match the actual array lengths

