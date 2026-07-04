"""In-memory session store. Swap for Redis / DB in production."""

from __future__ import annotations

from agentic_ide.models import Session, SessionEvent


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def create(self) -> Session:
        session = Session()
        self._sessions[session.session_id] = session
        return session

    def get(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)

    def append_event(self, session_id: str, event: SessionEvent) -> None:
        session = self._sessions.get(session_id)
        if session is None:
            raise KeyError(f"Session {session_id} not found")
        session.history.append(event)

    def update_state(self, session_id: str, patch: dict) -> None:
        session = self._sessions.get(session_id)
        if session is None:
            raise KeyError(f"Session {session_id} not found")
        session.state.update(patch)

    def list_ids(self) -> list[str]:
        return list(self._sessions.keys())


store = SessionStore()
