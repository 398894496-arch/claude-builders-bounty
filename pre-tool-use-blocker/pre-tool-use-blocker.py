#!/usr/bin/env python3
"""
Claude Code PreToolUse Hook — Destructive Command Blocker
Bounty #3: claude-builders-bounty/claude-builders-bounty

Intercepts destructive bash commands before execution.
Logs every blocked attempt with timestamp, command, and project path.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone

LOG_FILE = os.path.expanduser("~/.claude/hooks/blocked.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# ── Patterns ──────────────────────────────────────────────
# (pattern, explanation) — explanation is shown to Claude
DESTRUCTIVE_PATTERNS = [
    # File system destruction
    (r'\brm\s+.*-rf\b',                     "rm -rf: recursive force remove"),
    (r'\brm\s+.*--recursive\b',             "rm --recursive: recursive remove"),
    (r'\brm\s+.*--force\b',                 "rm --force: forced remove"),
    (r'\brm\s+-r\s',                        "rm -r: recursive remove"),
    (r'\bshred\b',                          "shred: secure file deletion"),
    (r'\bdd\s+if=',                         "dd: disk overwrite / image write"),

    # Force push / destructive git
    (r'git\s+push\s+.*--force(?![\-\w]*with[\-\w]*lease)', "git push --force (without --force-with-lease)"),
    (r'git\s+push\s+.*-f\b(?![\-\w]*lease)', "git push -f (without --force-with-lease)"),
    (r'git\s+push\s+.*\+\w+/\w+',           "git push +ref: force push via refspec"),
    (r'git\s+reset\b.*\b--hard\b',           "git reset --hard: discards all uncommitted changes"),
    (r'git\s+clean\s+-[f]',                 "git clean: removes untracked files"),

    # Database destruction
    (r'\bDROP\s+(TABLE|DATABASE|SCHEMA)\b', "DROP: removes database objects"),
    (r'\bTRUNCATE\b',                        "TRUNCATE: removes all rows"),
    # Matches DELETE FROM <table> that lacks a direct WHERE — lookahead
    # stops at semicolons so subqueries don't falsely satisfy the guard
    (r'\bDELETE\s+FROM\s+\w+\s*(?![^;]*\bWHERE\b)', "DELETE FROM without WHERE clause"),

    # System-level danger
    (r'\bchmod\s+777\b',                    "chmod 777: world-writable permissions"),
    (r'\bchmod\s+-R\s+777\b',               "chmod -R 777: recursive world-writable"),
    (r'\b>:?\s*/dev/sd[a-z]',               "overwrite block device"),
    (r'\bmkfs\.',                             "mkfs: create filesystem (destroys existing data)"),
    (r'\b:\(\)\s*\{',                        "fork bomb pattern"),
]

# Whitelist — commands that match destructive patterns but are safe
WHITELIST = [
    r'rm\s+-rf\s+/(?:tmp|var/(?:tmp|folders))(?:/|$)',  # rm -rf /tmp or /tmp/
    r'truncate\s+-s',                                     # truncate -s for file sizing
]


def is_whitelisted(command: str) -> bool:
    """Check if a matched command is actually safe."""
    for pattern in WHITELIST:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    return False


def log_block(project: str, blocked_cmd: str, reason: str):
    """Append a blocked attempt to the log file."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project": project,
        "command": blocked_cmd,
        "reason": reason,
    }
    try:
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass  # Best-effort logging


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        # If stdin is empty (shouldn't happen but handle gracefully)
        print(json.dumps({"continue": True}), flush=True)
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "").strip()
    project = input_data.get("cwd", os.getcwd())

    # Guard: empty command — nothing to check
    if not command:
        print(json.dumps({"continue": True}), flush=True)
        sys.exit(0)

    # Only intercept Bash tool — normalize casing/whitespace
    if tool_name.strip().lower() != "bash":
        print(json.dumps({"continue": True}), flush=True)
        sys.exit(0)

    # Check every destructive pattern
    for pattern, explanation in DESTRUCTIVE_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            if is_whitelisted(command):
                continue  # Safe whitelisted command
            # BLOCK
            log_block(project, command, explanation)
            msg = (
                f"⛔ BLOCKED: {explanation}\n"
                f"   Command: {command}\n"
                f"   Project: {project}\n"
                f"   Logged to: {LOG_FILE}\n\n"
                f"💡 If you are certain this is safe, run it manually in a terminal\n"
                f"   or use dangerouslyDisableSandbox in Claude Code.\n"
            )
            print(json.dumps({
                "continue": False,
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "decision": "block",
                    "reason": explanation,
                    "message": msg,
                }
            }), flush=True)
            sys.exit(0)

    # All good — allow
    print(json.dumps({"continue": True}), flush=True)


if __name__ == "__main__":
    main()
