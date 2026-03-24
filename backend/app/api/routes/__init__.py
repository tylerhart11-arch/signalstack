from fastapi import APIRouter

from app.api.routes.alerts import router as alerts_router
from app.api.routes.anomalies import router as anomalies_router
from app.api.routes.health import router as health_router
from app.api.routes.overview import router as overview_router
from app.api.routes.regime import router as regime_router
from app.api.routes.system import router as system_router
from app.api.routes.thesis import router as thesis_router


api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(overview_router, tags=["overview"])
api_router.include_router(regime_router, tags=["regime"])
api_router.include_router(anomalies_router, tags=["anomalies"])
api_router.include_router(thesis_router, tags=["thesis"])
api_router.include_router(system_router, tags=["system"])
api_router.include_router(alerts_router, tags=["alerts"])
