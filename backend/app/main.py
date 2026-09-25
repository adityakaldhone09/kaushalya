from __future__ import annotations
import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_settings
from app.database.connection import connect_db, close_db, get_db
from app.database.indexes import create_indexes
from app.routes import api_router
from app.routes.ai_routes import router as gemini_ai_router   # NEW — gemini AI routes

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)
settings = get_settings()


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s API server (%s)", settings.APP_NAME, settings.ENVIRONMENT)
    try:
        await connect_db()
        db = get_db()
        await create_indexes(db)
        logger.info("%s is ready", settings.APP_NAME)
    except Exception as exc:
        logger.error("Startup warning — MongoDB not available: %s", exc)
        logger.warning(
            "Server will start but DB-dependent endpoints will fail until MongoDB is available"
        )
    yield
    logger.info("Shutting down %s", settings.APP_NAME)
    await close_db()


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="KAUSHALYA API",
    description="AI-powered Skill & Employment Intelligence Platform — SIH26135",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global exception handler ──────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception on %s %s: %s",
        request.method, request.url.path, exc, exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": {
            "code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
        }},
    )


# ── Routes ────────────────────────────────────────────────────────────────────
# Gemini AI routes at /api/ai/*
app.include_router(gemini_ai_router, prefix="/api")

# All other routes (auth, trainees, jobs, training, intelligence…)
app.include_router(api_router, prefix="/api")


@app.get("/", include_in_schema=False)
async def root():
    return {
        "service": "KAUSHALYA API v2",
        "docs": "/docs",
        "health": "/api/healthz",
        "ai_health": "/api/ai/health",
    }
