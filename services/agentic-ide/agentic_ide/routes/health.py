"""Health-check route."""

from fastapi import APIRouter

from agentic_ide.models import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse()
