# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project — especially one involving API key exposure,
prompt injection, or agent authorization bypass — please report it privately by emailing
security@lovelogic.ai rather than opening a public GitHub issue.

Include: a description of the issue, reproduction steps, and any affected components.
We will respond within 48 hours.

## Secrets and Credentials

- API keys must be supplied via environment variables — never hardcoded in source files.
- See `ops/docker/.env.example` for the required variables. The `.env` file itself is gitignored.
- All agent audit actions write to `ops/ledgers/` before any publish or deploy step.

## Supported Versions

This project is pre-1.0. Security fixes are applied to the `main` branch only.

## Agent Governance

All agents enforce `requireApprovalFor` in their `workspace.json` config.
High-risk actions (deploy, publish, broadcast) cannot execute without a logged evidence artifact.
See `ops/runbooks/persistent-agent-deployment.md` for the full crash-survival and audit model.
