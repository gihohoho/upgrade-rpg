from __future__ import annotations

from fastapi import Depends, Query

from app.core.security import get_current_user_placeholder, require_admin_write_dev_key
from app.db.session import get_db_session

# Dependency defaults kept in one place so admin route cleanup can reduce repeated
# FastAPI Depends(...) boilerplate without changing the public API contract.
ADMIN_CURRENT_USER_DEP = Depends(get_current_user_placeholder)
ADMIN_DB_SESSION_DEP = Depends(get_db_session)
ADMIN_WRITE_GUARD_DEP = Depends(require_admin_write_dev_key)

# Shared query parameter defaults. These are intentionally Query(...) objects, not
# plain constants, so OpenAPI validation, aliases, and bounds stay identical.
MASTER_DOMAIN_QUERY = Query(default="itemTemplates", max_length=80)
MASTER_ROW_ID_QUERY = Query(..., ge=1)
MASTER_CATALOG_LIMIT_QUERY = Query(default=20, ge=1, le=200)
MASTER_CATALOG_PAGE_QUERY = Query(default=1, ge=1, le=100000)
MASTER_CATALOG_SEARCH_QUERY = Query(default=None, max_length=120)
MASTER_CATALOG_ENABLED_QUERY = Query(default="all", max_length=20)
MASTER_CATALOG_SORT_QUERY = Query(default="id_asc", max_length=30)
MASTER_RELATIONS_LIMIT_QUERY = Query(default=20, ge=1, le=80)

CHANGE_LOG_LIMIT_QUERY = Query(default=20, ge=1, le=100)
CHANGE_LOG_TARGET_TYPE_QUERY = Query(default=None, alias="targetType", max_length=120)
CHANGE_LOG_TARGET_ID_QUERY = Query(default=None, alias="targetId", max_length=160)
CHANGE_LOG_ACTION_QUERY = Query(default=None, max_length=80)
CHANGE_LOG_CHANGED_KEY_QUERY = Query(default=None, alias="changedKey", max_length=120)
CHANGE_LOG_APPLIED_QUERY = Query(default=None)
CHANGE_LOG_SORT_QUERY = Query(default="created_desc", max_length=40)

SAVE_SNAPSHOT_LIMIT_QUERY = Query(default=20, ge=1, le=100)
SAVE_SNAPSHOT_USER_ID_QUERY = Query(default=None, alias="userId", ge=1)
SAVE_SNAPSHOT_SLOT_KEY_QUERY = Query(default=None, alias="slotKey", max_length=80)
SAVE_SNAPSHOT_SOURCE_QUERY = Query(default=None, max_length=80)
SAVE_SNAPSHOT_DEFAULT_ONLY_QUERY = Query(default=False, alias="defaultOnly")
SAVE_SNAPSHOT_SORT_QUERY = Query(default="updated_desc", max_length=30)
