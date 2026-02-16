# ByteBell SWE-bench Pro MCP Benchmark Runner

Automated benchmark runner that sends SWE-bench Pro questions to an LLM (via OpenRouter), which uses MCP tools (ByteBell knowledge graph) to search codebases and produce exhaustive code-architecture answers.

Pure Python — no LangChain, no mcp_use. Direct HTTP calls to OpenRouter and the MCP server.

## Setup

### 1. Create a virtual environment

```bash
python3 -m venv .
source bin/activate
```

### 2. Install dependencies

```bash
pip install requests python-dotenv
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL_NAME=deepseek/deepseek-chat-v3.1
```

### 4. Configure MCP server

Edit `mcp_config.json` to point to your ByteBell MCP server:

```json
{
  "mcpServers": {
    "bytebell": {
      "url": "http://your-server:3100/mcp?access_token=your_token"
    }
  }
}
```

## Questions Format

JSON array where each item has `id`, `question`, `answer` (expected), and `files` (expected):

```json
[
  {
    "id": 1,
    "question": "Which files enforce per-user coupon limits?",
    "answer": "Expected answer text...",
    "files": [
      {
        "repo": "omni-store-rag",
        "path": "path/to/File.java",
        "why": "Reason this file is relevant"
      }
    ]
  }
]
```

## Usage

```bash
# Basic run
python src/evals.py \
    --questions sample_questions.json \
    --mcp-config mcp_config.json

# With specific model and verbose output
python src/evals.py \
    -q sample_questions.json \
    -m mcp_config.json \
    --model openai/gpt-4o \
    --verbose

# Run a slice (questions 0-4 only)
python src/evals.py \
    -q sample_questions.json \
    -m mcp_config.json \
    --start 0 --end 5

# Custom max steps and timeout
python src/evals.py \
    -q sample_questions.json \
    -m mcp_config.json \
    --max-steps 50 --timeout 600
```

### CLI Arguments

| Argument | Short | Default | Description |
|----------|-------|---------|-------------|
| `--questions` | `-q` | *(required)* | Path to questions JSON file |
| `--mcp-config` | `-m` | *(required)* | Path to MCP server config JSON |
| `--output` | `-o` | `benchmark_results.json` | Path to save aggregate results |
| `--data-dir` | `-d` | `results/` | Directory for per-question output |
| `--model` | | from `.env` | OpenRouter model ID |
| `--api-key` | | from `.env` | OpenRouter API key |
| `--max-steps` | | `40` | Max agent loop iterations per question |
| `--timeout` | | `300` | Timeout in seconds per question |
| `--delay` | | `1.0` | Delay between questions (seconds) |
| `--start` | | `0` | Start index in questions array |
| `--end` | | end of array | End index in questions array |
| `--verbose` | `-v` | `false` | Show detailed agent steps |

## Output

Each question produces three files in `results/<question_id>/`:

| File | Contents |
|------|----------|
| `answer.md` | The LLM's full markdown answer with a `## Relevant Files` table |
| `tool_calls.json` | Raw log of every MCP tool call (name, arguments, result preview) |
| `result.json` | Metadata: status, latency, token usage, cost, expected answer/files |

An aggregate `benchmark_results.json` is also saved with all results and a summary.

## How It Works

1. Connects to the ByteBell MCP server over StreamableHTTP
2. Fetches available MCP tools (`server_info`, `list_knowledge`, `graph_search`, `graph_traverse`, `retrieve_file`)
3. For each question, runs an agent loop:
   - LLM receives the question + MCP tools in OpenAI function-calling format
   - LLM calls tools to search across repos (DB, backend, frontend, config layers)
   - Tool calls execute in parallel via `ThreadPoolExecutor`
   - Null values in tool arguments are stripped (LLMs send explicit nulls; MCP Zod validation rejects them)
   - Loop continues until the LLM produces a final answer or hits `--max-steps`
4. Results are saved incrementally after each question
