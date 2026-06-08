#!/usr/bin/env bash
# Install destructive command blocker for Claude Code
# Usage: bash install.sh
set -e

HOOKS_DIR="${HOME}/.claude/hooks"
SCRIPT_NAME="pre-tool-use-blocker.py"
SCRIPT_PATH="${HOOKS_DIR}/${SCRIPT_NAME}"
LOG_FILE="${HOOKS_DIR}/blocked.log"

mkdir -p "${HOOKS_DIR}"

# 1. Copy the hook
cp "$(dirname "$0")/${SCRIPT_NAME}" "${SCRIPT_PATH}"
chmod +x "${SCRIPT_PATH}"
echo "✅ Installed ${SCRIPT_PATH}"

# 2. Register in settings.json using env vars (safe from shell escaping)
export SETTINGS_FILE="${HOME}/.claude/settings.json"
export HOOK_CMD="python3 ${SCRIPT_PATH}"
touch "${SETTINGS_FILE}"

python3 << 'PYREG'
import json, os
settings_path = os.environ['SETTINGS_FILE']
hook_cmd = os.environ['HOOK_CMD']

with open(settings_path) as f:
    try:    data = json.load(f)
    except: data = {}

hooks = data.setdefault('hooks', {})
pre = hooks.setdefault('PreToolUse', [])

# Check if already registered
already = any(
    h.get('hooks') and any(
        hh.get('command') == hook_cmd
        for hh in h.get('hooks', [])
    )
    for h in pre
)

if not already:
    pre.append({
        'matcher': 'Bash',
        'hooks': [
            {
                'type': 'command',
                'command': hook_cmd,
                'timeout': 2000
            }
        ]
    })
    with open(settings_path, 'w') as f:
        json.dump(data, f, indent=2)
    print('✅ Hook registered for Bash commands')
else:
    print('ℹ️  Hook already registered — skipped')
PYREG

# 3. Verify
echo ""
echo "=== Installation Complete ==="
echo "Hook: ${SCRIPT_PATH}"
echo "Log:  ${LOG_FILE}"
echo ""

# Test with valid JSON format
echo "--- Quick self-test ---"
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /important/dir"},"cwd":"/tmp/test"}' \
  | python3 "${SCRIPT_PATH}" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('⛔ BLOCKED' if d.get('continue')==False else '✅ ALLOWED')" 2>/dev/null || true
