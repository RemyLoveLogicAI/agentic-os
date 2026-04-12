# Agentic OS Repo / Folder Layout

## Root Shape

```text
agentic-os/
├── docs/
│   ├── master-spec.md
│   ├── deployment-blueprint.md
│   ├── phase-0-build-plan.md
│   └── architecture/
├── apps/
│   ├── voice-orion/
│   ├── command-palette/
│   ├── desktop-control/
│   └── operator-console/
├── services/
│   ├── spokenly-mcp-bridge/
│   ├── knowledge-graph-sync/
│   ├── rip-canon-sync/
│   └── approval-gate/
├── agents/
│   ├── orchestrator/
│   ├── verifier/
│   ├── executor/
│   └── witness/
├── integrations/
│   ├── notion/
│   ├── google/
│   ├── openclaw/
│   ├── zo/
│   └── macos/
├── packages/
│   ├── core/
│   ├── policy/
│   ├── memory/
│   ├── routing/
│   └── telemetry/
├── skills/
│   ├── voice-agent-daemon/
│   ├── zopenclaw/
│   ├── zopack/
│   └── glyphy-pets/
├── routes/
│   ├── api/
│   └── pages/
└── ops/
    ├── runbooks/
    ├── prompts/
    ├── checks/
    └── ledgers/
```

## Minimum Viable Layout

Build only:
- `docs/`
- `services/spokenly-mcp-bridge/`
- `apps/voice-orion/`
- `agents/orchestrator/`
- `packages/{core,policy,memory,routing}`
- `ops/{runbooks,prompts,checks,ledgers}`

## Priority

| Folder | Token Cost | Dependencies | Priority |
|---|---:|---|---|
| `docs/` | Low | none | P0 |
| `services/spokenly-mcp-bridge/` | Medium | Spokenly MCP | P0 |
| `apps/voice-orion/` | Medium | routing + policy | P0 |
| `packages/core/` | Medium | none | P0 |
| `packages/policy/` | Medium | approvals, trust model | P0 |
| `packages/memory/` | High | R.I.P., Knowledge Graph | P1 |
| `agents/orchestrator/` | High | router, services | P1 |
| `integrations/` | High | secrets, APIs | P1 |
| `skills/` | Low | reusable workflows | P2 |
| `ops/` | Medium | governance, checks | P0 |
