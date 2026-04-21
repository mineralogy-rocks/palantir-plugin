#!/usr/bin/env bash
# Async hook: auto-save an approved plan by delegating to the palantir skill.
# All atomization/save logic lives in the skill; this is pure plumbing.

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG="${TMPDIR:-/tmp}/palantir-plan-hook.log"
exec >> "$LOG" 2>&1

exec python3 "$HERE/_plan_auto_save.py"
