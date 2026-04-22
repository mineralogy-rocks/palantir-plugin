#!/usr/bin/env python3
"""Auto-approve Bash calls that invoke the Palantir CLI — nothing else.

Wired as a PreToolUse hook with matcher `Bash`. For every Bash call, decide:

- `allow`  — if the command is a Palantir CLI invocation (bare `palantir`,
             `${CLAUDE_PLUGIN_ROOT}/.claude/bin/palantir`, or an absolute
             plugin-cache path), optionally fed by a safe reader (`echo`,
             `cat`, `printf`) on the left of a pipe. No user prompt.
- `defer`  — for everything else. Claude Code falls back to its normal
             permission logic (allowlist, ask, deny).

Deliberately conservative:
- Any shell control flow (`;`, `&&`, `||`, subshells `$(…)`, backticks) → defer.
- Any dangerous verb (`sudo`, `rm`, `curl`, `wget`, `chmod`, `chown`, `kill`,
  `mv`, `cp` writing to system paths) → defer.
- A pipeline is approved only when every non-final stage is a safe reader and
  the final stage is a Palantir invocation.

This pattern is documented at https://code.claude.com/docs/en/hooks.md as the
intended channel for plugins to pre-approve their own CLI surface.
"""

from __future__ import annotations

import json
import os
import re
import sys


_SAFE_READERS = re.compile(r"^(?:echo|cat|printf|true|false|jq|head|tail)\b")
_DANGEROUS = re.compile(
	r"\b(?:sudo|rm|curl|wget|chmod|chown|kill|mkfifo|dd|shutdown|reboot)\b"
)
_SHELL_CONTROL = re.compile(r";|&&|\|\||\$\(|`|>|<")  # chaining, subshells, any redirect

# Recognized palantir invocations:
# - `palantir ...` bare (if on PATH)
# - `"${CLAUDE_PLUGIN_ROOT}/.claude/bin/palantir" ...` with or without quotes
# - absolute path inside ~/.claude/plugins/cache/.../palantir
_PALANTIR_RE = re.compile(
	r"""
	^\s*
	(?:"|\')?                                         # optional opening quote
	(?:
		\$\{?CLAUDE_PLUGIN_ROOT\}?/\.claude/bin/palantir
		|
		/[^\s"']+/\.claude/(?:bin|plugins/cache/[^\s"']+)/palantir
		|
		palantir
	)
	(?:"|\')?                                         # optional closing quote
	(?:\s|$)                                          # must be followed by space or EOS
	""",
	re.VERBOSE,
)


def _decide(kind: str, reason: str | None = None) -> dict:
	out: dict = {
		"hookSpecificOutput": {
			"hookEventName": "PreToolUse",
			"permissionDecision": kind,
		}
	}
	if reason:
		out["hookSpecificOutput"]["permissionDecisionReason"] = reason
	return out


def _is_palantir_stage(stage: str) -> bool:
	return _PALANTIR_RE.match(stage) is not None


def _is_safe_reader_stage(stage: str) -> bool:
	return _SAFE_READERS.match(stage.lstrip()) is not None


def evaluate(command: str) -> dict:
	cmd = command.strip()
	if not cmd:
		return _decide("defer")

	if _DANGEROUS.search(cmd):
		return _decide("defer")
	if _SHELL_CONTROL.search(cmd):
		return _decide("defer")

	# Split on pipes only. No `&&`, `;`, etc. reach here (already defer'd above).
	stages = [s.strip() for s in cmd.split("|")]
	if not stages:
		return _decide("defer")

	# Final stage must be the palantir invocation.
	if not _is_palantir_stage(stages[-1]):
		return _decide("defer")

	# All preceding stages must be safe readers (heredoc/echo/cat/printf).
	for stage in stages[:-1]:
		if not _is_safe_reader_stage(stage):
			return _decide("defer")

	# `logout` deletes credentials — always confirm.
	if re.search(r"/palantir[\"']?\s+logout\b|\bpalantir[\"']?\s+logout\b", stages[-1]):
		return _decide(
			"ask",
			"Palantir plugin: logout clears stored credentials — confirm.",
		)

	return _decide(
		"allow",
		"Palantir plugin: auto-approved palantir CLI call.",
	)


def main() -> int:
	raw = sys.stdin.read()
	if not raw.strip():
		# Nothing to decide on; let the normal flow run.
		sys.stdout.write(json.dumps(_decide("defer")))
		return 0
	try:
		payload = json.loads(raw)
	except json.JSONDecodeError:
		sys.stdout.write(json.dumps(_decide("defer")))
		return 0

	tool_input = payload.get("tool_input") or {}
	command = tool_input.get("command", "") if isinstance(tool_input, dict) else ""
	decision = evaluate(command) if isinstance(command, str) else _decide("defer")
	sys.stdout.write(json.dumps(decision))
	return 0


if __name__ == "__main__":
	try:
		sys.exit(main())
	except Exception:
		# Never break the host — on any internal error, defer to normal flow.
		sys.stdout.write(json.dumps(_decide("defer")))
		sys.exit(0)
