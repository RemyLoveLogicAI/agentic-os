import math
import os
from datetime import datetime, timezone
from pathlib import Path

MEMORY_ROOT = Path(os.getenv("MEMORY_ROOT", "./memory/workspace"))
DECAY_LAMBDA = 0.05


def workspace_path(workspace_id: str) -> Path:
    return MEMORY_ROOT / workspace_id


def freshness_score(last_accessed: str, base_weight: float = 1.0) -> float:
    dt = datetime.fromisoformat(last_accessed)
    days = max(0, (datetime.now(timezone.utc) - dt).total_seconds() / 86400)
    return base_weight * math.exp(-DECAY_LAMBDA * days)


def compact_session(workspace_id: str, session_id: str, messages: list) -> str:
    """Summarize raw session turns into a structured Markdown artifact."""
    base = workspace_path(workspace_id) / "runtime"
    base.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).isoformat()
    assistant_msgs = [m for m in messages if m.get("role") == "assistant"]
    tool_msgs = [m for m in messages if m.get("role") == "tool"]

    lines = [
        f"---",
        f'id: "session-{session_id}"',
        f'workspace: "{workspace_id}"',
        f"type: runtime",
        f'created: "{now}"',
        f'last_accessed: "{now}"',
        f"freshness_score: 1.0",
        f"---",
        f"",
        f"# Session {session_id[:8]} — Compact Summary",
        f"",
        f"**Workspace:** {workspace_id}",
        f"**Completed:** {now}",
        f"**Turns:** {len(messages)}",
        f"**Tool calls:** {len(tool_msgs)}",
        f"",
        f"## Key Assistant Actions",
        f"",
    ]
    for i, msg in enumerate(assistant_msgs[:8], 1):
        content = msg.get("content", "")
        if isinstance(content, str) and content.strip():
            lines.append(f"{i}. {content[:300]}")

    path = base / f"session-{session_id[:8]}.md"
    path.write_text("\n".join(lines))
    return str(path)


def prune_stale_runtime(workspace_id: str, threshold: float = 0.1) -> int:
    runtime_path = workspace_path(workspace_id) / "runtime"
    if not runtime_path.exists():
        return 0
    pruned = 0
    for md_file in runtime_path.glob("*.md"):
        text = md_file.read_text()
        for line in text.splitlines():
            if line.startswith("last_accessed:"):
                ts = line.split(":", 1)[1].strip().strip('"')
                if freshness_score(ts, base_weight=0.6) < threshold:
                    md_file.unlink()
                    pruned += 1
                break
    return pruned
