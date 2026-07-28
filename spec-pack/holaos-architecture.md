# holaOS Architecture Integration — Agentic OS

**Date:** 2026-05-12
**Status:** Active Implementation — Branch `claude/holaos-agent-strategy-X9H1y`

---

## Overview

This document integrates the holaOS "Agent Computer" model into Agentic OS's
existing architecture. Where Agentic OS provides governance, voice, and routing
layers, holaOS provides the **durable environment** agents live inside.

The two systems are complementary, not competing:

| Agentic OS Layer | holaOS Layer | Combined Capability |
|---|---|---|
| Voice Edge (Spokenly) | Workspace Input Interface | Voice → durable workspace |
| Command Router | Runtime Harness | Intent → persistent execution |
| Governance (Aegis/Violet Covenant) | Permission Boundaries | Policy-controlled tool access |
| Memory (R.I.P.) | SQLite + Markdown state | Canonical + operational memory |
| Orchestration (OpenClaw) | Workspace Templates | Multi-agent coordination |

---

## The Four Layers

### Layer 1 — Runtime Harness

The harness is the execution coordinator:
- Dispatches agent turns and manages tool calls
- Handles session lifecycle (start, pause, resume, terminate)
- Enforces permission boundaries between the LLM and OS surfaces
- Routes between workspaces in the OpenClaw mesh

**Key property:** Existing LangGraph/LangChain code plugs in via the tool-and-app
interface without rewrites.

### Layer 2 — State Store (Durability)

Hybrid storage: SQLite for structured state, Markdown for human-readable memory.
See `holaos/memory/runtime-schema.md` for full schema.

**Key property:** The environment *learns* across sessions — not via longer
context windows, but via accumulated, curated memory artifacts.

### Layer 3 — Workspace (The Container)

A workspace bundles:
- Agent instructions and goals
- Tools and MCP servers it can access
- Memory surfaces and state layout
- Identity and preference configuration
- Cron schedule for automated runs

Workspace templates are the viral distribution primitive — shareable across
the ecosystem like an "app" or "skill package."

See `holaos/workspaces/` for the three canonical LoveLogicAI workspace configs.

### Layer 4 — MCP Tool Bus

All tool access goes through MCP. Any MCP server wires in without custom
integration code. See `holaos/skills/skill-registry.json` for the curated
12-skill registry.

---

## Three Viral Skill Builds

| Build | Workspace File | Monthly Revenue Target | Viral Hook |
|---|---|---|---|
| Trend Arbitrage Agent | `holaos/workspaces/trend-arbitrage-agent.json` | $29/user | "AI monitors 900 markets 24/7" |
| Social Content Engine | `holaos/workspaces/social-content-engine.json` | $299/client | "Full week of content, zero humans" |
| Micro-SaaS Factory | `holaos/workspaces/microsaas-factory.json` | USDC/build + SaaS | "Built and shipped while I slept" |

---

## Integration with Existing Agentic OS Components

### R.I.P. ↔ holaOS Memory

R.I.P. (canonical memory and identity) maps directly to the holaOS Knowledge layer:

```
R.I.P. canonical claims  →  holaOS knowledge/ artifacts
R.I.P. session history   →  holaOS runtime/ + SQLite turns table
R.I.P. identity claims   →  holaOS identity/<workspace-id>.md
```

### Aegis / Violet Covenant ↔ Permission Boundaries

Aegis governance policies map to workspace permission configs:

```json
"permissions": {
  "file_system": false,
  "browser": false,
  "apis": ["musashi.bot", "typefully.com"]
}
```

The allowlisted API array is the Aegis policy surface for network access.

### OpenClaw ↔ Runtime Harness

OpenClaw's orchestration mesh is the multi-workspace coordinator. Each workspace
is a node in the OpenClaw graph, with the harness managing turn dispatch within
each node.

---

## Crash Survival Properties

Every workspace is designed with four crash-survival guarantees:

1. **Checkpoint at every state transition** — LangGraph checkpointer writes after
   every node execution, not just at session end.

2. **Idempotent tool calls** — Every external action is safe to retry.
   Duplicate detection via evidence ledger timestamps.

3. **Compaction schedule** — Runtime memory pruned weekly; only high-value
   artifacts promoted to the knowledge layer.

4. **Observability** — Sentry AI monitoring instruments all LLM calls.
   Critical failures route to Slack webhook.

---

## Deployment Options

| Option | Monthly Cost | Uptime | Best For |
|---|---|---|---|
| LangGraph Cloud | Pay-per-use | 99.9% | Managed, client-facing agents |
| Self-hosted Docker | ~$5-20/mo VPS | 99% | Local-first, cost-controlled |
| Cloudflare Workers | ~$5-45/mo | 99.99% | Serverless, edge-distributed |

See `holaos/runbook/persistent-agent-runbook.md` for full deployment instructions.

---

## Key Architectural Insights

1. **Workspace templates are the viral distribution mechanism.** A packaged
   workspace can be shared cross-ecosystem — equivalent to a "skill marketplace"
   primitive built on top of zopack.

2. **Separation of reasoning and environment is the safety layer.** The harness
   controls what the LLM can touch without exposing the raw OS.

3. **The agent gets smarter at the workspace over time** — not via larger
   context windows, but via curated knowledge artifacts that accumulate.

4. **holaOS compaction is the cost-control mechanism.** Without it, week-long
   agents accumulate unbounded context and costs spiral. With it, each session
   starts fresh from a compact summary.
