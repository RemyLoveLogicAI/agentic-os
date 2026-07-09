"""FastAPI deployable version of the Zo Super Server."""

import asyncio
import os

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse

HOST = os.environ.get("ZO_SUPER_SERVER_HOST", "0.0.0.0")
PORT = int(os.environ.get("ZO_SUPER_SERVER_PORT", "8000"))
AUTH_TOKEN = os.environ.get("ZO_SUPER_SERVER_TOKEN", "changeme")

app = FastAPI(title="Zo Super Server", version="0.1.0")


def _verify_authorization(
    authorization: str | None, x_api_token: str | None = None
) -> None:
    if authorization and authorization.startswith("Bearer "):
        if authorization.split(" ", 1)[1] == AUTH_TOKEN:
            return
    if x_api_token == AUTH_TOKEN:
        return
    raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/")
async def health() -> dict:
    return {"ok": True, "service": "zo-super-server"}


@app.post("/api/mcp")
async def mcp_handler(
    request: Request,
    authorization: str | None = Header(None),
    x_api_token: str | None = Header(None, alias="X-API-Token"),
) -> dict:
    _verify_authorization(authorization, x_api_token)
    try:
        data = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON") from exc
    return {"received": data, "status": "ok"}


async def _sse_stream():
    yield "event: ping\ndata: zo-super-server alive\n\n"
    await asyncio.sleep(0.1)


@app.get("/sse")
async def sse_handler() -> StreamingResponse:
    return StreamingResponse(
        _sse_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


def main() -> None:
    import uvicorn

    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
