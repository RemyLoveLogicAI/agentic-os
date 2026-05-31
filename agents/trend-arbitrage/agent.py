"""
Trend Arbitrage Agent — Skill Build #1
Monitors Musashi API every 2 min, surfaces prediction market spreads > 5%.
Checkpoint backend is selected via CHECKPOINT_BACKEND env var (sqlite/dynamodb/postgres).
"""

import asyncio
import json
import os
from datetime import datetime, timezone
from typing import Annotated, Literal, TypedDict

import httpx
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from packages.memory.checkpoint import get_checkpointer
from packages.memory.compaction import compact_session
from packages.memory.state import load_knowledge, save_signal


# ── State ────────────────────────────────────────────────────────────────────

class ArbitrageState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    run_id: str
    signals: list[dict]
    published: list[str]
    cost_usd: float
    last_run_ts: str


# ── Tools ─────────────────────────────────────────────────────────────────────

@tool
async def fetch_musashi_feed(categories: list[str] | None = None) -> dict:
    """Fetch live signals from Musashi API: tweet sentiment + market movers."""
    url = os.environ["MUSASHI_API_URL"] + "/v1/signals"
    headers = {"Authorization": f"Bearer {os.environ['MUSASHI_API_KEY']}"}
    params = {}
    if categories:
        params["categories"] = ",".join(categories)

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, headers=headers, params=params)
        resp.raise_for_status()
        return resp.json()


@tool
async def detect_arbitrage_spreads(signals: list[dict], min_spread_pct: float = 5.0) -> list[dict]:
    """Filter signals to those with cross-market spread above the threshold."""
    opportunities = []
    for sig in signals:
        spread = sig.get("spread_pct", 0)
        if spread >= min_spread_pct:
            market = sig.get("market")
            platform_a = sig.get("platform_a")
            platform_b = sig.get("platform_b")
            if not (market and platform_a and platform_b):
                continue
            opportunities.append({
                "market": market,
                "platform_a": platform_a,
                "platform_b": platform_b,
                "spread_pct": spread,
                "urgency": sig.get("urgency_score", 0),
                "detected_at": datetime.now(timezone.utc).isoformat(),
            })
    return sorted(opportunities, key=lambda x: x["spread_pct"], reverse=True)


@tool
async def publish_signal_thread(opportunities: list[dict]) -> dict:
    """Publish top arbitrage signals as a scheduled Typefully thread."""
    if not opportunities:
        return {"published": False, "reason": "no_opportunities"}

    top = [o for o in opportunities if o.get("urgency", 0) >= 7][:3]
    if not top:
        return {"published": False, "reason": "no_high_urgency_opportunities"}
    thread_lines = ["🧠 AI Arbitrage Signal — " + datetime.now(timezone.utc).strftime("%b %d %H:%M UTC"), ""]
    for i, opp in enumerate(top, 1):
        thread_lines.append(
            f"{i}. {opp['market']}\n"
            f"   {opp['platform_a']} vs {opp['platform_b']}\n"
            f"   Spread: {opp['spread_pct']:.1f}%  |  Urgency: {opp['urgency']}/10"
        )
    thread_lines.append("\nSignals by @LoveLogicAI — subscribe: lovelogic.ai/signals")

    # Typefully MCP call would go here via the MCP tool bus
    return {"published": True, "lines": thread_lines, "count": len(top)}


@tool
async def log_evidence(signal: dict, run_id: str) -> str:
    """Append an evidence artifact to the audit ledger (required before any publish)."""
    artifact = {
        "run_id": run_id,
        "ts": datetime.now(timezone.utc).isoformat(),
        "signal": signal,
    }
    save_signal(artifact, agent="trend-arbitrage")
    ledger_path = "ops/ledgers/trend-arbitrage-audit.jsonl"

    def _write() -> None:
        os.makedirs(os.path.dirname(ledger_path), exist_ok=True)
        with open(ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(artifact) + "\n")

    await asyncio.to_thread(_write)
    return f"Evidence logged: {run_id}"


TOOLS = [fetch_musashi_feed, detect_arbitrage_spreads, publish_signal_thread, log_evidence]


# ── Nodes ─────────────────────────────────────────────────────────────────────

llm = ChatAnthropic(model="claude-opus-4-8").bind_tools(TOOLS)

SYSTEM_PROMPT = """You are the LoveLogicAI Trend Arbitrage Agent.

Your job every run:
1. Fetch the latest signals from Musashi API.
2. Detect arbitrage spreads > 5% across Polymarket / Kalshi.
3. Log evidence for every signal before publishing.
4. Publish only the top 3 spreads via Typefully if urgency >= 7.
5. Keep your reasoning concise — no bloat.

Current knowledge base:
{knowledge}
"""


async def analyst_node(state: ArbitrageState) -> ArbitrageState:
    knowledge = load_knowledge("trend-arbitrage")
    messages = [SystemMessage(content=SYSTEM_PROMPT.format(knowledge=knowledge))] + state["messages"]
    response = await llm.ainvoke(messages)
    return {"messages": [response]}


async def tool_node(state: ArbitrageState) -> ArbitrageState:
    from langgraph.prebuilt import ToolNode
    tool_executor = ToolNode(TOOLS)
    return await tool_executor.ainvoke(state)


def should_continue(state: ArbitrageState) -> Literal["tools", "end"]:
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return "end"


# ── Graph ─────────────────────────────────────────────────────────────────────

def build_graph(checkpointer):
    g = StateGraph(ArbitrageState)
    g.add_node("analyst", analyst_node)
    g.add_node("tools", tool_node)
    g.add_edge(START, "analyst")
    g.add_conditional_edges("analyst", should_continue, {"tools": "tools", "end": END})
    g.add_edge("tools", "analyst")
    return g.compile(checkpointer=checkpointer)


# ── Entry point ───────────────────────────────────────────────────────────────

async def run_once(thread_id: str = "trend-arbitrage-main"):
    checkpointer = get_checkpointer()
    graph = build_graph(checkpointer)

    run_id = f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}"
    config = {"configurable": {"thread_id": thread_id}}

    initial_state: ArbitrageState = {
        "messages": [HumanMessage(content=f"Run ID {run_id}: fetch signals, detect spreads, log evidence, publish top opportunities.")],
        "run_id": run_id,
        "signals": [],
        "published": [],
        "cost_usd": 0.0,
        "last_run_ts": datetime.now(timezone.utc).isoformat(),
    }

    result = await graph.ainvoke(initial_state, config=config)

    # Compact session memory after each run
    await compact_session("trend-arbitrage", run_id)

    return result


if __name__ == "__main__":
    asyncio.run(run_once())
