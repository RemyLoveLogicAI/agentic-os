# Agent Instructions for agentic-os

## Repository Overview

agentic-os is a LoveLogicAI platform for persistent LangGraph agents with shared memory,
checkpoint infrastructure, and Cloudflare Workers-based micro-SaaS tooling.

## Key Conventions

- Commit style: Conventional Commits (`feat:`, `fix:`, etc.)
- Language: Python (agents), TypeScript (skills/services)
- See `.claude/skills/agentic-os/` for the full conventions skill

## Design Tool Integrations

**Paper** (paper.design) and **pen.dev / Pencil** MCP integrations are documented at:

```
docs/design-tools/paper-setup.md        ← Paper Desktop setup & MCP config
docs/design-tools/pen-dev-setup.md      ← Pencil setup & MCP config
docs/design-tools/verification-report.md ← Test plans & current status
docs/design-tools/workflow-comparison.md  ← Tool selection guidance
```

Reusable workflow skills:
```
skills/paper-design/SKILL.md   ← Paper session startup and design workflow
skills/pen-dev/SKILL.md        ← Pencil session startup (read_skill() required first)
```

**Setup status as of 2026-10-18:** Both tools require the desktop app on the local machine.
Paper: macOS/Windows only. Pencil: macOS/Windows/Linux desktop.
See `docs/design-tools/verification-report.md` for current blockers and required human actions.

## Memory & State

- Runtime state: SQLite at `state/runtime.db`
- Durable knowledge: Markdown at `memory/workspace/<agent>/knowledge/`
- Audit ledgers: `ops/ledgers/`

## Security

- API keys via environment variables only — never hardcoded
- `.env` must be gitignored
- High-risk actions (deploy, publish, broadcast) require `requireApprovalFor` in workspace.json
