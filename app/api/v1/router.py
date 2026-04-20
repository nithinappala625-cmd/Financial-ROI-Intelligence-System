"""
Master router — includes all sub-routers with prefix /api/v1.

Add new domain routers here as developers implement them.
"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router

# Import placeholder routers as they get implemented:
from app.api.v1.projects import router as projects_router
from app.api.v1.expenses import router as expenses_router
from app.api.v1.employees import router as employees_router
from app.api.v1.work_logs import router as work_logs_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.ai import router as ai_router
from app.api.v1.project_assignments import router as project_assignments_router
from app.api.v1.agentic_system import router as agentic_system_router
from app.api.v1.milestones import router as milestones_router

api_router = APIRouter()

# ── Core (implemented) ──────────────────────────────────────────────────
api_router.include_router(auth_router)

# ── Domain (placeholder routers — will be built by other developers) ────
api_router.include_router(projects_router)
api_router.include_router(expenses_router)
api_router.include_router(employees_router)
api_router.include_router(work_logs_router)
api_router.include_router(alerts_router)
api_router.include_router(ai_router)
api_router.include_router(project_assignments_router)
api_router.include_router(agentic_system_router)
api_router.include_router(milestones_router)
