# Persistent Agent Deployment Runbook

## Four Crash-Survival Properties

Every deployment must have all four:

1. **Checkpoint at every state transition** — LangGraph checkpoints on every node, not just at session end.
2. **Idempotent tool calls** — every API call, file write, and browser action is safe to retry without side effects.
3. **Memory compaction schedule** — prune transient runtime notes weekly; promote high-value artifacts to `knowledge/`.
4. **Observability wiring** — `getsentry/sentry-setup-ai-monitoring` instruments LLM calls automatically; pipe critical failures to Slack.

---

## Option A — Self-Hosted Docker (Free, Local-First)

```bash
cd ops/docker
cp .env.example .env
# Fill in ANTHROPIC_API_KEY and any agent-specific keys

docker compose up -d

# Verify all three agents are running
docker compose ps

# Tail logs
docker compose logs -f trend-arbitrage
docker compose logs -f social-content-engine
docker compose logs -f micro-saas-factory
```

`restart: always` ensures Docker restarts any container within ~500ms of a crash, reboot, or OOM kill.

### Checkpoint backend selection

| Environment | Set `CHECKPOINT_BACKEND` to | Notes |
|---|---|---|
| Local dev / VPS | `sqlite` | Zero config, single file |
| AWS Lambda / serverless | `dynamodb` | No connection pooling needed |
| Dedicated VM / LangGraph Cloud | `postgres` | Best for high-throughput |

---

## Option B — LangGraph Cloud (Managed)

LangGraph Cloud saves state at every execution step with built-in persistence. Fastest path to production.

```bash
pip install langgraph-cli
langgraph deploy --config langgraph.json
```

Install the DynamoDB backend and configure it:

```bash
pip install langgraph-checkpoint-aws
```

```python
from langgraph_checkpoint_aws import DynamoDBSaver

checkpointer = DynamoDBSaver(
    table_name="lovelogic-checkpoints",
    region_name="us-east-1",
)
```

---

## Option C — Fly.io Firecracker VMs (~$45/mo all-in)

```bash
fly launch --name lovelogic-agents --dockerfile ops/docker/Dockerfile.agent
fly secrets set ANTHROPIC_API_KEY=sk-ant-...
fly deploy
```

Crash recovery in ~500ms via Firecracker microVM restarts. Zero infrastructure management.

---

## Memory Compaction Schedule

The `compact_session()` function is called automatically at the end of each agent run.
To manually trigger compaction for a stale workspace:

```python
import asyncio
from packages.memory.compaction import compact_session
asyncio.run(compact_session("trend-arbitrage", "run-20260512T000000"))
```

Runtime files older than `RUNTIME_TTL_DAYS` (default: 7) are pruned automatically.

---

## Resuming a Crashed Run

Every agent uses a stable `thread_id`. LangGraph auto-restores state from the last checkpoint:

```python
config = {"configurable": {"thread_id": "trend-arbitrage-main"}}
result = await graph.ainvoke(new_message, config=config)
# State from the last successful checkpoint is automatically restored
```

---

## Audit Ledger Locations

| Agent | Ledger |
|---|---|
| Trend Arbitrage | `ops/ledgers/trend-arbitrage-audit.jsonl` |
| Social Content Engine | `ops/ledgers/social-content-audit.jsonl` |
| Micro-SaaS Factory | `ops/ledgers/micro-saas-factory-audit.jsonl` |

Each line is a newline-delimited JSON artifact written before any publish action. For the Micro-SaaS Factory, the ledger entry is written after the Cloudflare deploy but before the Product Hunt launch post.
