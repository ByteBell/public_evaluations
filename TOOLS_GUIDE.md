# SWE-Pro Evaluation — Tools Guide

This guide explains the three Python tools used to **run**, **enrich**, and **inspect** evaluation sessions, and how they connect to the scoring workflow in `evaluation_guide_for_swe_pro.md`.

---

## Table of Contents

1. [Pipeline Overview](#pipeline-overview)
2. [claude_auditor_test.py — Eval Driver](#1-claude_auditor_testpy--eval-driver)
3. [src/enrich_answers.py — Metric Enrichment](#2-srcenrich_answerspy--metric-enrichment)
4. [src/visualize_session.py — Session Inspector](#3-srcvisualize_sessionpy--session-inspector)
5. [Full End-to-End Workflow](#4-full-end-to-end-workflow)
6. [Output Directory Structure](#5-output-directory-structure)
7. [Common Recipes](#6-common-recipes)
8. [Troubleshooting](#7-troubleshooting)

---

## Pipeline Overview

The evaluation pipeline has four phases. Each tool owns one or more phases. for running on swe_pro taks

```
┌─────────────────────────────────────────────────────────────────────┐
│  Phase 1 & 2 & 3  →  claude_auditor_test.py                        │
│                                                                     │
│  For each task:                                                     │
│    Launch Claude (or Kilo) → wait for exit → collect OTel files    │
│    Then: call enrich_answers.py internally → patch answer.json     │
│                                                                     │
│  Phase 4  →  score_prep.py  (see evaluation_guide_for_swe_pro.md)  │
│    Compute Dimension A, write score_input.json                     │
│                                                                     │
│  Phase 5  →  LLM judge                                             │
│    Score Dimensions B, C, D using score_input.json                 │
└─────────────────────────────────────────────────────────────────────┘

Supporting tools (run any time):
  src/enrich_answers.py    — re-enrich a run dir that is missing metrics
  src/visualize_session.py — inspect a single session's OTel event log
```

---

## 1. `claude_auditor_test.py` — Eval Driver

**What it does:** Reads tasks from a JSON task file, launches one `claude --print` subprocess per task (or `kilo run --auto` if using the Kilo backend), collects OpenTelemetry (OTel) session files, and calls `enrich_answers.py` to populate cost/token metrics. Supports parallel execution of up to 10 tasks at once.

### 1.1 Prerequisites

- `claude` CLI installed and on `$PATH`
- `ANTHROPIC_API_KEY` set in your environment (for Anthropic models)
- For OpenRouter: `OPENROUTER_API_KEY` set, or passed via `--openrouter-api-key`
- For Kilo backend: `kilo` CLI installed
- Task file present:
  - Astropy: `results_swe_bench/astropy_tasks.json`
  - SWE-Pro: `results_on_swe_pro/swe_pro_tasks.json`
- OTel receiver running (the script starts/stops it automatically for the `claude` backend)

### 1.2 Quick Start

```bash
# Simplest: first 3 astropy tasks, mcp_skills mode, claude-opus-4-6
python claude_auditor_test.py

# SWE-Pro, all tasks, MCP + skill docs, sonnet can be used in raw , mcp mode too
python claude_auditor_test.py \
  --task-set swe_pro \
  --run-mode mcp_skills \ 
  --slice : \
  --model claude-sonnet-4-6

# Label the run so it doesn't overwrite a previous one
python claude_auditor_test.py \
  --task-set swe_pro \
  --run-mode mcp_skills \
  --slice : \
  --run 2
# output dir → results_on_swe_pro/auto_run_on_swe_pro_mcp_skills_claude-sonnet-4-6_run_2/
```

### 1.3 CLI Reference

| Flag | Type | Default | Description |
|---|---|---|---|
| `--task-set` | choice | `astropy` | `astropy` or `swe_pro` |
| `--run-mode` | choice | `mcp_skills` | `raw`, `mcp`, or `mcp_skills` (see §1.5) |
| `--slice` | string | `:3` | Python slice of the task list, e.g. `:5`, `3:6`, `:` (all) |
| `--testids ID …` | list | — | Run only tasks whose `instance_id` ends with any of these values. Overrides `--slice`. |
| `--repo` | string | — | Filter tasks to a single repo slug before slicing, e.g. `internetarchive/openlibrary` |
| `--model` | string | `claude-opus-4-6` | Model slug. Anthropic: `claude-sonnet-4-6`. OpenRouter: `qwen/qwen3.6-plus:free` |
| `--cli-backend` | choice | `claude` | `claude` (OTel-tracked) or `kilo` (metrics from JSON stdout) |
| `--run` | string | — | Label appended to output dir, e.g. `2` → `..._run_2` |
| `--eval` | flag | off | Iterate through every entry in the `EVAL_MODELS` list |
| `--eval-parallel` | flag | off | Run Kilo-backend models concurrently during eval mode |
| `--eval-models` | int list | all | 0-based indices into `EVAL_MODELS`, e.g. `--eval-models 0 2` |
| `--openrouter-api-key` | string | env var | Override `OPENROUTER_API_KEY` on the command line |

### 1.4 Output Directory Name

The output directory is computed automatically from the active configuration:

```
results_on_swe_pro/auto_run_on_<task_set>_<run_mode>_<model>[_run_<label>]/
```

Examples:

```
results_on_swe_pro/auto_run_on_swe_pro_mcp_claude-sonnet-4-6/
results_on_swe_pro/auto_run_on_swe_pro_mcp_skills_claude-opus-4-6_run_2/
results_on_swe_pro/auto_run_on_swe_pro_raw_claude-sonnet-4-6_run_1/
results_swe_bench/auto_run_on_astropy_mcp_skills_claude-sonnet-4-6/
```

### 1.5 Run Modes

| Mode | Claude's working directory | MCP tools available | ByteBell skill docs injected |
|---|---|---|---|
| `raw` | Local git checkout of the repo at `base_commit` | No — MCP disabled via `--mcp-config` | No |
| `mcp` | Empty `mcp_workspace/` directory | Yes — full ByteBell graph | No |
| `mcp_skills` | Empty `mcp_workspace/` directory | Yes — full ByteBell graph | Yes — `.claude/skills/bytebell/*.md` appended to system prompt |

Use `raw` when you want Claude to read the actual source files. Use `mcp` or `mcp_skills` when the task requires the ByteBell knowledge graph (all SWE-Pro tasks).

### 1.6 How Parallel Execution Works

The auditor runs tasks in two sub-phases:

1. **Serial launch** — tasks are launched one at a time in a staggered loop. After each launch, the script polls for the OTel session UUID (up to `OTEL_SESSION_LOCK_WAIT = 20` seconds). This ensures each Claude process's telemetry is correctly attributed before the next task starts.

2. **Parallel finish** — all launched processes run concurrently inside a `ThreadPoolExecutor` with `PARALLEL_WORKERS = 10` threads. Each thread waits for its process to exit, streams stdout/stderr to disk, copies OTel files, and writes the manifest.

The result: you can run 10 tasks in the time it takes to run one, with no telemetry cross-contamination.

### 1.7 Eval Mode

Eval mode iterates through the `EVAL_MODELS` list at the top of the script. Claude-backend models always run sequentially (OTel session locking requires it). Kilo-backend models can run in parallel with `--eval-parallel`.

```bash
# Run all models in EVAL_MODELS
python claude_auditor_test.py --task-set swe_pro --eval

# Run only models at index 0 and 2 in EVAL_MODELS
python claude_auditor_test.py --task-set swe_pro --eval --eval-models 0 2

# Run Kilo models concurrently
python claude_auditor_test.py --task-set swe_pro --eval --eval-parallel
```

At the end of an eval run, a combined summary table is printed showing answer rate, enrichment rate, average time, total cost, and total tokens for every model.

### 1.8 Per-Task Output

For every task, the auditor creates this directory tree:

```
<run_dir>/<instance_id>/
├── answer.json          ← Claude's patch or explanation (JSON)
│                           After enrichment: also contains cost/token/timing fields
├── run_manifest.json    ← Metadata recorded at finish time
├── telemetry/
│   ├── <session-uuid>_events.json   ← OTel log records (API calls, tool calls, prompts)
│   └── <session-uuid>_metrics.json  ← OTel metric points (counters, gauges)
└── logs/
    ├── auditor.log         ← Structured DEBUG log for this task
    └── claude_stdout.txt   ← Live Claude transcript (stdout + stderr streamed to disk)
```

**`answer.json` before enrichment:**
```json
{
  "answer": "diff --git a/openlibrary/plugins/importapi/import_validator.py ..."
}
```

**`run_manifest.json`:**
```json
{
  "instance_id":    "instance_internetarchive__openlibrary-00bec1e7...",
  "base_commit":    "02f647f7d525286b6e3a661133c3772649e585cd",
  "cli_backend":    "claude",
  "model_provider": "anthropic",
  "model":          "claude-sonnet-4-6",
  "mode":           "print",
  "run_mode":       "mcp",
  "run_ts":         "2026-04-16T07:17:53.164630+00:00",
  "elapsed_s":      394.88,
  "cwd":            "/path/to/mcp_workspace",
  "answer_written": true,
  "otel_session_id": "1538040e-0bad-4d5b-b62c-4aaa2047ab6c",
  "otel_sessions":  { "1538040e-...": ["telemetry/..._events.json", "..."] },
  "cli_metrics":    {}
}
```

---

## 2. `src/enrich_answers.py` — Metric Enrichment

**What it does:** Reads OTel telemetry files (or Kilo stdout JSON) for every task in a run directory and writes cost, token counts, and timing directly into `answer.json`. The auditor calls this automatically at the end of a run — use it manually to re-enrich or to process a run produced by another tool.

### 2.1 Usage

```bash
# Enrich all tasks in a run directory
python src/enrich_answers.py results_on_swe_pro/auto_run_on_swe_pro_mcp_claude-sonnet-4-6

# Re-enrich after fixing missing telemetry
python src/enrich_answers.py results_on_swe_pro/auto_run_on_swe_pro_mcp_skills_claude-opus-4-6_run_2
```

The script iterates every subdirectory in the given run dir. It skips directories without `answer.json` and prints a final count.

```
  [OK  ] instance_internetarchive__openlibrary-00bec1e7...: enriched
  [OK  ] instance_internetarchive__openlibrary-111347e9...: enriched
  [FAIL] instance_internetarchive__openlibrary-25858f9f...: no telemetry dir

Done: 2 enriched / 3 processed

Tasks WITHOUT answer.json (1):
  - instance_internetarchive__openlibrary-4a5d2a7d...
```

### 2.2 What Gets Written Into `answer.json`

After enrichment, `answer.json` contains the original `"answer"` field plus all metric fields:

```json
{
  "answer": "diff --git a/openlibrary/plugins/importapi/import_validator.py ...",

  "time_taken_seconds":          394.88,
  "start_time":                  "2026-04-16T07:11:04.859Z",
  "end_time":                    "2026-04-16T07:17:30.596Z",

  "total_cost_usd":              0.71575,
  "total_input_tokens":          25,
  "total_output_tokens":         22088,
  "total_cache_read_tokens":     571473,
  "total_cache_creation_tokens": 56777,
  "total_api_requests":          17,
  "total_tool_calls":            23,
  "models_used":                 ["claude-sonnet-4-6"],

  "claude_sonnet_4_6_input_tokens":          25,
  "claude_sonnet_4_6_output_tokens":         22088,
  "claude_sonnet_4_6_cache_read_tokens":     571473,
  "claude_sonnet_4_6_cache_creation_tokens": 56777,
  "claude_sonnet_4_6_cost_usd":              0.71575,
  "claude_sonnet_4_6_api_requests":          17
}
```

The per-model keys use a safe name derived from the model slug: slashes and colons stripped, non-alphanumeric characters replaced with `_`.

### 2.3 Telemetry Source Priority

The script tries sources in this order for each task:

1. **OTel events file pinned to the session** — `telemetry/<session-uuid>_events.json` where `session-uuid` comes from `run_manifest.json → otel_session_id`. Most reliable.
2. **Latest OTel events file** — if no session ID, picks the most-recently modified `*_events.json` in `telemetry/`. Used as fallback.
3. **Kilo stdout** — parses `logs/claude_stdout.txt` as NDJSON `step_finish` events. Used when there are no OTel files (Kilo backend).

`time_taken_seconds` always reflects the greater of the OTel-derived duration and `elapsed_s` from `run_manifest.json`, because OTel only spans API calls — local tool operations after the last API call are invisible to it.

---

## 3. `src/visualize_session.py` — Session Inspector

**What it does:** Renders a colour-coded event timeline and session summary for a single OTel session. Use this to understand exactly what Claude did in a specific task: which API calls it made, which tools it called, what it cost, where it spent time.

### 3.1 Usage

```bash
# Basic: event timeline + summary
python src/visualize_session.py \
  results_on_swe_pro/auto_run_on_swe_pro_mcp_claude-sonnet-4-6/\
instance_internetarchive__openlibrary-00bec1e7.../\
telemetry/1538040e-0bad-4d5b-b62c-4aaa2047ab6c_events.json

# With companion metrics file
python src/visualize_session.py \
  telemetry/1538040e-..._events.json \
  telemetry/1538040e-..._metrics.json

# Verbose: prompt text, raw tool inputs, efficiency ratios,
#          cumulative charts, and raw metrics dump
python src/visualize_session.py <events_file> [metrics_file] --verbose
# -v also works
```

### 3.2 Event Timeline

Each OTel log record is rendered as one entry in sequence order. There are five event types:

| Event | Colour | Fields shown |
|---|---|---|
| `user_prompt` | Cyan | `prompt_length` (chars); `--verbose`: full prompt text |
| `api_request` | Green | Model, token counts (input/output/cache_read/cache_create), cost, duration, speed |
| `tool_decision` | Yellow | Tool name, decision (approved/denied), source (auto/user) |
| `tool_result` | Blue | Tool name, success/fail, result size, duration; tool input fields |
| `api_error` | Red | Model, error message, HTTP status code, duration |

Example output (standard mode):

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  EVENT TIMELINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[  1]  07:11:04.859  (  +0.000s)  user_prompt
      prompt_length : 3,204 chars

[  2]  07:11:07.120  (  +2.261s)  api_request
      model         : claude-sonnet-4-6
      tokens        : in=25  out=412  cache_read=0  cache_create=5,820
      cost / time   : $0.001820  dur=2.1s  speed=fast

[  3]  07:11:07.150  (  +2.291s)  tool_decision
      tool          : mcp__swebench-server__smart_search
      decision      : approved  (source: auto)

[  4]  07:11:07.900  (  +3.041s)  tool_result
      tool          : mcp__swebench-server__smart_search  ✓ success
      result_size   : 14.2 KB  dur=750ms
      mcp_tool      : smart_search
      query          : openlibrary import validator required fields
```

### 3.3 Session Summary

Printed at the end of the timeline:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SESSION SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Duration          : 386.7s
  API requests      : 17
  Tool calls        : 23
  Errors            : 0

  Token Usage
    input           : 25
    output          : 22,088
    cache read      : 571,473
    cache creation  : 56,777
    total cost      : $0.715750

  Models Used
    · claude-sonnet-4-6

  Tool Call Breakdown
    mcp__swebench-server__smart_search    8×  ████████
    mcp__swebench-server__retrieve_file   6×  ██████
    mcp__swebench-server__graph_search    5×  █████
    Write                                 2×  ██
    Read                                  2×  ██

  Total data received from tools : 1.24 MB

  Per-Request Cost Table
  Seq  Model                           In      Out   CacheR   CacheC       Cost       Dur
  ───────────────────────────────────────────────────────────────────────────────────────
    2  claude-sonnet-4-6               25      412        0    5,820  $0.00182    2.10s
    5  claude-sonnet-4-6                0      840   52,108    4,200  $0.02841    3.40s
   ...
```

### 3.4 Verbose Extras (`--verbose`)

In addition to the above, `--verbose` shows:

- **OTel internal metadata** per event: batch index, scope name, `timeUnixNano`, body, severity
- **Full prompt text** for `user_prompt` events
- **All tool input fields** (not truncated) for `tool_result` events
- **Efficiency ratios** per API call: cache hit %, output tokens/second, total context tokens
- **Cumulative output token chart** — bar graph showing how many tokens were output at each API call
- **Cumulative cache read chart** — shows the context window growing across turns
- **Cost per API request chart** — bar graph of cost at each turn
- **Raw metrics dump** — every OTel metric data point with name, type, value, aggregation, and timestamp

---

## 4. Full End-to-End Workflow

### Step 1 — Run the Auditor

```bash
python claude_auditor_test.py \
  --task-set swe_pro \
  --run-mode mcp_skills \
  --slice : \
  --model claude-sonnet-4-6 \
  --run 1
```

The script:
1. Starts the OTel receiver on port 4318
2. Loads all tasks from `results_on_swe_pro/swe_pro_tasks.json`
3. For each task (staggered launch, parallel finish):
   - Builds the system prompt and user prompt
   - Launches `claude --print --dangerously-skip-permissions` in `mcp_workspace/`
   - Locks the OTel session UUID to this task
   - Waits for Claude to exit, streams transcript to `logs/claude_stdout.txt`
   - Copies OTel files to `telemetry/`
   - Writes `run_manifest.json`
4. Enriches every `answer.json` with metrics
5. Prints a per-task summary table
6. Stops the OTel receiver

### Step 2 — (Optional) Re-Enrich

If telemetry was missing for some tasks (e.g. OTel receiver wasn't running, or a task timed out mid-way), you can re-run enrichment after fixing:

```bash
python src/enrich_answers.py \
  results_on_swe_pro/auto_run_on_swe_pro_mcp_skills_claude-sonnet-4-6_run_1
```

### Step 3 — (Optional) Inspect a Session

If a task's answer looks wrong or you want to understand the agent's behaviour:

```bash
python src/visualize_session.py \
  results_on_swe_pro/auto_run_on_swe_pro_mcp_skills_claude-sonnet-4-6_run_1/\
  <instance_id>/telemetry/<uuid>_events.json \
  <instance_id>/telemetry/<uuid>_metrics.json \
  --verbose
```

Look at:
- How many API calls were made and whether they grew the cache correctly
- Which MCP tools were called and in what order
- Whether any `api_error` events appear (rate limits, timeouts)
- Whether the final tool calls wrote `answer.json`

### Step 4 — Pre-Process for Scoring

```bash
python score_prep.py --all
```

This reads `results_on_swe_pro/swe_pro_tasks.json` (gold patches) and `sweap_eval_full_v2.jsonl` (Scale's official test signals) and writes `score_input.json` next to every `answer.json`. It also prints Dimension A (File Coverage) stats immediately — no LLM judge needed.

### Step 5 — Score Dimensions B, C, D

For each task where `score_input.json → is_prose_only == false`:

1. Open `score_input.json`
2. Use `fail_to_pass`, `test_functions`, `assert_samples`, `test_patch` → score **Dimension C**
3. Use `gold_patch` → score **Dimension B**
4. Use `assert_samples` and `test_functions` → score **Dimension D**
5. Read `score_A` directly (pre-computed)

Full rubric: see `evaluation_guide_for_swe_pro.md`.

### Step 6 — Aggregate

Collect A+B+C+D totals across all tasks and compute the metrics in `evaluation_guide_for_swe_pro.md §7`: `avg_score`, `full_patch_rate`, `partial_rate`, `zero_rate`, broken down by repo and run mode.

---

## 5. Output Directory Structure

```
results_on_swe_pro/
└── auto_run_on_swe_pro_mcp_skills_claude-sonnet-4-6_run_1/
    │
    ├── instance_internetarchive__openlibrary-<hash>/
    │   ├── answer.json           ← model answer + enriched metrics
    │   ├── run_manifest.json     ← run metadata (model, mode, elapsed, session ID)
    │   ├── score_input.json      ← written by score_prep.py (not the auditor)
    │   ├── telemetry/
    │   │   ├── <uuid>_events.json    ← OTel log records
    │   │   └── <uuid>_metrics.json   ← OTel metric data points
    │   └── logs/
    │       ├── auditor.log           ← DEBUG log for this task
    │       └── claude_stdout.txt     ← Claude's full terminal transcript
    │
    ├── instance_<repo>-<hash>/
    │   └── ...
    │
    └── ...
```

---

## 6. Common Recipes

### Run a single known task

```bash
python claude_auditor_test.py \
  --task-set swe_pro \
  --testids 00bec1e7 \
  --run-mode mcp_skills
```

`--testids` matches on the suffix of `instance_id`, so you only need to paste the short hash.

### Re-run a specific repo

```bash
python claude_auditor_test.py \
  --task-set swe_pro \
  --repo internetarchive/openlibrary \
  --run-mode mcp_skills \
  --run 3
```

### Compare two models on the same tasks

```bash
# Run 1: sonnet
python claude_auditor_test.py \
  --task-set swe_pro --slice :10 --model claude-sonnet-4-6 --run sonnet

# Run 2: opus
python claude_auditor_test.py \
  --task-set swe_pro --slice :10 --model claude-opus-4-6 --run opus
```

Or use eval mode which does both and prints a combined table:

```bash
python claude_auditor_test.py --task-set swe_pro --slice :10 --eval --eval-models 0 1
```

### Inspect the most recent session for a task

```bash
TASK_DIR="results_on_swe_pro/auto_run_on_swe_pro_mcp_claude-sonnet-4-6/instance_internetarchive__openlibrary-00bec1e7c8f3272c469a58e1377df03f955ed478-v13642507b4fc1f8d234172bf8129942da2c2ca26"

python src/visualize_session.py \
  "$TASK_DIR/telemetry/$(ls -t "$TASK_DIR/telemetry/" | grep events | head -1)" \
  --verbose
```

### Check answer rate without scoring

```bash
# Count tasks that wrote an answer vs total
find results_on_swe_pro/auto_run_on_swe_pro_mcp_skills_claude-sonnet-4-6_run_1 \
  -name answer.json | wc -l

# Check which tasks are missing answer.json
python src/enrich_answers.py \
  results_on_swe_pro/auto_run_on_swe_pro_mcp_skills_claude-sonnet-4-6_run_1 \
  2>&1 | grep "WITHOUT"
```

---

## 7. Troubleshooting

### `answer.json` not created

1. Check `logs/claude_stdout.txt` — look for the model's response. If the answer is printed to stdout rather than written to the file, it means Claude ignored the system prompt instruction. This can happen on models that don't follow instructions well.
2. For Kilo backend: the auditor automatically tries to recover a JSON answer from stdout text events. Check `logs/claude_stdout.txt` for a `{"answer": "..."}` block.
3. Check `logs/auditor.log` for `answer.json NOT created` warnings.

### No OTel telemetry files

1. Check that the OTel receiver started: the auditor logs `OTel receiver started — PID=…, listening on :4318`.
2. If port 4318 was in use by another process, the auditor kills it before starting — check for `Port 4318 already in use — killing existing process` in the log.
3. If `OTEL_SESSION_LOCK_WAIT` (20 s) timed out, session UUID won't be pinned and `collect_new_session_files` falls back to a snapshot diff. This can cause telemetry to be attributed to the wrong task in a parallel run.
4. OTel requires `CLAUDE_CODE_ENABLE_TELEMETRY=1` — this is injected automatically into every subprocess via `OTEL_ENV`.

### Enrichment fails: `telemetry parse error`

The events file may be truncated (Claude was killed mid-flush). Try:
```bash
python -c "import json; json.load(open('path/to/events.json'))"
```
If it fails, the file is incomplete. The raw transcript in `logs/claude_stdout.txt` still has the answer; only the metrics will be missing.

### `No tasks matched — check --testids or TASK_SLICE`

- For `--testids`: the value must match a suffix of `instance_id`. Use the short hash (8+ chars), not the full ID.
- For `--slice`: Python slice syntax — `:3` means indices 0,1,2. `3:` means index 3 onward.
- For `--repo`: must be an exact match to the `repo` field in the task JSON, e.g. `internetarchive/openlibrary` (lowercase, with slash).

### Score is 0 for all dimensions

Check `score_input.json → is_prose_only`. If `true`, Claude wrote a description instead of a patch. Look at `logs/claude_stdout.txt` — common causes:
- Context overflow on a very long task
- Model ignored the output format instruction
- `answer.json` was not created so `score_prep.py` treated the model answer as empty
