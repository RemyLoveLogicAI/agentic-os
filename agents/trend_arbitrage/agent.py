"""Trend Arbitrage Agent — Skill Build #1.

Polls Musashi API every 2 minutes, identifies prediction market spreads > 5%,
alerts via Typefully, and logs every signal to the evidence ledger.
"""
import json
import os
import uuid
from datetime import datetime, timezone

import httpx
from anthropic import Anthropic
from langgraph.graph import StateGraph, START, END

from agents.shared.checkpointer import get_checkpointer
from agents.shared.memory import compact_session
from agents.shared.state import AgentState

MUSASHI_API_BASE = os.getenv("MUSASHI_API_BASE", "https://musashi.bot/api")
MUSASHI_API_KEY = os.getenv("MUSASHI_API_KEY", "")
ARBITRAGE_THRESHOLD = float(os.getenv("ARBITRAGE_THRESHOLD", "0.05"))
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ALERT_URGENCY_THRESHOLD = float(os.getenv("ALERT_URGENCY_THRESHOLD", "7.0"))


def poll_musashi(state: AgentState) -> AgentState:
    """Fetch latest signals from Musashi API."""
    try:
        resp = httpx.get(
            f"{MUSASHI_API_BASE}/signals",
            headers={"Authorization": f"Bearer {MUSASHI_API_KEY}"},
            timeout=10,
        )
        resp.raise_for_status()
        return {
            **state,
            "messages": state["messages"]
            + [
                {
                    "role": "tool",
                    "content": json.dumps(
                        {"signals": resp.json(), "polled_at": datetime.now(timezone.utc).isoformat()}
                    ),
                }
            ],
        }
    except Exception as exc:
        return {**state, "error": str(exc)}


def analyze_arbitrage(state: AgentState) -> AgentState:
    """Use Claude to identify spreads above threshold and rank by urgency."""
    if state.get("error"):
        return state

    last_tool = next((m for m in reversed(state["messages"]) if m.get("role") == "tool"), None)
    if not last_tool:
        return state

    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=(
            "You are a prediction market arbitrage analyst. Given market signals, "
            f"identify opportunities where the spread exceeds {ARBITRAGE_THRESHOLD * 100:.0f}%. "
            "Return JSON with keys: opportunities (array of objects with market, spread, urgency_score 0-10, summary), "
            "highest_urgency_score (float), alert_summary (string for Twitter). "
            "Return only valid JSON."
        ),
        messages=[{"role": "user", "content": f"Analyze: {last_tool['content']}"}],
    )
    tokens_used = response.usage.input_tokens + response.usage.output_tokens
    return {
        **state,
        "messages": state["messages"] + [{"role": "assistant", "content": response.content[0].text}],
        "cost_usd": state["cost_usd"] + tokens_used * 0.000003,
        "turn_count": state["turn_count"] + 1,
    }


def should_alert(state: AgentState) -> str:
    if state.get("error"):
        return "log_and_end"
    last = next((m for m in reversed(state["messages"]) if m.get("role") == "assistant"), None)
    if not last:
        return "log_and_end"
    try:
        data = json.loads(last["content"])
        if data.get("highest_urgency_score", 0) >= ALERT_URGENCY_THRESHOLD:
            return "send_alert"
    except (json.JSONDecodeError, TypeError):
        pass
    return "log_and_end"


def send_alert(state: AgentState) -> AgentState:
    """Post alert thread via Typefully skill (MCP call in production)."""
    last = next((m for m in reversed(state["messages"]) if m.get("role") == "assistant"), None)
    if last:
        try:
            data = json.loads(last["content"])
            print(f"[TYPEFULLY] Posting alert: {data.get('alert_summary', '')[:200]}")
        except (json.JSONDecodeError, TypeError):
            pass
    return state


def log_and_end(state: AgentState) -> AgentState:
    """Log outcome to evidence ledger and compact session memory."""
    entry = {
        "workspace": state["workspace_id"],
        "session": state["session_id"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "turns": state["turn_count"],
        "cost_usd": state["cost_usd"],
        "error": state.get("error"),
    }
    print(f"[EVIDENCE] {json.dumps(entry)}")
    compact_session(state["workspace_id"], state["session_id"], state["messages"])
    return state


def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("poll_musashi", poll_musashi)
    builder.add_node("analyze_arbitrage", analyze_arbitrage)
    builder.add_node("send_alert", send_alert)
    builder.add_node("log_and_end", log_and_end)

    builder.add_edge(START, "poll_musashi")
    builder.add_edge("poll_musashi", "analyze_arbitrage")
    builder.add_conditional_edges(
        "analyze_arbitrage",
        should_alert,
        {"send_alert": "send_alert", "log_and_end": "log_and_end"},
    )
    builder.add_edge("send_alert", "log_and_end")
    builder.add_edge("log_and_end", END)

    return builder.compile(checkpointer=get_checkpointer())


async def run(
    workspace_id: str = "trend-arbitrage-agent",
    thread_id: str = "default",
) -> AgentState:
    graph = build_graph()
    initial: AgentState = {
        "messages": [],
        "workspace_id": workspace_id,
        "session_id": str(uuid.uuid4()),
        "task": "poll_and_analyze",
        "cost_usd": 0.0,
        "turn_count": 0,
        "memory_artifacts": [],
        "last_compaction": None,
        "error": None,
    }
    return await graph.ainvoke(initial, config={"configurable": {"thread_id": thread_id}})


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
