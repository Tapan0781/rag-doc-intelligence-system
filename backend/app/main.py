from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .api.v1.routes.ingest import router as ingest_router
from .api.v1.routes.query import router as query_router
from .core.errors import AppError
from .core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="RAG Doc Intelligence", version="1.0.0")

    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.error_code, "message": exc.message},
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"error": "internal_error", "message": str(exc)},
        )

    app.include_router(ingest_router, prefix="/api/v1", tags=["ingest"])
    app.include_router(query_router, prefix="/api/v1", tags=["query"])

    return app


app = create_app()
