# Phase 0 Operations Runbook

## Start the System

```bash
# Start the operator console (includes orchestrator)
bun run dev
```

The operator console starts at `http://localhost:4200`.

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Operator panel (HTML) |
| `/health` | GET | Health check |
| `/api/state` | GET | Full system state |
| `/api/command` | POST | Submit a command |
| `/api/evidence` | GET | View evidence ledger |
| `/api/approvals` | GET | List all approvals |
| `/api/approvals/:id/approve` | POST | Approve a request |
| `/api/approvals/:id/deny` | POST | Deny a request |
| `/api/clarifications` | GET | List clarifications |
| `/api/clarifications/:id` | POST | Resolve clarification |

## Submit a Command

```bash
curl -X POST http://localhost:4200/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "check status", "source": "typed"}'
```

## Approve an Action

```bash
curl -X POST http://localhost:4200/api/approvals/apr_XXXXXXXX/approve
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `AGENTIC_OS_PORT` | 4200 | Server port |
| `AGENTIC_OS_HOST` | 0.0.0.0 | Server host |
| `APPROVAL_TTL_MS` | 300000 | Approval TTL (5 min) |
| `AUTO_APPROVE_SAFE` | true | Auto-approve safe actions |
| `EVIDENCE_DIR` | ./ops/ledgers/evidence | Evidence storage |
| `LOG_LEVEL` | info | Log verbosity |
| `ZO_SUPER_SERVER_URL` | http://localhost:3000 | Zo server URL |
| `ZO_SUPER_SERVER_TOKEN` | (required) | Auth token |

## Evidence Rotation

Evidence files are stored as daily JSONL files in `ops/ledgers/evidence/`.
Format: `evidence-YYYY-MM-DD.jsonl`

## Troubleshooting

1. **Server won't start**: Check port 4200 is available
2. **Approval expired**: Default TTL is 5 minutes
3. **API adapter fails**: Ensure Zo Super Server is running
4. **Unknown intents**: Command didn't match any routing rules
