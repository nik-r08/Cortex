from fastapi import APIRouter

from backend.api.documents import router as documents_router
from backend.api.health import router as health_router
from backend.api.search import router as search_router
from backend.api.stats import router as stats_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(documents_router)
api_router.include_router(search_router)
api_router.include_router(stats_router)
