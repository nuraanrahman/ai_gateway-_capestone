from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.middleware.request_id import RequestIDMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("AI Gateway starting", extra={"extra": {"environment": settings.environment}})
    yield
    logger.info("AI Gateway shutting down")


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="One API key. Every LLM.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Middleware — add in reverse execution order (last added = outermost = runs first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIDMiddleware)


@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok", "version": settings.version, "environment": settings.environment}


@app.get("/", tags=["system"])
async def root():
    return {
        "name": settings.app_name,
        "version": settings.version,
        "docs": "/docs",
        "health": "/health",
    }
