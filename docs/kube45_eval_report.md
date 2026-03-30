# KubeCluster45 Evaluation Report

**Model:** Claude Opus 4.6  
**Pricing:** $5.00 / M input · $25.00 / M output tokens  
**Dataset:** 45 questions — 11 MIXED · 34 OBS  
**Conditions:** MCP-assisted (knowledge graph tools) vs Unaided (no MCP, no web search)

---

## 1. Files Reported vs Files Correct

*"Reported"* = number of files the model identified as impacted.  
*"True"* = of those reported, how many were actually in the ground truth.  
*"Hit rate"* = True / Reported (precision on reported files).

| | MCP | No-MCP |
|--|-----|--------|
| **Total files reported** | 573 | 781 |
| **True (in GT)** | 116 | 257 |
| **Hit rate (reported → true)** | 20.2% | 32.9% |
| GT total files across all questions | 544 | 544 |
| Avg reported per question | 12.7 | 17.4 |
| Avg true per question | 2.6 | 5.7 |

## 2. Cost & Time — No-MCP Run

> Data from **30/45** questions (cost) · **38/45** (tools) · **35/45** (time)

| Metric | Total | Avg / question |
|--------|-------|----------------|
| Input tokens  | 1,036,556  | 32,392 |
| Output tokens | 162,100 | 4,631 |
| **Cost (USD)** | **$8.6568** | **$0.2886** |
| Tool calls | 767 | 20.2 |
| Time (s)   | 5493 | 156.9 |
| Time (min) | 91.5 | 2.6 |

**Cost split:** input = $5.1828 (56%) · output = $4.0525 (44%)

## 3. MCP Tool Calls

> Token/cost data not recorded in MCP answer files. Tool call data from **11/45** questions.

| Metric | Total | Avg / question |
|--------|-------|----------------|
| MCP tool calls | 192 | 17.5 |

## 4. By Category

| Category | Questions | MCP Reported | MCP True | MCP Hit% | NoMCP Reported | NoMCP True | NoMCP Hit% | NoMCP Cost | NoMCP Avg Time(s) |
|----------|-----------|-------------|---------|---------|---------------|-----------|-----------|-----------|-----------------|
| MIXED | 11 | 240 | 67 | 27.9% | 225 | 115 | 51.1% | $3.0259 | 52.0 |
| OBS | 34 | 333 | 49 | 14.7% | 556 | 142 | 25.5% | $5.6309 | 188.0 |

## 5. Per-Question Detail

| # | Question | GT | MCP Rep | MCP True | MCP Hit% | MCP Tools | NoMCP Rep | NoMCP True | NoMCP Hit% | NoMCP Tools | NoMCP Time(s) | NoMCP Cost |
|---|----------|----|---------|---------|---------|----------|----------|-----------|-----------|------------|--------------|-----------|
| 1 | MIXED_TC001 | 0 | 18 | 0 | 0% | 6 | 37 | 0 | 0% | 141 | 97 | $1.5669 |
| 2 | MIXED_TC002 | 11 | 3 | 2 | 67% | N/A | 14 | 11 | 79% | 18 | 45 | $0.1708 |
| 3 | MIXED_TC003 | 30 | 8 | 8 | 100% | 16 | 29 | 28 | 97% | 8 | 15 | $0.2200 |
| 4 | MIXED_TC004 | 30 | 8 | 7 | 88% | 22 | 19 | 19 | 100% | 16 | 35 | $0.1375 |
| 5 | MIXED_TC005 | 10 | 6 | 5 | 83% | 10 | 6 | 5 | 83% | 16 | 30 | $0.1160 |
| 6 | MIXED_TC006 | 25 | 12 | 2 | 17% | 24 | 14 | 8 | 57% | 14 | 35 | $0.2625 |
| 7 | MIXED_TC007 | 16 | 44 | 2 | 5% | 18 | 0 | 0 | — | N/A | N/A | $0.1625 |
| 8 | MIXED_TC008 | 8 | 32 | 3 | 9% | N/A | 60 | 4 | 7% | 28 | N/A | N/A |
| 9 | MIXED_TC009 | 40 | 38 | 33 | 87% | 10 | 46 | 40 | 87% | 15 | 103 | $0.1904 |
| 10 | MIXED_TC010 | 0 | 46 | 0 | 0% | N/A | 0 | 0 | — | 22 | N/A | N/A |
| 11 | MIXED_TC011 | 14 | 25 | 5 | 20% | 12 | 0 | 0 | — | 20 | 56 | $0.1994 |
| 12 | OBS_TC001 | 25 | 14 | 4 | 29% | 18 | 36 | 18 | 50% | 13 | 127 | $0.2200 |
| 13 | OBS_TC002 | 0 | 125 | 0 | 0% | N/A | 56 | 0 | 0% | 22 | 147 | $1.0950 |
| 14 | OBS_TC003 | 3 | 44 | 2 | 5% | 28 | 74 | 2 | 3% | 24 | 124 | $0.2375 |
| 15 | OBS_TC004 | 15 | 10 | 0 | 0% | N/A | 56 | 8 | 14% | 16 | 133 | $0.3875 |
| 16 | OBS_TC005 | 7 | 8 | 5 | 62% | N/A | 9 | 2 | 22% | 20 | 115 | $0.1243 |
| 17 | OBS_TC006 | 9 | 12 | 7 | 58% | N/A | 32 | 9 | 28% | N/A | N/A | N/A |
| 18 | OBS_TC007 | 1 | 11 | 0 | 0% | N/A | 34 | 1 | 3% | 10 | 96 | $0.2650 |
| 19 | OBS_TC008 | 25 | 30 | 8 | 27% | N/A | 29 | 15 | 52% | 18 | 806 | $0.2550 |
| 20 | OBS_TC009 | 16 | 16 | 14 | 88% | 28 | 1 | 1 | 100% | N/A | 508 | N/A |
| 21 | OBS_TC010 | 3 | 3 | 0 | 0% | N/A | 0 | 0 | — | 16 | 104 | $0.1237 |
| 22 | OBS_TC011 | 9 | 9 | 0 | 0% | N/A | 22 | 1 | 5% | 15 | 381 | $0.2540 |
| 23 | OBS_TC012 | 16 | 2 | 1 | 50% | N/A | 20 | 7 | 35% | 18 | 163 | $0.2550 |
| 24 | OBS_TC013 | 9 | 4 | 0 | 0% | N/A | 21 | 9 | 43% | 14 | 200 | $0.2650 |
| 25 | OBS_TC014 | 35 | 0 | 0 | — | N/A | 38 | 26 | 68% | 18 | 152 | $0.2750 |
| 26 | OBS_TC015 | 22 | 0 | 0 | — | N/A | 0 | 0 | — | 16 | 175 | N/A |
| 27 | OBS_TC016 | 2 | 0 | 0 | — | N/A | 31 | 2 | 6% | 18 | 142 | $0.2950 |
| 28 | OBS_TC017 | 17 | 0 | 0 | — | N/A | 0 | 0 | — | N/A | N/A | N/A |
| 29 | OBS_TC018 | 12 | 0 | 0 | — | N/A | 17 | 5 | 29% | 18 | 157 | $0.2650 |
| 30 | OBS_TC019 | 12 | 0 | 0 | — | N/A | 10 | 10 | 100% | 14 | 238 | $0.1960 |
| 31 | OBS_TC020 | 12 | 1 | 0 | 0% | N/A | 0 | 0 | — | 22 | 69 | N/A |
| 32 | OBS_TC021 | 0 | 0 | 0 | — | N/A | 0 | 0 | — | 16 | N/A | N/A |
| 33 | OBS_TC022 | 4 | 0 | 0 | — | N/A | 9 | 3 | 33% | 15 | 185 | $0.1910 |
| 34 | OBS_TC023 | 9 | 0 | 0 | — | N/A | 0 | 0 | — | 25 | N/A | $0.2218 |
| 35 | OBS_TC024 | 8 | 0 | 0 | — | N/A | 0 | 0 | — | 14 | 97 | N/A |
| 36 | OBS_TC025 | 3 | 1 | 0 | 0% | N/A | 0 | 0 | — | 18 | 85 | N/A |
| 37 | OBS_TC026 | 8 | 1 | 0 | 0% | N/A | 10 | 8 | 80% | 14 | 135 | $0.2160 |
| 38 | OBS_TC027 | 6 | 0 | 0 | — | N/A | 12 | 6 | 50% | 20 | 224 | $0.2490 |
| 39 | OBS_TC028 | 1 | 6 | 1 | 17% | N/A | 0 | 0 | — | 18 | 135 | $0.1077 |
| 40 | OBS_TC029 | 5 | 0 | 0 | — | N/A | 7 | 5 | 71% | N/A | 112 | N/A |
| 41 | OBS_TC030 | 5 | 8 | 3 | 38% | N/A | 2 | 0 | 0% | N/A | N/A | $0.1325 |
| 42 | OBS_TC031 | 5 | 28 | 4 | 14% | N/A | 30 | 4 | 13% | 18 | N/A | N/A |
| 43 | OBS_TC032 | 26 | 0 | 0 | — | N/A | 0 | 0 | — | N/A | 212 | N/A |
| 44 | OBS_TC033 | 9 | 0 | 0 | — | N/A | 0 | 0 | — | 8 | N/A | N/A |
| 45 | OBS_TC034 | 21 | 0 | 0 | — | N/A | 0 | 0 | — | 11 | 55 | N/A |

## 6. Most Expensive Questions (No-MCP, top 10)

| Question | Cost | Input Tok | Output Tok | Time(s) | Tools | GT Files | Reported | True |
|----------|------|-----------|-----------|---------|-------|----------|---------|------|
| MIXED_TC001 | $1.5669 | 292,386 | 4,200 | 97 | 141 | 0 | 37 | 0 |
| OBS_TC002 | $1.0950 | 185,000 | 6,800 | 147 | 22 | 0 | 56 | 0 |
| OBS_TC004 | $0.3875 | 48,500 | 5,800 | 133 | 16 | 15 | 56 | 8 |
| OBS_TC016 | $0.2950 | 28,000 | 6,200 | 142 | 18 | 2 | 31 | 2 |
| OBS_TC014 | $0.2750 | 24,000 | 6,200 | 152 | 18 | 35 | 38 | 26 |
| OBS_TC007 | $0.2650 | 22,000 | 6,200 | 96 | 10 | 1 | 34 | 1 |
| OBS_TC013 | $0.2650 | 22,000 | 6,200 | 200 | 14 | 9 | 21 | 9 |
| OBS_TC018 | $0.2650 | 22,000 | 6,200 | 157 | 18 | 12 | 17 | 5 |
| MIXED_TC006 | $0.2625 | 18,500 | 6,800 | 35 | 14 | 25 | 14 | 8 |
| OBS_TC008 | $0.2550 | 22,000 | 5,800 | 806 | 18 | 25 | 29 | 15 |

---
*Prices: Claude Opus 4.6 — $5.00/M input · $25.00/M output (Anthropic, Feb 2026)*  
*Ground truth: `results/KubeCluster45/question_*/ground_truth_enhanced.json`*  
*Answers: `New_eval_kube45/Answers_with_mcp/` and `New_eval_kube45/Answers_without_mcp/`*