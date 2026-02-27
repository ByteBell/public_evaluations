# Our new benchmarking plan 

We will focus on the single repo in the dataset dataset/Kubecluster/kubernetes and will consider the impacts only caused by files in this repo and the blast radius / impact radius will be strictly limited to this single repo only. 


## How will we collect the questions ? 

We will target PR's on kubernetes with labels such as size/XL & size/XXL and focus on PRs that solve a bug (kind/bug) , adds a feature (kind/feature), removing tech debt (kind/cleanup ) etc. following top prs in each category 


after finding a set of top PRs lets say we have a list of 50 PRs the we will extract pr meta what it tries to solve , what it changes and finally formulate a question regarding a change in the source now that change can be easily derived based on the PR but it is not limited to the changes introduces by the PR . PR will give the question generator a inspiration to think of so generator doesnt have nothing to start with and we can get a good quality set of questions .


## How will we generate Ground truth ? 

Using agentic workspace with Guiding pipeline to agentic tools like claude code, copilot,  gemini code all of them followed the same pipeline to construct the ground truth , the capablity of models is then not a important requirement as even haiku 4.5 , sonnet 4.5, gemini 2.5 performed much better then opus 4.6 extended thinking one. Why is so , cause instead of zero shotting them with a problem and let them figure out how to resolve it we give them recipe of how to do it

I already used this simliar approach earlier in while enhancing the gt for the multirepo so oat single repo it should work .

( I added the rules i used  agentic_gt_population.md)


## How will we evaluate ? 

described in evaluation.md 


## Detailed Question Types & Breakdown


Core Design Principle: Make Hallucination the Main Enemy
From the KubeCluster45 findings, every SOTA has >56% hallucination rate. For a single-repo benchmark to be harder, you need questions where:

The true blast radius is small but models overestimate it wildly (trap questions)
The true blast radius is large but non-obvious (models miss the pattern entirely)
Generated code is in the answer (models don't know when to stop at the source vs include zz_generated.* files)
Proposed PR Categories
Tier 1 — "Black" (Zero-Impact Traps)
PRs: kind/bug or kind/cleanup that refactor internal logic without touching any exported/interface signature.

Example shape: A kubelet scheduling loop gets a bug fix — pure implementation change, no signature changes, no struct mutations. Correct answer: 0 impacted files.

Why hard: Models will hallucinate dozens of files because they see "scheduler" or "kubelet" and assume cascade. You already saw this with MIXED_TC001 — the "trap" questions exposed the hallucination problem most starkly.

Tier 2 — "Red" (Internal Interface Cascades)
PRs: kind/feature or kind/api-change adding methods to widely-implemented internal interfaces.

Target interfaces in kubernetes:

scheduler.Plugin, scheduler.FilterPlugin, scheduler.ScorePlugin
admission.Interface, admission.MutationInterface
storage.Interface, storage.Backend
kubelet.PodManager, kubelet.VolumeManager
Why hard: Many plugin implementations scattered across pkg/scheduler/framework/plugins/*/, each must be traced. Models hallucinate random files. The concrete implementor detection is the same hard problem as the multi-repo case.

Tier 3 — "Orange" (Struct/Type Mutations)
PRs: kind/api-change or kind/cleanup that change:

A struct field from value → pointer (or vice versa) → struct literal sites
A type from []T → named type → range iteration sites
Variadic function signatures → all call sites
Within kubernetes these live in pkg/, staging/src/k8s.io/, plugin/. The fan-out within staging packages is particularly hard to trace.

Tier 4 — "Yellow" (Generated Code Boundary)
PRs: changes to staging/src/k8s.io/api/*/types.go that trigger code generation.

The hard question: does the model list zz_generated.deepcopy.go, zz_generated.conversion.go, and the generated client code as "impacted"? These files must be regenerated but aren't hand-edited. This tests whether models understand the generated/source boundary — a uniquely kubernetes challenge.

Tier 5 — "Grey" (Feature-Gate Conditional Impact)
PRs: new features behind a feature gate where impacted files are only conditionally compiled/executed.

The question becomes: "What breaks if this feature gate is enabled?" — requires the model to understand the gate pattern and trace only gated code paths.

PR Skimming Checklist
For each candidate PR from size/XL + size/XXL:

Signal	Keep	Drop
Change is in ≤3 source files but cascades to ≥10 consumers	Yes	
Change looks like high fan-out but is implementation-only	Yes (Tier 1 trap)	
Change is purely in vendor/		Drop
Change is purely doc/comment		Drop
Change touches zz_generated.* as the primary change		Drop (generated changes are the output, not input)
Change is in staging/src/k8s.io/ shared packages	Yes (high cascade)	
Change is a pure gofmt / rename		Drop
PR has a kind/api-change label	Yes (structured GT possible)	
Diff touches interface definition AND has ≥5 implementing packages	Yes (Tier 2)	
What Makes It Harder Than KubeCluster45
The multi-repo benchmark had a natural scope limiter — you only searched 10-15 other repos. A single-repo benchmark has no scope boundary. The kubernetes codebase has ~3,500 packages. Models don't know when to stop searching, so hallucination pressure is higher.

Also: kubernetes has fakes and mocks inside the same repo (pkg/xxx/testing/fake*.go, pkg/xxx/fake/). These are legitimate impacted files (they implement interfaces) but models systematically miss them. They're high-value precision tests.

Suggested Distribution (50 questions)

| Tier | Count | Rationale |
|------|------:|-----------|
| Black (zero-impact traps) | 8 | Directly exploits the hallucination problem |
| Red (interface cascades) | 15 | Hardest to get right, most discrimination power |
| Orange (struct/type mutations) | 12 | Known hard from MIXED questions |
| Yellow (generated code boundary) | 8 | Unique to kubernetes, novel test axis |
| Grey (feature-gate conditional) | 7 | Tests reasoning about conditional impact |

---

## Question Generation Pipeline

### Overview

The pipeline takes a curated PR candidate list and produces one question per PR entry. The PR is the **inspiration** — the actual question is about a specific, concrete Go symbol change within the kubernetes codebase. The pipeline has four phases, where AI is used in Phases A, B, and C, and Phase D is purely mechanical assembly.

```
pr_candidates.json  (curated, human-reviewed PR list)
        │
        ▼
 ┌──────────────────────────────┐
 │  PHASE A · PR Diff Analysis  │  AI reads the PR diff + actual source files.
 │  (What changed, precisely)   │  Extracts: which Go symbol changed, change
 └──────────────┬───────────────┘  type, before/after, and the source file path.
                │
                ▼
 ┌──────────────────────────────┐
 │  PHASE B · Angle Selection   │  AI maps the change to a tier. Checks running
 │  (Type + question angle)     │  distribution quotas. Picks the sharpest angle
 └──────────────┬───────────────┘  that maximises difficulty for SOTA models.
                │
                ▼
 ┌──────────────────────────────┐
 │  PHASE C · Question Write    │  AI reads the actual kubernetes source file.
 │  (Concrete question text)    │  Writes a question naming real Go symbols,
 └──────────────┬───────────────┘  real file paths, real package names.
                │
                ▼
 ┌──────────────────────────────┐
 │  PHASE D · Assembly          │  Writes question.json per ID.
 │  (Schema + meta.json)        │  Updates meta.json distribution map.
 └──────────────────────────────┘
```

The model used at Phases A, B, and C must support tool use so it can read source files from `dataset/Kubecluster/kubernetes/` during generation. The PR diff is fetched from the GitHub API.

---

### Input

`pr_candidates.json` — the curated list output by `fetch_pr_candidates.py` after human review. Each entry has at minimum:

```json
{
  "number": 136039,
  "title": "Promote MutatingAdmissionPolicy to v1 (GA)",
  "url": "https://github.com/kubernetes/kubernetes/pull/136039",
  "merged_at": "2026-02-18",
  "labels": ["kind/api-change", "kind/feature", "size/XXL"],
  "tier": "Red",
  "key_files": ["staging/src/k8s.io/api/admissionregistration/v1/types.go"]
}
```

The `tier` field from the fetch script is a **hint**, not a binding assignment. Phase B may override it.

---

### Phase A — PR Diff Analysis

#### Purpose

Extract the single most question-worthy Go symbol change from the PR. A PR may touch hundreds of files; Phase A narrows focus to the one change that is (a) concrete, (b) has a traceable blast radius within the repo, and (c) is not a generated or test-file-only change.

#### Inputs to Phase A

| Input | Source |
|---|---|
| `pr.number` | From pr_candidates.json |
| `pr.key_files` | From pr_candidates.json (heuristic file list) |
| PR diff hunks | Fetched from GitHub API (`/repos/kubernetes/kubernetes/pulls/{number}/files`) |
| Actual source file content | Read from `dataset/Kubecluster/kubernetes/<file>` for each key_file |

#### AI Prompt Contract

The AI must identify **one primary change** — the Go symbol (interface, struct, function, type alias) whose modification has the broadest intra-repo blast radius. It must answer:

**A1 — What is the primary symbol that changed?**
Identify: symbol name, kind (interface/struct/func/type), the file it lives in, and a verbatim before/after extracted from the actual source file on disk.

**A2 — What change type is it?**
One of: `new_interface_method`, `removed_interface_method`, `value_to_pointer`, `pointer_to_value`, `map_to_named_type`, `slice_to_named_type`, `signature_change`, `field_rename`, `field_type_change`, `implementation_only`.

`implementation_only` means the change is purely internal — no exported type surface changed. This is the signal for a Black (zero-impact trap) question.

**A3 — What is the blast radius shape?**
A brief, structured assessment: how many implementing types / call sites / struct literal sites likely exist within the kubernetes repo. The AI must check the source file and any obvious interface embeddings before answering this — not guess.

#### Phase A Output Schema

```json
{
  "primary_change": {
    "symbol":      "admission.ValidationInterface",
    "kind":        "interface",
    "change_type": "new_interface_method",
    "source_file": "staging/src/k8s.io/apiserver/pkg/admission/interfaces.go",
    "before":      "type ValidationInterface interface {\n    Validate(...) error\n}",
    "after":       "type ValidationInterface interface {\n    Validate(...) error\n    ValidateInit(ctx context.Context) error\n}",
    "new_symbol":  "ValidateInit"
  },
  "blast_radius_shape": {
    "estimate":    "medium",
    "reasoning":   "~20 admission plugins in pkg/admission/plugin/ each implement this interface via a Handler embed; fakes in testing/ also implement it"
  },
  "secondary_changes": [],
  "skip_reason": null
}
```

`skip_reason` is non-null if the PR should be skipped (e.g. diff is purely generated files, no suitable symbol found). The pipeline moves to the next PR in that case.

#### Rules for Phase A

1. **AI must read actual source files** — not infer before/after from the diff text alone. The diff shows the change but the full file context is needed to write accurate `before`/`after` blocks.
2. **One primary change per PR.** If a PR changes multiple symbols, pick the one with the highest expected intra-repo blast radius. Secondary changes are listed but not used for question generation.
3. **`change_type = implementation_only` if** no exported type signature, no interface, no struct field type, and no function signature changed — only internal logic. This is a valid and valuable result (produces a Black question).
4. **Do not invent symbols.** If the diff does not clearly show a Go type/interface/function change, set `skip_reason` and do not proceed.
5. **`source_file` must exist on disk** at `dataset/Kubecluster/kubernetes/<source_file>`. If it does not exist in the local clone, set `skip_reason: "source_file_not_in_local_clone"`.

---

### Phase B — Angle Selection

#### Purpose

Map the Phase A output to a question tier and select the most discriminating angle to ask. Phase B also enforces the target distribution — if the Red quota (15) is already filled, a Red-shaped change must be reclassified or held.

#### Inputs to Phase B

| Input | Source |
|---|---|
| Phase A output | `primary_change` block |
| Running distribution | Current count per tier in the output directory |
| Target distribution | Black=8, Red=15, Orange=12, Yellow=8, Grey=7 |

#### AI Prompt Contract

**B1 — Tier assignment**

Map `change_type` to tier using these primary rules:

| `change_type` | Primary tier |
|---|---|
| `implementation_only` | Black |
| `new_interface_method`, `removed_interface_method` | Red |
| `signature_change` | Red |
| `value_to_pointer`, `pointer_to_value` | Orange |
| `map_to_named_type`, `slice_to_named_type` | Orange |
| `field_type_change`, `field_rename` | Orange |
| Any change in `staging/src/k8s.io/api/*/types.go` | Yellow (override) |
| Any change guarded by a feature gate check | Grey (override) |

If the quota for the primary tier is full, the AI may: (a) assign a secondary tier if the change genuinely fits, or (b) flag `quota_full: true` to signal the PR should be skipped.

**B2 — Question angle**

Within the assigned tier, the AI selects the angle that maximises difficulty:
- Red → prefer interface methods that have many small implementing structs (fakes, plugins) rather than a single large implementor
- Orange → prefer changes that have both struct literal sites AND range/index sites (two breaking patterns at once)
- Black → prefer changes in hot modules (scheduler, kubelet, admission) where models are most likely to hallucinate cascade
- Yellow → prefer types where the generated client code is non-trivially impacted (not just `deepcopy`)
- Grey → prefer gates that are close to default-on so the question is about real conditional paths, not dead code

#### Phase B Output Schema

```json
{
  "tier":             "Red",
  "tier_description": "Interface Cascade",
  "quota_full":       false,
  "angle":            "new_interface_method on a widely-implemented admission plugin interface",
  "difficulty_notes": "pkg/admission/plugin/ has ~18 structs that embed handler and implement this interface; testing/ fakes also implement it; models will miss the fakes",
  "question_framing": "new_interface_method"
}
```

---

### Phase C — Question Generation

#### Purpose

Write the final question text. The question must be self-contained — a reader with access to the kubernetes repository should be able to answer it without seeing the PR. It must name real Go symbols, real file paths, and real package names extracted from the actual source file.

#### Inputs to Phase C

| Input | Source |
|---|---|
| Phase A `primary_change` block | Phase A output |
| Phase B `tier`, `angle`, `question_framing` | Phase B output |
| Full content of `primary_change.source_file` | Read from `dataset/Kubecluster/kubernetes/` |

#### AI Prompt Contract

The AI writes a question with three mandatory components:

**C1 — Setup (the hypothetical or real change)**
Describe the change concretely. For hypothetical changes (not exactly what the PR does), the setup states: "Consider the following change to `<file>`:" followed by a verbatim diff block or a precise description. For direct PR changes, the setup states: "The following change is made to `<file>`:" followed by the actual diff.

**C2 — Scope declaration**
Every question ends with: *"Which files within the `kubernetes/kubernetes` repository would fail to compile or exhibit a runtime regression as a result of this change? List each file by its path relative to the repository root."*

For Black questions: *"Which files within `kubernetes/kubernetes`, if any, are impacted by this change?"* — the explicit "if any" signals that zero is a valid answer without telegraphing it.

For Grey questions: *"Assuming the feature gate `<GateName>` is enabled, which files within `kubernetes/kubernetes` are conditionally impacted?"*

**C3 — Exclusion clause (where applicable)**
For Yellow questions only, append: *"Do not include files that are automatically regenerated by `hack/update-codegen.sh` — list only files requiring manual changes."* This tests whether the model knows the generated/source boundary.

#### Phase C Output Schema

```json
{
  "question_text": "The following change is made to `staging/src/k8s.io/apiserver/pkg/admission/interfaces.go`:\n\n```go\n// Before\ntype ValidationInterface interface {\n    Validate(ctx context.Context, a Attributes, o ObjectInterfaces) error\n}\n\n// After\ntype ValidationInterface interface {\n    Validate(ctx context.Context, a Attributes, o ObjectInterfaces) error\n    ValidateInit(ctx context.Context) error\n}\n```\n\nThe new method `ValidateInit` must be implemented by all concrete types that satisfy `ValidationInterface`.\n\nWhich files within the `kubernetes/kubernetes` repository would fail to compile or exhibit a runtime regression as a result of this change? List each file by its path relative to the repository root.",
  "source_symbols": ["ValidationInterface", "ValidateInit"],
  "source_file":    "staging/src/k8s.io/apiserver/pkg/admission/interfaces.go"
}
```

#### Rules for Phase C

1. **All Go symbol names in the question must exist in the actual source file.** The AI must read the file before writing the question. No invented method names, struct fields, or package paths.
2. **`before` block must be verbatim from the file.** Copy-paste, do not paraphrase.
3. **The change described must be a change to a single file.** If the blast radius requires understanding two files, the question describes only the primary file change and the downstream impact is for the evaluatee to discover.
4. **No hints about the answer.** The question must not mention which packages are downstream, which structs implement the interface, or how many files are expected to be impacted.
5. **Black questions must not hint at zero.** The "if any" framing is the only concession. Do not add phrases like "this is an internal change" or "this may have limited impact."
6. **Question length should be 80–200 words.** Enough to be precise; short enough to be unambiguous.

---

### Phase D — Assembly

#### Algorithm

```
For each successfully processed PR entry:

  question_id = next available KSR_TC<NNN> (zero-padded, sequential)

  Write results/KubeSingle50/<question_id>/question.json

  Append to meta.json:
    questions[question_id] = {
      "id":          question_id,
      "type":        phase_b.tier,
      "pr":          pr.number,
      "module":      phase_a.primary_change.symbol,
      "source_file": phase_a.primary_change.source_file
    }

  Increment actual_distribution[phase_b.tier]
```

Stop when `sum(actual_distribution.values()) == 50` or the PR candidate list is exhausted.

#### Rules for Phase D

1. **Do not overwrite an existing `question.json`** unless `--force` is passed. Idempotent runs must be safe.
2. **`meta.json` is the single source of truth for IDs.** Never derive question IDs from directory listing — always read `meta.json`.
3. **`actual_distribution` in `meta.json` must equal the sum of type counts across `questions`.** Verify before writing.
4. **Sequential ID assignment** — `KSR_TC001` through `KSR_TC050`. Gaps are not allowed. If a question is deleted, renumber.

---

### Question Schema (`question.json`)

```json
{
  "id":                    "KSR_TC001",
  "question_type":         "Red",
  "question_type_description": "Interface Cascade",
  "question":              "<full question text from Phase C>",
  "scope":                 "single_repo",
  "repo":                  "kubernetes",
  "source_change": {
    "file":        "staging/src/k8s.io/apiserver/pkg/admission/interfaces.go",
    "module":      "admission.ValidationInterface",
    "change_type": "new_interface_method",
    "symbol":      "ValidateInit"
  },
  "source_pr": {
    "number":       136039,
    "title":        "Promote MutatingAdmissionPolicy to v1 (GA)",
    "url":          "https://github.com/kubernetes/kubernetes/pull/136039",
    "relationship": "inspired_by"
  }
}
```

`relationship` is one of:
- `direct` — the question asks exactly about what the PR changed
- `inspired_by` — the PR pointed to the area but the question uses a related or adjacent change for sharpness

---

### Meta File Schema (`meta.json`)

```json
{
  "benchmark":    "KubeSingle50",
  "created":      "2026-02-26",
  "repo":         "kubernetes/kubernetes",
  "total":        50,
  "target_distribution": {
    "Black": 8, "Red": 15, "Orange": 12, "Yellow": 8, "Grey": 7
  },
  "actual_distribution": {
    "Black": 8, "Red": 14, "Orange": 13, "Yellow": 8, "Grey": 7
  },
  "questions": [
    {
      "id":          "KSR_TC001",
      "type":        "Red",
      "pr":          136039,
      "module":      "admission.ValidationInterface",
      "source_file": "staging/src/k8s.io/apiserver/pkg/admission/interfaces.go"
    }
  ]
}
```

The `meta.json` is the entry point for any human reviewing the benchmark. Before opening a single `question.json`, a reviewer can see the full distribution, which PRs were used, and which Go symbols each question is about.

---

### Directory Structure

```
results/KubeSingle50/
  meta.json
  KSR_TC001/
    question.json
  KSR_TC002/
    question.json
  ...
  KSR_TC050/
    question.json
```

Ground truth for each question lives in the same directory once the GT pipeline runs:

```
  KSR_TC001/
    question.json
    ground_truth_enhanced.json     ← populated by agentic GT pipeline
```

---

### Error Handling

| Situation | Action |
|---|---|
| Phase A cannot find changed Go symbol | Set `skip_reason`, move to next PR |
| Phase A source file not in local clone | Set `skip_reason: source_file_not_in_local_clone`, move to next PR |
| Phase B quota full for the natural tier | Try secondary tier; if also full, `quota_full: true`, move to next PR |
| Phase C question text references a non-existent symbol | Re-run Phase C once with error feedback; if still invalid, skip |
| PR diff is only generated files or vendor/ | Phase A detects this, sets `skip_reason: generated_or_vendor_only` |
| PR diff is test-only | Phase A detects this, sets `skip_reason: test_only` |
| Total kept questions < 50 after exhausting candidate list | Extend PR candidate window (increase `--days`) and re-run |

---

### Agentic Model Requirements

The model executing Phases A, B, C must be able to:

1. **Read files from disk** — to load source file content from `dataset/Kubecluster/kubernetes/`. Required for accurate `before`/`after` extraction and question writing.
2. **Fetch from GitHub API** — to retrieve PR diff hunks.
3. **Return structured JSON** — all AI outputs must be parseable JSON. Markdown fences must be stripped before parsing.
4. **Reason about Go semantics** — must understand interface satisfaction, struct literal initialisation, and the difference between generated and hand-written Go files.

Recommended model: **Claude Sonnet 4.6** — sufficient for all phases, cost-effective at 50 questions.

---

### Quality Checks (after Phase D)

After `meta.json` is written, verify:

1. `len(meta.questions) == meta.total`
2. `sum(actual_distribution.values()) == meta.total`
3. Every `question.json` passes schema validation (all required fields present, no `null` values)
4. Every `source_change.file` exists on disk at `dataset/Kubecluster/kubernetes/<file>`
5. Every `source_change.symbol` appears as a substring of the actual source file content
6. No two questions share the same `source_change.symbol` + `source_change.file` combination (no duplicate questions)
7. Black questions: verify `change_type == implementation_only` in Phase A output
8. Yellow questions: verify `source_change.file` matches `staging/src/k8s.io/api/*/types.go` pattern


