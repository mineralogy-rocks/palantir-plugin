#!/usr/bin/env python3
"""Trigger the palantir skill to save an approved plan, in a headless sub-agent.

Invoked by on_plan_approved.sh on PostToolUse/ExitPlanMode with async: true.
Reads the Claude Code hook payload from stdin, extracts the plan body, and
launches `claude -p` with a short instruction telling the sub-agent to run
the palantir skill's Plan Protocol on it.

Atomization and save mechanics live in the skill (see .claude/skills/palantir/
references/plan-protocol.md and .claude/rules/atomize.md). This script is pure
plumbing — no rule duplication, no prompt templating beyond pointing at the
skill.

Async hooks ignore stdout/stderr/exit code, so all observability goes to the
log file that on_plan_approved.sh wires up via `exec >> ... 2>&1`.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone

SUBAGENT_TIMEOUT = 300  # generous cap; claude -p does a full skill run
NOTIFY_TITLE = "Palantir"


def log(msg: str) -> None:
	ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
	print(f"[{ts}] {msg}", flush=True)


def notify(body: str, subtitle: str | None = None) -> None:
	"""Fire-and-forget OS notification. Disabled via PALANTIR_HOOK_NOTIFY=0.

	Best-effort: osascript on macOS, notify-send on Linux. Any failure is
	logged and swallowed — a missing notifier must never break the hook.
	"""
	if os.environ.get("PALANTIR_HOOK_NOTIFY", "1") == "0":
		return
	try:
		if sys.platform == "darwin" and shutil.which("osascript"):
			# Escape double quotes and backslashes for AppleScript
			body_esc = body.replace("\\", "\\\\").replace('"', '\\"')
			title_esc = NOTIFY_TITLE.replace("\\", "\\\\").replace('"', '\\"')
			script = f'display notification "{body_esc}" with title "{title_esc}"'
			if subtitle:
				sub_esc = subtitle.replace("\\", "\\\\").replace('"', '\\"')
				script += f' subtitle "{sub_esc}"'
			subprocess.run(
				["osascript", "-e", script],
				capture_output=True, text=True, timeout=5,
			)
			return
		if shutil.which("notify-send"):
			subprocess.run(
				["notify-send", NOTIFY_TITLE, body],
				capture_output=True, text=True, timeout=5,
			)
			return
		log(f"notify skipped (no notifier available): {body}")
	except Exception as exc:
		log(f"notify failed: {exc!r}")


def main() -> int:
	log("==== hook fired ====")
	raw = sys.stdin.read()
	if not raw.strip():
		log("empty stdin; nothing to do")
		return 0
	try:
		payload = json.loads(raw)
	except json.JSONDecodeError as exc:
		log(f"stdin not JSON: {exc}")
		return 0

	plan = ((payload.get("tool_input") or {}).get("plan") or "").strip()
	session_id = payload.get("session_id") or "nosession"
	if not plan:
		log("tool_input.plan is empty; nothing to do")
		return 0

	sha12 = hashlib.sha256(plan.encode("utf-8")).hexdigest()[:12]
	sid = (session_id or "nosession")[:16]
	dedupe_key = f"plan-{sid}-{sha12}"
	plan_title = _first_title(plan)
	log(f"session={sid} plan_bytes={len(plan)} dedupe_key={dedupe_key} title={plan_title!r}")

	notify(f"Saving approved plan: {plan_title}", subtitle="Auto-save started")

	prompt = (
		"The user has just approved a plan. Save it to Palantir by invoking the "
		"palantir skill and following its Plan Protocol (references/plan-protocol.md) "
		"with the existing atomization rules (rules/atomize.md). Use this exact "
		f"dedupe-key so retries are idempotent: {dedupe_key}. Tag the plan "
		"'auto-saved'. After the save completes, append a final line on its own: "
		"`PALANTIR_AUTOSAVE_DONE: <plan_id>` on success, or "
		"`PALANTIR_AUTOSAVE_FAILED: <short reason>` on failure. "
		"The approved plan text follows between <<< and >>>.\n\n"
		f"<<<\n{plan}\n>>>"
	)

	try:
		result = subprocess.run(
			["claude", "-p", prompt],
			capture_output=True,
			text=True,
			timeout=SUBAGENT_TIMEOUT,
		)
	except FileNotFoundError:
		log("claude CLI not on PATH; cannot auto-save plan")
		notify(f"Save failed: {plan_title}", subtitle="claude CLI not on PATH")
		return 0
	except subprocess.TimeoutExpired:
		log(f"claude -p timed out after {SUBAGENT_TIMEOUT}s")
		notify(f"Save failed: {plan_title}", subtitle=f"sub-agent timed out after {SUBAGENT_TIMEOUT}s")
		return 0
	except Exception as exc:
		log(f"claude -p raised {exc!r}")
		notify(f"Save failed: {plan_title}", subtitle=f"{type(exc).__name__}")
		return 0

	log(f"claude -p exit={result.returncode}")
	if result.stdout.strip():
		log(f"stdout head: {result.stdout[:500]!r}")
	if result.stderr.strip():
		log(f"stderr head: {result.stderr[:500]!r}")

	outcome, detail = _interpret_subagent_output(result.stdout, result.returncode)
	if outcome == "ok":
		notify(f"Plan saved: {plan_title}", subtitle=f"Palantir plan #{detail}" if detail else "Saved to Palantir")
	else:
		notify(f"Save failed: {plan_title}", subtitle=detail or "see log")
	return 0


_H1_RE = re.compile(r"^\s*#\s+(.+?)\s*$", re.MULTILINE)
_DONE_RE = re.compile(r"PALANTIR_AUTOSAVE_DONE:\s*(\S+)")
_FAIL_RE = re.compile(r"PALANTIR_AUTOSAVE_FAILED:\s*(.+?)\s*$", re.MULTILINE)


def _first_title(plan: str) -> str:
	m = _H1_RE.search(plan)
	if m:
		return m.group(1)[:80]
	for line in plan.splitlines():
		s = line.strip()
		if s:
			return s[:80]
	return "Approved plan"


def _interpret_subagent_output(stdout: str, exit_code: int) -> tuple[str, str | None]:
	"""Return (outcome, detail) from sub-agent stdout.

	outcome is 'ok' or 'fail'. detail is plan_id on success or short reason on
	failure (may be None). Prefers explicit markers over exit code.
	"""
	if stdout:
		done = _DONE_RE.search(stdout)
		if done:
			return "ok", done.group(1)
		fail = _FAIL_RE.search(stdout)
		if fail:
			return "fail", fail.group(1)[:120]
	if exit_code == 0:
		# No marker but sub-agent exited cleanly — treat as likely success
		# (skill may have printed a markdown table without the marker).
		return "ok", None
	return "fail", f"exit {exit_code}"


if __name__ == "__main__":
	try:
		sys.exit(main())
	except Exception as exc:
		log(f"unhandled: {exc!r}")
		sys.exit(0)
