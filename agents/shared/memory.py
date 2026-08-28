import math
import os
from datetime import datetime, timezone
from pathlib import Path

MEMORY_ROOT = Path(os.getenv("MEMORY_ROOT", "./memory/workspace"))
DECAY_LAMBDA = 0.05


def _msg_type(m) -> str:
    """Normalize message type from a dict or a LangChain BaseMessage."""
    if hasattr(m, "type"):
        return m.type  # BaseMessage: "ai", "human", "tool"
    if hasattr(m, "get"):
        role = m.get("role", "")
        return "ai" if role == "assistant" else role
    return ""


def _msg_content(m) -> str:
    """Return string content from a dict or a LangChain BaseMessage."""
    if hasattr(m, "content"):
        content = m.content
    elif hasattr(m, "get"):
        content = m.get("content", "")
    else:
        content = ""
    return content if isinstance(content, str) else str(content) if content is not None else ""


def workspace_path(workspace_id: str) -> Path:
    safe_id = Path(workspace_id).name
    if not safe_id or safe_id in (".", "..") or safe_id != workspace_id:
        raise ValueError(f"Invalid workspace_id: {workspace_id!r}")
    root = MEMORY_ROOT.resolve()
    resolved = (root / safe_id).resolve()
    if root not in resolved.parents:
        raise ValueError(f"Invalid workspace_id: {workspace_id!r}")
    return resolved


def freshness_score(last_accessed: str, base_weight: float = 1.0) -> float:
    dt = datetime.fromisoformat(last_accessed)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    days = max(0, (datetime.now(timezone.utc) - dt).total_seconds() / 86400)
    return base_weight * math.exp(-DECAY_LAMBDA * days)


def compact_session(workspace_id: str, session_id: str, messages: list) -> str:
    """Summarize raw session turns into a structured Markdown artifact."""
    base = workspace_path(workspace_id) / "runtime"
    base.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).isoformat()
    assistant_msgs = [m for m in messages if _msg_type(m) in ("ai", "assistant")]
    tool_msgs = [m for m in messages if _msg_type(m) == "tool"]

    lines = [
        "---",
        f'id: "session-{session_id}"',
        f'workspace: "{workspace_id}"',
        "type: runtime",
        f'created: "{now}"',
        f'last_accessed: "{now}"',
        "freshness_score: 1.0",
        "---",
        "",
        f"# Session {session_id} — Compact Summary",
        "",
        f"**Workspace:** {workspace_id}",
        f"**Completed:** {now}",
        f"**Turns:** {len(messages)}",
        f"**Tool calls:** {len(tool_msgs)}",
        "",
        "## Key Assistant Actions",
        "",
    ]
    for i, msg in enumerate(assistant_msgs[:8], 1):
        content = _msg_content(msg)
        if content.strip():
            lines.append(f"{i}. {content[:300]}")

    path = base / f"session-{session_id}.md"
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
