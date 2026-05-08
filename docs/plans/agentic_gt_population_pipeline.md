# Agentic Ground Truth Population Pipeline

## Overview

This document defines the rules and structure for an agentic pipeline that populates
`ground_truth_enhanced.json` files for all 145 breaking-change questions.

The pipeline has **four phases**, where AI is used in Phases 1 and 3, and grep is
the deterministic backbone in Phase 2.

```
Question text + source repo
        │
        ▼
 ┌─────────────────────────────┐
 │  PHASE 1 · AI Chain Link    │  AI reads the question + type definition and
 │  (Observation Expansion)    │  produces a full "search plan": every term,
 └─────────────┬───────────────┘  pattern, sub-type, and alias to grep for.
               │
               ▼
 ┌─────────────────────────────┐
 │  PHASE 2 · Grep             │  Deterministic. Import-aware. Uses every
 │  (Candidate Collection)     │  term from the search plan. Produces a
 └─────────────┬───────────────┘  candidate list: (repo, file, grep_hits).
               │
               ▼
 ┌─────────────────────────────┐
 │  PHASE 3 · AI Verification  │  AI reads each candidate file and decides:
 │  (Semantic Filtering)       │  is it truly impacted? What code breaks?
 └─────────────┬───────────────┘  What is the fix? Drops false positives.
               │
               ▼
 ┌─────────────────────────────┐
 │  PHASE 4 · Assemble & Write │  Collect verified entries. Compute summary.
 │  (ground_truth_enhanced)    │  Write JSON.
 └─────────────────────────────┘
```

The model used at Phase 1 and Phase 3 **must support tool use / agentic calls** so
it can read source files from disk when it needs more context. Claude Sonnet or
Claude Opus are the recommended choices.

---

## Input

Each question directory contains `question.json`:

```json
{
  "id": "MIXED_TC001",
  "question": "Add a new method WaitForCacheSync(ctx context.Context) bool to the SharedInformer interface ..."
}
```

The dataset repos are all cloned at `dataset/Kubecluster/<repo>/`.

---

## Phase 1 — AI Chain Link (Observation Expansion)

### Purpose

A simple grep for `SharedInformer` misses files that reference only
`SharedIndexInformer`, `HasSynced`, or factory wrappers. The AI must
*think like a Go developer* and enumerate every symbol that is relevant
to the breaking change before a single grep is run.

### Inputs to Phase 1

| Input | Description |
|---|---|
| `question_text` | The full question string from `question.json` |
| `source_type_definition` | The actual Go source block of the changed type (read from `dataset/Kubecluster/<source_repo>/<source_file>`) |
| `change_info` | The structured change block: `{change_type, module, before, after}` |

The `source_type_definition` is extracted by reading the relevant file from the
dataset repo — not from any cached or generated data.

### AI Prompt Contract

The AI must answer **three questions** and return a structured JSON object.

#### Question A — What is this change?

Produce the canonical `change` block (fills `before`, `after`, `description`,
`change_type`, `breaking_patterns`). This replaces the rule-based extractor.
The AI reads the actual source definition to produce accurate `before`/`after`
code.

#### Question B — What Go symbols does this touch?

This is the **chain-linking** step. The AI must list every symbol that:

1. **Is the changed type** — the interface/struct/function itself.
2. **Embeds or extends the changed type** — e.g. `SharedIndexInformer` embeds
   `SharedInformer`; any concrete struct that implements the interface.
3. **Is produced by the changed type** — factory types, constructor functions.
4. **Is a method or field unique to the changed type** — method names, field
   names that only appear on this type and its implementors.
5. **Is a usage pattern** — utility functions that accept/return the type (e.g.
   `cache.WaitForCacheSync` accepts `InformerSynced` callbacks from informers).
6. **Is a test double** — fake/mock/stub types that implement the interface.

For each symbol, the AI also specifies:
- The Go symbol name (for grep)
- Whether it is a type, function, method, or field
- Why it's related to the breaking change
- The recommended grep pattern (regex)

#### Question C — What repos and import paths are involved?

Given the list of target repos from the question, the AI must:
- Confirm the import path of the changed package
- Note any **secondary import paths** (e.g. a type may appear under two module
  paths if there is a staging alias)
- Flag any repos where the impact is **indirect** (e.g. a repo depends on a
  wrapper library that depends on the changed package) — these need a deeper
  grep strategy

### Phase 1 Output Schema

```json
{
  "change": {
    "module":      "cache.SharedInformer",
    "change_type": "new_interface_method",
    "before":      "type SharedInformer interface {",
    "after":       "type SharedInformer interface { WaitForCacheSync(ctx context.Context) bool }",
    "description": "New method added. All implementors must add WaitForCacheSync.",
    "source_repo": "kubernetes",
    "source_file": "staging/src/k8s.io/client-go/tools/cache/shared_informer.go"
  },
  "breaking_patterns": [
    {
      "id":         "missing_interface_method",
      "example":    "var _ cache.SharedInformer = (*MyType)(nil)",
      "why_breaks": "Concrete type does not implement the new method."
    },
    {
      "id":         "factory_wrap",
      "example":    "factory.WaitForCacheSync(ctx.Done())",
      "why_breaks": "Factory wrappers that delegate to SharedInformer must propagate the new method."
    }
  ],
  "import_paths": [
    "k8s.io/client-go/tools/cache"
  ],
  "search_plan": {
    "terms": [
      {
        "symbol":      "SharedInformer",
        "kind":        "interface",
        "relation":    "direct",
        "grep_pattern": "SharedInformer",
        "reason":      "The changed interface itself."
      },
      {
        "symbol":      "SharedIndexInformer",
        "kind":        "interface",
        "relation":    "extends",
        "grep_pattern": "SharedIndexInformer",
        "reason":      "Embeds SharedInformer; all its implementors must also add the method."
      },
      {
        "symbol":      "HasSynced",
        "kind":        "method",
        "relation":    "method_on_interface",
        "grep_pattern": "\\.HasSynced",
        "reason":      "The existing sync-check method; files that call it are using informers and may need WaitForCacheSync too."
      },
      {
        "symbol":      "WaitForCacheSync",
        "kind":        "function",
        "relation":    "usage_pattern",
        "grep_pattern": "WaitForCacheSync",
        "reason":      "Utility that orchestrates sync on multiple informers; files calling it manage SharedInformer implementations."
      },
      {
        "symbol":      "SharedInformerFactory",
        "kind":        "interface",
        "relation":    "factory",
        "grep_pattern": "SharedInformerFactory|InformerFactory",
        "reason":      "Factory types that produce SharedInformer instances and forward lifecycle methods."
      },
      {
        "symbol":      "FakeSharedInformer",
        "kind":        "struct",
        "relation":    "test_double",
        "grep_pattern": "FakeSharedInformer|fakeInformer",
        "reason":      "Test doubles that implement SharedInformer; must add WaitForCacheSync."
      }
    ]
  }
}
```

### Rules for Phase 1

1. **AI must read the actual source file** before emitting `before`/`after`. It
   must not hallucinate code.
2. **`search_plan.terms` must be exhaustive** — include everything related, even
   if the relevance seems indirect. Phase 3 AI will filter false positives. It is
   better to over-include in the search plan than to miss files.
3. **`grep_pattern` must be a valid `grep -E` regex**. Test patterns for both
   CamelCase names and package-prefixed forms (e.g. `cache\.SharedInformer` and
   plain `SharedInformer`).
4. For `map_to_named_type` changes, include patterns for ALL map operations that
   would break: `\.\w+\[`, `range .*\.\w+`, `make(map\[`, map literal `{}`
   assignments.
5. For `value_to_pointer` changes, include patterns for struct literal with
   value assignment: `FieldName\s*:\s*pkg\.TypeName\{`, `\.FieldName\s*=\s*`, and
   `TypeName{` (value initialisation).
6. For `signature_change` / `new_interface_method`, always include the interface
   name AND any known concrete implementors AND any `var _ Interface = (*Type)(nil)`
   compile-check patterns.
7. Deduplicate patterns — do not emit the same grep regex twice.
8. Emit at most **20 terms** per question. If more exist, prioritise by
   likelihood of impact.

---

## Phase 2 — Grep (Candidate Collection)

### Purpose

Run every grep pattern from Phase 1's `search_plan.terms` against every target
repo, scoped to files that import the relevant package. Collect all matching files
as candidates.

### Algorithm

```
For each import_path in phase1_output.import_paths:
    For each repo in target_repos:
        importing_files = grep -rln "<import_path>" <repo>/ --include="*.go"

        For each file in importing_files:
            hits = []
            For each term in phase1_output.search_plan.terms:
                matches = grep -n -E "<term.grep_pattern>" <file>
                hits.extend(matches)

            if hits:
                candidates.add((repo, file, hits))

# Fallback for repos with no import hits (indirect dependency):
For each repo in target_repos where importing_files was empty:
    For each term in phase1_output.search_plan.terms:
        files = grep -rln -E "<term.grep_pattern>" <repo>/ --include="*.go"
        For each file in files:
            hits = grep -n -E "<term.grep_pattern>" <file>
            candidates.add((repo, file, hits))
```

### Rules for Phase 2

1. **Import-aware first, fallback second.** Always try to scope by import path
   before doing a repo-wide search. This reduces false positives dramatically.
2. **Collect line numbers with hits** (`grep -n`). Phase 3 needs them for context.
3. **Cap candidates at 100 per question.** If more than 100 files match, keep the
   top 100 sorted by: (a) number of distinct terms matched, (b) file path depth
   (shallower = more likely to be a core file).
4. **Include `_test.go` files.** Test files that mock or implement the interface
   are genuine breaking-change sites.
5. **Store the matched term IDs** alongside each hit so Phase 3 knows which
   symbols were found in that file.

### Phase 2 Output Schema

```json
{
  "candidates": [
    {
      "repo":     "argo-cd",
      "file":     "pkg/client/informers/externalversions/factory.go",
      "term_ids": ["SharedInformerFactory", "WaitForCacheSync"],
      "hits": [
        {"line": 42, "content": "func (f *sharedInformerFactory) WaitForCacheSync(stopCh <-chan struct{}) map[reflect.Type]bool {"},
        {"line": 57, "content": "    return cache.WaitForCacheSync(stopCh, informer.HasSynced)"}
      ]
    }
  ]
}
```

---

## Phase 3 — AI Verification (Semantic Filtering)

### Purpose

For each candidate file, the AI reads the actual file content and makes a
binary decision: **is this file truly impacted by the breaking change?**

If yes, the AI also extracts:
- The exact lines of code that break (verbatim from the file)
- Which breaking patterns apply
- A specific, actionable fix

### Inputs to Phase 3

For each candidate:

| Input | Description |
|---|---|
| `change` block | From Phase 1 output |
| `breaking_patterns` | From Phase 1 output |
| `candidate.hits` | The grep matches found in Phase 2 |
| `file_content` | The full content of the actual file (read from disk) |

The AI **must read the actual file** — not just the grep excerpts. The full file
context is necessary to determine if, e.g., a `SharedInformerFactory` wrapper
correctly delegates the new method or not.

### AI Prompt Contract

For each candidate file, the AI answers:

1. **Is the file impacted?** (`is_impacted: true/false`) — A file is impacted if
   and only if the breaking change would cause a compile error or a silent
   behaviour change in that file specifically.

2. **Which breaking patterns apply?** — A subset of the pattern IDs from Phase 1.

3. **What is the code evidence?** — Verbatim lines from the file (copy-pasted,
   not paraphrased) that demonstrate the breakage.

4. **What is the specific fix?** — A concrete description of the code change
   needed. Not generic advice — it must mention the actual function/field names
   present in this file.

5. **What is the severity?** — One of:
   - `compile_error` — the file will not compile after the change
   - `runtime_regression` — the file compiles but behaviour is wrong
   - `test_only` — only test code breaks; production code is fine

### Rules for Phase 3

1. **`is_impacted = false` if the file only imports the package but does not use
   the changed symbol directly.** Importing `k8s.io/client-go/tools/cache` alone
   is not a breakage if the file never references `SharedInformer` or its methods.

2. **`is_impacted = false` for files that use the type correctly with no
   structural conflict.** E.g. a file that stores `cache.SharedIndexInformer` in a
   `cache.SharedInformer` typed variable already satisfies the interface — it just
   needs to ensure the concrete type it passes has `WaitForCacheSync`.

3. **`is_impacted = true` for files that define a struct that claims to implement
   the interface** (via type assertion `var _ Interface = (*Struct)(nil)` or by
   passing it to a function expecting the interface) but do not have the new method.

4. **`code_evidence` must be exact verbatim lines from the file.** The verifier
   will check these strings exist in the file. Do not paraphrase.

5. **`suggested_fix` must name actual symbols from this file.** Generic fixes like
   "implement the interface" are not acceptable. Say: "Add method
   `WaitForCacheSync(ctx context.Context) bool` to the `sharedInformerFactory`
   struct defined at line 38."

6. **Do not mark a file as impacted purely because it appears in an old ground
   truth.** Do not use external data sources — only the file content and the
   breaking change description.

7. **Cap Phase 3 at 100 files per question.** If there are more candidates than
   this, sort by number of distinct Phase 1 terms matched and take the top 100.

### Phase 3 Output Schema (per candidate)

```json
{
  "repo":               "argo-cd",
  "file":               "pkg/client/informers/externalversions/factory.go",
  "is_impacted":        true,
  "breaking_patterns":  ["factory_wrap", "missing_interface_method"],
  "code_evidence": [
    "func (f *sharedInformerFactory) WaitForCacheSync(stopCh <-chan struct{}) map[reflect.Type]bool {",
    "    return cache.WaitForCacheSync(stopCh, informer.HasSynced)"
  ],
  "severity":       "compile_error",
  "suggested_fix":  "Add WaitForCacheSync(ctx context.Context) bool to the sharedInformerFactory struct (line 38) and delegate to each managed informer's WaitForCacheSync method."
}
```

---

## Phase 4 — Assemble & Write

### Algorithm

```
impacted_files = [entry for entry in phase3_results if entry.is_impacted]
false_positives = [entry for entry in phase3_results if not entry.is_impacted]

# Compute impact_summary
by_pattern = {}
for f in impacted_files:
    for pid in f.breaking_patterns:
        by_pattern[pid] = by_pattern.get(pid, 0) + 1

impact_summary = {
    "total_impacted_files":  len(impacted_files),
    "total_false_positives": len(false_positives),
    "repos_affected":        sorted({f.repo for f in impacted_files}),
    "by_pattern":            by_pattern,
    "by_severity":           {sev: count for sev, count in severity_counts.items()}
}

Write ground_truth_enhanced.json with:
  - change block from Phase 1
  - breaking_patterns from Phase 1
  - impacted_files from Phase 3 (is_impacted=true only)
  - false_positives: [] (Phase 3 rejections are not stored — just dropped)
  - impact_summary computed above
```

### Rules for Phase 4

1. **`false_positives` array is always empty** in the written file. The Phase 3
   rejections are silently dropped. The array exists in the schema for human
   annotation use; the pipeline does not populate it.
2. **`impact_summary.by_pattern` counts** must exactly equal the sum of pattern
   occurrences across `impacted_files`. The script must verify this before writing.
3. **`impact_summary.repos_affected`** must be derived from the actual
   `impacted_files` array, not from the question text.
4. **Do not overwrite an existing file** that has no TODOs and passes schema
   validation, unless `--force` is passed. This prevents re-running the pipeline
   from destroying good manually-reviewed results.

---

## Change-Type Rules

Each breaking-change type has specific requirements for Phase 1 chain-linking.

### `new_interface_method`

Phase 1 **must** enumerate:
- The interface name itself
- All known interfaces that embed it (search the source repo for `interface { ... InterfaceName }`)
- All known concrete types that implement it (search for `var _ InterfaceName = ` and `func (*Type) MethodName`)
- The new method name itself (as a grep term for files that already forward it)
- Factory/builder types that produce the interface
- Test fakes/mocks that implement the interface

### `value_to_pointer`

Phase 1 **must** enumerate:
- `PackageName.FieldType{` — value struct literal initialisation
- `.FieldName = PackageName.FieldType{` — value assignment to the field
- `.FieldName = FieldType{` — same without package prefix (same-package code)
- `: FieldType{` — field in a composite literal
- Functions that return `FieldType` (not `*FieldType`) — return type breaks

### `map_to_named_type`

Phase 1 **must** enumerate:
- `\.FieldName\[` — direct map index read
- `\.FieldName\[.*\] =` — direct map index write
- `range .*\.FieldName` — range loop over the map
- `make(map\[string\]string)` and assignment to the field
- `map\[string\]string{` initialisation assigned to the field
- `= nil` where the field is assigned nil (works for map, breaks for named type if named type has no nil)
- Passing `.FieldName` to a function expecting `map[string]string`

### `field_rename`

Phase 1 **must** enumerate:
- `\.OldFieldName` — all access sites
- `OldFieldName:` — composite literal field key
- `"OldFieldName"` — JSON/YAML tag references (these don't break compilation but may be present)
- Struct definitions that embed the changed struct and shadow the field name

### `signature_change` / add parameter

Phase 1 **must** enumerate:
- The function/method name with call pattern: `FuncName\(`
- All interface definitions that declare this function signature
- All types that implement those interfaces (for the same reasons as `new_interface_method`)
- Struct fields of function type that hold the signature: `type Fn func(...)` aliases

---

## Agentic Model Requirements

The model executing this pipeline must be able to:

1. **Read files from disk** — to load source type definitions and candidate file
   content. This requires a file-read tool.
2. **Run grep** — either via a shell tool or by reading files and searching
   in-memory.
3. **Make multiple sequential decisions** — Phase 1 enrichment, then Phase 2
   grep plan, then per-file Phase 3 verification. The model needs to reason about
   results from prior steps.
4. **Return structured JSON** — all AI outputs must be parseable JSON with the
   schemas defined above. Markdown fences must be stripped before parsing.

Recommended models:
- **Claude Sonnet 4.6** — strong code reasoning, tool use, cost-effective
- **Claude Opus 4.6** — maximum accuracy for ambiguous cases

The pipeline should call these models via the Anthropic SDK (not OpenRouter) for
reliable tool use.

---

## Error Handling Rules

| Situation | Action |
|---|---|
| Phase 1 AI returns invalid JSON | Retry once; if still invalid, fall back to rule-based extraction and mark the question `ai_extraction_failed` |
| Phase 1 cannot find the source file | Log `source_file=TODO`; still attempt Phase 2 with available terms; mark output `source_file_not_found` |
| Phase 2 finds 0 candidates | Write the file with `impacted_files=[]`; log `no_candidates_found` |
| Phase 2 finds >100 candidates | Truncate to 100 (sorted by term match count desc), log `candidates_capped` |
| Phase 3 AI returns invalid JSON for a file | Mark file as `uncertain`; include it in output with `severity=uncertain` and empty `code_evidence` |
| Phase 3 AI unavailable | Write all Phase 2 candidates as-is (grep-only mode), mark output `ai_verification_skipped` |
| Target repo does not exist in `dataset/Kubecluster/` | Skip that repo; log warning |

---

## Quality Checks (after all phases)

After writing `ground_truth_enhanced.json`, the pipeline must self-verify:

1. No field has value `"TODO"` or `""` (except `false_positives` which may be `[]`).
2. `change.source_file` exists on disk at `dataset/Kubecluster/<source_repo>/<source_file>`.
3. Every `impacted_files[].file` exists on disk.
4. Every `code_evidence` string is a substring of the actual file content.
5. `impact_summary.total_impacted_files == len(impacted_files)`.
6. Every pattern ID in `impacted_files[].breaking_patterns` is defined in the
   top-level `breaking_patterns` array.

If any check fails, the pipeline must re-run Phase 3 for the failing entries or
log the failure for manual review.

---

## Directory Structure

```
src/
  populate_enhanced_gt_final.py    ← existing grep+OpenRouter implementation (reference)
  agentic_gt_population.py         ← NEW: implements this pipeline using Anthropic SDK
  verify_enhanced_gt.py            ← verification script (unchanged)

docs/
  plans/
    enhanced_ground_truth_population.md   ← original plan
    agentic_gt_population_pipeline.md     ← THIS DOCUMENT
```
