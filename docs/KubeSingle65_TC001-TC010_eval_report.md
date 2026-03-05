# KubeSingle65 — Evaluation Report: KSR_TC001–TC010

**Scope:** 10 questions from KubeSingle65 (`KSR_TC001` – `KSR_TC010`)

**Models evaluated:**
| Label | File | Mode |
|-------|------|------|
| `claude-direct` | `Claude_Sonnet_4.6_answer.json` | Direct (single non-agentic pass) |
| `grok-direct` | `Grok_code_fast_answer.json` | Direct (single non-agentic pass) |
| `claude-mcp` | `mcp_anthropic_claude-sonnet-4.6_answer.json` | Agentic (MCP tools, multi-step) |
| `grok-mcp` | `mcp_x-ai_grok-code-fast-1_answer.json` | Agentic (MCP tools, multi-step) |
| `gemini-direct` | `gemini_pro_3.1_answer.json` | Direct — TC001 only |

**Date compiled:** 2026-03-02

**Evaluation framework:** `evaluation.md` fact-based marking scheme, scored via `src/evaluate_ksr.py`

---

## 1. Ground Truth Summary

All 10 questions target changes in the **`kubernetes/kubernetes`** monorepo — specifically in the `staging/src/k8s.io/component-helpers/nodedeclaredfeatures` and `staging/src/k8s.io/code-generator` packages. This is the "single-repo" design of KubeSingle65 in contrast to KubeCluster45 (which spanned multiple repos simultaneously).

| TC | GT Files | Max Score | Change Type | Patterns | Severity |
|----|:--------:|:---------:|-------------|----------|----------|
| TC001 | 0 | 0 | `//go:generate` directive removed (no-op change) | — | — |
| TC002 | 5 | 50 | `Feature` interface gains `IsVersionGated() bool` | `missing_interface_method`, `interface_slice_assignment` | 4× compile, 1× test |
| TC003 | 5 | 50 | `FeatureGate.Enabled` gains leading `ctx context.Context` param | `missing_interface_method`, `call_site_arity_mismatch` | 4× compile, 1× test |
| TC004 | 6 | 60 | `MatchResult.UnsatisfiedRequirements` type changes from `[]string` → `FeatureRequirement` | `field_type_mismatch`, `strings_join_incompatible`, `spread_operator_type_mismatch` | 5× compile, 1× test |
| TC005 | 3 | 30 | `NodeConfiguration.Version` changes from `*version.Version` → `version.Version` (ptr→value) | `nil_comparison_on_value_type`, `pointer_assigned_to_value_field` | 2× compile, 1× test |
| TC006 | 1 | 10 | `InferForScheduling` removed from `Feature` interface | `method_call_through_removed_interface_method` | 1× compile |
| TC007 | 2 | 20 | `lintRule` function type signature changes entirely | `old_signature_lint_rule_function` | 1× compile, 1× test |
| TC008 | 0 | 0 | Internal `newLinter` body change — no exported API change | — | — |
| TC009 | 1 | 10 | `lintRules` factory function removed entirely | `undefined_symbol_reference` | 1× compile |
| TC010 | 1 | 10 | `lintComments` reverts from 3 params back to 2 | `call_site_arity_mismatch` | 1× test |
| **Total** | **24** | **240** | | | |

**Key observations:**
- 2 of 10 questions are zero-impact (`TC001`, `TC008`): correct answer is "nothing breaks"
- Questions are weighted small — 24 files across 10 TCs, with TC002–TC004 holding most of the marks
- All impacts are within a single repo (`kubernetes`), making hallucinations into other repos especially penalised

---

## 2. Scoring Scheme

Per `evaluation.md`:

```
Per correct file (max 10 marks):
  File Detection   4  — binary, automated
  Breaking Pattern 0-2 — LLM judge
  Severity         0-1 — LLM judge
  Fix Quality      0-3 — LLM judge

Per hallucinated file:          −5 marks (automated)
Per false positive omitted:     +2 marks (automated)

final_pct = raw_score / max_possible × 100%   (can go negative)
```

This report presents **three score columns** per model:

| Column | Hallucination penalty | Purpose |
|--------|----------------------|---------|
| `−5pen%` | −5 per hallucination | Standard / full-penalty result |
| `−2pen%` | −2 per hallucination | Moderate-penalty recalculation |
| `no-pen%` | 0 | Pure recall+quality ceiling (ignores over-listing) |

For zero-GT-file questions (`max_possible = 0`), the formula is: `final_pct = 100 + raw_score`. Under no-penalty these always score 100%; under penalty they degrade proportionally to hallucinations listed.

---

## 3. Per-Question Score Tables

### TC001 — `//go:generate` removal (GT = 0 files, max = 0)
*Correct answer: "nothing breaks." Any file listed is a hallucination.*

| Model | Hall | −5pen% | −2pen% | no-pen% |
|-------|:----:|-------:|-------:|--------:|
| claude-direct | 0 | **100.0** | **100.0** | **100.0** |
| grok-direct | 0 | **100.0** | **100.0** | **100.0** |
| gemini-direct | 0 | **100.0** | **100.0** | **100.0** |
| claude-mcp | 0 | **100.0** | **100.0** | **100.0** |
| grok-mcp | **6** | 70.0 | 88.0 | 100.0 |

All direct models and claude-mcp correctly identified this as a no-op. Grok-mcp read actual files and still listed 6 false files including `testing/mocks.go` and three test files — despite them being unchanged.

---

### TC002 — `IsVersionGated()` added to `Feature` interface (GT = 5 files, max = 50)

| Model | Found | Missed | Hall | Pos | −5pen% | −2pen% | no-pen% |
|-------|:-----:|:------:|:----:|:---:|-------:|-------:|--------:|
| claude-direct | 5 | 0 | **6** | 45 | 30.0 | 66.0 | 90.0 |
| grok-direct | 4 | 1 | 0 | 35 | **70.0** | **70.0** | 70.0 |
| claude-mcp | 4 | 1 | 0 | 34 | 68.0 | 68.0 | 68.0 |
| grok-mcp | 4 | 1 | 0 | 27 | 54.0 | 54.0 | 54.0 |

Claude-direct found all 5 files but added 6 hallucinations — its positive marks (45/50=90%) are completely eroded by the penalty. Grok-direct, claude-mcp, and grok-mcp all found 4/5 with zero hallucinations; grok-direct edges claude-mcp slightly on dimension scoring.

---

### TC003 — `Enabled(ctx)` new leading param on `FeatureGate` (GT = 5 files, max = 50)

| Model | Found | Missed | Hall | Pos | −5pen% | −2pen% | no-pen% |
|-------|:-----:|:------:|:----:|:---:|-------:|-------:|--------:|
| claude-direct | 5 | 0 | 4 | 34 | 28.0 | 52.0 | 68.0 |
| grok-direct | 4 | 1 | 2 | 16 | 12.0 | 24.0 | 32.0 |
| claude-mcp | 5 | 0 | 4 | 34 | 28.0 | 52.0 | 68.0 |
| grok-mcp | — | — | — | — | *skip* | *skip* | *skip* |

Grok-mcp returned an empty answer (timed out or failed). Claude-direct and claude-mcp are identical — both found all 5 files but added 4 hallucinations each. Grok-direct managed 4/5 but with worse dimension quality and 2 hallucinations, landing last.

---

### TC004 — `MatchResult.UnsatisfiedRequirements` type change (GT = 6 files, max = 60)

| Model | Found | Missed | Hall | Pos | −5pen% | −2pen% | no-pen% |
|-------|:-----:|:------:|:----:|:---:|-------:|-------:|--------:|
| claude-direct | 6 | 0 | 0 | 41 | **68.3** | **68.3** | 68.3 |
| grok-direct | 6 | 0 | 0 | 39 | 65.0 | 65.0 | 65.0 |
| grok-mcp | 4 | 2 | 0 | 28 | 46.7 | 46.7 | 46.7 |
| claude-mcp | **2** | **4** | 0 | 18 | 30.0 | 30.0 | 30.0 |

The clean result — no hallucinations across all models. Direct models dominate: both found all 6 files. Claude-mcp is the worst performer, finding only 2/6 despite spending 14 tool calls and 388K input tokens. Grok-mcp found 4/6. **This is the clearest example of MCP actively underperforming direct inference.**

---

### TC005 — `NodeConfiguration.Version` pointer→value change (GT = 3 files, max = 30)

| Model | Found | Missed | Hall | Pos | −5pen% | −2pen% | no-pen% |
|-------|:-----:|:------:|:----:|:---:|-------:|-------:|--------:|
| claude-direct | 3 | 0 | 0 | 21 | **70.0** | **70.0** | 70.0 |
| claude-mcp | 3 | 0 | 0 | 20 | 66.7 | 66.7 | 66.7 |
| grok-direct | 2 | 1 | 0 | 14 | 46.7 | 46.7 | 46.7 |
| grok-mcp | 2 | 1 | 0 | 12 | 40.0 | 40.0 | 40.0 |

Clean again — zero hallucinations. Claude wins (direct slightly over MCP). Grok finds 2/3 in both modes. Penalty column irrelevant since all hallucinations = 0.

---

### TC006 — `InferForScheduling` removed from interface (GT = 1 file, max = 10)

| Model | Found | Missed | Hall | Pos | −5pen% | −2pen% | no-pen% |
|-------|:-----:|:------:|:----:|:---:|-------:|-------:|--------:|
| claude-direct | 1 | 0 | 0 | 10 | **100.0** | **100.0** | 100.0 |
| claude-mcp | 1 | 0 | 0 | 10 | **100.0** | **100.0** | 100.0 |
| grok-direct | 1 | 0 | 0 | 7 | 70.0 | 70.0 | 70.0 |
| grok-mcp | 1 | 0 | 0 | 7 | 70.0 | 70.0 | 70.0 |

Perfect detection across all four models. Claude achieves full 10/10 dimension score; Grok gets 7/10 (lower breaking-pattern or fix-quality dimension). MCP offers no lift here.

---

### TC007 — `lintRule` function type signature change (GT = 2 files, max = 20)

| Model | Found | Missed | Hall | Pos | −5pen% | −2pen% | no-pen% |
|-------|:-----:|:------:|:----:|:---:|-------:|-------:|--------:|
| claude-mcp | 2 | 0 | 1 | 18 | **65.0** | **80.0** | **90.0** |
| grok-direct | 1 | 1 | 0 | 9 | 45.0 | 45.0 | 45.0 |
| claude-direct | 2 | 0 | 1 | 13 | 40.0 | 55.0 | 65.0 |
| grok-mcp | 2 | 0 | **2** | 13 | 15.0 | 45.0 | 65.0 |

TC007 is claude-mcp's best relative performance. It found both files with higher dimension scores (18 positive marks vs. 13 for claude-direct — better explanation/fix quality). Grok-mcp found both files but hallucinated 2 extras, crashing from 65% no-pen to 15% at −5. The hallucination gap between claude-mcp and grok-mcp is identical in no-pen (both 65%) but grok-mcp's 2 extra hallucinations cost it 50 pct pts at −5 penalty.

---

### TC008 — Internal `newLinter` body change (GT = 0 files, max = 0)
*Correct answer: "nothing breaks."*

| Model | Hall | −5pen% | −2pen% | no-pen% |
|-------|:----:|-------:|-------:|--------:|
| claude-direct | 0 | **100.0** | **100.0** | **100.0** |
| claude-mcp | 0 | **100.0** | **100.0** | **100.0** |
| grok-mcp | 0 | **100.0** | **100.0** | **100.0** |
| grok-direct | — | *skip* | *skip* | *skip* |

Grok-direct returned an empty answer (skipped). All other models correctly identified this as no-impact. Claude-mcp spent 15 tool calls and 415K tokens to arrive at the same answer as claude-direct (86s, 12.5K tokens).

---

### TC009 — `lintRules` factory function removed (GT = 1 file, max = 10)

| Model | Found | Missed | Hall | Pos | −5pen% | −2pen% | no-pen% |
|-------|:-----:|:------:|:----:|:---:|-------:|-------:|--------:|
| claude-direct | 1 | 0 | 0 | 9 | **90.0** | **90.0** | 90.0 |
| claude-mcp | **0** | **1** | 0 | 0 | 0.0 | 0.0 | 0.0 |
| grok-mcp | **0** | **1** | 0 | 0 | 0.0 | 0.0 | 0.0 |
| grok-direct | — | — | — | — | *skip* | *skip* | *skip* |

Claude-direct answered in **9 seconds** and found the single impacted file with 9/10 dimension marks. Both MCP models spent 84–96 seconds and 370–454K tokens to miss the file entirely. This is the starkest efficiency illustration in the dataset.

---

### TC010 — `lintComments` reverts to 2-param signature (GT = 1 file, max = 10)

| Model | Found | Missed | Hall | Pos | −5pen% | −2pen% | no-pen% |
|-------|:-----:|:------:|:----:|:---:|-------:|-------:|--------:|
| grok-direct | 1 | 0 | 1 | 9 | **40.0** | **70.0** | **90.0** |
| claude-direct | 1 | 0 | 1 | 6 | 10.0 | 40.0 | 60.0 |
| claude-mcp | **0** | **1** | 1 | 0 | −50.0 | −20.0 | 0.0 |
| grok-mcp | **0** | **1** | 1 | 0 | −50.0 | −20.0 | 0.0 |

Both MCP models missed the correct file and hallucinated a different one, netting −50% at full penalty. Grok-direct found the correct file with higher dimension quality (9 vs. 6 positive marks), showing the test-only severity of this change was better understood.

---

## 4. Aggregate Score Summary

> Skipped questions excluded from each model's average. −2pen and no-pen recalculated from stored `dimension_totals` and `files_hallucinated`.

### 4.1 Average % Score (per-question mean)

| Model | Qs Scored | −5pen% | −2pen% | no-pen% | Penalty Gap (−5 vs no-pen) |
|-------|:---------:|-------:|-------:|--------:|---------------------------:|
| **claude-direct** | 10 | **63.6** | **74.1** | **81.1** | 17.5 pts |
| grok-direct | 8 | 56.1 | 61.3 | 64.8 | 8.7 pts |
| claude-mcp | 10 | 50.8 | 57.7 | 62.3 | 11.5 pts |
| grok-mcp | 9 | 38.4 | 47.1 | 52.9 | 14.5 pts |

Claude-direct leads across all three penalty regimes. The relatively small penalty gaps (8–18 pts) compared to the KubeCluster45 dataset (37–167 pts) reflects the single-repo scope of these questions — with fewer files to hallucinate across, all models were more precise.

### 4.2 Weighted % Score (total raw / total max)

A more stable metric that weights larger questions proportionally.

**Positive marks totals and hallucination data:**

| Model | Pos Marks | Hall Files | Hall Penalty (−5) | Raw −5pen | Raw −2pen | Max | Wtd −5pen% | Wtd −2pen% | Wtd no-pen% |
|-------|:---------:|:---------:|:-----------------:|:---------:|:---------:|:---:|-----------:|-----------:|------------:|
| claude-direct | 179 | 13 | −65 | 119 | 153 | 240 | **49.6** | **63.8** | **74.6** |
| grok-direct | 129 | 4 | −20 | 114 | 121 | 230¹ | 49.6 | 52.6 | 56.1 |
| claude-mcp | 134 | 6 | −30 | 104 | 122 | 240 | 43.3 | 50.8 | 55.8 |
| grok-mcp | 87 | 11 | −55 | 32 | 65 | 190² | 16.8 | 34.2 | 45.8 |

¹ TC008 and TC009 excluded (skipped) — max reduced to 230.
² TC003 excluded (skipped) — max reduced to 190.

The weighted metric reveals that grok-mcp's aggregate is sharply dragged down by TC001 (6 hallucinations on a 0-GT question), TC007 (2 hallucinations), and TC010 (0 found, 1 hallucinated). Under no-penalty, grok-mcp's positive marks relative to max (87/190 = 45.8%) are actually better than some questions suggest.

### 4.3 Four-Way Score Comparison: −5pen vs −2pen vs no-pen

| Model | −5pen avg | −2pen avg | no-pen avg | Swing (−5→no-pen) |
|-------|----------:|----------:|----------:|------------------:|
| claude-direct | 63.6% | 74.1% | 81.1% | +17.5 pts |
| grok-direct | 56.1% | 61.3% | 64.8% | **+8.7 pts** |
| claude-mcp | 50.8% | 57.7% | 62.3% | +11.5 pts |
| grok-mcp | 38.4% | 47.1% | 52.9% | +14.5 pts |

**Key reading:** Grok-direct has the smallest swing from penalty to no-penalty — it hallucinates least in absolute terms (4 hallucinated files across 8 questions). Claude-direct has the most swing (+17.5 pts) because despite leading in positive marks, it still added 13 hallucinated files — more than any other model.

---

## 5. Timing Deep-Dive

### 5.1 Per-Question Response Times (seconds)

| TC      | GT | claude-direct | grok-direct | claude-mcp | grok-mcp |
|-------  |:--:|:-------------:|:-----------:|:----------:|:--------:|
| TC001   | 0  | 175           | 70          | 52.1       | 82.2 |
| TC002   | 5  | 249           | 60          | 54.1       | **27.3** |
| TC003   | 5  | 172           | 62          | 93.2       | 130.5 |
| TC004   | 6  | **38**        | ⚠️ ~900     | 90.4       | 89.3 |
| TC005   | 3  | 170           | 54          | 219.5      | 121.2 |
| TC006   | 1  | 159           | 100         | 99.5       | 78.1 |
| TC007   | 2  | 960         | 99          | 50.5       | 73.8 |
| TC008   | 0  | 86            | 90          | 92.3       | 77.9 |
| TC009   | 1  | **9**         | 150         | 84.4       | 96.4 |
| TC010   | 1  | 26            | 45          | 49.4       | 45.4 |
| **Avg** |    | **~116s**     | **~81s**¹   | **79s** | **82s** |

¹ Grok-direct TC004 time (≈15 minutes) excluded as an anomaly; median used for the rest.

> N/A = timing metadata not present in answer file.

**Notable timing observations:**

- **TC009 — claude-direct in 9 seconds:** The fastest correct answer in the dataset. Claude-direct's direct reasoning found the single compile-error file (`targets.go` referencing the deleted `lintRules()`) with near-instant confidence. Both MCP models took 84–96 seconds and failed to find it.

- **TC004 — grok-direct ⚠️ ~15 minutes:** An anomaly. Grok-direct took approximately 900 seconds on TC004. Despite this, it found all 6 files correctly (65%). No tool usage, so this was pure inference latency, not agentic overhead.

- **TC005 — claude-mcp 219.5s:** The slowest MCP run in the set. Claude-mcp launched 44 tool calls and 24 agent steps to read through 1.85M input tokens — the largest context window in the dataset — to find 3 files. Claude-direct found the same 3 files in 170s with 28K tokens.

- **MCP convergence:** Both MCP models converge around 50–130s per question regardless of GT complexity, since the agentic setup/teardown and tool calling overhead creates a floor. Direct models have high variance (9s to 249s) correlated with question complexity.

### 5.2 Time vs. Score Efficiency

| Model | Avg Time (s) | Avg −5pen% | Score/Minute |
|-------|:-----------:|:----------:|:------------:|
| claude-direct | ~116 | 63.6% | **32.9 pts/min** |
| grok-direct | ~81¹ | 56.1% | 41.6 pts/min |
| claude-mcp | ~89 | 50.8% | 34.3 pts/min |
| grok-mcp | ~82 | 38.4% | 28.1 pts/min |

¹ Excluding TC004 anomaly.

**Grok-direct has the best score-per-minute ratio** (41.6), combining fast wall-clock responses with clean, hallucination-free answers across 8 questions. Claude-mcp (34.3) edges ahead of grok-mcp (28.1) despite lower scores by running slightly faster on average.

### 5.3 Token Consumption: MCP vs. Direct

| Model | Avg Input Tokens | Avg Output Tokens | Total Context / Q |
|-------|:----------------:|:-----------------:|:-----------------:|
| claude-direct | ~23,900 | ~2,890 | **~26,800** |
| grok-direct | ~2,090¹ | ~640¹ | ~2,730 |
| claude-mcp | **~421,800** | ~3,967 | ~425,800 |
| grok-mcp | **~510,100** | ~6,487 | ~516,600 |

¹ Grok-direct token counts are unreliable (many stored as 0); estimates from available TCs only.

Claude-mcp consumes **~16×** more input tokens than claude-direct per question. Grok-mcp consumes even more. This context inflation reflects the MCP loop: each tool call reads files and appends them to the context, resulting in exponential growth for questions requiring many file reads (TC005: 1.85M tokens for claude-mcp).

### 5.4 Tool Calls & Agent Steps per Question

| TC | GT | claude-mcp tools/steps | grok-mcp tools/steps |
|----|:--:|:----------------------:|:--------------------:|
| TC001 | 0 | 8 / 5 | 16 / 17 |
| TC002 | 5 | 9 / 5 | 3 / 4 |
| TC003 | 5 | 15 / 7 | 25 / 25 |
| TC004 | 6 | 14 / 10 | 18 / 19 |
| TC005 | 3 | **44 / 24** | 25 / 25 |
| TC006 | 1 | 15 / 7 | 16 / 17 |
| TC007 | 2 | 8 / 5 | 17 / 18 |
| TC008 | 0 | 15 / 11 | 12 / 13 |
| TC009 | 1 | 13 / 10 | 14 / 15 |
| TC010 | 1 | 5 / 4 | 5 / 6 |
| **Avg** | | **14.6 / 8.8** | **15.1 / 15.9** |

**Grok-mcp almost always reaches its step cap (25 in TC003 and TC005).** When it hits the cap it submits whatever partial answer it has, which explains the `empty_answer` skip in TC003 and the missed files in TC009/TC010. Claude-mcp has more variable step counts — it terminates early when confident (5 steps on TC001/TC002/TC007) and expands to 24 steps when the problem is harder (TC005).

---

## 6. MCP Strengths

### S1 — Best on multi-step reasoning questions (TC007)
Claude-mcp scored highest overall on TC007 (65%, vs. 40% for claude-direct) by achieving higher dimension marks once it found the files. The agentic loop allowed it to read the actual function type definition, compare before/after, and produce a more specific breaking explanation and fix suggestion — earning higher breaking_pattern and fix_quality scores.

### S2 — Zero hallucination on complex questions
On TC002, TC004, TC005, TC006, TC008, and TC009 — claude-mcp produced zero hallucinated files. For complex questions with many potential decoys in the codebase, the ability to *verify* each candidate file by actually reading it keeps the hallucination rate low. Claude-direct hallucinated 13 files in total; claude-mcp hallucinated only 6.

### S3 — Reliable non-answer for no-impact questions
On the two zero-GT questions (TC001, TC008), claude-mcp correctly returned no impacted files — despite having tool access that could lead it to over-read and report. This demonstrates disciplined confidence: it used tools to verify, then correctly stated nothing breaks.

### S4 — Grok-mcp's extremely fast wins
Grok-mcp answered TC002 in **27.3 seconds** — the fastest agentic response in the dataset — with 3 tool calls / 4 steps. When the problem is tractable from a small, targeted read, grok-mcp's speed-first approach is competitive.

---

## 7. MCP Weaknesses

### W1 — Token explosion on deep searches
TC005 is the extreme case: claude-mcp used **1.85M input tokens** to find 3 files — the same 3 files claude-direct found with 28K tokens. Grok-mcp used 913K. The agentic loop reads every file it visits and appends it to context. On a single-repo change with deep call chains, this compounds quickly.

### W2 — Severe underperformance on TC004 (claude-mcp only)
TC004 is the biggest surprise: claude-direct found all 6 files in 38 seconds and 18K tokens. Claude-mcp found only 2/6 despite 14 tool calls, 388K tokens, and 90 seconds. MCP over-focused on the type change itself, likely reading the definition file exhaustively but failing to grep for all 6 call sites. Direct inference used broader pattern-matching from the full context window.

### W3 — Grok-mcp hits step cap and returns garbage
TC003 (grok-mcp skip), TC005 (25 steps — cap hit), and similar: grok-mcp's agentic loop runs to the maximum step limit without converging, then either returns empty or returns a partial answer. Claude-mcp never hits the cap in this dataset — it terminates when confident.

### W4 — Both MCP models missed TC009 and TC010
A symbol deletion (`lintRules`) and a parameter count revert (`lintComments`) — both single-file changes with straightforward call-site impact. Claude-direct found both in 9s and 26s respectively. The MCP models spent 45–96 seconds each and missed the correct file in both cases, with grok-mcp additionally hallucinating a file in TC010. The MCP loop may have over-complicated the search rather than doing a simple grep for callers.

### W5 — Heavy per-call overhead for 0-GT questions
TC001 and TC008 are no-op changes. Grok-mcp read 555K tokens and made 16 tool calls on TC001 before hallucinating 6 files. Claude-mcp used 415K tokens and 15 tool calls on TC008. Both models' correct answer was "nothing breaks" — but MCP's exploration overhead is unavoidable regardless of whether it ultimately gets the right answer.

---

## 8. Hallucination Profile

| Model | Total Hall | Hall on 0-GT Qs | Hall on >0 GT Qs | Hall Rate¹ |
|-------|:----------:|:----------------:|:-----------------:|:----------:|
| claude-direct | 13 | 0 | 13 | 37.1% |
| grok-direct | 4 | 0 | 4 | 14.3% |
| claude-mcp | 6 | 0 | 6 | 15.4% |
| **grok-mcp** | **11** | **6** | **5** | **37.9%** |

¹ Hall rate = hallucinated / (found + hallucinated). Skipped questions excluded.

**Grok-direct has the cleanest hallucination profile** (4 total, all on >0 GT questions, 14.3% rate). Claude-mcp is similarly clean (6 total, 15.4%). Claude-direct and grok-mcp both hover at ~38% hallucination rates, but for different reasons: claude-direct hallucinates while finding all correct files too (over-completion), while grok-mcp hallucinates even when missing correct files (misdirection).

Notably: **no model hallucinated on zero-GT questions except grok-mcp** (6 on TC001). This suggests grok-mcp's agentic loop is more prone to false confidence when there truly is nothing to find.

---

## 9. Per-Model Rankings

### 9.1 By Average −5pen%

| Rank | Model | −5pen avg | −2pen avg | no-pen avg | Qs |
|:----:|-------|----------:|----------:|----------:|:--:|
| 1 | **claude-direct** | **63.6%** | **74.1%** | **81.1%** | 10 |
| 2 | grok-direct | 56.1% | 61.3% | 64.8% | 8 |
| 3 | claude-mcp | 50.8% | 57.7% | 62.3% | 10 |
| 4 | grok-mcp | 38.4% | 47.1% | 52.9% | 9 |

### 9.2 By Clean Precision (no hallucinations, weighted)

| Model | Files Found | Files Missed | Files Hall | Precision | Recall |
|-------|:-----------:|:------------:|:----------:|:---------:|:------:|
| grok-direct | 22 | 4 | 4 | **84.6%** | 81.5%¹ |
| claude-mcp | 22 | 10 | 6 | **78.6%** | 68.8% |
| claude-direct | 28 | 4 | 13 | 68.3% | **87.5%** |
| grok-mcp | 17 | 13 | 11 | 60.7% | 56.7%² |

¹ Recall = found / (found + missed), over scored questions only.
² TC003 excluded (skip).

Claude-direct has the highest recall (87.5%) — it finds the most files — but lowest precision (68.3%) due to adding hallucinations alongside correct files. Grok-direct and claude-mcp tie on precision (84.6% and 78.6%) with grok-direct having better recall on its 8 scored questions.

---

## 10. Key Findings

### F1 — Direct wins overall at this scale
On 10 single-repo questions with 0–6 impacted files each, **direct (non-agentic) inference is faster, more token-efficient, and scores higher** than MCP across both models. The task scale does not justify the overhead of multi-step tool usage.

### F2 — Claude-direct: best accuracy, worst precision
Claude-direct leads in every aggregate metric, but it consistently over-lists files. Its 13 hallucinations across 10 questions (37.1% hallucination rate) represent a systematic "better safe than sorry" tendency. At −2pen this costs only 74.1% average (vs. 81.1% no-pen), but the gap widens with stricter penalties.

### F3 — Grok-direct: most precise, most coverage gaps
Grok-direct's 4 hallucinations across 8 questions (14.3% rate) is the cleanest profile. However, it returned `empty_answer` on TC008 and TC009 — meaning it either failed or skipped two questions outright. Its coverage per question (81.5% recall on scored questions) is competitive with claude-direct but with 2 zero-score skips dragging the average down.

### F4 — Claude-mcp: MCP done right, but at cost
Claude-mcp scores only ~50% at −5pen (12 pts behind claude-direct) but achieves this with controlled tool use — never hitting step caps, terminating early when confident, and hallucinating only 6 files across 10 questions. The cost: 16× more tokens per question. For questions where understanding context is critical (TC007 dimension quality), MCP shows clear value.

### F5 — Grok-mcp: MCP done wrong at this scale
Grok-mcp is the weakest model by every metric at −5pen (38.4%). It burned 6 hallucinations on a trivially correct no-op question (TC001), hit its step cap on TC003 returning empty, and missed simple single-file changes in TC009/TC010 while still hallucinating adjacent files. The token cost (510K avg) is higher than claude-mcp (422K) with worse results.

### F6 — The −2 penalty shifts the landscape
At −2 penalty, the ranking is identical but gaps narrow significantly. Grok-mcp gains the most (38.4% → 47.1%, +8.7 pts) since its hallucinations are concentrated in fewer, more egregious cases (TC001: 6 at once). Under −2pen, the hallucinations on TC001 alone cost it only 24% pts (vs. 60% at −5pen). Claude-direct's 13 total hallucinations cost it 10.3 pts (vs. 17.5 pts at −5pen).

### F7 — TC009 is the benchmark question for inference quality
Nine-second answer. One file. 90% score. Claude-direct demonstrated that for a clear symbol-deletion change, direct pattern-matching on the change description outperforms 84 seconds of agentic exploration (claude-mcp: 0%). TC009 is the single most diagnostic question for evaluating whether a model can read a change description and translate it to a file-level impact without tool noise.

### F8 — MCP consistently underperforms on tests-only changes
TC007 (test_only severity) was where claude-mcp had its best relative performance — suggesting the agentic loop helps when the change is subtle. But TC010 (also test_only) saw both MCP models score −50% (missed the file, hallucinated another). The difference: TC007 had a function-type signature change requiring cross-file understanding; TC010 was a parameter count revert detectable by a trivial grep. MCP excels at semantic, not syntactic, detection.

---

## 11. Files Produced (per question)

| File | Description |
|------|-------------|
| `ground_truth_enhanced.json` | Structured GT with breaking patterns, code evidence, suggested fixes |
| `enhanced_evaluation.json` | Per-model fact-based scores (−5 penalty regime) |
| `Claude_Sonnet_4.6_answer.json` | Direct Claude Sonnet 4.6 answer (thinking mode, single pass) |
| `Grok_code_fast_answer.json` | Direct Grok Code Fast answer (single pass) |
| `mcp_anthropic_claude-sonnet-4.6_answer.json` | Agentic Claude answer (MCP filesystem tools) |
| `mcp_x-ai_grok-code-fast-1_answer.json` | Agentic Grok answer (MCP filesystem tools) |
| `gemini_pro_3.1_answer.json` | Direct Gemini Pro 3.1 answer (TC001 only) |

Cluster-level summary: `results/KubeSingle65/enhanced_analysis_summary.json`
