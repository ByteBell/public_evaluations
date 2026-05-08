# Evaluation Framework for Enhanced Ground Truth

This document defines the scoring methodology used to evaluate LLM answers against the enhanced ground truth schema (`ground_truth_enhanced.json`). It replaces the previous LLM-judge-as-sole-evaluator approach with a fact-based marking system where each claim is independently verifiable.

---

## Ground Truth Structure (Recap)

Each question's ground truth contains:

- **`change`** — the source of the breaking change (module, file, before/after)
- **`breaking_patterns`** — enumerated code patterns that break (each with an ID)
- **`impacted_files`** — files that WILL break, each with pattern IDs, code evidence, severity, and suggested fix
- **`false_positives`** — files that LOOK relevant but DON'T break

Schema definition: `ground_truth_enhanced.schema.json`

---

## Scoring Dimensions

Each impacted file in the ground truth is a **fact**. A model's answer is scored on how many facts it correctly identifies and how well it understands each one.

### Per Correct Fact (max +10 marks)

| Marks | Dimension | Type | Description |
|:-----:|-----------|------|-------------|
| **4** | File Detection | Binary (0 or 4) | Did the model list this exact file (repo + path)? Either found or not — no partial credit. |
| **2** | Breaking Pattern | Range (0 to 2) | Did the model identify the correct breaking pattern(s) for this file? A file can have multiple patterns (e.g. `direct_index_read` AND `direct_index_write`). Scored by LLM judge as a fraction of patterns correctly identified. |
| **1** | Severity | Binary (0 or 1) | Did the model correctly classify the severity (`compile_error`, `runtime_behavior_change`, or `test_failure`)? Scored by LLM judge |
| **3** | Fix Quality | Range (0 to 3) | Did the model suggest the correct resolution? Scored by LLM judge on a 0-3 scale. Full marks for a fix that matches the ground truth's `suggested_fix`. Partial credit for directionally correct but incomplete fixes. |

**Automated vs LLM-judged breakdown:**

- **4/10 marks are fully automated** — File Detection (4)  require only exact matching against ground truth
- **6/10 marks require an LLM judge** — Breaking Pattern (2) + Fix Quality (3) + Severity (1) need semantic comparison, but are constrained to small, well-defined sub-problems rather than judging entire answers

### Per Hallucinated File (flat -5 marks)

Any file listed by the model that does **not** appear in `impacted_files` incurs a flat penalty of **-5 marks**.

This is deterministic — no LLM judge needed. The file either exists in the ground truth or it doesn't.

**Rationale for flat penalty over sub-component breakdown:** For hallucinated files, there is no ground truth entry to compare against. Scoring "how good is the justification for a non-existent impact" is meaningless and would require the LLM judge to evaluate fiction. A flat penalty is simple, deterministic, and sufficient.

### Per False Positive Correctly Omitted (+2 marks)

Each file in the ground truth's `false_positives` array that the model does **not** list earns **+2 marks**.

This rewards precision — a model that avoids traps in the ground truth's false positive list demonstrates genuine understanding rather than pattern-matching on file names that mention related concepts.

> **Note:** The hallucination penalty already provides indirect reward for avoiding wrong files. The false positive bonus specifically targets files that are *designed to be traps* — they mention Labels, import ObjectMeta, etc., but don't actually break. These are harder to correctly omit than random unrelated files.

---

## Score Calculation

### Maximum Score

```
max_possible = (total_impacted_files × 10) + (total_false_positives × 2)
```

For a question with 18 impacted files and 5 false positives:

```
max_possible = (18 × 10) + (5 × 2) = 190
```

### Raw Score

```
raw_score = sum(per_fact_scores) + sum(false_positive_bonuses) - sum(hallucination_penalties)
```

Where:
- `per_fact_scores` = sum of (File Detection + Breaking Pattern + Severity + Fix Quality) for each correctly detected impacted file
- `false_positive_bonuses` = +2 for each false positive correctly omitted
- `hallucination_penalties` = -2 for each file listed by the model that isn't in `impacted_files`

### Final Percentage

```
final_score = raw_score / max_possible × 100%
```

**The score CAN go negative.** A model that hallucinates many files and finds few correct ones will score below zero. This is intentional — it reflects that the model's output is worse than producing no answer at all. Negative scores are valid and should be reported as-is for honest comparison.

---

## Scoring Examples

### Example 1: Strong Model

Ground truth: 18 impacted files, 3 false positives. Max possible = 186.

- Finds 15/18 files correctly
  - Average per-fact score: 8.5/10 (good pattern identification, mostly correct fixes)
  - Subtotal: 15 × 8.5 = **+127.5**
- Correctly omits all 3 false positives: 3 × 2 = **+6**
- Hallucinated 2 wrong files: 2 × -2 = **-4**

```
raw = 127.5 + 6 - 4 = 125.5
final = 125.5 / 186 × 100% = 
```

### Example 2: Weak Model with Heavy Hallucination

Ground truth: 18 impacted files, 3 false positives. Max possible = 186.

- Finds 5/18 files correctly
  - Average per-fact score: 6/10
  - Subtotal: 5 × 6 = **+30**
- Lists 2 of the 3 false positives as impacted (only 1 correctly omitted): **+2**
- Hallucinated 12 wrong files (including the 2 false positives): 12 × -2 = **-60**

```
raw = 30 + 2 - 24 = 8
final = 8 / 186 × 100% = 
```

### Example 3: Conservative Model

Ground truth: 18 impacted files, 3 false positives. Max possible = 186.

- Finds 8/18 files correctly
  - Average per-fact score: 9/10 (very accurate when it does find files)
  - Subtotal: 8 × 9 = **+72**
- Correctly omits all 3 false positives: 3 × 2 = **+6**
- Zero hallucinated files: **-0**


This model is precise but has low recall — it only found 8/18 files. The scoring correctly reflects that: safe but incomplete.

---

## LLM Judge Usage

The LLM judge is used in a **constrained** capacity — only for two sub-dimensions:

### 1. Breaking Pattern Scoring (0-2 marks)

**Input to judge:**
- Ground truth patterns for this file (e.g. `["direct_index_read", "direct_index_write"]`)
- Model's stated reason/explanation for why this file is affected

**Judge instruction:** Score 0-2 based on what fraction of the ground truth patterns the model correctly identified. If the file has 2 patterns and the model identified 1, score 1/2 = 1.0.

### 2. Fix Quality Scoring (0-3 marks)

**Input to judge:**
- Ground truth `suggested_fix` (e.g. `"secret.Labels.Set(common.LabelKeySecretType, secretType)"`)
- Model's stated fix/change recommendation for this file

**Judge instruction:** Score 0-3:
- **3** — Fix is semantically equivalent to the ground truth fix
- **2** — Fix is directionally correct but missing details (e.g. says "use accessor method" without specifying which one)
- **1** — Fix mentions the right concept but is vague or partially wrong (e.g. "update the Labels usage" without specifics)
- **0** — No fix suggested, or fix is completely wrong

---

## File Matching Rules

When comparing a model's listed files against the ground truth:

### Exact Match
A model's file matches a ground truth entry when `file` path match.

### Path Normalization
- Leading `/` or `./` should be stripped
- Paths are compared case-sensitively (Go repos are case-sensitive)

### Unmatched Files
Any file from the model's answer that does not match any entry in `impacted_files` (after alias resolution and normalization) is counted as a hallucination and incurs the -5 penalty.

---

## Comparison with Previous Evaluation

| Aspect | Previous (`evaluate.py`) | Enhanced |
|--------|--------------------------|----------|
| Ground truth source | LLM-generated prose answer | Structured facts with verifiable evidence |
| Scoring method | LLM judge scores entire answer (60/30/10 weighted) | Per-fact marking with binary + range dimensions |
| Hallucination detection | File-existence check against filesystem | Match against curated ground truth + explicit false positives |
| Automation | ~0% automated (LLM judge for everything) | 50% automated (file detection + severity are exact match) |
| Score range | 0-100% | Unbounded negative to 100% |
| Granularity | Single score per model per question | Per-file breakdown with dimension-level detail |
| Reproducibility | LLM judge variance across runs | Binary dimensions are deterministic; only pattern + fix scoring has variance |
