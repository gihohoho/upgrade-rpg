from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.admin.admin_diff_engine import build_admin_diff
from app.services.admin.admin_rollback_snapshot import build_rollback_snapshot, verify_rollback_snapshot


def _change_maps(items: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    before: dict[str, Any] = {}
    after: dict[str, Any] = {}
    for item in items if isinstance(items, list) else []:
        if not isinstance(item, dict):
            continue
        key = str(item.get("key") or "").strip()
        if not key:
            continue
        if "before" in item:
            before[key] = deepcopy(item.get("before"))
        if "after" in item:
            after[key] = deepcopy(item.get("after"))
    return before, after


def enrich_admin_preview(preview: dict[str, Any], *, mode: str, target_id: int | str | None = None) -> dict[str, Any]:
    """Add optional unifiedDiff/rollbackSnapshot fields without changing legacy preview fields."""
    result = deepcopy(preview)
    domain = str(result.get("domain") or "unknown")
    resolved_id = target_id if target_id is not None else result.get("id") or result.get("changeLogId") or "preview"

    if mode == "create":
        before: Any = {}
        after: Any = deepcopy(result.get("normalizedDraft") or {})
    else:
        accepted_source = result.get("acceptedChanges") or result.get("acceptedFields") or []
        legacy_source = result.get("changes") or []
        if mode == "rollback" and not accepted_source:
            # Legacy ChangeLog rows describe original before -> applied after.
            # Rollback Preview must describe current/applied after -> rollback before.
            original_before, original_after = _change_maps(legacy_source)
            before, after = original_after, original_before
        else:
            before, after = _change_maps(accepted_source or legacy_source)
        if mode == "delete":
            before = after or before
            after = {}
        elif mode == "restore":
            restored = after or before
            before = {}
            after = restored

    unified_diff = build_admin_diff(before, after)
    snapshot = build_rollback_snapshot(domain=domain, target_id=resolved_id, before=before, after=after)
    if not verify_rollback_snapshot(snapshot):
        raise RuntimeError("rollback snapshot fingerprint verification failed")
    result["unifiedDiff"] = unified_diff
    result["unifiedDiffCount"] = len(unified_diff)
    result["rollbackSnapshot"] = snapshot
    result["previewSchemaVersion"] = 1
    return result
