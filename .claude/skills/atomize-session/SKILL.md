---
description: Atomize the current session into discrete knowledge entries and store in Palantir
model: sonnet
allowed-tools: Bash(curl *), Bash(echo *), Read, Grep
---

# /atomize-session

Review the entire conversation for noteworthy content and atomize it into discrete knowledge entries. All entries from the same session are automatically grouped by the server via `group_id`.

## Rules

Follow the atomization rules in `${CLAUDE_PLUGIN_ROOT}/.claude/rules/atomize.md`:

## Process

1. Scan the full conversation for decisions, findings, errors, and reusable patterns
2. Create one entry per distinct topic — do not combine multiple items
3. Generate a BLUF for each entry
4. Include one `note` entry with a session summary (tags: `session-summary`)
5. POST all entries via the bulk endpoint

## Storage

```bash
curl -s "$PALANTIR_API_URL/v1/entries/bulk" \
  -H "Authorization: Bearer $PALANTIR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"entries": [{"content": "BODY", "bluf": "BLUF", "kind": "KIND", "project": "'$PALANTIR_PROJECT_NAME'", "tags": ["tag1", "tag2"]}]}'
```

If no meaningful content exists, say so and do nothing.