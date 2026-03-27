Context is about to be compressed. Atomize the full session into discrete knowledge entries to preserve before compression.

## Rules

Follow the atomization rules in `rules/palantir/atomize.md`:
- One topic per entry — if two sentences needed to describe what it's "about," split it
- BLUF: 1-2 standalone sentences, direct answer to the core question
- Body: 200-400 words with enough context for future use
- Kind: `decision`, `finding`, `error`, `pattern`, or `note`
- Tags: lowercase, hyphenated, 2-4 per entry
- If no meaningful content, do nothing silently

## Process

1. Review the entire conversation for decisions, findings, errors, and reusable patterns
2. Create one entry per distinct topic
3. Generate a BLUF for each entry
4. Include one `note` entry with a session summary (tags: `session-summary`, `pre-compact`)
5. POST all entries in a single bulk request (server auto-groups them via `group_id`)

## Storage

```bash
curl -s "$PALANTIR_API_URL/v1/entries/bulk" \
  -H "Authorization: Bearer $PALANTIR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"entries": [{"content": "BODY", "bluf": "BLUF", "kind": "KIND", "project": "'$PALANTIR_PROJECT_NAME'", "tags": ["tag1", "tag2"]}]}'
```