# Zo Super Server

A lightweight MCP/SSE gateway for the LoveLogic AI stack.

## Endpoints

- `GET /` - Health check
- `POST /api/mcp` - MCP endpoint protected by Bearer token or `X-API-Token` header
- `GET /sse` - Minimal Server-Sent Events stream

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Environment

- `ZO_SUPER_SERVER_HOST` - bind host (default `0.0.0.0`)
- `ZO_SUPER_SERVER_PORT` - bind port (default `8000`)
- `ZO_SUPER_SERVER_TOKEN` - Bearer/`X-API-Token` value for `/api/mcp` (default `changeme`)
