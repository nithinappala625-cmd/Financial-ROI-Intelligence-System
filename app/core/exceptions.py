"""
Custom application exceptions and global exception handlers.

Exceptions: NotFoundError, UnauthorizedError, ForbiddenError, BudgetExceededError.
Handlers are registered in main.py via register_exception_handlers().
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


# ── Custom Exceptions ─────────────────────────────────────────────────────


class NotFoundError(Exception):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource: str = "Resource", identifier: str = ""):
        self.resource = resource
        self.identifier = identifier
        super().__init__(f"{resource} not found: {identifier}")


class UnauthorizedError(Exception):
    """Raised when authentication is required but missing or invalid."""

    def __init__(self, detail: str = "Authentication required"):
        self.detail = detail
        super().__init__(detail)


class ForbiddenError(Exception):
    """Raised when the user lacks permission for the requested action."""

    def __init__(self, detail: str = "Insufficient permissions"):
        self.detail = detail
        super().__init__(detail)


class BudgetExceededError(Exception):
    """Raised when an operation would exceed a project budget."""

    def __init__(self, project_id: str = "", amount: float = 0.0):
        self.project_id = project_id
        self.amount = amount
        super().__init__(
            f"Budget exceeded for project {project_id} by {amount}"
        )


# ── Global Exception Handlers ────────────────────────────────────────────


def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the FastAPI app."""

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)},
        )

    @app.exception_handler(UnauthorizedError)
    async def unauthorized_handler(request: Request, exc: UnauthorizedError):
        return JSONResponse(
            status_code=401,
            content={"detail": exc.detail},
        )

    @app.exception_handler(ForbiddenError)
    async def forbidden_handler(request: Request, exc: ForbiddenError):
        return JSONResponse(
            status_code=403,
            content={"detail": exc.detail},
        )

    @app.exception_handler(BudgetExceededError)
    async def budget_exceeded_handler(
        request: Request, exc: BudgetExceededError
    ):
        return JSONResponse(
            status_code=422,
            content={"detail": str(exc)},
        )
