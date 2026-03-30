#!/usr/bin/env python3
"""
Small-Eval Answer Generator
============================
Generates answers for every question in results/small-eval/ using an
MCP-connected LLM via OpenRouter. Only the raw `question` field is sent —
no tier, PR number, or other metadata is included in the prompt.

Output saved as answer_{model_name}_{mcp_version}.json inside each q* folder.
Tool calls are explicitly recorded in the output JSON.

Usage:
    python3 src/small_eval_answer_gen.py \
        --model_name "anthropic/claude-sonnet-4-5" \
        --mcp_version "gitnexus-v1"

    # Explicit credentials:
    python3 src/small_eval_answer_gen.py \
        --model_name "openai/gpt-4o" \
        --mcp_version "gitnexus-v1" \
        --mcp_url "https://mcp.example.com/mcp?apiKey=..." \
        --api_key sk-or-v1-...

    # Override questions dir:
    python3 src/small_eval_answer_gen.py \
        --model_name "google/gemini-pro" \
        --mcp_version "gitnexus-v2" \
        --questions_dir results/small-eval \
        --threads 2

Credentials (in priority order):
    --api_key flag > OPENROUTER_API_KEY env var
    --mcp_url flag > MCP_URL env var
    .env file is loaded automatically.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Optional

import requests
from dotenv import load_dotenv

# ─── Logging ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("small_eval_answer_gen")

# ─── Constants ────────────────────────────────────────────────────────────────

DEFAULT_QUESTIONS_DIR = (
    Path(__file__).resolve().parents[1] / "results" / "small-eval"
)
MAX_RETRIES = 3
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"


# ─── Data classes ─────────────────────────────────────────────────────────────

@dataclass
class ToolCallRecord:
    tool_name: str = ""
    arguments: dict = field(default_factory=dict)
    result_preview: str = ""
    full_result: str = ""
    latency_seconds: float = 0.0


# ─── MCP Client ───────────────────────────────────────────────────────────────

class MCPClient:
    """Minimal MCP StreamableHTTP client (spec 2025-03-26)."""

    def __init__(self, url: str, timeout: int = 30):
        self.url = url
        self.timeout = timeout
        self.session_id: Optional[str] = None
        self.tools: list = []
        self.server_instructions: str = ""
        self._http = requests.Session()
        self._req_counter = 0

    def _next_id(self) -> int:
        self._req_counter += 1
        return self._req_counter

    def _post(self, payload: dict, expect_response: bool = True) -> Optional[dict]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id

        resp = self._http.post(
            self.url, json=payload, headers=headers,
            timeout=self.timeout, stream=True,
        )
        try:
            sid = resp.headers.get("Mcp-Session-Id")
            if sid:
                self.session_id = sid

            if resp.status_code == 202:
                return None

            resp.raise_for_status()

            content_type = resp.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return resp.json()

            if "text/event-stream" in content_type:
                for line in resp.iter_lines(decode_unicode=True):
                    if not line or line.startswith(":") or line.startswith("event:"):
                        continue
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                        except json.JSONDecodeError:
                            logger.warning(f"[MCP] Malformed SSE data: {line[:100]}")
                            continue
                        if "id" in data and ("result" in data or "error" in data):
                            return data
                        if "method" in data:
                            logger.debug(f"[MCP] Server notification: {data.get('method')}")
                if expect_response:
                    raise TimeoutError("MCP SSE stream closed without a JSON-RPC response")
                return None

            logger.warning(f"[MCP] Unexpected Content-Type: {content_type}, trying JSON")
            return resp.json()
        finally:
            resp.close()

    def initialize(self):
        """Full MCP initialization handshake."""
        endpoint = self.url.split("?")[0]
        logger.info(f"[MCP] Connecting to {endpoint}...")

        init_resp = self._post({
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "bytebell-bench", "version": "3.0"},
            },
        })
        result = init_resp.get("result", {})
        server_info = result.get("serverInfo", {})
        self.server_instructions = result.get("instructions", "")
        logger.info(
            f"[MCP] Connected: {server_info.get('name', '?')} v{server_info.get('version', '?')} "
            f"| session={self.session_id or 'none'}"
        )

        # Required initialized notification
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"},
                   expect_response=False)

        # Fetch tools
        tools_resp = self._post({
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/list",
            "params": {},
        })
        self.tools = tools_resp.get("result", {}).get("tools", [])
        logger.info(f"[MCP] Tools: {[t['name'] for t in self.tools]}")

    def call_tool(self, name: str, arguments: dict) -> str:
        """Call an MCP tool and return the text result."""
        clean_args = {k: v for k, v in arguments.items() if v is not None}
        resp = self._post({
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {"name": name, "arguments": clean_args},
        })
        if resp.get("error"):
            err = resp["error"]
            return f"MCP error {err.get('code')}: {err.get('message')}"
        content = resp.get("result", {}).get("content", [])
        texts = []
        for item in content:
            if isinstance(item, dict):
                texts.append(item.get("text", str(item)))
            else:
                texts.append(str(item))
        return "\n".join(texts) if texts else str(resp.get("result", ""))

    def get_openai_tools(self) -> list:
        """Convert MCP tools to OpenAI function-calling format."""
        result = []
        for tool in self.tools:
            schema = tool.get("inputSchema", {})
            params = {k: v for k, v in schema.items() if k != "$schema"}
            result.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": params,
                },
            })
        return result


# ─── LLM Client ───────────────────────────────────────────────────────────────

class LLMClient:
    """Direct OpenRouter API client."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def chat(self, messages: list, tools: Optional[list] = None) -> dict:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0
        }
        if tools:
            payload["tools"] = tools

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://bytebell.ai",
            "X-Title": "ByteBell Small-Eval Benchmark",
        }
        t0 = time.perf_counter()
        resp = requests.post(OPENROUTER_BASE_URL, json=payload,
                             headers=headers, timeout=120)
        resp.raise_for_status()
        elapsed = round(time.perf_counter() - t0, 1)
        data = resp.json()
        usage = data.get("usage", {})
        logger.info(
            f"[LLM] {self.model} replied in {elapsed}s | "
            f"prompt={usage.get('prompt_tokens', '?')} "
            f"completion={usage.get('completion_tokens', '?')}"
        )
        return data


# ─── Agent ────────────────────────────────────────────────────────────────────

class AgentTimeoutError(TimeoutError):
    pass


def run_agent(
    llm: LLMClient,
    mcp: MCPClient,
    question: str,
    max_steps: int = 25,
    wall_timeout: int = 600,
) -> tuple:
    """
    Agentic tool-calling loop.
    Returns (answer, tool_records, steps, total_input_tokens, total_output_tokens).
    """
    system_prompt = (
        f"## MCP Server Instructions\n\n{mcp.server_instructions}"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]

    tools = mcp.get_openai_tools()
    tool_records: list[ToolCallRecord] = []
    total_input = 0
    total_output = 0
    steps = 0
    wall_start = time.perf_counter()

    def _check_wall():
        if wall_timeout and (time.perf_counter() - wall_start) > wall_timeout:
            raise AgentTimeoutError(
                f"Wall-clock timeout ({wall_timeout}s) exceeded after {steps} steps"
            )

    for step in range(max_steps):
        steps += 1
        _check_wall()

        logger.info(
            f"[AGENT] Step {step + 1}/{max_steps} | "
            f"wall={round(time.perf_counter() - wall_start, 1)}s | "
            f"tokens_so_far={total_input + total_output}"
        )

        resp = llm.chat(messages, tools=tools)
        choice = resp.get("choices", [{}])[0]
        message = choice.get("message", {})
        finish_reason = choice.get("finish_reason", "")

        usage = resp.get("usage", {})
        total_input += usage.get("prompt_tokens", 0)
        total_output += usage.get("completion_tokens", 0)

        tool_calls = message.get("tool_calls")
        if not tool_calls or finish_reason == "stop":
            answer = message.get("content", "") or ""
            return answer, tool_records, steps, total_input, total_output

        messages.append(message)

        parsed = []
        for tc in tool_calls:
            fn = tc.get("function", {})
            name = fn.get("name", "")
            try:
                args = json.loads(fn.get("arguments", "{}"))
            except json.JSONDecodeError:
                args = {}
            parsed.append((tc.get("id", ""), name, args))

        logger.info(f"[TOOLS] Calling {len(parsed)} tool(s): {[n for _, n, _ in parsed]}")

        remaining = (wall_timeout - (time.perf_counter() - wall_start)) if wall_timeout else None
        tool_timeout = max(remaining, 10) if remaining is not None else None

        results_map = {}
        done_set = set()

        def _exec(tc_id, tool_name, tool_args):
            t0 = time.perf_counter()
            text = mcp.call_tool(tool_name, tool_args)
            return tc_id, tool_name, tool_args, text, round(time.perf_counter() - t0, 3)

        with ThreadPoolExecutor(max_workers=min(len(parsed), 8)) as pool:
            futures = {pool.submit(_exec, i, n, a): i for i, n, a in parsed}
            try:
                for future in as_completed(futures, timeout=tool_timeout):
                    tc_id, tool_name, tool_args, text, elapsed = future.result()
                    results_map[tc_id] = (tool_name, tool_args, text, elapsed)
                    done_set.add(future)
                    logger.info(f"[TOOLS] {tool_name} done in {elapsed}s")
            except TimeoutError:
                for f in futures:
                    if f not in done_set:
                        f.cancel()
                raise AgentTimeoutError("Tool execution timed out")

        for tc_id, name, args in parsed:
            _, _, text, elapsed = results_map[tc_id]
            preview = text[:500] + ("..." if len(text) > 500 else "")
            tool_records.append(ToolCallRecord(
                tool_name=name,
                arguments=args,
                result_preview=preview,
                full_result=text,
                latency_seconds=elapsed,
            ))
            messages.append({
                "role": "tool",
                "tool_call_id": tc_id,
                "content": text,
            })

    # Max steps reached — request a final answer
    logger.info("[AGENT] Max steps reached — requesting final answer")
    messages.append({
        "role": "user",
        "content": "You have reached the maximum number of tool calls. "
                   "Please provide your final answer now based on what you have found.",
    })
    resp = llm.chat(messages, tools=None)
    choice = resp.get("choices", [{}])[0]
    message = choice.get("message", {})
    usage = resp.get("usage", {})
    total_input += usage.get("prompt_tokens", 0)
    total_output += usage.get("completion_tokens", 0)
    answer = message.get("content", "") or ""
    return answer, tool_records, steps, total_input, total_output


# ─── Helpers ──────────────────────────────────────────────────────────────────

def sanitize_for_filename(s: str) -> str:
    """Make a string safe for use in a filename."""
    return s.replace("/", "_").replace(":", "_").replace(" ", "_").replace(".", "-")


def load_questions(questions_dir: Path) -> list:
    """
    Scan questions_dir for sub-directories that contain a question.json.
    Returns list of (q_id, q_dir, question_data) tuples, sorted by name.
    """
    entries = []
    if not questions_dir.is_dir():
        return entries
    for q_dir in sorted(questions_dir.iterdir()):
        if not q_dir.is_dir():
            continue
        q_file = q_dir / "question.json"
        if not q_file.exists():
            logger.warning(f"Skipping {q_dir.name} — no question.json")
            continue
        try:
            with open(q_file) as f:
                data = json.load(f)
        except Exception as e:
            logger.warning(f"Skipping {q_dir.name} — cannot parse question.json: {e}")
            continue
        q_id = data.get("id", q_dir.name)
        entries.append((q_id, q_dir, data))
    return entries


# ─── Worker ───────────────────────────────────────────────────────────────────

def run_one(
    thread_id: int,
    q_id: str,
    question_text: str,
    mcp_url: str,
    api_key: str,
    model: str,
    max_steps: int,
    mcp_timeout: int,
    wall_timeout: int,
    max_retries: int = MAX_RETRIES,
) -> dict:
    """Run one question through MCP + LLM with retries. Returns a result dict."""
    last_error = ""

    for attempt in range(1, max_retries + 1):
        if attempt > 1:
            logger.info(f"[T{thread_id}] Retry {attempt}/{max_retries} — {q_id}")

        logger.info(
            f"[T{thread_id}] Starting {q_id}: {question_text[:70].rstrip()}..."
        )
        t0 = time.perf_counter()

        try:
            mcp = MCPClient(mcp_url, timeout=mcp_timeout)
            mcp.initialize()
            llm = LLMClient(api_key, model)
        except Exception as e:
            last_error = f"Init failed: {type(e).__name__}: {e}"
            logger.error(f"[T{thread_id}] INIT FAILED {q_id} | attempt {attempt} | {last_error}")
            time.sleep(min(attempt * 2, 10))
            continue

        try:
            answer, tool_records, steps, inp_tok, out_tok = run_agent(
                llm, mcp, question_text,
                max_steps=max_steps,
                wall_timeout=wall_timeout,
            )
            elapsed = round(time.perf_counter() - t0, 2)
            logger.info(
                f"[T{thread_id}] Done {q_id} | {elapsed}s | "
                f"{len(tool_records)} tools | {inp_tok + out_tok} tokens"
            )
            return {
                "status": "success",
                "answer": answer,
                "latency_seconds": elapsed,
                "tool_calls_count": len(tool_records),
                "tool_calls": [asdict(r) for r in tool_records],
                "agent_steps": steps,
                "input_tokens": inp_tok,
                "output_tokens": out_tok,
                "total_tokens": inp_tok + out_tok,
                "error": "",
            }

        except AgentTimeoutError as e:
            elapsed = round(time.perf_counter() - t0, 2)
            last_error = f"AgentTimeoutError: {e}"
            logger.error(f"[T{thread_id}] WALL TIMEOUT {q_id} | {elapsed}s")
            return {
                "status": "timeout",
                "answer": "",
                "latency_seconds": elapsed,
                "tool_calls_count": 0,
                "tool_calls": [],
                "agent_steps": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "error": last_error,
            }

        except Exception as e:
            elapsed = round(time.perf_counter() - t0, 2)
            last_error = f"{type(e).__name__}: {e}"
            logger.error(
                f"[T{thread_id}] FAILED {q_id} | attempt {attempt} | {elapsed}s | {last_error}"
            )
            time.sleep(min(attempt * 2, 10))
            continue

    logger.error(f"[T{thread_id}] GAVE UP {q_id} after {max_retries} attempts")
    return {
        "status": "error",
        "answer": "",
        "latency_seconds": 0.0,
        "tool_calls_count": 0,
        "tool_calls": [],
        "agent_steps": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "error": f"Failed after {max_retries} retries: {last_error}",
    }


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Generate answer_{model_name}_{mcp_version}.json for every question "
            "in results/small-eval/ using MCP + OpenRouter. Tool calls are explicitly "
            "saved. Only the question field is sent — no metadata in the prompt."
        )
    )
    parser.add_argument(
        "--model_name", "-m", required=True,
        help="OpenRouter model ID, e.g. 'anthropic/claude-sonnet-4-5'",
    )
    parser.add_argument(
        "--mcp_version", required=True,
        help="MCP version label used in output filename, e.g. 'gitnexus-v1'",
    )
    parser.add_argument(
        "--mcp_url",
        default=None,
        help="Full MCP server URL (incl. any API key param). Falls back to MCP_URL env var.",
    )
    parser.add_argument(
        "--api_key",
        default=None,
        help="OpenRouter API key. Falls back to OPENROUTER_API_KEY env var.",
    )
    parser.add_argument(
        "--questions_dir", "-q",
        default=str(DEFAULT_QUESTIONS_DIR),
        help=f"Directory containing question sub-folders (default: {DEFAULT_QUESTIONS_DIR})",
    )
    parser.add_argument(
        "--threads", "-t", type=int, default=2,
        help="Concurrent worker threads (default: 2)",
    )
    parser.add_argument(
        "--max_steps", type=int, default=25,
        help="Max agent steps per question (default: 25)",
    )
    parser.add_argument(
        "--timeout", type=int, default=120,
        help="Per-MCP-call read timeout in seconds (default: 120)",
    )
    parser.add_argument(
        "--wall_timeout", type=int, default=600,
        help="Max wall-clock seconds per question (default: 600)",
    )
    parser.add_argument(
        "--skip_existing", action="store_true", default=True,
        help="Skip questions that already have an output file (default: True)",
    )
    parser.add_argument(
        "--no_skip_existing", dest="skip_existing", action="store_false",
        help="Re-run and overwrite even if output file already exists",
    )
    args = parser.parse_args()

    load_dotenv()

    api_key = args.api_key or os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        logger.error("No OpenRouter API key. Set OPENROUTER_API_KEY or use --api_key")
        sys.exit(1)

    mcp_url = args.mcp_url or os.getenv("MCP_URL", "")
    if not mcp_url:
        logger.error("No MCP URL. Set MCP_URL env var or use --mcp_url")
        sys.exit(1)

    model = args.model_name
    mcp_version = args.mcp_version
    safe_model = sanitize_for_filename(model)
    safe_mcp = sanitize_for_filename(mcp_version)
    output_filename = f"answer_{safe_model}_{safe_mcp}.json"

    questions_dir = Path(args.questions_dir)
    if not questions_dir.is_dir():
        logger.error(f"Questions directory not found: {questions_dir}")
        sys.exit(1)

    all_questions = load_questions(questions_dir)
    if not all_questions:
        logger.error(f"No valid question.json files found in {questions_dir}")
        sys.exit(1)

    pending = []
    skipped = 0
    for q_id, q_dir, data in all_questions:
        out_file = q_dir / output_filename
        if args.skip_existing and out_file.exists():
            logger.info(f"  Skipping {q_id} — {output_filename} already exists")
            skipped += 1
        else:
            pending.append((q_id, q_dir, data))

    logger.info("=" * 60)
    logger.info("SMALL-EVAL ANSWER GENERATOR")
    logger.info("=" * 60)
    logger.info(f"  Model:           {model}")
    logger.info(f"  MCP version:     {mcp_version}")
    logger.info(f"  Output file:     {output_filename}")
    logger.info(f"  Questions dir:   {questions_dir}")
    logger.info(f"  Total found:     {len(all_questions)}")
    logger.info(f"  Already done:    {skipped}")
    logger.info(f"  To process:      {len(pending)}")
    logger.info(f"  Threads:         {args.threads}")
    logger.info(f"  Max steps:       {args.max_steps}")
    logger.info(f"  MCP timeout:     {args.timeout}s")
    logger.info(f"  Wall timeout:    {args.wall_timeout}s")
    logger.info(f"  MCP endpoint:    {mcp_url.split('?')[0]}")
    logger.info("=" * 60)

    if not pending:
        logger.info("Nothing to do — all questions already answered.")
        sys.exit(0)

    total = len(pending)
    completed = 0
    errors = 0
    t_start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=args.threads) as pool:
        future_to_item = {}
        for idx, (q_id, q_dir, data) in enumerate(pending):
            q_text = data.get("question", "")
            fut = pool.submit(
                run_one,
                idx % args.threads,
                q_id, q_text,
                mcp_url, api_key, model,
                args.max_steps, args.timeout, args.wall_timeout,
            )
            future_to_item[fut] = (q_id, q_dir, data)

        for future in as_completed(future_to_item):
            q_id, q_dir, q_data = future_to_item[future]
            try:
                result = future.result()
            except Exception as e:
                logger.error(f"Unhandled exception for {q_id}: {type(e).__name__}: {e}")
                result = {
                    "status": "error",
                    "answer": "",
                    "latency_seconds": 0.0,
                    "tool_calls_count": 0,
                    "tool_calls": [],
                    "agent_steps": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "error": f"Unhandled: {type(e).__name__}: {e}",
                }

            output = {
                "question_id": q_id,
                "answer": result["answer"],
                "tool_calls": result["tool_calls"],  # explicit full tool call records
                "metadata": {
                    "model": model,
                    "mcp_version": mcp_version,
                    "status": result["status"],
                    "time_taken_seconds": result["latency_seconds"],
                    "tool_calls_count": result["tool_calls_count"],
                    "agent_steps": result["agent_steps"],
                    "tokens": {
                        "input": result["input_tokens"],
                        "output": result["output_tokens"],
                        "total": result["total_tokens"],
                    },
                    "error": result["error"],
                },
            }

            out_file = q_dir / output_filename
            try:
                with open(out_file, "w") as f:
                    json.dump(output, f, indent=2, default=str)
                logger.info(f"  Saved → {out_file}")
            except Exception as e:
                logger.error(f"Could not write {out_file}: {e}")

            completed += 1
            if result["status"] != "success":
                errors += 1

            logger.info(
                f"  [{completed}/{total}] {q_id} — {result['status']} "
                f"({result['latency_seconds']:.1f}s, {result['total_tokens']} tokens, "
                f"{result['tool_calls_count']} tool calls)"
            )

    elapsed = round(time.perf_counter() - t_start, 1)
    success = completed - errors
    logger.info("=" * 60)
    logger.info(f"DONE — {success}/{total} succeeded, {errors} errors, {elapsed}s total")
    logger.info("=" * 60)

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
