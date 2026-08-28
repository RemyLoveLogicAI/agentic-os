"""Social Content Engine — Skill Build #2."""
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

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
TYPEFULLY_API_KEY = os.getenv("TYPEFULLY_API_KEY", "")


def _strip_json_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1])
    return text


def research_trends(state: AgentState) -> dict:
    try:
        resp = httpx.post(
            "https://api.firecrawl.dev/v1/scrape",
            headers={"Authorization": f"Bearer {FIRECRAWL_API_KEY}"},
            json={"url": "https://trends24.in", "formats": ["markdown"]},
            timeout=20,
        )
        resp.raise_for_status()
        return {
            "messages": [
                {
                    "role": "user",
                    "content": json.dumps(
                        {"trends": resp.json(), "researched_at": datetime.now(timezone.utc).isoformat()}
                    ),
                }
            ],
        }
    except Exception as exc:
        return {"error": str(exc)}


def generate_content(state: AgentState) -> dict:
    if state.get("error"):
        return {}

    human_msgs = [m for m in state["messages"] if getattr(m, "type", None) == "human"]
    weekly_brief = human_msgs[0].content if human_msgs else "Produce this week's content"
    trend_data = human_msgs[-1].content if len(human_msgs) > 1 else weekly_brief

    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=(
                "You are a professional content strategist for LoveLogicAI. "
                "Given trending topics, produce a full week of content. "
                "Return JSON with: x_threads (array of 7-tweet threads), linkedin_posts (array), "
                "youtube_scripts (array of 60s scripts), reel_hooks (array of 15s hooks). "
                "Each piece should have: platform, content, hashtags, posting_time, media_prompt. "
                "Optimize for virality and brand authenticity."
            ),
            messages=[
                {
                    "role": "user",
                    "content": f"Campaign brief: {weekly_brief}\n\nTrend data: {trend_data}",
                }
            ],
        )
    except Exception as exc:
        return {"error": str(exc)}

    raw_text = response.content[0].text
    try:
        json.loads(_strip_json_fences(raw_text))
    except (json.JSONDecodeError, ValueError):
        return {"error": f"generate_content: LLM response is not valid JSON: {raw_text[:200]}"}
    tokens_used = response.usage.input_tokens + response.usage.output_tokens
    return {
        "messages": [{"role": "assistant", "content": raw_text}],
        "cost_usd": state["cost_usd"] + tokens_used * 0.000003,
        "turn_count": state["turn_count"] + 1,
    }


def schedule_content(state: AgentState) -> dict:
    if state.get("error"):
        return {}
    last = next(
        (m for m in reversed(state["messages"]) if getattr(m, "type", None) == "ai"),
        None,
    )
    if last:
        try:
            data = json.loads(_strip_json_fences(last.content))
            thread_count = len(data.get("x_threads", []))
            linkedin_count = len(data.get("linkedin_posts", []))
            print(f"[TYPEFULLY] Scheduling {thread_count} X threads, {linkedin_count} LinkedIn posts")
        except (json.JSONDecodeError, TypeError, AttributeError):
            print("[TYPEFULLY] Scheduling content batch")
    return {}


def log_and_end(state: AgentState) -> dict:
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
    return {}


def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("research_trends", research_trends)
    builder.add_node("generate_content", generate_content)
    builder.add_node("schedule_content", schedule_content)
    builder.add_node("log_and_end", log_and_end)

    builder.add_edge(START, "research_trends")
    builder.add_edge("research_trends", "generate_content")
    builder.add_edge("generate_content", "schedule_content")
    builder.add_edge("schedule_content", "log_and_end")
    builder.add_edge("log_and_end", END)

    return builder.compile(checkpointer=get_checkpointer())


async def run(
    workspace_id: str = "social-content-engine",
    thread_id: str | None = None,
    weekly_brief: str = "",
) -> AgentState:
    if not thread_id:
        thread_id = str(uuid.uuid4())
    graph = build_graph()
    initial: AgentState = {
        "messages": [{"role": "user", "content": weekly_brief or "Produce this week's content"}],
        "workspace_id": workspace_id,
        "session_id": str(uuid.uuid4()),
        "task": "weekly_content_production",
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
