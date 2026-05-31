# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

Agentic OS is a **spec-first, pre-implementation** repository. It contains architecture specifications, research data, and operational ledgers — no runnable application code yet (no `package.json`, no `apps/`, `services/`, or `packages/` directories). The `.gitignore` anticipates a Node/Bun/Next.js stack for when implementation begins. Phase 0 (the first shippable slice) is the active build focus.

There are no build, lint, or test commands to run. When implementation begins, `spec-pack/repo-layout.md` defines the intended folder topology (note: `spec-pack/` serves as the docs directory — that file refers to it as `docs/`, but the actual directory is `spec-pack/`).

## Canonical Reading Order

Start here to understand the system:

1. `spec-pack/master-spec.md` — the system contract and nine-layer definition
2. `spec-pack/deployment-blueprint.md` — deployment stages and topology diagram
3. `spec-pack/phase-0-build-plan.md` — current build focus (the proof slice)
4. `spec-pack/repo-layout.md` — planned folder topology

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
├── spec-pack/          # Architecture specs and diagrams (canonical)
│   ├── assets/         # PNG architecture diagrams
│   └── *.md            # master-spec, deployment-blueprint, phase-0-build-plan, repo-layout
├── ops/
│   └── ledgers/        # Append-only JSON ledgers
│       ├── big_bank_database.json   # Centralized research sweep database
│       └── storage_migration.json  # Mac Mini → external SSD migration log
└── research/           # Research sweep outputs
    ├── *.md            # Markdown sweep reports (named by date and sweep type)
    ├── big_bank_database.json      # Mirror of ops/ledgers/big_bank_database.json
    ├── night-sweeps/   # Night sweep markdown reports
    └── big_bank_night_sweeps/      # Night sweep JSON outputs
```

The `ops/ledgers/big_bank_database.json` and `research/big_bank_database.json` are both used as landing targets for sweep appends — treat `ops/ledgers/` as the canonical ledger location.

## Research Sweep Convention

The repo runs recurring **Big Bank triple-sweep** research tasks on JPMorgan Chase (JPM) and its peers (BAC, WFC, C, GS, MS). Each sweep produces:

- A **Markdown report** in `research/` named `YYYY-MM-DD-{sweep-type}-sweep.md`
- A **JSON entry** appended to `ops/ledgers/big_bank_database.json` (and mirrored in `research/big_bank_database.json`)

The JSON ledger is an append-only array. Each entry includes `timestamp`, `sweep_type`, and a `results` block with `target` (JPM) and `peers`. The "Big Bank" alias maps to JPM (JPMorgan Chase & Co., ticker `JPM`, CIK `0000019617`).

## Planned Implementation Structure

When Phase 0 build begins, the repo will grow these directories (see `spec-pack/repo-layout.md`):

```
apps/          voice-orion, command-palette, desktop-control, operator-console
services/      spokenly-mcp-bridge, approval-gate, knowledge-graph-sync, rip-canon-sync
agents/        orchestrator, verifier, executor, witness
integrations/  notion, google, openclaw, zo, macos
packages/      core, policy, memory, routing, telemetry
skills/        voice-agent-daemon, zopenclaw, zopack, glyphy-pets
routes/        api, pages
ops/           runbooks, prompts, checks, ledgers
```

Phase 0 minimum viable build targets only: `services/spokenly-mcp-bridge/`, `apps/voice-orion/`, `agents/orchestrator/`, `packages/{core,policy,memory,routing}`, and `ops/`.
