# Search Protocol

Use this when the user wants to recall past knowledge, find related context, or investigate
how something was handled before.

> **Required reading**: `../../rules/api.md` (MCP tool reference — search modes, parameters)

## Step 1 — Search

Choose the search mode based on the query (see `../../rules/api.md` for details):
- **`hybrid`** (default): Best for general queries. Fuses content and BLUF embeddings via
  Reciprocal Rank Fusion.
- **`bluf`**: When looking for high-level summaries or scanning for a topic.
- **`content`**: When looking for specific implementation details or code-level context.

Use `search_knowledge(query, kind?, tags?, plan_id?, task_id?, search_mode, limit)`.

Also search tasks if the query might relate to tracked work:
`search_tasks(query, status?, tags?, due_date_lte?, due_date_gte?, limit)`.

## Step 2 — Follow links

For results with a `group_id`, consider fetching siblings via
`list_entries(group_id=...)` to get the full atomization batch.

For results with `related_ids`, consider fetching those entries via `get_entry(id)` to discover
connected knowledge.

For results with a `task_id`, fetch the task via `get_task(id)` to show the work context.

Limit link-following to avoid noise: max 2 group fetches, 3 related entry fetches, 3 task fetches.

## Step 3 — Present results

Always present results as a markdown table for quick scanning, followed by detail sections.

### Results table

Start with a summary table of all results:

```markdown
Found N entries related to "query":

| # | Kind | BLUF | Tags | Date |
|---|------|------|------|------|
| #42 | decision | We chose Pinia over Vuex for state management | `nuxt`, `migration` | 2026-04-10 |
| #38 | finding | N+1 query on indicators caused 2.3s response times | `django`, `performance` | 2026-04-08 |
| #35 | error | OAuth flow fails when redirect URI has trailing slash | `auth`, `dpa-mcp` | 2026-04-05 |
```

### Tasks table (if any)

If tasks were found, present them separately:

```markdown
Related tasks:

| # | Status | Title | Entries | Date |
|---|--------|-------|---------|------|
| #22 | wip | TAU migration into gtaapi | 5 | 2026-04-12 |
| #16 | done | DPA MCP Server launch | 8 | 2026-03-28 |
```

### Detail sections

After the table, expand on results only if the user needs more context. Use collapsible
sections or bullet points per entry:

```markdown
**#42 [decision]** We chose Pinia over Vuex for state management
> Pinia was selected because it has first-class TypeScript support, a simpler API
> without mutations, and is the officially recommended library for Vue 3...
> Tags: `nuxt`, `migration` · Related: #38, #40 · Task: #22
```

### No results

If nothing was found:

```markdown
No entries found in Palantir for "query". Consider checking:
- Different search terms or synonyms
- Broader tags
- Whether this knowledge has been stored yet
```
