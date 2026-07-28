# Persistent Agent Runbook — LoveLogicAI 24/7 Deployment

**Date:** 2026-05-12
**Scope:** Three viral skill builds deployed persistently: Trend Arbitrage, Social Content Engine, Micro-SaaS Factory

---

## Four Crash Survival Properties (Apply to All Options)

Every agent deployment must satisfy these before going to production:

1. **Checkpoint at every state transition** — LangGraph checkpointer writes after every
   node execution. Set `CHECKPOINT_BACKEND=dynamodb` for multi-process deployments.

2. **Idempotent tool calls** — Every external action is safe to retry without
   side effects. Duplicate detection via evidence ledger timestamps.

3. **Memory compaction on schedule** — `compact_session()` runs at every session end.
   Prune stale runtime artifacts weekly with `prune_stale_runtime()`.

4. **Observability wiring** — Wire `getsentry/sentry-setup-ai-monitoring` to
   instrument all LLM calls. Route critical failures to Slack webhook.

---

## Option A: LangGraph Cloud (Recommended for Managed)

**Best for:** Client-facing agents with SLA requirements.
**Cost:** Pay-per-use LLM tokens + minimal hosting.
**Uptime:** 99.9% managed.

```bash
# 1. Install LangChain CLI
pip install langchain-cli

# 2. Authenticate
langchain login

# 3. Deploy
cd agentic-os/
langchain app deploy --name trend-arbitrage-agent

# 4. Set environment variables in LangGraph Cloud dashboard
# ANTHROPIC_API_KEY, MUSASHI_API_KEY, CHECKPOINT_BACKEND=dynamodb
```

**Python config for DynamoDB checkpointer:**
```python
from agents.shared.checkpointer import get_checkpointer

# Set env: CHECKPOINT_BACKEND=dynamodb
# Set env: LANGGRAPH_CHECKPOINT_TABLE=lovelogic-checkpoints
# Set env: AWS_DEFAULT_REGION=us-east-1
checkpointer = get_checkpointer()  # auto-selects DynamoDB
```

**Resume any run after crash:**
```python
config = {"configurable": {"thread_id": "client-workspace-001"}}
result = await graph.ainvoke(initial_state, config=config)
# State auto-restored from last checkpoint
```

---

## Option B: Self-Hosted Docker (Local-First)

**Best for:** Running on M4 Mac mini or $5/mo VPS.
**Cost:** ~$5-20/mo infrastructure.
**Uptime:** 99% with `restart: always`.

```bash
# 1. Clone and configure
git clone https://github.com/remylovelogicai/agentic-os.git
cd agentic-os

# 2. Set environment variables
cp .env.example .env
# Edit .env: add ANTHROPIC_API_KEY, MUSASHI_API_KEY, etc.

# 3. Build and launch all three agents
docker compose -f docker/docker-compose.yml up -d

# 4. Verify all containers are healthy
docker compose -f docker/docker-compose.yml ps

# 5. Monitor logs
docker compose -f docker/docker-compose.yml logs -f trend-arbitrage-agent
```

**The critical directive:**
```yaml
restart: always  # Docker restarts within ~500ms of any crash, reboot, or OOM kill
```

**Required .env file:**
```bash
ANTHROPIC_API_KEY=sk-ant-...
MUSASHI_API_KEY=...
FIRECRAWL_API_KEY=...
TYPEFULLY_API_KEY=...
FAL_KEY=...
CLOUDFLARE_API_TOKEN=...
CLOUDFLARE_ACCOUNT_ID=...
CHECKPOINT_BACKEND=memory   # Change to 'dynamodb' for persistence across redeploys
```

---

## Option C: Cloudflare Workers (Serverless, Edge)

**Best for:** Micro-SaaS Factory — agents that are also HTTP services.
**Cost:** ~$5-45/mo all-in.
**Uptime:** 99.99%.

```bash
# Install Wrangler
npm install -g wrangler

# Authenticate
wrangler login

# Deploy the micro-SaaS factory worker
wrangler deploy --name microsaas-factory

# Set secrets
wrangler secret put ANTHROPIC_API_KEY
wrangler secret put CLOUDFLARE_API_TOKEN
```

**Cloudflare Durable Objects for state:**
```typescript
import { AgentState } from 'cloudflare:workers'

export class WorkspaceAgent extends AgentState {
  async onRequest(request: Request): Promise<Response> {
    // Durable Object — state persists automatically across requests
    return new Response('ok')
  }
}
```

---

## Cron Scheduling

For agents with `cron` fields in their workspace config:

**Docker (cron via host systemd):**
```bash
# /etc/cron.d/lovelogic-agents
*/2 * * * * docker exec trend-arbitrage-agent python -m agents.trend_arbitrage.agent
```

**Cloudflare Workers (built-in cron triggers):**
```toml
# wrangler.toml
[triggers]
crons = ["*/2 * * * *"]
```

**LangGraph Cloud (schedule via API):**
```python
from langgraph_sdk import get_client
client = get_client()
await client.crons.create(
    assistant_id="trend-arbitrage-agent",
    schedule="*/2 * * * *",
    input={"task": "poll_and_analyze"},
)
```

---

## Memory Management Checklist

- [ ] `compact_session()` called at every agent session end
- [ ] `prune_stale_runtime()` scheduled weekly (cron: `0 0 * * 0`)
- [ ] SQLite `sessions` TTL: 90 days
- [ ] SQLite `turns` TTL: 30 days
- [ ] Knowledge artifacts reviewed monthly, low-value entries pruned manually
- [ ] DynamoDB checkpoint TTL: 7 days (set via table TTL attribute)

---

## Cost Estimates

| Agent | Tokens/run | Runs/day | Est. Daily LLM Cost |
|---|---|---|---|
| Trend Arbitrage (2-min cron) | ~500 | 720 | ~$1.08 |
| Social Content Engine (weekly) | ~8,000 | 0.14 | ~$0.03 |
| Micro-SaaS Factory (on-demand) | ~3,000 | varies | ~$0.01-0.50 |

**Total estimated daily cost: ~$1.12-1.61 LLM cost** plus infrastructure.
At $29/user subscription, break-even at 2 users for Trend Arbitrage.

---

## Rollout Order

1. **Day 1-2:** Deploy Trend Arbitrage Agent locally with Docker. Validate signal quality.
2. **Day 3-4:** Deploy Social Content Engine. Run first weekly cycle. Review output.
3. **Day 5-7:** Deploy Micro-SaaS Factory. Build first tool. Post launch thread.
4. **Week 2:** Move Trend Arbitrage to LangGraph Cloud. Switch to DynamoDB checkpointer.
5. **Week 3:** Wire Sentry AI monitoring to all three agents.
6. **Week 4:** Launch $29/mo waitlist for Trend Arbitrage SaaS dashboard.
