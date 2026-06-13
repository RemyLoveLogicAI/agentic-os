"""Unit tests for the LangGraph workflow."""

import pytest

from agentic_ide.graph.nodes import classify, route
from agentic_ide.models import RiskLevel
from agentic_ide.services.session_store import store


def _make_state(command: str) -> dict:
    session = store.create()
    return {
        "session_id": session.session_id,
        "command": command,
        "context": {},
        "events": [],
    }


def test_classify_echo() -> None:
    state = _make_state("echo hello world")
    result = classify(state)
    assert result["intent"] == "echo"
    assert result["risk"] == RiskLevel.safe
    assert result["tool_name"] == "echo"


def test_classify_risky() -> None:
    state = _make_state("delete all echo data")
    result = classify(state)
    assert result["risk"] == RiskLevel.needs_approval


def test_classify_unknown() -> None:
    state = _make_state("do something weird")
    result = classify(state)
    assert result["intent"] == "unknown"
    assert result["risk"] == RiskLevel.reject


def test_route_safe() -> None:
    assert route({"risk": RiskLevel.safe}) == "execute"


def test_route_needs_approval() -> None:
    assert route({"risk": RiskLevel.needs_approval}) == "await_approval"


def test_route_reject() -> None:
    assert route({"risk": RiskLevel.reject}) == "reject"
