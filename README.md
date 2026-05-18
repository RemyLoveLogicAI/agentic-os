# Agentic OS

> A voice-native operating system for the Agentic Web.

**One loop**: speak → route → approve → act → verify → remember.

---

## Table of Contents

- [What It Is](#what-it-is)
- [Why It Exists](#why-it-exists)
- [Quickstart](#quickstart)
- [Core Loop](#core-loop)
- [System Layers](#system-layers)
- [Architecture](#architecture)
- [Status](#status)
- [Deliverables](#deliverables)
- [Philosophy](#philosophy)
- [Token-Based Roadmap](#token-based-roadmap)
- [Publish Checklist](#publish-checklist)

---

## What It Is

Agentic OS is a layered control system that turns spoken intent into verified action.

It combines:
- **Spokenly** — voice clarification and MCP-driven question capture
- **Voice Orion** — deterministic command parsing and approval gates
- **Command Palette** — fast command discovery and selection
- **DLAM / R1** — desktop and machine control
- **OpenClaw** — orchestration and multi-agent coordination
- **R.I.P.** — canonical memory and identity
- **Knowledge Graph** — operational context
- **Aegis / Violet Covenant** — governance and trust policy
- **zopack** — portable bundles
- **glyphy pets / CYOA** — ambient state and narrative UX

---

## Why It Exists

Most agent stacks fail in three places:

1. They cannot ask clarifying questions reliably.
2. They cannot execute safely across desktop and API surfaces.
3. They cannot remember what happened in a canonical, auditable way.

Agentic OS closes all three gaps.

---

## Quickstart

### Prerequisites

- [Bun](https://bun.sh) v1.1+

### Install & Run

```bash
# Clone
git clone https://github.com/RemyLoveLogicAI/agentic-os.git
cd agentic-os

# Install dependencies
bun install

# Start the operator console
bun run dev
# → http://localhost:4200

# Run tests
bun test

# Submit a command via API
curl -X POST http://localhost:4200/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "check status"}'
```

### Read the Spec

```bash
open spec-pack/README.md
```

### Understand the Loop

1. Human speaks or types a request.
2. Command edge classifies intent.
3. Governance decides if the action is safe.
4. Execution plane performs the action.
5. Evidence is captured.
6. Memory is updated.
7. System learns for the next round.

### Build Phase-0

See `spec-pack/phase-0-build-plan.md` for the first shippable slice.

---

## Core Loop

```
┌─────────────┐
│   Human     │
│  speaks or  │
│   types     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Voice Edge  │  ← Spokenly MCP
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Command     │  ← Voice Orion + Command Palette
│ Router      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Policy /    │  ← Aegis + Violet Covenant
│ Approval    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Execution   │  ← DLAM / R1 + API adapters
│ Plane       │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Evidence    │  ← Logs, artifacts, receipts
│ Capture     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Memory /    │  ← R.I.P. + Knowledge Graph
│ Identity    │
└──────┬──────┘
       │
       └──────────────────────┐
                              │
                              ▼
                    ┌─────────────┐
                    │ Orchestration│  ← OpenClaw + peers
                    │ Mesh         │
                    └─────────────┘
```

---

## System Layers

| Layer | Purpose | Key Artifacts |
|---|---|---|
| Voice edge | Human input, dictation, clarification | Spokenly MCP |
| Desktop edge | Physical machine control | tmux, VS Code browser, SSH |
| Command edge | Discovery, classification, routing | Voice Orion, Command Palette |
| Execution edge | CLI, API, browser, shortcut actions | DLAM / R1, Zo API |
| Orchestration mesh | Multi-agent coordination | OpenClaw, peer coordination |
| Memory and identity | Canonical truth, history, claims | R.I.P., Knowledge Graph |
| Governance and verification | Approval gates, evidence checks | Aegis, Violet Covenant |
| Productization and packaging | Reusable, portable bundles | zopack |
| Ambient state and storytelling | Visible, memorable UX | glyphy pets, CYOA |

---

## Architecture

See `spec-pack/assets/` for diagrams:

- `agentic-os-architecture.png` — layer overview
- `agentic-os-phase0-flow.png` — phase-0 execution flow
- `agentic-os-repo-layout.png` — folder topology
- `agentic-os-docs-pack.png` — doc structure

---

## Status

This repo is the **spec and operating narrative**.

Implementation follows a phase-0 slice:

- [x] Voice clarification loop
- [x] Deterministic router
- [x] Approval gate
- [x] One safe desktop action
- [x] One safe API action
- [x] Evidence logging
- [x] Operator console

---

## Deliverables

| File | Purpose |
|---|---|
| `README.md` | This document |
| `spec-pack/README.md` | Pack overview |
| `spec-pack/master-spec.md` | Canonical system contract |
| `spec-pack/deployment-blueprint.md` | Deployment stages |
| `spec-pack/phase-0-build-plan.md` | First slice |
| `spec-pack/repo-layout.md` | Folder structure |
| `spec-pack/assets/*.png` | Architecture diagrams |

---

## Philosophy

- **No proof, no claim.** Evidence required.
- **Prefer reversible decisions.** Keep options open.
- **Keep the first slice thin and real.** Ship, then iterate.
- **Treat memory as a product surface.** It matters.
- **Treat governance as a feature.** Not an afterthought.

---

## Token-Based Roadmap

| Feature | Token Cost | Dependencies | Priority |
|---|---:|---|---|
| Voice clarification via Spokenly | Medium | MCP bridge | P0 |
| Deterministic command routing | Medium | parsing rules | P0 |
| Approval-gated execution | Medium | storage, TTL, operator panel | P0 |
| Memory / identity canon | High | R.I.P., Knowledge Graph | P0 |
| Execution adapters | High | desktop + API integrations | P0 |
| Orchestration mesh | High | OpenClaw, peer coordination | P1 |
| Portable packaging | Medium | zopack | P1 |
| Ambient state layer | Low | glyphy pets, CYOA | P2 |

---

## Publish Checklist

Before publishing:

- [ ] All markdown files render correctly on GitHub
- [ ] Diagrams are visible in `spec-pack/assets/`
- [ ] `README.md` has a clear one-line tagline
- [ ] Quickstart section is actionable
- [ ] Table of contents links work
- [ ] All cross-references resolve
- [ ] Token roadmap is up to date
- [ ] License is included (MIT recommended)
- [ ] `.gitignore` is set for any generated artifacts
- [ ] Repo description matches README intro

After publishing:

- [ ] Add GitHub Topics: `agents`, `voice`, `mcp`, `operating-system`, `agentic-web`
- [ ] Enable Discussions if community input is welcome
- [ ] Add a `CONTRIBUTING.md` if accepting external contributions
- [ ] Add a `CODE_OF_CONDUCT.md` for community projects
- [ ] Pin the repo if it's a flagship project
- [ ] Add release tags for stable milestones

---

## License

MIT — use freely, attribute kindly.

---

*Built with intent for the Agentic Web.*
