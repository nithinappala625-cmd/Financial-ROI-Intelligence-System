"""
Structured JSON logging configuration.

Uses structlog for structured logging with trace ID injection per request.
"""

import logging
import sys
import uuid

import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


def setup_logging() -> None:
    """Configure structlog for structured JSON logging."""

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer()
            if True  # Use JSON in production
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Also configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    # Silence SQLAlchemy SQL query logging
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


class TraceIDMiddleware(BaseHTTPMiddleware):
    """Middleware that injects a unique trace ID into every request context."""

    async def dispatch(self, request: Request, call_next):
        trace_id = str(uuid.uuid4())[:8]
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(trace_id=trace_id)

        response = await call_next(request)
        response.headers["X-Trace-ID"] = trace_id
        return response
