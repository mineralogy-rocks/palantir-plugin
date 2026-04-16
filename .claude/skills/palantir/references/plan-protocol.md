# Plan Protocol

Use this when the user has approved a plan and wants to persist it. Plans are stored as a raw
plan document plus atomized entries derived from it.

> **Required reading**: `../../rules/atomize.md` (atomization rules), `../../rules/api.md` (MCP tool reference)

## Step 1 — Preflight

Same as Write Protocol: search for duplicates (`search_knowledge`) and get the tag inventory
(`list_tags`). Run both in parallel. See `../../rules/api.md` for tool signatures.

## Step 2 — Atomize the plan

Break the approved plan into entries. Each entry should cover one of:
- A discrete decision and its rationale
- An implementation step with enough context to act on independently
- A constraint or requirement that shapes the implementation
- A risk or trade-off that was accepted
- A follow-up or open question

Every atomized entry must use `kind: "machine-plan"`. This kind indicates the entry was
machine-curated from an approved plan. Do not override to `decision`, `finding`, or other kinds
— `machine-plan` is the canonical kind for all plan-derived entries, regardless of whether an
individual entry describes a decision, a risk, or an implementation step.

Every entry needs standalone `content` (100-400 words) and a `bluf` (1-2 sentences). Follow
the Atomization Rules in SKILL.md and `../../rules/atomize.md` — someone reading just one entry
should understand it fully without seeing the rest of the plan.

## Step 3 — Submit

Use `save_approved_plan(title, content, entries, tags?, dedupe_key?)`:
- `title`: Concise plan title
- `content`: The full raw plan text as approved
- `entries`: The atomized entries list, each with `content`, `bluf`, `kind`, `tags`
- `tags`: Plan-level tags
- `dedupe_key`: Provide one when automation may retry (prevents duplicate plans)

See `../../rules/api.md` for the full tool signature.

## Step 4 — Confirm

Present the saved plan as a markdown table:

```markdown
Plan #3 saved: "Bos frontend migration from Nuxt 2 to Nuxt 3"
Tags: `bos`, `nuxt`, `migration` · Dedupe key: `bos-nuxt3-migration-2026`

| # | BLUF | Tags |
|---|------|------|
| #99 | Three-phase migration over 3 sprints covering state, syntax, and UI library | `bos`, `nuxt`, `planning` |
| #100 | Phase 1: Replace Vuex with Pinia stores | `bos`, `nuxt`, `pinia` |
| #101 | Phase 2: Convert Options API to Composition API | `bos`, `nuxt`, `frontend` |
| #102 | Phase 3: Replace sgept-ui with sui3 components | `bos`, `sui3`, `frontend` |
| #103 | Risk accepted: build missing sui3 components incrementally | `bos`, `sui3`, `migration` |
```
