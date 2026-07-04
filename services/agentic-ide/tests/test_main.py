"""Integration tests for the Agentic IDE FastAPI app."""

import pytest
from httpx import ASGITransport, AsyncClient

from agentic_ide.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health(client: AsyncClient) -> None:
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "agentic-ide"


@pytest.mark.asyncio
async def test_create_session(client: AsyncClient) -> None:
    resp = await client.post("/sessions")
    assert resp.status_code == 201
    data = resp.json()
    assert "session_id" in data


@pytest.mark.asyncio
async def test_get_session(client: AsyncClient) -> None:
    create = await client.post("/sessions")
    sid = create.json()["session_id"]

    resp = await client.get(f"/sessions/{sid}")
    assert resp.status_code == 200
    assert resp.json()["session_id"] == sid


@pytest.mark.asyncio
async def test_session_not_found(client: AsyncClient) -> None:
    resp = await client.get("/sessions/nonexistent")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_act_echo(client: AsyncClient) -> None:
    create = await client.post("/sessions")
    sid = create.json()["session_id"]

    resp = await client.post(f"/sessions/{sid}/act", json={"command": "echo hello"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "executed"
    assert data["risk"] == "safe"
    assert data["result"]["echo"] == "echo hello"


@pytest.mark.asyncio
async def test_act_status(client: AsyncClient) -> None:
    create = await client.post("/sessions")
    sid = create.json()["session_id"]

    resp = await client.post(f"/sessions/{sid}/act", json={"command": "health check"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "executed"
    assert data["result"]["status"] == "ok"


@pytest.mark.asyncio
async def test_act_needs_approval(client: AsyncClient) -> None:
    create = await client.post("/sessions")
    sid = create.json()["session_id"]

    resp = await client.post(f"/sessions/{sid}/act", json={"command": "delete echo this"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "pending"
    assert data["risk"] == "needs_approval"


@pytest.mark.asyncio
async def test_act_reject(client: AsyncClient) -> None:
    create = await client.post("/sessions")
    sid = create.json()["session_id"]

    resp = await client.post(f"/sessions/{sid}/act", json={"command": "unknown command xyz"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "rejected"
    assert data["risk"] == "reject"


@pytest.mark.asyncio
async def test_history(client: AsyncClient) -> None:
    create = await client.post("/sessions")
    sid = create.json()["session_id"]

    await client.post(f"/sessions/{sid}/act", json={"command": "echo test"})

    resp = await client.get(f"/sessions/{sid}/history")
    assert resp.status_code == 200
    events = resp.json()
    assert len(events) >= 2  # classify + execute + verify
    nodes = [e["node"] for e in events]
    assert "classify" in nodes
    assert "verify" in nodes
