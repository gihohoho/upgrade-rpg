from __future__ import annotations

from typing import Any


def build_admin_change_logs_unavailable_payload(
    *,
    limit: int | None,
    target_type: str | None,
    target_id: str | None,
    action: str | None,
    changed_key: str | None,
    applied: bool | None,
    sort: str | None,
    exc: Exception,
) -> dict[str, Any]:
    """Build the guarded fallback payload for local change-log route failures.

    The route keeps returning the same admin response envelope even when a local
    dev DB or service drift causes an unexpected exception before normal service
    fallback handling can run.
    """

    try:
        safe_limit = max(1, min(int(limit or 20), 100))
    except Exception:
        safe_limit = 20
    safe_sort = sort or "created_desc"
    warnings = ["admin_change_logs_route_exception_guarded"]
    return {
        "status": "unavailable",
        "readOnly": True,
        "count": 0,
        "total": 0,
        "limit": safe_limit,
        "filters": {
            "targetType": target_type,
            "targetId": target_id,
            "action": action,
            "changedKey": changed_key,
            "applied": applied,
            "sort": safe_sort,
            "warnings": warnings,
        },
        "rows": [],
        "rawBeforeAfterReturned": False,
        "warnings": warnings,
        "debug": {
            "errorClass": exc.__class__.__name__,
            "errorMessage": str(exc)[:500],
            "hint": "backend/app/services/admin/admin_change_log_service.py의 change-logs 조회 경로 또는 로컬 DB 스키마를 확인하세요.",
        },
    }
