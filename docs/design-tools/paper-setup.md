# Paper Design Tool — Setup & MCP Integration

**Official source:** https://paper.design/docs/mcp  
**Date checked:** 2026-10-18  
**Status:** Installation documented; MCP live-testing blocked (requires local desktop — see Blockers)

---

## What Paper Is

Paper is a vector design tool (macOS / Windows desktop app) that exposes its document-editing
capabilities to AI agents through an MCP stdio server backed by the running Paper Desktop process.
The desktop app IS the MCP server; there is no cloud-hosted or headless mode.

---

## Prerequisites

| Requirement | Notes |
|---|---|
| macOS or Windows | Linux desktop not supported |
| Paper Desktop app | Download from https://paper.design |
| Claude Code CLI | `claude` command in PATH |
| A Paper account | Sign-in inside the app before use |

---

## Installation

### 1 — Install Paper Desktop

Download and install Paper Desktop from https://paper.design.  
Launch it and sign in before proceeding.

### 2 — Install the Claude Code plugin

Run this in a terminal on the machine where Paper Desktop is running:

```bash
claude plugin marketplace add paper-design/agent-plugins
claude plugin install paper-desktop@paper
```

The first command fetches the official Paper plugin from the marketplace.  
The second installs it, binding the running Paper Desktop process via stdio.

### 3 — Connect other agent clients

For clients other than Claude Code (Cursor, Continue, Windsurf, etc.), use Paper Desktop's
built-in **"Connect your agent"** flow:

1. Open Paper Desktop → Preferences → AI Agents  
2. Click **Connect agent** and follow the client-specific steps  
3. The generated config contains the stdio transport command — copy it into the client's MCP config

Generic config template (replace `/path/to/paper` with the actual binary path from the Paper app):

```json
{
  "mcpServers": {
    "paper": {
      "type": "stdio",
      "command": "/path/to/paper",
      "args": ["mcp"]
    }
  }
}
```

**Legacy HTTP transport** (alternative while Desktop is open):
```
http://127.0.0.1:29979/mcp
```
The stdio CLI method is now preferred; use HTTP only as a fallback.

### 4 — Verify the server is live

Open a new Claude Code session and run:

```
/mcp
```

You should see `paper-desktop` in the server list with its tools.

---

## MCP Tools (expected capabilities)

Tool names are discovered at runtime via `/mcp`. Based on official documentation, Paper exposes
capabilities for: document navigation, frame/layer creation and mutation, design token access,
component placement, asset export (PNG/SVG/PDF), and code generation (CSS/React/HTML).

---

## Loading Design Instructions (Skills)

The Claude Code plugin (`paper-design/agent-plugins`) installs a SKILL.md that future sessions
load automatically. For other clients, use the locally authored workflow skill at
`skills/paper-design/SKILL.md` in this repository.

---

## Reconnecting / Restarting

1. Ensure Paper Desktop is running with a document open
2. Restart the Claude Code session (`claude --reload-mcp`)
3. If the plugin is missing: `claude plugin install paper-desktop@paper`

---

## Known Limitations

- **Desktop-only:** No headless or remote mode. Remote cloud agent sessions cannot connect.
- **macOS/Windows only:** Linux not supported (WSL with mirrored networking is a workaround).
- **One document at a time:** The MCP server reflects the frontmost open document.
- **Visual inspection:** Requires the Paper Desktop app on the same machine.

---

## Blockers for This Remote Session

This documentation was prepared in a remote cloud container (Linux, no display).

| Blocker | Required human action |
|---|---|
| Paper Desktop not installed | Install on local macOS/Windows machine |
| No `paper` CLI in PATH | Follows automatically after Desktop install |
| MCP stdio requires local process | Run `claude plugin install paper-desktop@paper` on local machine |
| Live MCP testing unverified | Open a Claude Code desktop session on the machine running Paper Desktop |

**Status: installed but unverified** — documentation complete; live MCP tests must run locally.
