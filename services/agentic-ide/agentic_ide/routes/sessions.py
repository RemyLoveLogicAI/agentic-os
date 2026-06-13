"""Session management and agent command execution routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from agentic_ide.models import (
    ActRequest,
    ActResponse,
    ActionStatus,
    RiskLevel,
    SessionEvent,
    SessionResponse,
)
from agentic_ide.services.session_store import store
from agentic_ide.graph.workflow import compile_workflow

router = APIRouter(prefix="/sessions", tags=["sessions"])

_workflow = compile_workflow()


@router.post("", response_model=SessionResponse, status_code=201)
async def create_session() -> SessionResponse:
    session = store.create()
    return SessionResponse(
        session_id=session.session_id,
        created_at=session.created_at,
        state=session.state,
    )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str) -> SessionResponse:
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse(
        session_id=session.session_id,
        created_at=session.created_at,
        state=session.state,
    )


@router.post("/{session_id}/act", response_model=ActResponse)
async def act(session_id: str, body: ActRequest) -> ActResponse:
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    initial_state = {
        "session_id": session_id,
        "command": body.command,
        "context": body.context,
        "events": [],
    }

    final_state = await _workflow.ainvoke(initial_state)

    return ActResponse(
        session_id=session_id,
        status=final_state.get("status", ActionStatus.failed),
        risk=final_state.get("risk", RiskLevel.reject),
        result=final_state.get("result"),
        events=final_state.get("events", []),
    )


@router.get("/{session_id}/history", response_model=list[SessionEvent])
async def history(session_id: str) -> list[SessionEvent]:
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.history
