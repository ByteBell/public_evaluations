# ByteBell MCP — Speed-First Query Prompt

Answer the question below using **only** ByteBell MCP tools. Optimize for speed and accuracy.

---

## Hard Rules

1. **ONLY use ByteBell MCP tools** — no local file reads, no git APIs, no GitNexus skills.
2. **Parallelize** — every tool call that doesn't depend on a previous result MUST be fired in the same batch. Never serialize independent calls.
3. **Always use `base_commit` as `commitHash`** on every `retrieve_file` call. The latest indexed commit may contain the fix — you need the code as it was when the bug existed. Never fetch latest first then re-fetch at base. Double-fetching wastes ~40% of total time.
4. **Skip `retrieve_file(metadata)`** — for bug-finding, search tools already tell you which files matter. Go straight to `operation: content` with a line range. The metadata round-trip is wasted time.
5. **Record timestamps** — run `date +%s` at task start and end. Elapsed = end − start.

---

## Tool Selection Guide

You have a diverse toolset. Pick the right tool for the job — don't default to one tool for everything.

| Situation | Best tool | Why |
|---|---|---|
| You have class/function/variable names from the question | `keyword_lookup` | Exact match on OrgKeyword nodes — fastest, most precise. Returns files + line context. |
| You need to understand what the bug is about broadly | `smart_search` | Semantic search across file summaries and keywords. Good for finding relevant files when you don't know exact names. |
| You know the file path and need to read specific lines | `retrieve_file` (content) | Direct file content. Always pass `commitHash: <base_commit>` and a tight `startLine/endLine`. |
| You need to find which files import/use a specific symbol | `keyword_lookup` or `cypher` | keyword_lookup for quick hits; cypher `MATCH (ok:OrgKeyword {name:...})-[:APPEARS_IN_FILE]->(fv)` for exhaustive cross-file traces. |
| You need to understand how a module/folder is structured | `graph_traverse` (folder) | Returns direct children with summaries. Useful when search didn't pinpoint the exact file. |
| You need relationships between files (imports, dependencies) | `graph_traverse` (folder_dependency_graph) or `cypher` | When the bug spans multiple files or you need call-chain context. |
| You need to check what files changed at a commit | `cypher` on FileVersion nodes | `MATCH ... {commit_hash: '<hash>'} RETURN fn.relative_path, fv.change_type` |
| You need the repo's high-level architecture | `get_repo_hubs` | Hub analysis — use only if you're lost and need orientation. Expensive, use sparingly. |

### Parallel batching rules

These tools are **always independent** and can fire together:
- `keyword_lookup` + `smart_search` (different search strategies, combine results)
- Multiple `retrieve_file` calls for different files
- `keyword_lookup` for different keywords
- `date +%s` alongside any MCP call

These tools **depend on prior results** — must wait:
- `retrieve_file(content)` depends on knowing which file + line range (from search results)
- `cypher` with specific commit hashes depends on discovering valid hashes first

### Anti-patterns (things that waste time)

- **Calling `retrieve_file(metadata)` before `retrieve_file(content)`** — search results already identify the files. Go straight to content.
- **Fetching files without `commitHash`** — you get the latest version which may contain the fix. Always scope to `base_commit`.
- **Fetching the same file twice** at different commits — decide the right commit before your first call.
- **Using `smart_search` when you have exact symbol names** — use `keyword_lookup` instead, it's faster and more precise.
- **Calling `graph_traverse(repo)` to explore** — this is browsing, not searching. Use only if you genuinely can't identify the relevant area from search.
- **Single-threading calls** — if you're about to call keyword_lookup then smart_search sequentially, batch them.

---

## Target Knowledge Base

- **Knowledge ID:** `eb768039-0fd9-4051-bf82-44ce31015d78`
- **Name:** `astropy`
- **Type:** `CODE`

Always scope queries to this knowledge ID.

---


## Indexed Commits

The graph only has `FileVersion`/`FolderVersion` nodes for indexed commits. If you need commit-scoped queries, first run:

```cypher
MATCH (k:Knowledge {knowledge_id: 'eb768039-0fd9-4051-bf82-44ce31015d78'})
MATCH (k)-[:HAS_FILE]->(fn:FileNode)-[:HAS_VERSION]->(fv:FileVersion)
RETURN collect(DISTINCT fv.commit_hash) AS commits
LIMIT 1
```

Never guess commit hashes — only use hashes from this query.

---

## Token Tracking

Track tokens per tool call. Estimate using these rough sizes:

- **Search calls** (smart_search, graph_search, keyword_lookup): ~2,000–10,000 tokens per call
- **File retrieval**: ~500–4,000 tokens per call depending on line count
- **Graph traversal / cypher**: ~1,000–8,000 tokens per call
- **Thinking tokens**: ~150 tokens/second of reasoning time

**Cost rates:** Input $3/M, Output $15/M, MCP processing $0.

---

## Output Format

Output a **single JSON object** exactly matching this schema. No markdown wrapping, no commentary outside the JSON.

```json
{
  "instance_id": "<repo>__<repo>-<issue_number>",
  "base_commit": "<commit hash from the question>",
  "question_summary": "<1-2 sentence summary of the bug/issue>",

  "root_cause": {
    "file": "<relative file path>",
    "line": <line number where bug starts>,
    "description": "<clear explanation of WHY the bug occurs>",
    "buggy_code": "<exact buggy code snippet>"
  },

  "fix": {
    "file": "<relative file path>",
    "line": <line number where fix applies>,
    "description": "<what the fix does and why it works>",
    "patch": {
      "old": "<exact original code block>",
      "new": "<exact fixed code block>"
    }
  },

  "new_test": {
    "file": "<test file path>",
    "test_name": "<test function name>",
    "code": "<complete test function code>"
  },

  "evidence": {
    "buggy_code_location": "<file:lines at commit hash>",
    "fix_commit": null,
    "fix_commit_message": null,
    "fix_author": null,
    "fix_date": null
  },

  "analysis": {
    "code_at_base_commit": {
      "lines_NNN_MMM": "<relevant code at the base commit>"
    },
    "explanation": "<full technical explanation of the bug and fix>",
    "minimal_fix": "<1-sentence description of the minimal change needed>"
  },

  "token_tracking": {
    "tool_calls": [
      {"tool": "<tool name>", "counted_tokens": <estimated tokens>}
    ],
    "tool_input_subtotal": <sum of all tool response tokens>,
    "thinking_tokens": <total_thinking_seconds * 150>,
    "total_input_tokens": <tool_input_subtotal + thinking_tokens>,
    "total_output_tokens": <tokens in this JSON response>,
    "input_cost_usd": <total_input_tokens / 1000000 * 3>,
    "output_cost_usd": <total_output_tokens / 1000000 * 15>,
    "total_cost_usd": <input_cost + output_cost>,
    "timing": {
      "start_unix": <epoch from date +%s at start>,
      "end_unix": <epoch from date +%s at end>,
      "elapsed_seconds": <end - start>,
      "tool_calls_count": <total number of tool calls>,
      "avg_seconds_per_tool": <elapsed / tool_calls_count>
    }
  }
}
```

**Field notes:**
- `evidence.fix_commit` etc. are `null` — you are identifying the bug, not the fix commit.
- `analysis.code_at_base_commit` key should be `lines_<start>_<end>` matching the lines you retrieved.
- `token_tracking.tool_calls` — log every MCP tool call and `date +%s` bash calls.
- All costs in USD, rounded to 4 decimal places.
