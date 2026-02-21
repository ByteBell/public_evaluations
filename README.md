# ByteBell Cross-Repository Impact Analysis Benchmark

No existing benchmark tests whether an LLM + MCP tool can trace the ripple effects of a breaking code change across multiple repositories. We built our own.

We assembled **82,894 source files** across **25 Kubernetes and observability repositories**, wrote **100 cross-repo impact questions**, and ran them against **8 LLMs** via the ByteBell MCP knowledge graph — consuming **646 million tokens** (~$94 USD total).

## Setup

```bash
python3 -m venv .
source bin/activate
pip install requests python-dotenv psutil
```

Create `.env` with your OpenRouter API key:

```
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

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

Edit `models.json` to configure which models to evaluate and their pricing.

---

## Datasets

### KubeCluster40 — 40 Cross-Repository Impact Questions

The primary dataset lives in `results/KubeCluster40/` and contains **40 questions** across two categories:

| Prefix | Count | Description |
|--------|:-----:|-------------|
| **OBS** | 30 | Observability — interface/function changes in Prometheus, OpenTelemetry Collector, Thanos, Grafana, Jaeger, Loki, Mimir, and Tempo that ripple across the observability stack |
| **MIXED** | 10 | Mixed infrastructure — breaking changes to shared Kubernetes interfaces (e.g. `SharedInformer`, `Querier`) that affect both infrastructure tools and observability platforms |

Each question asks: *"If you add/modify method X on interface Y in repo Z, which files across repos A, B, C, D would need to implement or adapt to this change?"*

### Per-Question Folder Structure

Each `question_<ID>/` folder contains:

```
question_MIXED_TC001/
  question.json                       # The question text
  anthropic_claude-haiku-4.5.json     # Claude Haiku's answer + tool calls + cost
  deepseek_deepseek-chat-v3.1.json    # DeepSeek's answer
  google_gemini-3-flash-preview.json  # Gemini Flash's answer
  openai_gpt-5.1-codex-max.json      # GPT-5.1 Codex Max's answer
  openai_gpt-5.1-codex-mini.json     # GPT-5.1 Codex Mini's answer
  x-ai_grok-code-fast-1.json         # Grok Code's answer
  xiaomi_mimo-v2-flash.json           # MiMo's answer
  claude_opus_aicopilot.json          # Claude Opus (via AICopilot) answer
  evaluation.json                     # Model metadata + relevance scores
  analysis.json                       # LLM judge comparative scores
```

### Model Answer Files

Each `<model>.json` contains the full result of running that model against the question via the ByteBell MCP knowledge graph:

```json
{
  "model": "openai/gpt-5.1-codex-max",
  "answer": "## Architecture Overview\n...",
  "llm_condensed_answer": "SUMMARY: ...\nFILES:\n- repo/path — reason\n...",
  "cost": {
    "input_tokens": 983242,
    "output_tokens": 8207,
    "total_tokens": 991449,
    "cost_usd": 1.311123
  },
  "status": "success",
  "latency_seconds": 137.96,
  "tool_calls_count": 24,
  "agent_steps": 25,
  "tool_calls": [...]
}
```

- `answer` — the model's full verbose response (often 3000-6000 tokens)
- `llm_condensed_answer` — a structured summary extracted by a cheap model (see below)
- `cost` — token counts and USD cost for this single question

### Answer Condensation

Raw model answers are verbose — tables, architecture overviews, detailed explanations. Before sending answers to the LLM judge, each answer is **condensed** using the `smoke_test_model` (currently `xiaomi/mimo-v2-flash`, the cheapest model at $0.09/M input) into a structured format:

```
SUMMARY: The change to SharedInformer affects 4 repos. ArgoCD and cert-manager
have custom informer factories that implement the interface directly...

FILES:
- argo-cd/pkg/client/informers/externalversions/factory.go — implements SharedInformerFactory
- cert-manager/internal/informers/core_filteredsecrets.go — dual-cache wrapper implements SharedInformer
- cert-manager/pkg/client/informers/externalversions/factory.go — generated informer factory
- opentelemetry-operator/main.go — uses controller-runtime which wraps SharedInformer
...
```

This condensation happens in two places:
1. **At generation time** (`mcp_context_generation.py`) — stored as `llm_condensed_answer` in each model result file
2. **At evaluation time** (`evaluate.py`) — backfills any missing condensations before sending to the judge

### Scoring Criteria

The LLM judge (`judge_model` in `models.json`, currently `google/gemini-3.1-pro-preview`) scores each model using a **60/30/10** weighted criteria:

| Weight | Criteria | What It Measures |
|:------:|----------|------------------|
| **60%** | File Accuracy | Did the model identify the correct affected repositories and files? Are the listed files actually relevant to the interface change? |
| **30%** | Reasoning Quality | Did the model explain *why* each file is affected — interface implementation, dependency chain, data flow? Did it describe what specifically needs to change? |
| **10%** | Precision Penalty | Did the model list clearly irrelevant files (hallucination)? Models that pad answers with irrelevant files score lower. |

Each model is scored **independently** as a percentage accuracy (0-100%). Scores are not normalized across models — multiple models can receive the same score.

### Analysis Output

After evaluation, `analysis_summary.json` contains the final leaderboard with accuracy vs. cost:

```
Model                                         |   Avg % |     Cost $ |      %/$ | Judged
----------------------------------------------+---------+------------+----------+-------
openai/gpt-5.1-codex-max                      |   78.8% | $  43.7883 |     1.80 |     40
anthropic/claude-haiku-4.5                    |   77.2% | $  17.2828 |     4.47 |     16
google/gemini-3-flash-preview                 |   72.1% | $  12.4790 |     5.78 |     40
deepseek/deepseek-chat-v3.1                   |   63.1% | $   3.0286 |    20.84 |     40
x-ai/grok-code-fast-1                         |   48.5% | $   5.4157 |     8.96 |     40
claude-opus-4.6/aicopilot                       |   44.8% | $   0.0000 |     0.00 |     40
openai/gpt-5.1-codex-mini                     |   44.1% | $   9.6812 |     4.56 |     40
xiaomi/mimo-v2-flash                          |   43.6% | $   3.8807 |    11.24 |     40
```

Key metrics per model:
- **Avg %** — mean independent accuracy percentage across all judged questions (higher = better)
- **Cost $** — total USD spent across all questions (input + output tokens)
- **%/$** — accuracy percentage per dollar spent (higher = more accuracy per dollar)
- **Judged** — number of questions where the model produced a scoreable answer

### Evaluation Pipeline

```
question.json ──► mcp_context_generation.py ──► <model>.json (full answer + condensed)
                                                        │
                                                        ▼
                                               evaluate.py --force
                                                        │
                                         ┌──────────────┼──────────────┐
                                         ▼              ▼              ▼
                                  evaluation.json  analysis.json  analysis_summary.json
                                  (model metadata  (judge scores  (leaderboard with
                                   + relevance)     per question)  cost vs accuracy)
```

---

## Scripts

### `src/download_dataset.py` — Dataset Downloader

Downloads all 25 Kubernetes and observability repositories that make up the benchmark dataset into `dataset/Kubecluster/`.

Each repository is shallow-cloned (`--depth 1`) to minimize disk usage. Repos that already exist locally are skipped, so the script is safe to re-run — it will only fetch what's missing. On failure, it reports which repos could not be cloned and exits with code 1.

The 25 repositories:

| Repository | GitHub |
|------------|--------|
| argo-cd | argoproj/argo-cd |
| autoscaler | kubernetes/autoscaler |
| cert-manager | cert-manager/cert-manager |
| cilium | cilium/cilium |
| crossplane | crossplane/crossplane |
| external-dns | kubernetes-sigs/external-dns |
| external-secrets | external-secrets/external-secrets |
| flux2 | fluxcd/flux2 |
| gatekeeper | open-policy-agent/gatekeeper |
| grafana | grafana/grafana |
| helm | helm/helm |
| ingress-nginx | kubernetes/ingress-nginx |
| istio | istio/istio |
| jaeger | jaegertracing/jaeger |
| karpenter | aws/karpenter-provider-aws |
| kubernetes | kubernetes/kubernetes |
| kustomize | kubernetes-sigs/kustomize |
| loki | grafana/loki |
| mimir | grafana/mimir |
| opentelemetry-collector | open-telemetry/opentelemetry-collector |
| opentelemetry-collector-contrib | open-telemetry/opentelemetry-collector-contrib |
| opentelemetry-operator | open-telemetry/opentelemetry-operator |
| prometheus | prometheus/prometheus |
| tempo | grafana/tempo |
| thanos | thanos-io/thanos |

```bash
python3 src/download_dataset.py
```

No arguments. Clones everything into `dataset/Kubecluster/`.

---

### `src/mcp_stress.py` — MCP Server Stress Test

Pure MCP stress test (no LLM involved). Hammers the `graph_search` tool with concurrent threads to find the maximum concurrency the server can handle within a given RAM budget.

**How it works:**

The test runs in two phases:

1. **Phase 1 — Discovery:** Starts at 5 threads and increases by 5 each round (10-second probe per round). Each thread repeatedly calls `graph_search` on the MCP server. A background `ServerMonitor` thread samples the server process's CPU% and RSS memory every second using `psutil`. If the server's RSS exceeds `--server-mem-limit` or any call errors out, discovery stops and the last safe thread count is recorded.

2. **Phase 2 — Stability Soak:** Runs the maximum safe thread count for 30 seconds of sustained load to confirm the server stays healthy under continuous pressure. Reports per-thread latency breakdown (avg, min, max, p50, p99) and server resource usage (CPU cores, peak RSS, samples).

The monitor finds the MCP server process by looking up which PID is listening on the MCP port via `lsof`.

```bash
python3 src/mcp_stress.py \
    --mcp-config mcp_config.json \
    --server-mem-limit 4000 \
    --max-duration 300
```

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--mcp-config` | `-m` | **required** | Path to MCP config JSON file |
| `--server-mem-limit` | | `4000` | Max server RSS in MB |
| `--start-threads` | | `5` | Initial thread count |
| `--thread-step` | | `5` | Threads to add each discovery round |
| `--probe-duration` | | `10` | Seconds per discovery probe round |
| `--soak-duration` | | `30` | Seconds for stability soak phase |
| `--query` | | `SharedInformer` | Search query string |
| `--channels` | | `classes imports` | Search channels |
| `--timeout` | | `30` | Read timeout per MCP call in seconds |
| `--sample-interval` | | `1.0` | Server monitor sample interval in seconds |
| `--max-duration` | | `300` | Hard time limit for the entire test |

---

### `src/smoke_test.py` — LLM + MCP Smoke Test

End-to-end smoke test that auto-discovers the maximum concurrent thread count the LLM can handle, then answers ALL questions at that concurrency while monitoring server memory.

**How it works:**

1. **Phase 1 — Discovery:** Starts at 3 threads, bumps +1 each round. Each thread picks a random question from the provided file, sends it through the full LLM agent loop (LLM calls MCP tools to search the codebase, gets results, formulates an answer). If any thread errors (LLM timeout, refusal, crash), discovery stops and the last clean thread count is recorded.

2. **Phase 2 — Answer All:** Takes every question from the file, shuffles them, and batches them through the max safe thread count. Each batch runs in parallel. Progress is logged per-batch. Stops if the server memory limit is breached or errors appear.

Outputs a timestamped JSON file with full results including per-thread latency, tokens, cost, and server resource usage.

```bash
python3 src/smoke_test.py \
    --questions cross_repo_whole.json \
    --mcp-config mcp_config.json

# With a time cap:
python3 src/smoke_test.py \
    --questions cross_repo_whole.json \
    --mcp-config mcp_config.json \
    --max-duration 300
```

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--questions` | `-q` | **required** | Path to questions JSON file |
| `--mcp-config` | `-m` | **required** | Path to MCP config JSON file |
| `--start-threads` | | `3` | Initial thread count for discovery |
| `--thread-step` | | `1` | Threads to add each round |
| `--max-duration` | | unlimited | Hard time limit in seconds |
| `--model` | | from `models.json` | OpenRouter model name |
| `--api-key` | | env | OpenRouter API key |
| `--max-steps` | | `25` | Max agent steps per question |
| `--timeout` | | `120` | Read timeout per MCP call in seconds |
| `--server-mem-limit` | | `4000` | Max server RSS in MB (stops test if exceeded) |
| `--seed` | | none | Random seed for reproducibility |

---

### `src/evals.py` — Single-Model Benchmark Runner

Core infrastructure. Provides the `MCPClient`, `LLMClient`, and `run_agent` loop used by all other scripts. Also works standalone to run questions from a JSON file against a single model via MCP.

The agent loop sends a detailed system prompt instructing the LLM to plan, discover files across repos using MCP tools (server_info, list_knowledge, graph_search, retrieve_file), follow dependency chains, and produce a structured Markdown answer with an architecture overview, detailed analysis, and a table of all relevant files. Tool calls within a single step execute in parallel.

```bash
python3 src/evals.py \
    --questions cross_repo_whole.json \
    --mcp-config mcp_config.json \
    --model deepseek/deepseek-chat-v3.1
```

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--questions` | `-q` | **required** | Path to questions JSON file |
| `--mcp-config` | `-m` | **required** | Path to MCP config JSON file |
| `--output-dir` | `-o` | `results` | Output directory for results |
| `--data-dir` | `-d` | `results` | Directory for per-question result files |
| `--model` | | `deepseek/deepseek-chat-v3.1` | OpenRouter model name |
| `--api-key` | | env | OpenRouter API key |
| `--max-steps` | | `40` | Max agent steps per question |
| `--timeout` | | `300` | Read timeout per MCP call in seconds |
| `--delay` | | `1.0` | Delay between questions in seconds |
| `--start` | | `0` | Start index (slice questions) |
| `--end` | | all | End index (slice questions) |
| `--verbose` | `-v` | off | Enable verbose logging |

---

### `src/mcp_context_generation.py` — MCP Context Generation

Reads questions from a folder of `question_*/question.json` files and runs them against every model in `models.json` in parallel (one thread pool per model). Results are saved back into the same question folders. Cached successful answers are skipped on re-runs — only failed/blank ones are retried. Stops immediately on 402 payment errors.

After all models finish, prints a comparison table with success count, errors, average latency, tokens, cost, and wall-clock time per model.

```bash
python3 src/mcp_context_generation.py \
    --questions-dir results/KubeCluster40 \
    --mcp-config mcp_config.json \
    --threads 3

# Only run specific models:
python3 src/mcp_context_generation.py \
    --questions-dir results/KubeCluster40 \
    --mcp-config mcp_config.json \
    --models "xiaomi/mimo-v2-flash" "deepseek/deepseek-chat-v3.1"
```

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--questions-dir` | `-q` | **required** | Path to folder containing `question_*/question.json` files |
| `--mcp-config` | `-m` | **required** | Path to MCP config JSON file |
| `--models` | | all from `models.json` | Specific model(s) to run |
| `--threads` | `-t` | `3` | Concurrent threads per model |
| `--max-steps` | | `25` | Max agent steps per question |
| `--timeout` | | `120` | Read timeout per MCP call in seconds |
| `--api-key` | | env | OpenRouter API key |
| `--num-questions` | `-n` | all | Number of questions to run |
| `--seed` | | none | Random seed for reproducibility |

---

### `src/evaluate.py` — Answer Evaluator

Evaluates LLM answers by checking whether the file paths mentioned in each answer physically exist in `dataset/Kubecluster/`. For each question folder in the given results directory, it reads every model answer file, extracts file paths from markdown tables and inline backtick references, resolves repo names (handling aliases like "argocd" -> "argo-cd"), and checks the filesystem.

Computes two scores per model answer:

- **relevance_score** (0-10, higher = better): Combines file accuracy (fraction of mentioned files that exist), answer substance (length/structure), and file coverage (number of real files found).
- **hallucination_score** (0-10, higher = worse): Fraction of mentioned file paths that don't physically exist in the dataset.

**Outputs per question folder:**

- `evaluation.json` — file-existence scores per model
- `analysis.json` — LLM judge comparison: semantic relevance score (1-10) with justification per model (requires `OPENROUTER_API_KEY`)

**Aggregated output:**

- `analysis_summary.json` — written to the results directory root, contains a per-model summary table (avg LLM judge score, questions judged) and per-question breakdown with every model's score and justification. The judge model is configured via `judge_model` in `models.json`.

```bash
python3 src/evaluate.py --results-dir results

# Or for a specific subfolder:
python3 src/evaluate.py --results-dir results/KubeCluster40
```

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--results-dir` | `-r` | **required** | Path to results folder containing `question_*/` subfolders |

---

### `src/aggregate_metrics.py` — Aggregate Metrics

Aggregates per-model scores from all `evaluation.json` and `analysis.json` files into a single `metrics.json`. Reports average relevance, average hallucination, average LLM judge score, file accuracy percentage, questions answered, and questions errored per model, sorted by LLM judge score descending.

```bash
python3 src/aggregate_metrics.py --results-dir results

# Or for a specific subfolder:
python3 src/aggregate_metrics.py --results-dir results/KubeCluster40
```

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--results-dir` | `-r` | **required** | Path to results folder containing `question_*/` subfolders |

---

### `src/count_errors.py` — Error Counter

Counts errored or blank answer files per model across all results.

```bash
python3 src/count_errors.py
```

---

### `src/error_analysis.py` — Error Type Breakdown

Classifies and counts error types (402 Payment Required, 429 Rate Limited, Timeout, 5xx Server Error, blank answers, etc.) across all failed answer files, with per-model breakdown.

```bash
python3 src/error_analysis.py
```

---

### `src/replace_questions.py` — Question Updater

One-time script that replaces CRW_TC042-TC071 in `cross_repo_whole.json` with 30 new observability cross-repo questions (OBS_TC001-OBS_TC030) covering Prometheus, OpenTelemetry Collector, Thanos, Grafana, Jaeger, Loki, Mimir, and Tempo.

```bash
python3 src/replace_questions.py
```

---

## Output Structure

Questions live in folders like `results/KubeCluster40/` with per-question subfolders. Model results are saved back into the same folders:

```
results/KubeCluster40/
  question_MIXED_TC001/
    question.json                    # The question + expected answer + expected files
    xiaomi_mimo-v2-flash.json        # Model answer + tool calls + cost
    deepseek_deepseek-chat-v3.1.json # Another model's answer
    openai_gpt-oss-120b.json         # One file per model in models.json
    ...
    evaluation.json                  # File-existence scores per model
    analysis.json                    # LLM-based relevance comparison per model
  question_MIXED_TC002/
    question.json
    xiaomi_mimo-v2-flash.json
    deepseek_deepseek-chat-v3.1.json
    ...
    evaluation.json
    analysis.json
  ...
  20250601_120000-mcp_context_generation.json  # Timestamped run summary
  metrics.json                                 # Aggregate scores (after running aggregate_metrics.py)
```

### Per-Question Folder Contents

Each `question_<ID>/` folder contains:

| File | Description |
| ---- | ----------- |
| `question.json` | The question text, expected answer, expected files, and source repo |
| `<model>.json` | One per model — the model's answer, tool calls, token usage, cost, latency, and status |
| `evaluation.json` | File-existence check results: relevance score (0-10), hallucination score (0-10), found/missing files per model |
| `analysis.json` | LLM judge comparison: semantic relevance score (1-10) with justification per model |

### `question.json` Format

```json
{
  "id": "SA_TC001",
  "question": "If the ServiceAccount struct in kubernetes/...",
  "expected_answer": "The change affects...",
  "expected_files": [
    {"repo": "istio", "files": ["pilot/pkg/..."], "reason": "..."}
  ],
  "repo": "kubernetes"
}
```

### Model Answer File Format (e.g. `deepseek_deepseek-chat-v3.1.json`)

```json
{
  "model": "deepseek/deepseek-chat-v3.1",
  "answer": "## Architecture Overview\n...",
  "cost": {
    "input_tokens": 45000,
    "output_tokens": 3200,
    "total_tokens": 48200,
    "cost_usd": 0.0141
  },
  "status": "success",
  "latency_seconds": 42.5,
  "tool_calls_count": 12,
  "agent_steps": 8,
  "tool_calls": [...]
}
```

### `analysis.json` Format

For each question, `analysis.json` contains an LLM-generated comparison of each model's answer against the expected answer:

```json
{
  "question_id": "SA_TC001",
  "question": "...",
  "expected_answer": "...",
  "model_analyses": [
    {
      "model": "deepseek/deepseek-chat-v3.1",
      "relevance": 8,
      "justification": "The answer correctly identifies 6 of 7 expected files..."
    }
  ]
}
```

### Evaluation Workflow

```text
1. Run mcp_context_generation.py -q results/KubeCluster40  →  question_*/<model>.json
2. Run evaluate.py -r results/KubeCluster40                →  question_*/evaluation.json + analysis.json
3. Run aggregate_metrics.py -r results/KubeCluster40       →  metrics.json
```

## Test Case Categories

100 test cases in `cross_repo_whole.json`:

| Prefix | Count | Description |
|--------|:-----:|-------------|
| **CRW** | 41 | Cross-Repo Wide — struct/interface/function changes in core Kubernetes that break downstream consumers |
| **OBS** | 30 | Observability — cross-repo impact across Prometheus, Thanos, Mimir, Loki, Tempo, Jaeger, Grafana, and OTel Collector |
| **KM** | 14 | Kubernetes Modification — struct/interface changes in Kubernetes core packages |
| **SA** | 13 | Source Across — breaking changes from multiple source repos with broad cross-repo impact |
| **NK** | 2 | Non-Kubernetes — changes originating in non-core repos (kustomize, helm) |

## Adding New Questions

To add more queries for the ByteBell MCP to resolve, create new question folders following the same format as `results/KubeCluster40/question_*/question.json`.

### Steps

1. Pick a unique question ID (e.g. `CUSTOM_TC001`).
2. Create a folder inside your questions directory: `question_CUSTOM_TC001/`
3. Add a `question.json` inside it with this format:

```json
{
  "id": "CUSTOM_TC001",
  "question": "Your cross-repo impact question here...",
  "expected_answer": "Description of the expected impact...",
  "expected_files": [
    {"repo": "argo-cd", "path": "controller/appcontroller.go", "why": "Reason this file is affected"},
    {"repo": "prometheus", "path": "discovery/kubernetes/pod.go", "why": "Reason this file is affected"}
  ],
  "repo": "source-repo-name"
}
```

4. Run `mcp_context_generation.py` with the path to your folder:

```bash
python3 src/mcp_context_generation.py \
    --questions-dir results/KubeCluster40 \
    --mcp-config mcp_config.json
```

You can add any number of question folders. The script discovers all `question_*/question.json` files automatically and skips questions that already have cached successful answers.

### Using a Different Folder

You don't have to use `KubeCluster40`. You can create any folder with `question_*/question.json` subfolders and point the script at it:

```bash
# Create a new question set
mkdir -p results/ObservabilityQuestions/question_OBS_NEW_001
# Add question.json ...
mkdir -p results/ObservabilityQuestions/question_OBS_NEW_002
# Add question.json ...

# Run against your custom folder
python3 src/mcp_context_generation.py \
    --questions-dir results/ObservabilityQuestions \
    --mcp-config mcp_config.json
```

This lets you maintain separate question sets for different domains, test scenarios, or evaluation runs. Each folder is self-contained — questions and model results all live together under the same directory.

---

## How It Works

1. Connects to the ByteBell MCP server over StreamableHTTP
2. Fetches available MCP tools (`server_info`, `list_knowledge`, `graph_search`, `graph_traverse`, `retrieve_file`)
3. For each question, runs an agent loop:
   - LLM receives the question + MCP tools in OpenAI function-calling format
   - LLM calls tools to search across repos
   - Tool calls execute in parallel via `ThreadPoolExecutor`
   - Loop continues until the LLM produces a final answer or hits `--max-steps`
4. Results are saved incrementally after each question
5. Evaluation checks mentioned file paths against the actual dataset filesystem
6. Analysis uses an LLM judge to compare answers against expected answers for semantic relevance

Pure Python — no LangChain, no mcp_use. Direct HTTP calls to OpenRouter and the MCP server.
