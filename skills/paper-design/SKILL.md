# Paper Design Workflow Skill

> Locally authored workflow skill — based on official documentation (paper.design/docs/mcp, 2026-10-18).
> This is NOT an official Paper plugin skill. For the official skill, install via:
> `claude plugin marketplace add paper-design/agent-plugins && claude plugin install paper-desktop@paper`

## Prerequisites

- Paper Desktop running on this machine (macOS or Windows)
- Paper plugin installed (`claude plugin install paper-desktop@paper`)
- A Paper document open
- `pencil` visible in `/mcp` server list

## Session Startup

1. Confirm Paper Desktop is running and a document is open
2. Verify the MCP server is connected: `/mcp` → look for `paper-desktop`
3. No required initial tool call — tools are available immediately after connection

## First Step: Confirm Document Identity

```
get_document()    → read the current document's identity and structure
```

Always call this first to confirm you are working in the expected document.

## Design Workflow: LoveLogicAI Agent Dashboard

Build four frames in order:

1. **Navigation** — top bar, 1440×64px, brand primary background
2. **Agent Status Cards** — grid, 280×160px per card, 16px gap
3. **Task Queue** — scrollable list panel, 320px wide
4. **Activity Feed** — right column, timestamped event list

### Token System

| Token | Purpose |
|---|---|
| `color.primary` | Brand primary (navigation, CTAs) |
| `color.surface` | Card and panel backgrounds |
| `color.text.primary` | Body text |
| `spacing.base` | 16px base unit |
| `font.body` | 14px / 1.5 line-height |
| `font.heading` | 24px / 1.25 line-height |

### Verification Round-Trip

After any write, read back the layer:
```
get_document() or get_selection()
```
If returned values differ from what was written, wait one tick and read again (writes are async).

## Code Export

```
get_code()       → CSS, React, or HTML from selected layers
export_asset()   → PNG / SVG / PDF from a frame
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| Server not in `/mcp` | Ensure Paper Desktop is open; restart Claude Code |
| Plugin missing | `claude plugin install paper-desktop@paper` |
| Write not reflected | Wait one tick; Paper writes are async to the render layer |

## Full Setup Instructions

`docs/design-tools/paper-setup.md`
