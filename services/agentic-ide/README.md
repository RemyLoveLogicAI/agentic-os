# Agentic IDE — MVP

FastAPI + LangGraph service for the Agentic OS control plane.

## Architecture

```
Request → FastAPI Router → LangGraph Workflow → Tool Execution → Response
                              ↕
                        Session State
```

The service exposes a REST API that drives a LangGraph-based agent workflow:

- **classify** — Determine intent and risk level from user input
- **route** — Select execution path (safe / needs-approval / reject)
- **execute** — Run the approved action via the tool registry
- **verify** — Confirm the result and capture evidence

## Quick Start

```bash
cd services/agentic-ide
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn agentic_ide.main:app --reload
```

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness check |
| POST | `/sessions` | Create a new agent session |
| GET | `/sessions/{id}` | Retrieve session state |
| POST | `/sessions/{id}/act` | Submit a command to the agent workflow |
| GET | `/sessions/{id}/history` | Event history for a session |

## Tests

```bash
pytest
```
