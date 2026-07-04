"""FastAPI application entry point for the Agentic IDE."""

from fastapi import FastAPI

from agentic_ide.config import settings
from agentic_ide.routes.health import router as health_router
from agentic_ide.routes.sessions import router as sessions_router

app = FastAPI(
    title="Agentic IDE",
    version="0.1.0",
    description="FastAPI + LangGraph orchestration service for the Agentic OS control plane.",
)

app.include_router(health_router)
app.include_router(sessions_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "agentic_ide.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
