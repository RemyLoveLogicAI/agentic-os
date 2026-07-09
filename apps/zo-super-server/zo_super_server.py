# zo_super_server.py

import asyncio
from aiohttp import web
import os

# Config
HOST = os.environ.get("ZO_SUPER_SERVER_HOST", "0.0.0.0")
PORT = int(os.environ.get("ZO_SUPER_SERVER_PORT", "3000"))
AUTH_TOKEN = os.environ.get("ZO_SUPER_SERVER_TOKEN", "changeme")

routes = web.RouteTableDef()

@routes.get("/")
async def health(request):
    return web.json_response({"ok": True, "service": "zo-super-server"})

@routes.post("/api/mcp")
async def mcp_handler(request):
    # Simple Bearer token check
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer ") or auth.split(" ", 1)[1] != AUTH_TOKEN:
        return web.json_response({"error": "Unauthorized"}, status=401)
    try:
        data = await request.json()
    except Exception:
        return web.json_response({"error": "Invalid JSON"}, status=400)
    # Example: echo back the payload
    return web.json_response({"received": data, "status": "ok"})

@routes.get("/sse")
async def sse_handler(request):
    # Minimal SSE endpoint for event streaming
    response = web.StreamResponse(
        status=200,
        reason='OK',
        headers={
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
        }
    )
    await response.prepare(request)
    await response.write(b"event: ping\ndata: zo-super-server alive\n\n")
    await asyncio.sleep(0.1)
    return response

def main():
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, host=HOST, port=PORT)

if __name__ == "__main__":
    main()
