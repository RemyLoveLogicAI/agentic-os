# pen.dev (Pencil) — Setup & MCP Integration

**Product name:** Pencil (by High Agency, Inc.)  
**Official sources:** https://pen.dev · https://docs.pen.dev/core-concepts/ai-agents · https://docs.pencil.dev/getting-started/ai-integration  
**Date checked:** 2026-10-18  
**Status:** Installation documented; MCP live-testing blocked in this remote container (no display — see Blockers)

---

## What pen.dev / Pencil Is

Pencil is an AI-native design tool for `.pen` design files. It stores designs as structured JSON
alongside code (rather than in a cloud database), and exposes its capabilities to external AI agents
through an MCP stdio server backed by the running desktop app or IDE extension.

**Key distinction:** `.pen` documents are code-adjacent JSON files that live in your repository,
making design-to-code workflows tightly integrated with version control.

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Pencil desktop app OR IDE extension | macOS / Windows / Linux desktop supported |
| A `.pen` document open | The MCP server operates on the active document |
| An agent client (Claude Code, Cursor, etc.) | Configured via Settings → MCP in Pencil |
| Pencil account + model-provider API key | Configured in Settings → Agents |

---

## Installation

### 1 — Install the Pencil app or extension

**Desktop app (recommended):**  
Download from https://pen.dev for your OS.  
Linux desktop is supported (requires a display / Wayland or X11 session).

**IDE extension:**  
Search for "Pencil" in your IDE's extension marketplace (VS Code, JetBrains).

### 2 — Open a .pen document

Create or open the `.pen` file the agent should work in.

### 3 — Enable your agent client in Pencil

1. Open Pencil Settings (⚙️) → **MCP**
2. Enable the external client you are using (Claude Code, Cursor, etc.)
3. Pencil generates the configuration automatically

### 4 — Reload the agent client

Restart the agent client session. Confirm `pencil` appears in the MCP server list:

```
/mcp
```

### 5 — Call read_skill() immediately

Per Pencil's external-agent documentation, `read_skill()` must be the **first tool call in every
new session**. Do not call any other Pencil tool before this.

```
read_skill()    → loads Pencil's official design instructions into this session
```

After `read_skill()` returns, read every file it references before proceeding.

---

## MCP Transport

- **Type:** stdio — local Unix socket (macOS/Linux) or named pipe (Windows)
- **Executable path:** Resolved automatically by Pencil during the MCP setup flow
- **Authentication:** No separate MCP auth; the running desktop session is the credential

---

## MCP Tools

| Tool | Purpose |
|---|---|
| `read_skill()` | **Load design instructions** — call first in every session |
| `get_style` | Read styling properties, tokens, and theme values |
| `get_app_state` | Read current document state (layers, frames, selections) |
| `execute` | Apply design operations to the active document |
| `browser` | Open/navigate browser panels (desktop app only) |
| `spawn_agents` | Multi-agent coordination; requires `-enable_spawn_agents` server flag |

---

## Project Integration

`.pen` files are JSON — commit them to version control alongside the code they describe:

```
apps/
  design/
    agent-dashboard.pen    ← design document
    design-tokens.pen      ← token library
```

---

## Reconnecting / Restarting

1. Ensure Pencil is open with the target `.pen` document
2. Reload the agent client session
3. Call `read_skill()` again — prior instruction context does not persist across sessions

---

## Known Limitations

- **Requires running desktop/IDE app.** No cloud-hosted MCP endpoint.
- **Document-scoped.** Server operates on the frontmost/active `.pen` document.
- **`spawn_agents` requires flag.** Pass `-enable_spawn_agents` when starting Pencil.
- **`browser` tool desktop-only.** Not available via IDE extension.

---

## Blockers for This Remote Session

This documentation was prepared in a headless remote cloud container (no display).

| Blocker | Required human action |
|---|---|
| No display in container | Run Pencil on local machine or Linux desktop with Wayland/X11 |
| No `pen` CLI detected | Install Pencil desktop app and enable MCP in Settings |
| MCP stdio requires running process | Open Pencil desktop with a `.pen` document |
| `read_skill()` instructions not loaded | Call in a live session after connection |
| Live MCP testing unverified | Run a Claude Code desktop session alongside Pencil |

**Status: installed but unverified** — documentation complete; live MCP tests must run locally.
