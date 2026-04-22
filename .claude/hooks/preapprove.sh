#!/usr/bin/env bash
# PreToolUse hook wrapper: routes the Claude Code payload through the Python
# decider and echoes the resulting JSON back on stdout. Stderr swallowed so a
# stray message never disrupts the permission flow.

exec python3 "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_preapprove.py" 2>/dev/null
