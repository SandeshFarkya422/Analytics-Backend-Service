from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import time
from app.api import mock_api, ingestion_api, analytics_api
from app.core.logging import logger

app = FastAPI(
    title="Analytics Backend Service",
    description="Large-scale data ingestion and analytics API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s")
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(mock_api.router)
app.include_router(ingestion_api.router)
app.include_router(analytics_api.router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
