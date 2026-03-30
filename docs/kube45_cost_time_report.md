# KubeCluster45 — Cost & Time Analysis

**Model:** Claude Opus 4.6  
**Pricing:** $5.00 / M input tokens · $25.00 / M output tokens  
**Dataset:** 45 questions — 11 MIXED · 34 OBS  
**Conditions:** MCP-assisted vs Unaided (no MCP, no web search)

---

## 1. No-MCP Run — Overall Summary

> Data available for **30/45** questions (cost) · **38/45** (tool calls) · **35/45** (time)

| Metric | Total | Avg / question |
|--------|-------|----------------|
| Input tokens  | 1,036,556  | 32,392 |
| Output tokens | 162,100 | 4,631 |
| **Cost (USD)** | **$8.6568** | **$0.2886** |
| Tool calls    | 767 | 20.2 |
| Time (seconds) | 5493 | 156.9 |
| Time (minutes) | 91.5 | 2.6 |

## 2. MCP Run — Tool Calls

> Token/cost data not consistently recorded in MCP answer files. Tool call data available for **11/45** questions.

| Metric | Total | Avg / question |
|--------|-------|----------------|
| MCP tool calls | 192 | 17.5 |

## 3. No-MCP — By Question Category

### MIXED (11 questions)

| Metric | Total | Avg / question |
|--------|-------|----------------|
| Cost (USD) | $3.0259 | $0.3362 |
| Time (s)   | 416 | 52.0 |
| Tool calls | 298 | 29.8 |

### OBS (34 questions)

| Metric | Total | Avg / question |
|--------|-------|----------------|
| Cost (USD) | $5.6309 | $0.2681 |
| Time (s)   | 5077 | 188.0 |
| Tool calls | 469 | 16.8 |

## 4. Per-Question Detail

| # | Question | Cat | NoMCP In-Tok | NoMCP Out-Tok | NoMCP Cost | NoMCP Tools | NoMCP Time(s) | MCP Tools |
|---|----------|-----|-------------|--------------|-----------|------------|--------------|-----------|
| 1 | MIXED_TC001 | MIXED | 292,386 | 4,200 | $1.5669 | 141 | 97 | 6 |
| 2 | MIXED_TC002 | MIXED | 15,150 | 3,800 | $0.1708 | 18 | 45 | N/A |
| 3 | MIXED_TC003 | MIXED | 18,500 | 5,100 | $0.2200 | 8 | 15 | 16 |
| 4 | MIXED_TC004 | MIXED | 8,500 | 3,800 | $0.1375 | 16 | 35 | 22 |
| 5 | MIXED_TC005 | MIXED | 7,200 | 3,200 | $0.1160 | 16 | 30 | 10 |
| 6 | MIXED_TC006 | MIXED | 18,500 | 6,800 | $0.2625 | 14 | 35 | 24 |
| 7 | MIXED_TC007 | MIXED | 18,500 | 2,800 | $0.1625 | N/A | N/A | 18 |
| 8 | MIXED_TC008 | MIXED | N/A | N/A | N/A | 28 | N/A | N/A |
| 9 | MIXED_TC009 | MIXED | 14,070 | 4,800 | $0.1904 | 15 | 103 | 10 |
| 10 | MIXED_TC010 | MIXED | 17,350 | N/A | N/A | 22 | N/A | N/A |
| 11 | MIXED_TC011 | MIXED | 17,370 | 4,500 | $0.1994 | 20 | 56 | 12 |
| 12 | OBS_TC001 | OBS | 18,500 | 5,100 | $0.2200 | 13 | 127 | 18 |
| 13 | OBS_TC002 | OBS | 185,000 | 6,800 | $1.0950 | 22 | 147 | N/A |
| 14 | OBS_TC003 | OBS | 18,500 | 5,800 | $0.2375 | 24 | 124 | 28 |
| 15 | OBS_TC004 | OBS | 48,500 | 5,800 | $0.3875 | 16 | 133 | N/A |
| 16 | OBS_TC005 | OBS | 10,850 | 2,800 | $0.1243 | 20 | 115 | N/A |
| 17 | OBS_TC006 | OBS | N/A | N/A | N/A | N/A | N/A | N/A |
| 18 | OBS_TC007 | OBS | 22,000 | 6,200 | $0.2650 | 10 | 96 | N/A |
| 19 | OBS_TC008 | OBS | 22,000 | 5,800 | $0.2550 | 18 | 806 | N/A |
| 20 | OBS_TC009 | OBS | N/A | 3,500 | N/A | N/A | 508 | 28 |
| 21 | OBS_TC010 | OBS | 10,730 | 2,800 | $0.1237 | 16 | 104 | N/A |
| 22 | OBS_TC011 | OBS | 22,800 | 5,600 | $0.2540 | 15 | 381 | N/A |
| 23 | OBS_TC012 | OBS | 22,000 | 5,800 | $0.2550 | 18 | 163 | N/A |
| 24 | OBS_TC013 | OBS | 22,000 | 6,200 | $0.2650 | 14 | 200 | N/A |
| 25 | OBS_TC014 | OBS | 24,000 | 6,200 | $0.2750 | 18 | 152 | N/A |
| 26 | OBS_TC015 | OBS | N/A | N/A | N/A | 16 | 175 | N/A |
| 27 | OBS_TC016 | OBS | 28,000 | 6,200 | $0.2950 | 18 | 142 | N/A |
| 28 | OBS_TC017 | OBS | N/A | N/A | N/A | N/A | N/A | N/A |
| 29 | OBS_TC018 | OBS | 22,000 | 6,200 | $0.2650 | 18 | 157 | N/A |
| 30 | OBS_TC019 | OBS | 15,200 | 4,800 | $0.1960 | 14 | 238 | N/A |
| 31 | OBS_TC020 | OBS | N/A | N/A | N/A | 22 | 69 | N/A |
| 32 | OBS_TC021 | OBS | N/A | 2,200 | N/A | 16 | N/A | N/A |
| 33 | OBS_TC022 | OBS | 14,200 | 4,800 | $0.1910 | 15 | 185 | N/A |
| 34 | OBS_TC023 | OBS | 26,870 | 3,500 | $0.2218 | 25 | N/A | N/A |
| 35 | OBS_TC024 | OBS | N/A | 2,200 | N/A | 14 | 97 | N/A |
| 36 | OBS_TC025 | OBS | N/A | N/A | N/A | 18 | 85 | N/A |
| 37 | OBS_TC026 | OBS | 14,200 | 5,800 | $0.2160 | 14 | 135 | N/A |
| 38 | OBS_TC027 | OBS | 22,800 | 5,400 | $0.2490 | 20 | 224 | N/A |
| 39 | OBS_TC028 | OBS | 7,530 | 2,800 | $0.1077 | 18 | 135 | N/A |
| 40 | OBS_TC029 | OBS | N/A | N/A | N/A | N/A | 112 | N/A |
| 41 | OBS_TC030 | OBS | 12,500 | 2,800 | $0.1325 | N/A | N/A | N/A |
| 42 | OBS_TC031 | OBS | 18,850 | N/A | N/A | 18 | N/A | N/A |
| 43 | OBS_TC032 | OBS | N/A | 4,500 | N/A | N/A | 212 | N/A |
| 44 | OBS_TC033 | OBS | N/A | 3,500 | N/A | 8 | N/A | N/A |
| 45 | OBS_TC034 | OBS | N/A | N/A | N/A | 11 | 55 | N/A |

## 5. Cost Breakdown

| Component | Tokens | Cost | % of total |
|-----------|--------|------|-----------|
| Input  | 1,036,556  | $5.1828  | 59.9% |
| Output | 162,100 | $4.0525 | 46.8% |
| **Total** | — | **$8.6568** | 100% |

## 6. Most Expensive Questions (No-MCP)

| Question | Cost | Input Tok | Output Tok | Time(s) | Tools |
|----------|------|-----------|-----------|---------|-------|
| MIXED_TC001 | $1.5669 | 292,386 | 4,200 | 97 | 141 |
| OBS_TC002 | $1.0950 | 185,000 | 6,800 | 147 | 22 |
| OBS_TC004 | $0.3875 | 48,500 | 5,800 | 133 | 16 |
| OBS_TC016 | $0.2950 | 28,000 | 6,200 | 142 | 18 |
| OBS_TC014 | $0.2750 | 24,000 | 6,200 | 152 | 18 |
| OBS_TC007 | $0.2650 | 22,000 | 6,200 | 96 | 10 |
| OBS_TC013 | $0.2650 | 22,000 | 6,200 | 200 | 14 |
| OBS_TC018 | $0.2650 | 22,000 | 6,200 | 157 | 18 |
| MIXED_TC006 | $0.2625 | 18,500 | 6,800 | 35 | 14 |
| OBS_TC008 | $0.2550 | 22,000 | 5,800 | 806 | 18 |

## 7. Key Numbers

- **Total no-MCP cost across 45 questions:** $8.6568 *(from 30 questions with cost data)*
- **Average cost per question (no-MCP):** $0.2886
- **Average time per question (no-MCP):** 156.9 seconds
- **Average tool calls per question (no-MCP):** 20.2
- **Average tool calls per question (MCP):** 17.5 *(from 11 questions with data)*
- **Total wall-clock time (no-MCP, all 45q):** ~91.5 minutes *(from 35 questions)*

---
*Prices: Claude Opus 4.6 — $5.00/M input tokens · $25.00/M output tokens (Anthropic, Feb 2026)*