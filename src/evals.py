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

    def __init__(self, url: str):
        self.url = url
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

        resp = self._http.post(self.url, json=payload, headers=headers, timeout=30)
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

        resp = requests.post(self.base_url, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        return resp.json()


# ─── Agent Loop ──────────────────────────────────────────────────────────────

def run_agent(
    llm: LLMClient,
    mcp: MCPClient,
    question: str,
    max_steps: int = 25,
    verbose: bool = False,
) -> tuple[str, list[ToolCallRecord], int, int, int]:
    """
    Simple tool-calling loop. Returns:
        (answer, tool_calls, agent_steps, total_input_tokens, total_output_tokens)
    """
    system_prompt = (
        "You are an expert code analyst performing an EXHAUSTIVE codebase audit. "
        "You have access to a knowledge graph spanning MULTIPLE repositories. "
        "Your job is to find EVERY file that is relevant to the question — missing even one file is a failure.\n\n"

        "## Workflow\n\n"
        "1. Call `server_info` first.\n"
        "2. Call `list_knowledge` to discover ALL available repositories.\n"
        "3. For EACH repo that could be relevant, search with `graph_search` using multiple query variations "
        "(different keywords, synonyms, related concepts). A single search is NEVER enough.\n"
        "4. For promising files, call `retrieve_file` with operation=metadata to read purpose, classes, "
        "functions, and imports. Use this to discover MORE related files (callers, callees, shared interfaces).\n"
        "5. Follow the dependency chain: if file A imports/calls file B, search for file B too.\n"
        "6. Search across ALL layers: DB schema/SQL, backend service/controller/helper/DAO, "
        "frontend UI components, config files, API DTOs.\n"
        "7. BEFORE answering, ask yourself: 'Have I searched ALL repos? Have I covered DB, backend, "
        "frontend, and config layers? Have I followed imports and call chains?' "
        "If the answer is no, keep searching.\n"
        "8. Only produce your final answer when you are >90%% confident you have found ALL relevant files.\n\n"

        "## Answer Format\n\n"
        "Your answer MUST be proper Markdown with:\n"
        "- A clear explanation of the flow/architecture\n"
        "- Code-level details (class names, method names, DB columns) where relevant\n"
        "- A ## Relevant Files section at the END with EVERY file across ALL repos:\n\n"
        "## Relevant Files\n\n"
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

    for step in range(max_steps):
        steps += 1

        if verbose:
            logger.info(f"  Step {step + 1}/{max_steps}")

        # Call LLM
        resp = llm.chat(messages, tools=tools)
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

        if verbose:
            names = [name for _, name, _ in parsed_calls]
            logger.info(f"    Executing {len(parsed_calls)} tool call(s) in parallel: {names}")

        # Execute all tool calls in parallel
        def _exec_tool(tc_id, tool_name, tool_args):
            result_text = mcp.call_tool(tool_name, tool_args)
            return tc_id, tool_name, tool_args, result_text

        results_map = {}
        with ThreadPoolExecutor(max_workers=min(len(parsed_calls), 8)) as pool:
            futures = {
                pool.submit(_exec_tool, tc_id, name, args): tc_id
                for tc_id, name, args in parsed_calls
            }
            for future in as_completed(futures):
                tc_id, tool_name, tool_args, result_text = future.result()
                results_map[tc_id] = (tool_name, tool_args, result_text)

        # Append results in original order (must match tool_calls order)
        for tc_id, tool_name, tool_args in parsed_calls:
            _, _, result_text = results_map[tc_id]

            result_preview = result_text[:500] + ("..." if len(result_text) > 500 else "")
            tool_records.append(ToolCallRecord(
                tool_name=tool_name,
                arguments=tool_args,
                result_preview=result_preview,
            ))

            if verbose:
                preview = result_text[:200].replace("\n", " ")
                logger.info(f"    {tool_name} -> {preview}...")

            messages.append({
                "role": "tool",
                "tool_call_id": tc_id,
                "content": result_text,
            })

    # Max steps reached — ask for final answer
    messages.append({
        "role": "user",
        "content": "You have reached the maximum number of tool calls. Please provide your best answer now based on what you've gathered.",
    })
    resp = llm.chat(messages, tools=None)
    choice = resp.get("choices", [{}])[0]
    message = choice.get("message", {})
    usage = resp.get("usage", {})
    total_input += usage.get("prompt_tokens", 0)
    total_output += usage.get("completion_tokens", 0)
    steps += 1

    return message.get("content", ""), tool_records, steps, total_input, total_output


# ─── Token cost estimation ───────────────────────────────────────────────────

_pricing_cache: dict[str, dict] = {}
DEFAULT_PRICING = {"input": 3.0, "output": 15.0}


def fetch_openrouter_pricing() -> dict[str, dict]:
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
    cache = fetch_openrouter_pricing()
    pricing = cache.get(model.split(":")[0], DEFAULT_PRICING)
    cost = (input_tokens * pricing["input"] / 1_000_000) + \
           (output_tokens * pricing["output"] / 1_000_000)
    return round(cost, 6)


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
    output_path = Path(args.output)
    data_dir = Path(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

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
    parser.add_argument("--output", "-o", default="benchmark_results.json")
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
