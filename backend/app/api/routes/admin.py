from fastapi import APIRouter

from app.api.routes.admin_change_log_routes import router as admin_change_log_router
from app.api.routes.admin_master_data_routes import router as admin_master_data_router
from app.api.routes.admin_overview_snapshot_routes import router as admin_overview_snapshot_router

router = APIRouter()
router.include_router(admin_overview_snapshot_router)
router.include_router(admin_master_data_router)
router.include_router(admin_change_log_router)
