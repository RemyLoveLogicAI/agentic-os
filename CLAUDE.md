# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

Agentic OS is a **spec-first** repository whose implementation has started. Alongside architecture specifications, research data, and operational ledgers, the repo now contains runnable code: a root `package.json` + `tsconfig.json` (TypeScript), `apps/zo-super-server/` (Python MCP server), `services/loop-harness/`, `agents/` (durable LangGraph agents under `agents/{trend_arbitrage,social_content,microsaas_factory}` + `agents/shared/`), `skills/task-manager/`, `src/metropolis/` (car-kernel, TypeScript), `docker/`, and `holaos/`. Phase 0 (the first shippable slice) is the active build focus.

**Available commands** (see `package.json`):
- `npm run typecheck` — TypeScript type check (no emit)
- `npm run build:car` — compile `src/metropolis/` via `tsc`
- `npm run example:car` — compile and run the car-kernel example
- `bun run build:task-manager` — build `skills/task-manager/`

Python agents run under `docker/docker-compose.yml` with `restart: on-failure`. `spec-pack/repo-layout.md` defines the target topology (note: `spec-pack/` serves as the docs directory — that file refers to it as `docs/`, but the actual directory is `spec-pack/`).

## Canonical Reading Order

Start here to understand the system:

1. `spec-pack/master-spec.md` — the system contract and nine-layer definition
2. `spec-pack/deployment-blueprint.md` — deployment stages and topology diagram
3. `spec-pack/phase-0-build-plan.md` — current build focus (the proof slice)
4. `spec-pack/repo-layout.md` — planned folder topology
5. `spec-pack/holaos-architecture.md` — HolaOS runbook and workspace architecture

Diagrams live in `spec-pack/assets/` as PNG. The intended convention (per `CONTRIBUTING.md`) is to store D2 source files (`.d2`) alongside rendered PNGs, but no `.d2` sources exist yet.

## Nine-Layer Architecture

The system converts spoken intent into verified, auditable action through nine layers:

| Layer | Purpose | Key Component |
|---|---|---|
| Voice edge | Human speech input and clarification | Spokenly MCP |
| Desktop edge | Physical machine control | tmux, VS Code browser, SSH |
| Command edge | Discovery, classification, routing | Voice Orion, Command Palette |
| Execution edge | CLI, API, browser, shortcut actions | DLAM / R1, Zo API |
| Orchestration mesh | Multi-agent coordination | OpenClaw |
| Memory and identity | Canonical truth and history | R.I.P., Knowledge Graph |
| Governance and verification | Approval gates, evidence checks | Aegis, Violet Covenant |
| Productization and packaging | Reusable portable bundles | zopack |
| Ambient state and storytelling | Visible system health UX | glyphy pets, CYOA |

The core data flow: `Voice → Command Router → Policy/Approval Gate → Execution Plane → Evidence Capture → Memory/Identity`

### Component Name to Code Location

Concept names used in the spec differ from planned folder names. Reference this table when implementing:

| Concept Name | Planned Code Location |
|---|---|
| Spokenly MCP (voice clarification) | `services/spokenly-mcp-bridge/` |
| Voice Orion (command parser) | `apps/voice-orion/` |
| Command Palette | `apps/command-palette/` |
| DLAM / R1 (desktop control) | `apps/desktop-control/` |
| Operator Console | `apps/operator-console/` |
| OpenClaw (orchestration) | `integrations/openclaw/` |
| R.I.P. (canonical memory sync) | `services/rip-canon-sync/` |
| Knowledge Graph sync | `services/knowledge-graph-sync/` |
| Aegis / Violet Covenant (policy) | `services/approval-gate/`, `packages/policy/` |
| zopack | `skills/zopack/` |
| glyphy pets | `skills/glyphy-pets/` |
| Voice agent daemon | `skills/voice-agent-daemon/` |

## Governance Principles

These principles govern all design and implementation decisions:

- **No proof, no claim.** Every action must produce evidence.
- **High-risk actions must be approved.** Approval gate is not optional.
- **Prefer reversible decisions.** Keep options open.
- **Canonical memory must be diffable.** R.I.P. stores canonical truth; Knowledge Graph stores operational context.
- **Packaging must be reproducible.** zopack bundles are the portability unit.

## Current Folder Structure

```
agentic-os/
├── _docs/             # Dependency notes and scratch docs
├── agents/            # Durable LangGraph agents (Python)
│   ├── shared/        # Shared utilities (delta-dict returns, BaseMessage helpers)
│   ├── trend_arbitrage/
│   ├── social_content/
│   └── microsaas_factory/
├── apps/
│   └── zo-super-server/   # Python MCP server
├── docker/            # Dockerfile.agent, docker-compose.yml (restart: on-failure)
├── holaos/            # Runbooks, memory, skills, workspaces
├── ops/
│   ├── ledgers/       # Append-only JSON ledgers
│   │   ├── big_bank_database.json              # Canonical research sweep database
│   │   ├── big_bank_database_append_*.json     # Dated append files
│   │   └── storage_migration.json              # Mac Mini → external SSD migration log
│   └── runbooks/
├── research/          # Research sweep outputs
│   ├── *.md           # Markdown sweep reports (see naming patterns below)
│   ├── big_bank_database.json      # Optional copy of ops/ledgers/big_bank_database.json (may lag)
│   ├── night-sweeps/               # Night sweep markdown reports
│   ├── big_bank_night_sweeps/      # Night sweep JSON outputs
│   └── big_bank_morning_sweeps/    # Morning sweep JSON outputs
├── services/
│   └── loop-harness/
├── skills/
│   └── task-manager/
├── spec-pack/         # Architecture specs and diagrams (canonical)
│   ├── assets/        # PNG architecture diagrams
│   └── *.md           # master-spec, deployment-blueprint, phase-0-build-plan, repo-layout, holaos-architecture
└── src/
    └── metropolis/    # car-kernel (TypeScript)
```

Always append sweep data to `ops/ledgers/big_bank_database.json` — that is the canonical ledger. `research/big_bank_database.json` is an optional manual copy that may lag behind and should not be used as an append target.

## Research Sweep Convention

The repo runs recurring **Big Bank triple-sweep** research tasks on JPMorgan Chase (JPM) and its peers (BAC, WFC, C, GS, MS). Each sweep produces:

- A **Markdown report** in `research/` (see naming patterns below)
- A **JSON entry** appended to `ops/ledgers/big_bank_database.json`

**Markdown naming patterns** — two patterns coexist in `research/`:
- `YYYY-MM-DD-{sweep-type}-sweep.md` — canonical going forward (e.g., `2026-05-10-noon-sweep.md`)
- `big-bank-{sweep-type}-sweep-YYYY-MM-DD.md` — older pattern (e.g., `big-bank-morning-sweep-2026-05-02.md`)

Use `YYYY-MM-DD-{sweep-type}-sweep.md` for new sweeps. Subdirectory outputs go to `research/night-sweeps/`, `research/big_bank_night_sweeps/`, or `research/big_bank_morning_sweeps/` depending on sweep type.

The JSON ledger is an append-only array. Each entry includes `timestamp`, `sweep_type`, and a `results` block with `target` (JPM) and `peers`. The "Big Bank" alias maps to JPM (JPMorgan Chase & Co., ticker `JPM`, CIK `0000019617`).

## Planned Implementation Structure

Phase 0 build is underway. Several directories from the target topology in `spec-pack/repo-layout.md` already exist (`apps/`, `services/`, `agents/`, `skills/`, `ops/`). Still to be added:

```
apps/          voice-orion, command-palette, desktop-control, operator-console
services/      spokenly-mcp-bridge, approval-gate, knowledge-graph-sync, rip-canon-sync
integrations/  notion, google, openclaw, zo, macos
packages/      core, policy, memory, routing, telemetry
skills/        voice-agent-daemon, zopenclaw, zopack, glyphy-pets
routes/        api, pages
```

Phase 0 minimum viable remaining targets: `services/spokenly-mcp-bridge/`, `apps/voice-orion/`, and `packages/{core,policy,memory,routing}`.
