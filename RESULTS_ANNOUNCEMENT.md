# Cross-Repository Impact Analysis Benchmark — Results

## The Dataset

We assembled a large-scale Kubernetes and observability codebase spanning **25 production repositories** and **82,894 source files** — including Kubernetes core, Prometheus, Grafana, ArgoCD, Istio, cert-manager, OpenTelemetry, Thanos, Loki, and more.

From this codebase, we wrote **40 cross-repository impact analysis questions** designed to test whether an LLM can trace the ripple effects of a breaking code change across multiple repositories. Each question follows the pattern:

> *"If you add/modify method X on interface Y in repo Z, which files across repos A, B, C, D would need to implement or adapt to this change?"*

The 40 questions fall into two categories:

| Category | Count | Description |
|----------|:-----:|-------------|
| **OBS** | 30 | Observability stack — interface/function changes in Prometheus, OpenTelemetry Collector, Thanos, Grafana, Jaeger, Loki, Mimir, and Tempo that ripple across the observability ecosystem |
| **MIXED** | 10 | Mixed infrastructure — breaking changes to shared Kubernetes interfaces (e.g. `SharedInformer`, `Querier`, `Clientset`) that affect both infrastructure tools and observability platforms |

Questions range from 2-repo impact (e.g., a Helm struct change affecting Kustomize) to 7-repo impact (e.g., a Kubernetes `types.go` struct change rippling through ArgoCD, cert-manager, Prometheus, Istio, and Cilium).

### Repository List

The complete dataset includes these 25 repositories:

| Repository | Domain |
|------------|--------|
| kubernetes/kubernetes | Core orchestration |
| prometheus/prometheus | Metrics collection |
| grafana/grafana | Visualization |
| istio/istio | Service mesh |
| cilium/cilium | Networking & security |
| argoproj/argo-cd | GitOps delivery |
| cert-manager/cert-manager | Certificate management |
| open-telemetry/opentelemetry-collector | Telemetry pipeline |
| open-telemetry/opentelemetry-collector-contrib | Telemetry contrib |
| open-telemetry/opentelemetry-operator | Telemetry operator |
| thanos-io/thanos | Long-term metrics storage |
| grafana/loki | Log aggregation |
| grafana/mimir | Metrics backend |
| grafana/tempo | Distributed tracing |
| jaegertracing/jaeger | Distributed tracing |
| helm/helm | Package management |
| kubernetes-sigs/kustomize | Configuration management |
| kubernetes/autoscaler | Auto-scaling |
| kubernetes/ingress-nginx | Ingress controller |
| kubernetes-sigs/external-dns | DNS management |
| external-secrets/external-secrets | Secrets management |
| fluxcd/flux2 | GitOps toolkit |
| open-policy-agent/gatekeeper | Policy enforcement |
| crossplane/crossplane | Infrastructure as code |
| aws/karpenter-provider-aws | Node provisioning |

---

## Evaluation Setup

Each model was given the same 40 questions and access to the **ByteBell MCP knowledge graph** — a tool that indexes all 82,894 files and exposes `graph_search`, `graph_traverse`, `retrieve_file`, and `list_knowledge` operations over the entire codebase. Models used an agentic loop: they planned a search strategy, called MCP tools to explore the codebase, followed dependency chains, and formulated a structured answer listing all affected files with reasoning.

Each model was allowed up to **25 agent steps** (tool calls) per question.

### Scoring Methodology

**We used an LLM as judge** to score results. The judge model was **Google Gemini 3.1 Pro Preview** (`google/gemini-3.1-pro-preview`).

Each model's answer was first **condensed** using a cheap model (`xiaomi/mimo-v2-flash`) into a structured summary containing:
- A brief explanation of the change's impact
- A flat list of affected files with reasons

The judge then scored each model's condensed answer **independently** on a **0-100% accuracy scale** using the following weighted criteria:

| Weight | Criteria | What It Measures |
|:------:|----------|------------------|
| **60%** | File Accuracy | Did the model identify the correct affected repositories and files? Are the listed files actually relevant to the interface change? |
| **30%** | Reasoning Quality | Did the model explain *why* each file is affected — interface implementation, dependency chain, data flow? |
| **10%** | Precision Penalty | Did the model list clearly irrelevant files (hallucination)? Models that pad answers with irrelevant files score lower. |

Scores are independent per model (not normalized across models), making them directly comparable as percentage accuracy.

---

## Results

### Leaderboard

| # | Model | Avg Accuracy | Total Cost | Accuracy/$ | Questions Judged |
|---|-------|:------------:|:----------:|:----------:|:----------------:|
| 1 | openai/gpt-5.1-codex-max | **78.8%** | $43.79 | 1.80 | 40 |
| 2 | anthropic/claude-haiku-4.5 | **77.2%** | $17.28 | 4.47 | 16* |
| 3 | google/gemini-3-flash-preview | **72.1%** | $12.48 | 5.78 | 40 |
| 4 | deepseek/deepseek-chat-v3.1 | **63.1%** | $3.03 | 20.84 | 40 |
| 5 | x-ai/grok-code-fast-1 | **48.5%** | $5.42 | 8.96 | 40 |
| 6 | claude-opus-4.6/aicopilot | **44.8%** | $0.00 | — | 40 |
| 7 | openai/gpt-5.1-codex-mini | **44.1%** | $9.68 | 4.56 | 40 |
| 8 | xiaomi/mimo-v2-flash | **43.6%** | $3.88 | 11.24 | 40 |

**\*Claude Haiku 4.5** only answered 16 of 40 questions due to being removed from the model rotation before completion. Its 77.2% average is based on 16 questions only.

**Total tokens consumed across all models: ~207 million tokens (~$95 USD).**

### About `claude-opus-4.6/aicopilot`

The `claude-opus-4.6/aicopilot` entry is **not** an MCP-based evaluation. It represents the answers produced when **Claude Code (Claude Opus 4.6) was given direct access to all 25 repositories on disk** — the full 82,894 files — and asked the same questions without the ByteBell MCP knowledge graph. This serves as a baseline measuring what a top-tier LLM can do with raw file access but no structured knowledge graph.

Its $0.00 cost reflects that it was run locally via Claude Code (AICopilot) rather than through OpenRouter API billing.

---

## Analysis

### 1. Tool-augmented search dramatically outperforms raw knowledge

GPT-5.1 Codex Max with MCP tools scored **78.8%** — nearly double the **44.8%** achieved by Claude Opus 4.6 with direct file access to the same codebase. The MCP knowledge graph's structured search (`graph_search`, `graph_traverse`) lets models efficiently discover cross-repo dependencies that even a top-tier model misses when relying on brute-force file reading.

### 2. Cost-efficiency varies by 10x across models

DeepSeek V3.1 achieves **63.1% accuracy at just $3.03** — a cost-efficiency ratio of 20.84 %/$, while GPT-5.1 Codex Max scores higher (78.8%) but at **$43.79**, giving it only 1.80 %/$. For organizations running this type of analysis at scale, DeepSeek delivers ~80% of the top model's accuracy at ~7% of the cost.

### 3. Model size alone doesn't predict cross-repo reasoning ability

GPT-5.1 Codex Mini (**44.1%**) scored below models like DeepSeek V3.1 (63.1%) and Gemini Flash (72.1%) despite being a larger, more expensive model. Cross-repository impact analysis requires disciplined tool use — knowing *when to stop searching* and *which dependency chains to follow* — rather than raw model capacity. Codex Mini frequently hallucinated irrelevant RBAC manifests and YAML files as needing interface updates.

### 4. Hallucination is the primary failure mode

The most common reason for low scores wasn't *missing* files — it was *inventing* them. Models that padded their answers with files from unrequested repositories, fabricated file paths, or confused consumers with implementors received heavy penalties. Grok Code Fast correctly noted that some consumers don't need changes but missed critical custom wrappers, while MiMo identified factory files but missed the key custom informer implementations.

### 5. The "sweet spot" for agentic code analysis

Gemini 3 Flash Preview hits the practical sweet spot: **72.1% accuracy at $12.48** with consistent 40/40 question coverage. It avoids the extreme cost of Codex Max while substantially outperforming the budget models. For teams that need reliable cross-repo impact analysis without enterprise-tier API budgets, this is the model to watch.

### 6. Direct file access is not a substitute for a knowledge graph

Claude Opus 4.6 — one of the most capable models available — scored only **44.8%** when given the full codebase directly. This isn't a model quality issue; it's an information retrieval problem. With 82,894 files, the model can't efficiently navigate dependency chains across 25 repositories without a structured index. The MCP knowledge graph transforms an impossible search problem into a tractable one.

---

## Methodology Notes

- All models accessed the same ByteBell MCP knowledge graph instance
- Questions and expected answers were written by humans before any model evaluation
- The judge model (Gemini 3.1 Pro Preview) was not one of the evaluated models
- Answer condensation before judging ensures the judge evaluates substance, not formatting
- All evaluation code, raw model answers, and judge scores are included in this repository for full reproducibility
- Cost calculations use OpenRouter API pricing as of the evaluation date

---

## Reproducing These Results

```bash
# 1. Clone and set up
git clone <this-repo>
cd public_evaluations
python3 -m venv . && source bin/activate
pip install requests python-dotenv psutil

# 2. Download the 25-repo dataset
python3 src/download_dataset.py

# 3. Generate model answers via MCP
python3 src/mcp_context_generation.py \
    --questions-dir results/KubeCluster30 \
    --mcp-config mcp_config.json


# 4. Run the LLM judge
python3 src/evaluate.py \
    --results-dir results/KubeCluster30 \
    --workers 4
```

See `README.md` for full documentation of all scripts, flags, and configuration options.
