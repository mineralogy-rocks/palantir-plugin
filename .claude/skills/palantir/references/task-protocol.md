# Task Protocol

Tasks are work containers that group related entries and track lifecycle.

> **Required reading**: `../../rules/atomize.md` (for entry creation), `../../rules/api.md` (MCP tool reference)

## Creating a task

1. Search for existing tasks first: `search_tasks(query)`. If a matching task already exists,
   tell the user instead of creating a duplicate.
2. Create with `create_task(title, status, tags?, due_date?)`. Default status is `planning`.
   See `../../rules/api.md` for task statuses.
3. If the user provided substantive context alongside the task request, atomize it into entries
   linked to the new task via `task_id` (follow the Write Protocol and Atomization Rules in
   SKILL.md and `../../rules/atomize.md`).

## Updating a task

1. Resolve the task: if the user gives an ID, use `get_task(id)`. If they describe it by name,
   use `search_tasks(query)` and confirm the match.
2. Update with `update_task(task_id, status?, title?, tags?, due_date?)`.
3. Common transitions: `planning` -> `ready` -> `wip` -> `review` -> `done`.
   Use `blocked` when stalled, `archived` to soft-delete.

## Adding context to a task

When the user has new findings, decisions, or notes for an existing task:
1. Resolve the task (same as updating).
2. Atomize the new content following the Write Protocol, setting `task_id` on each entry.
