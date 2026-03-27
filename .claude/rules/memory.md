# Palantir Memory Rules

These rules are mandatory for all sessions in projects connected to Palantir.

## Environment

- `$PALANTIR_API_URL` — base URL (e.g., `http://palantir.local`)
- `$PALANTIR_API_KEY` — auth token
- `$PALANTIR_PROJECT_NAME` — project identifier (auto-set by sync.sh)

All curl commands use these env vars directly. No hardcoded values.

## System Overview

| Component | Trigger | What it does |
|-----------|---------|--------------|
| **PreCompact hook** | Before context compression | Atomizes full session into discrete entries with BLUFs (model: sonnet) |
| `/atomize-session` | Manual | Same as PreCompact — atomize current session on demand |
| `/atomize-me` | Manual | Atomize user-provided text or file into grouped entries |
| `/recall` | Auto or manual | Search Palantir for past decisions, findings, errors, patterns, and related tasks |
| `/task` | Manual | Create, update status, or add context entries to tasks |

Atomization rules are in `$CLAUDE_PROJECT_DIR/.claude/rules/palantir/atomize.md`. 
Full API reference in `$CLAUDE_PROJECT_DIR/.claude/rules/palantir/api.md`.

## When to Act Manually

### Targeted search mid-session

When you need specific past context (e.g., "how did we handle X before?"), search Palantir:

```bash
curl -s "$PALANTIR_API_URL/v1/search" \
  -H "Authorization: Bearer $PALANTIR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "DESCRIBE_WHAT_YOU_NEED", "project": "'$PALANTIR_PROJECT_NAME'", "limit": 5}'
```

### Explicit user request to store something

If the user says "remember this" or explicitly asks to store something, use:

```bash
curl -s "$PALANTIR_API_URL/v1/entries" \
  -H "Authorization: Bearer $PALANTIR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"content": "WHAT_TO_STORE", "bluf": "ONE_SENTENCE_SUMMARY", "kind": "KIND", "project": "'$PALANTIR_PROJECT_NAME'"}'
```

Entry kinds: `decision`, `finding`, `error`, `pattern`, `note`, `review`.

### Task status updates

When work on a task is completed or blocked:

```bash
curl -s "$PALANTIR_API_URL/v1/tasks/TASK_ID" -X PATCH \
  -H "Authorization: Bearer $PALANTIR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"status": "NEW_STATUS"}'
```

Task statuses: `planning`, `ready`, `wip`, `review`, `done`, `blocked`, `archived`.

### Task search

To find a task by topic/title semantically:

```bash
curl -s "$PALANTIR_API_URL/v1/tasks/search" \
  -H "Authorization: Bearer $PALANTIR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "DESCRIBE_TASK", "project": "'$PALANTIR_PROJECT_NAME'", "limit": 5}'
```