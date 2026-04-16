# Palantir API Reference

When Palantir MCP tools are available (`mcp__palantir-mcp__*`), use them directly instead of curl commands. The MCP tools handle authentication and project scoping automatically.

## MCP Tools

### Search
- `search_knowledge(query, kind?, tags?, plan_id?, task_id?, search_mode="hybrid", limit=5)`
- `search_tasks(query, status?, tags?, due_date_lte?, due_date_gte?, limit=5)`

### Entries
- `create_entry(content, bluf, kind="note", tags?, task_id?)`
- `create_entries_bulk(entries)` — each entry: {content, bluf, kind, tags, task_id?}
- `get_entry(entry_id)`
- `list_entries(kind?, tags?, plan_id?, task_id?, group_id?, limit=20, offset=0)`

### Plans
- `save_approved_plan(title, content, entries, tags?, dedupe_key?)` — each entry: {content, bluf, kind="machine-plan", tags}
- `get_plan(plan_id)`
- `list_plans(tags?, limit=20, offset=0)`

### Tasks
- `create_task(title, status="planning", tags?, due_date?)`
- `get_task(task_id)`
- `update_task(task_id, status?, title?, tags?, due_date?)`
- `list_tasks(status?, tags?, due_date_lte?, due_date_gte?, limit=20, offset=0)`

### Tags
- `list_tags(q?, limit=50)` — always call before creating entries

## Entry Kinds
`decision` | `finding` | `error` | `pattern` | `note` | `review` | `machine-plan`

## Task Statuses
`planning` | `ready` | `wip` | `review` | `done` | `blocked` | `archived`

## Search Modes
- `hybrid` (default) — fuses content + BLUF embeddings via Reciprocal Rank Fusion
- `content` — content embeddings only
- `bluf` — BLUF embeddings only
