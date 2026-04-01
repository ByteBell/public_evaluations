# visualize_session.py

Terminal visualizer for verifying Claude Code evaluation results. Each task in `results_swe_bench/` contains raw OpenTelemetry logs alongside the `answer.json` — this script renders those logs into a human-readable timeline so you can independently verify the token counts, costs, and timing reported in the evaluation `.md` files.

## Prerequisites

- Python 3.8+
- No external dependencies (stdlib only)

## Usage

```
python3 src/visualize_session.py <events_file> [metrics_file] [-v]
```

| Argument | Required | Description |
|----------|----------|-------------|
| `events_file` | Yes | Path to the `*_events.json` log inside a task result directory |
| `metrics_file` | No | Path to the matching `*_metrics.json` in the same directory |
| `-v` / `--verbose` | No | Show full detail: all attributes, prompt text, tool I/O, raw metrics, cumulative charts |

## Where the Logs Live

Every evaluated task directory contains three files:

```
results_swe_bench/<run>/<instance_id>/
  ├── answer.json                          # model answer + aggregated metrics
  ├── <session-uuid>_events.json           # raw OTel event log (every API call, tool use, prompt)
  └── <session-uuid>_metrics.json          # raw OTel metric counters (token totals, cost)
```

**Raw v3 example:**
```
results_swe_bench/claude-opus-4.6-v3-raw/astropy__astropy-7166/
  ├── answer.json
  ├── af3b6561-37ce-4f4d-a39f-675ee2239fcd_events.json
  └── af3b6561-37ce-4f4d-a39f-675ee2239fcd_metrics.json
```

**MCP v2 example:**
```
results_swe_bench/claude_opus_4.6_mcp_v2/astropy__astropy-7606/
  ├── answer.json
  ├── bf792fbc-09a9-4c68-a9e3-b918b9d47b70_events.json
  └── bf792fbc-09a9-4c68-a9e3-b918b9d47b70_metrics.json
```

## Examples

**Verify a Raw v3 task:**
```bash
python3 src/visualize_session.py \
  results_swe_bench/claude-opus-4.6-v3-raw/astropy__astropy-7166/af3b6561-37ce-4f4d-a39f-675ee2239fcd_events.json \
  results_swe_bench/claude-opus-4.6-v3-raw/astropy__astropy-7166/af3b6561-37ce-4f4d-a39f-675ee2239fcd_metrics.json
```

**Verify an MCP v2 task with full detail:**
```bash
python3 src/visualize_session.py \
  results_swe_bench/claude_opus_4.6_mcp_v2/astropy__astropy-7606/bf792fbc-09a9-4c68-a9e3-b918b9d47b70_events.json \
  results_swe_bench/claude_opus_4.6_mcp_v2/astropy__astropy-7606/bf792fbc-09a9-4c68-a9e3-b918b9d47b70_metrics.json \
  -v
```

**Events only (skip metrics):**
```bash
python3 src/visualize_session.py \
  results_swe_bench/claude-opus-4.6-v3-raw/astropy__astropy-12907/*_events.json
```

## What to Verify

The `answer.json` in each task directory reports aggregated metrics:

```json
{
  "time_taken_seconds": 151.308,
  "total_cost_usd": 0.39267,
  "total_input_tokens": 4320,
  "total_output_tokens": 7370,
  "total_cache_read_tokens": 484355,
  "total_cache_creation_tokens": 55079,
  "total_api_requests": 20,
  "total_tool_calls": 20
}
```

Running `visualize_session.py` on the corresponding `_events.json` and `_metrics.json` independently recomputes these values from the raw OTel records. The **Session Summary** and **Per-Request Cost Table** let you confirm that every number in `answer.json` — and by extension every number in the evaluation reports — traces back to individual, timestamped API calls.

## Output Sections

### Default mode

| Section | What it shows |
|---------|---------------|
| **Event Timeline** | Every event in order — `user_prompt`, `api_request`, `tool_decision`, `tool_result`, `api_error` — with timestamps and key attributes |
| **Session Summary** | Duration, API request count, tool call count, error count |
| **Token Usage** | Input, output, cache read, cache creation totals + total cost |
| **Models Used** | Model IDs invoked during the session |
| **Tool Call Breakdown** | Histogram of tool usage by name |
| **Per-Request Cost Table** | Every API request: model, tokens (in/out/cache read/cache create), cost, duration |

### Verbose mode (`-v`) adds

| Section | What it shows |
|---------|---------------|
| **OTel metadata** | Batch index, scope, timeUnixNano per event |
| **Full prompt text** | Complete user prompt content |
| **Tool inputs** | Raw tool parameters and input payloads |
| **Efficiency ratios** | Cache hit %, output tok/s, total context per request |
| **Cumulative Output Tokens chart** | Bar chart of output tokens per request with running total |
| **Cumulative Cache Read chart** | Bar chart showing context window growth |
| **Cost per Request chart** | Bar chart of cost distribution with running total |
| **Raw Metrics Dump** | All OTel metric data points |

## Event Types

| Event | Color | Description |
|-------|-------|-------------|
| `user_prompt` | Cyan | User input with prompt length |
| `api_request` | Green | API call with model, tokens, cost, duration |
| `tool_decision` | Yellow | Tool selection with decision source |
| `tool_result` | Blue | Tool execution with success/failure, size, duration |
| `api_error` | Red | API error with status code |

## File Format

Supports `.json` (single object or array) and `.jsonl` (one JSON per line). Both follow the [OpenTelemetry Logs Data Model](https://opentelemetry.io/docs/specs/otel/logs/data-model/).
