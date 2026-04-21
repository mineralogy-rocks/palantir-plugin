# Palantir Memory Rules

These rules apply to all sessions in projects connected to Palantir.

## System Overview

| Component | Trigger | What it does |
|-----------|---------|--------------|
| **PreCompact hook** | Before context compression | Atomizes full session into discrete entries with BLUFs |
| **PostToolUse hook** | After plan approval (ExitPlanMode) | Fires `async: true`; launches `claude -p` in the background to run the palantir skill's Plan Protocol on the approved plan. Emits OS notifications at start and finish (`osascript` on macOS, `notify-send` on Linux; disable with `PALANTIR_HOOK_NOTIFY=0`). Does not wake or block the parent session. |
| **palantir skill** | Manual or auto-invoked | Middleware for all Palantir operations — enforces atomization |

## When to Act

### Storing knowledge
Invoke the `palantir` skill whenever the user asks to store, log, or remember something. The skill handles atomization, deduplication, and submission.

### Searching past knowledge
Invoke the `palantir` skill when the user asks about previous work, past decisions, or how something was handled before.

### After plan approval
The async PostToolUse hook on ExitPlanMode auto-saves the plan in the background via a headless `claude -p` sub-agent that runs the Plan Protocol. No action required from the parent session — keep implementing. If the user explicitly asks you to save the plan (or the hook logs a failure at `$TMPDIR/palantir-plan-hook.log`), invoke the palantir skill directly; using the same dedupe-key will upsert rather than duplicate the plan.

### Task management
Use the `palantir` skill's Task Protocol to create, update, or add context to tasks.
