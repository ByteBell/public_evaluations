# Neo4j Knowledge Graph — Schema & Understanding Guide

> How to read, understand, and query the knowledge graph. This document explains what each node means, what its properties tell you, and how everything connects.

---

## The Big Picture

The graph represents a **fully-analyzed code repository**. When you open Neo4j Browser and look at the data, you'll see a hierarchy:

```
Knowledge (the repo)
  ├── RepoSummary (bird's-eye view of the whole repo)
  │     └── LevelSummary (one per depth level)
  │           ├── LevelBatch (chunks of files/folders at this level)
  │           └── FolderNode (directories at this level)
  ├── FolderNode (root folders)
  │     ├── FolderNode (subfolders)
  │     └── FileNode (source files)
  ├── FileNode (flat access to all files)
  └── OrgKeyword (semantic tags linking to files)
```

---

## Node Types

### Knowledge

The **root node** of a repository. Everything in the graph connects back to this.

| Property       | Meaning                                             |
| -------------- | --------------------------------------------------- |
| `knowledge_id` | UUID — the primary identifier for this repo's graph |
| `org_id`       | Organization that owns this repo                    |

**How to find it**: `MATCH (k:Knowledge {knowledge_id: "..."}) RETURN k`

---

### FileNode

Represents a **single source file** that was analyzed. This is the most detailed node — it contains structural analysis (classes, functions, imports), semantic analysis (domain concepts, business entities), and AI-generated summaries.

| Property              | Type     | What it tells you                                                                                               |
| --------------------- | -------- | --------------------------------------------------------------------------------------------------------------- |
| `node_id`             | string   | Same as `relative_path` — unique within a knowledge_id                                                          |
| `relative_path`       | string   | Path from repo root, e.g. `"src/services/auth/login.ts"`                                                        |
| `name`                | string   | Just the filename, e.g. `"login.ts"` (auto-extracted from path)                                                 |
| `knowledge_id`        | string   | Which Knowledge this file belongs to                                                                            |
| `org_id`              | string   | Organization identifier                                                                                         |
| `repo_name`           | string   | Repository name                                                                                                 |
| `branch_name`         | string   | Git branch that was analyzed                                                                                    |
| `language`            | string   | Programming language: `"typescript"`, `"python"`, `"go"`, etc.                                                  |
| `purpose`             | string   | One-line AI summary of what the file does                                                                       |
| `summary`             | string   | Detailed multi-section summary (JSON stringified if structured)                                                 |
| `section_map`         | string   | Pipe-separated table of contents: `"L1-25: Imports \| L26-80: AuthService"`                                     |
| `is_big_file`         | string   | `"isABigFile"` or `"notABigFile"` — whether the file was too large and had to be split into chunks for analysis |
| `classes`             | string[] | Class names defined in this file, e.g. `["AuthService", "SessionManager"]`                                      |
| `functions`           | string[] | Function names defined in this file, e.g. `["login", "logout"]`                                                 |
| `imports_internal`    | string[] | Imports from within the repo: `["./config", "../utils/crypto"]`                                                 |
| `imports_external`    | string[] | Third-party imports: `["express", "jsonwebtoken"]`                                                              |
| `contracts_provided`  | string[] | APIs/interfaces this file exposes to other files                                                                |
| `contracts_consumed`  | string[] | APIs/interfaces this file depends on from other files                                                           |
| `ontology_concepts`   | string[] | Domain concepts: `["authentication", "session_management"]`                                                     |
| `business_entities`   | string[] | Business objects: `["user", "session", "token"]`                                                                |
| `system_capabilities` | string[] | What the system can do: `["user_login", "token_validate"]`                                                      |
| `keywords`            | string[] | General tags: `["auth", "jwt", "middleware"]`                                                                   |
| `side_effects`        | string[] | Runtime effects: `["writes_session_store", "sends_auth_event"]`                                                 |
| `config_dependencies` | string[] | Config the file needs: `["JWT_SECRET", "SESSION_TTL"]`                                                          |
| `data_flow_direction` | string   | How data moves through this file: `"Receives credentials, produces JWT tokens"`                                 |

**Unique key**: `(node_id, knowledge_id)`

---

### FolderNode

Represents a **directory** in the repository. Contains aggregated metadata from all files inside it.

| Property           | Type     | What it tells you                                                        |
| ------------------ | -------- | ------------------------------------------------------------------------ |
| `node_id`          | string   | Unique ID: `"{orgId}_{repoName}_L{level}_{path_underscored}"`            |
| `relative_path`    | string   | Directory path from repo root: `"src/services/auth"`                     |
| `name`             | string   | Display name: `"L2_folder_auth"` (level prefix + folder name)            |
| `knowledge_id`     | string   | Which Knowledge this belongs to                                          |
| `org_id`           | string   | Organization identifier                                                  |
| `repo_name`        | string   | Repository name                                                          |
| `commit_hash`      | string   | Git commit hash                                                          |
| `level`            | number   | Depth in hierarchy (**bottom-up**: 1 = deepest leaf folders, max = root) |
| `purpose`          | string   | AI-generated summary of what this folder is for                          |
| `summary`          | string   | Detailed summary (JSON stringified)                                      |
| `classes`          | string[] | All classes found in files under this folder                             |
| `functions`        | string[] | All functions found in files under this folder                           |
| `imports_internal` | string[] | All internal imports from files under this folder                        |
| `imports_external` | string[] | All external imports from files under this folder                        |
| `dependency_graph` | string   | Mermaid diagram showing how children depend on each other                |
| `subFileIds`       | string[] | Relative paths of all files in this folder                               |
| `subFolderIds`     | string[] | Relative paths of all subfolders                                         |

**Unique key**: `(node_id, knowledge_id)`

**Level numbering is bottom-up**:

- Level 1 = deepest leaf folders (like `src/services/auth/helpers/`)
- Level 2 = one level above that
- Max level = root-level folders (like `src/`, `config/`, `docs/`)

---

### RepoSummary

The **bird's-eye view** of the entire repository. One per branch.

| Property           | Type     | What it tells you                                          |
| ------------------ | -------- | ---------------------------------------------------------- |
| `knowledge_id`     | string   | Which Knowledge this belongs to                            |
| `org_id`           | string   | Organization identifier                                    |
| `repo_name`        | string   | Repository name                                            |
| `user_name`        | string   | GitHub owner                                               |
| `branch_name`      | string   | Which branch this summary describes                        |
| `commit_hash`      | string   | Which commit was analyzed                                  |
| `architecture`     | string   | High-level architecture description                        |
| `data_flow`        | string   | How data flows through the system                          |
| `key_patterns`     | string[] | Design patterns used: `["Factory", "Builder", "Strategy"]` |
| `major_subsystems` | string   | JSON-encoded array of `{name, responsibility}` objects     |
| `max_depth`        | number   | Deepest nesting level                                      |
| `tree`             | string   | Full `tree` command output of the repo structure           |

**Unique key**: `(knowledge_id, org_id, branch_name)` — supports multi-branch repos

---

### LevelSummary

A **semantic overview of one depth level** in the hierarchy. Answers "what kind of code lives at this depth?"

| Property           | Type   | What it tells you                               |
| ------------------ | ------ | ----------------------------------------------- |
| `knowledge_id`     | string | Which Knowledge this belongs to                 |
| `org_id`           | string | Organization                                    |
| `repo_name`        | string | Repository                                      |
| `user_name`        | string | GitHub owner                                    |
| `branch_name`      | string | Git branch                                      |
| `commit_hash`      | string | Git commit                                      |
| `level`            | number | Which depth level (1-based, same as FolderNode) |
| `name`             | string | Display name: `"Level 3 Summary"`               |
| `summary`          | string | AI summary describing what this level contains  |
| `dependency_graph` | string | Concatenated Mermaid diagrams from all batches  |
| `tree`             | string | Tree-formatted view of all items at this level  |

**Unique key**: `(knowledge_id, org_id, branch_name, level)`

---

### LevelBatch

When a level has too many files/folders to summarize at once, it's split into **token-limited batches**. Each LevelBatch is one such chunk.

| Property           | Type     | What it tells you                                                         |
| ------------------ | -------- | ------------------------------------------------------------------------- |
| `node_id`          | string   | ID format: `"{orgId}_{repoName}_L{level}_{itemType}_batch_{batchNumber}"` |
| `knowledge_id`     | string   | Which Knowledge                                                           |
| `org_id`           | string   | Organization                                                              |
| `repo_name`        | string   | Repository                                                                |
| `branch_name`      | string   | Git branch                                                                |
| `level`            | number   | Which level this batch belongs to                                         |
| `batch_number`     | number   | Batch number (1-based)                                                    |
| `total_batches`    | number   | Total batches at this level for this item type                            |
| `item_type`        | string   | `"files"` or `"folders"` — what this batch contains                       |
| `sub_file_ids`     | string[] | Relative paths of files in this batch                                     |
| `sub_folder_ids`   | string[] | Relative paths of folders in this batch                                   |
| `purpose`          | string   | AI summary of what the items in this batch do                             |
| `summary`          | string   | Detailed summary (JSON stringified)                                       |
| `classes`          | string[] | Important classes found in this batch                                     |
| `functions`        | string[] | Important functions found in this batch                                   |
| `imports_internal` | string[] | Internal imports used by items in this batch                              |
| `imports_external` | string[] | External packages used by items in this batch                             |
| `dependency_graph` | string   | Mermaid diagram of cross-item dependencies                                |

**Unique key**: `(node_id, knowledge_id)`

---

### OrgKeyword

A **semantic keyword** extracted from files via LLM analysis. OrgKeywords are scoped to an organization and represent domain concepts, business terms, capabilities, etc.

| Property          | Type   | What it tells you                                               |
| ----------------- | ------ | --------------------------------------------------------------- |
| `keyword`         | string | The keyword itself: `"authentication"`, `"jwt"`, `"user_login"` |
| `semantic_type`   | string | Category (see table below)                                      |
| `org_id`          | string | Organization scope                                              |
| `total_frequency` | number | How many times this keyword appears across all files            |

**Unique key**: `(keyword, semantic_type, org_id)`

**Semantic types** — each keyword belongs to one category:

| semantic_type         | What it represents       | Example keywords                           |
| --------------------- | ------------------------ | ------------------------------------------ |
| `keywords`            | General tags             | `"auth"`, `"middleware"`, `"caching"`      |
| `ontology_concepts`   | Domain concepts          | `"authentication"`, `"payment_processing"` |
| `business_entities`   | Business objects         | `"user"`, `"order"`, `"invoice"`           |
| `system_capabilities` | What the system can do   | `"user_login"`, `"order_processing"`       |
| `side_effects`        | Runtime effects          | `"writes_to_disk"`, `"sends_email"`        |
| `config_dependencies` | Config keys needed       | `"DATABASE_URL"`, `"JWT_SECRET"`           |
| `data_flow_direction` | Data movement patterns   | `"receives_http_produces_events"`          |
| `contracts_provided`  | APIs/interfaces exposed  | `"authservice"`, `"userapi"`               |
| `contracts_consumed`  | APIs/interfaces consumed | `"databaseclient"`, `"rediscache"`         |

---

### Code Element Nodes

These are small, reusable nodes that appear in multiple contexts:

#### Class

| Property       | Meaning                                                                |
| -------------- | ---------------------------------------------------------------------- |
| `name`         | Class name: `"AuthService"`, `"Deployment"`                            |
| `knowledge_id` | Which Knowledge                                                        |
| `org_id`       | Organization                                                           |
| `repo_name`    | Repository                                                             |
| `description`  | What the class does (extracted from `"ClassName: description"` format) |

**Unique key**: `(name, org_id, repo_name)` from FileNode context; `(name, knowledge_id, org_id)` from LevelSummary context

#### Function

| Property       | Meaning                                        |
| -------------- | ---------------------------------------------- |
| `name`         | Function name: `"login"`, `"createDeployment"` |
| `knowledge_id` | Which Knowledge                                |
| `org_id`       | Organization                                   |
| `repo_name`    | Repository                                     |
| `description`  | What the function does                         |

**Unique key**: Same pattern as Class

#### Import (from FileNode)

| Property       | Meaning                                |
| -------------- | -------------------------------------- |
| `path`         | Import path: `"express"`, `"./config"` |
| `type`         | `"internal"` or `"external"`           |
| `org_id`       | Organization                           |
| `repo_name`    | Repository                             |
| `knowledge_id` | Which Knowledge                        |

#### ImportInternal / ImportExternal (from LevelSummary/LevelBatch)

| Property       | Meaning         |
| -------------- | --------------- |
| `path`         | Import path     |
| `knowledge_id` | Which Knowledge |
| `org_id`       | Organization    |

---

## Relationships — How Everything Connects

### Repository Structure (top-down navigation)

```
Knowledge
  │
  ├──[:HAS_FILE]──────────→ FileNode         (flat access to any file)
  ├──[:HAS_FOLDER]─────────→ FolderNode       (flat access to any folder)
  ├──[:HAS_ROOT_FOLDER]────→ FolderNode       (root-level folders only, max level)
  ├──[:HAS_REPO_SUMMARY]──→ RepoSummary      (one per branch)
  └──[:HAS_LEVEL_BATCH]───→ LevelBatch       (flat access to any batch)
```

### Folder Hierarchy (tree navigation)

```
FolderNode (parent)
  ├──[:CONTAINS_FOLDER]──→ FolderNode (child)     parent directory → subdirectory
  └──[:CONTAINS_FILE]────→ FileNode                directory → file inside it
```

The folder hierarchy is computed from `relative_path` — a FolderNode at `"src/services"` contains FolderNode `"src/services/auth"` and FileNode `"src/services/index.ts"`.

### Level Hierarchy (summary navigation)

```
RepoSummary
  └──[:HAS_LEVEL_SUMMARY]──→ LevelSummary (one per depth level)
                                │
                                ├──[:HAS_FOLDER]──────────→ FolderNode (folders at this level)
                                ├──[:INCLUDES_FILE_AT_LEVEL]→ FileNode (files at this level)
                                ├──[:HAS_FILE_BATCH]──────→ LevelBatch (item_type='files')
                                ├──[:HAS_FOLDER_BATCH]────→ LevelBatch (item_type='folders')
                                ├──[:HAS_CLASS]───────────→ Class
                                ├──[:HAS_FUNCTION]────────→ Function
                                ├──[:HAS_INTERNAL_IMPORT]─→ ImportInternal
                                └──[:HAS_EXTERNAL_IMPORT]─→ ImportExternal
```

### Batch Membership (what's inside a batch)

```
LevelBatch
  ├──[:INCLUDES_FILE]────────→ FileNode          (files in this batch)
  ├──[:INCLUDES_FOLDER]──────→ FolderNode        (folders in this batch)
  ├──[:HAS_CLASS]────────────→ Class
  ├──[:HAS_FUNCTION]─────────→ Function
  ├──[:HAS_INTERNAL_IMPORT]──→ ImportInternal
  └──[:HAS_EXTERNAL_IMPORT]──→ ImportExternal
```

### File Code Elements (what a file defines/uses)

```
FileNode
  ├──[:DEFINES_CLASS]────────→ Class              classes defined in this file
  ├──[:DEFINES_FUNCTION]─────→ Function           functions defined in this file
  ├──[:IMPORTS_INTERNAL]─────→ Import (type:"internal")   internal imports
  └──[:IMPORTS_EXTERNAL]─────→ Import (type:"external")   third-party imports
```

### Semantic Keywords (cross-file concept search)

```
OrgKeyword ──[:APPEARS_IN_FILE]──→ FileNode
```

This is the **only relationship with properties**:

| Property     | Type     | Meaning                                                   |
| ------------ | -------- | --------------------------------------------------------- |
| `frequency`  | number   | How many times this keyword appears in this specific file |
| `created_at` | datetime | When this link was first created                          |
| `updated_at` | datetime | When last updated                                         |

---

## How to Navigate the Graph

### "I want to understand the whole repo"

```cypher
MATCH (k:Knowledge {knowledge_id: $id})-[:HAS_REPO_SUMMARY]->(rs:RepoSummary)
RETURN rs.architecture, rs.data_flow, rs.key_patterns, rs.total_files, rs.total_classes
```

### "What are the major areas of the codebase?"

```cypher
MATCH (k:Knowledge {knowledge_id: $id})-[:HAS_ROOT_FOLDER]->(root:FolderNode)
RETURN root.relative_path, root.purpose, root.total_file_count
ORDER BY root.total_file_count DESC
```

### "Show me the folder tree under src/"

```cypher
MATCH (parent:FolderNode {knowledge_id: $id, relative_path: "src"})
      -[:CONTAINS_FOLDER*1..3]->(child:FolderNode)
RETURN child.relative_path, child.level, child.purpose, child.direct_file_count
```

### "What files are in a specific folder?"

```cypher
MATCH (folder:FolderNode {knowledge_id: $id, relative_path: "src/services/auth"})
      -[:CONTAINS_FILE]->(f:FileNode)
RETURN f.relative_path, f.purpose, f.language
```

### "Tell me about a specific file"

```cypher
MATCH (f:FileNode {knowledge_id: $id, relative_path: "src/services/auth/login.ts"})
RETURN f.purpose, f.summary, f.classes, f.functions,
       f.ontology_concepts, f.business_entities, f.contracts_provided
```

### "What files deal with authentication?"

```cypher
MATCH (kw:OrgKeyword {keyword: "authentication", org_id: $orgId})
      -[r:APPEARS_IN_FILE]->(f:FileNode)
RETURN f.relative_path, f.purpose, r.frequency
ORDER BY r.frequency DESC
```

### "What are the most common domain concepts?"

```cypher
MATCH (kw:OrgKeyword {semantic_type: "ontology_concepts", org_id: $orgId})
RETURN kw.keyword, kw.total_frequency, kw.file_count
ORDER BY kw.total_frequency DESC LIMIT 20
```

### "What config does this repo depend on?"

```cypher
MATCH (kw:OrgKeyword {semantic_type: "config_dependencies", org_id: $orgId})
RETURN kw.keyword, kw.file_count
ORDER BY kw.file_count DESC
```

### "Find files that write to disk or send emails"

```cypher
MATCH (f:FileNode {knowledge_id: $id})
WHERE ANY(se IN f.side_effects WHERE se CONTAINS "writes" OR se CONTAINS "sends")
RETURN f.relative_path, f.side_effects, f.purpose
```

### "Which files are big files (split into chunks)?"

```cypher
MATCH (f:FileNode {knowledge_id: $id, is_big_file: "isABigFile"})
RETURN f.relative_path
```

### "What does level 3 of the hierarchy contain?"

```cypher
MATCH (ls:LevelSummary {knowledge_id: $id, level: 3})
RETURN ls.summary, ls.folderCount, ls.fileCount, ls.totalTokenCount
```

### "What are the batches at level 2?"

```cypher
MATCH (ls:LevelSummary {knowledge_id: $id, level: 2})
      -[:HAS_FILE_BATCH]->(batch:LevelBatch)
RETURN batch.batch_number, batch.item_count, batch.purpose, batch.classes
ORDER BY batch.batch_number
```

### "Which files define a specific class?"

```cypher
MATCH (f:FileNode)-[:DEFINES_CLASS]->(c:Class {name: "AuthService"})
RETURN f.relative_path, f.purpose
```

### "What external libraries does this repo use?"

```cypher
MATCH (f:FileNode {knowledge_id: $id})-[:IMPORTS_EXTERNAL]->(i:Import)
RETURN i.path, count(f) AS used_by_files
ORDER BY used_by_files DESC LIMIT 20
```

---

## How to Navigate the Graph with `graph_search`

> **For MCP clients**: `graph_search` is your primary search tool. One call fires 7 parallel channel queries and returns paginated results per channel. Use the decision tree below to reach the target file in **1–2 calls**.

### What `graph_search` returns

A single call returns **7 independent channels**, each with its own `{ data, pagination }`:

| Channel       | What it searches                                         | Best for                                              |
| ------------- | -------------------------------------------------------- | ----------------------------------------------------- |
| **purpose**   | `FileNode.purpose` + `ontology_concepts`                 | Natural-language questions ("where is auth handled?") |
| **classes**   | `FileNode.classes[]`                                     | Finding a known class (`AuthService`, `UserModel`)    |
| **functions** | `FileNode.functions[]`                                   | Finding a known function (`login`, `parseConfig`)     |
| **imports**   | `FileNode.imports_internal[]` + `imports_external[]`     | Finding who uses a library or internal module         |
| **keywords**  | `OrgKeyword` nodes linked via `APPEARS_IN_FILE`          | Domain/concept search (`jwt`, `caching`, `webhook`)   |
| **paths**     | `FileNode.relative_path` + `FolderNode.relative_path`    | Partial path match (`auth`, `middleware`, `utils`)    |
| **glob**      | Regex match on `relative_path` (only when `glob` is set) | File pattern matching (`**/*.test.ts`, `src/api/**`)  |

### Decision tree: pick the fastest route

```
What do you know about the target file?
│
├─ Exact or partial path/filename?
│   → query: the path fragment, read `paths` channel first
│   → or set `glob` param (e.g. "**/*.controller.ts") and read `glob` channel
│
├─ Class or function name?
│   → query: the name, read `classes` or `functions` channel first
│
├─ Library or import it uses?
│   → query: the import name (e.g. "express", "./config"), read `imports` channel
│
├─ Domain concept or business term?
│   → query: the concept (e.g. "authentication session"), read `purpose` + `keywords` channels
│
└─ Vague / exploratory?
    → query: best guess terms, scan ALL channels — the channel with results tells you which dimension matched
```

### Query formulation tips

1. **Use specific, lowercase terms.** The tool splits your query on whitespace and matches each term with `CONTAINS` (case-insensitive). `"auth login"` searches for files where properties contain `"auth"` AND/OR `"login"`.
2. **Multi-word queries cast a wider net.** Each term is matched independently — more terms = more potential hits but also more noise. Use 1–3 precise terms.
3. **Narrow with filters before paginating.** Use optional params to reduce result sets:
   - `knowledgeId` — scope to a single repo
   - `path` — prefix filter (e.g. `"src/services"` only searches within that subtree)
   - `fileRole` — filter by role if you know it
   - `glob` — structural pattern matching (activates the glob channel)
4. **Read the highest-scoring channels first.** Channels with `totalItems > 0` are the relevant ones. If `classes` returns 2 hits and `purpose` returns 40, the class match is likely more precise.

### Reaching the file in 1–2 calls

**Call 1: `graph_search`** — returns `path` + `purpose` per hit across all channels.

- If you see the file you need → done. You have its `path` and `purpose`.
- If multiple candidates → read the `purpose` field to disambiguate.
- If too many results → re-call with a narrower `path` prefix or more specific terms.

**Call 2 (if needed): `getFileDetails`** — pass the `path` from the search result to get full metadata: `summary`, `section_map`, `classes`, `functions`, `imports`, `contracts`, `ontology_concepts`, etc.

### Channel priority by query type

| Query type                   | Read first             | Then check              |
| ---------------------------- | ---------------------- | ----------------------- |
| "Find the UserService class" | `classes`              | `purpose`               |
| "Where is login handled?"    | `purpose`              | `functions`, `keywords` |
| "Files using express"        | `imports`              | `paths`                 |
| "All test files"             | `glob` (`**/*.test.*`) | `paths`                 |
| "Authentication system"      | `keywords`             | `purpose`               |
| "src/services/auth"          | `paths`                | —                       |
| "Payment processing"         | `purpose`              | `keywords`              |

### Pagination

Each channel is independently paginated. Default: `page=1`, `pageSize=20`.

- `pagination.totalItems` — total matches for that channel
- `pagination.hasNextPage` — whether more results exist
- Increment `page` to fetch the next batch (same query, same filters)

### Combining with other tools

| Goal                         | Tool sequence                                     |
| ---------------------------- | ------------------------------------------------- |
| Find a file by concept       | `graph_search` → done (path + purpose in results) |
| Get full file analysis       | `graph_search` → `getFileDetails(path)`           |
| Browse folder structure      | `getRepoOverview` → `listFolders` → `listFiles`   |
| Understand repo architecture | `getRepoOverview` (reads RepoSummary)             |
| Cross-repo search            | `graph_search` without `knowledgeId` (org-scoped) |

---

## Understanding Level Numbering

Levels count **bottom-up** from the deepest folders:

| Level   | Meaning              | Example for a 9-level repo   |
| ------- | -------------------- | ---------------------------- |
| 1       | Deepest leaf folders | `src/services/auth/helpers/` |
| 2       | One above deepest    | `src/services/auth/`         |
| ...     | ...                  | ...                          |
| 9 (max) | Root-level folders   | `src/`, `config/`, `docs/`   |

Root folders (the ones connected via `[:HAS_ROOT_FOLDER]`) always have the **maximum level** number for that repo.

---

## Complete Relationship Reference

| Relationship             | From                    | To             | Properties                              | Meaning                               |
| ------------------------ | ----------------------- | -------------- | --------------------------------------- | ------------------------------------- |
| `HAS_FILE`               | Knowledge               | FileNode       | —                                       | Repo contains this file               |
| `HAS_FOLDER`             | Knowledge               | FolderNode     | —                                       | Repo contains this folder             |
| `HAS_ROOT_FOLDER`        | Knowledge               | FolderNode     | —                                       | Top-level directory                   |
| `HAS_REPO_SUMMARY`       | Knowledge               | RepoSummary    | —                                       | Repo overview (per branch)            |
| `HAS_LEVEL_BATCH`        | Knowledge               | LevelBatch     | —                                       | Flat access to batch                  |
| `HAS_LEVEL_SUMMARY`      | RepoSummary             | LevelSummary   | —                                       | Summary for one depth level           |
| `HAS_FOLDER`             | LevelSummary            | FolderNode     | —                                       | Folders at this level                 |
| `INCLUDES_FILE_AT_LEVEL` | LevelSummary            | FileNode       | —                                       | Files at this level                   |
| `HAS_FILE_BATCH`         | LevelSummary            | LevelBatch     | —                                       | File batch at this level              |
| `HAS_FOLDER_BATCH`       | LevelSummary            | LevelBatch     | —                                       | Folder batch at this level            |
| `CONTAINS_FOLDER`        | FolderNode              | FolderNode     | —                                       | Parent → child directory              |
| `CONTAINS_FILE`          | FolderNode              | FileNode       | —                                       | Directory → file inside it            |
| `DEFINES_CLASS`          | FileNode                | Class          | —                                       | File defines this class               |
| `DEFINES_FUNCTION`       | FileNode                | Function       | —                                       | File defines this function            |
| `IMPORTS_INTERNAL`       | FileNode                | Import         | —                                       | File imports from within repo         |
| `IMPORTS_EXTERNAL`       | FileNode                | Import         | —                                       | File imports a third-party package    |
| `INCLUDES_FILE`          | LevelBatch              | FileNode       | —                                       | Batch contains this file              |
| `INCLUDES_FOLDER`        | LevelBatch              | FolderNode     | —                                       | Batch contains this folder            |
| `HAS_CLASS`              | LevelSummary/LevelBatch | Class          | —                                       | Level/batch references this class     |
| `HAS_FUNCTION`           | LevelSummary/LevelBatch | Function       | —                                       | Level/batch references this function  |
| `HAS_INTERNAL_IMPORT`    | LevelSummary/LevelBatch | ImportInternal | —                                       | Level/batch uses this internal import |
| `HAS_EXTERNAL_IMPORT`    | LevelSummary/LevelBatch | ImportExternal | —                                       | Level/batch uses this external import |
| `APPEARS_IN_FILE`        | OrgKeyword              | FileNode       | `frequency`, `created_at`, `updated_at` | Keyword found in this file N times    |

---

## PageRank-Based File Importance — Reaching Relevant Files Faster

### The Problem: Too Many Sequential Tool Calls

When an MCP client (typically an LLM agent) explores a repo today, the typical flow looks like this:

```
list_knowledge → graph_search → graph_search → graph_search →
getFileDetails → getFileDetails → graph_search (restart) → getFileDetails → ...
```

That's **8-12 tool calls** to reach the right files. The agent searches by keywords one at a time, fetches files one by one, sometimes restarts from scratch because earlier results weren't relevant enough. Each `graph_search` returns results scored only by local text matching (`CONTAINS` on keywords, class names, etc.) — there's no notion of which files are **structurally important** in the codebase. So the agent has to do multiple exploratory searches to figure out what matters.

### Why PageRank Changes Everything

PageRank pre-computes a **global importance score** for every `FileNode` based on how connected it is in the graph. Files that are heavily imported, referenced by many folders, or linked to many semantic keywords naturally rank higher.

This means when a `graph_search` returns 40 results, the agent can **immediately see which 3-5 files are the structural hubs** — and fetch those first. These hub files typically reference or import the remaining files the agent would have searched for anyway, so the information cascades from a single fetch.

**The result: 2-4 tool calls instead of 8-12.**

```
getRepoHubs → graph_search (results pre-sorted by importance) →
getFileDetails (on top 2-3 hits — the actual hubs)
```

### Implementation Strategy

#### Step 1: Build the Weighted Adjacency Graph

The edges that matter for file importance:

| Edge Type            | Signal                                                              |
| -------------------- | ------------------------------------------------------------------- |
| `IMPORTS_INTERNAL`   | FileA imports FileB → strongest signal (direct code dependency)     |
| `APPEARS_IN_FILE`    | OrgKeyword → FileNode (high-frequency keywords boost a file)       |
| `CONTAINS_FILE`      | FolderNode → FileNode (files in root-level folders get slight boost)|
| `DEFINES_CLASS`      | Reverse signal — files defining widely-used classes are important   |
| `DEFINES_FUNCTION`   | Reverse signal — same logic for widely-called functions             |

The key insight: `IMPORTS_INTERNAL` already forms a **directed graph between files**. A file imported by many other files is a hub — exactly what PageRank was designed to find.

#### Step 2: Compute PageRank per `knowledge_id`

Run as a batch job whenever a repo is analyzed (or re-analyzed). Using Neo4j's Graph Data Science library:

```cypher
-- Project the file-imports-file graph
CALL gds.graph.project(
  'file-import-graph',
  'FileNode',
  {
    IMPORTS_INTERNAL: {
      type: 'IMPORTS_INTERNAL',
      orientation: 'REVERSE'  -- files that ARE imported rank high
    }
  },
  {
    nodeProperties: ['knowledge_id'],
    relationshipProperties: {}
  }
)
```

```cypher
-- Run PageRank
CALL gds.pageRank.write('file-import-graph', {
  maxIterations: 20,
  dampingFactor: 0.85,
  writeProperty: 'pagerank'
})
YIELD nodePropertiesWritten, ranIterations
```

After this, every `FileNode` has a `pagerank` property — a float between 0 and 1.

#### Step 3: Compute Semantic Centrality Score

PageRank on imports alone misses files that are **conceptually central** but don't have many direct importers (config files, type definitions, orchestration files). Add a second score based on keyword connectivity:

```cypher
MATCH (f:FileNode {knowledge_id: $kid})
OPTIONAL MATCH (kw:OrgKeyword)-[r:APPEARS_IN_FILE]->(f)
WITH f,
     sum(r.frequency) AS keyword_weight,
     count(DISTINCT kw) AS keyword_diversity
SET f.semantic_centrality = keyword_diversity * 0.7 + keyword_weight * 0.3
```

Then combine into a single composite score:

```cypher
MATCH (f:FileNode {knowledge_id: $kid})
SET f.importance = 0.6 * f.pagerank + 0.4 * (f.semantic_centrality / max_semantic)
```

The **0.6 / 0.4 weighting** means structural connectivity (imports) matters more than semantic tagging, but both contribute.

#### Step 4: Sort `graph_search` Results by Importance

Every channel now uses the composite importance score as a **sort tiebreaker**:

```cypher
-- Before (current behavior):
MATCH (f:FileNode) WHERE f.purpose CONTAINS $term
RETURN f.relative_path, f.purpose
LIMIT 20

-- After:
MATCH (f:FileNode) WHERE f.purpose CONTAINS $term
RETURN f.relative_path, f.purpose, f.importance, f.pagerank
ORDER BY f.importance DESC
LIMIT 20
```

Now the **first 3-5 results in any channel are almost always the files the agent actually needs**.

#### Step 5: Add a `getRepoHubs` Endpoint

A new MCP tool that returns the top-N files by PageRank for a given `knowledge_id`:

```cypher
MATCH (f:FileNode {knowledge_id: $kid})
RETURN f.relative_path, f.purpose, f.pagerank,
       f.classes, f.functions, f.imports_internal
ORDER BY f.pagerank DESC
LIMIT 10
```

This gives the agent a **"table of contents" of the most structurally important files in one call**. From any of these hub files, `imports_internal` already tells you what other files are reachable — so the agent can plan which files to fetch without additional searches.

#### Step 6: Cross-Repo PageRank

For multi-repo scenarios, extend this with **personalized PageRank**. If `OrgKeyword` nodes are shared across repos (same `org_id`), they act as bridges:

```
FileA (repo1) <--APPEARS_IN_FILE-- OrgKeyword("authentication") --APPEARS_IN_FILE--> FileB (repo2)
```

Project a bipartite graph of `FileNode` and `OrgKeyword` across all repos in the org, then run PageRank on that. Files that share many high-frequency keywords with files in other repos become **cross-repo hubs**.

### New FileNode Properties

| Property              | Type   | What it tells you                                            |
| --------------------- | ------ | ------------------------------------------------------------ |
| `pagerank`            | float  | Import-graph PageRank score (0-1). Higher = more imported.   |
| `semantic_centrality` | float  | Keyword connectivity score. Higher = more concepts linked.   |
| `importance`          | float  | Composite score (0.6 * pagerank + 0.4 * semantic_centrality) |

### MCP Client Decision Tree (with PageRank)

```
Starting a new exploration?
│
├─ Want the structural backbone of a repo?
│   → getRepoHubs → read top 5-10 hub files' imports_internal
│   → You now know the critical files AND what they connect to (1 call)
│
├─ Searching for a concept/feature?
│   → graph_search (results now sorted by importance)
│   → Top 3 results are hub files that match your query (1 call)
│   → getFileDetails on the top hit if you need full metadata (2 calls total)
│
└─ Exploring across multiple repos?
    → graph_search without knowledgeId (cross-repo, importance-sorted)
    → Cross-repo hub files surface first thanks to shared OrgKeyword PageRank
```

### Before vs After Comparison

| Metric                        | Before PageRank | After PageRank |
| ----------------------------- | --------------- | -------------- |
| Tool calls to find key files  | 8-12            | 2-4            |
| Agent restarts / dead ends    | Frequent        | Rare           |
| Cross-repo discovery          | Manual          | Automatic      |
| Result quality (first page)   | Noisy           | Hub-first      |
