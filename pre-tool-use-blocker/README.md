# Claude Code Destructive Command Blocker

A `PreToolUse` hook that intercepts and blocks destructive bash commands before
Claude Code executes them.

**Bounty #3: $100 — claude-builders-bounty/claude-builders-bounty**

## Quick Install

```bash
bash install.sh
```

## What It Blocks

| Category | Patterns |
|----------|----------|
| File system | `rm -rf`, `rm --force`, `shred`, `dd if=` |
| Git force | `git push --force`, `git reset --hard`, `git clean -f` |
| Database | `DROP TABLE`, `TRUNCATE`, `DELETE FROM` (without WHERE) |
| Permissions | `chmod 777`, `chmod -R 777` |
| System | `/dev/sd*` overwrite, `mkfs`, fork bombs |

## Verification

```bash
# Should be BLOCKED:
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /etc"},"cwd":"/tmp"}' \
  | python3 ~/.claude/hooks/pre-tool-use-blocker.py

# Should be ALLOWED:
echo '{"tool_name":"Bash","tool_input":{"command":"ls -la"},"cwd":"/tmp"}' \
  | python3 ~/.claude/hooks/pre-tool-use-blocker.py

# View blocked log
cat ~/.claude/hooks/blocked.log
```

## Requirements Met

- [x] Claude Code hooks format (`~/.claude/hooks/`)
- [x] Blocks: `rm -rf`, `DROP TABLE`, `git push --force`, `TRUNCATE`, `DELETE FROM`
- [x] Logs to `~/.claude/hooks/blocked.log` with timestamp/command/project
- [x] Clear message explaining why blocked
- [x] Does not interfere with normal commands
- [x] Install in 2 commands: `bash install.sh`

## License

MIT
