"""Build the LangGraph workflow for the Agentic IDE command loop."""

from __future__ import annotations

from langgraph.graph import StateGraph, END

from agentic_ide.graph.state import WorkflowState
from agentic_ide.graph import nodes


def build_workflow() -> StateGraph:
    """
    Construct the graph:

        classify → route ─┬─ execute ─────→ verify → END
                          ├─ await_approval → verify → END
                          └─ reject ────────→ verify → END
    """
    graph = StateGraph(WorkflowState)

    graph.add_node("classify", nodes.classify)
    graph.add_node("execute", nodes.execute)
    graph.add_node("await_approval", nodes.await_approval)
    graph.add_node("reject", nodes.reject)
    graph.add_node("verify", nodes.verify)

    graph.set_entry_point("classify")
    graph.add_conditional_edges("classify", nodes.route, {
        "execute": "execute",
        "await_approval": "await_approval",
        "reject": "reject",
    })

    graph.add_edge("execute", "verify")
    graph.add_edge("await_approval", "verify")
    graph.add_edge("reject", "verify")
    graph.add_edge("verify", END)

    return graph


def compile_workflow():
    """Return a compiled, invocable graph."""
    return build_workflow().compile()
