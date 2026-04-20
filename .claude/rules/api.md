# Palantir API Reference

All Palantir operations go through a single CLI at `${CLAUDE_PLUGIN_DIR}/.claude/bin/palantir`. Use
it exclusively — do not call the REST API directly with curl. Any agent (Claude Code, Codex,
Gemini, etc.) can invoke the same CLI; credentials persist at `~/.config/palantir/credentials.json`
so one login covers every agent on the same machine.

## CLI Commands

### Tags

```bash
# Always call before creating entries to reuse existing tags
"${CLAUDE_PLUGIN_DIR}/.claude/bin/palantir" tag list [--q <prefix>] [--limit <n>]
"${CLAUDE_PLUGIN_DIR}/.claude/bin/palantir" tag create --name <name>
```

### Search

```bash
# Semantic search across knowledge entries
"${CLAUDE_PLUGIN_DIR}/.claude/bin/palantir" search knowledge \
  --query <q> [--kind <k>] [--tag <name>]... [--mode hybrid|content|bluf] [--limit <n>] [--raw]

# Search tasks by title
"${CLAUDE_PLUGIN_DIR}/.claude/bin/palantir" search tasks \
  --query <q> [--status <s>] [--tag <name>]... [--due-lte <d>] [--due-gte <d>] [--limit <n>] [--raw]
```

### Entries

```bash
# Create a single entry
"${CLAUDE_PLUGIN_DIR}/.claude/bin/palantir" entry create \
  --bluf <text> --content <text> [--kind <k>] [--tag <name>]... [--task-id <id>]

# Create with long content via stdin (avoids argv length limits)
echo "..." | "${CLAUDE_PLUGIN_DIR}/.claude/bin/palantir" entry create \
  --bluf <text> --stdin [--kind <k>] [--tag <name>]...

# Bulk create from JSON file: {"entries":[{content,bluf,kind,tags},...]}
"${CLAUDE_PLUGIN_DIR}/.claude/bin/palantir" entry bulk --file <path>

# Get a single entry by ID
"${CLAUDE_PLUGIN_DIR}/.claude/bin/palantir" entry get <id>

# List entries with optional filters
"${CLAUDE_PLUGIN_DIR}/.claude/bin/palantir" entry list \
  [--kind <k>] [--tag <name>]... [--plan-id <id>] [--task-id <id>] [--limit <n>] [--offset <n>]
```

### Plans

```bash
# Save an approved plan with atomized entries
"${CLAUDE_PLUGIN_DIR}/.claude/bin/palantir" plan save \
  --title <t> --content <text> --entries-file <path> [--tag <name>]... [--dedupe-key <k>]

# Get a plan by ID
"${CLAUDE_PLUGIN_DIR}/.claude/bin/palantir" plan get <id>

# List plans
"${CLAUDE_PLUGIN_DIR}/.claude/bin/palantir" plan list [--query <q>] [--tag <name>]... [--limit <n>]
```

### Tasks

```bash
# Create a task
"${CLAUDE_PLUGIN_DIR}/.claude/bin/palantir" task create \
  --title <t> [--status <s>] [--tag <name>]... [--due-date <d>]

# Get a task by ID
"${CLAUDE_PLUGIN_DIR}/.claude/bin/palantir" task get <id>

# Update a task
"${CLAUDE_PLUGIN_DIR}/.claude/bin/palantir" task update <id> \
  [--status <s>] [--title <t>] [--tag <name>]... [--due-date <d>]

# List tasks
"${CLAUDE_PLUGIN_DIR}/.claude/bin/palantir" task list \
  [--status <s>] [--tag <name>]... [--due-lte <d>] [--due-gte <d>] [--limit <n>]
```

### Auth

Auth is handled by the palantir skill's **Auth Protocol** — do not prompt the user to run these
commands. When any CLI call prints `[PALANTIR_LOGIN_REQUIRED]`, or when the user says "log me in",
invoke the palantir skill and follow `references/auth-protocol.md`. The skill runs `palantir login`
in the background on the user's behalf and surfaces only the authorization URL they need to click.
Logout stays on the `ask` permission list because it revokes tokens.

```bash
# Invoked by the skill, not by the user:
"${CLAUDE_PLUGIN_DIR}/.claude/bin/palantir" login     # allowed — run by the Auth Protocol
"${CLAUDE_PLUGIN_DIR}/.claude/bin/palantir" logout    # asks — user confirms each time
```

## Entry Kinds
`decision` | `finding` | `error` | `pattern` | `note` | `review` | `machine-plan`

## Task Statuses
`planning` | `ready` | `wip` | `review` | `done` | `blocked` | `archived`

## Search Modes
- `hybrid` (default) — fuses content + BLUF embeddings via Reciprocal Rank Fusion
- `content` — content embeddings only
- `bluf` — BLUF embeddings only

## Environment Variables
- `PALANTIR_API_URL` — API base URL (required if not stored in credentials.json)
- `PALANTIR_CONFIG_DIR` — override default `~/.config/palantir`

## Agent-agnostic invocation

Other agents can call the same CLI directly without the launcher:

```bash
python3 "${PALANTIR_PLUGIN_DIR}/.claude/bin/cli.py" <group> <verb> [flags]
```

Or, if `.claude/bin/` is on PATH:

```bash
palantir <group> <verb> [flags]
```
