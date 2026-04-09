# MCP Tool Usage Exploration Report: Astropy SWE-bench Tasks

**Date**: 2026-04-08
**Dataset**: 22 astropy tasks from `princeton-nlp/SWE-bench_Verified`
**Runs analyzed**: 6 MCP-enabled runs across 4 LLM providers and 2 harnesses

---

## 1. Runs Overview

| Run Label | Model | Harness | Total Cost | Total MCP Calls | Total Non-MCP | Avg Time/Task | MCP Failures |
|-----------|-------|---------|------------|-----------------|---------------|---------------|--------------|
| sonnet_cc | Claude Sonnet 4.6 | Claude Code | $6.96 | 184 | 37 | 151s | 7 |
| opus_cc | Claude Opus 4.6 | Claude Code | $11.53 | 227 | 66 | 249s | 29 |
| sonnet_kilo | Claude Sonnet 4.6 | Kilo | $18.68 | 395 | 48 | 264s | 0 |
| gpt54mini_kilo | GPT-5.4-mini | Kilo | $1.23 | 279 | 74 | 37s | 0 |
| gpt54nano_kilo | GPT-5.4-nano | Kilo | $0.91 | 439 | 94 | 81s | 0 |
| qwen_kilo | Qwen 3.6-plus | Kilo | $0.00 | 296 | 86 | 269s | 0 |

**Key takeaway**: Kilo+Sonnet is the most expensive run ($18.68) with the most MCP calls (395). Opus Claude Code has 29 MCP failures - the most of any run. GPT-5.4-mini achieves lowest average time (37s) with moderate MCP usage.

---

## 2. MCP Tool Usage Breakdown

### 2.1 Tool Distribution by Run

| Tool | sonnet_cc | opus_cc | sonnet_kilo | gpt54mini | gpt54nano | qwen |
|------|-----------|---------|-------------|-----------|-----------|------|
| retrieve_file | 137 (74%) | 119 (52%) | 305 (77%) | 147 (53%) | 282 (64%) | 192 (65%) |
| smart_search | 32 (17%) | 80 (35%) | 29 (7%) | 7 (3%) | 37 (8%) | 27 (9%) |
| keyword_lookup | 11 (6%) | 10 (4%) | 1 (<1%) | 28 (10%) | 38 (9%) | 2 (1%) |
| list_knowledge | 4 (2%) | 18 (8%) | 22 (6%) | 19 (7%) | 11 (3%) | 18 (6%) |
| graph_search | 0 | 0 | 15 (4%) | 49 (18%) | 9 (2%) | 46 (16%) |
| cypher | 0 | 0 | 21 (5%) | 2 (1%) | 21 (5%) | 9 (3%) |
| graph_traverse | 0 | 0 | 1 (<1%) | 6 (2%) | 9 (2%) | 0 |
| get_repo_hubs | 0 | 0 | 0 | 16 (6%) | 0 | 0 |
| save_conversation | 0 | 0 | 0 | 2 (1%) | 19 (4%) | 0 |
| submit_feedback | 0 | 0 | 0 | 0 | 12 (3%) | 0 |

### 2.2 retrieve_file Operation Breakdown

| Run | content | metadata | other |
|-----|---------|----------|-------|
| sonnet_cc | 129 (94%) | 8 (6%) | 0 |
| opus_cc | 114 (96%) | 4 (3%) | 1 |
| sonnet_kilo | 291 (95%) | 14 (5%) | 0 |
| gpt54mini | 18 (78%) | 5 (22%) | 0* |
| gpt54nano | 56 (84%) | 8 (12%) | 2 |
| qwen | 146 (76%) | 27 (14%) | 19 |

*GPT-5.4-mini had 124 retrieve_file calls where input couldn't be parsed - suggests malformed inputs.

---

## 3. Critical Bottlenecks & Failure Patterns

### 3.1 BOTTLENECK: retrieve_file Looping (All Runs)

**The dominant anti-pattern across ALL runs is consecutive retrieve_file calls.**

Top sequence patterns (2-grams):
- `retrieve_file -> retrieve_file`: 108x (sonnet_cc), 92x (opus_cc), **263x** (sonnet_kilo), 115x (gpt54mini), **220x** (gpt54nano), 144x (qwen)
- `retrieve_file -> retrieve_file -> retrieve_file` (3-gram): 86x (sonnet_cc), 69x (opus_cc), **229x** (sonnet_kilo), 88x (gpt54mini), **174x** (gpt54nano), 104x (qwen)

**Root cause**: Models are reading files one-by-one, often re-reading the same file with different `fromLine`/`toLine` ranges or `search` terms, instead of:
1. Using `metadata` operation first to get the file's `section_map`, then doing targeted `content` reads
2. Using `graph_search` or `keyword_lookup` to find the right file/section before retrieving

**Worst case**: `sonnet_kilo` on `astropy__astropy-13398` made **54 consecutive retrieve_file calls** ($3.01, 875s) - reading through transformation code file by file without a strategic search plan.

**Skill pointer**: A `bytebell-code-search` skill should enforce the 3-step pattern:
```
1. smart_search or keyword_lookup to FIND the right files
2. retrieve_file(metadata) to get section_map and structure
3. retrieve_file(content, fromLine, toLine) for targeted reads
```
This would prevent the "wander through the codebase" anti-pattern.

---

### 3.2 BOTTLENECK: Wrong knowledgeId (Opus Claude Code - 29 failures)

**Opus CC used wrong knowledgeId values in 19 of 22 tasks.** Instead of the actual UUID (`eb768039-0fd9-4051-bf82-44ce31015d78`), it guessed:
- `"astropy"` (15 tasks) - the repo name, not the ID
- `"astropy__astropy"` (1 task) - the task prefix
- `"astropy__astropy-14096"` (1 task) - the full task ID
- `"cm91z37yz000gomhtuhkfr1f7"` (1 task) - a random-looking string
- `"9c0b78ab-fa50-4d57-89f1-8d990d722dd4"` (1 task) - a wrong UUID

These calls with wrong knowledgeId resulted in failures, wasting tokens and time. The model then had to call `list_knowledge` to discover the correct UUID, and re-attempt.

**Skill pointer**: The `bytebell-code-search` skill must hammer home:
```
ALWAYS call list_knowledge FIRST to get the knowledgeId.
NEVER guess the knowledgeId from repo name, task ID, or any other source.
The knowledgeId is a UUID like "eb768039-0fd9-4051-bf82-44ce31015d78".
```

**Why this matters for minimal prompt**: In the current 960-line system prompt, the `list_knowledge` instruction is likely buried. A skill that fires at search time would put this front and center.

---

### 3.3 BOTTLENECK: commitHash Usage Inconsistency

| Run | With commitHash | Without commitHash |
|-----|----------------|-------------------|
| sonnet_cc | 84% | 16% |
| opus_cc | **12%** | **88%** |
| sonnet_kilo | 15% | 85% |
| gpt54mini | 36% | 64% |
| gpt54nano | 32% | 68% |
| qwen | 16% | 84% |

Each task specifies a `base_commit` that the question refers to. The MCP supports `commitHash` to retrieve code at a specific version. Yet **most runs omit it in 65-88% of calls**.

**Impact**: Without commitHash, models get the latest indexed version which may differ from the bug commit. This could lead to:
- Finding code that's already been fixed (false positive)
- Missing code that existed at the bug version but was later removed
- Incorrect line numbers in the diff

**Sonnet CC is the outlier** at 84% commitHash usage - it appears the Claude Code harness or system prompt for this run included better guidance about using commitHash.

**Skill pointer**: The `bytebell-commit-aware` skill should enforce:
```
When the question references a specific commit/version:
1. Extract the commitHash from the question
2. CARRY commitHash through ALL subsequent calls - smart_search, retrieve_file, keyword_lookup
3. Use FileVersion nodes (not FileNode) for historical state
```

---

### 3.4 BOTTLENECK: Wasted Tool Calls (GPT-5.4-nano)

GPT-5.4-nano made **31 non-search MCP calls** that were entirely wasted:
- `save_conversation_history`: 19 calls - the model tried to "save" its work as a conversation, which is not relevant to the task
- `submit_feedback`: 12 calls - the model tried to submit tool feedback about its own failures, e.g., "apply_patch tool failed verification"

**Root cause**: The model saw these tools available and used them as a coping mechanism when it couldn't figure out how to apply patches. It's treating MCP tools as a general-purpose assistant rather than a code knowledge retrieval system.

**Skill pointer**: Tool descriptions should be clearer about when NOT to use certain tools:
```
save_conversation_history: For multi-session research only. NOT for task bookkeeping.
submit_feedback: For genuine tool bugs only. NOT for task frustration.
```

---

### 3.5 BOTTLENECK: Sonnet Kilo Using webfetch Instead of MCP (7 calls)

Sonnet on Kilo made 8 `webfetch` calls (7 on astropy-7166 alone), presumably trying to fetch code from GitHub directly instead of using the MCP knowledge graph. This is a complete bypass of the MCP workflow.

**Skill pointer**: The system prompt or skill should state:
```
NEVER fetch code from GitHub/external URLs. ALL code is available through ByteBell MCP tools.
```

---

### 3.6 BOTTLENECK: GPT-5.4-mini Malformed Inputs (124 unparseable retrieve_file inputs)

70% of GPT-5.4-mini's retrieve_file calls had inputs that couldn't be parsed as JSON. This suggests the model is generating malformed tool call inputs.

**Skill pointer**: This is a model capability issue, not a skill issue. However, tool descriptions with explicit parameter examples would help:
```
retrieve_file({
  "knowledgeId": "uuid-here",
  "operation": "content",
  "relativePath": "path/to/file.py",
  "fromLine": 1,
  "toLine": 50
})
```

---

## 4. Task-Level Analysis: Extreme Cases

### 4.1 Hardest Tasks (highest MCP calls across runs)

| Task | Issue | Avg MCP Calls | Worst Run |
|------|-------|---------------|-----------|
| astropy-13398 | ITRS to AltAz transform | 26.8 | sonnet_kilo (62 calls, $3.01) |
| astropy-13236 | Remove NdarrayMixin auto-transform | 22.2 | sonnet_kilo (48 calls, $1.44) |
| astropy-13453 | HTML table format | 23.2 | gpt54nano (43 calls, $0.12) |
| astropy-14598 | FITS Card long string | 20.7 | gpt54nano (36 calls, $0.08) |
| astropy-13977 | Quantity ufunc | 17.5 | gpt54nano (37 calls, $0.05) |

These tasks required exploring multiple interconnected files across the astropy codebase. The models struggled with:
1. **Finding the right entry point** - many smart_search queries returned irrelevant results
2. **Understanding the call chain** - bugs in transformation code require tracing through multiple layers
3. **Scoping the fix** - knowing when you have enough context to write the patch

### 4.2 Easiest Tasks (lowest MCP calls)

| Task | Issue | Avg MCP Calls | Best Run |
|------|-------|---------------|----------|
| astropy-7671 | minversion LooseVersion | 5.2 | sonnet_cc (2 calls) |
| astropy-14309 | is_fits IndexError | 8.2 | sonnet_kilo (5 calls) |
| astropy-14995 | NDData mask propagation | 8.2 | gpt54nano (1 call!) |

These were localized bugs where the fix was in a single obvious file. Models found the right code quickly.

---

## 5. Tool Call Sequence Patterns (What Works vs What Doesn't)

### 5.1 Efficient Pattern (sonnet_cc typical flow)
```
list_knowledge -> smart_search -> retrieve_file(metadata) -> retrieve_file(content, targeted) -> [answer]
```
4-6 MCP calls total. The model gets the knowledgeId, searches semantically, reads metadata for structure, then reads the specific code section.

### 5.2 Inefficient Pattern (sonnet_kilo typical flow)
```
list_knowledge -> smart_search -> retrieve_file -> retrieve_file -> retrieve_file -> ... (20-50x) -> [answer]
```
The model finds a starting point but then reads file after file linearly, often re-reading the same file with different line ranges.

### 5.3 Exploration-Heavy Pattern (gpt54mini typical flow)
```
list_knowledge -> get_repo_hubs -> graph_search -> graph_search -> keyword_lookup -> retrieve_file -> graph_search -> keyword_lookup -> retrieve_file -> [answer]
```
More diverse tool usage but excessive graph exploration before settling on the right files.

### 5.4 Disoriented Pattern (opus_cc with wrong knowledgeId)
```
smart_search(knowledgeId="astropy") [FAIL] -> list_knowledge -> smart_search(correct UUID) -> retrieve_file -> ...
```
Wastes the first call on a guessed knowledgeId.

---

## 6. Actionable Skill Pointers for skills_integration.md

Based on this analysis, the following specific behaviors should be encoded into ByteBell skills:

### P1: Search Workflow Discipline (bytebell-code-search.md)
- **Force `list_knowledge` first** unless knowledgeId is already known from context
- **Ban knowledgeId guessing** - explicit rule: "knowledgeId is always a UUID"
- **Enforce metadata-first pattern**: `retrieve_file(metadata)` before `retrieve_file(content)`
- **Limit consecutive retrieve_file calls**: After 5 retrieve_file calls without a search step, the skill should suggest pivoting to `smart_search`, `keyword_lookup`, or `graph_search` to reorient
- **Include commitHash carry-through rule**: If the question specifies a commit, ALL subsequent calls must include it

### P2: Graph Exploration Guard (bytebell-graph-explore.md)
- **Cap exploration depth**: After `get_repo_hubs` + 2 `graph_search` calls, the model should have enough orientation to start targeted retrieval
- **Prefer keyword_lookup over graph_search** for finding specific functions/classes (keyword_lookup is more precise)
- **Never use `webfetch` or external URLs** when MCP tools are available

### P3: Commit-Scoped Analysis (bytebell-commit-aware.md)
- **Extract commitHash from question text** as first step
- **Carry through ALL calls** - this was the #1 gap across non-sonnet_cc runs
- **Validate code version**: If a file's content doesn't match expected version, re-fetch with commitHash

### P4: Tool Hygiene (part of minimal prompt)
- **Ban save_conversation_history** in evaluation/task contexts
- **Ban submit_feedback** unless a genuine tool malfunction is observed
- **Limit list_knowledge** to once per session (data doesn't change mid-session)
- **Warn about malformed inputs**: Include 1-2 concrete JSON examples per tool

### P5: Task-Specific Efficiency Hints
For bug-fix tasks specifically:
```
1. Read the failing test first (retrieve_file with test path from FAIL_TO_PASS)
2. Use keyword_lookup to find the function under test
3. retrieve_file(metadata) on the source file
4. retrieve_file(content, targeted lines) on the bug location
5. Write the fix - typically 1-5 lines changed
```
This 5-step pattern, fresh in context at task start, would prevent the 20-50 call retrieve_file spirals.

---

## 7. Data Files

- Full raw analysis: `results_swe_bench/_full_mcp_analysis.json`
- Per-run detailed reports: `results_swe_bench/{run_dir}/_mcp_analysis.json`

---

## 8. Summary of Key Findings

| Finding | Impact | Fix |
|---------|--------|-----|
| retrieve_file looping (229x in sonnet_kilo) | 77% of all MCP calls are retrieve_file | Skill enforces metadata-first + search-between-reads |
| Wrong knowledgeId (29 failures in opus) | Wasted calls + retries | Skill mandates list_knowledge first |
| Missing commitHash (65-88% of calls) | Reading wrong code version | Skill enforces commitHash carry-through |
| Wasted non-search tools (31 calls in nano) | Token waste | Clearer tool descriptions + ban list |
| webfetch bypass (8 calls in sonnet_kilo) | Bypasses knowledge graph entirely | Explicit "no external URLs" rule |
| Malformed inputs (124 in gpt54mini) | Failed tool calls | Better parameter examples in tool descriptions |
| No metadata-before-content pattern | Blind file reading | Skill demonstrates section_map workflow |

The single highest-impact improvement would be **enforcing the metadata-first retrieve_file pattern** combined with **search-between-reads discipline**. This alone would likely cut MCP call counts by 40-60% across all models.
