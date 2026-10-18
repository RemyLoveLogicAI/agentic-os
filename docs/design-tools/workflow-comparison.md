# Paper vs pen.dev — Design Tool Workflow Comparison

**Date:** 2026-10-18  
**Note:** Based on documentation research only; live parity testing pending local setup.

---

## At a Glance

| Dimension | Paper | pen.dev (Pencil) |
|---|---|---|
| **Format** | Proprietary (cloud/local) | `.pen` JSON files in repo |
| **Platform** | macOS, Windows (no Linux desktop) | macOS, Windows, Linux desktop |
| **MCP transport** | stdio (`paper mcp`) + legacy HTTP | stdio (Unix socket / named pipe) |
| **Agent init** | Plugin install, then `/mcp` | `read_skill()` required first |
| **Version control** | Via Paper's own sync | Native — `.pen` files are JSON |
| **Design tokens** | Supported | Supported (`get_style`) |
| **Code export** | `get_code` → CSS/React/HTML | `execute` + design-to-code (verify live) |
| **Multi-agent** | Not documented | `spawn_agents` (flag required) |
| **Linux support** | ❌ (WSL workaround only) | ✅ (requires display) |
| **Remote/headless** | ❌ | ❌ |

---

## Workflow Fit by Task

### UI/Component Design → Code

**Paper:** Strong code-generation story. Best for handoff-style workflows where design is the
source of truth and code is generated from it.

**Pencil:** Native code-adjacent workflow — `.pen` files live next to the code they describe.
Better fit when design and implementation evolve together in the same repository.

**Recommendation for this repo:** Pencil (`agentic-os` is code-first; `.pen` files version-control
alongside Python/TypeScript). Paper for standalone design deliverables intended for handoff.

### Design Token Systems

Both tools support tokens. Pencil's token storage in `.pen` JSON makes tokens version-diffable
alongside code. Paper is better for cross-project consistency across a shared design system.

### Agent-Driven Design Iteration

**Pencil:** `spawn_agents` (when enabled) supports parallel agent work on separate documents.
Better for large-scale agentic workflows in this repository.

### Design Review / Visual Inspection

Both require the desktop app for visual inspection. Neither has a cloud rendering endpoint
accessible from a remote agent session.

---

## Recommended Tool by Workflow

| Workflow | Recommended tool |
|---|---|
| Agent dashboard UI design | **Pencil** (`.pen` files version-controlled with the code) |
| Standalone marketing / brand assets | **Paper** (stronger design canvas, better export) |
| Design-to-code in CI/CD | **Pencil** (JSON-based, diffable, repo-native) |
| Cross-project shared design system | **Paper** (cloud sync across repositories) |

---

## Session Startup Comparison

**Paper:**
1. Ensure Paper Desktop is open
2. Start Claude Code session — plugin loads automatically
3. Begin working (no required first tool call)

**Pencil:**
1. Ensure Pencil is open with the target `.pen` file
2. Start Claude Code session
3. **Call `read_skill()` immediately** before any other tool call
4. Read all referenced instruction files

---

## Untested Capabilities (require live sessions)

- Paper: actual tool names and schemas, code export quality, visual inspection fidelity
- Pencil: `read_skill()` return schema, referenced instruction file structure, `.pen` JSON format
- Both: multi-document workflows, complex component libraries, animation/motion support
