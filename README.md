# ByteBell Cross-Repository Impact Analysis Benchmark

No existing benchmark tests whether an LLM + MCP tool can trace the ripple effects of a breaking code change across multiple repositories. We built our own.

We assembled **82,894 source files** across **15 Kubernetes ecosystem repositories**, wrote **100 cross-repo impact questions**, and ran them against **8 LLMs** via the ByteBell MCP knowledge graph — consuming **646 million tokens** (~$94 USD total).

## What We Did

1. **Built the dataset** — cloned 15 real-world Kubernetes repos (kubernetes, cilium, istio, helm, argo-cd, cert-manager, etc.) into `dataset/`, totaling 82,894 files
2. **Indexed them** into the ByteBell MCP knowledge graph server for semantic code search
3. **Wrote 100 test cases** (`cross_repo_whole.json`) — each describes a hypothetical breaking change in one repo (e.g. "add a method to the SharedInformer interface") and asks the LLM to find all affected files across the other repos
4. **Ran every question against 8 LLMs** via OpenRouter, each using MCP tools to search the codebase
5. **Evaluated answers** by checking whether the file paths each LLM mentioned actually exist in the dataset

## Dataset

15 repositories, 82,894 files:

| Repository | Files | GitHub |
|------------|------:|--------|
| kubernetes | 28,358 | kubernetes/kubernetes |
| cilium | 25,218 | cilium/cilium |
| istio | 6,108 | istio/istio |
| autoscaler | 5,867 | kubernetes/autoscaler |
| argo-cd | 5,132 | argoproj/argo-cd |
| helm | 1,974 | helm/helm |
| gatekeeper | 1,596 | open-policy-agent/gatekeeper |
| kustomize | 1,548 | kubernetes-sigs/kustomize |
| external-secrets | 1,491 | external-secrets/external-secrets |
| cert-manager | 1,235 | cert-manager/cert-manager |
| ingress-nginx | 1,140 | kubernetes/ingress-nginx |
| crossplane | 1,013 | crossplane/crossplane |
| karpenter | 993 | kubernetes-sigs/karpenter |
| flux2 | 669 | fluxcd/flux2 |
| external-dns | 552 | kubernetes-sigs/external-dns |

## Test Case Categories

100 test cases in `cross_repo_whole.json`, categorized by prefix:

| Prefix | Count | Description | Source Repos | Affected Repos |
|--------|:-----:|-------------|--------------|:--------------:|
| **CRW** | 71 | Cross-Repo Wide — struct/interface/function changes in core Kubernetes that break downstream consumers | kubernetes/kubernetes | 1-5 per question |
| **KM** | 14 | Kubernetes Modification — struct/interface changes in Kubernetes core packages | kubernetes/kubernetes | 1-4 per question |
| **SA** | 13 | Source Across — breaking changes from multiple source repos with broad cross-repo impact | kubernetes, kustomize, helm | 1-6 per question |
| **NK** | 2 | Non-Kubernetes — changes originating in non-core repos (kustomize, helm) | kustomize, helm | 1 per question |

All 100 questions are unique. Each describes a hypothetical breaking change (e.g. adding a method to an interface, changing a struct field type) and the LLM must identify which files across the 15 repos would be affected.

## Models Evaluated

| Model | Answers | Tokens | Cost |
|-------|--------:|-------:|-----:|
| stepfun/step-3.5-flash | 100 | 125M | $12.68 |
| xiaomi/mimo-v2-flash | 100 | 118M | $10.73 |
| arcee-ai/trinity-large-preview:free | 100 | 100M | $0.00 |
| deepseek/deepseek-chat-v3.1 | 89 | 87M | $8.75 |
| x-ai/grok-code-fast-1 | 100 | 85M | $17.91 |
| google/gemini-3-flash-preview | 99 | 64M | $32.30 |
| openai/gpt-oss-120b | 98 | 57M | $2.23 |
| anthropic/claude-haiku-4.5 | 10 | 10M | $9.03 |
| **Total** | **696** | **646M** | **$93.62** |

## How to Run

### 1. Setup

```bash
python3 -m venv .
source bin/activate
pip install requests python-dotenv
```

### 2. Configure

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

### 3. Run the multi-model evaluation

```bash
python3 src/multi_model_eval.py \
    --questions cross_repo_whole.json \
    --mcp-config mcp_config.json \
    --threads 3 \
    --timeout 120
```

This runs all 100 questions against every model in `models.json`. Successful results are cached — re-running automatically retries only failed/blank answers. Stops immediately on 402 payment errors.

### 4. Score the results

```bash
# Generate evaluation.json for each question (checks files against dataset/)
python3 src/evaluate.py

# Generate aggregate metrics.json across all models
python3 src/aggregate_metrics.py
```

## Output Structure

```
results/
  question_SA_TC001/
    question.json                    # The question
    xiaomi_mimo-v2-flash.json        # Model answer + tool calls + cost
    deepseek_deepseek-chat-v3.1.json # Another model's answer
    ...
    evaluation.json                  # Scores for each model on this question
  question_SA_TC002/
    ...
  metrics.json                       # Aggregate scores per model
```

### Evaluation Scoring

Each model answer is scored on two dimensions:

- **relevance_score** (0-10, higher = better): How many real files the model found, answer substance, and file coverage
- **hallucination_score** (0-10, higher = worse): Fraction of mentioned file paths that don't physically exist in `dataset/`

File verification is objective — every path mentioned in the LLM's answer is checked against the actual filesystem in `dataset/<repo>/<path>`.

## How It Works

1. Connects to the ByteBell MCP server over StreamableHTTP
2. Fetches available MCP tools (`server_info`, `list_knowledge`, `graph_search`, `graph_traverse`, `retrieve_file`)
3. For each question, runs an agent loop:
   - LLM receives the question + MCP tools in OpenAI function-calling format
   - LLM calls tools to search across repos
   - Tool calls execute in parallel via `ThreadPoolExecutor`
   - Loop continues until the LLM produces a final answer or hits `--max-steps`
4. Results are saved incrementally after each question

Pure Python — no LangChain, no mcp_use. Direct HTTP calls to OpenRouter and the MCP server.

## SWE-bench Pro Benchmark

A separate benchmark that runs SWE-bench Pro questions against multiple models via MCP, with versioned results and per-question analysis.

### Run the SWE-bench Pro test

```bash
python3 src/test_swe_bench_pro.py \
    --bench swe_bench_pro.json \
    --questions 5 \
    --threads 3
```

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--bench` | | `swe_bench_pro.json` | Path to SWE-bench Pro questions JSON |
| `--models-config` | | `swe_bench_models.json` | Path to models config JSON |
| `--mcp-config` | `-m` | `mcp_config.json` | Path to MCP config JSON |
| `--questions` | `-n` | `3` | Number of questions to run from the start |
| `--max-steps` | | `25` | Max agent steps per question |
| `--timeout` | | `120` | MCP call timeout in seconds |
| `--threads` | `-t` | `3` | Concurrent threads (single pool across all question×model pairs) |
| `--api-key` | | env | OpenRouter API key (falls back to `OPENROUTER_API_KEY`) |

Results are saved to `sweBenchProResults/<VERSION>/<instance_id>/` where `VERSION` comes from `.env`. Each question directory contains `question.json` and one `<model>.json` per model. Supports resume — existing result files are skipped on re-run. Retries up to 3 times on timeout/connection errors with backoff.

## All Runnable Scripts

### `src/evals.py` — Single-Model Benchmark Runner

Core infrastructure. Runs questions from a JSON file against a single model via MCP.

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

### `src/multi_model_eval.py` — Multi-Model Evaluator

Runs all questions against every model in `models.json`. Caches successful results — re-running retries only failed/blank answers. Stops immediately on 402 payment errors.

```bash
python3 src/multi_model_eval.py \
    --questions cross_repo_whole.json \
    --mcp-config mcp_config.json \
    --threads 3
```

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--questions` | `-q` | **required** | Path to questions JSON file |
| `--mcp-config` | `-m` | **required** | Path to MCP config JSON file |
| `--models` | | all from `models.json` | Specific model(s) to run |
| `--threads` | `-t` | `3` | Concurrent threads per model |
| `--max-steps` | | `25` | Max agent steps per question |
| `--timeout` | | `120` | Read timeout per MCP call in seconds |
| `--api-key` | | env | OpenRouter API key |
| `--num-questions` | `-n` | all | Number of questions to run |
| `--output-dir` | `-o` | `results` | Output directory for per-question results |
| `--seed` | | none | Random seed for reproducibility |

### `src/smoke_test.py` — LLM Smoke Test

Auto-discovers the maximum concurrent thread count the LLM can handle, then answers all questions at that concurrency. Monitors server memory usage.

```bash
python3 src/smoke_test.py \
    --questions cross_repo_whole.json \
    --mcp-config mcp_config.json
```

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--questions` | `-q` | **required** | Path to questions JSON file |
| `--mcp-config` | `-m` | **required** | Path to MCP config JSON file |
| `--start-threads` | | `3` | Initial thread count for discovery |
| `--thread-step` | | `1` | Threads to add each round |
| `--max-duration` | | unlimited | Hard time limit in seconds |
| `--model` | | `deepseek/deepseek-chat-v3.1` | OpenRouter model name |
| `--api-key` | | env | OpenRouter API key |
| `--max-steps` | | `25` | Max agent steps per question |
| `--timeout` | | `120` | Read timeout per MCP call in seconds |
| `--server-mem-limit` | | `4000` | Max server RSS in MB (stops test if exceeded) |
| `--seed` | | none | Random seed for reproducibility |

### `src/mcp_stress.py` — MCP Stress Test

Pure MCP stress test (no LLM). Hammers `graph_search` across threads and auto-discovers the maximum thread count within a RAM budget.

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

### `src/evaluate.py` — Answer Evaluator

Evaluates LLM answers by checking file paths against the actual dataset. Computes `relevance_score` (0-10) and `hallucination_score` (0-10) for each model answer. Writes `evaluation.json` into each question folder.

```bash
python3 src/evaluate.py
```

No arguments. Reads from `results/` and `dataset/` directories.

### `src/aggregate_metrics.py` — Aggregate Metrics

Aggregates per-model metrics across all questions into a final `metrics.json`.

```bash
python3 src/aggregate_metrics.py
```

No arguments. Reads `evaluation.json` files from `results/` and writes `results/metrics.json`.

### `src/count_errors.py` — Error Counter

Counts errored/blank answer files per model across all results.

```bash
python3 src/count_errors.py
```

No arguments. Reads from `results/` directory.

### `src/delete_errors.py` — Error File Cleanup

Deletes all errored/blank answer files so `multi_model_eval.py` will retry them on the next run.

```bash
python3 src/delete_errors.py
```

No arguments. Deletes errored files from `results/` directory.

### `src/error_analysis.py` — Error Type Breakdown

Classifies and counts error types (402, 429, timeout, 5xx, blank, etc.) across all failed answer files, broken down per model.

```bash
python3 src/error_analysis.py
```

No arguments. Reads from `results/` directory.
