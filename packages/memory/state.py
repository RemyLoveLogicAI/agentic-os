"""
Hybrid state store: SQLite for runtime metadata, Markdown for durable knowledge.
Mirrors holaOS's memory architecture:
  memory/workspace/<agent>/runtime/  — transient working context
  memory/workspace/<agent>/knowledge/ — long-term retained facts
"""

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


MEMORY_ROOT = Path(os.environ.get("MEMORY_ROOT", "memory/workspace"))
RUNTIME_DB = Path(os.environ.get("RUNTIME_DB", "state/runtime.db"))


def _runtime_dir(agent: str) -> Path:
    d = MEMORY_ROOT / agent / "runtime"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _knowledge_dir(agent: str) -> Path:
    d = MEMORY_ROOT / agent / "knowledge"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _db() -> sqlite3.Connection:
    RUNTIME_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(RUNTIME_DB))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            agent    TEXT NOT NULL,
            run_id   TEXT NOT NULL,
            payload  TEXT NOT NULL,
            ts       TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS artifacts (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            agent    TEXT NOT NULL,
            run_id   TEXT NOT NULL,
            payload  TEXT NOT NULL,
            ts       TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def save_signal(payload: dict, agent: str = "unknown") -> int:
    """Persist a transient signal record to SQLite."""
    conn = _db()
    ts = datetime.now(timezone.utc).isoformat()
    cur = conn.execute(
        "INSERT INTO signals (agent, run_id, payload, ts) VALUES (?, ?, ?, ?)",
        (agent, payload.get("run_id", ""), json.dumps(payload), ts),
    )
    conn.commit()
    return cur.lastrowid


def save_artifact(agent: str, payload: dict) -> int:
    """Persist a durable artifact to SQLite and a Markdown file in knowledge/."""
    conn = _db()
    ts = datetime.now(timezone.utc).isoformat()
    cur = conn.execute(
        "INSERT INTO artifacts (agent, run_id, payload, ts) VALUES (?, ?, ?, ?)",
        (agent, payload.get("run_id", ""), json.dumps(payload), ts),
    )
    conn.commit()

    # Write Markdown snapshot to knowledge base
    fname = f"{payload.get('run_id', 'artifact')}.md"
    kb_path = _knowledge_dir(agent) / fname
    lines = [f"# Artifact: {payload.get('run_id', '')}", f"**Recorded:** {ts}", "", "```json"]
    lines.append(json.dumps(payload, indent=2))
    lines.append("```")
    kb_path.write_text("\n".join(lines))

    return cur.lastrowid


def load_knowledge(agent: str, key: str | None = None) -> str:
    """Load durable knowledge for an agent. key selects a specific .md file."""
    kd = _knowledge_dir(agent)
    if key:
        candidates = list(kd.glob(f"{key}*.md"))
        if candidates:
            return candidates[-1].read_text()
        return ""
    # Return catalog of all knowledge files (for context bootstrapping)
    files = sorted(kd.glob("*.md"))
    if not files:
        return ""
    catalog = [f"## Knowledge: {agent}", ""]
    for f in files[-10:]:  # last 10 artifacts max to avoid context bloat
        catalog.append(f"### {f.stem}")
        catalog.append(f.read_text()[:500])  # truncate per artifact
        catalog.append("")
    return "\n".join(catalog)


def list_recent_signals(agent: str, limit: int = 20) -> list[dict]:
    """Return the most recent signal records for an agent."""
    conn = _db()
    rows = conn.execute(
        "SELECT payload, ts FROM signals WHERE agent = ? ORDER BY id DESC LIMIT ?",
        (agent, limit),
    ).fetchall()
    return [{"payload": json.loads(r[0]), "ts": r[1]} for r in rows]
