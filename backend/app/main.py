"""FastAPI application entry point."""

from fastapi import FastAPI, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.app.routes import approval, assessment, evidence, health, machines, telemetry

app = FastAPI(
    title="ForgeGuard API",
    description="REST API for the ForgeGuard industrial maintenance decision-support pipeline.",
    version="1.0.0",
)
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(machines.router, prefix="/api/v1", tags=["machines"])
app.include_router(telemetry.router, prefix="/api/v1", tags=["telemetry"])
app.include_router(evidence.router, prefix="/api/v1", tags=["evidence"])
app.include_router(assessment.router, prefix="/api/v1", tags=["assessment"])
app.include_router(approval.router, prefix="/api/v1", tags=["approval"])


@app.exception_handler(RequestValidationError)
async def handle_validation_error(
    request: Request,
    error: RequestValidationError,
) -> JSONResponse:
    if request.url.path == "/api/v1/approval":
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid approval request"},
        )
    return await request_validation_exception_handler(request, error)
