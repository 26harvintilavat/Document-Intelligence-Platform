from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": settings.app_slug,
        "version": settings.app_version,
        "environment": settings.environment,
    }