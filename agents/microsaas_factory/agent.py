"""Micro-SaaS Factory Agent — Skill Build #3."""
import json
import os
import uuid
from datetime import datetime, timezone

from anthropic import Anthropic
from langgraph.graph import StateGraph, START, END

from agents.shared.checkpointer import get_checkpointer
from agents.shared.memory import compact_session
from agents.shared.state import AgentState

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "")
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")


def _strip_json_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1])
    return text


def design_product(state: AgentState) -> dict:
    prompt = next(
        (getattr(m, "content", "") for m in state["messages"] if getattr(m, "type", "") == "human"),
        "Build a useful web utility",
    )
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=(
                "You are a micro-SaaS architect. Given a product prompt, design the simplest viable "
                "Cloudflare Worker utility under 500 lines. Return JSON with: "
                "worker_name, description, endpoint_spec (array of routes), "
                "value_proposition, target_user, x402_price_usdc (float), "
                "worker_code (full TypeScript Cloudflare Worker implementation)."
            ),
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as exc:
        return {"error": str(exc)}

    tokens_used = response.usage.input_tokens + response.usage.output_tokens
    return {
        "messages": [{"role": "assistant", "content": response.content[0].text}],
        "cost_usd": state["cost_usd"] + tokens_used * 0.000003,
        "turn_count": state["turn_count"] + 1,
    }


def deploy_worker(state: AgentState) -> dict:
    if state.get("error"):
        return {}
    last = next(
        (m for m in reversed(state["messages"]) if getattr(m, "type", None) == "ai"),
        None,
    )
    if not last:
        return {"error": "No worker design found"}
    try:
        design = json.loads(_strip_json_fences(last.content))
        if not isinstance(design, dict):
            return {"error": "Worker design response was not a JSON object"}
        worker_name = design.get("worker_name", "lovelogic-tool")
        print(f"[CLOUDFLARE] Deploying worker: {worker_name}")
        print(f"[CLOUDFLARE] x402 price: {design.get('x402_price_usdc', 0.10)} USDC")
        return {
            "messages": [
                {
                    "role": "tool",
                    "content": json.dumps(
                        {
                            "deployed": True,
                            "worker_name": worker_name,
                            "url": f"https://{worker_name}.lovelogicai.workers.dev",
                            "deployed_at": datetime.now(timezone.utc).isoformat(),
                        }
                    ),
                }
            ],
        }
    except (json.JSONDecodeError, TypeError) as exc:
        return {"error": str(exc)}


def announce_launch(state: AgentState) -> dict:
    last_tool = next(
        (m for m in reversed(state["messages"]) if getattr(m, "type", None) == "tool"),
        None,
    )
    if last_tool:
        try:
            deployment = json.loads(last_tool.content)
            if deployment.get("deployed"):
                url = deployment.get("url", "")
                name = deployment.get("worker_name", "")
                print(f"[TYPEFULLY] Announcing launch of {name}: {url}")
        except (json.JSONDecodeError, TypeError, AttributeError):
            pass
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
    builder.add_node("design_product", design_product)
    builder.add_node("deploy_worker", deploy_worker)
    builder.add_node("announce_launch", announce_launch)
    builder.add_node("log_and_end", log_and_end)

    builder.add_edge(START, "design_product")
    builder.add_edge("design_product", "deploy_worker")
    builder.add_edge("deploy_worker", "announce_launch")
    builder.add_edge("announce_launch", "log_and_end")
    builder.add_edge("log_and_end", END)

    return builder.compile(checkpointer=get_checkpointer())


async def run(
    workspace_id: str = "microsaas-factory",
    thread_id: str | None = None,
    product_prompt: str = "",
) -> AgentState:
    if not thread_id:
        thread_id = str(uuid.uuid4())
    graph = build_graph()
    initial: AgentState = {
        "messages": [{"role": "user", "content": product_prompt or "Build a useful web utility"}],
        "workspace_id": workspace_id,
        "session_id": str(uuid.uuid4()),
        "task": "build_and_deploy",
        "cost_usd": 0.0,
        "turn_count": 0,
        "memory_artifacts": [],
        "last_compaction": None,
        "error": None,
    }
    return await graph.ainvoke(initial, config={"configurable": {"thread_id": thread_id}})


if __name__ == "__main__":
    import asyncio
    asyncio.run(run(product_prompt="Build a URL expander API that reveals where short links actually go"))
