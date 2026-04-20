#!/usr/bin/env python3
"""
Minimal OTLP/HTTP JSON receiver.
Listens on port 4318, writes per-session JSON array files to .claude/logs/.
  .claude/logs/{session_id}_events.json
  .claude/logs/{session_id}_metrics.json

Each file is a valid, human-readable JSON array of records.
"""

import json
import os
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

LOGS_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

SUFFIXES = {
    "/v1/logs":    "_events.json",
    "/v1/metrics": "_metrics.json",
}


def attr_value(attrs):
    """Return session.id stringValue from an attributes list, or None."""
    for attr in attrs:
        if attr.get("key") == "session.id":
            return attr.get("value", {}).get("stringValue", "").strip() or None
    return None


def extract_session_id(payload):
    """Pull session.id from wherever it appears in an OTLP payload."""
    # --- metrics: session.id lives on each data point, not on the resource ---
    for rm in payload.get("resourceMetrics", []):
        for sm in rm.get("scopeMetrics", []):
            for metric in sm.get("metrics", []):
                for agg_key in ("sum", "gauge", "histogram", "exponentialHistogram", "summary"):
                    for dp in metric.get(agg_key, {}).get("dataPoints", []):
                        sid = attr_value(dp.get("attributes", []))
                        if sid:
                            return sid

    # --- logs: session.id lives on each log record's attributes ---
    for rl in payload.get("resourceLogs", []):
        for sl in rl.get("scopeLogs", []):
            for lr in sl.get("logRecords", []):
                sid = attr_value(lr.get("attributes", []))
                if sid:
                    return sid

    return None


def append(path, record):
    """Read existing array (if any), append new record, rewrite the whole file."""
    entry = {"ts": datetime.now(timezone.utc).isoformat(), "data": record}
    try:
        with open(path, "r") as f:
            records = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        records = []
    records.append(entry)
    with open(path, "w") as f:
        json.dump(records, f, indent=2)


class OTLPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body)
        except Exception:
            payload = {"raw": body.decode(errors="replace")}

        session_id = extract_session_id(payload) or "unknown"
        suffix = SUFFIXES.get(self.path, "_other.json")
        dest = os.path.join(LOGS_DIR, f"{session_id}{suffix}")

        append(dest, payload)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b"{}")

    def log_message(self, *_):
        pass  # silence per-request stdout noise


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 4318
    print(f"OTLP receiver on :{port}  →  {LOGS_DIR}/", flush=True)
    HTTPServer(("localhost", port), OTLPHandler).serve_forever()
