from fastapi import FastAPI

from app.api.health import router as health_router
from app.core.config import settings

app = FastAPI(
    title = settings.app_name,
    version = settings.app_version,
    description="A learning-first Document Intelligence Platform using RAG, vector databases, FastAPI, Docker, and modern fronted tools." 
)

app.include_router(health_router)

@app.get("/")
def root():
    return {
        "message": "Welcome to Document Intelligence Platform",
        "docs": "/docs",
        "health": "/health"
    }