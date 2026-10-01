#!/usr/bin/env python3
"""
PermissionDenied hook logger.

Appends one NDJSON record per denial to ~/.claude/permission-prompts.jsonl.
Wrapped in try/except — never blocks hook flow on logging failure.

Mining example:
    jq -s 'group_by(.tool) | map({tool: .[0].tool, count: length}) | sort_by(.count) | reverse | .[:20]' \
        ~/.claude/permission-prompts.jsonl
"""
import datetime
import json
import os
import sys

LOG_PATH = os.path.expanduser("~/.claude/permission-prompts.jsonl")

try:
    payload = json.load(sys.stdin)
    record = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "session": payload.get("session_id", ""),
        "tool": payload.get("tool_name", ""),
        "input_summary": json.dumps(payload.get("tool_input", {}))[:8000],
        "reason": payload.get("reason", ""),
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")
except Exception:  # noqa: S110, BLE001 — never block hook flow on logging failure
    pass

sys.exit(0)
