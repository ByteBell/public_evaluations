# Qwen 3.6 Plus Preview — Raw vs MCP Debiased Comparison

**Companion to:** `qwen_3.6_preview_comparison.md`
**Date:** 2026-04-02

The full comparison averages are meaningfully skewed by one runaway task in each run:

| Outlier | Run | Cost | Time | Requests | Score | Why it skews |
|---------|-----|------|------|----------|-------|--------------|
| `14598` | Raw | **$15.84** | 4,781 s | 65 | 7/8 | 4.0× raw avg cost; alone represents 25% of total raw spend |
| `13977` | MCP | **$10.84** | 1,164 s | 49 | 6/8 | 2.9× MCP avg cost; most expensive MCP task despite a tie result |

Removing one outlier from each run gives a cleaner picture of typical behaviour.

---

## Debiased Top-Line Summary

| Metric | Raw (15 tasks, −14598) | MCP (13 tasks, −13977) | Delta |
|--------|------------------------|------------------------|-------|
| Overall score | 108/120 | 91/104 | — |
| Overall % | **90.0%** | **87.5%** | Raw +2.5 pp |
| Avg score / task | 7.2/8 | 7.0/8 | Raw +0.2 |
| Patch quality % | **73.3%** | **66.7%** | Raw +6.6 pp |
| Exact (8/8) | 7 | 5 | Raw +2 |
| Near-perfect (7/8) | 4 | 4 | Tie |
| Partial (6/8) | 4 | 3 | — |
| Partial (5/8) | 0 | 1 | MCP worse |
| Fail (≤4/8) | 0 | 0 | Tie |
| Exact + Near-perfect | **11/15 (73.3%)** | **9/13 (69.2%)** | Raw +4.1 pp |
| Total time | 8,580 s | 10,359 s | — |
| **Avg time / task** | **572 s** | **797 s** | **Raw −28%** |
| Total cost | $47.28 | $41.36 | — |
| **Avg cost / task** | **$3.15** | **$3.18** | **Essentially equal** |

---

## What Changes After Debiasing

### Cost: the gap closes to zero

| | Full avg | Debiased avg | Change |
|---|----------|--------------|--------|
| Raw | $3.95 | **$3.15** | −20% |
| MCP | $3.73 | **$3.18** | −15% |
| Delta | Raw +$0.22 | **Raw −$0.03** | Flip |

The raw run's apparent cost advantage in the full comparison disappears entirely. Both modes cost the same per task once you strip the one runaway job (`14598` for raw). The MCP overhead is not a consistent savings — it is noise around the same underlying cost floor.

### Time: Raw gets dramatically faster, MCP barely changes

| | Full avg | Debiased avg | Change |
|---|----------|--------------|--------|
| Raw | 835 s | **572 s** | −31% |
| MCP | 823 s | **797 s** | −3% |
| Delta | ~Tie | **Raw −28%** | Raw now clearly faster |

`14598` alone accounts for 36% of raw's total wall-clock time. With it gone, raw is substantially faster. MCP's time distribution is more spread across multiple slow tasks (`14369`: 3,603s, `13579`: 1,986s, `14365`: 1,280s), so removing just one outlier barely moves its average.

### Quality: Raw still leads, but the margin shrinks

| Metric | Full comparison | Debiased |
|--------|----------------|---------|
| Overall % delta | Raw +3.2 pp | Raw +2.5 pp |
| Patch % delta | Raw +8.6 pp | Raw +6.6 pp |
| Exact+Near-perfect delta | Raw +10.7 pp | Raw +4.1 pp |

The quality gap narrows but does not close. Raw still wins on every quality dimension. The direction is unchanged; the magnitude is more modest.

---

## Debiased Cost Distribution

### Raw (15 tasks, outlier removed)

| Bucket | Tasks | % |
|--------|-------|---|
| < $2.00 | 7 | 47% |
| $2.00–$4.00 | 4 | 27% |
| $4.00–$7.00 | 3 | 20% |
| $7.00–$10.00 | 1 | 7% |
| > $10.00 | 0 | 0% |

Median: ~$1.99 · Mean: $3.15

### MCP (13 tasks, outlier removed)

| Bucket | Tasks | % |
|--------|-------|---|
| < $2.00 | 4 | 31% |
| $2.00–$4.00 | 6 | 46% |
| $4.00–$7.00 | 3 | 23% |
| $7.00–$10.00 | 0 | 0% |
| > $10.00 | 0 | 0% |

Median: ~$3.25 · Mean: $3.18

MCP has a tighter, more consistent cost distribution (nearly all tasks fall in $1–$7). Raw has a longer tail even after removing `14598` — three tasks still cost $4–$8. MCP's $0.895 minimum (`14508`) is also the cheapest single task across both runs.

---

## Debiased Time Distribution

### Raw (15 tasks, outlier removed)

| Bucket | Tasks | % |
|--------|-------|---|
| < 300 s | 4 | 27% |
| 300–600 s | 6 | 40% |
| 600–900 s | 3 | 20% |
| 900–2000 s | 2 | 13% |
| > 2000 s | 0 | 0% |

Median: ~537 s · Mean: 572 s

### MCP (13 tasks, outlier removed)

| Bucket | Tasks | % |
|--------|-------|---|
| < 300 s | 4 | 31% |
| 300–600 s | 5 | 38% |
| 600–1000 s | 1 | 8% |
| 1000–2000 s | 2 | 15% |
| > 2000 s | 1 (`13579`: 1,986s) | 8% |

Median: ~340 s · Mean: 797 s

MCP's median (340s) is actually *lower* than raw's (537s) — half the MCP tasks complete quickly (< 300s). But the long tail from three slow tasks (13579, 14365, 14369) drags the mean up to 797s. Raw's distribution is tighter around the middle.

---

## Debiased Shared-Task Head-to-Head (10 tasks, −13977)

Removing `13977` (a tie at 6/8 for both runs) from the shared set:

| Metric | Raw (10 shared) | MCP (10 shared) | Delta |
|--------|----------------|-----------------|-------|
| Total score | 75/80 | 68/80 | — |
| Score % | **93.8%** | **85.0%** | Raw +8.8 pp |
| Raw wins | 5 | — | |
| MCP wins | 0 | — | |
| Ties | 5 | — | |

The head-to-head story is unchanged: Raw wins 5–0 on shared tasks with or without the outlier. The delta grows very slightly (from +7.9 pp to +8.8 pp) since the removed task was a tie that mildly reduced the gap.

---

## Summary: What the Debiased View Reveals

| Claim from full comparison | Holds after debiasing? |
|---------------------------|----------------------|
| Raw scores higher on quality | ✅ Yes — gap narrows but direction unchanged |
| Raw has better patch quality | ✅ Yes — 73.3% vs 66.7% |
| MCP is cheaper per task | ❌ No — cost is essentially equal ($3.15 vs $3.18) |
| Speed is roughly equal | ❌ No — Raw is 28% faster (572s vs 797s) |
| Raw wins all head-to-head shared tasks | ✅ Yes — still 5–0 |
| MCP adds unique task coverage | ✅ Yes — unaffected by outlier removal |

**The takeaway:** the full comparison overstates MCP's cost advantage (it was driven by Raw's one runaway task). The debiased picture is: **same cost, Raw 28% faster, Raw measurably better quality**. The only genuine MCP advantage — unlocking hard tasks that Raw didn't attempt — remains valid and unaffected by the outliers.
