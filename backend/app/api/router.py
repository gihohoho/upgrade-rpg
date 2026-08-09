from fastapi import APIRouter

from app.api.routes import account, account_admin, admin, auth, game, health

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(account.router, prefix="/account", tags=["account"])
api_router.include_router(account_admin.router, prefix="/account-admin", tags=["account-admin"])
api_router.include_router(game.router, prefix="/game", tags=["game"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
