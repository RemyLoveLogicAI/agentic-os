# pen.dev (Pencil) Design Workflow Skill

> Locally authored workflow skill — based on official documentation (docs.pen.dev, 2026-10-18).
> This is NOT an official Pencil skill. For official desktop-composer skills, see Pencil Settings → Skills.
> For external MCP clients, `read_skill()` loads the official instructions at session start.

## Prerequisites

- Pencil desktop app running (macOS / Windows / Linux desktop with display)
- Pencil MCP enabled for this client (Settings → MCP in Pencil)
- A `.pen` document open
- Agent client reloaded after enabling; `pencil` visible in `/mcp`

## MANDATORY: Session Startup

**Call `read_skill()` as the FIRST tool call in every new session.**
Do not call any other Pencil tool before this.

```
read_skill()    → loads Pencil's official design instructions
```

After `read_skill()` returns, read every file it references before proceeding.

## MCP Tools Quick Reference

| Tool | When to use |
|---|---|
| `read_skill()` | **First call every session** |
| `get_app_state` | Read document state, layers, selections |
| `get_style` | Read color tokens, spacing, typography |
| `execute` | Apply a design operation |
| `browser` | Open/navigate browser panels (desktop only) |
| `spawn_agents` | Multi-agent work (requires `-enable_spawn_agents` flag) |

## Document Location

```
apps/
  design/
    agent-dashboard.pen      ← primary dashboard design
    design-tokens.pen         ← shared token library
```

`.pen` files are JSON — commit them alongside the code they describe.

## Design Workflow: LoveLogicAI Agent Dashboard

Create `apps/design/agent-dashboard.pen` with four sections:

1. **Navigation** — top bar frame
2. **Agent Status Cards** — grid with card components
3. **Task Queue** — scrollable list panel
4. **Activity Feed** — timestamped event list

Use the same token values as the Paper workflow skill for cross-tool comparison:
- Primary: brand primary, Surface: card bg, Body: 14px/1.5, Heading: 24px/1.25

### Verification Round-Trip

```
get_app_state()   → read back after every execute() call
```

Confirm returned values match the intended write. Check the instruction files from `read_skill()`
for any constraints that may affect what values are accepted.

## Reconnecting

If the session disconnects:
1. Ensure Pencil is open with the target `.pen` document
2. Restart the agent session
3. Call `read_skill()` again — prior context does not persist

## Troubleshooting

| Symptom | Fix |
|---|---|
| `pencil` not in `/mcp` | Pencil → Settings → MCP → enable this client |
| `read_skill()` missing | Check Pencil version; do not substitute another call |
| `spawn_agents` unavailable | Start Pencil with `-enable_spawn_agents` flag |
| `browser` unavailable | Only in desktop app, not IDE extension |

## Full Setup Instructions

`docs/design-tools/pen-dev-setup.md`
