---
description: Atomize user-provided text or file into discrete knowledge entries and store in Palantir
argument_hint: "<text or file path>"
model: sonnet
allowed-tools: Bash(curl *), Bash(echo *), Read, Grep
context: fork
---

# /atomize-me

Atomize user-provided content (meeting notes, daily notes, plans, documents) into discrete knowledge entries. All entries from the same atomization are automatically grouped by the server via `group_id`.

## Input Resolution

- If the argument is a file path, read the file contents first
- Otherwise, treat the argument as raw text to atomize

## Rules

Follow the atomization rules in `${CLAUDE_PLUGIN_ROOT}/.claude/rules/atomize.md`:

## Process

1. Read and understand the provided content
2. Identify distinct topics, decisions, findings, and patterns
3. Create one entry per topic with a BLUF and appropriate kind
4. POST all entries via the bulk endpoint (server auto-assigns a shared `group_id`)

## Storage

```bash
curl -s "$PALANTIR_API_URL/v1/entries/bulk" \
  -H "Authorization: Bearer $PALANTIR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"entries": [{"content": "BODY", "bluf": "BLUF", "kind": "KIND", "project": "'$PALANTIR_PROJECT_NAME'", "tags": ["tag1", "tag2"]}]}'
```

If no meaningful content exists, say so and do nothing.