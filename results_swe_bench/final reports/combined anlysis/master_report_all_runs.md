# SWE-Bench Comprehensive Evaluation Report — All Models, All Runs

**Dataset:** `princeton-nlp/SWE-bench_Verified` — `astropy/astropy`
**Tasks:** 22 tasks from `astropy_tasks.json`
**Judge:** Claude Code (claude-sonnet-4-6)
**Report compiled:** 2026-04-06
**Coverage:** 12 distinct evaluation runs · 5 models · 2 agent platforms · 2 access modes

---

## Table of Contents

1. [Evaluation Framework](#evaluation-framework)
2. [All Runs: Performance Leaderboard](#all-runs-performance-leaderboard)
3. [Grade Distribution (All Runs)](#grade-distribution-all-runs)
4. [Token & Cost Efficiency](#token--cost-efficiency)
5. [Time Analysis](#time-analysis)
6. [Raw vs MCP: Per-Model Delta](#raw-vs-mcp-per-model-delta)
7. [Cross-Agent Comparison: Claude Code vs Kilo](#cross-agent-comparison-claude-code-vs-kilo)
8. [Persistent Hard Tasks](#persistent-hard-tasks)
9. [Failure Pattern Summary](#failure-pattern-summary)

---

## Evaluation Framework

### Scoring Rubric

| Dimension | Weight | What is graded |
|-----------|--------|----------------|
| Root cause identification (RC) | 3 pts | Did the model correctly diagnose *why* the bug exists? |
| Correct file(s) | 2 pts | Did it identify the right file(s) to change? |
| Correct patch / code change | 3 pts | Does the proposed code change match or is functionally equivalent to ground truth? |

**Grade tiers:** ✅ Exact (8/8) · ✅ Near-perfect (7/8) · ⚠️ Partial (5–6/8) · ❌ Fail (≤4/8)

**Maximum possible:** 176 pts (22 tasks × 8 pts)

### Agent Platforms

| Platform | Access Mode | Description |
|----------|-------------|-------------|
| **Claude Code** | Raw | Direct repository access; multi-model (primary + Haiku routing layer) |
| **Claude Code** | MCP | ByteBell knowledge graph via MCP; no direct repo clone; single model |
| **Kilo** | Raw | Kilo agent with direct repository clone; single model; OpenRouter routing |
| **Kilo** | MCP | Kilo agent with ByteBell MCP knowledge graph; no local repo; single model |

### Token Methodology

**Effective Input (Eff Input)** = Input tokens + α × Cache Write tokens + 0.1 × Cache Read tokens

All three input-side token classes are included because all three incur real cost:

| API backend | Cache Write multiplier α | Cache Read multiplier |
|-------------|--------------------------|----------------------|
| Anthropic direct (CC runs 1–4) | **1.25×** | 0.10× |
| OpenAI / GPT | **1.0×** (not separately reported for Kilo runs) | 0.10× |
| Qwen free tier (no caching) | — | — |

**Kilo/OpenRouter runs (5, 7, 8, 9, 11, 12):** Cache Write tokens are not surfaced separately in OpenRouter telemetry, so α × CW = 0 for these runs. Their Eff Input is therefore slightly understated compared to Claude Code runs where CW is fully tracked.

**Output tokens** = generated tokens; reported as-is. For Qwen models, reasoning tokens (chain-of-thought) are generated separately and listed where available.

---

## All Runs: Performance Leaderboard

| # | Model | Agent | Mode | Score | **%** | RC% | Files% | Patch% | Date |
|---|-------|-------|------|-------|-------|-----|--------|--------|------|
| 9 | **Claude Sonnet 4.6** | Kilo | MCP | **166/176** | **94.3%** | 98.5% | 100% | 86.4% | 2026-04-06 |
| 1 | **Claude Sonnet 4.6** | Claude Code | Raw | **164/176** | **93.2%** | 100% | 100% | 81.8% | 2026-04-02 |
| 4 | **Claude Opus 4.6** | Claude Code | MCP | **163/176** | **92.6%** | 97.0% | 100% | 83.3% | 2026-04-01 |
| 3 | **Claude Opus 4.6** | Claude Code | Raw | **162/176** | **92.0%** | 97.0% | 100% | 81.8% | 2026-03-31 |
| 10 | **Qwen 3.6 Plus** | Kilo | MCP | **160/176** | **90.9%** | 97.0% | 100% | 78.8% | 2026-04-03 |
| 2 | **Claude Sonnet 4.6** | Claude Code | MCP | **158/176** | **89.8%** | 98.5% | 100% | 74.2% | 2026-04-02 |
| 7 | **GPT-5.4 Mini** | Kilo | Raw | **156/176** | **88.6%** | 95.5% | 97.7% | 75.8% | 2026-04-03 |
| 6 | **Qwen 3.6 Plus** | Kilo | Raw | **146/176** | **83.0%** | 92.4% | 95.5% | 65.2% | 2026-04-03 |
| 5 | **Claude Sonnet 4.6** | Kilo | Raw | **145/176** | **82.4%** | 89.4% | 97.7% | 65.2% | 2026-04-05† |
| 11 | **GPT-5.4 Mini** | Kilo | MCP | **142/176** | **80.7%** | 87.9% | 93.2% | 65.2% | 2026-04-05 |
| 8 | **GPT-5.4 Nano** | Kilo | Raw | **129/176** | **73.3%** | 87.9% | 90.9% | 47.0% | 2026-04-03 |
| 12 | **GPT-5.4 Nano** | Kilo | MCP | **118/176** | **67.0%** | 75.8% | 81.8% | 48.5% | 2026-04-03 |

> **Run 9 note:** Directory `auto_run_on_mcp_kilo_anthropic_claude-sonnet-4.6`. The `run_manifest.json` files recorded a different model name due to a logging bug during concurrent execution; telemetry and stdout confirm Claude Sonnet 4.6. Cost $18.68. Highest overall score of all 12 runs.
>
> **Run 10 note:** Directory `auto_run_on_mcp_kilo_qwen_qwen3.6-plus:free` — free tier, $0.00.
>
> **Run 12 note:** Directory `auto_run_on_mcp_kilo_openai_gpt-5.4-nano`. OTel logging recorded a different model name (logging bug); the actual model is GPT-5.4 Nano. Score suppressed by MCP environment failures: `apply_patch` tool unavailable without a local repo clone.
>
> **Run 5 note (†):** Tasks 14995 and 7166 were re-run on 2026-04-06 to recover missing metrics. All aggregates now cover all 22 tasks. Scores unchanged.

### Dimension Breakdown (All Runs)

| # | Model | Agent | Mode | RC (66 max) | RC% | Files (44 max) | Files% | Patch (66 max) | Patch% | Total |
|---|-------|-------|------|-------------|-----|----------------|--------|----------------|--------|-------|
| 9 | Claude Sonnet 4.6 | Kilo | MCP | 65 | 98.5% | 44 | **100%** | 57 | **86.4%** | **166** |
| 1 | Claude Sonnet 4.6 | Claude Code | Raw | 66 | **100%** | 44 | **100%** | 54 | 81.8% | 164 |
| 4 | Claude Opus 4.6 | Claude Code | MCP | 64 | 97.0% | 44 | **100%** | 55 | 83.3% | 163 |
| 3 | Claude Opus 4.6 | Claude Code | Raw | 64 | 97.0% | 44 | **100%** | 54 | 81.8% | 162 |
| 10 | Qwen 3.6 Plus | Kilo | MCP | 64 | 97.0% | 44 | **100%** | 52 | 78.8% | 160 |
| 2 | Claude Sonnet 4.6 | Claude Code | MCP | 65 | 98.5% | 44 | **100%** | 49 | 74.2% | 158 |
| 7 | GPT-5.4 Mini | Kilo | Raw | 63 | 95.5% | 43 | 97.7% | 50 | 75.8% | 156 |
| 6 | Qwen 3.6 Plus | Kilo | Raw | 61 | 92.4% | 42 | 95.5% | 43 | 65.2% | 146 |
| 5 | Claude Sonnet 4.6 | Kilo | Raw | 59 | 89.4% | 43 | 97.7% | 43 | 65.2% | 145 |
| 11 | GPT-5.4 Mini | Kilo | MCP | 58 | 87.9% | 41 | 93.2% | 43 | 65.2% | 142 |
| 8 | GPT-5.4 Nano | Kilo | Raw | 58 | 87.9% | 40 | 90.9% | 31 | 47.0% | 129 |
| 12 | GPT-5.4 Nano | Kilo | MCP | 50 | 75.8% | 36 | 81.8% | 32 | 48.5% | 118 |

**Key observations:**
- **Patch quality is the primary discriminator.** RC and file identification are nearly always high (≥88% across successful runs); patch correctness ranges from 47% to 86% and determines the final rank.
- **Claude Sonnet 4.6 on Claude Code is the only run achieving 100% RC.** Every other run missed the root cause on at least one task.
- **File identification is consistently ≥90%** except in run 12 (GPT Nano MCP, env failures) and run 8 (GPT Nano Raw). Identifying the correct file is an easier sub-task than constructing the correct patch.

---

## Grade Distribution (All Runs)

| # | Model | Agent | Mode | ✅ Exact (8/8) | ✅ Near-Perf (7/8) | ⚠️ Partial (6/8) | ⚠️ Partial (5/8) | ❌ Fail (≤4/8) | E+NP% |
|---|-------|-------|------|---------------|-------------------|-----------------|-----------------|----------------|-------|
| 9 | Claude Sonnet 4.6 | Kilo | MCP | **14** | 7 | 0 | 1 | 0 | **95.5%** |
| 1 | Claude Sonnet 4.6 | Claude Code | Raw | **14** | 5 | 2 | 1 | 0 | **86.4%** |
| 4 | Claude Opus 4.6 | Claude Code | MCP | 13 | 6 | 2 | 1 | 0 | 86.4% |
| 3 | Claude Opus 4.6 | Claude Code | Raw | 14 | 5 | 1 | 1 | **1** | 86.4% |
| 10 | Qwen 3.6 Plus | Kilo | MCP | 11 | 7 | 1 | 2 | 1 | 81.8% |
| 2 | Claude Sonnet 4.6 | Claude Code | MCP | 7 | **13** | 1 | 1 | 0 | **90.9%** |
| 7 | GPT-5.4 Mini | Kilo | Raw | 10 | 8 | 1 | 2 | 1 | 81.8% |
| 6 | Qwen 3.6 Plus | Kilo | Raw | 7 | 9 | 2 | 2 | 2 | 72.7% |
| 5 | Claude Sonnet 4.6 | Kilo | Raw | 5 | 9 | 5 | 1 | 2 | 63.6% |
| 11 | GPT-5.4 Mini | Kilo | MCP | 5 | 9 | 3 | 2 | 3 | 63.6% |
| 8 | GPT-5.4 Nano | Kilo | Raw | 3 | 7 | 4 | 4 | 4 | 45.5% |
| 12 | GPT-5.4 Nano | Kilo | MCP | 2 | 11 | 1 | 2 | 6 | 59.1% |

> **Exact + Near-perfect %** (E+NP%) captures the top-tier quality rate: tasks where the model produced a functionally correct or near-correct fix.

**Key observations:**
- **Run 9 (Sonnet 4.6 Kilo MCP) leads with 14 Exact matches** — tied with Claude Sonnet CC Raw — and zero complete failures. Kilo MCP is the highest-scoring configuration for Claude Sonnet.
- **Claude Sonnet MCP (run 2) produces the most Near-perfects (13/22)** but only 7 Exact. MCP constrains the model to targeted retrieval, producing correct logic with slightly different style.
- **Claude Opus Raw (run 3) has the only true failure on Claude Code** (task 7606: no patch proposed at all). Sonnet and both MCP runs eliminate all failures.
- **Run 12's 6 failures are structural** (apply_patch tool unavailable in GPT Nano MCP mode) rather than reasoning failures.

---

## Token & Cost Efficiency

### Effective Token Usage Per Task

> **Eff Input = (Input tokens + 0.1 × Cache Read tokens) / N tasks**
> Cost-normalized context consumption per task. Cache reads are priced at 10% of standard input, so each cache-read token contributes 0.1 to this metric. Models without prompt caching (Qwen runs, GPT Mini MCP) show raw input token accumulation.
>
> **Output = total generated tokens / N tasks**
> For Qwen, includes reasoning tokens (chain-of-thought); noted separately where available.

| # | Model | Agent | Mode | Eff Input / task | Output / task | Notes on caching |
|---|-------|-------|------|-----------------|---------------|------------------|
| 11 | GPT-5.4 Mini | Kilo | MCP | **30K** | 2.0K | No cache (CR=0); leanest run overall |
| 2 | Claude Sonnet 4.6 | Claude Code | MCP | **55K** | 9.1K | Input+1.25×CW+0.1×CR; CW fully tracked (Anthropic direct) |
| 7 | GPT-5.4 Mini | Kilo | Raw | **58K** | 3.2K | Input+0.1×CR; CW not reported by OpenRouter |
| 4 | Claude Opus 4.6 | Claude Code | MCP | **78K** | 5.7K | Input+1.25×CW+0.1×CR; CW fully tracked |
| 8 | GPT-5.4 Nano | Kilo | Raw | **120K** | 10.2K | Input+0.1×CR; CW not reported |
| 1 | Claude Sonnet 4.6 | Claude Code | Raw | **126K** | 19.7K | Input+1.25×CW+0.1×CR; CW=1.02M tracked |
| 3 | Claude Opus 4.6 | Claude Code | Raw | **130K** | 12.6K | Input+1.25×CW+0.1×CR; CW=1.06M tracked |
| 12 | GPT-5.4 Nano | Kilo | MCP | **187K** | 3.2K | Input+0.1×CR; CW not reported; env failures inflate CR |
| 9 | Claude Sonnet 4.6 | Kilo | MCP | **190K** | 14.0K | Input+0.1×CR; CW not reported; highest scoring run |
| 5 | Claude Sonnet 4.6 | Kilo | Raw | **206K** | 23.6K | Input+0.1×CR; CW not reported; all 22 tasks |
| 10 | Qwen 3.6 Plus | Kilo | MCP | **656K** | 9.1K | No caching; full prompt each step; incl. 3.6K reasoning |
| 6 | Qwen 3.6 Plus | Kilo | Raw | **1,321K** | 32.4K | No caching; full context each call; incl. 26.3K reasoning |

> **Qwen reasoning tokens** (not included in Eff Input, generated alongside output):
> - Qwen Raw: 26,320 reasoning tokens/task avg (81% of output is reasoning)
> - Qwen MCP: 3,570 reasoning tokens/task avg (39% of output is reasoning)

### Comprehensive Cost Comparison

| # | Model | Agent | Mode | Score | Total Cost | Avg Cost / task | Cost / point | Eff Input / task |
|---|-------|-------|------|-------|-----------|-----------------|--------------|-----------------|
| 6 | Qwen 3.6 Plus | Kilo | Raw | 146/176 | **$0.00** | **$0.00** | **$0.00** | 1,321K |
| 10 | Qwen 3.6 Plus | Kilo | MCP | 160/176 | **$0.00** | **$0.00** | **$0.00** | 656K |
| 8 | GPT-5.4 Nano | Kilo | Raw | 129/176 | $0.808 | **$0.037** | **$0.006** | 120K |
| 12 | GPT-5.4 Nano | Kilo | MCP | 118/176 | $0.912 | **$0.041** | **$0.008** | 187K |
| 7 | GPT-5.4 Mini | Kilo | Raw | 156/176 | $1.117 | **$0.051** | **$0.007** | 58K |
| 11 | GPT-5.4 Mini | Kilo | MCP | 142/176 | $1.228 | **$0.056** | **$0.009** | 30K |
| 2 | Claude Sonnet 4.6 | Claude Code | MCP | 158/176 | $6.60 | $0.300 | $0.042 | **23K** |
| 4 | Claude Opus 4.6 | Claude Code | MCP | 163/176 | $11.53 | $0.524 | $0.071 | **38K** |
| 1 | Claude Sonnet 4.6 | Claude Code | Raw | 164/176 | $11.83 | $0.538 | $0.072 | 68K |
| 3 | Claude Opus 4.6 | Claude Code | Raw | 162/176 | $16.16 | $0.734 | $0.100 | 70K |
| 9 | Claude Sonnet 4.6 | Kilo | MCP | **166/176** | $18.68 | $0.849 | $0.113 | 190K |
| 5 | Claude Sonnet 4.6 | Kilo | Raw | 145/176 | $22.55 | $1.025 | $0.155 | 206K |

> †Run 5 metrics recovered via re-run on 2026-04-06; all 22 tasks now included.

**Key cost observations:**
- **GPT-5.4 Mini Raw delivers the best cost/point ($0.007) at 88.6% accuracy** — by far the most cost-efficient non-free option.
- **Qwen free tier (runs 6, 10) achieves 83.0% and 90.9% respectively at $0** — outstanding value when the free tier is available.
- **Claude Code MCP cuts cost vs Raw by 44% for Sonnet ($6.60 vs $11.83) and 29% for Opus ($11.53 vs $16.16)** while maintaining comparable accuracy.
- **Claude Sonnet on Kilo MCP (run 9, $18.68) achieves the highest score (94.3%)** but at a premium — Kilo routes through OpenRouter with per-token pricing that negates any free-tier benefit.
- **Kilo Sonnet Raw is the most expensive per-task ($1.03) and per-point ($0.155)** — high cache-read volume on OpenRouter pricing makes large-context traversal costly.

---

## Time Analysis

| # | Model | Agent | Mode | Total Time (s) | **Avg Time / task (s)** | Fastest Task (s) | Slowest Task (s) | Timeout Issues |
|---|-------|-------|------|---------------|------------------------|-----------------|-----------------|----------------|
| 11 | GPT-5.4 Mini | Kilo | MCP | 813 | **37** | 18 | 80 | None |
| 12 | GPT-5.4 Nano | Kilo | MCP (env-fail) | 1,779 | **81** | 13 | 175 | None |
| 2 | Claude Sonnet 4.6 | Claude Code | MCP | 3,273 | **149** | 41 | 385 | None |
| 9 | Claude Sonnet 4.6 | Kilo | MCP | 5,809 | **264** | 63 | 1,291 | None |
| 10 | Qwen 3.6 Plus | Kilo | MCP | 5,919 | **269** | 41 | 997 | None |
| 3 | Claude Opus 4.6 | Claude Code | Raw | 5,528 | **251** | 100 | 612 | None |
| 4 | Claude Opus 4.6 | Claude Code | MCP | 5,474 | **249** | 43 | 845 | None |
| 1 | Claude Sonnet 4.6 | Claude Code | Raw | 6,826 | **310** | 22 | 1,637 | None |
| 7 | GPT-5.4 Mini | Kilo | Raw | 9,895 | **450** | 4 | 1,307 | 7 tasks @ ~1,306s |
| 5 | Claude Sonnet 4.6 | Kilo | Raw | 10,488 | **477** | 27 | 2,851 | None (45-min cap) |
| 6 | Qwen 3.6 Plus | Kilo | Raw | 18,894 | **859** | 56 | 3,015 | None |
| 8 | GPT-5.4 Nano | Kilo | Raw | 21,544 | **979** | 14 | 2,685 | 8 tasks @ ~2,684s |

> †Run 5 metrics recovered; all 22-task totals reflected above.

**Key time observations:**
- **GPT Mini MCP is 12× faster than GPT Mini Raw (37s vs 450s avg)** — the most dramatic speedup in the entire evaluation. MCP eliminates all repository traversal.
- **Qwen MCP is 3.2× faster than Qwen Raw (269s vs 859s avg)** — MCP reduces Qwen's avg input from 1.32M to 0.66M tokens, cutting step count by >50%.
- **Claude Code MCP is 2.1× faster than Raw for Sonnet (149s vs 310s)** and essentially tied for Opus (249s vs 251s). Opus's MCP overhead (deeper reasoning per step) offsets the traversal savings.
- **GPT Mini Raw has systematic 1,306s timeouts** (7 of the first 11 tasks hit a ~21-min wall-clock limit). Later tasks with no timeout ran in 4–354s — vastly faster.
- **GPT Nano Raw has systematic 2,684s timeouts** (8 tasks hit a ~45-min limit). Nano requires dramatically more steps to achieve similar coverage.
- **Claude Sonnet on Kilo Raw is 54% slower than on Claude Code Raw** (477s vs 310s) with a significantly lower score — suggesting the Kilo scaffolding is less optimized for Claude's tooling patterns.

---

## Raw vs MCP: Per-Model Delta

### Claude Sonnet 4.6 — Claude Code

| Metric | Raw (Run 1) | MCP (Run 2) | Delta | Winner |
|--------|-------------|-------------|-------|--------|
| Score | 164/176 (93.2%) | 158/176 (89.8%) | −6 pts / −3.4 pp | **Raw** |
| RC% | **100%** | 98.5% | −1.5 pp | **Raw** |
| Files% | 100% | 100% | — | Tie |
| Patch% | **81.8%** | 74.2% | −7.6 pp | **Raw** |
| Exact (8/8) | **14** | 7 | −7 | **Raw** |
| Near-perfect (7/8) | 5 | **13** | +8 | **MCP** |
| Fails | 0 | 0 | — | Tie |
| Avg time/task | 310s | **149s** | **−52%** | **MCP** |
| Avg cost/task | $0.538 | **$0.300** | **−44%** | **MCP** |
| Eff Input/task | 126K | **55K** | **−56%** | **MCP** |
| Output/task | 19.7K | **9.1K** | **−54%** | **MCP** |

> MCP is 1.8× cheaper, 2.1× faster, and 2.3× leaner on cost-normalized tokens (55K vs 126K Eff Input/task). Raw is 3.4 pp more accurate with 2× more exact matches. Trade-off is sharp and consistent. Note: both runs use Anthropic direct API; cache writes are fully tracked and included in Eff Input at 1.25× rate.

---

### Claude Opus 4.6 — Claude Code

| Metric | Raw (Run 3) | MCP (Run 4) | Delta | Winner |
|--------|-------------|-------------|-------|--------|
| Score | 162/176 (92.0%) | 163/176 (92.6%) | +1 pt / +0.6 pp | **MCP** |
| RC% | 97.0% | 97.0% | — | Tie |
| Files% | 100% | 100% | — | Tie |
| Patch% | 81.8% | **83.3%** | +1.5 pp | **MCP** |
| Exact (8/8) | **14** | 13 | −1 | **Raw** |
| Near-perfect (7/8) | 5 | **6** | +1 | **MCP** |
| Fails | **1** (task 7606) | 0 | −1 | **MCP** |
| Avg time/task | 251s | **249s** | −0.8% | Tie |
| Avg cost/task | $0.734 | **$0.524** | **−29%** | **MCP** |
| Eff Input/task | 130K | **78K** | **−40%** | **MCP** |
| Output/task | 12.6K | **5.7K** | **−55%** | **MCP** |

> For Opus, MCP is strictly better: higher score, zero failures, 29% cheaper, 40% leaner on cost-normalized tokens (78K vs 130K Eff Input/task), nearly identical speed. MCP eliminates Opus's only outright failure (task 7606). Both runs use Anthropic direct API with full CW tracking at 1.25× rate.

---

### Claude Sonnet 4.6 — Kilo

| Metric | Raw (Run 5) | MCP (Run 9) | Delta | Winner |
|--------|-------------|-------------|-------|--------|
| Score | 145/176 (82.4%) | **166/176 (94.3%)** | **+21 pts / +11.9 pp** | **MCP** |
| RC% | 89.4% | **98.5%** | +9.1 pp | **MCP** |
| Files% | 97.7% | **100%** | +2.3 pp | **MCP** |
| Patch% | 65.2% | **86.4%** | +21.2 pp | **MCP** |
| Exact (8/8) | 5 | **14** | +9 | **MCP** |
| Near-perfect (7/8) | 9 | 7 | −2 | **Raw** |
| Fails | **2** | 0 | −2 | **MCP** |
| Avg time/task | 477s | **264s** | **−45%** | **MCP** |
| Avg cost/task | $1.025 | $0.849 | −17% | **MCP** |
| Eff Input/task | 206K | **190K** | −8% | **MCP** |
| Output/task | 23.6K | **14.0K** | −41% | **MCP** |

> **Kilo MCP is a dramatic win for Claude Sonnet.** The MCP knowledge graph eliminates the two hallucination failures seen in raw mode, triples the exact-match count (5→14), and lifts Sonnet from the worst Claude configuration (82.4%) to the best result in the entire evaluation (94.3%). Cost and token footprint also improve. This is the strongest Raw→MCP uplift across all models.

---

### GPT-5.4 Mini — Kilo

| Metric | Raw (Run 7) | MCP (Run 11) | Delta | Winner |
|--------|-------------|--------------|-------|--------|
| Score | 156/176 (88.6%) | 142/176 (80.7%) | −14 pts / −7.9 pp | **Raw** |
| RC% | **95.5%** | 87.9% | −7.6 pp | **Raw** |
| Files% | **97.7%** | 93.2% | −4.5 pp | **Raw** |
| Patch% | **75.8%** | 65.2% | −10.6 pp | **Raw** |
| Exact (8/8) | **10** | 5 | −5 | **Raw** |
| Near-perfect (7/8) | 8 | **9** | +1 | **MCP** |
| Fails | 1 (task 13398) | **3** | +2 | **Raw** |
| Avg time/task | 450s | **37s** | **−92%** | **MCP** |
| Avg cost/task | $0.051 | $0.056 | +10% | **Raw** |
| Eff Input/task | 58K | **30K** | **−48%** | **MCP** |
| Output/task | 3.2K | **2.0K** | **−38%** | **MCP** |

> MCP is dramatically faster (12×) and 48% leaner on cost-normalized tokens, but scores 7.9 pp lower. The 3 MCP failures are structural (`apply_patch` unavailable without a local repo clone for tasks 13398, 14369, 7606) rather than reasoning failures. If the environment issue is resolved, MCP parity with raw is plausible.

---

### GPT-5.4 Nano — Kilo

| Metric | Raw (Run 8) | MCP (Run 12) | Delta | Winner |
|--------|-------------|--------------|-------|--------|
| Score | 129/176 (73.3%) | 118/176 (67.0%) | −11 pts / −6.3 pp | **Raw** |
| RC% | **87.9%** | 75.8% | −12.1 pp | **Raw** |
| Files% | **90.9%** | 81.8% | −9.1 pp | **Raw** |
| Patch% | **47.0%** | 48.5% | +1.5 pp | Tie |
| Exact (8/8) | 3 | **2** | −1 | **Raw** |
| Near-perfect (7/8) | 7 | **11** | +4 | **MCP** |
| Fails | **4** | **6** | +2 | **Raw** |
| Avg time/task | 979s | **81s** | **−92%** | **MCP** |
| Avg cost/task | $0.037 | $0.041 | +11% | **Raw** |
| Eff Input/task | 120K | **187K** | +56% | **Raw** |
| Output/task | 10.2K | **3.2K** | −69% | **MCP** |

> MCP is 12× faster but 6.3 pp less accurate. The 6 MCP failures are structural (`apply_patch` environment failures), same root cause as GPT Mini MCP. Nano's raw patch quality (47%) is already the lowest of any run; the MCP environment failures compound this. Nano's main advantage — very low cost ($0.037–0.041/task) — is preserved in both modes.

---

### Qwen 3.6 Plus — Kilo

| Metric | Raw (Run 6) | MCP (Run 10) | Delta | Winner |
|--------|-------------|--------------|-------|--------|
| Score | 146/176 (83.0%) | 160/176 (90.9%) | **+14 pts / +7.9 pp** | **MCP** |
| RC% | 92.4% | **97.0%** | +4.6 pp | **MCP** |
| Files% | 95.5% | **100%** | +4.5 pp | **MCP** |
| Patch% | 65.2% | **78.8%** | +13.6 pp | **MCP** |
| Exact (8/8) | 7 | **11** | +4 | **MCP** |
| Fails | **2** | 1 | −1 | **MCP** |
| Avg time/task | 859s | **269s** | **−69%** | **MCP** |
| Avg cost/task | $0.00 | $0.00 | — | Tie |
| Eff Input/task | 1,321K | **656K** | **−50%** | **MCP** |
| Output/task | 32.4K (incl. 26K reasoning) | **9.1K** (incl. 3.6K reasoning) | **−72%** | **MCP** |

> **MCP uniformly improves Qwen across every dimension.** The free MCP run gains +7.9 pp over raw at identical cost ($0). Raw burns 1.32M tokens/task with no caching — the full prompt is rebuilt each step. MCP halves token consumption and cuts reasoning tokens from 26K to 3.6K per task by narrowing the search space.
>
> **The two hallucination failures in Qwen Raw (tasks 8707, 14369)** — where the model incorrectly asserts the fix is already present — are substantially resolved by MCP: task 8707 jumps from 2/8 to 8/8 (Exact); task 14369 partially recovers. Structured graph retrieval prevents the code-state hallucination failure mode.

---

### Claude Sonnet 4.6 — All Four Configurations

| Metric | CC Raw (R1) | CC MCP (R2) | Kilo Raw (R5) | Kilo MCP (R9) |
|--------|-------------|-------------|---------------|---------------|
| Score | 164/176 (93.2%) | 158/176 (89.8%) | 145/176 (82.4%) | **166/176 (94.3%)** |
| RC% | **100%** | 98.5% | 89.4% | 98.5% |
| Files% | **100%** | **100%** | 97.7% | **100%** |
| Patch% | 81.8% | 74.2% | 65.2% | **86.4%** |
| Exact (8/8) | **14** | 7 | 5 | **14** |
| Fails | 0 | 0 | 2 | 0 |
| Avg time/task | 310s | **149s** | 477s | 264s |
| Avg cost/task | $0.538 | **$0.300** | $1.025 | $0.849 |
| Eff Input/task | 126K | **55K** | 206K† | 190K† |
| Output/task | 19.7K | **9.1K** | 23.6K | 14.0K |

> **Kilo MCP is the best Claude Sonnet configuration overall (94.3%)**, narrowly beating Claude Code Raw (93.2%). The MCP knowledge graph on Kilo eliminates raw-mode hallucination failures and achieves the highest patch quality of any Sonnet run (86.4%). Claude Code MCP remains the cheapest and fastest option at 55K Eff Input/task — but note: CC runs include 1.25× cache-write cost in this figure, while Kilo/OpenRouter runs do not track CW separately (actual Kilo Eff Input is likely higher than shown). Kilo Raw is the weakest configuration — slower, more expensive, and 10.8 pp below Claude Code Raw.

---

## Cross-Agent Comparison: Claude Code vs Kilo

### Aggregated by Agent Platform

| Agent | # Runs | Avg Score | Best Score | Worst Score | Avg Time/task | Avg Cost/task |
|-------|--------|-----------|------------|-------------|---------------|---------------|
| **Claude Code** | 4 | **161.8/176 (91.9%)** | 164/176 | 158/176 | **240s** | $0.524 |
| **Kilo** | 8 | **143.5/176 (81.5%)** | 166/176 | 118/176 | **386s** | $0.284 |

> Claude Code runs show lower variance (158–164) and higher floor. Kilo runs show higher ceiling (166 with Sonnet Kilo MCP) but also much lower floor (118 with env-fail). Kilo is cheaper on average because GPT-Nano ($0.037/task) and free Qwen ($0) pull the average down.

### Same Model, Different Agent: Claude Sonnet 4.6

Covered in the Raw vs MCP section above — Claude Code outperforms Kilo by 10.8 pp in raw mode.

---

## Persistent Hard Tasks

Tasks where **every single run** scored ≤7/8 (no run achieved a perfect 8/8):

| Task | Issue | Best Score (Run) | Consistent Failure Mode |
|------|-------|-----------------|------------------------|
| `14365` (Task 11) | QDP reader fails on lowercase commands | 8/8 (**Run 9, Sonnet Kilo MCP**) | Most runs miss `v.upper() == "NO"` check in data-line parsing; only `re.IGNORECASE` applied |
| `14598` (Task 15) | FITS CONTINUE cards double un-escaping | 8/8 (**Runs 1, 3, 4, 9**) | Parser-side fix (regex anchor + remove replace) vs writer-side fix; Qwen MCP and Opus runs solve it |

Tasks where **most runs** scored ≤6/8 (difficult across the board):

| Task | Issue | Scores Range | Key Pattern |
|------|-------|-------------|-------------|
| `7606` (Task 19) | `Unit.__eq__` returns `False` vs `NotImplemented` | 0–6/8 | `UnitBase.__eq__` universally missed; `UnrecognizedUnit` focused by issue description |
| `13977` (Task 7) | `Quantity.__array_ufunc__` duck types | 6–8/8 | Only Opus MCP (run 4) and Claude Sonnet Raw (run 1) achieve 8/8 full body wrap |
| `12907` (Task 1) | `separability_matrix` nested CompoundModels | 1–8/8 | Kilo Sonnet Raw adds only test cases without the source fix; most others get it right |
| `14096` (Task 8) | `SkyCoord` misleading AttributeError | 6–8/8 | MRO-walk over-engineering vs GT's 2-line `__getattribute__`; models pick complexity |

### Task-by-Task Scorecard (All 12 Runs)

| Task | Instance | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | R9 | R10 | R11 | R12 |
|------|----------|----|----|----|----|----|----|----|----|----|----|-----|-----|
| 1 | `12907` | 8✅ | 8✅ | 8✅ | 8✅ | 1❌ | 8✅ | 5⚠ | 5⚠ | 8✅ | 8✅ | 7✅ | 0❌ |
| 2 | `13033` | 7✅ | 7✅ | 8✅ | 8✅ | 6⚠ | 7✅ | 7✅ | 7✅ | 7✅ | 8✅ | 7✅ | 7✅ |
| 3 | `13236` | 8✅ | 8✅ | 8✅ | 8✅ | 7✅ | 8✅ | 8✅ | 6⚠ | 8✅ | 8✅ | 8✅ | 0❌ |
| 4 | `13398` | 8✅ | 8✅ | 8✅ | 8✅ | 6⚠ | 8✅ | 4❌ | 2❌ | 7✅ | 7✅ | 2❌ | 1❌ |
| 5 | `13453` | 8✅ | 7✅ | 8✅ | 7✅ | 7✅ | 7✅ | 8✅ | 7✅ | 8✅ | 8✅ | 7✅ | 7✅ |
| 6 | `13579` | 8✅ | 8✅ | 8✅ | 6⚠ | 7✅ | 7✅ | 6⚠ | 7✅ | 8✅ | 6⚠ | 8✅ | 7✅ |
| 7 | `13977` | 8✅ | 6⚠ | 6⚠ | 8✅ | 7✅ | 6⚠ | 7✅ | 6⚠ | 7✅ | 7✅ | 7✅ | 7✅ |
| 8 | `14096` | 6⚠ | 7✅ | 7✅ | 7✅ | 7✅ | 7✅ | 8✅ | 7✅ | 8✅ | 7✅ | 7✅ | 7✅ |
| 9 | `14182` | 8✅ | 8✅ | 8✅ | 8✅ | 5⚠ | 8✅ | 7✅ | 4❌ | 7✅ | 8✅ | 6⚠ | 6⚠ |
| 10 | `14309` | 7✅ | 7✅ | 7✅ | 7✅ | 8✅ | 7✅ | 7✅ | 7✅ | 8✅ | 7✅ | 8✅ | 7✅ |
| 11 | `14365` | 7✅ | 7✅ | 7✅ | 7✅ | 5⚠ | 6⚠ | 7✅ | 6⚠ | **8✅** | 6⚠ | 6⚠ | 6⚠ |
| 12 | `14369` | 8✅ | 7✅ | 8✅ | 8✅ | 7✅ | 3❌ | 7✅ | 5⚠ | 7✅ | 7✅ | 3❌ | 3❌ |
| 13 | `14508` | 6⚠ | 7✅ | 8✅ | 8✅ | 8✅ | 8✅ | 8✅ | 6⚠ | 8✅ | 8✅ | 7✅ | 7✅ |
| 14 | `14539` | 8✅ | 8✅ | 8✅ | 8✅ | 8✅ | 8✅ | 8✅ | 8✅ | 8✅ | 8✅ | 8✅ | 8✅ |
| 15 | `14598` | 8✅ | 7✅ | 8✅ | 5⚠ | 7✅ | 5⚠ | 5⚠ | 4❌ | 5⚠ | 5⚠ | 7✅ | 7✅ |
| 16 | `14995` | 8✅ | 8✅ | 8✅ | 8✅ | 8✅ | 7✅ | 8✅ | 8✅ | 8✅ | 8✅ | 8✅ | 8✅ |
| 17 | `7166` | 7✅ | 7✅ | 8✅ | 8✅ | 7✅ | 8✅ | 8✅ | 7✅ | 8✅ | 8✅ | 7✅ | 0❌ |
| 18 | `7336` | 8✅ | 7✅ | 8✅ | 8✅ | 8✅ | 7✅ | 8✅ | 8✅ | 8✅ | 8✅ | 8✅ | 7✅ |
| 19 | `7606` | 5⚠ | 5⚠ | 3❌ | 6⚠ | 7✅ | 5⚠ | 7✅ | 3❌ | 7✅ | 6⚠ | 3❌ | 2❌ |
| 20 | `7671` | 8✅ | 7✅ | 7✅ | 7✅ | 8✅ | 7✅ | 8✅ | 7✅ | 8✅ | 7✅ | 6⚠ | 6⚠ |
| 21 | `8707` | 7✅ | 7✅ | 6⚠ | 8✅ | 6⚠ | 2❌ | 7✅ | 5⚠ | 7✅ | 8✅ | 7✅ | 7✅ |
| 22 | `8872` | 8✅ | 7✅ | 7✅ | 7✅ | 7✅ | 7✅ | 8✅ | 8✅ | 8✅ | 7✅ | 7✅ | 7✅ |
| | **Total** | **164** | **158** | **162** | **163** | **145** | **146** | **156** | **129** | **166** | **160** | **142** | **118** |

> Runs: R1=Sonnet CC Raw · R2=Sonnet CC MCP · R3=Opus CC Raw · R4=Opus CC MCP · R5=Sonnet Kilo Raw · R6=Qwen Kilo Raw · R7=GPT Mini Kilo Raw · R8=GPT Nano Kilo Raw · R9=Sonnet Kilo MCP · R10=Qwen Kilo MCP · R11=GPT Mini Kilo MCP · R12=GPT Nano Kilo MCP (env-fail)

**Easiest tasks (≥8/8 in 10+ of 12 runs):** 14539 (12/12 perfect), 14995 (11/12), 7336 (11/12)

**Hardest tasks (avg score <7/8):**
- **12907**: avg 6.1/8 — Kilo Sonnet (1/8) and Qwen/Nano MCP failures pull avg down
- **13398**: avg 6.2/8 — ITRS transforms (1–4h task); GPT models struggle; Qwen MCP recovers
- **7606**: avg 5.1/8 — Unit.__eq__ / NotImplemented semantics; universally partial
- **14598**: avg 6.2/8 — FITS CONTINUE cards; parser vs writer fix confusion

---

## Failure Pattern Summary

### By Failure Type

| Failure Mode | Runs Affected | Tasks Affected | Description |
|-------------|---------------|----------------|-------------|
| **Over-engineering** | All Claude/Qwen | 14096, 14508, 13579 (occ.) | Model produces complex, correct-in-spirit but wrong-in-detail fix; GT is a 1–2 line change |
| **Partial scope** | All runs | 7606, 13977 | Fixes one class or one code path; misses the other class/path that GT requires |
| **Missing `v.upper()` in QDP** | 8 of 12 runs | 14365 | Only Sonnet Kilo MCP (run 9) and GPT Mini (raw + MCP) include the `.upper()` fix |
| **Wrong codec (ascii vs latin-1)** | Sonnet runs | 8707 | GT requires latin-1 for FITS bytes; Sonnet uses ascii (works for ASCII-only FITS) |
| **Hallucinated code state** | Qwen/Sonnet Raw Kilo | 8707, 14369 | Model asserts the fix is already in the code; proposes only tests or cache invalidation |
| **No patch proposed** | Opus CC Raw | 7606 | Opus returns only filename, no fix; 3/8 |
| **MCP env failures (apply_patch)** | Kilo MCP nano-dir (run 12) | 12907, 13236, 7166, others | `apply_patch` fails because no local repo exists in MCP mode |
| **MCP env failures** | GPT Mini MCP | 13398, 14369, 7606 | Same apply_patch issue; also commit hash not in MCP index |
| **Timeout exhaustion** | GPT Mini Raw | 3,5,7,8,10,11 | ~1,306s limit hit; answer produced but reasoning truncated |
| **Timeout exhaustion** | GPT Nano Raw | 1,5,6,7,8 | ~2,684s limit; longer context needs more steps |

### By Model Archetype

| Model | Strength | Consistent Weakness |
|-------|----------|---------------------|
| **Claude Sonnet 4.6 (CC)** | 100% RC; high exact count; no failures | Over-engineers 14096/14508; misses `v.upper()` |
| **Claude Opus 4.6 (CC)** | High exact count; MCP fully resolves weaknesses | Raw: task 7606 produces no patch at all |
| **GPT-5.4 Mini (Kilo)** | Excellent cost/accuracy ratio; consistent | Fails ITRS transform (13398) and CDS grammar (14369 MCP) |
| **GPT-5.4 Nano (Kilo)** | Very cheap; fast on simple tasks | Patch quality 47%; many partial timeouts; wrong return types |
| **Qwen 3.6 Plus (Kilo)** | Best free-tier score (90.9% MCP); $0 cost | Raw hallucinations on 8707/14369; verbose reasoning = 1.3M tokens/task raw |

---

## Appendix: Run Index

| Run # | Source Report | Run Directory | Date |
|-------|--------------|---------------|------|
| 1 | `raw/claude_sonnet4.6_raw_on_claude_code.md` | `auto_run_on_claude_sonnet_4_6_raw/` | 2026-04-02 |
| 2 | `mcp/claude_sonnet4.6_WITH_MCP_on_claude_code.md` | `auto_run_on_claude_sonnet_4_6_mcp/` | 2026-04-02 |
| 3 | `raw/claude_opus_4.6_run_raw_on_claude_code.md` | `claude-opus-4.6-v3-raw/` | 2026-03-31 |
| 4 | `mcp/claude_opus_4.6_mcp_on_claude_code.md` | `claude_opus_4.6_mcp_v2/` | 2026-04-01 |
| 5 | `raw/claude_sonnet4.6_raw_on_kilo.md` | `auto_run_on_raw_kilo_anthropic_claude-sonnet-4.6/` | 2026-04-05 |
| 6 | `raw/qwen_3.6_preview_free_raw.md` | `auto_run_on_raw_kilo_qwen_qwen3.6-plus:free/` | 2026-04-03 |
| 7 | `raw/gpt5.4-mini_raw_on_kilo.md` | `auto_run_on_raw_kilo_openai_gpt-5.4-mini/` | 2026-04-03 |
| 8 | `raw/gpt5.4-nano_raw_on_kilo.md` | `auto_run_on_raw_kilo_openai_gpt-5.4-nano/` | 2026-04-03 |
| 9 | `mcp/claude_sonnet4.6_mcp_on_kilo.md` | `auto_run_on_mcp_kilo_anthropic_claude-sonnet-4.6/` | 2026-04-06 |
| 10 | `mcp/qwen_3.6_preview_free_mcp.md` | `auto_run_on_mcp_kilo_qwen_qwen3.6-plus:free/` | 2026-04-03 |
| 11 | `mcp/gpt5.4-mini_mcp_on_kilo.md` | `auto_run_on_mcp_kilo_openai_gpt-5.4-mini/` | 2026-04-05 |
| 12 | `mcp/gpt5.4-nano_mcp_on_kilo.md` | `auto_run_on_mcp_kilo_openai_gpt-5.4-nano/` | 2026-04-03 |
