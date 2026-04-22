# Palantir Memory Rules

These rules apply to all sessions in projects connected to Palantir.

## System Overview

| Component | Trigger | What it does |
|-----------|---------|--------------|
| **PreToolUse hook** | Every `Bash` tool call | Auto-approves Bash commands that invoke only the Palantir CLI (bare `palantir`, `${CLAUDE_PLUGIN_ROOT}/.claude/bin/palantir`, or an absolute cache-dir path), optionally fed by a safe reader (`echo`/`cat`/`printf`) through a single pipe. Everything else — chains, redirects, subshells, dangerous verbs, unrelated commands — defers to Claude Code's normal permission flow. Effect: no per-call permission prompts for Palantir skill invocations after the plugin is installed, no user settings edit required. |
| **PreCompact hook** | Before context compression | Atomizes full session into discrete entries with BLUFs |
| **PostToolUse hook** | After plan approval (ExitPlanMode) | Writes the approved plan to a temp file and returns `hookSpecificOutput.additionalContext` JSON that instructs the main session's Claude to invoke the palantir skill's Plan Protocol against that file, atomize, and save via `plan save` with an idempotent `dedupe_key`. The hook itself does no LLM work and no subprocess spawning; it is pure plumbing. Progress is logged to `$TMPDIR/palantir-plan-hook.log`. |
| **palantir skill** | Manual or auto-invoked | Middleware for all Palantir operations — enforces atomization |

## When to Act

### Storing knowledge
Invoke the `palantir` skill whenever the user asks to store, log, or remember something. The skill handles atomization, deduplication, and submission.

### Searching past knowledge
Invoke the `palantir` skill when the user asks about previous work, past decisions, or how something was handled before.

### After plan approval
The PostToolUse hook on ExitPlanMode injects a system reminder via `hookSpecificOutput.additionalContext` telling the main session's Claude to save the plan to Palantir as its next action. Claude reads the plan from the temp file the hook writes, invokes the palantir skill's Plan Protocol (proper atomization per `rules/atomize.md`), and saves via `plan save` with the supplied `dedupe_key` (so retries upsert rather than duplicate). No background subprocess, no subagent, no Anthropic Messages API call — the main session's Claude is the atomization brain. Hook trace: `$TMPDIR/palantir-plan-hook.log`.

### Task management
Use the `palantir` skill's Task Protocol to create, update, or add context to tasks.
