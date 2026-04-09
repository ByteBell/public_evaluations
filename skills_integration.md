# ByteBell MCP: Skills-Based Context Injection

## Context

ByteBell's MCP server currently injects ~10K+ tokens upfront on every session:

- **960-line system prompt** (~5,100 tokens) via the MCP `instructions` field — always injected, regardless of what the user is doing
- **7 verbose tool descriptions** (~5,100 tokens) — all embed decision trees, channel tables, and multi-step workflows

This is wasteful and incorrect for how modern LLMs receive context. Specifically:

- Tool descriptions in MCP are "on-demand" in some clients — Claude Code may not always surface them in full to the LLM until a tool is invoked
- The `instructions` field IS always injected at session start — so it dominates context even for trivial queries
- Skills (`.claude/skills/`) solve this: Claude Code and Cursor load skill context **only when triggered by user intent**, making context injection lazy and precise

**The second problem**: not all MCP clients support skills. MCP Jam, Postman, and generic HTTP clients get nothing if we strip the system prompt. We need dual-mode behavior: minimal prompt for skill-capable clients, full prompt for legacy clients — selected automatically based on who is connecting.

**Goal**: Reliable, complex tool chains for Claude Code users through just-in-time guidance injection. Token reduction is a side effect — the primary win is behavioral quality.

---

## Why Skills Improve Tool Chain Quality (Not Just Token Count)

This is the core benefit the plan must deliver. Token savings are a side effect. The real improvement is that the LLM gets **actionable, task-specific guidance at the moment of a decision**, not diluted in a 960-line prompt it parsed at session start.

### The Problem with Always-On Prompts

The current system prompt works like a textbook: the LLM reads it at session start, then attempts to recall the relevant section 15 messages later when it's mid-analysis. This is unreliable for complex queries:

- By message 15 of a commit-scoped cross-repo analysis, the rule "carry commitHash through ALL subsequent calls" is buried deep in context — the LLM may drop it
- The 17 critical rules are all equally prominent — the LLM can't prioritize "use retrieve_file metadata first" over less-critical rules when they're in the same list
- The channel selection guidance for `graph_search` (12 channels, complex logic) competes for attention with PDF rules, traverse patterns, and cross-repo guidance — even if none of that is relevant to the current task

### What Skills Change

A skill loads **exactly when the user's intent matches**, injecting only the guidance relevant to the current task. The LLM now has:

- A fresh, high-signal decision tree at the moment it needs to make a decision
- Concrete tool call examples that mirror exactly what it's about to do
- Explicit pivot logic ("if smart_search returns 0 results → do this next")
- Step-by-step chains for complex multi-tool scenarios

### Concrete Scenarios — Before vs After

**Scenario: Commit-scoped cross-repo impact analysis**

_Before (system prompt):_ LLM has a general description of commitHash parameter spread across multiple sections. In a long conversation, it often: forgets to carry commitHash to subsequent calls, uses FileNode instead of FileVersion, doesn't order results by committed_at.

_After (bytebell-commit-aware skill loads):_

```
## Commit-Scoped Analysis Workflow
1. smart_search({ query, commitHash }) — always start here
2. CARRY commitHash to ALL subsequent calls — graph_search, graph_traverse, retrieve_file
3. Use FileVersion nodes (not FileNode) for historical state — FileNode = current only
4. Order by committed_at DESC to find latest version at or before target commit
5. Impact chain: changes in FileA → smart_search(similar, FileA) → find all dependents
```

The LLM now reliably executes the full 5-step chain because the guidance is fresh and task-specific.

---

**Scenario: Cross-repo integration surface analysis**

_Before:_ The integration surface section is on line 620 of the system prompt. The LLM might partially execute it or miss the mirror-pattern logic (api ↔ api_call, event_pub ↔ event_sub).

_After (bytebell-graph-explore skill loads):_

```
## Cross-Repo Breaking Change Detection
1. graph_search(integration, "ServiceA") — find what ServiceA exposes
2. For each surface: graph_search(integration, surface_value) across ALL repos (no knowledgeId)
3. Mirror pattern — surface type pairs: api/api_call, event_pub/event_sub, queue_write/queue_read
4. retrieve_file(metadata) for each dependent → section_map → targeted content
5. Report: {changed_file, dependent_repos[], breaking_change_risk}
```

The LLM now knows to check mirror pairs and run cross-repo searches — guidance it would only execute if it recalled the exact pattern from deep context.

---

**Scenario: Unknown codebase first exploration**

_Before:_ The LLM defaults to smart_search because it's listed first, even when the user hasn't named anything specific to search for. get_repo_hubs guidance is buried.

_After (bytebell-graph-explore skill loads):_

```
## First Exploration of Unknown Codebase
1. list_knowledge — confirm available repos and IDs
2. get_repo_hubs({ knowledgeId }) — PageRank-ranked entry points, purpose, key classes
3. graph_traverse({ operation: "repo" }) — bird's-eye view via RepoSummary
4. graph_traverse({ operation: "folder_tree", path: "/" }) — full structure in one call
5. Only then: smart_search for specific concepts once you know the lay of the land
```

The LLM follows a systematic exploration chain rather than jumping straight to semantic search on a codebase it hasn't oriented to yet.

---

**Scenario: PDF + Code hybrid query**

_Before:_ The LLM mixes PDF and code results, sometimes calling retrieve_file on a PDF node (wrong), sometimes missing that source_type="pdf" requires retrieve_pdf_page.

_After (bytebell-pdf skill loads):_

```
## Reading Results That Mix Code and PDF
- source_type: "code" → retrieve_file(metadata → content)
- source_type: "pdf"  → retrieve_pdf_page(metadata → content)
NEVER call retrieve_file on a PDF node — it will fail
```

This single rule, fresh in context at the moment the mixed results appear, prevents a class of errors that currently requires the LLM to recall source_type routing from the system prompt.

### How Skills Enable This

Skills work because they load at **intent time**, not session time. The decision tree for `bytebell-code-search` loads when the user says "find where X is handled" — at exactly the point the LLM is about to call `smart_search`. The guidance is fresh, specific, and not competing with irrelevant context.

This is fundamentally different from a system prompt: the system prompt hopes the LLM remembers what it read; skills ensure the LLM has what it needs when it needs it.

---

## What Gets Deprecated

| Item                                             | Status                               | Notes                                                           |
| ------------------------------------------------ | ------------------------------------ | --------------------------------------------------------------- |
| 960-line system prompt as default                | Deprecated for skill-capable clients | Renamed to `buildFullInstructions`, kept as fallback for legacy |
| Always-on context injection regardless of client | Deprecated                           | Replaced by client-detected + key-controlled dual-mode          |

## What Is New

| Item                                       | Description                                                                                                                                                                                                         |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.claude/skills/bytebell/` — 6 skill files | Lazy-loaded workflow context for Claude Code / Cursor (distributed/managed by user)                                                                                                                                 |
| `buildMinimalInstructions()`               | ~180-token system prompt for skill-capable clients                                                                                                                                                                  |
| `clientDetection.ts`                       | Pure-function client type detection + instruction mode resolution                                                                                                                                                   |
| `instructionMode` on API key doc           | Per-key variant: `'minimal' \| 'full' \| 'auto'` — keys become explicit configuration profiles                                                                                                                      |
| `MCP_INSTRUCTION_MODE` env var             | Deployment-level override                                                                                                                                                                                           |
| **Conditional tool descriptions**          | Each tool exports two descriptions: full (verbose, current) + minimal (2-3 lines). Mode selected at `registerAllTools` time via `instructionMode`. Duplication within `full` mode will be cleaned up incrementally. |

## API Key as Variant — Mental Model

API keys now carry explicit behavior profiles:

| Key variant                         | `instructionMode` | System prompt                   | Tool descriptions     |
| ----------------------------------- | ----------------- | ------------------------------- | --------------------- |
| Skills key (Claude Code team)       | `'minimal'`       | ~180 tokens                     | Lean (2-3 lines)      |
| Legacy key (MCP Jam / integrations) | `'full'`          | ~5,100 tokens                   | Verbose (current)     |
| Auto key (default)                  | `'auto'`          | Detected from `clientInfo.name` | Follows detected mode |

Skills delivery (distributing skill files to end users' `~/.claude/skills/bytebell/`) is handled separately by the ByteBell team outside this plan.

---

## How Context Injection Actually Works (Real Scenarios)

### Scenario A — Claude Code user asks "find where JWT auth is handled"

1. Claude Code connects → `clientInfo.name = "claude-code"` detected
2. `resolveInstructionMode` → `'minimal'` (180 tokens injected, not 5,100)
3. User types the query → Claude Code pattern-matches against `SKILL.md` triggers
4. `bytebell-code-search.md` loads (~600 tokens) — Claude now has the full search workflow
5. Claude calls `smart_search({ query: "JWT authentication token validation" })`
6. Finds hit → calls `retrieve_file(metadata)` → `retrieve_file(content, fromLine, toLine)`
7. Total context used: 180 (prompt) + 600 (skill, on demand) + tool results = ~1,500 tokens vs 10,200 before

### Scenario B — MCP Jam user asks the same question

1. MCP Jam connects → `clientInfo.name` = unknown/legacy
2. `resolveInstructionMode` → `'full'` (5,100 tokens injected)
3. Full workflow guidance inline — LLM has everything it needs
4. Same quality response, no skills needed

### Scenario C — Operator forces full mode for a specific API key

1. MongoDB: `{ instructionMode: "full" }` on a production key
2. Even if `clientInfo.name = "claude-code"` is detected, API key override wins
3. Claude Code user gets full prompt (useful for enterprise clients who don't use skills)

---

## Skills File Structure

```
/Users/deadbytes/Documents/ByteBell/agent-box/
└── .claude/
    └── skills/
        └── bytebell/
            ├── SKILL.md                    ← master router + graph model overview (~200 tokens)
            ├── bytebell-code-search.md     ← smart_search → graph_search → retrieve_file (~600 tokens)
            ├── bytebell-graph-explore.md   ← graph_traverse, get_repo_hubs, cross-repo (~250 tokens)
            ├── bytebell-pdf.md             ← PDF search + retrieve_pdf_page workflow (~200 tokens)
            ├── bytebell-cypher.md          ← raw Cypher, graph schema, examples (~300 tokens)
            └── bytebell-commit-aware.md    ← commitHash parameter, FileVersion patterns (~180 tokens)
```

**Why repo-local, not `~/.claude/skills/`**: version-controlled with server, deployable via git, available to any dev opening agent-box in Claude Code.

### SKILL.md Format

```markdown
---
name: bytebell
description: >
  ByteBell Knowledge Graph — search, traverse, and retrieve from indexed
  code repositories and PDF documents. Tools: smart_search, graph_search,
  graph_traverse, keyword_lookup, get_repo_hubs, retrieve_file,
  retrieve_pdf_page, cypher.
user-invocable: true
argument-hint: "[search query or task description]"
---

# ByteBell Knowledge Server

[graph model in 5 lines]
[tool roster]
[routing table: intent → which sub-skill to read]
```

Sub-skills (bytebell-code-search.md, etc.) have **no frontmatter** — they are reference documents read by the router skill, not independently invocable. Each sub-skill contains the workflow content moved out of tool descriptions and the system prompt.

---

## buildMinimalInstructions() Content

```
# ByteBell Knowledge Server

A Neo4j-backed code and PDF knowledge graph. Search, traverse, and retrieve
content from indexed repositories.

## Graph Model (Flat Folder)
7 node types: Knowledge → RepoSummary, FolderNode/FolderVersion,
FileNode/FileVersion, OrgKeyword. No levels, no batches.
ALL array fields (classes, functions, imports, keywords, contracts,
integration_surface) are OrgKeyword nodes → APPEARS_IN_FILE → FileVersion.
Omit knowledgeId to search ALL repos.

## Tools
list_knowledge · smart_search · graph_search · graph_traverse ·
keyword_lookup · get_repo_hubs · retrieve_file · retrieve_pdf_page · cypher

## DataMode: {CODE_ONLY|PDF_ONLY|CODE_AND_PDF}

You are a code knowledge assistant. Only respond to queries about indexed
repositories. For unrelated requests, politely redirect.

Pre-loaded: server_info and list_knowledge appended below.
Do NOT re-call these unless you need a refresh.
```

~180 tokens. DataMode conditional content adds ~10 tokens for PDF variant. Off-topic guard stays here (must always be active, not skill-gated).

---

## Client Detection Logic

### New File: `mcp-server/src/core/instructions/clientDetection.ts`

```typescript
export type InstructionMode = "minimal" | "full" | "auto";
export type ClientType = "claude-code" | "cursor" | "legacy" | "unknown";

const SKILL_CAPABLE = ["claude-code", "claude", "cursor"];

export function detectClientType(name: string | undefined): ClientType {
  if (!name) return "unknown";
  const n = name.toLowerCase().replace(/[\s_-]+/g, "-");
  if (SKILL_CAPABLE.some((c) => n.includes(c))) return n.includes("cursor") ? "cursor" : "claude-code";
  return "legacy";
}

export function resolveInstructionMode(
  clientType: ClientType,
  envMode: InstructionMode,
  apiKeyMode: InstructionMode | undefined,
): InstructionMode {
  if (apiKeyMode && apiKeyMode !== "auto") return apiKeyMode; // API key wins
  if (envMode !== "auto") return envMode; // Env var second
  return clientType === "claude-code" || clientType === "cursor" ? "minimal" : "full"; // Auto-detect
}
```

**Fallback chain** (highest → lowest priority):

1. `McpApiKeyDocument.instructionMode` — per-key MongoDB field
2. `MCP_INSTRUCTION_MODE` env var — deployment override
3. `clientInfo.name` from MCP initialize handshake — auto-detect
4. Default: `'full'` (safe — unknown client gets full guidance)

### Where clientInfo is Extracted

In `sessionService.ts` → `handleMcpSession()` → inside `isInitializeRequest(body)` branch — this is the only place where both the MCP initialize payload and `mcpContext` are simultaneously available.

---

## Token Budget Summary

| Context Component  | Before      | After (minimal key)             | After (full key)       |
| ------------------ | ----------- | ------------------------------- | ---------------------- |
| System prompt      | ~5,100      | ~180                            | ~5,100 (unchanged)     |
| Tool descriptions  | ~5,100      | ~760 (trimmed — 7 tools × ~100) | ~5,100 (unchanged)     |
| Skills (on demand) | 0           | 0–1,530 per query               | 0 (not applicable)     |
| **Total upfront**  | **~10,200** | **~940**                        | **~10,200**            |
| **Savings**        | —           | **~91% reduction**              | **0% (no regression)** |

---

## Critical Files to Modify

| File                                                      | Change                                                                                                                                   |
| --------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `mcp-server/src/auth/types.ts`                            | Add `instructionMode?: 'minimal' \| 'full' \| 'auto'` to both `McpApiKeyDocument` and `ValidatedMcpApiKey`                               |
| `mcp-server/src/config.ts`                                | Add `mcpInstructionMode: process.env.MCP_INSTRUCTION_MODE \|\| 'auto'`                                                                   |
| `mcp-server/src/middleware/mcpAuthMiddleware.ts`          | Copy `instructionMode` from keyDoc into returned `ValidatedMcpApiKey`                                                                    |
| `mcp-server/src/services/sessionService.ts`               | Extract `body.params.clientInfo.name` on initialize, call `detectClientType` + `resolveInstructionMode`, pass mode to `createMcpSession` |
| `mcp-server/src/core/server/setupMcpServer.ts`            | Accept `instructionMode` param, branch on `buildMinimalInstructions` vs `buildFullInstructions`                                          |
| `mcp-server/src/core/instructions/defaultInstructions.ts` | Add `buildMinimalInstructions(mode)`, rename existing to `buildFullInstructions`, keep `buildInstructions` as alias                      |
| `mcp-server/src/core/tools/smartSearch.ts`                | Add `descriptionMinimal` (2-3 lines) alongside existing `description` (full)                                                             |
| `mcp-server/src/core/tools/graphSearch.ts`                | Add `descriptionMinimal` — lean version, remove cheat sheet prose                                                                        |
| `mcp-server/src/core/tools/graphTraverse.ts`              | Add `descriptionMinimal` — keep operations table, remove pattern prose                                                                   |
| `mcp-server/src/core/tools/retrieveFile.ts`               | Add `descriptionMinimal` — keep operations/params, remove three-step prose                                                               |
| `mcp-server/src/core/tools/cypher.ts`                     | Add `descriptionMinimal` — keep schema + constraints header only                                                                         |
| `mcp-server/src/core/tools/keywordLookup.ts`              | Add `descriptionMinimal` — keep type list, remove "when to use" prose                                                                    |
| `mcp-server/src/core/tools/getRepoHubs.ts`                | Add `descriptionMinimal` — 2-line description                                                                                            |
| `mcp-server/src/core/tools/retrievePdfPage.ts`            | Add `descriptionMinimal` — keep operations block + rules only                                                                            |
| `mcp-server/src/core/tools/index.ts`                      | Pass `instructionMode` to `registerAllTools`; each tool selects description based on mode                                                |

### New Files to Create

| Path                                                  | Purpose                                              |
| ----------------------------------------------------- | ---------------------------------------------------- |
| `mcp-server/src/core/instructions/clientDetection.ts` | Client type detection + instruction mode resolution  |
| `.claude/skills/bytebell/SKILL.md`                    | Master skill with frontmatter + routing table        |
| `.claude/skills/bytebell/bytebell-code-search.md`     | Full code search workflow (from defaultInstructions) |
| `.claude/skills/bytebell/bytebell-graph-explore.md`   | graph_traverse + structural navigation               |
| `.claude/skills/bytebell/bytebell-pdf.md`             | PDF workflow                                         |
| `.claude/skills/bytebell/bytebell-cypher.md`          | Cypher reference with graph schema                   |
| `.claude/skills/bytebell/bytebell-commit-aware.md`    | Commit-scoped analysis patterns                      |

---

## Implementation Phases

### Phase 1: Additive Infrastructure (zero behavior change)

1. Add `instructionMode?` to `McpApiKeyDocument` + `ValidatedMcpApiKey` in `types.ts`
2. Add `mcpInstructionMode` to `config.ts`
3. Create `clientDetection.ts` (pure functions, not yet wired)
4. Add `buildMinimalInstructions()` to `defaultInstructions.ts`, rename existing to `buildFullInstructions`, keep `buildInstructions` alias

### Phase 2: Wire Up Detection (first behavior change)

5. Update `mcpAuthMiddleware.ts` to copy `instructionMode` from keyDoc
6. Update `sessionService.ts` to extract `clientInfo.name` and resolve mode
7. Update `setupMcpServer.ts` to accept and apply `instructionMode`
8. At this point: Claude Code gets minimal prompt, others get full. Verify via logs.

### Phase 3: Create Skills Files

9. Create `.claude/skills/bytebell/` directory + all 6 skill files
10. Content is sourced from existing `defaultInstructions.ts` and tool descriptions — reorganization, not rewrite

### Phase 4: Add Minimal Tool Descriptions

11. For each tool file, add `descriptionMinimal` export (2-3 lines) alongside the unchanged `description` (full)
12. Update `registerAllTools` in `index.ts` to accept `instructionMode` and select the correct description per tool
13. Full descriptions are untouched — no regression for `full` mode clients

---

## Verification

**Unit tests for `clientDetection.ts`:**

- `"claude-code"`, `"Claude Code"` → `'claude-code'`
- `"cursor"` → `'cursor'`
- `"mcp-inspector"`, `"mcp-jam"`, `undefined` → `'legacy'` / `'unknown'`
- `resolveInstructionMode` with all combination of apiKey/env/client type values

**Integration check via server logs:**

- Add log line in `setupMcpServer`: `instructionMode=minimal tokens=~180 client=claude-code`
- Connect Claude Code → verify `minimal` in logs
- Connect mcp-inspector → verify `full` in logs

**Per-key override test:**

- Set `{ instructionMode: "full" }` on a test MongoDB API key
- Connect Claude Code with that key → logs should show `full`

**Live skill test (Claude Code):**

- Ask a search query → verify bytebell-code-search.md loads
- Verify 3-call workflow executes (smart_search → metadata → content)

**Regression: PDF workflow (CODE_AND_PDF DataMode):**

- Verify `retrieve_pdf_page` works correctly using skill guidance alone
- `source_type: "pdf"` results correctly route to `retrieve_pdf_page`

**Env var override:**

- `MCP_INSTRUCTION_MODE=minimal` → legacy client gets minimal prompt (useful for skills testing without Claude Code)
- `MCP_INSTRUCTION_MODE=full` → full rollback for all clients

---

## Appendix: Empirical Findings from MCP Log Analysis (2026-04-08)

> Based on analysis of 6 MCP-enabled runs (22 astropy SWE-bench tasks each, 132 task-runs total) across Claude Sonnet CC, Claude Opus CC, Kilo+Sonnet, Kilo+GPT-5.4-mini, Kilo+GPT-5.4-nano, and Kilo+Qwen 3.6-plus.
> Full report: `results_swe_bench/mcp_exploration_report.md`
> Raw data: `results_swe_bench/_full_mcp_analysis.json`

### Finding 1: retrieve_file Looping Is the #1 Cost Driver

`retrieve_file` accounts for **52–77% of all MCP calls** across every run. The dominant anti-pattern is long chains of consecutive `retrieve_file(content)` calls without any search or metadata step in between.

- Worst case: Kilo+Sonnet made **229 retrieve_file→retrieve_file→retrieve_file triplets** across 22 tasks, costing $18.68 total.
- Models read files blind — they skip `retrieve_file(metadata)` which returns the `section_map` (classes, functions, line ranges), then resort to scanning with overlapping `fromLine/toLine` windows.

**Skill action for `bytebell-code-search.md`:**
```
## Mandatory Pattern: Metadata Before Content
1. retrieve_file({ operation: "metadata" }) — get section_map, line count, imports
2. Pick the section you need from section_map
3. retrieve_file({ operation: "content", fromLine, toLine }) — targeted read

NEVER call retrieve_file(content) on a full file without checking metadata first.
After 3 consecutive retrieve_file calls, STOP and re-orient with smart_search or keyword_lookup.
```

### Finding 2: Wrong knowledgeId Causes Cascading Failures

Opus CC used guessed knowledgeId values (`"astropy"`, `"astropy__astropy"`, `"astropy__astropy-14096"`) instead of the actual UUID in **19 of 22 tasks**, causing **29 MCP failures**. Every failure triggered a retry cycle: fail → call `list_knowledge` → re-attempt with correct UUID.

**Skill action for `bytebell-code-search.md`:**
```
## Rule: Never Guess knowledgeId
knowledgeId is ALWAYS a UUID (e.g. "eb768039-0fd9-4051-bf82-44ce31015d78").
It is NEVER a repo name, task ID, or slug.
If you don't have it, call list_knowledge FIRST. This call is cheap (<100ms).
```

### Finding 3: commitHash Is Dropped in 65–88% of Calls

Each SWE-bench task specifies a `base_commit` — the exact version where the bug exists. Yet most runs omit `commitHash` from their MCP calls, fetching the latest indexed version instead.

| Run | Calls WITH commitHash | Calls WITHOUT |
|-----|-----------------------|---------------|
| Sonnet CC | **84%** | 16% |
| Opus CC | 12% | **88%** |
| Sonnet Kilo | 15% | **85%** |
| GPT-5.4-mini | 36% | 64% |
| GPT-5.4-nano | 32% | 68% |
| Qwen | 16% | **84%** |

Sonnet CC is the only run that reliably uses commitHash — its harness/prompt apparently enforces this. All others are reading potentially wrong code versions.

**Skill action for `bytebell-commit-aware.md`:**
```
## Rule: Carry commitHash Through Every Call
When the question references a specific commit or version:
1. Extract the commitHash from the question (40-char hex string after "commit")
2. Pass commitHash to EVERY subsequent call: smart_search, keyword_lookup, retrieve_file
3. If you forget and get unexpected results, re-fetch with commitHash before concluding

Omitting commitHash means you may read code that has already been fixed or restructured.
```

### Finding 4: Wasted Non-Search Tool Calls

GPT-5.4-nano made **19 `save_conversation_history`** and **12 `submit_feedback`** calls — these are not knowledge retrieval tools and contributed nothing to answering questions. The model used them as coping mechanisms when it got stuck.

Kilo+Sonnet made **8 `webfetch` calls** to GitHub, completely bypassing the MCP knowledge graph.

**Skill action for minimal prompt / tool descriptions:**
```
## Tools You Should NOT Call During Code Analysis Tasks
- save_conversation_history — for multi-session research only, not task bookkeeping
- submit_feedback — for genuine tool bugs only, not task frustration
- get_conversation — only if explicitly resuming a prior session
- webfetch / external URLs — ALL code is available through ByteBell tools; never fetch from GitHub
```

### Finding 5: Optimal vs Wasteful Tool Sequences

**Efficient (4–6 MCP calls, typical of best sonnet_cc tasks):**
```
list_knowledge → smart_search → retrieve_file(metadata) → retrieve_file(content, targeted) → answer
```

**Wasteful (20–62 MCP calls, typical of worst kilo tasks):**
```
list_knowledge → smart_search → retrieve_file → retrieve_file → retrieve_file → ... (×50) → answer
```

**Disoriented (opus_cc with wrong knowledgeId):**
```
smart_search(knowledgeId="astropy") [FAIL] → list_knowledge → smart_search(correct UUID) → ...
```

The efficient pattern should be the **canonical example** in `bytebell-code-search.md`.

### Finding 6: Task Difficulty Correlates with File Spread, Not Bug Complexity

The hardest tasks (highest MCP call counts) were those requiring code from **multiple interconnected files** (e.g. astropy-13398: ITRS transformations touching 5+ files across coordinate frames). The easiest were single-file bugs.

**Skill action for `bytebell-graph-explore.md`:**
```
## Multi-File Bug Investigation
When a bug spans multiple files:
1. Start with keyword_lookup or graph_search to map the dependency chain
2. Use graph_traverse({ operation: "repo" }) for bird's-eye structure
3. Retrieve only the files in the dependency chain — don't scan broadly
```

### Summary: Priority Actions for Skill Files

| Priority | Skill File | Key Rule | Expected Impact |
|----------|-----------|----------|-----------------|
| P1 | bytebell-code-search.md | Metadata-first retrieve_file + search-between-reads | 40–60% MCP call reduction |
| P2 | bytebell-code-search.md | Never guess knowledgeId; list_knowledge first | Eliminates 29 failures (opus pattern) |
| P3 | bytebell-commit-aware.md | Carry commitHash through ALL calls | Correct code version in 65–88% more calls |
| P4 | Minimal prompt | Ban wasted tools (save_conversation, submit_feedback, webfetch) | Saves 39+ wasted calls |
| P5 | bytebell-graph-explore.md | Multi-file bugs: map dependencies first, then retrieve targeted | Prevents 50-call spirals on hard tasks |
