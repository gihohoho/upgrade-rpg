from __future__ import annotations

from app.services.admin.admin_config import AdminConfigService
from app.services.admin.admin_readiness_service import AdminReadinessService
from app.services.admin.admin_overview_snapshots_service import AdminOverviewSnapshotsService
from app.services.admin.admin_master_catalog_service import AdminMasterCatalogService
from app.services.admin.admin_create_lifecycle_service import AdminCreateLifecycleService
from app.services.admin.admin_change_log_service import AdminChangeLogService
from app.services.admin.admin_edit_draft_service import AdminEditDraftService
from app.services.admin.admin_shared_utils import AdminSharedUtilsService

class AdminService(AdminConfigService, AdminSharedUtilsService, AdminReadinessService, AdminOverviewSnapshotsService, AdminMasterCatalogService, AdminEditDraftService, AdminChangeLogService, AdminCreateLifecycleService):
    """Stable route facade for split backend admin services.

    Admin routes keep importing this class while implementation details live in
    backend/app/services/admin/*.py modules.
    """

    pass
