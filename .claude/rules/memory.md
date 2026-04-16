# Palantir Memory Rules

These rules apply to all sessions in projects connected to Palantir.

## System Overview

| Component | Trigger | What it does |
|-----------|---------|--------------|
| **PreCompact hook** | Before context compression | Atomizes full session into discrete entries with BLUFs |
| **PostToolUse hook** | After plan approval (ExitPlanMode) | Reminds Claude to save approved plan to Palantir |
| **palantir skill** | Manual or auto-invoked | Middleware for all Palantir operations — enforces atomization |

## When to Act

### Storing knowledge
Invoke the `palantir` skill whenever the user asks to store, log, or remember something. The skill handles atomization, deduplication, and submission.

### Searching past knowledge
Invoke the `palantir` skill when the user asks about previous work, past decisions, or how something was handled before.

### After plan approval
The PostToolUse hook on ExitPlanMode automatically reminds Claude to save the plan. Follow the Plan Protocol in the palantir skill.

### Task management
Use the `palantir` skill's Task Protocol to create, update, or add context to tasks.
