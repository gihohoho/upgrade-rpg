from fastapi import APIRouter

from app.api.routes import admin, game, health

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(game.router, prefix="/game", tags=["game"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
