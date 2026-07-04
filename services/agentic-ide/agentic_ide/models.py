"""Pydantic models for requests, responses, and domain objects."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# --- Enums -------------------------------------------------------------------

class RiskLevel(str, Enum):
    safe = "safe"
    needs_approval = "needs_approval"
    reject = "reject"


class ActionStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    executed = "executed"
    failed = "failed"
    rejected = "rejected"


# --- Domain ------------------------------------------------------------------

class SessionEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    node: str
    payload: dict[str, Any] = Field(default_factory=dict)


class Session(BaseModel):
    session_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    history: list[SessionEvent] = Field(default_factory=list)
    state: dict[str, Any] = Field(default_factory=dict)


# --- Requests ----------------------------------------------------------------

class ActRequest(BaseModel):
    command: str
    context: dict[str, Any] = Field(default_factory=dict)


# --- Responses ---------------------------------------------------------------

class SessionResponse(BaseModel):
    session_id: str
    created_at: datetime
    state: dict[str, Any]


class ActResponse(BaseModel):
    session_id: str
    status: ActionStatus
    risk: RiskLevel
    result: Any = None
    events: list[SessionEvent] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "agentic-ide"
    version: str = "0.1.0"
