"""
Social Content Engine — Skill Build #2
Produces a full week of multi-platform content from a single brief.
Checkpoint backend is selected via CHECKPOINT_BACKEND env var (sqlite/dynamodb/postgres).
"""

import asyncio
import json
import os
from datetime import datetime, timezone
from typing import Annotated, Literal, TypedDict

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from packages.memory.checkpoint import get_checkpointer
from packages.memory.compaction import compact_session
from packages.memory.state import load_knowledge, save_artifact


# ── State ────────────────────────────────────────────────────────────────────

class ContentEngineState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    client_id: str
    run_id: str
    brief: str
    research: list[dict]
    content_plan: list[dict]
    published_ids: list[str]
    week_start: str


# ── Tools ─────────────────────────────────────────────────────────────────────

@tool
async def research_trends(topics: list[str], sources: list[str] | None = None) -> list[dict]:
    """Scrape trending content from Twitter, Reddit, GitHub, and HN via Firecrawl."""
    # Firecrawl MCP tool call goes here via the MCP tool bus
    # Returns structured trend objects with title, url, engagement, and summary
    default_sources = sources or ["twitter.com", "reddit.com", "news.ycombinator.com"]
    return [
        {
            "topic": topic,
            "sources": default_sources,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
            "status": "mcp_call_required",
        }
        for topic in topics
    ]


@tool
async def generate_content_plan(
    brief: str,
    brand_voice: str,
    trends: list[dict],
    platforms: list[str],
) -> list[dict]:
    """Generate a weekly content plan with post specs for each platform."""
    plan = []
    platform_formats = {
        "twitter": ("thread", 14),
        "linkedin": ("long-form", 5),
        "youtube": ("script", 2),
        "instagram": ("reel-script", 7),
    }
    for platform in platforms:
        fmt, count = platform_formats.get(platform, ("post", 3))
        for i in range(count):
            plan.append({
                "platform": platform,
                "format": fmt,
                "index": i + 1,
                "status": "draft",
                "scheduled_at": None,
            })
    return plan


@tool
async def produce_media_asset(content_spec: dict) -> dict:
    """Generate video/audio assets via fal.ai for reel scripts and voiceovers."""
    # fal.ai MCP tool calls go here via the MCP tool bus
    return {
        "spec": content_spec,
        "asset_type": "video" if content_spec.get("format") in ("reel-script",) else "audio",
        "status": "mcp_call_required",
        "produced_at": datetime.now(timezone.utc).isoformat(),
    }


@tool
async def schedule_posts(content_plan: list[dict], client_id: str) -> dict:
    """Schedule all approved posts across platforms via Typefully."""
    # Typefully MCP tool call goes here via the MCP tool bus
    scheduled = [p for p in content_plan if p.get("status") == "approved"]
    return {
        "scheduled_count": len(scheduled),
        "platforms": list({p.get("platform") for p in scheduled if p.get("platform")}),
        "client_id": client_id,
        "scheduled_at": datetime.now(timezone.utc).isoformat(),
        "status": "mcp_call_required",
    }


@tool
async def save_content_artifact(plan: list[dict], run_id: str, client_id: str) -> str:
    """Persist the content plan as a durable knowledge artifact."""
    artifact = {
        "run_id": run_id,
        "client_id": client_id,
        "ts": datetime.now(timezone.utc).isoformat(),
        "plan": plan,
    }
    save_artifact("social-content-engine", artifact)
    ledger_path = "ops/ledgers/social-content-audit.jsonl"
    os.makedirs(os.path.dirname(ledger_path), exist_ok=True)
    with open(ledger_path, "a") as f:
        f.write(json.dumps(artifact) + "\n")
    return f"Content plan saved: {run_id} ({len(plan)} items)"


TOOLS = [research_trends, generate_content_plan, produce_media_asset, schedule_posts, save_content_artifact]


# ── Nodes ─────────────────────────────────────────────────────────────────────

llm = ChatAnthropic(model="claude-opus-4-7", temperature=0.3).bind_tools(TOOLS)

SYSTEM_PROMPT = """You are the LoveLogicAI Social Content Engine.

Your weekly workflow:
1. Research trending topics in the client's niche using Firecrawl.
2. Generate a full content plan (14 X threads, 5 LinkedIn, 2 YouTube scripts, 7 Reels) aligned to brand voice.
3. Produce media asset specs for fal.ai tools where needed.
4. Save the content plan as a durable artifact before scheduling.
5. Schedule all posts via Typefully.

Client ID: {client_id}
Brand Voice:
{brand_voice}

Past performance:
{knowledge}
"""


async def content_director_node(state: ContentEngineState) -> ContentEngineState:
    brand_voice = load_knowledge("social-content-engine", key="brand-voice")
    knowledge = load_knowledge("social-content-engine", key="audience-feedback")
    messages = [
        SystemMessage(content=SYSTEM_PROMPT.format(
            client_id=state["client_id"],
            brand_voice=brand_voice or "Authoritative, concise, and educational. No hype.",
            knowledge=knowledge or "No prior performance data.",
        ))
    ] + state["messages"]
    response = await llm.ainvoke(messages)
    return {"messages": [response]}


async def tool_node(state: ContentEngineState) -> ContentEngineState:
    from langgraph.prebuilt import ToolNode
    tool_executor = ToolNode(TOOLS)
    return await tool_executor.ainvoke(state)


def should_continue(state: ContentEngineState) -> Literal["tools", "end"]:
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return "end"


# ── Graph ─────────────────────────────────────────────────────────────────────

def build_graph(checkpointer):
    g = StateGraph(ContentEngineState)
    g.add_node("director", content_director_node)
    g.add_node("tools", tool_node)
    g.add_edge(START, "director")
    g.add_conditional_edges("director", should_continue, {"tools": "tools", "end": END})
    g.add_edge("tools", "director")
    return g.compile(checkpointer=checkpointer)


# ── Entry point ───────────────────────────────────────────────────────────────

async def run_weekly(client_id: str, brief: str):
    checkpointer = get_checkpointer()
    graph = build_graph(checkpointer)

    run_id = f"content-{client_id}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}"
    week_start = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    config = {"configurable": {"thread_id": f"content-engine-{client_id}"}}

    initial_state: ContentEngineState = {
        "messages": [HumanMessage(content=f"Run ID {run_id}: produce this week's content plan.\n\nBrief:\n{brief}")],
        "client_id": client_id,
        "run_id": run_id,
        "brief": brief,
        "research": [],
        "content_plan": [],
        "published_ids": [],
        "week_start": week_start,
    }

    result = await graph.ainvoke(initial_state, config=config)
    compact_session("social-content-engine", run_id)
    return result


if __name__ == "__main__":
    brief = os.environ.get("CONTENT_BRIEF", "Focus this week on AI agent infrastructure and LoveLogicAI's agentic-os launch.")
    client_id = os.environ.get("CLIENT_ID", "lovelogicai")
    asyncio.run(run_weekly(client_id, brief))
