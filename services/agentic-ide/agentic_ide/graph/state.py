"""LangGraph state definition for the Agentic IDE workflow."""

from __future__ import annotations

from typing import Any, TypedDict

from agentic_ide.models import RiskLevel, ActionStatus, SessionEvent


class WorkflowState(TypedDict, total=False):
    session_id: str
    command: str
    context: dict[str, Any]
    intent: str
    risk: RiskLevel
    tool_name: str
    tool_args: dict[str, Any]
    status: ActionStatus
    result: Any
    error: str | None
    events: list[SessionEvent]
