"""AI routes — TODO: Implement (stub returning mock data). See Section 14.2."""
from fastapi import APIRouter
router = APIRouter(prefix="/ai", tags=["AI Intelligence"])
# TODO: GET /ai/forecast/cashflow, GET /ai/forecast/budget-exhaustion/{project_id},
#       GET /ai/risk/{project_id}, GET /ai/anomalies, GET /ai/recommendations,
#       POST /ai/simulate
