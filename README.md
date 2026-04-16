# Palantir Plugin for Claude Code

A Claude Code plugin that gives your AI assistant persistent memory across sessions.
Stores decisions, findings, errors, and patterns with semantic search and enforced
atomization — so context is never lost when conversations end or compress.

## Prerequisites

You need a running Palantir instance (API + MCP server). Set up from the
[palantir](https://github.com/mineralogy-rocks/palantir) repository:

```bash
git clone https://github.com/mineralogy-rocks/palantir.git
cd palantir
docker-compose up -d
```

## Installation

```bash
claude plugin install github:mineralogy-rocks/palantir-plugin
```

For local development/testing without installing:

```bash
claude --plugin-dir /path/to/palantir-plugin
```

## Configuration

The plugin communicates with Palantir through the **Palantir MCP server**. Add
the MCP server to your project's `.mcp.json`:

```json
{
  "mcpServers": {
    "palantir-mcp": {
      "type": "streamable-http",
      "url": "https://your-palantir-instance.com/mcp/"
    }
  }
}
```

For local development:

```json
{
  "mcpServers": {
    "palantir-mcp": {
      "type": "streamable-http",
      "url": "http://mcp.palantir.local:81/mcp/"
    }
  }
}
```

The MCP server handles OAuth authentication — on first use, it will prompt you
to authorize via GitHub.

To verify the plugin is enabled:

```bash
claude plugin list
```

## What the plugin does

The plugin acts as a middleware layer between the AI agent and Palantir. It enforces
**atomization** — breaking complex knowledge into discrete, standalone,
individually-searchable entries — before anything is written. It also ensures
duplicate checks, tag reuse, correct kind classification, and standalone BLUF summaries.

When a plan is approved in `/plan` mode, a hook automatically injects a reminder
for the agent to save the plan to Palantir before starting implementation.

## Skill

| Skill | Description |
|-------|-------------|
| `/palantir` | Unified middleware for all Palantir operations — stores entries, saves plans, searches knowledge, manages tasks |

The skill routes by intent:

| Intent | Protocol |
|--------|----------|
| Store knowledge ("remember this", "log this") | Write Protocol |
| Save an approved plan | Plan Protocol |
| Search/recall ("what do we know about X") | Search Protocol |
| Create/update tasks | Task Protocol |

## Hook

| Event | Matcher | What it does |
|-------|---------|-------------|
| **PostToolUse** | `ExitPlanMode` | Reminds the agent to save the approved plan to Palantir |

## Plugin structure

```
.claude-plugin/
  plugin.json                          # Plugin manifest (v2.0.0)
  marketplace.json                     # Marketplace listing
.claude/
  skills/palantir/
    SKILL.md                           # Routing + atomization rules + quality checklist
    references/
      write-protocol.md                # Store entries (findings, decisions, errors, etc.)
      plan-protocol.md                 # Save approved plans with machine-plan entries
      search-protocol.md               # Search and recall past knowledge
      task-protocol.md                 # Task lifecycle management
  hooks/
    hooks.json                         # Hook definitions (PostToolUse on ExitPlanMode)
    palantir-plan-reminder.json        # additionalContext payload for plan persistence
  rules/
    atomize.md                         # Shared atomization rules
    api.md                             # MCP tool reference
    memory.md                          # When to use what
```

## How it works

Palantir stores knowledge as **entries** — discrete units covering one topic each.
Each entry has:
- A **BLUF** (Bottom Line Up Front) — 1-2 sentence summary
- **Content** — full context (100-400 words)
- **Kind** — `decision`, `finding`, `error`, `pattern`, `note`, `review`, or `machine-plan`
- **Tags** — for categorization and retrieval

Entries are embedded for semantic search using dual embeddings (content + BLUF)
merged via Reciprocal Rank Fusion.

**Plans** store approved plans with atomized `machine-plan` entries.

**Tasks** group related entries and track work status
(`planning` -> `ready` -> `wip` -> `review` -> `done`).

## Manual hook setup (without the plugin)

If you want plan persistence without installing the full plugin, you can set it up
manually. Add to your project's `.claude/settings.local.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "ExitPlanMode",
        "hooks": [
          {
            "type": "command",
            "command": "cat \"$CLAUDE_PROJECT_DIR/.claude/hooks/palantir-plan-reminder.json\""
          }
        ]
      }
    ]
  }
}
```

Then create `.claude/hooks/palantir-plan-reminder.json`:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "MANDATORY: Before starting implementation, save the approved plan to Palantir. Invoke the palantir skill and follow the Plan Protocol. All atomized entries must use kind: machine-plan. Do NOT skip this step."
  }
}
```

**Why JSON with `additionalContext`?** Plain `echo` output from PostToolUse hooks
goes to the debug log — the agent never sees it. The `additionalContext` field is
what gets injected into the agent's conversation as a system reminder.

## Changes from v1

- **Unified skill**: 4 separate skills (`atomize-me`, `atomize-session`, `recall`,
  `task`) merged into one `palantir` skill with reference protocols
- **MCP tools**: Uses `mcp__palantir-mcp__*` tools instead of curl/REST API calls
- **Plan persistence**: New PostToolUse hook on `ExitPlanMode` replaces the
  PreCompact hook
- **New entry kinds**: Added `review` and `machine-plan`
- **Tag management**: `list_tags` for reuse before creating entries
- **Plans API**: `save_approved_plan` for structured plan storage

## License

MIT
