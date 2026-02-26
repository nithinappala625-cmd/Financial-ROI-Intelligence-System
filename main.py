"""
AI Financial Management & ROI Intelligence Platform — Backend Entry Point.

Creates the FastAPI app, registers all routers, adds middleware,
and configures startup/shutdown lifecycle events.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.events import lifespan
from app.core.exceptions import register_exception_handlers
from app.core.logging import TraceIDMiddleware, setup_logging
from config import settings

# ── Setup logging ─────────────────────────────────────────────────────────
setup_logging()

# ── Create app ────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description=(
        "Enterprise AI-powered financial management platform combining "
        "project accounting, employee productivity analytics, and "
        "deep-learning-powered forecasting."
    ),
    lifespan=lifespan,
)

# ── Middleware ─────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TraceIDMiddleware)

# ── Register exception handlers ───────────────────────────────────────────
register_exception_handlers(app)

# ── Include routers ───────────────────────────────────────────────────────
app.include_router(api_router)


# ── Health check ──────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }
