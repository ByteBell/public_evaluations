# KubeCluster45 — Enhanced Ground Truth & Evaluation Report

**Commit range:** `753a89bd5c24fc29e77af1da7a96367edcdfc3b1` → `f40df19e036707e38757b029e1f574d0868d726b`

**Scope:** 45 questions — 11 MIXED (`MIXED_TC001–011`) + 34 OBS (`OBS_TC001–034`)

**Date compiled:** 2026-02-25

---

## Commits Covered

| SHA (short) | Message |
|-------------|---------|
| `15a88d9` | some general truths enhanced |
| `bd029af` | some more gts |
| `e05f816` | all ground truths enhanced |
| `5a48464` | evaluation enhanced |
| `1e7b88c` | evaluation enhanced |
| `f40df19` | no penalty scores |

Six commits across two work streams: (1) populating `ground_truth_enhanced.json` for all 45 questions, and (2) running and storing `enhanced_evaluation.json` + `enhanced_evaluation_no_penalties.json` for all 45 questions.

---

## 1. Ground Truth Evolution

### 1.1 Format: Before vs After

**Before — `ground_truth.json`**

The original ground truth was produced by a single run of `claude-opus-4.6-direct-data-access`. It had this shape:

```json
{
  "model": "anthropic/claude-opus-4.6-direct-data-access",
  "expected_files": [
    { "repo": "argo-cd", "files": ["pkg/client/informers/externalversions/factory.go"],
      "reason": "Generated SharedInformerFactory managing informer lifecycle" }
  ],
  "answer": "...",
  "llm_condensed_answer": "...",
  "cost": ...,
  "latency_seconds": ...
}
```

The `expected_files` list was the sole source of truth. There were no severity labels, no breaking pattern taxonomy, no code evidence, and no agentic verification — just a file list with free-text reasons, as produced in a single agent run.

**After — `ground_truth_enhanced.json`**

The enhanced GT is produced by a 4-phase agentic pipeline defined in `docs/plans/agentic_gt_population_pipeline.md`. It has a fully structured schema:

```json
{
  "$schema": "...",
  "id": "MIXED_TC001",
  "change": {
    "module": "cache.SharedInformer",
    "source_repo": "kubernetes",
    "source_file": "staging/src/k8s.io/client-go/tools/cache/shared_informer.go",
    "before": "type SharedInformer interface { ... }",
    "after":  "type SharedInformer interface { ... WaitForCacheSync(ctx context.Context) bool }",
    "description": "..."
  },
  "breaking_patterns": [
    { "id": "missing_interface_method", "example": "...", "why_breaks": "..." }
  ],
  "impacted_files": [
    { "repo": "...", "file": "...", "severity": "compile_error",
      "breaking_patterns": ["missing_interface_method"],
      "code_evidence": ["verbatim line from file"],
      "suggested_fix": "concrete fix naming actual symbols" }
  ],
  "false_positives": [],
  "impact_summary": { "total_impacted_files": N, "repos_affected": [...], "by_pattern": {...}, "by_severity": {...} },
  "_pipeline_notes": { "phase1_search_terms": [...], "phase2_candidate_count": {...}, "phase3_verdict": "..." }
}
```

Key structural additions:
- **`change.before`/`change.after`**: verbatim Go code extracted from source repo (Phase 1 reads actual files)
- **`breaking_patterns`**: named, typed taxonomy of how code breaks (e.g., `range_iteration`, `missing_interface_method`, `struct_literal_value`)
- **`impacted_files[].severity`**: one of `compile_error`, `runtime_regression`, `test_only`, `informational`
- **`impacted_files[].code_evidence`**: verbatim lines from the actual file (Phase 3 reads actual files)
- **`impacted_files[].suggested_fix`**: concrete fix naming actual functions/structs/lines, not generic advice
- **`_pipeline_notes`**: audit trail of Phase 1 search terms used, Phase 2 candidate counts per repo, Phase 3 verdict

### 1.2 File Counts: Original vs Enhanced (all 45 questions)

> Source: `ground_truth.json` (`expected_files`) vs `ground_truth_enhanced.json` (`impacted_files`)

| Question | Orig GT | Enh GT | Delta |
|----------|--------:|-------:|------:|
| MIXED_TC001 | 13 | 0 | **-13** |
| MIXED_TC002 | 8 | 11 | +3 |
| MIXED_TC003 | 9 | 30 | **+21** |
| MIXED_TC004 | 9 | 30 | **+21** |
| MIXED_TC005 | 12 | 11 | -1 |
| MIXED_TC006 | 11 | 25 | **+14** |
| MIXED_TC007 | 14 | 16 | +2 |
| MIXED_TC008 | 8 | 8 | 0 |
| MIXED_TC009 | 12 | 40 | **+28** |
| MIXED_TC010 | 11 | 0 | **-11** |
| MIXED_TC011 | 13 | 14 | +1 |
| OBS_TC001 | 12 | 25 | **+13** |
| OBS_TC002 | 13 | 0 | **-13** |
| OBS_TC003 | 11 | 3 | -8 |
| OBS_TC004 | 13 | 15 | +2 |
| OBS_TC005 | 11 | 7 | -4 |
| OBS_TC006 | 11 | 9 | -2 |
| OBS_TC007 | 9 | 1 | -8 |
| OBS_TC008 | 15 | 25 | +10 |
| OBS_TC009 | 14 | 16 | +2 |
| OBS_TC010 | 10 | 3 | -7 |
| OBS_TC011 | 14 | 9 | -5 |
| OBS_TC012 | 13 | 16 | +3 |
| OBS_TC013 | 12 | 9 | -3 |
| OBS_TC014 | 11 | 35 | **+24** |
| OBS_TC015 | 15 | 22 | +7 |
| OBS_TC016 | 12 | 2 | -10 |
| OBS_TC017 | 15 | 17 | +2 |
| OBS_TC018 | 15 | 12 | -3 |
| OBS_TC019 | 12 | 12 | 0 |
| OBS_TC020 | 11 | 12 | +1 |
| OBS_TC021 | 8 | 0 | **-8** |
| OBS_TC022 | 11 | 6 | -5 |
| OBS_TC023 | 7 | 10 | +3 |
| OBS_TC024 | 11 | 8 | -3 |
| OBS_TC025 | 9 | 3 | -6 |
| OBS_TC026 | 9 | 8 | -1 |
| OBS_TC027 | 10 | 6 | -4 |
| OBS_TC028 | 6 | 1 | -5 |
| OBS_TC029 | 8 | 5 | -3 |
| OBS_TC030 | 10 | 5 | -5 |
| OBS_TC031 | 19 | 5 | **-14** |
| OBS_TC032 | 21 | 26 | +5 |
| OBS_TC033 | 11 | 9 | -2 |
| OBS_TC034 | 13 | 21 | +8 |
| **TOTAL** | **522** | **548** | **+26** |

Net change: **+26 files** across 45 questions. The numbers however obscure significant churn — 23 questions had their file count *decrease* (agentic verification removed false positives), and 17 had their count *increase* (the search-plan expansion found files the single-run oracle missed).

### 1.3 Shocking Reversals — Four Questions Dropped to Zero

Four questions, previously claiming 6–13 impacted files in the original GT, were verified to have **zero impacted files** by the enhanced pipeline:

**MIXED_TC001** (`orig=13 → enh=0`)
Change: `WaitForCacheSync(ctx context.Context) bool` added to `cache.SharedInformer`.

Phase 3 verdict (from `_pipeline_notes.phase3_verdict`):
> "None of the four target repos define custom concrete types that explicitly implement `cache.SharedInformer` or `cache.SharedIndexInformer`. All usage is via field storage of concrete implementations created by `cache.NewSharedInformer`/`cache.NewSharedIndexInformer`, struct embedding of the interface type (ClusterInformer in argo-cd auto-inherits the new method via the embedded field), or factory types with their own unrelated WaitForCacheSync signature. No file defines a struct with all required SharedInformer methods, so no file will fail to compile after this change."

The original GT listed 13 files across argo-cd, cert-manager, prometheus, opentelemetry-collector-contrib based on pattern matching. The agentic pipeline, reading actual file content, found that none of them define a struct that would break.

**MIXED_TC010** (`orig=11 → enh=0`)
Change: `HealthCheck(ctx context.Context) error` added to `kubernetes.Interface`.

The pipeline determined that `kubernetes.Interface` is so large (dozens of sub-interface methods) that no downstream project defines their own complete concrete implementor — they all embed `*Clientset`. The original GT had listed 11 files across argo-cd, cert-manager, grafana, helm, opentelemetry-collector-contrib without verifying concrete implementation.

**OBS_TC002** (`orig=13 → enh=0`)
Change: `Labels` type changes from `type Labels []Label` to `type Labels struct { data string }`.

The original GT identified 13 files across prometheus, thanos, mimir, loki. The pipeline found that the actual Labels implementations in those repos were each of the *alternate build-tag variants* (slicelabels, stringlabels, dedupelabels) — i.e., the change was *already represented* across build configurations; no file was genuinely impacted because the repos use their own build-tagged implementations, not a monolithic one.

**OBS_TC021** (`orig=8 → enh=0`)
Change: `QueryableCreator` function type gets a new `deduplicate bool` parameter prepended.

Pipeline determined that none of the target repos (thanos, etc.) define their own `QueryableCreator`-typed functions outside of their own internal packages. The original GT listed 8 files without code evidence; Phase 3 rejected all of them.

### 1.4 Biggest Upward Expansions

These questions were most under-specified in the original GT:

| Question | Orig | Enh | Delta | Key Reason |
|----------|-----:|----:|------:|------------|
| MIXED_TC009 | 12 | 40 | +28 | `AddKnownTypes` variadic → struct — 36 direct call sites + 4 test sites across 4 repos, original missed most |
| OBS_TC014 | 11 | 35 | +24 | `CreateTracesFunc` signature added `*zap.Logger` — 29 files with `signature_mismatch` pattern found by grep |
| MIXED_TC003 | 9 | 30 | +21 | `Containers []Container` → `ContainerList` named type — 26 range iterations break |
| MIXED_TC004 | 9 | 30 | +21 | `ServiceSpec.Type` value → pointer — 18 struct literal sites + 11 compile errors |
| MIXED_TC006 | 11 | 25 | +14 | `Secret.Data` map → `SecretData` interface — 16 range iterations + 12 index reads |
| OBS_TC001 | 12 | 25 | +13 | `Querier.SelectSorted` new interface method — 25 files with `missing_interface_method` |

MIXED_TC009 is the most striking: a change to `runtime.Scheme.AddKnownTypes` touches 40 files in cert-manager, external-secrets, grafana, and opentelemetry-operator — the original GT had 12 files and covered only a subset of repos.

### 1.5 Repo Coverage Corrections

The enhanced pipeline corrected the repo assignment in **26 of 45 questions**. The pattern is consistently: repos were *removed* from the impacted list, not added.

Notable corrections:

| Question | Removed Repos | Added Repos |
|----------|--------------|-------------|
| MIXED_TC001 | argo-cd, cert-manager, opentelemetry-collector-contrib, prometheus | — |
| MIXED_TC003 | opentelemetry-collector-contrib | opentelemetry-operator |
| MIXED_TC007 | opentelemetry-collector-contrib | opentelemetry-operator |
| MIXED_TC010 | argo-cd, cert-manager, grafana, helm, opentelemetry-collector-contrib | — |
| MIXED_TC011 | kubernetes, opentelemetry-collector-contrib | opentelemetry-operator |
| OBS_TC001 | prometheus | — |
| OBS_TC002 | loki, mimir, prometheus, thanos | — |
| OBS_TC031 | loki | — |

The most frequent correction: `opentelemetry-collector-contrib` → `opentelemetry-operator` for MIXED questions (3 occurrences). The original agent confused the two repos. The enhanced pipeline correctly placed the impact in `opentelemetry-operator` after reading actual file content.

### 1.6 Severity Distribution (Enhanced GT)

> Source: `impact_summary.by_severity` across all 45 enhanced GTs

| Severity | Files | % |
|----------|------:|--:|
| compile_error | 381 | 69.5% |
| test_only | 95 | 17.3% |
| runtime_regression | 18 | 3.3% |
| informational | 15 | 2.7% |
| test_failure | 3 | 0.5% |
| *(no severity / zero-file questions)* | — | — |
| **Total** | **548** | 100% |

Roughly 7 in 10 enhanced GT impacted files are classified as `compile_error` — hard, deterministic breaks. The `test_only` category (17.3%) captures test stubs and mocks that implement the changed interface. `runtime_regression` covers cases like `value_to_pointer` changes where the code compiles but nil-dereferences at runtime.

### 1.7 Top Breaking Patterns (Enhanced GT)

| Pattern | Count |
|---------|------:|
| `missing_interface_method` | 79 |
| `interface_method_signature_change` | 37 |
| `direct_variadic_call` | 36 |
| `signature_mismatch_createtracesfunc` | 29 |
| `range_iteration` | 26 |
| `bool_context_call` | 24 |
| `struct_literal_value` | 18 |
| `range_over_map` | 16 |
| `withtrace_factory_option` | 15 |
| `map_index_read` | 13 |

`missing_interface_method` (79 files) is the most common single pattern — driven by the many `new_interface_method` questions where concrete types must add a new method. `range_iteration` (26) and `range_over_map` (16) together reflect the `map_to_named_type` and slice-to-struct change types.

---

## 2. Evaluation Framework Evolution

### 2.1 Before — Single LLM Judge (`evaluation.json`)

The original evaluation (`evaluation.json`) used a single LLM judge scoring each model's full answer on a **relevance_score** (0–100 integer). The judge had no structured rubric: it evaluated the entire answer holistically and produced a free-text `judge_justification` plus a single number.

Example justification for OBS_TC001, claude-haiku-4.5:
> "Found 18 files with better coverage than first response. Still includes some hallucinations like spin_off_subqueries_queryable, loki."

Characteristics of the old approach:
- One score per question per model (no per-file breakdown)
- Partially penalized hallucinations but inconsistently (judge discretion)
- No structured per-file evidence requirement
- Scores ranged 0–100 and could not go negative
- Judge model: `anthropic/claude-haiku-4.5`

### 2.2 After — Fact-Based Marking Scheme (`enhanced_evaluation.json`)

Defined in `evaluation.md`, the new framework replaces the holistic judge with a **fact-based marking scheme**. Each impacted file in the GT is an independent fact worth up to **10 marks**:

| Dimension | Marks | Type |
|-----------|------:|------|
| File Detection | 4 | Binary, automated |
| Breaking Pattern | 0–2 | LLM judge (constrained) |
| Severity | 0–1 | LLM judge (constrained) |
| Fix Quality | 0–3 | LLM judge (constrained) |

**Per hallucinated file: −5 marks (automated, deterministic)**

**Per false positive correctly omitted: +2 marks (automated)**

Score formula:
```
max_possible = (impacted_files × 10) + (false_positives × 2)
raw_score    = Σ(per_fact_scores) + Σ(FP_bonuses) − Σ(hallucination_penalties)
final_pct    = raw_score / max_possible × 100%
```

**Scores can go negative.** A model that hallucinates many files scores below 0%, which is intentional and correct — it is worse than saying nothing.

Infrastructure used:
- Judge model: `anthropic/claude-haiku-4.5`
- Extractor model: `xiaomi/mimo-v2-flash` (extracts structured file lists from model answers)
- Scoring version: `enhanced_v1`

### 2.3 The `enhanced_evaluation_no_penalties.json`

A separate recalculation removes the −5 hallucination penalty entirely. The numerator becomes only the positive marks earned (file detection + breaking pattern + severity + fix quality). This separates two questions:

- **With penalties:** "Is this model a net positive contribution? (Scores honest reward minus confusion added)"
- **Without penalties:** "How much of the true ground truth did this model cover? (Pure recall/quality on correct hits)"

---

## 3. Score Results

### 3.1 Complete Three-Way Comparison

> Columns: `Orig%` = original `evaluation.json` avg `relevance_score`; `Enh%` = enhanced with penalty `avg_final_pct`; `NoPen%` = no-penalty `avg_final_pct`. Sorted by `Enh%` descending.

| Model | Orig% | Enh% | NoPen% | Delta (Enh−Orig) |
|-------|------:|-----:|-------:|----------------:|
| minimax/minimax-m2.5 | 43.44 | **+0.43** | 31.47 | −43.0 |
| google/gemini-3-flash-preview | 51.56 | −6.00 | 31.93 | −57.6 |
| claude-opus-4/aicopilot | 30.48 | −14.28 | 16.14 | −44.8 |
| openai/gpt-5.1-codex-mini | 44.00 | −18.02 | 26.07 | −62.0 |
| deepseek/deepseek-chat-v3.1 | 44.22 | −29.12 | 29.30 | −73.3 |
| xiaomi/mimo-v2-flash | 46.91 | −32.40 | 31.49 | −79.3 |
| openai/gpt-5.1-codex-max | 59.11 | −39.25 | 36.98 | −98.4 |
| x-ai/grok-code-fast-1 | 45.24 | −69.65 | 32.05 | −114.9 |
| anthropic/claude-sonnet-4.6 | 67.71 | −79.30 | 44.54 | **−147.0** |
| openai/gpt-5.2-codex | 3.85 | −87.78 | 11.11 | −91.6 |
| anthropic/claude-haiku-4.5 | 57.73 | −125.12 | 42.32 | **−183.7** |
| **GT Oracle** (claude-opus-4.6-direct) | N/A | −10.95 | **48.81** | N/A |

> Source: `analysis_summary.json` (orig), `enhanced_analysis_summary.json` (enh), per-question `enhanced_evaluation_no_penalties.json` aggregated (no-pen).

### 3.2 Ranking Reversal

**Original ranking (old GT, holistic judge):**
1. claude-sonnet-4.6 — 67.71%
2. gpt-5.1-codex-max — 59.11%
3. claude-haiku-4.5 — 57.73%
4. gemini-3-flash-preview — 51.56%
5. xiaomi/mimo-v2-flash — 46.91%

**Enhanced ranking with penalties:**
1. minimax/minimax-m2.5 — +0.43% *(only model above zero)*
2. gemini-3-flash-preview — −6.00%
3. GT Oracle (claude-opus-4.6-direct) — −10.95%
4. claude-opus-4/aicopilot — −14.28%
5. gpt-5.1-codex-mini — −18.02%
...
10. claude-sonnet-4.6 — −79.30%
11. gpt-5.2-codex — −87.78%
12. claude-haiku-4.5 — −125.12%

**The former leaders are now the worst performers.** Claude Sonnet, which dominated the original evaluation at 67.71%, sits at −79.30% under the new framework. Claude Haiku drops from 3rd to last at −125.12%.

**No-penalty ranking:**
1. GT Oracle (claude-opus-4.6-direct) — 48.81%
2. claude-sonnet-4.6 — 44.54%
3. claude-haiku-4.5 — 42.32%
4. gpt-5.1-codex-max — 36.98%
5. grok-code-fast-1 — 32.05%

With penalties removed, the original ranking partially resurfaces — Sonnet and Haiku re-emerge near the top. This tells us that their *quality on correct hits* is high, but their hallucination volume obliterates the net score under the penalty regime.

### 3.3 Hallucination: The Critical Finding

> Source: `enhanced_analysis_summary.json` — aggregate across 45 questions.

| Model | Files Found | Files Missed | Files Hallucinated | Hall Rate |
|-------|------------:|-------------:|-------------------:|----------:|
| anthropic/claude-haiku-4.5 | 303 | 403 | **1,251** | **80.5%** |
| x-ai/grok-code-fast-1 | 130 | 418 | 521 | 80.0% |
| claude-opus-4/aicopilot | 47 | 426 | 184 | 79.7% |
| anthropic/claude-sonnet-4.6 | 245 | 303 | 524 | 68.1% |
| xiaomi/mimo-v2-flash | 160 | 388 | 414 | 72.1% |
| openai/gpt-5.1-codex-mini | 80 | 468 | 215 | 72.9% |
| openai/gpt-5.1-codex-max | 186 | 362 | 371 | 66.6% |
| deepseek/deepseek-chat-v3.1 | 117 | 431 | 241 | 67.3% |
| google/gemini-3-flash-preview | 123 | 425 | 207 | 62.7% |
| minimax/minimax-m2.5 | 164 | 350 | 209 | 56.0% |
| GT Oracle (claude-opus-4.6-direct) | 252 | 296 | 322 | 56.1% |
| openai/gpt-5.2-codex | 2 | 17 | 15 | 88.2% |

> Hall Rate = `hallucinated / (found + hallucinated)` — proportion of listed files that were wrong.

Claude Haiku hallucinated **1,251 files** — more than twice the entire true GT (548 files). With a flat −5 penalty per hallucination, this generated −6,255 raw penalty marks, overwhelming its +2,483 in positive marks.

Claude Sonnet found the most correct files (245 found) but also hallucinated heavily (524 files). Its raw penalty marks: −2,620 against +1,984 positive.

The **GT Oracle** (claude-opus-4.6-direct-data-access) — the same model that produced the original GT — hallucinated 322 files against 252 correct. Even with direct data access, it has a 56.1% hallucination rate. This is a sobering finding: the model that authored the original ground truth was itself overstating impact.

**Minimax** is the only model that is net-positive (+0.43%) under the penalty regime. It hallucinated 209 files — the second-lowest count (after claude-opus-4/aicopilot's 184), and crucially it *found* 164 correct files, giving it a positive balance.

### 3.4 Penalty Impact Per Model

The gap between no-penalty and with-penalty scores shows exactly how much hallucination is costing each model:

| Model | NoPen% | Enh% | Penalty Gap |
|-------|-------:|-----:|------------:|
| anthropic/claude-haiku-4.5 | 42.32 | −125.12 | **167.4 pts** |
| anthropic/claude-sonnet-4.6 | 44.54 | −79.30 | 123.8 pts |
| x-ai/grok-code-fast-1 | 32.05 | −69.65 | 101.7 pts |
| xiaomi/mimo-v2-flash | 31.49 | −32.40 | 63.9 pts |
| openai/gpt-5.1-codex-max | 36.98 | −39.25 | 76.2 pts |
| openai/gpt-5.1-codex-mini | 26.07 | −18.02 | 44.1 pts |
| deepseek/deepseek-chat-v3.1 | 29.30 | −29.12 | 58.4 pts |
| google/gemini-3-flash-preview | 31.93 | −6.00 | 37.9 pts |
| minimax/minimax-m2.5 | 31.47 | +0.43 | 31.0 pts |
| GT Oracle | 48.81 | −10.95 | 59.8 pts |

Gemini and Minimax have the smallest penalty gaps — they hallucinate less per unit of true recall. Haiku has the biggest gap by far: 167 percentage points lost to hallucination alone.

### 3.5 Per-Question Extremes (Claude Sonnet)

Claude Sonnet's per-question scores under the enhanced penalty framework range wildly:

**Worst 5 questions:**
| Question | Final% | Found | Missed | Hallucinated |
|----------|-------:|------:|-------:|-------------:|
| OBS_TC028 | −1,560% | 1 | 0 | 33 |
| OBS_TC007 | −950% | 0 | 1 | 19 |
| OBS_TC016 | −515% | 1 | 1 | 22 |
| OBS_TC025 | −350% | 3 | 0 | 26 |
| OBS_TC003 | −180% | 2 | 1 | 14 |

**Best 5 questions:**
| Question | Final% | Found | Missed | Hallucinated |
|----------|-------:|------:|-------:|-------------:|
| OBS_TC026 | +75% | 8 | 0 | 1 |
| MIXED_TC009 | +63.5% | 29 | 11 | 2 |
| OBS_TC021 | +70% | 0 | 0 | 6 |
| OBS_TC002 | +55% | 0 | 0 | 9 |
| MIXED_TC010 | +50% | 0 | 0 | 10 |

OBS_TC028 at −1,560% is an extreme outlier: Sonnet listed 33 hallucinated files against 1 correct file in a GT with only 1 impacted file (max_possible ≈ 10). Raw penalty: −165 from hallucinations, +10 from the 1 correct file = −155 raw score, hence the extreme %.

The best questions include three 0-GT-file questions (MIXED_TC010, OBS_TC002, OBS_TC021) where models that listed no files score 100% without penalties. Sonnet still scored 50–70% on these even with penalties (it hallucinated some files but the per-question max_possible is small, so the ratio doesn't go as negative).

### 3.6 Illustrative Per-Question Example: MIXED_TC001

MIXED_TC001 (WaitForCacheSync on SharedInformer) is the cleanest illustration of the framework's behavioral change:

- Enhanced GT: **0 impacted files** (pipeline verified no concrete implementations break)
- Max possible score: 0 (no facts to score)
- No-penalty score: **100%** for every model (correct to identify no impact)
- With-penalty scores: proportional to hallucinations listed

| Model | Hall Count | Final% (with pen) | NoPen% |
|-------|----------:|------------------:|-------:|
| x-ai/grok-code-fast-1 | 0 | **+100%** | 100% |
| deepseek/deepseek-chat-v3.1 | 5 | +75% | 100% |
| google/gemini-3-flash-preview | 7 | +65% | 100% |
| openai/gpt-5.1-codex-max | 7 | +65% | 100% |
| anthropic/claude-sonnet-4.6 | 11 | +45% | 100% |
| openai/gpt-5.1-codex-mini | 11 | +45% | 100% |
| claude-opus-4/aicopilot | 15 | +25% | 100% |
| anthropic/claude-haiku-4.5 | 19 | +5% | 100% |
| GT Oracle (claude-opus-4.6-direct) | 14 | +30% | 100% |
| minimax/minimax-m2.5 | 21 | −5% | 100% |
| xiaomi/mimo-v2-flash | 30 | **−50%** | 100% |

> Source: `results/KubeCluster45/question_MIXED_TC001/enhanced_evaluation.json`

Grok-code-fast-1 correctly identified there was nothing to flag — it listed 0 files and scored perfectly. Xiaomi listed 30 hallucinated files on a question with zero true answers.

The GT Oracle (the model that authored the original 13-file ground truth for this question) now hallucinated 14 files when re-evaluated against the corrected GT, scoring only +30%.

---

## 4. Key Findings & Takeaways

### F1 — The hallucination crisis is universal

Every single model has a hallucination rate above 50%. The best performer under the no-penalty regime (GT Oracle, 48.81%) still listed 322 false files. The fact-based scoring with the −5 penalty is the first framework capable of surfacing this problem numerically rather than absorbing it into holistic scores.

### F2 — Original rankings were systematically wrong

The original evaluation rewarded verbosity. Models that listed more files (even wrong ones) appeared more "thorough" to the holistic judge. Claude Sonnet (#1 at 67.71% orig) is actually the second-most hallucination-prone model in absolute file count (524 hallucinations). The new framework correctly penalizes this.

### F3 — The original GT overstated impact in 4 questions, understated it in many others

The 4 zero-file corrections (MIXED_TC001, MIXED_TC010, OBS_TC002, OBS_TC021) represent the most dramatic reversals — questions where 6–13 files were claimed as impacted but agentic verification found zero. Simultaneously, MIXED_TC009 grew from 12 to 40 files and OBS_TC014 from 11 to 35 — the original agent missed large swaths of the true impact.

### F4 — Repo attribution was corrected in 26/45 questions

26 questions had at least one repo added or removed. The direction is consistently toward precision: repos were removed (false attribution from the original agent) in most cases. The most systematic correction was `opentelemetry-collector-contrib` → `opentelemetry-operator` in 3 MIXED questions.

### F5 — The GT Oracle cannot serve as ground truth

The model that produced the original GT (claude-opus-4.6-direct-data-access) scores −10.95% under the enhanced framework. Its "own" ground truth now classifies 322 of its listed files as hallucinations. This validates the need for a deterministic agentic pipeline (grep + file reads) rather than relying on a single LLM oracle run for ground truth production.

### F6 — No-penalty scores are calibrated and sensible

Under no-penalty scoring, the top models score 26–49%, which feels realistic for a hard code-impact detection task. Haiku and Sonnet are still competitive (42% and 44%) — their underlying detection quality is good. The penalty framework just makes their over-listing behavior costly.

### F7 — Minimax is the only net-positive model (barely)

Minimax/minimax-m2.5 at +0.43% is the sole model above zero under the penalty scheme. Its formula: moderate recall (164/548 files found, 30%), moderate hallucinations (209), and the lowest penalty-to-recall ratio among high-volume models. Still only marginally net-positive — the task remains genuinely hard for all models.

---

## 5. Recalculation with −1 Hallucination Penalty

The original enhanced evaluation uses a **−5 mark flat penalty per hallucinated file**. This section recalculates all scores with a reduced **−1 mark penalty**, keeping every other dimension identical. The recalculation is derived directly from the stored `dimension_totals` in each `enhanced_evaluation.json`:

```
positive_marks = file_detection + breaking_pattern + severity + fix_quality
raw_1pen       = positive_marks + false_positive_bonus + (−1 × files_hallucinated)
final_1pen_pct = raw_1pen / max_possible × 100%
```

For 0-GT-file questions (max_possible = 0):
```
final_1pen_pct = 100 − (1 × files_hallucinated)
```

### 5.1 Four-Way Score Comparison

> Sorted by −1pen score descending. n=45 per model except aicopilot (40), minimax (40, 3 empty_answer skipped), haiku (55), gpt-5.2-codex (3).

| Model | Orig% | −5pen% | **−1pen%** | NoPen% |
|-------|------:|-------:|-----------:|-------:|
| GT Oracle (claude-opus-4.6-direct) | N/A | −10.95 | **36.86** | 48.81 |
| minimax/minimax-m2.5 | 43.44 | +0.46 | **27.16** | 31.47 |
| google/gemini-3-flash-preview | 51.56 | −6.00 | **24.35** | 31.93 |
| openai/gpt-5.1-codex-max | 59.11 | −39.25 | **21.73** | 36.98 |
| anthropic/claude-sonnet-4.6 | 67.71 | −79.30 | **19.77** | 44.54 |
| xiaomi/mimo-v2-flash | 46.91 | −32.40 | **18.72** | 31.49 |
| deepseek/deepseek-chat-v3.1 | 44.22 | −29.12 | **17.61** | 29.30 |
| openai/gpt-5.1-codex-mini | 44.00 | −18.02 | **17.25** | 26.07 |
| x-ai/grok-code-fast-1 | 45.24 | −69.65 | **11.71** | 32.05 |
| claude-opus-4/aicopilot | 30.48 | −14.28 | **10.06** | 16.14 |
| anthropic/claude-haiku-4.5 | 57.73 | −125.12 | **8.83** | 42.32 |
| openai/gpt-5.2-codex | 51.33 | −87.78 | **−8.67** | 11.11 |

### 5.2 What Changes at −1pen

**Under −5 penalty:** Only 1 model was net-positive (minimax at +0.46%). Every other model scored negative.

**Under −1 penalty:** **11 of 12 models are net-positive.** Only gpt-5.2-codex remains negative at −8.67% (answered only 3 questions, 88.2% hallucination rate).

The ranking is stable at the extremes — minimax, gemini, and codex-max stay ahead; haiku and grok stay near the bottom — but absolute scores become readable and positive for almost everyone.

### 5.3 Penalty Sensitivity per Model

Delta between −5pen and −1pen (i.e., how much the lower penalty helps each model):

| Model | −5pen% | −1pen% | Swing |
|-------|-------:|-------:|------:|
| anthropic/claude-haiku-4.5 | −125.12 | +8.83 | **+133.9 pts** |
| anthropic/claude-sonnet-4.6 | −79.30 | +19.77 | +99.1 pts |
| x-ai/grok-code-fast-1 | −69.65 | +11.71 | +81.4 pts |
| openai/gpt-5.2-codex | −87.78 | −8.67 | +79.1 pts |
| openai/gpt-5.1-codex-max | −39.25 | +21.73 | +61.0 pts |
| xiaomi/mimo-v2-flash | −32.40 | +18.72 | +51.1 pts |
| deepseek/deepseek-chat-v3.1 | −29.12 | +17.61 | +46.7 pts |
| GT Oracle | −10.95 | +36.86 | +47.8 pts |
| openai/gpt-5.1-codex-mini | −18.02 | +17.25 | +35.3 pts |
| google/gemini-3-flash-preview | −6.00 | +24.35 | +30.4 pts |
| minimax/minimax-m2.5 | +0.46 | +27.16 | +26.7 pts |
| claude-opus-4/aicopilot | −14.28 | +10.06 | +24.3 pts |

Haiku gains the most (+133.9 pts) because it has the most hallucinations (1,251). At −1 penalty its 303 correct file detections (~2,483 positive marks) start to outweigh the hallucination cost (−1,251 instead of −6,255). Models with fewer hallucinations (Minimax, Gemini) naturally have smaller swings — they were already close to their ceiling.

### 5.4 −1pen Ranking vs Original Ranking

| Rank | Original (holistic judge) | −5pen | −1pen |
|-----:|--------------------------|------:|------:|
| 1 | claude-sonnet-4.6 (67.71%) | minimax (+0.46%) | GT Oracle (36.86%) |
| 2 | gpt-5.1-codex-max (59.11%) | gemini (−6.00%) | minimax (27.16%) |
| 3 | claude-haiku-4.5 (57.73%) | GT Oracle (−10.95%) | gemini (24.35%) |
| 4 | gemini-3-flash (51.56%) | aicopilot (−14.28%) | gpt-5.1-codex-max (21.73%) |
| 5 | xiaomi/mimo (46.91%) | gpt-5.1-codex-mini (−18.02%) | claude-sonnet-4.6 (19.77%) |
| 10 | — | claude-sonnet-4.6 (−79.30%) | aicopilot (10.06%) |
| 11 | — | gpt-5.2-codex (−87.78%) | haiku (8.83%) |
| 12 | — | claude-haiku-4.5 (−125.12%) | gpt-5.2-codex (−8.67%) |

Sonnet recovers from #10 under −5pen to #5 under −1pen. Haiku recovers from last at −125% to #11 at +8.83% — still near the bottom but no longer catastrophically negative. gpt-5.2-codex is the only model that stays negative under both penalty regimes.

### 5.5 Remaining Hallucination Cost at −1pen

Even at −1 per hallucination, the gap between no-penalty and −1pen scores is still meaningful:

| Model | NoPen% | −1pen% | Remaining gap |
|-------|-------:|-------:|--------------:|
| anthropic/claude-haiku-4.5 | 42.32 | 8.83 | **33.5 pts** |
| anthropic/claude-sonnet-4.6 | 44.54 | 19.77 | 24.8 pts |
| x-ai/grok-code-fast-1 | 32.05 | 11.71 | 20.3 pts |
| openai/gpt-5.1-codex-max | 36.98 | 21.73 | 15.3 pts |
| deepseek/deepseek-chat-v3.1 | 29.30 | 17.61 | 11.7 pts |
| GT Oracle | 48.81 | 36.86 | 11.9 pts |
| xiaomi/mimo-v2-flash | 31.49 | 18.72 | 12.8 pts |
| openai/gpt-5.1-codex-mini | 26.07 | 17.25 | 8.8 pts |
| google/gemini-3-flash-preview | 31.93 | 24.35 | 7.6 pts |
| minimax/minimax-m2.5 | 31.47 | 27.16 | **4.3 pts** |

At −1pen, Minimax (4.3 pt gap) and Gemini (7.6 pt gap) are closest to their no-penalty ceiling — they have already absorbed their hallucination cost with minimal damage. Haiku still loses 33.5 points from hallucination even at −1 per file — the raw volume (1,251 hallucinated files) is the problem, not the penalty magnitude.

---

## 6. Files Produced (per question)

Each of the 45 question directories now contains:

| File | Status | Description |
|------|--------|-------------|
| `ground_truth.json` | Unchanged | Original GT from claude-opus-4.6-direct-data-access |
| `ground_truth_enhanced.json` | **New** | 4-phase agentic pipeline GT with full schema |
| `evaluation.json` | Unchanged | Original holistic LLM-judge evaluation |
| `enhanced_evaluation.json` | **New** | Fact-based marking against enhanced GT, with −5 hallucination penalty |
| `enhanced_evaluation_no_penalties.json` | **New** | Same scoring, penalties removed |

Plus two cluster-level aggregates:
- `results/KubeCluster45/analysis_summary.json` — original model summaries (11 models, 45 questions)
- `results/KubeCluster45/enhanced_analysis_summary.json` — enhanced model summaries (12 entries including GT Oracle)
