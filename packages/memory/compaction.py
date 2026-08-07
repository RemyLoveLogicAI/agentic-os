"""
Session compaction: summarise transient runtime context into a durable
knowledge artifact after each agent run. Mirrors holaOS compaction logic.

At end of session:
  1. Read all runtime/*.md files for the agent.
  2. Produce a compact summary (key decisions, signals, outcomes).
  3. Write to knowledge/<run_id>-compact.md.
  4. Prune runtime files older than RUNTIME_TTL_DAYS.
"""

import asyncio
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

MEMORY_ROOT = Path(os.environ.get("MEMORY_ROOT", "memory/workspace"))
RUNTIME_TTL_DAYS = int(os.environ.get("RUNTIME_TTL_DAYS", "7"))

COMPACTION_PROMPT = """\
You are a memory compaction agent. Below are the raw working notes from an agent session.
Produce a concise summary (max 400 words) that retains:
- Key signals or opportunities identified
- Actions taken and their outcomes
- Decisions made and the reasoning
- Any important facts to remember for the next session

Omit verbose reasoning, failed attempts, and intermediate tool outputs.
Write in bullet-point format. Start with "## Session {run_id} Compact".

Raw notes:
{raw_notes}
"""


async def compact_session(agent: str, run_id: str) -> str | None:
    """Compact runtime notes for agent/run_id into a knowledge artifact."""
    runtime_dir = MEMORY_ROOT / agent / "runtime"
    knowledge_dir = MEMORY_ROOT / agent / "knowledge"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    knowledge_dir.mkdir(parents=True, exist_ok=True)

    runtime_files = sorted(runtime_dir.glob(f"{run_id}*.md"))
    if not runtime_files:
        marker = knowledge_dir / f"{run_id}-compact.md"
        await asyncio.to_thread(marker.write_text, f"## Session {run_id} Compact\n\n- No runtime notes recorded.\n", encoding="utf-8")
        await asyncio.to_thread(_prune_runtime, runtime_dir)
        return str(marker)

    raw_notes = "\n\n---\n\n".join([await asyncio.to_thread(f.read_text, encoding="utf-8") for f in runtime_files])

    model_name = os.environ.get("COMPACTION_MODEL", "claude-haiku-4-5-20251001")
    llm = ChatAnthropic(model=model_name, temperature=0, max_tokens=600)
    try:
        response = await llm.ainvoke([HumanMessage(content=COMPACTION_PROMPT.format(run_id=run_id, raw_notes=raw_notes[:8000]))])
        summary = response.content if isinstance(response.content, str) else str(response.content)
    except Exception as exc:
        summary = f"## Session {run_id} Compact\n\n- Compaction failed: {type(exc).__name__}"

    compact_path = knowledge_dir / f"{run_id}-compact.md"
    await asyncio.to_thread(compact_path.write_text, summary, encoding="utf-8")

    await asyncio.to_thread(_prune_runtime, runtime_dir)
    return str(compact_path)


def write_runtime_note(agent: str, run_id: str, content: str):
    """Append a working note to the runtime context for this session."""
    runtime_dir = MEMORY_ROOT / agent / "runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    note_path = runtime_dir / f"{run_id}.md"
    ts = datetime.now(timezone.utc).isoformat()
    with note_path.open("a", encoding="utf-8") as f:
        f.write(f"\n\n<!-- {ts} -->\n{content}")


def _prune_runtime(runtime_dir: Path) -> None:
    """Delete runtime files older than RUNTIME_TTL_DAYS."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=RUNTIME_TTL_DAYS)
    for f in runtime_dir.glob("*.md"):
        mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
        if mtime < cutoff:
            f.unlink()
