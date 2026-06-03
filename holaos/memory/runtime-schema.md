# holaOS Memory Layer — Runtime Schema

LoveLogicAI's persistent agent infrastructure uses a hybrid memory architecture
inspired by holaOS's environment-first design: SQLite for structured state,
Markdown for human-readable, inspectable memory artifacts.

## Storage Topology

| Layer | Technology | Path | Contents |
|---|---|---|---|
| Runtime State | SQLite | `state/runtime.db` | Sessions, turns, queue, cron jobs, metadata |
| Runtime Memory | Markdown | `memory/workspace/<id>/runtime/` | Working context, compacted per session |
| Durable Knowledge | Markdown | `memory/workspace/<id>/knowledge/` | Long-term facts, decisions, references |
| Identity | Markdown | `identity/<workspace-id>.md` | Agent persona, goals, behavior tuning |
| Preferences | Markdown | `preference/<workspace-id>.md` | User/client preferences, alert thresholds |

## SQLite Schema — runtime.db

```sql
CREATE TABLE sessions (
  id          TEXT PRIMARY KEY,
  workspace   TEXT NOT NULL,
  started_at  TEXT NOT NULL,
  ended_at    TEXT,
  status      TEXT DEFAULT 'active',  -- active | completed | crashed
  turn_count  INTEGER DEFAULT 0,
  cost_usd    REAL DEFAULT 0.0
);

CREATE TABLE turns (
  id           TEXT PRIMARY KEY,
  session_id   TEXT REFERENCES sessions(id),
  turn_index   INTEGER NOT NULL,
  role         TEXT NOT NULL,          -- user | assistant | tool
  content      TEXT,
  tool_calls   TEXT,                   -- JSON array
  cost_tokens  INTEGER DEFAULT 0,
  created_at   TEXT NOT NULL
);

CREATE TABLE memory_artifacts (
  id              TEXT PRIMARY KEY,
  workspace       TEXT NOT NULL,
  type            TEXT NOT NULL,       -- runtime | knowledge | identity
  filename        TEXT NOT NULL,
  created_at      TEXT NOT NULL,
  last_accessed   TEXT,
  freshness_score REAL DEFAULT 1.0
);

CREATE TABLE cron_jobs (
  id          TEXT PRIMARY KEY,
  workspace   TEXT NOT NULL,
  expression  TEXT NOT NULL,
  last_run    TEXT,
  next_run    TEXT,
  status      TEXT DEFAULT 'active'
);

CREATE TABLE evidence_ledger (
  id           TEXT PRIMARY KEY,
  session_id   TEXT REFERENCES sessions(id),
  action_type  TEXT NOT NULL,
  description  TEXT,
  payload      TEXT,                   -- JSON
  outcome      TEXT,
  timestamp    TEXT NOT NULL
);
```

## Recall System

Recall is catalog-based with freshness ranking rather than embedding-based.
This keeps the system lightweight and local-first without requiring a vector
database.

### Freshness Ranking

Each memory artifact carries a `freshness_score` that decays over time:

```
freshness_score = base_weight * exp(-lambda * days_since_access)
```

Where:
- `base_weight` = 1.0 for knowledge artifacts, 0.6 for runtime artifacts
- `lambda` = 0.05 (5% daily decay)

Artifacts below `freshness_score < 0.1` are candidates for pruning.

### Compaction Protocol

At the end of each session:
1. Raw turn transcripts are summarized into a structured `session-<id>.md` file
2. High-value insights are promoted to `knowledge/` with a freshness reset
3. Runtime artifacts older than 7 days with score < 0.1 are pruned
4. SQLite `sessions` row is updated with final status and cost

This ensures the next run bootstraps from compact, curated context rather than
replaying unbounded history — the key to stability over weeks-long runs.

## Memory Catalog Format

Each Markdown file in `knowledge/` begins with YAML front-matter:

```yaml
---
id: "know-2026-05-12-001"
workspace: "trend-arbitrage-agent"
type: knowledge
tags: [prediction-markets, signal, arbitrage]
created: "2026-05-12T14:30:00Z"
last_accessed: "2026-05-12T16:00:00Z"
freshness_score: 1.0
---
```

## Workspace Directory Layout

```
memory/
  workspace/
    trend-arbitrage-agent/
      runtime/
        session-20260512-001.md
        queue-state.md
      knowledge/
        market-signals-2026-05.md
        account-watchlist.md
        arbitrage-history.md
    social-content-engine/
      runtime/
        session-20260512-001.md
      knowledge/
        brand-voice.md
        content-calendar.md
        audience-feedback.md
    microsaas-factory/
      runtime/
        session-20260512-001.md
      knowledge/
        deployed-tools.md
        revenue-dashboard.md
        build-history.md

state/
  runtime.db

evidence/
  trend-arbitrage-agent/
    2026-05-12.jsonl
  social-content-engine/
    2026-05-12.jsonl
  microsaas-factory/
    2026-05-12.jsonl
```
