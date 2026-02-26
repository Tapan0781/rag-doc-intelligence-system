from __future__ import annotations

import time

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from .api.v1.routes.health import router as health_router
from .api.v1.routes.ingest import router as ingest_router
from .api.v1.routes.query import router as query_router
from .core.errors import AppError
from .core.logging import configure_logging, log_request, request_id
from .core.rate_limit import enforce_rate_limit
from .core.security import require_api_key


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(
        title="RAG Doc Intelligence",
        version="1.0.0",
        dependencies=[Depends(require_api_key)],
    )

    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.error_code, "message": exc.message},
        )

    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        enforce_rate_limit(request)
        return await call_next(request)

    @app.middleware("http")
    async def access_log_middleware(request: Request, call_next):
        start = time.perf_counter()
        rid = request_id()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Request-Id"] = rid
        log_request(request, response.status_code, duration_ms, rid)
        return response

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"error": "internal_error", "message": str(exc)},
        )

    app.include_router(health_router, prefix="/api/v1", tags=["health"])
    app.include_router(ingest_router, prefix="/api/v1", tags=["ingest"])
    app.include_router(query_router, prefix="/api/v1", tags=["query"])

    return app


app = create_app()
