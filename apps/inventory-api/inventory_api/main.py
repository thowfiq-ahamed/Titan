"""
TITAN Inventory API - Main Application Entrypoint
Standardized enterprise FastAPI service with Prometheus metrics,
correlation ID tracing, structured logging, and Kubernetes lifecycle hooks.
"""

import time
import uuid
import random
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config import settings
from .logging import logger, correlation_id_ctx
from .database import init_db
from .metrics import (
    HTTP_REQUESTS_TOTAL,
    HTTP_REQUEST_DURATION_SECONDS,
    get_metrics_response
)
from .routers import health, items, fault_injection
from .routers.fault_injection import get_runtime_fault_state


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup and shutdown lifecycle management."""
    logger.info(
        f"Starting {settings.APP_NAME} v{settings.APP_VERSION} (Env: {settings.ENVIRONMENT})"
    )
    # Initialize DB schema if running in development / test SQLite mode
    try:
        init_db()
    except Exception as exc:
        logger.warning(f"Database schema auto-init deferred or failed: {str(exc)}")
    yield
    logger.info(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title="TITAN Inventory API",
    description="Core workload API for TITAN Cloud-Native Delivery & Reliability Intelligence Platform",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def titan_telemetry_and_fault_middleware(request: Request, call_next):
    """
    Core middleware handling:
    1. Correlation ID extraction or generation
    2. Fault injection simulation (latency & error surge)
    3. Metrics recording (rate, errors, duration)
    4. Structured request/response logging
    """
    correlation_id = request.headers.get("X-Correlation-ID") or request.headers.get("X-Request-ID")
    if not correlation_id:
        correlation_id = str(uuid.uuid4())
    correlation_id_ctx.set(correlation_id)

    path = request.url.path
    method = request.method
    start_time = time.perf_counter()

    # Apply controlled fault injection if path is not a health check or fault config
    if settings.ENABLE_FAULT_INJECTION and not path.startswith(("/health", "/test/faults", "/metrics")):
        faults = get_runtime_fault_state()

        # 1. Latency injection
        latency_ms = faults.get("artificial_latency_ms", 0)
        if latency_ms > 0:
            time.sleep(latency_ms / 1000.0)

        # 2. Error surge injection (simulates bad release producing HTTP 500s)
        if faults.get("error_rate_enabled", False):
            pct = faults.get("error_rate_percentage", 100)
            if random.randint(1, 100) <= pct:
                duration = time.perf_counter() - start_time
                HTTP_REQUESTS_TOTAL.labels(method=method, endpoint=path, status_code="500").inc()
                HTTP_REQUEST_DURATION_SECONDS.labels(method=method, endpoint=path).observe(duration)
                logger.error(
                    f"Simulated bad release error surge triggered on {method} {path}",
                    extra={"http_status": 500, "duration_ms": round(duration * 1000, 2)}
                )
                res = JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={
                        "error": "SimulatedInternalError",
                        "message": "Controlled reliability experiment: simulated bad release failure",
                        "status_code": 500,
                        "correlation_id": correlation_id
                    }
                )
                res.headers["X-Correlation-ID"] = correlation_id
                return res

    try:
        response: Response = await call_next(request)
        duration = time.perf_counter() - start_time

        # Record metrics
        status_code_str = str(response.status_code)
        HTTP_REQUESTS_TOTAL.labels(method=method, endpoint=path, status_code=status_code_str).inc()
        HTTP_REQUEST_DURATION_SECONDS.labels(method=method, endpoint=path).observe(duration)

        # Attach correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id

        # Structured request logging
        logger.info(
            f"{method} {path} - {response.status_code} ({round(duration * 1000, 2)}ms)",
            extra={
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2)
            }
        )
        return response

    except Exception as exc:
        duration = time.perf_counter() - start_time
        HTTP_REQUESTS_TOTAL.labels(method=method, endpoint=path, status_code="500").inc()
        HTTP_REQUEST_DURATION_SECONDS.labels(method=method, endpoint=path).observe(duration)
        logger.exception(f"Unhandled exception during request processing: {str(exc)}")
        res = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "InternalServerError",
                "message": "An unexpected server error occurred.",
                "status_code": 500,
                "correlation_id": correlation_id
            }
        )
        res.headers["X-Correlation-ID"] = correlation_id
        return res


# Global Exception Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    cid = correlation_id_ctx.get()
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPException",
            "message": str(exc.detail),
            "detail": str(exc.detail),
            "status_code": exc.status_code,
            "correlation_id": cid
        },
        headers={"X-Correlation-ID": cid}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    cid = correlation_id_ctx.get()
    errors = [{"loc": [str(x) for x in err["loc"]], "msg": err["msg"], "type": err["type"]} for err in exc.errors()]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Invalid request parameters or payload",
            "status_code": 422,
            "correlation_id": cid,
            "details": errors
        },
        headers={"X-Correlation-ID": cid}
    )


# Mount Endpoints
app.include_router(health.router)
app.include_router(items.router)

# Controlled Fault Injection router (Mounted only when enabled or for testing)
if settings.ENABLE_FAULT_INJECTION:
    app.include_router(fault_injection.router)


@app.get("/metrics", tags=["Observability"], summary="Prometheus Metrics")
def metrics_endpoint():
    """Prometheus scrape target."""
    return get_metrics_response()


@app.get("/", tags=["General"])
def root_info():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs",
        "metrics": "/metrics",
        "health": "/health/ready"
    }
