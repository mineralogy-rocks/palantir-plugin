# Write Protocol

Use this when storing knowledge — logging a finding, decision, error, pattern, note, or review.

> **Required reading**: `../../rules/atomize.md` (atomization rules), `../../rules/api.md` (MCP tool reference)

## Step 1 — Preflight

Run these two calls in parallel before any write:

1. **Duplicate check**: `search_knowledge` with a query summarizing the content to store. If a
   near-duplicate exists (same topic, same conclusion), tell the user and ask whether to skip,
   update, or create anyway.
2. **Tag inventory**: `list_tags` to get existing tags. Reuse these. Only invent a new tag when
   no existing tag fits.

See `../../rules/api.md` for full tool signatures.

## Step 2 — Atomize

Break the input into discrete knowledge atoms following the Atomization Rules in SKILL.md and
`../../rules/atomize.md`. Key requirements:

- One topic per entry
- Self-contained content (100-400 words)
- Standalone BLUF (1-2 sentences)
- Accurate kind classification (see `../../rules/atomize.md` for the full kind table)
- 2-4 reused tags

Never use `machine-plan` kind here — that kind is reserved for the Plan Protocol.

## Step 3 — Submit

- **Single atom**: Use `create_entry(content, bluf, kind, tags, task_id?)`.
- **Multiple atoms**: Use `create_entries_bulk(entries)`. The server auto-assigns a shared
  `group_id` for traceability. Each entry in the list needs: `content`, `bluf`, `kind`, `tags`,
  and optionally `task_id`.

## Step 4 — Confirm

Present what was stored as a markdown table:

```markdown
Stored N entries (group #GID):

| # | Kind | BLUF | Tags |
|---|------|------|------|
| #92 | finding | N+1 query caused by missing select_related on category FK | `django`, `performance` |
| #93 | decision | Added select_related to IndicatorViewSet queryset | `django-orm`, `api-design` |
```

If cross-references (`related_ids`) were auto-detected, append them:

```markdown
Cross-references detected: #92 → #83, #84
```
