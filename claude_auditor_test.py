#!/usr/bin/env python3
"""
claude_auditor_test.py
======================
Autonomous Claude Code driver for SWE-bench style evaluation tasks.

Flow (per task)
---------------
1. Load tasks from TASKS_FILE and slice with TASK_SLICE.
2. Start a fresh OTel receiver (kills any existing process on :4318).
3. For each task:
   a. Create output folder: OUT_DIR/<instance_id>/{output,telemetry,logs}/
   b. Snapshot existing OTel log files.
   c. Build the prompt from the task's `question` field (answer/patch fields stripped).
   d. Run `claude` inside dataset/Astropy/<base_commit>/ with the configured system prompt.
   e. Wait for OTel flush, collect new session files into telemetry/.
   f. Write run_manifest.json.
   g. Kill Claude session (print mode exits naturally; PTY is terminated).
4. After all tasks, kill the OTel receiver.

Configuration
-------------
Edit the constants in the "── Configuration ──" block below.
"""

import argparse
import json
import logging
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time

# Thread-local model config — lets parallel model threads each see their own
# MODEL_PROVIDER / OPENROUTER_MODEL / CLI_BACKEND without clobbering each other.
_thread_local = threading.local()

def _tl(name: str):
    """Return the thread-local override for `name` if set, else the module global."""
    return getattr(_thread_local, name, globals()[name])
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from tqdm import tqdm

# ── Configuration ─────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent
ASTROPY_DIR  = PROJECT_ROOT / "dataset" / "Astropy"   # commit checkout dirs live here
OTEL_LOGS    = PROJECT_ROOT / "logs"   # receiver writes here (sibling of otel-receiver.py)
RECEIVER_PY  = "otel-receiver.py"
CLAUDE_BIN   = shutil.which("claude") or "/Users/deadbytes/.local/bin/claude"

# OTel env vars injected directly into every Claude subprocess.
# The commit checkout dirs have no .claude/settings.json, so we cannot rely on
# Claude discovering them via the project-root walk — we must pass them explicitly.
OTEL_ENV = {
    "CLAUDE_CODE_ENABLE_TELEMETRY":     "1",
    "OTEL_METRICS_EXPORTER":            "otlp",
    "OTEL_LOGS_EXPORTER":               "otlp",
    "OTEL_EXPORTER_OTLP_PROTOCOL":      "http/json",
    "OTEL_EXPORTER_OTLP_ENDPOINT":      "http://localhost:4318",
    "OTEL_METRIC_EXPORT_INTERVAL":      "10000",
    "OTEL_LOGS_EXPORT_INTERVAL":        "5000",
    "OTEL_LOG_USER_PROMPTS":            "1",
    "OTEL_LOG_TOOL_DETAILS":            "1",
    "OTEL_METRICS_INCLUDE_SESSION_ID":  "true",
    "OTEL_METRICS_INCLUDE_VERSION":     "true",
    "OTEL_METRICS_INCLUDE_ACCOUNT_UUID":"true",
}

# Input: path to the tasks JSON
TASKS_FILE = PROJECT_ROOT / "results_swe_bench" / "astropy_tasks.json"

# Slice string — controls which tasks to run. Examples:
#   ":"    → all tasks
#   "0:3"  → first 3  (indices 0, 1, 2)
#   ":5"   → first 5
#   "3:"   → everything from index 3 onward
#   "2:4"  → indices 2 and 3
TASK_SLICE = ":3"

# ── Model provider ────────────────────────────────────────────────────────────
# "anthropic"   — use Anthropic-hosted Claude models (default)
# "openrouter"  — use any OpenRouter model (open-source or otherwise)
MODEL_PROVIDER = "openrouter"

# Anthropic model (used when MODEL_PROVIDER == "anthropic"). Options:
#   "claude-opus-4-6"           — most capable
#   "claude-sonnet-4-6"         — balanced (default)
#   "claude-haiku-4-5-20251001" — fastest / cheapest
MODEL = "claude-sonnet-4-6"

# OpenRouter settings (used when MODEL_PROVIDER == "openrouter").
#   OPENROUTER_API_KEY  — your OpenRouter API key (sk-or-...)
#   OPENROUTER_MODEL    — full model slug as listed on openrouter.ai
#   Note: uses ANTHROPIC_BASE_URL redirect, no "openrouter/" prefix needed
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_MODEL   = "qwen/qwen3.6-plus:free"

# "print"       — subprocess + `claude -p` (non-interactive, exits when done)
# "interactive" — pexpect PTY (interactive TUI, useful for auto-approval loops)
MODE = "print"

# ── CLI backend ───────────────────────────────────────────────────────────────
# "claude" — Claude Code CLI  (`claude --print …`)              OTel supported
# "kilo"   — Kilo CLI         (`kilo run --auto --json …`)      metrics via JSON
# "cline"  — Cline CLI        (`cline --no-interactive -y …`)   metrics via JSON
CLI_BACKEND = "claude"   # overridden by --cli-backend CLI arg

# ── Eval mode ─────────────────────────────────────────────────────────────────
# Set EVAL_MODE = True (or pass --eval) to iterate over EVAL_MODELS sequentially,
# running the full pipeline (launch → collect → enrich) for each model and
# printing a combined summary table at the end.
EVAL_MODE            = False   # overridden by --eval CLI flag
EVAL_PARALLEL_MODELS = False   # overridden by --eval-parallel; runs kilo models concurrently

# Prompt-caching policy per backend/provider (from OpenRouter docs):
#   "claude_code" — Claude Code CLI injects cache_control on system prompts
#                   automatically when calling any Anthropic-compatible endpoint
#                   (including OpenRouter).  No extra config needed from our side.
#   "auto"        — Provider handles caching with no configuration required
#                   (OpenAI, DeepSeek, Grok, Moonshot, Groq, Gemini 2.5).
#
# Rule: always pair Anthropic Claude models with backend="claude" so that
# prompt caching is applied without manual intervention.
EVAL_MODELS = [
    # ── Anthropic via OpenRouter — claude backend for native prompt caching ──
    {"provider": "openrouter", "model": "anthropic/claude-sonnet-4.6",      "backend": "kilo", "cache": "claude_code"},
    {"provider": "openrouter", "model": "anthropic/claude-opus-4.6",        "backend": "kilo", "cache": "claude_code"},
    # ── NO CACHE MODELS : Qwen & GEMMA ─────────────────────────────────────────────────────────────────
    {"provider": "openrouter", "model": "qwen/qwen3.6-plus:free",           "backend": "kilo",   "cache": "auto"},
    {"provider": "openrouter", "model": "google/gemma-4-31b-it",             "backend": "kilo",   "cache": "auto"},

    # # ── OpenAI — automatic caching (min 1 024 tokens) ────────────────────────
    {"provider": "openrouter", "model": "openai/gpt-5.4-mini",                    "backend": "kilo",   "cache": "auto"},
    {"provider": "openrouter", "model": "openai/gpt-5.4-nano",                    "backend": "kilo",   "cache": "auto"},

    # ── DeepSeek — automatic caching ─────────────────────────────────────────
    # {"provider": "openrouter", "model": "deepseek/deepseek-3.5-seq2seq:latest",   "backend": "kilo",   "cache": "auto"},
]

# ── Run-mode ──────────────────────────────────────────────────────────────────
# "raw" — Claude reads from the local Astropy checkout (original behaviour)
# "mcp" — Claude runs in an empty workspace and must use ByteBell MCP tools
RUN_MODE = "raw"   # overridden by --run-mode CLI arg


def _active_out_dir() -> Path:
    """
    Compute the output root from the active backend / provider / model / mode / run-mode.
    Called at runtime so CLI overrides are respected.
    Pattern: results_swe_bench/auto_run_on_<run_mode>[_<backend>]_<model>[_<mode>]
    """
    model   = _tl("OPENROUTER_MODEL") if _tl("MODEL_PROVIDER") == "openrouter" else _tl("MODEL")
    safe    = model.replace("/", "_").replace(" ", "_")
    backend = f"{_tl('CLI_BACKEND')}_" if _tl("CLI_BACKEND") != "claude" else ""
    base    = f"{RUN_MODE}_{backend}{safe}"
    slug    = base if MODE == "print" else f"{base}_{MODE}"
    return PROJECT_ROOT / "results_swe_bench" / f"auto_run_on_{slug}"

# Empty directory used as cwd for MCP runs so Claude has no local repo context
MCP_WORKSPACE = PROJECT_ROOT / "mcp_workspace"

# How long to wait (seconds) for Claude to finish in interactive PTY mode
INTERACTIVE_TIMEOUT = 1000

# Seconds to wait after Claude exits for OTel to flush its buffers
OTEL_FLUSH_WAIT = 8

# How many tasks to run in parallel (1 = sequential).
# Each task is a separate `claude --print` subprocess with its own OTel session.
# Session IDs are locked to tasks within the first OTEL_SESSION_LOCK_WAIT seconds,
# so parallel runs never mix each other's telemetry files.
PARALLEL_WORKERS = 1

# How long (seconds) to poll for the task's OTel session UUID to appear before giving up
OTEL_SESSION_LOCK_WAIT = 20

# ── System prompt ─────────────────────────────────────────────────────────────
# Injected via `--system-prompt` on every Claude invocation.
# The literal placeholder {answer_path} is filled in per-task at runtime.

MCP_SYSTEM_PROMPT_TEMPLATE = """\
Use the ByteBell MCP tools to answer the question. Write your answer to `{answer_path}` as JSON:

{{"answer": "your answer here"}}

Question:

{question}
"""

SYSTEM_PROMPT_TEMPLATE = """\
## Ground Rules

**YOU MUST:**
- Read files directly from the locally cloned repository on disk at the base commit path
- Form your answer entirely from first-principles evidence gathered in this session

**YOU MUST NOT:**
- Use web search of any kind
- Call any git CLI commands (no `git log`, `git blame`, `git diff`, `git show`, etc.)
- Call any GitHub, GitLab, or any other remote REST/GraphQL API
- Read any file inside an `answers/`, `results/`, `results_swe_bench/`, `expected/`, \
or `cached/` directory

## Output Format

Write your answer **only** to:

    {answer_path}

The file must be valid JSON with exactly this structure:

{{
  "answer": "<your complete patch or explanation here>"
}}

Do NOT print the answer to the terminal. Only write it to that file.
"""

# ── Logging setup ─────────────────────────────────────────────────────────────

LOG_FMT  = "%(asctime)s  %(levelname)-8s  %(message)s"
DATE_FMT = "%H:%M:%S"


class _ColorFormatter(logging.Formatter):
    """ANSI-colored console formatter — colors by log level, no external deps."""
    _LEVEL_COLORS = {
        logging.DEBUG:    "\033[36m",    # cyan
        logging.INFO:     "\033[32m",    # green
        logging.WARNING:  "\033[33m",    # yellow
        logging.ERROR:    "\033[31m",    # red
        logging.CRITICAL: "\033[1;31m",  # bold red
    }
    _TS_COLOR    = "\033[2;37m"   # dim white  — timestamp
    _MSG_COLOR   = "\033[97m"     # bright white — message
    _RESET       = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        lc   = self._LEVEL_COLORS.get(record.levelno, "")
        lvl  = f"{lc}{record.levelname:<8}{self._RESET}"
        ts   = f"{self._TS_COLOR}{self.formatTime(record, self.datefmt)}{self._RESET}"
        msg  = f"{self._MSG_COLOR}{record.getMessage()}{self._RESET}"
        return f"{ts}  {lvl}  {msg}"


log = logging.getLogger("auditor")
log.setLevel(logging.DEBUG)

# Console handler — colored INFO+ output
_console = logging.StreamHandler(sys.stdout)
_console.setLevel(logging.INFO)
_console.setFormatter(_ColorFormatter(datefmt=DATE_FMT))
log.addHandler(_console)


def _make_task_logger(instance_id: str, logs_dir: Path) -> tuple:
    """
    Create a task-specific child logger that:
      - writes DEBUG+ to logs_dir/auditor.log (task-isolated file)
      - propagates INFO+ to the parent 'auditor' console handler

    Using a child logger (auditor.<instance_id>) means parallel tasks never
    write to each other's log files.  Returns (logger, file_handler).
    """
    task_log = logging.getLogger(f"auditor.{instance_id}")
    task_log.setLevel(logging.DEBUG)
    # Remove any stale handlers from a prior run of the same instance_id
    task_log.handlers.clear()
    log_file = logs_dir / "auditor.log"
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(LOG_FMT, datefmt=DATE_FMT))
    task_log.addHandler(fh)
    task_log.debug("File log opened: %s", log_file)
    return task_log, fh


def _close_task_logger(task_log: logging.Logger, fh: logging.FileHandler) -> None:
    fh.flush()
    fh.close()
    task_log.removeHandler(fh)


# ── Helpers ───────────────────────────────────────────────────────────────────

def parse_slice(spec: str) -> slice:
    """
    Parse a Python-style slice string into a slice object.
    Examples: "0:3" → slice(0,3), ":5" → slice(None,5), "3:" → slice(3,None), ":" → slice(None,None)
    """
    parts = spec.split(":")
    start = int(parts[0]) if parts[0].strip() else None
    stop  = int(parts[1]) if len(parts) > 1 and parts[1].strip() else None
    return slice(start, stop)


def port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def kill_otel_receiver() -> None:
    """Kill whatever process is bound to port 4318 (the OTel receiver)."""
    try:
        result = subprocess.run(["lsof", "-ti", "tcp:4318"], capture_output=True, text=True)
        proc_ids = result.stdout.strip().split()
        if not proc_ids:
            log.info("No process found on :4318 — nothing to kill.")
            return
        for proc_id in proc_ids:
            os.kill(int(proc_id), signal.SIGKILL)
            log.info("OTel receiver (PID=%s) killed.", proc_id)
    except Exception as exc:
        log.error("Could not kill OTel receiver: %s", exc)


def start_otel_receiver() -> None:
    """Start a fresh otel-receiver.py. Kills any existing process on :4318 first."""
    if port_in_use(4318):
        log.info("Port 4318 already in use — killing existing process first.")
        kill_otel_receiver()
        time.sleep(0.5)
    log.info("Starting OTel receiver (%s) …", RECEIVER_PY)
    proc = subprocess.Popen(
        [sys.executable, str(RECEIVER_PY)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1.5)
    if port_in_use(4318):
        log.info("OTel receiver started — PID=%d, listening on :4318", proc.pid)
    else:
        log.warning("OTel receiver did not start in time — telemetry may be missing.")


def snapshot_logs() -> set:
    """Return the set of existing OTel log filenames (basenames only)."""
    if not OTEL_LOGS.exists():
        return set()
    names = {f.name for f in OTEL_LOGS.iterdir() if f.is_file()}
    log.debug("OTel snapshot: %d existing file(s).", len(names))
    return names


def collect_new_session_files(before: set, telemetry_dir: Path) -> dict:
    """
    Diff current OTel logs against `before`, copy new ones to telemetry_dir.
    Returns {session_id: [copied Path, …]}.
    """
    if not OTEL_LOGS.exists():
        return {}
    after = {f.name: f for f in OTEL_LOGS.iterdir() if f.is_file()}
    new_names = set(after) - before
    log.debug("%d new OTel file(s) found.", len(new_names))

    sessions: dict = {}
    for name in new_names:
        m = re.match(r"^([a-f0-9\-]{36})_(events|metrics)\.json$", name)
        if not m:
            log.debug("Skipping non-session file: %s", name)
            continue
        sid = m.group(1)
        dst = telemetry_dir / name
        shutil.copy2(after[name], dst)
        sessions.setdefault(sid, []).append(dst)
        log.info("  Copied OTel log → telemetry/%s", name)
    return sessions


def wait_for_session_id(before, task_log):
    deadline = time.monotonic() + OTEL_SESSION_LOCK_WAIT
    task_log.debug("Polling for OTel session UUID (up to %d s)...", OTEL_SESSION_LOCK_WAIT)
    while time.monotonic() < deadline:
        if OTEL_LOGS.exists():
            for f in OTEL_LOGS.iterdir():
                if f.name not in before:
                    m = re.match(r"^([a-f0-9-]{36})_events[.]json$", f.name)
                    if m:
                        task_log.info("OTel session UUID locked: %s", m.group(1))
                        return m.group(1)
        time.sleep(0.5)
    task_log.warning("Timed out -- falling back to snapshot diff.")
    return None


def copy_session_files(session_id, telemetry_dir, task_log):
    copied = []
    if not OTEL_LOGS.exists() or not session_id:
        return copied
    for f in OTEL_LOGS.iterdir():
        if f.name.startswith(session_id):
            dst = telemetry_dir / f.name
            shutil.copy2(f, dst)
            copied.append(dst)
            task_log.info("  Copied OTel log -> telemetry/%s", f.name)
    return copied

def build_mcp_prompt(task: dict, answer_path: Path) -> str:
    """
    Build the MCP-mode user prompt. Claude receives the bare question and must
    answer using only ByteBell MCP tools — no local files.
    """
    return (
        f"{task['question']}\n\n"
        f"---\n"
        f"Write your answer to: {answer_path}\n"
        f"Format: {{\"answer\": \"your answer\"}}\n"
    )


def build_prompt(task: dict, answer_path: Path) -> str:
    """
    Build the user prompt from the task's question field only.
    No other task fields are included.
    """
    return (
        f"{task['question']}\n\n"
        f"---\n"
        f"Write your answer to: {answer_path}\n"
        f"Format: {{\"answer\": \"your patch / explanation\"}}\n"
    )


def _effective_model() -> str:
    """Return the model string for --model, formatted per CLI backend and provider."""
    backend  = _tl("CLI_BACKEND")
    provider = _tl("MODEL_PROVIDER")
    or_model = _tl("OPENROUTER_MODEL")
    model    = _tl("MODEL")
    if backend == "kilo":
        if provider == "openrouter":
            return f"openrouter/{or_model}"
        return f"anthropic/{model}"
    # claude / cline: OpenRouter via ANTHROPIC_BASE_URL redirect, slug as-is
    if provider == "openrouter":
        return or_model
    return model


def _provider_env() -> dict:
    """Extra env vars required by the active provider."""
    if _tl("MODEL_PROVIDER") == "openrouter":
        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY is not set but MODEL_PROVIDER='openrouter'")
        return {
            "OPENROUTER_API_KEY":  OPENROUTER_API_KEY,
            "ANTHROPIC_BASE_URL":  "https://openrouter.ai/api",
            "ANTHROPIC_AUTH_TOKEN": OPENROUTER_API_KEY,
            "ANTHROPIC_API_KEY":   "",
        }
    return {}


def launch_claude_print(prompt, system_prompt, cwd, task_log):
    model = _effective_model()
    task_log.info("Launching Claude (print / provider=%s / model=%s) ...", _tl("MODEL_PROVIDER"), model)
    task_log.debug("CWD: %s", cwd)
    proc = subprocess.Popen(
        [CLAUDE_BIN, "--print", "--dangerously-skip-permissions",
         "--model", model, "--system-prompt", system_prompt, prompt],
        cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, env={**os.environ, **OTEL_ENV, **_provider_env()},
    )
    task_log.debug("Claude PID: %d", proc.pid)
    return proc


def _launch_kilo(prompt, system_prompt, cwd, task_log):
    """Launch Kilo CLI in autonomous JSON mode.

    Kilo has no --system-prompt flag; we prepend the system prompt to the
    user message.  The --json flag makes Kilo emit NDJSON lines to stdout
    that include per-message token counts and cumulative cost — used later
    by _parse_kilo_metrics() to populate run_manifest.json.
    """
    kilo_bin = shutil.which("kilo") or "kilo"
    model    = _effective_model()
    task_log.info("Launching Kilo (auto/format=json / provider=%s / model=%s) ...", _tl("MODEL_PROVIDER"), model)
    task_log.debug("CWD: %s", cwd)

    combined = f"[SYSTEM]\n{system_prompt}\n[/SYSTEM]\n\n{prompt}"

    env = {**os.environ}
    if _tl("MODEL_PROVIDER") == "openrouter" and OPENROUTER_API_KEY:
        env["OPENROUTER_API_KEY"] = OPENROUTER_API_KEY

    proc = subprocess.Popen(
        [kilo_bin, "run", "--auto", "--format", "json", "--model", model, combined],
        cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, env=env,
    )
    task_log.debug("Kilo PID: %d", proc.pid)
    return proc


def launch_agent(prompt, system_prompt, cwd, task_log):
    """Dispatch to the correct CLI backend."""
    if _tl("CLI_BACKEND") == "kilo":
        return _launch_kilo(prompt, system_prompt, cwd, task_log)
    return launch_claude_print(prompt, system_prompt, cwd, task_log)


def _parse_kilo_metrics(stdout_text: str) -> dict:
    """Extract token/cost metrics from kilo --format json NDJSON stdout.

    Kilo emits one JSON object per line.  Metrics are in "step_finish" events:
      {"type":"step_finish","part":{"cost":<n>,"tokens":{"input":<n>,"output":<n>,
        "reasoning":<n>,"cache":{"read":<n>,"write":<n>}}}}
    Sum across all step_finish events (one per agent turn / API call).
    """
    total_input = total_output = total_reasoning = total_cache_read = total_cache_write = 0
    total_cost  = 0.0
    n_steps     = 0

    for line in stdout_text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        if not isinstance(obj, dict) or obj.get("type") != "step_finish":
            continue
        part  = obj.get("part", {})
        toks  = part.get("tokens", {})
        cache = toks.get("cache", {})
        total_input       += int(toks.get("input",     0) or 0)
        total_output      += int(toks.get("output",    0) or 0)
        total_reasoning   += int(toks.get("reasoning", 0) or 0)
        total_cache_read  += int(cache.get("read",     0) or 0)
        total_cache_write += int(cache.get("write",    0) or 0)
        total_cost        += float(part.get("cost",    0) or 0)
        n_steps           += 1

    if n_steps == 0:
        return {}

    return {
        "total_input_tokens":          total_input,
        "total_output_tokens":         total_output,
        "total_reasoning_tokens":      total_reasoning,
        "total_cache_read_tokens":     total_cache_read,
        "total_cache_creation_tokens": total_cache_write,
        "total_cost_usd":              round(total_cost, 6),
        "total_api_requests":          n_steps,
    }



def run_interactive_mode(prompt: str, system_prompt: str, cwd: Path) -> str:
    """Drive Claude Code via PTY (pexpect). Returns captured session text."""
    import pexpect

    log.info("Launching Claude (interactive PTY / model=%s) …", MODEL)
    log.debug("CWD: %s", cwd)

    child = pexpect.spawn(
        CLAUDE_BIN,
        args=[
            "--dangerously-skip-permissions",
            "--model", MODEL,
            "--system-prompt", system_prompt,
        ],
        cwd=str(cwd),
        encoding="utf-8",
        timeout=INTERACTIVE_TIMEOUT,
        env={**os.environ, **OTEL_ENV},
    )
    log_buf: list = []
    child.logfile_read = type("_Sink", (), {
        "write": lambda self, s: log_buf.append(s),
        "flush": lambda self: None,
    })()

    log.info("Waiting for Claude interactive prompt …")
    try:
        child.expect(["How can I help", r"❯", pexpect.TIMEOUT], timeout=30)
        log.debug("Ready prompt detected.")
    except pexpect.TIMEOUT:
        log.debug("Startup TIMEOUT — sending task anyway.")

    log.info("Injecting task prompt …")
    child.sendline(prompt)

    while True:
        try:
            idx = child.expect(
                [
                    r"(?i)(allow|approve|yes/no|y/n)",    # 0 — permission prompt
                    r"(?i)(task complete|done|finished)",  # 1 — explicit done marker
                    pexpect.TIMEOUT,                       # 2 — idle for timeout seconds
                    pexpect.EOF,                           # 3 — session ended
                ],
                timeout=30,
            )
        except pexpect.EOF:
            log.info("PTY EOF — session ended.")
            break

        if idx == 0:
            log.info("Permission prompt detected — auto-approving.")
            child.sendline("y")
        elif idx == 1:
            log.info("Task-complete marker detected — closing session.")
            break
        elif idx == 2:
            log.info("No output for 30 s — assuming task complete.")
            break
        elif idx == 3:
            log.info("PTY EOF.")
            break

    child.sendline("exit")
    try:
        child.expect(pexpect.EOF, timeout=10)
    except Exception:
        child.terminate(force=True)

    return "".join(log_buf)


# ── Per-task runner (two phases) ─────────────────────────────────────────────
#
# Phase 1 — serial, called one-at-a-time from main():
#   setup_and_launch()  creates dirs/logger, launches Claude, locks session ID.
#   Returns a context dict passed to finish_task().
#
# Phase 2 — parallel, submitted to ThreadPoolExecutor:
#   finish_task()  waits for the process, collects output + OTel, writes files.

def setup_and_launch(task: dict, task_num: int, total: int) -> dict:
    """
    Serial phase: create output dirs, launch Claude as a background process,
    then block until its OTel session ID appears (so the next task's launch
    won't steal this session).  Returns a context dict for finish_task().
    """
    instance_id  = task["instance_id"]
    base_commit  = task["base_commit"]

    if RUN_MODE == "mcp":
        cwd      = MCP_WORKSPACE
    else:
        cwd      = ASTROPY_DIR
    out_root = _active_out_dir()

    log.info("=" * 70)
    log.info("TASK %d/%d  —  %s  [launching]  mode=%s", task_num, total, instance_id, RUN_MODE)
    log.info("  base_commit : %s", base_commit)
    log.info("=" * 70)

    task_dir      = out_root / instance_id
    answer_path   = task_dir / "answer.json"
    telemetry_dir = task_dir / "telemetry"
    logs_dir      = task_dir / "logs"
    for d in (task_dir, telemetry_dir, logs_dir):
        d.mkdir(parents=True, exist_ok=True)

    task_log, fh = _make_task_logger(instance_id, logs_dir)

    if RUN_MODE == "mcp":
        prompt        = build_mcp_prompt(task, answer_path)
        system_prompt = MCP_SYSTEM_PROMPT_TEMPLATE.format(
            question=task["question"], answer_path=str(answer_path)
        )
    else:
        prompt        = build_prompt(task, answer_path)
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(answer_path=str(answer_path))

    before = snapshot_logs()
    task_log.info("OTel snapshot before launch: %d file(s)", len(before))

    # Launch the configured CLI backend (non-blocking)
    proc = launch_agent(prompt, system_prompt, cwd, task_log)

    # OTel session locking is only meaningful for the claude backend.
    # Kilo/Cline don't emit OTel, so skip the wait entirely.
    session_id = wait_for_session_id(before, task_log) if _tl("CLI_BACKEND") == "claude" else None
    if _tl("CLI_BACKEND") != "claude":
        task_log.info("OTel session tracking skipped (backend=%s).", _tl("CLI_BACKEND"))

    return {
        "task"        : task,
        "task_num"    : task_num,
        "total"       : total,
        "instance_id" : instance_id,
        "base_commit" : base_commit,
        "task_dir"    : task_dir,
        "answer_path" : answer_path,
        "telemetry_dir": telemetry_dir,
        "logs_dir"    : logs_dir,
        "task_log"    : task_log,
        "fh"          : fh,
        "proc"        : proc,
        "session_id"  : session_id,
        "run_start"   : time.monotonic(),
    }


def finish_task(ctx: dict) -> None:
    """
    Parallel phase: wait for the Claude process to finish, save output,
    copy OTel files, and write the run manifest.
    """
    task_log     = ctx["task_log"]
    fh           = ctx["fh"]
    proc         = ctx["proc"]
    session_id   = ctx["session_id"]
    instance_id  = ctx["instance_id"]
    base_commit  = ctx["base_commit"]
    task_dir     = ctx["task_dir"]
    answer_path  = ctx["answer_path"]
    telemetry_dir= ctx["telemetry_dir"]
    logs_dir     = ctx["logs_dir"]
    run_start    = ctx["run_start"]

    try:
        task_log.info("Waiting for Claude to finish …")

        # Stream stdout+stderr to disk line-by-line so the file is visible while the agent runs
        stdout_lines: list[str] = []
        stderr_lines: list[str] = []
        transcript_path = logs_dir / "claude_stdout.txt"

        import threading
        _write_lock = threading.Lock()

        def _stream(stream, accumulator: list[str], log_file):
            for line in stream:
                accumulator.append(line)
                with _write_lock:
                    log_file.write(line)
                    log_file.flush()

        with transcript_path.open("w", encoding="utf-8") as _log_fh:
            t_out = threading.Thread(target=_stream, args=(proc.stdout, stdout_lines, _log_fh), daemon=True)
            t_err = threading.Thread(target=_stream, args=(proc.stderr, stderr_lines, _log_fh), daemon=True)
            t_out.start()
            t_err.start()
            t_out.join()
            t_err.join()
            proc.wait()

        stdout_text = "".join(stdout_lines)
        stderr_text = "".join(stderr_lines)

        elapsed = time.monotonic() - run_start
        if proc.returncode != 0:
            task_log.warning("Claude non-zero exit code %d", proc.returncode)
        else:
            task_log.info("Claude finished in %.1f s.", elapsed)

        # Transcript already written incrementally above
        combined = stderr_text + stdout_text
        task_log.info("Transcript saved → logs/claude_stdout.txt (%d chars)", len(combined))

        # ── OTel (claude backend only) ────────────────────────────────────────
        sessions: dict = {}
        if _tl("CLI_BACKEND") == "claude":
            task_log.info("Waiting %d s for OTel flush …", OTEL_FLUSH_WAIT)
            time.sleep(OTEL_FLUSH_WAIT)
            if session_id:
                copied = copy_session_files(session_id, telemetry_dir, task_log)
                sessions = {session_id: copied} if copied else {}
            else:
                task_log.warning("No session ID — falling back to snapshot diff.")
                sessions = collect_new_session_files(set(), telemetry_dir)
            if not sessions:
                task_log.warning("No OTel session files found for this task.")
            else:
                for sid, files in sessions.items():
                    task_log.info("OTel session: %s (%d file(s))", sid, len(files))

        # ── Kilo JSON metrics ─────────────────────────────────────────────────
        cli_metrics: dict = {}
        if _tl("CLI_BACKEND") == "kilo":
            cli_metrics = _parse_kilo_metrics(stdout_text)
            if cli_metrics:
                task_log.info("Kilo metrics: %s", cli_metrics)
            else:
                task_log.warning("Kilo --json metrics not found in stdout.")

        # Verify answer
        answer_written = answer_path.exists()
        if answer_written:
            try:
                preview = json.loads(answer_path.read_text(encoding="utf-8"), strict=False)
                task_log.info("answer.json written — preview: %s", str(preview)[:200])
            except json.JSONDecodeError as exc:
                task_log.warning("answer.json invalid JSON: %s", exc)
        else:
            task_log.warning("answer.json NOT created at: %s", answer_path)
            task_log.debug("stdout preview:\n%s", combined[:500])
            # ── Fallback: extract answer from kilo text events in stdout ──────
            # Models sometimes print {"answer": "..."} as a text event instead of
            # writing it with the write tool.  Recover it from the NDJSON stream.
            if _tl("CLI_BACKEND") == "kilo":
                for _line in stdout_text.splitlines():
                    _line = _line.strip()
                    if not _line:
                        continue
                    try:
                        _evt = json.loads(_line, strict=False)
                        _text = _evt.get("part", {}).get("text", "")
                        if _text:
                            _candidate = _text.strip()
                            # strip markdown code fences if present
                            if _candidate.startswith("```"):
                                _candidate = re.sub(r"^```[^\n]*\n?", "", _candidate)
                                _candidate = re.sub(r"\n?```$", "", _candidate.strip())
                            _parsed = json.loads(_candidate, strict=False)
                            if isinstance(_parsed, dict) and "answer" in _parsed:
                                answer_path.write_text(
                                    json.dumps(_parsed, indent=2) + "\n", encoding="utf-8"
                                )
                                answer_written = True
                                task_log.info(
                                    "answer.json recovered from stdout text event (%d chars)",
                                    len(_parsed["answer"]),
                                )
                                break
                    except (json.JSONDecodeError, Exception):
                        continue

        # Manifest
        manifest = {
            "instance_id"   : instance_id,
            "base_commit"   : base_commit,
            "cli_backend"   : _tl("CLI_BACKEND"),
            "model_provider": _tl("MODEL_PROVIDER"),
            "model"         : _effective_model(),
            "mode"          : MODE,
            "run_mode"      : RUN_MODE,
            "run_ts"        : datetime.now(timezone.utc).isoformat(),
            "elapsed_s"     : round(elapsed, 2),
            "cwd"           : str(MCP_WORKSPACE if RUN_MODE == "mcp" else ASTROPY_DIR),
            "answer_written": answer_written,
            "otel_session_id": session_id,
            "otel_sessions" : {sid: [str(f) for f in files] for sid, files in sessions.items()},
            "cli_metrics"   : cli_metrics,
            "structure"     : {
                "answer.json": "Claude task answer",
                "telemetry/": "Raw OTel session files",
                "logs/": "Auditor log + Claude transcript",
            },
        }
        (task_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        task_log.info("run_manifest.json written.")
        task_log.info("Task output: %s", task_dir)

    finally:
        _close_task_logger(task_log, fh)


# ── Enrichment phase ─────────────────────────────────────────────────────────

def _enrich_from_otel(task_dir: Path) -> tuple:
    """Enrich answer.json using OTel telemetry (claude backend).
    Returns (ok, msg, metrics_dict).
    """
    src_dir = str(PROJECT_ROOT / "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    try:
        from enrich_answers import enrich_task  # type: ignore
    except ImportError as exc:
        return False, f"cannot import enrich_answers: {exc}", {}

    ok, msg = enrich_task(str(task_dir))
    metrics: dict = {}
    if ok:
        answer_path = task_dir / "answer.json"
        try:
            data = json.loads(answer_path.read_text(encoding="utf-8"))
            metrics = {k: v for k, v in data.items() if k != "answer"}
        except Exception:
            pass
    return ok, msg, metrics


def _enrich_from_kilo(task_dir: Path) -> tuple:
    """Enrich answer.json from kilo cli_metrics stored in run_manifest.json.
    Returns (ok, msg, metrics_dict).
    """
    answer_path   = task_dir / "answer.json"
    manifest_path = task_dir / "run_manifest.json"

    if not answer_path.exists():
        return False, "no answer.json", {}
    if not manifest_path.exists():
        return False, "no run_manifest.json", {}

    manifest    = json.loads(manifest_path.read_text(encoding="utf-8"))
    cli_metrics = manifest.get("cli_metrics") or {}
    elapsed_s   = manifest.get("elapsed_s", 0)

    if not cli_metrics:
        return False, "no cli_metrics in manifest", {}

    # _parse_kilo_metrics already stores fields using the standard schema names
    # (total_input_tokens, total_output_tokens, …).  Just pass them through and
    # add time_taken_seconds from the manifest elapsed_s.
    normalized: dict = {"time_taken_seconds": elapsed_s, **cli_metrics}

    answer  = json.loads(answer_path.read_text(encoding="utf-8"), strict=False)
    enriched = {"answer": answer.get("answer", "")}
    enriched.update(normalized)
    for k, v in answer.items():
        if k not in enriched:
            enriched[k] = v

    answer_path.write_text(json.dumps(enriched, indent=2) + "\n", encoding="utf-8")
    return True, "enriched (kilo)", normalized


def run_enrichment_phase(contexts: list) -> list:
    """Phase 3: enrich every answer.json with metrics. Returns per-task result dicts."""
    log.info("Phase 3: enriching %d task(s) …", len(contexts))
    results = []
    for ctx in contexts:
        task_dir    = ctx["task_dir"]
        instance_id = ctx["instance_id"]
        try:
            if _tl("CLI_BACKEND") == "claude":
                ok, msg, metrics = _enrich_from_otel(task_dir)
            elif _tl("CLI_BACKEND") == "kilo":
                ok, msg, metrics = _enrich_from_kilo(task_dir)
            else:
                ok, msg, metrics = False, f"no enrichment for backend={_tl('CLI_BACKEND')}", {}
        except Exception as exc:
            ok, msg, metrics = False, str(exc), {}

        log.info("  [%s] %s: %s", "OK  " if ok else "FAIL", instance_id, msg)
        results.append({
            "instance_id": instance_id,
            "task_dir":    task_dir,
            "enriched":    ok,
            "msg":         msg,
            "metrics":     metrics,
        })
    return results


def print_summary_table(enrich_results: list) -> None:
    """Print a formatted per-task evaluation summary table to stdout."""
    if not enrich_results:
        return

    model_label = _effective_model()
    header = f"  EVALUATION SUMMARY  —  {_tl('CLI_BACKEND')} / {model_label} / {RUN_MODE}"
    w      = max(len(header) + 4, 84)
    SEP    = "═" * w
    THIN   = "─" * w

    print()
    print(SEP)
    print(header)
    print(SEP)
    print(f"  {'Task':<30}  {'Ans':^3}  {'Enr':^3}  {'Time(s)':>7}  {'Cost($)':>9}  {'Input':>7}  {'Output':>7}  {'CacheR':>7}")
    print(THIN)

    n_ans = n_enr = 0
    tot_time = tot_cost = tot_in = tot_out = tot_cr = 0.0

    for r in enrich_results:
        m     = r["metrics"]
        ans   = "✓" if (r["task_dir"] / "answer.json").exists() else "✗"
        enr   = "✓" if r["enriched"] else "✗"
        t     = float(m.get("time_taken_seconds") or 0)
        c     = float(m.get("total_cost_usd") or 0)
        inp   = int(m.get("total_input_tokens") or 0)
        out   = int(m.get("total_output_tokens") or 0)
        cr    = int(m.get("total_cache_read_tokens") or 0)

        if ans == "✓": n_ans += 1
        if enr == "✓": n_enr += 1
        tot_time += t; tot_cost += c; tot_in += inp; tot_out += out; tot_cr += cr

        label = r["instance_id"].replace("astropy__", "")
        print(
            f"  {label:<30}  {ans:^3}  {enr:^3}"
            f"  {t:>7.1f}  {c:>9.5f}  {inp:>7}  {out:>7}  {cr:>7}"
        )

    total = len(enrich_results)
    print(THIN)
    print(
        f"  {'TOTAL':<30}  {f'{n_ans}/{total}':^3}  {f'{n_enr}/{total}':^3}"
        f"  {tot_time:>7.1f}  {tot_cost:>9.5f}  {int(tot_in):>7}  {int(tot_out):>7}  {int(tot_cr):>7}"
    )
    print(SEP)
    print()


# ── Pipeline helper + eval mode ──────────────────────────────────────────────

def _run_pipeline(tasks: list) -> list:
    """
    Run phases 1 + 2 + 3 for the current global model/backend/run-mode config.
    Caller is responsible for starting/stopping the OTel receiver if needed.
    Returns enrich_results list.
    """
    total = len(tasks)
    _active_out_dir().mkdir(parents=True, exist_ok=True)
    if RUN_MODE == "mcp":
        MCP_WORKSPACE.mkdir(parents=True, exist_ok=True)

    # Phase 1 — staggered launch
    log.info("Phase 1: staggered launch (%d task(s)) …", total)
    contexts: list = []
    for i, task in tqdm(enumerate(tasks, start=1), total=total,
                        desc="launching", unit="task", leave=False):
        ctx = setup_and_launch(task, i, total)
        contexts.append(ctx)

    # Phase 2 — parallel finish
    log.info("Phase 2: waiting for %d parallel agent run(s) …", total)
    with tqdm(total=total, desc="finishing", unit="task", leave=False) as pbar:
        with ThreadPoolExecutor(max_workers=PARALLEL_WORKERS) as pool:
            futures = {pool.submit(finish_task, ctx): ctx["instance_id"]
                       for ctx in contexts}
            for future in as_completed(futures):
                iid = futures[future]
                try:
                    future.result()
                    log.info("✓ %s complete", iid)
                except Exception as exc:
                    log.error("✗ %s raised: %s", iid, exc)
                pbar.update(1)

    # Phase 3 — enrich
    return run_enrichment_phase(contexts)


def _apply_model_config(cfg: dict) -> None:
    """Store model config in thread-local so parallel threads don't clobber each other."""
    _thread_local.MODEL_PROVIDER = cfg["provider"]
    if cfg["provider"] == "openrouter":
        _thread_local.OPENROUTER_MODEL = cfg["model"]
        _thread_local.MODEL = MODEL  # preserve global for non-openrouter reads
    else:
        _thread_local.MODEL = cfg["model"]
        _thread_local.OPENROUTER_MODEL = OPENROUTER_MODEL
    _thread_local.CLI_BACKEND = cfg["backend"]


def _run_one_model(model_cfg: dict, tasks: list, idx: int, n_models: int) -> dict:
    """Run the full pipeline for a single model config. Thread-safe for kilo backend."""
    _apply_model_config(model_cfg)
    label = _effective_model()
    log.info("─" * 70)
    log.info("MODEL %d/%d  —  %s  (backend=%s, cache=%s)",
             idx, n_models, label, _tl("CLI_BACKEND"), model_cfg.get("cache", "?"))
    log.info("  Output : %s", _active_out_dir())
    log.info("─" * 70)
    enrich_results = _run_pipeline(tasks)
    log.info("Model %d/%d done — %s", idx, n_models, label)
    return {"model_cfg": model_cfg, "model_label": label, "enrich_results": enrich_results}


def run_eval_mode(tasks: list, selector: str) -> None:
    """
    Run every model in EVAL_MODELS against the same task set.

    Parallelism strategy:
      • claude-backend models always run sequentially — OTel session-ID locking
        requires knowing which Claude process owns which telemetry file.
      • kilo-backend models can run in parallel (no OTel dependency).
        Set EVAL_PARALLEL_MODELS = True or pass --eval-parallel to enable.
    """
    n_models   = len(EVAL_MODELS)
    n_tasks    = len(tasks)
    needs_otel = any(m["backend"] == "claude" for m in EVAL_MODELS)

    claude_models = [m for m in EVAL_MODELS if m["backend"] == "claude"]
    kilo_models   = [m for m in EVAL_MODELS if m["backend"] != "claude"]

    log.info("=" * 70)
    log.info("EVAL MODE  —  %d model(s) × %d task(s)  [%s]", n_models, n_tasks, selector)
    log.info("  Run-mode       : %s  |  Mode : %s", RUN_MODE, MODE)
    log.info("  claude models  : %d  (sequential, OTel)", len(claude_models))
    log.info("  kilo models    : %d  (%s)", len(kilo_models),
             "parallel" if EVAL_PARALLEL_MODELS else "sequential — set EVAL_PARALLEL_MODELS=True to parallelise")
    log.info("=" * 70)

    if needs_otel:
        start_otel_receiver()

    all_results: list = []
    model_order = list(enumerate(EVAL_MODELS, 1))   # preserve original order for summary

    try:
        # ── claude models: always sequential ─────────────────────────────────
        sequential = [(idx, cfg) for idx, cfg in model_order if cfg["backend"] == "claude"]
        for idx, cfg in sequential:
            all_results.append(_run_one_model(cfg, tasks, idx, n_models))

        # ── kilo models: parallel or sequential ──────────────────────────────
        parallel_list = [(idx, cfg) for idx, cfg in model_order if cfg["backend"] != "claude"]
        if EVAL_PARALLEL_MODELS and parallel_list:
            log.info("Running %d kilo model(s) in parallel …", len(parallel_list))
            with tqdm(total=len(parallel_list), desc="models", unit="model", leave=False) as mpbar:
                with ThreadPoolExecutor(max_workers=len(parallel_list)) as pool:
                    futs = {
                        pool.submit(_run_one_model, cfg, tasks, idx, n_models): (idx, cfg)
                        for idx, cfg in parallel_list
                    }
                    for fut in as_completed(futs):
                        try:
                            all_results.append(fut.result())
                        except Exception as exc:
                            idx, cfg = futs[fut]
                            log.error("Model %d (%s) raised: %s", idx, cfg["model"], exc)
                        mpbar.update(1)
        else:
            for idx, cfg in parallel_list:
                all_results.append(_run_one_model(cfg, tasks, idx, n_models))

    finally:
        if needs_otel:
            log.info("Eval complete — stopping OTel receiver.")
            kill_otel_receiver()

    # Re-sort by original EVAL_MODELS order before printing
    order = {cfg["model"]: i for i, cfg in enumerate(EVAL_MODELS)}
    all_results.sort(key=lambda r: order.get(r["model_cfg"]["model"], 999))
    print_eval_summary(all_results)


def print_eval_summary(all_results: list) -> None:
    """Print a combined per-model summary table for an eval run."""
    if not all_results:
        return

    w   = 96
    SEP = "═" * w
    THN = "─" * w

    print()
    print(SEP)
    print(f"  EVAL SUMMARY  —  run_mode={RUN_MODE}  /  {len(all_results)} model(s)")
    print(SEP)
    print(f"  {'Model':<42}  {'Bk':^5}  {'Ans':^5}  {'Enr':^5}  {'AvgTime':>8}  {'TotalCost':>10}  {'TotalIn':>9}  {'TotalOut':>9}")
    print(THN)

    for r in all_results:
        cfg   = r["model_cfg"]
        ers   = r["enrich_results"]
        total = len(ers)
        if total == 0:
            continue

        n_ans  = sum(1 for e in ers if (e["task_dir"] / "answer.json").exists())
        n_enr  = sum(1 for e in ers if e["enriched"])
        t_time = sum(float(e["metrics"].get("time_taken_seconds") or 0) for e in ers)
        t_cost = sum(float(e["metrics"].get("total_cost_usd")     or 0) for e in ers)
        t_in   = sum(int  (e["metrics"].get("total_input_tokens") or 0) for e in ers)
        t_out  = sum(int  (e["metrics"].get("total_output_tokens")or 0) for e in ers)
        avg_t  = t_time / total

        # Shorten model slug for display
        short_model = cfg["model"].split("/")[-1][:40]
        bk          = cfg["backend"][:5]
        cache_icon  = "⚡" if cfg.get("cache") == "claude_code" else "~"

        print(
            f"  {short_model:<40}{cache_icon}  {bk:^5}  {n_ans}/{total:^3}  {n_enr}/{total:^3}"
            f"  {avg_t:>8.1f}  {t_cost:>10.5f}  {t_in:>9}  {t_out:>9}"
        )

    print(THN)
    # Aggregate totals across all models
    grand_ans  = sum(sum(1 for e in r["enrich_results"] if (e["task_dir"] / "answer.json").exists()) for r in all_results)
    grand_enr  = sum(sum(1 for e in r["enrich_results"] if e["enriched"]) for r in all_results)
    grand_cost = sum(sum(float(e["metrics"].get("total_cost_usd") or 0) for e in r["enrich_results"]) for r in all_results)
    grand_in   = sum(sum(int  (e["metrics"].get("total_input_tokens") or 0) for e in r["enrich_results"]) for r in all_results)
    grand_out  = sum(sum(int  (e["metrics"].get("total_output_tokens") or 0) for e in r["enrich_results"]) for r in all_results)
    grand_tot  = sum(len(r["enrich_results"]) for r in all_results)

    print(
        f"  {'GRAND TOTAL':<42}  {'':^5}  {grand_ans}/{grand_tot:^3}  {grand_enr}/{grand_tot:^3}"
        f"  {'—':>8}  {grand_cost:>10.5f}  {grand_in:>9}  {grand_out:>9}"
    )
    print(SEP)
    print()


# ── Main ──────────────────────────────────────────────────────────────────────

def load_tasks() -> list:
    """
    Load tasks from TASKS_FILE keeping only the three fields the script needs:
      instance_id  — used internally for output folder naming
      base_commit  — used internally to locate the right checkout directory
      question     — the only field ever shown to Claude (with commit masked)
    Everything else (answer, patch, version, difficulty, repo, dates, …) is dropped.
    """
    with open(TASKS_FILE, encoding="utf-8") as f:
        data = json.load(f)
    keep = {"instance_id", "base_commit", "question"}
    return [{k: v for k, v in t.items() if k in keep} for t in data["tasks"]]


def main() -> None:
    parser = argparse.ArgumentParser(description="Autonomous Claude Code eval driver")
    parser.add_argument(
        "--testids", nargs="+", metavar="ID",
        help="Run only these task IDs (numeric suffix, e.g. 14369 14598). "
             "Overrides TASK_SLICE when provided.",
    )
    parser.add_argument(
        "--slice", metavar="SLICE", default=None,
        help="Python slice of the task list, e.g. ':3', '3:6', '::2'. Overrides TASK_SLICE config.",
    )
    parser.add_argument(
        "--run-mode", choices=["raw", "mcp"], default=None,
        help="raw: Claude reads local repo (default). mcp: Claude uses ByteBell MCP only.",
    )
    parser.add_argument(
        "--openrouter-api-key", metavar="KEY", default=None,
        help="OpenRouter API key (overrides OPENROUTER_API_KEY config / env var).",
    )
    parser.add_argument(
        "--cli-backend", choices=["claude", "kilo"], default=None,
        help="CLI backend to use (default: claude). kilo: uses `kilo run --auto --format json`.",
    )
    parser.add_argument(
        "--eval", action="store_true", default=False,
        help="Eval mode: run every model in EVAL_MODELS against the same task set.",
    )
    parser.add_argument(
        "--eval-parallel", action="store_true", default=False,
        help="Run kilo-backend models in parallel during eval (claude models always sequential).",
    )
    parser.add_argument(
        "--eval-models", nargs="+", metavar="IDX", type=int, default=None,
        help="Indices (0-based) of EVAL_MODELS to run, e.g. --eval-models 0 1 runs only the "
             "first two models. Omit to run all.",
    )
    parser.add_argument(
        "--model", metavar="SLUG", default=None,
        help="Model slug to use. For anthropic: 'claude-sonnet-4-6'. "
             "For openrouter: 'qwen/qwen3.6-plus:free', 'openai/gpt-4o', etc. "
             "Overrides MODEL / OPENROUTER_MODEL config.",
    )
    args = parser.parse_args()

    # Apply --run-mode override
    if args.run_mode is not None:
        global RUN_MODE
        RUN_MODE = args.run_mode

    # Apply --openrouter-api-key override
    if args.openrouter_api_key is not None:
        global OPENROUTER_API_KEY
        OPENROUTER_API_KEY = args.openrouter_api_key

    # Apply --model override (sets the right constant for the active provider)
    if args.model is not None:
        global MODEL, OPENROUTER_MODEL
        if MODEL_PROVIDER == "openrouter":
            OPENROUTER_MODEL = args.model
        else:
            MODEL = args.model

    # Apply --cli-backend override
    if args.cli_backend is not None:
        global CLI_BACKEND
        CLI_BACKEND = args.cli_backend

    # Apply --eval / --eval-parallel / --eval-models overrides
    if args.eval:
        global EVAL_MODE
        EVAL_MODE = True
    if args.eval_parallel:
        global EVAL_PARALLEL_MODELS
        EVAL_PARALLEL_MODELS = True
    if args.slice is not None:
        global TASK_SLICE
        TASK_SLICE = args.slice

    if args.eval_models is not None:
        global EVAL_MODELS
        try:
            EVAL_MODELS = [EVAL_MODELS[i] for i in args.eval_models]
        except IndexError as e:
            parser.error(f"--eval-models index out of range: {e}. "
                         f"Valid indices: 0–{len(EVAL_MODELS)-1}")

    all_tasks = load_tasks()

    if args.testids:
        # Strip brackets/commas in case user pastes [ 14369 , 14598 ]
        raw_ids = {re.sub(r"[\[\],]", "", t).strip() for t in args.testids}
        tasks = [t for t in all_tasks if any(t["instance_id"].endswith(rid) for rid in raw_ids)]
        selector = f"--testids {' '.join(sorted(raw_ids))}"
    else:
        tasks = all_tasks[parse_slice(TASK_SLICE)]
        selector = f"slice={TASK_SLICE}"

    total = len(tasks)

    if total == 0:
        log.warning("No tasks matched — check --testids or TASK_SLICE. Exiting.")
        return

    # ── Eval mode: iterate over EVAL_MODELS ───────────────────────────────────
    if EVAL_MODE:
        run_eval_mode(tasks, selector)
        return

    # ── Single-model header ───────────────────────────────────────────────────
    active_out_dir = _active_out_dir()
    log.info("=" * 70)
    log.info("Claude Auditor — SWE-bench evaluation run")
    log.info("  Tasks file  : %s", TASKS_FILE.name)
    log.info("  Selection   : %s  (%d task(s))", selector, total)
    log.info("  CLI backend : %s", CLI_BACKEND)
    log.info("  Provider    : %s", MODEL_PROVIDER)
    log.info("  Model       : %s", _effective_model())
    log.info("  Mode        : %s", MODE)
    log.info("  Run-mode    : %s", RUN_MODE)
    log.info("  Workers     : %d", PARALLEL_WORKERS)
    log.info("  Output dir  : %s", active_out_dir)
    log.info("=" * 70)

    # ── Single-model mode ─────────────────────────────────────────────────────
    active_out_dir.mkdir(parents=True, exist_ok=True)
    if RUN_MODE == "mcp":
        MCP_WORKSPACE.mkdir(parents=True, exist_ok=True)

    if CLI_BACKEND == "claude":
        start_otel_receiver()

    enrich_results: list = []
    try:
        enrich_results = _run_pipeline(tasks)
    finally:
        if CLI_BACKEND == "claude":
            log.info("All tasks complete — stopping OTel receiver.")
            kill_otel_receiver()

    log.info("=" * 70)
    log.info("Run complete. Results in: %s", active_out_dir)
    log.info("=" * 70)

    print_summary_table(enrich_results)


if __name__ == "__main__":
    main()
