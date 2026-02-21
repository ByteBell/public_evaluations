"""
ByteBell SWE-bench Pro MCP Benchmark Runner
=============================================
Pure Python — no LangChain, no mcp_use.
Direct HTTP calls to OpenRouter (LLM) and MCP server (tools).

Usage:
    pip install requests python-dotenv

    python src/evals.py \
        --questions sample_questions.json \
        --mcp-config mcp_config.json \
        --max-steps 25
"""

import argparse
import json
import os
import sys
import time
import logging
import traceback
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Any

from dotenv import load_dotenv

# ─── Logging ─────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("benchmark")


# ─── Data classes ────────────────────────────────────────────────────────────

@dataclass
class ToolCallRecord:
    tool_name: str = ""
    arguments: dict = field(default_factory=dict)
    result_preview: str = ""
    latency_seconds: float = 0.0


@dataclass
class QuestionResult:
    index: int = 0
    question_id: str = ""
    question_text: str = ""
    expected_answer: str = ""
    expected_files: list = field(default_factory=list)
    repo: str = ""
    answer: str = ""
    tools_called: list = field(default_factory=list)
    context_retrieved: list = field(default_factory=list)
    num_tool_calls: int = 0
    num_agent_steps: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    latency_seconds: float = 0.0
    status: str = "pending"
    error_message: str = ""
    timestamp: str = ""


# ─── MCP Client (StreamableHTTP) ────────────────────────────────────────────

class MCPClient:
    """Minimal MCP client over StreamableHTTP. No dependencies beyond requests."""

    def __init__(self, url: str, timeout: int = 30):
        self.url = url
        self.timeout = timeout
        self.session_id: str | None = None
        self.tools: list[dict] = []
        self._http = requests.Session()

    def _post(self, payload: dict) -> dict:
        """Send a JSON-RPC request to the MCP server and parse the SSE response."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.session_id:
            headers["mcp-session-id"] = self.session_id

        resp = self._http.post(self.url, json=payload, headers=headers, timeout=self.timeout)
        resp.raise_for_status()

        # Capture session ID from response headers
        sid = resp.headers.get("mcp-session-id")
        if sid:
            self.session_id = sid

        # Parse SSE: look for "data: {...}" lines
        body = resp.text
        for line in body.splitlines():
            if line.startswith("data: "):
                return json.loads(line[6:])

        # Fallback: try parsing whole body as JSON
        return resp.json()

    def initialize(self):
        """Initialize the MCP session and fetch available tools."""
        # 1. Initialize
        init_resp = self._post({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "bytebell-bench", "version": "2.0"},
            },
        })

        server_info = init_resp.get("result", {}).get("serverInfo", {})
        self.server_instructions = init_resp.get("result", {}).get("instructions", "")
        logger.info(f"MCP connected: {server_info.get('name', 'unknown')}")

        # 2. List tools
        tools_resp = self._post({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        })
        self.tools = tools_resp.get("result", {}).get("tools", [])
        logger.info(f"MCP tools: {[t['name'] for t in self.tools]}")

    def call_tool(self, name: str, arguments: dict) -> str:
        """Call an MCP tool and return the text result."""
        # Strip None values — LLMs send explicit nulls for optional params,
        # MCP servers (Zod validation) reject them.
        clean_args = {k: v for k, v in arguments.items() if v is not None}

        resp = self._post({
            "jsonrpc": "2.0",
            "id": int(time.time() * 1000),
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": clean_args,
            },
        })

        result = resp.get("result", {})

        # Handle error responses
        if resp.get("error"):
            err = resp["error"]
            return f"MCP error {err.get('code')}: {err.get('message')}"

        # Extract text from content array
        content = result.get("content", [])
        texts = []
        for item in content:
            if isinstance(item, dict):
                texts.append(item.get("text", str(item)))
            else:
                texts.append(str(item))
        return "\n".join(texts) if texts else str(result)

    def get_openai_tools(self) -> list[dict]:
        """Convert MCP tools to OpenAI function-calling format."""
        openai_tools = []
        for tool in self.tools:
            schema = tool.get("inputSchema", {})
            # Remove $schema key — OpenAI doesn't want it
            params = {k: v for k, v in schema.items() if k != "$schema"}
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": params,
                },
            })
        return openai_tools


# ─── OpenRouter LLM Client ──────────────────────────────────────────────────

class LLMClient:
    """Direct OpenRouter API calls. No LangChain."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        """Call the LLM and return the raw response JSON."""
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0,
            "max_tokens": 4096,
        }
        if tools:
            payload["tools"] = tools

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://bytebell.ai",
            "X-Title": "ByteBell SWE-bench Benchmark",
        }

        t0 = time.perf_counter()
        try:
            resp = requests.post(self.base_url, json=payload, headers=headers, timeout=120)
            resp.raise_for_status()
            elapsed = round(time.perf_counter() - t0, 1)
            data = resp.json()
            usage = data.get("usage", {})
            logger.info(f"[LLM] {self.model} replied in {elapsed}s | "
                         f"prompt={usage.get('prompt_tokens', '?')} "
                         f"completion={usage.get('completion_tokens', '?')}")
            return data
        except requests.exceptions.Timeout:
            elapsed = round(time.perf_counter() - t0, 1)
            logger.error(f"[LLM] {self.model} TIMED OUT after {elapsed}s")
            raise
        except requests.exceptions.HTTPError as e:
            elapsed = round(time.perf_counter() - t0, 1)
            logger.error(f"[LLM] {self.model} HTTP {e.response.status_code} after {elapsed}s")
            raise


# ─── Agent Loop ──────────────────────────────────────────────────────────────

class AgentTimeoutError(TimeoutError):
    """Raised when the agent loop exceeds its wall-clock timeout."""
    pass


def run_agent(
    llm: LLMClient,
    mcp: MCPClient,
    question: str,
    max_steps: int = 25,
    verbose: bool = False,
    wall_timeout: int = 600,
) -> tuple[str, list[ToolCallRecord], int, int, int]:
    """
    Simple tool-calling loop. Returns:
        (answer, tool_calls, agent_steps, total_input_tokens, total_output_tokens)

    Args:
        wall_timeout: Maximum wall-clock seconds for the entire agent loop (default 600 = 10 min).
                      Set to 0 to disable.
    """
    system_prompt = (
        "You are an expert code analyst and software architect performing an EXHAUSTIVE codebase audit. "
        "You have access to a knowledge graph spanning MULTIPLE repositories. "
        "Your job is to find EVERY file that is relevant to the question, understand how they interact, "
        "and produce a grounded, evidence-backed analysis — missing even one file is a failure.\n\n"

        "## Phase 1: Planning\n\n"
        "Before making any tool calls, reason about the question:\n"
        "- What domains does this touch? (DB, backend, frontend, config, infra)\n"
        "- What keywords, class names, or patterns should I search for?\n"
        "- Which repos are likely involved?\n"
        "Plan your search strategy, then execute it.\n\n"

        "## Phase 2: Discovery\n\n"
        "1. Call `server_info` first.\n"
        "2. Call `list_knowledge` to discover ALL available repositories.\n"
        "3. For EACH repo that could be relevant, search with `graph_search` using multiple query variations "
        "(different keywords, synonyms, related concepts). A single search is NEVER enough.\n"
        "4. For promising files, call `retrieve_file` with operation=metadata to read purpose, classes, "
        "functions, and imports. Use this to discover MORE related files (callers, callees, shared interfaces).\n"
        "5. Follow the dependency chain: if file A imports/calls file B, search for file B too.\n"
        "6. Search across ALL layers: DB schema/SQL, backend service/controller/helper/DAO, "
        "frontend UI components, config files, API DTOs.\n"
        "7. After each round of tool calls, assess: 'What have I found so far? What gaps remain? "
        "Have I covered ALL repos and ALL layers?' If gaps remain, keep searching.\n"
        "8. Only move to Phase 3 when you are >90%% confident you have found ALL relevant files.\n\n"

        "## Phase 3: Synthesis & Answer\n\n"
        "Your answer MUST be proper Markdown with these sections:\n\n"
        "### 1. Architecture Overview\n"
        "Explain the end-to-end flow/architecture. How do the components interact? "
        "What is the request/data path from start to finish?\n\n"
        "### 2. Detailed Analysis\n"
        "For each major component, provide code-level details:\n"
        "- Exact class names, method signatures, DB table/column names\n"
        "- How data flows between components (API calls, imports, shared models)\n"
        "- **Ground every claim in tool output** — cite the specific file and function/class you found. "
        "Do NOT make claims that are not backed by evidence from your tool calls.\n\n"
        "### 3. Relevant Files\n\n"
        "A complete table with EVERY file across ALL repos:\n\n"
        "| Repo | File Path | Why |\n"
        "|------|-----------|-----|\n"
        "| repo-name | full/path/to/File.java | Specific reason (mention class/method/field names) |\n\n"
        "This table MUST include files from EVERY relevant repo and EVERY layer (DB, backend, frontend, config). "
        "Do NOT omit files. More files is better than fewer files.\n\n"

        f"## MCP Server Instructions\n\n{mcp.server_instructions}"
    )

    messages: list[dict] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]

    tools = mcp.get_openai_tools()
    tool_records: list[ToolCallRecord] = []
    total_input = 0
    total_output = 0
    steps = 0
    wall_start = time.perf_counter()

    def _check_wall_timeout(phase: str):
        if wall_timeout and (time.perf_counter() - wall_start) > wall_timeout:
            elapsed = round(time.perf_counter() - wall_start, 1)
            raise AgentTimeoutError(
                f"Agent wall-clock timeout ({wall_timeout}s) exceeded during {phase} "
                f"after {elapsed}s and {steps} steps"
            )

    for step in range(max_steps):
        steps += 1
        step_start = time.perf_counter()

        _check_wall_timeout(f"step {step + 1} start")

        logger.info(f"[AGENT] Step {step + 1}/{max_steps} | "
                     f"wall={round(time.perf_counter() - wall_start, 1)}s | "
                     f"tokens_so_far={total_input + total_output}")

        # Call LLM
        logger.info(f"[LLM] Calling {llm.model} ...")
        llm_start = time.perf_counter()
        resp = llm.chat(messages, tools=tools)
        llm_elapsed = round(time.perf_counter() - llm_start, 1)
        logger.info(f"[LLM] Response in {llm_elapsed}s")

        choice = resp.get("choices", [{}])[0]
        message = choice.get("message", {})
        finish_reason = choice.get("finish_reason", "")

        # Track tokens
        usage = resp.get("usage", {})
        total_input += usage.get("prompt_tokens", 0)
        total_output += usage.get("completion_tokens", 0)

        tool_calls = message.get("tool_calls")

        # No tool calls → final answer
        if not tool_calls or finish_reason == "stop":
            answer = message.get("content", "") or ""
            return answer, tool_records, steps, total_input, total_output

        # Append assistant message with tool calls
        messages.append(message)

        # Parse all tool calls
        parsed_calls = []
        for tc in tool_calls:
            fn = tc.get("function", {})
            tool_name = fn.get("name", "")
            try:
                tool_args = json.loads(fn.get("arguments", "{}"))
            except json.JSONDecodeError:
                tool_args = {}
            parsed_calls.append((tc.get("id", ""), tool_name, tool_args))

        names = [name for _, name, _ in parsed_calls]
        logger.info(f"[TOOLS] Executing {len(parsed_calls)} tool call(s) in parallel: {names}")

        # Execute all tool calls in parallel
        def _exec_tool(tc_id, tool_name, tool_args):
            t0 = time.perf_counter()
            result_text = mcp.call_tool(tool_name, tool_args)
            elapsed = round(time.perf_counter() - t0, 3)
            return tc_id, tool_name, tool_args, result_text, elapsed

        # Calculate remaining wall-clock budget for tool execution
        tool_timeout = None
        if wall_timeout:
            remaining = wall_timeout - (time.perf_counter() - wall_start)
            if remaining <= 0:
                _check_wall_timeout("tool execution start")
            tool_timeout = max(remaining, 10)  # at least 10s

        results_map = {}
        with ThreadPoolExecutor(max_workers=min(len(parsed_calls), 8)) as pool:
            futures = {
                pool.submit(_exec_tool, tc_id, name, args): tc_id
                for tc_id, name, args in parsed_calls
            }
            done_futures = set()
            try:
                for future in as_completed(futures, timeout=tool_timeout):
                    tc_id, tool_name, tool_args, result_text, elapsed = future.result()
                    results_map[tc_id] = (tool_name, tool_args, result_text, elapsed)
                    done_futures.add(future)
                    logger.info(f"[TOOLS] {tool_name} completed in {elapsed}s")
            except TimeoutError:
                # Some tool calls didn't finish in time — cancel them
                pending_ids = []
                for f, tid in futures.items():
                    if f not in done_futures:
                        f.cancel()
                        pending_ids.append(tid)
                raise AgentTimeoutError(
                    f"Tool execution timed out after {tool_timeout:.0f}s. "
                    f"Pending tool call IDs: {pending_ids}"
                )

        # Append results in original order (must match tool_calls order)
        for tc_id, tool_name, tool_args in parsed_calls:
            _, _, result_text, tool_elapsed = results_map[tc_id]

            result_preview = result_text[:500] + ("..." if len(result_text) > 500 else "")
            tool_records.append(ToolCallRecord(
                tool_name=tool_name,
                arguments=tool_args,
                result_preview=result_preview,
                latency_seconds=tool_elapsed,
            ))

            if verbose:
                preview = result_text[:200].replace("\n", " ")
                logger.info(f"    {tool_name} ({tool_elapsed}s) -> {preview}...")

            messages.append({
                "role": "tool",
                "tool_call_id": tc_id,
                "content": result_text,
            })

        step_elapsed = round(time.perf_counter() - step_start, 1)
        logger.info(f"[AGENT] Step {step + 1} complete in {step_elapsed}s | "
                     f"total_tool_calls={len(tool_records)}")

    # Max steps reached — ask for final answer
    wall_elapsed = round(time.perf_counter() - wall_start, 1)
    logger.info(f"[AGENT] Max steps ({max_steps}) reached after {wall_elapsed}s — requesting final answer")
    messages.append({
        "role": "user",
        "content": "You have reached the maximum number of tool calls. Please provide your best answer now based on what you've gathered.",
    })
    logger.info(f"[LLM] Calling {llm.model} (final answer) ...")
    llm_start = time.perf_counter()
    resp = llm.chat(messages, tools=None)
    llm_elapsed = round(time.perf_counter() - llm_start, 1)
    logger.info(f"[LLM] Final answer in {llm_elapsed}s")

    choice = resp.get("choices", [{}])[0]
    message = choice.get("message", {})
    usage = resp.get("usage", {})
    total_input += usage.get("prompt_tokens", 0)
    total_output += usage.get("completion_tokens", 0)
    steps += 1

    total_wall = round(time.perf_counter() - wall_start, 1)
    logger.info(f"[AGENT] Complete: {steps} steps, {len(tool_records)} tool calls, "
                 f"{total_input + total_output} tokens, {total_wall}s wall time")

    return message.get("content", ""), tool_records, steps, total_input, total_output


# ─── Models config ────────────────────────────────────────────────────────────

_models_config: dict = {}
_MODELS_JSON = Path(__file__).resolve().parent.parent / "models.json"


def load_models_config(path: Path | None = None) -> dict:
    """Load models.json. Cached after first call."""
    global _models_config
    if _models_config:
        return _models_config
    p = path or _MODELS_JSON
    if p.exists():
        with open(p) as f:
            _models_config = json.load(f)
        logger.info(f"Loaded {len(_models_config.get('models', {}))} models from {p.name}")
    else:
        logger.warning(f"models.json not found at {p} — using empty config")
        _models_config = {"models": {}}
    return _models_config


def get_model_pricing(model: str) -> tuple[float, float]:
    """Return (input_cost_per_million, output_cost_per_million) for a model.

    Lookup order:
      1. models.json per-model pricing
      2. OpenRouter pricing API
      3. Zero (free)
    """
    cfg = load_models_config()
    model_entry = cfg.get("models", {}).get(model) or cfg.get("models", {}).get(model.split(":")[0])

    if model_entry:
        return (
            float(model_entry["input_cost_per_million_tokens"]),
            float(model_entry["output_cost_per_million_tokens"]),
        )

    # Fallback: OpenRouter API
    cache = _fetch_openrouter_pricing()
    pricing = cache.get(model.split(":")[0])
    if pricing:
        return pricing["input"], pricing["output"]

    return 0.0, 0.0


# ─── Token cost estimation ───────────────────────────────────────────────────

_pricing_cache: dict[str, dict] = {}


def _fetch_openrouter_pricing() -> dict[str, dict]:
    global _pricing_cache
    if _pricing_cache:
        return _pricing_cache
    try:
        resp = requests.get("https://openrouter.ai/api/v1/models", timeout=15)
        resp.raise_for_status()
        for m in resp.json().get("data", []):
            mid = m.get("id", "")
            pricing = m.get("pricing", {})
            _pricing_cache[mid] = {
                "input": round(float(pricing.get("prompt", "0")) * 1_000_000, 4),
                "output": round(float(pricing.get("completion", "0")) * 1_000_000, 4),
            }
        logger.info(f"Fetched pricing for {len(_pricing_cache)} models")
    except Exception as e:
        logger.warning(f"Could not fetch pricing: {e}")
    return _pricing_cache


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost in USD using per-model pricing from models.json."""
    input_rate, output_rate = get_model_pricing(model)
    cost = (input_tokens * input_rate / 1_000_000) + \
           (output_tokens * output_rate / 1_000_000)
    return round(cost, 6)


# ─── Answer condensation ─────────────────────────────────────────────────────


def condense_answer(answer: str, question: str, api_key: str,
                    model: str | None = None) -> str:
    """Condense a verbose model answer into a short summary + file list.

    Uses the smoke_test_model (cheap/fast) from models.json to extract
    just the essential findings: brief summary and affected file paths.

    Returns condensed text, or the original answer (truncated) on failure.
    """
    if not answer or not answer.strip():
        return "(empty)"

    if model is None:
        cfg = load_models_config()
        model = cfg.get("smoke_test_model", "xiaomi/mimo-v2-flash")

    prompt = (
        "Condense the following model answer into a structured summary.\n"
        "Extract ONLY:\n"
        "1. A 2-3 sentence summary of the key findings\n"
        "2. The list of specific file paths mentioned with a brief reason for each\n\n"
        f"QUESTION: {question}\n\n"
        f"FULL ANSWER:\n{answer}\n\n"
        "Respond in this exact format (no markdown, no code fences):\n"
        "SUMMARY: <2-3 sentences>\n"
        "FILES:\n"
        "- <repo>/<path/to/file> — <brief reason>\n"
        "- <repo>/<path/to/file> — <brief reason>\n"
        "...\n"
    )

    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
                "max_tokens": 4096,
            },
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=30,
        )
        resp.raise_for_status()
        content = resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        condensed = content.strip()
        if condensed:
            return condensed
    except Exception as e:
        logger.warning(f"condense_answer failed: {e}")

    # Fallback: truncate original
    return answer[:3000] + "\n... [truncated]" if len(answer) > 3000 else answer


# ─── Benchmark Runner ────────────────────────────────────────────────────────

def run_single_question(
    llm: LLMClient,
    mcp: MCPClient,
    question: dict,
    index: int,
    model_name: str,
    max_steps: int,
    timeout: int,
    verbose: bool,
) -> QuestionResult:
    q_id = str(question.get("id", f"q_{index}"))
    q_text = question.get("question", "")
    q_expected = question.get("answer", "")
    q_files = question.get("files", [])
    q_repo = question.get("repo", "")

    result = QuestionResult(
        index=index,
        question_id=q_id,
        question_text=q_text,
        expected_answer=q_expected,
        expected_files=q_files,
        repo=q_repo,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    logger.info(f"[{index}] Running: {q_id}")
    start = time.perf_counter()

    try:
        answer, tool_records, steps, inp_tok, out_tok = run_agent(
            llm, mcp, q_text, max_steps=max_steps, verbose=verbose,
        )

        elapsed = time.perf_counter() - start
        result.answer = answer
        result.latency_seconds = round(elapsed, 2)
        result.status = "success"
        result.tools_called = [asdict(tc) for tc in tool_records]
        result.num_tool_calls = len(tool_records)
        result.num_agent_steps = steps
        result.input_tokens = inp_tok
        result.output_tokens = out_tok
        result.total_tokens = inp_tok + out_tok
        result.estimated_cost_usd = estimate_cost(model_name, inp_tok, out_tok)

    except Exception as e:
        elapsed = time.perf_counter() - start
        result.latency_seconds = round(elapsed, 2)
        result.status = "error"
        result.error_message = f"{type(e).__name__}: {str(e)}"
        logger.error(f"[{index}] Error: {q_id} — {e}")
        if verbose:
            logger.debug(traceback.format_exc())

    logger.info(
        f"[{index}] Done: {result.status} | "
        f"{result.latency_seconds}s | "
        f"{result.num_tool_calls} tools | "
        f"{result.total_tokens} tokens | "
        f"${result.estimated_cost_usd}"
    )
    return result


def run_benchmark(args: argparse.Namespace):
    load_dotenv()

    api_key = args.api_key or os.getenv("OPENROUTER_API_KEY", "")
    model_name = args.model or os.getenv("OPENROUTER_MODEL_NAME", "deepseek/deepseek-chat-v3.1")

    if not api_key:
        logger.error("No API key. Set OPENROUTER_API_KEY or use --api-key")
        sys.exit(1)

    # Load questions
    questions_path = Path(args.questions)
    if not questions_path.exists():
        logger.error(f"Questions file not found: {questions_path}")
        sys.exit(1)

    with open(questions_path) as f:
        questions = json.load(f)
    if isinstance(questions, dict):
        questions = questions.get("questions", questions.get("data", [questions]))

    total = len(questions)
    start_idx = args.start or 0
    end_idx = args.end or total
    questions = questions[start_idx:end_idx]

    logger.info(f"Loaded {total} questions, running [{start_idx}:{end_idx}] = {len(questions)}")
    logger.info(f"Model: {model_name}")

    # Setup MCP
    with open(Path(args.mcp_config)) as f:
        mcp_config = json.load(f)
    mcp_url = list(mcp_config.get("mcpServers", {}).values())[0]["url"]

    mcp = MCPClient(mcp_url)
    mcp.initialize()

    # Setup LLM
    llm = LLMClient(api_key, model_name)

    # Run
    results: list[dict] = []

    # Auto-generate output filename: {timestamp}-{model_name}.json
    run_ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_model = model_name.replace("/", "_").replace(":", "_")
    output_path = Path(args.output_dir) / f"{run_ts}-{safe_model}.json"

    data_dir = Path(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    logger.info(f"Results file: {output_path}")

    run_start = time.perf_counter()

    for i, question in enumerate(questions):
        global_idx = start_idx + i

        result = run_single_question(
            llm, mcp, question, global_idx, model_name,
            args.max_steps, args.timeout, args.verbose,
        )

        result_dict = asdict(result)
        results.append(result_dict)
        _save_question_result(data_dir, result_dict, model_name)
        _save_results(output_path, results, model_name, args, run_start)

        if args.delay > 0 and i < len(questions) - 1:
            time.sleep(args.delay)

    # Final summary
    run_elapsed = time.perf_counter() - run_start
    summary = _compute_summary(results, model_name, run_elapsed)
    _save_results(output_path, results, model_name, args, run_start, summary)

    logger.info("=" * 60)
    logger.info("BENCHMARK COMPLETE")
    logger.info(f"  Total questions:  {summary['total_questions']}")
    logger.info(f"  Successful:       {summary['successful']}")
    logger.info(f"  Errors:           {summary['errors']}")
    logger.info(f"  Timeouts:         {summary['timeouts']}")
    logger.info(f"  Total time:       {summary['total_time_seconds']}s")
    logger.info(f"  Avg latency:      {summary['avg_latency_seconds']}s")
    logger.info(f"  Total tokens:     {summary['total_tokens']}")
    logger.info(f"  Total cost:       ${summary['total_cost_usd']}")
    logger.info(f"  Total tool calls: {summary['total_tool_calls']}")
    logger.info(f"  Results saved to: {output_path}")
    logger.info("=" * 60)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _compute_summary(results: list[dict], model: str, elapsed: float) -> dict:
    successful = [r for r in results if r["status"] == "success"]
    errors = [r for r in results if r["status"] == "error"]
    timeouts = [r for r in results if r["status"] == "timeout"]
    latencies = [r["latency_seconds"] for r in successful]
    avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else 0

    return {
        "model": model,
        "total_questions": len(results),
        "successful": len(successful),
        "errors": len(errors),
        "timeouts": len(timeouts),
        "total_time_seconds": round(elapsed, 2),
        "avg_latency_seconds": avg_latency,
        "median_latency_seconds": round(sorted(latencies)[len(latencies) // 2], 2) if latencies else 0,
        "total_tokens": sum(r["total_tokens"] for r in results),
        "total_input_tokens": sum(r["input_tokens"] for r in results),
        "total_output_tokens": sum(r["output_tokens"] for r in results),
        "total_cost_usd": round(sum(r["estimated_cost_usd"] for r in results), 4),
        "total_tool_calls": sum(r["num_tool_calls"] for r in results),
        "avg_tool_calls_per_question": round(
            sum(r["num_tool_calls"] for r in results) / len(results), 2
        ) if results else 0,
    }


def _save_question_result(results_dir: Path, result: dict, model: str):
    q_id = str(result.get("question_id", f"q_{result.get('index', 0)}"))
    safe_id = q_id.replace("/", "_").replace("\\", "_").replace(" ", "_")
    q_dir = results_dir / safe_id
    q_dir.mkdir(parents=True, exist_ok=True)

    # 1. answer.md — the LLM's markdown answer
    answer_text = result.get("answer", "")
    question_text = result.get("question_text", "")
    with open(q_dir / "answer.md", "w") as f:
        f.write(f"# Question {q_id}\n\n")
        f.write(f"> {question_text}\n\n")
        f.write(f"---\n\n")
        f.write(answer_text or "_No answer generated._")
        f.write("\n")
    logger.info(f"  Saved: {q_dir / 'answer.md'}")

    # 2. tool_calls.json — raw tool call log
    with open(q_dir / "tool_calls.json", "w") as f:
        json.dump(result.get("tools_called", []), f, indent=2, default=str)
    logger.info(f"  Saved: {q_dir / 'tool_calls.json'}")

    # 3. result.json — metadata (no answer text, no tool calls)
    entry = {
        "question_id": q_id,
        "question": question_text,
        "expected_answer": result.get("expected_answer", ""),
        "expected_files": result.get("expected_files", []),
        "cost": {
            "input_tokens": result.get("input_tokens", 0),
            "output_tokens": result.get("output_tokens", 0),
            "total_tokens": result.get("total_tokens", 0),
            "estimated_cost_usd": result.get("estimated_cost_usd", 0.0),
            "model": model,
        },
        "status": result.get("status", ""),
        "latency_seconds": result.get("latency_seconds", 0.0),
        "num_tool_calls": result.get("num_tool_calls", 0),
        "num_agent_steps": result.get("num_agent_steps", 0),
        "error_message": result.get("error_message", ""),
        "timestamp": result.get("timestamp", ""),
    }

    with open(q_dir / "result.json", "w") as f:
        json.dump(entry, f, indent=2, default=str)
    logger.info(f"  Saved: {q_dir / 'result.json'}")


def _save_results(
    path: Path, results: list[dict], model: str,
    args: argparse.Namespace, run_start: float,
    summary: dict | None = None,
):
    output = {
        "benchmark": "bytebell-swe-bench-pro",
        "model": model,
        "mcp_config": args.mcp_config,
        "max_steps": args.max_steps,
        "timeout": args.timeout,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "questions_file": args.questions,
        "total_results": len(results),
        "summary": summary or {},
        "results": results,
    }
    with open(path, "w") as f:
        json.dump(output, f, indent=2, default=str)


# ─── CLI ─────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ByteBell SWE-bench Pro MCP Benchmark Runner")
    parser.add_argument("--questions", "-q", required=True)
    parser.add_argument("--mcp-config", "-m", required=True)
    parser.add_argument("--output-dir", "-o", default="results")
    parser.add_argument("--data-dir", "-d", default="results")
    parser.add_argument("--model", default=None)
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--max-steps", type=int, default=40)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--start", type=int, default=None)
    parser.add_argument("--end", type=int, default=None)
    parser.add_argument("--verbose", "-v", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_benchmark(args)
