"""LangGraph node functions — each node is a pure-ish transform on WorkflowState."""

from __future__ import annotations

from agentic_ide.models import RiskLevel, ActionStatus, SessionEvent
from agentic_ide.graph.state import WorkflowState
from agentic_ide.services.tool_registry import registry
from agentic_ide.services.session_store import store

# Keywords that signal a built-in tool invocation
_TOOL_KEYWORDS: dict[str, str] = {
    "echo": "echo",
    "ping": "echo",
    "status": "status",
    "health": "status",
}

# Commands that require human approval before execution
_RISKY_KEYWORDS: set[str] = {"delete", "remove", "drop", "reset", "destroy"}


def classify(state: WorkflowState) -> WorkflowState:
    """Determine intent and risk level from the raw command."""
    command = state["command"].strip().lower()

    # Determine intent
    intent = "unknown"
    tool_name = ""
    tool_args: dict = {}
    for keyword, tool in _TOOL_KEYWORDS.items():
        if keyword in command:
            intent = tool
            tool_name = tool
            tool_args = {"message": state["command"]}
            break

    # Assess risk
    risk = RiskLevel.safe
    for risky in _RISKY_KEYWORDS:
        if risky in command:
            risk = RiskLevel.needs_approval
            break

    if intent == "unknown":
        risk = RiskLevel.reject

    event = SessionEvent(node="classify", payload={"intent": intent, "risk": risk.value})
    store.append_event(state["session_id"], event)

    return {
        **state,
        "intent": intent,
        "risk": risk,
        "tool_name": tool_name,
        "tool_args": tool_args,
        "events": [*state.get("events", []), event],
    }


def route(state: WorkflowState) -> str:
    """Conditional edge: decide which node comes next based on risk."""
    risk = state.get("risk", RiskLevel.reject)
    if risk == RiskLevel.safe:
        return "execute"
    if risk == RiskLevel.needs_approval:
        return "await_approval"
    return "reject"


async def execute(state: WorkflowState) -> WorkflowState:
    """Run the selected tool and capture the result."""
    tool_name = state.get("tool_name", "")
    tool_args = state.get("tool_args", {})

    try:
        result = await registry.invoke(tool_name, tool_args)
        status = ActionStatus.executed
        error = None
    except Exception as exc:
        result = None
        status = ActionStatus.failed
        error = str(exc)

    event = SessionEvent(
        node="execute",
        payload={"tool": tool_name, "status": status.value, "result": result, "error": error},
    )
    store.append_event(state["session_id"], event)

    return {
        **state,
        "status": status,
        "result": result,
        "error": error,
        "events": [*state.get("events", []), event],
    }


def await_approval(state: WorkflowState) -> WorkflowState:
    """Park the action — requires human approval before proceeding."""
    event = SessionEvent(
        node="await_approval",
        payload={"tool": state.get("tool_name", ""), "risk": state.get("risk", "needs_approval")},
    )
    store.append_event(state["session_id"], event)

    return {
        **state,
        "status": ActionStatus.pending,
        "result": None,
        "error": None,
        "events": [*state.get("events", []), event],
    }


def reject(state: WorkflowState) -> WorkflowState:
    """Reject an unrecognised or dangerous command."""
    event = SessionEvent(
        node="reject",
        payload={"command": state.get("command", ""), "reason": "unrecognised or rejected"},
    )
    store.append_event(state["session_id"], event)

    return {
        **state,
        "status": ActionStatus.rejected,
        "result": None,
        "error": "Command not recognised or rejected by policy",
        "events": [*state.get("events", []), event],
    }


def verify(state: WorkflowState) -> WorkflowState:
    """Capture evidence and finalise the workflow."""
    status = state.get("status", ActionStatus.failed)
    event = SessionEvent(
        node="verify",
        payload={"final_status": status.value, "has_result": state.get("result") is not None},
    )
    store.append_event(state["session_id"], event)
    store.update_state(state["session_id"], {"last_status": status.value})

    return {
        **state,
        "events": [*state.get("events", []), event],
    }
