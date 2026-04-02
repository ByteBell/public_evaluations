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
import time
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
TASK_SLICE = ":"

# Output root — each task writes to OUT_DIR/<instance_id>/
OUT_DIR = PROJECT_ROOT / "results_swe_bench" / "auto_run_on_qwen3.6_plus_preview"

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
OPENROUTER_MODEL   = "qwen/qwen3.6-plus-preview:free"

# "print"       — subprocess + `claude -p` (non-interactive, exits when done)
# "interactive" — pexpect PTY (interactive TUI, useful for auto-approval loops)
MODE = "print"

# ── Run-mode ──────────────────────────────────────────────────────────────────
# "raw" — Claude reads from the local Astropy checkout (original behaviour)
# "mcp" — Claude runs in an empty workspace and must use ByteBell MCP tools
RUN_MODE = "raw"   # overridden by --run-mode CLI arg

# Output dir for MCP runs (raw run dir is OUT_DIR above)
MCP_OUT_DIR = PROJECT_ROOT / "results_swe_bench" / "mcp_run_on_qwen3.6_plus_preview_with_mcp"

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
PARALLEL_WORKERS = 10

# How long (seconds) to poll for the task's OTel session UUID to appear before giving up
OTEL_SESSION_LOCK_WAIT = 20

# ── System prompt ─────────────────────────────────────────────────────────────
# Injected via `--system-prompt` on every Claude invocation.
# The literal placeholder {answer_path} is filled in per-task at runtime.

MCP_SYSTEM_PROMPT_TEMPLATE = """\
# ByteBell MCP

Answer the question below using **only** ByteBell MCP tools

---

## Hard Rules

1. **ONLY use ByteBell MCP tools** — no local file reads, no git APIs, no GitNexus skills.

---

Just write your answer, no special format needed.

{{ "answer": "answer" }} that's it

Question :

{question}

Write your answer to {answer_path}
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
    """Return the model string to pass to --model, accounting for provider."""
    if MODEL_PROVIDER == "openrouter":
        # OpenRouter integration redirects ANTHROPIC_BASE_URL, so model slug
        # is passed as-is (no "openrouter/" prefix needed).
        return OPENROUTER_MODEL
    return MODEL


def _provider_env() -> dict:
    """Extra env vars required by the active provider."""
    if MODEL_PROVIDER == "openrouter":
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
    task_log.info("Launching Claude (print / provider=%s / model=%s) ...", MODEL_PROVIDER, model)
    task_log.debug("CWD: %s", cwd)
    proc = subprocess.Popen(
        [CLAUDE_BIN, "--print", "--dangerously-skip-permissions",
         "--model", model, "--system-prompt", system_prompt, prompt],
        cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, env={**os.environ, **OTEL_ENV, **_provider_env()},
    )
    task_log.debug("Claude PID: %d", proc.pid)
    return proc



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
        out_root = MCP_OUT_DIR
    else:
        cwd      = ASTROPY_DIR
        out_root = OUT_DIR

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

    # Launch Claude (non-blocking)
    proc = launch_claude_print(prompt, system_prompt, cwd, task_log)

    # Block here until this task's session ID appears in OTel —
    # since we are the only Claude just launched, the first new session is ours.
    session_id = wait_for_session_id(before, task_log)

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
        stdout_text, stderr_text = proc.communicate()  # no timeout — let Claude run as long as needed

        elapsed = time.monotonic() - run_start
        if proc.returncode != 0:
            task_log.warning("Claude non-zero exit code %d", proc.returncode)
        else:
            task_log.info("Claude finished in %.1f s.", elapsed)

        # Save transcript
        combined = stderr_text + stdout_text
        (logs_dir / "claude_stdout.txt").write_text(combined, encoding="utf-8")
        task_log.info("Transcript saved → logs/claude_stdout.txt (%d chars)", len(combined))

        # Wait for OTel flush then copy this session's files
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

        # Verify answer
        answer_written = answer_path.exists()
        if answer_written:
            try:
                preview = json.loads(answer_path.read_text(encoding="utf-8"))
                task_log.info("answer.json written — preview: %s", str(preview)[:200])
            except json.JSONDecodeError as exc:
                task_log.warning("answer.json invalid JSON: %s", exc)
        else:
            task_log.warning("answer.json NOT created at: %s", answer_path)
            task_log.debug("stdout preview:\n%s", combined[:500])

        # Manifest
        manifest = {
            "instance_id"   : instance_id,
            "base_commit"   : base_commit,
            "model_provider": MODEL_PROVIDER,
            "model"         : _effective_model(),
            "mode"          : MODE,
            "run_mode"      : RUN_MODE,
            "run_ts"        : datetime.now(timezone.utc).isoformat(),
            "elapsed_s"     : round(elapsed, 2),
            "cwd"           : str(MCP_WORKSPACE if RUN_MODE == "mcp" else ASTROPY_DIR),
            "answer_written": answer_written,
            "otel_session_id": session_id,
            "otel_sessions" : {sid: [str(f) for f in files] for sid, files in sessions.items()},
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
        "--run-mode", choices=["raw", "mcp"], default=None,
        help="raw: Claude reads local repo (default). mcp: Claude uses ByteBell MCP only.",
    )
    parser.add_argument(
        "--openrouter-api-key", metavar="KEY", default=None,
        help="OpenRouter API key (overrides OPENROUTER_API_KEY config / env var).",
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

    log.info("=" * 70)
    log.info("Claude Auditor — SWE-bench evaluation run")
    log.info("  Tasks file  : %s", TASKS_FILE.name)
    log.info("  Selection   : %s  (%d task(s))", selector, total)
    active_out_dir = MCP_OUT_DIR if RUN_MODE == "mcp" else OUT_DIR

    log.info("  Provider    : %s", MODEL_PROVIDER)
    log.info("  Model       : %s", _effective_model())
    log.info("  Mode        : %s", MODE)
    log.info("  Run-mode    : %s", RUN_MODE)
    log.info("  Workers     : %d", PARALLEL_WORKERS)
    log.info("  Output dir  : %s", active_out_dir)
    log.info("=" * 70)

    if total == 0:
        log.warning("No tasks matched — check --testids or TASK_SLICE. Exiting.")
        return

    active_out_dir.mkdir(parents=True, exist_ok=True)
    if RUN_MODE == "mcp":
        MCP_WORKSPACE.mkdir(parents=True, exist_ok=True)

    # Start the OTel receiver once for the whole run
    start_otel_receiver()

    try:
        # ── Phase 1: serial launch + session-ID lock ──────────────────────────
        # Launch one task at a time and wait for its OTel session ID to appear
        # before launching the next.  This guarantees each session ID is
        # unambiguously attributed to its task even under full parallelism.
        log.info("Phase 1: staggered launch (%d task(s)) …", total)
        contexts = []
        for i, task in tqdm(enumerate(tasks, start=1), total=total,
                            desc="launching", unit="task", leave=False):
            ctx = setup_and_launch(task, i, total)
            contexts.append(ctx)

        # ── Phase 2: parallel finish ──────────────────────────────────────────
        # All Claude processes are now running.  Wait for them in parallel.
        log.info("Phase 2: waiting for %d parallel Claude run(s) …", total)
        with tqdm(total=total, desc="finishing", unit="task") as pbar:
            with ThreadPoolExecutor(max_workers=PARALLEL_WORKERS) as pool:
                futures = {pool.submit(finish_task, ctx): ctx["instance_id"]
                           for ctx in contexts}
                for future in as_completed(futures):
                    instance_id = futures[future]
                    try:
                        future.result()
                        log.info("✓ %s complete", instance_id)
                    except Exception as exc:
                        log.error("✗ %s raised: %s", instance_id, exc)
                    pbar.update(1)
    finally:
        log.info("All tasks complete — stopping OTel receiver.")
        kill_otel_receiver()

    log.info("=" * 70)
    log.info("Run complete. Results in: %s", active_out_dir)
    log.info("=" * 70)


if __name__ == "__main__":
    main()
