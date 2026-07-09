from __future__ import annotations

from typing import Any


def build_admin_requirements_data(admin_user_id: int) -> dict[str, Any]:
    return {
        "editableDomains": [
            "characters",
            "skills",
            "items",
            "bosses",
            "drop_tables",
            "field_zones",
            "enhancement_rules",
            "mailbox_rewards",
            "events",
            "users",
        ],
        "requiresChangeLog": True,
        "requiresRollback": True,
        "readOnlyOverviewReady": True,
        "adminUserId": admin_user_id,
    }


def build_admin_overview_data(overview: dict[str, Any], admin_user_id: int) -> dict[str, Any]:
    return {
        "status": overview["status"],
        "readOnly": overview["readOnly"],
        "adminUserId": admin_user_id,
        "readiness": overview.get("readiness"),
    }


def build_master_domains_data(domains: dict[str, Any], admin_user_id: int) -> dict[str, Any]:
    return {
        "status": domains["status"],
        "readOnly": domains["readOnly"],
        "adminUserId": admin_user_id,
        "count": domains["count"],
        "defaultDomain": domains["defaultDomain"],
    }


def build_master_catalog_data(catalog: dict[str, Any], admin_user_id: int) -> dict[str, Any]:
    return {
        "status": catalog["status"],
        "readOnly": catalog["readOnly"],
        "adminUserId": admin_user_id,
        "domain": catalog["domain"],
        "count": catalog["count"],
        "total": catalog["total"],
        "page": catalog["page"],
        "totalPages": catalog["totalPages"],
        "filters": catalog["filters"],
        "rawJsonReturned": catalog["rawJsonReturned"],
        "assetsReturned": catalog["assetsReturned"],
    }


def build_master_create_blueprint_data(blueprint: dict[str, Any], admin_user_id: int) -> dict[str, Any]:
    return {
        "status": blueprint["status"],
        "readOnly": blueprint["readOnly"],
        "createApplyReady": blueprint["createApplyReady"],
        "createApplyUnlocked": blueprint.get("createApplyUnlocked", False),
        "insertLocked": blueprint.get("insertLocked", True),
        "confirmTextRequired": blueprint.get("confirmTextRequired"),
        "adminUserId": admin_user_id,
        "domain": blueprint["domain"],
        "fieldCount": blueprint.get("fieldCount", 0),
        "requiredFields": blueprint.get("requiredFields", []),
        "relationOptionsReturned": blueprint.get("relationOptionsReturned", False),
        "rawJsonReturned": blueprint.get("rawJsonReturned", False),
        "assetsReturned": blueprint.get("assetsReturned", False),
    }


def build_master_create_preview_data(preview: dict[str, Any], admin_user_id: int) -> dict[str, Any]:
    return {
        "status": preview["status"],
        "readOnly": preview["readOnly"],
        "dryRun": preview["dryRun"],
        "writeBlocked": preview["writeBlocked"],
        "adminUserId": admin_user_id,
        "domain": preview["domain"],
        "fieldCount": preview.get("fieldCount", 0),
        "errorCount": preview.get("errorCount", 0),
        "wouldBeValid": preview.get("wouldBeValid", False),
        "createApplyReady": preview.get("createApplyReady", False),
        "createApplyUnlocked": preview.get("createApplyUnlocked", False),
        "insertLocked": preview.get("insertLocked", True),
        "confirmTextRequired": preview.get("confirmTextRequired"),
    }


def build_master_create_apply_data(created: dict[str, Any], admin_user_id: int) -> dict[str, Any]:
    return {
        "status": created["status"],
        "readOnly": created.get("readOnly"),
        "dryRun": created.get("dryRun"),
        "writeBlocked": created.get("writeBlocked"),
        "created": created.get("created", False),
        "adminUserId": admin_user_id,
        "domain": created.get("domain"),
        "id": created.get("id"),
        "code": created.get("code"),
        "fieldCount": created.get("fieldCount", 0),
        "errorCount": created.get("errorCount", 0),
        "changeLogId": created.get("changeLogId"),
    }


def build_master_detail_data(detail: dict[str, Any], admin_user_id: int) -> dict[str, Any]:
    return {
        "status": detail["status"],
        "readOnly": detail["readOnly"],
        "adminUserId": admin_user_id,
        "domain": detail["domain"],
        "id": detail["id"],
        "rawJsonReturned": detail["rawJsonReturned"],
        "sanitizedJsonReturned": detail["sanitizedJsonReturned"],
        "assetsReturned": detail["assetsReturned"],
        "safeForAdminWriteUi": detail["safeForAdminWriteUi"],
    }


def build_master_relations_data(relations: dict[str, Any], admin_user_id: int) -> dict[str, Any]:
    return {
        "status": relations["status"],
        "readOnly": relations["readOnly"],
        "adminUserId": admin_user_id,
        "domain": relations["domain"],
        "id": relations["id"],
        "groupCount": relations["groupCount"],
        "totalRelatedRows": relations["totalRelatedRows"],
        "rawJsonReturned": relations["rawJsonReturned"],
        "assetsReturned": relations["assetsReturned"],
        "safeForAdminWriteUi": relations["safeForAdminWriteUi"],
    }


def build_master_edit_preview_data(preview: dict[str, Any], admin_user_id: int) -> dict[str, Any]:
    return {
        "status": preview["status"],
        "readOnly": preview["readOnly"],
        "dryRun": preview["dryRun"],
        "adminUserId": admin_user_id,
        "domain": preview["domain"],
        "id": preview["id"],
        "diffCount": preview["diffCount"],
        "errorCount": preview["errorCount"],
        "wouldBeValid": preview["wouldBeValid"],
    }


def build_master_edit_apply_data(applied: dict[str, Any], admin_user_id: int) -> dict[str, Any]:
    return {
        "status": applied["status"],
        "readOnly": applied.get("readOnly"),
        "dryRun": applied.get("dryRun"),
        "writeBlocked": applied.get("writeBlocked"),
        "applied": applied.get("applied", False),
        "adminUserId": admin_user_id,
        "domain": applied.get("domain"),
        "id": applied.get("id"),
        "diffCount": applied.get("diffCount", 0),
        "errorCount": applied.get("errorCount", 0),
        "changeLogId": applied.get("changeLogId"),
    }


def build_change_logs_data(logs: dict[str, Any], admin_user_id: int) -> dict[str, Any]:
    return {
        "status": logs["status"],
        "readOnly": logs["readOnly"],
        "adminUserId": admin_user_id,
        "count": logs["count"],
        "total": logs["total"],
        "limit": logs["limit"],
        "filters": logs["filters"],
        "warnings": logs.get("warnings", []),
    }


def build_change_log_detail_data(detail: dict[str, Any], admin_user_id: int) -> dict[str, Any]:
    return {
        "status": detail["status"],
        "readOnly": detail["readOnly"],
        "adminUserId": admin_user_id,
        "id": detail.get("id"),
        "changedKeyCount": detail.get("changedKeyCount", 0),
        "rollbackAvailable": (detail.get("rollback") or {}).get("available", False),
        "createDeleteAvailable": (detail.get("createDelete") or {}).get("available", False),
        "createDeleteRestoreAvailable": (detail.get("createDeleteRestore") or {}).get("available", False),
    }


def build_create_delete_preview_data(preview: dict[str, Any], admin_user_id: int) -> dict[str, Any]:
    return {
        "status": preview["status"],
        "readOnly": preview.get("readOnly"),
        "dryRun": preview.get("dryRun"),
        "writeBlocked": preview.get("writeBlocked"),
        "adminUserId": admin_user_id,
        "changeLogId": preview.get("changeLogId"),
        "createDeleteReady": preview.get("createDeleteReady", False),
        "wouldDelete": preview.get("wouldDelete", False),
        "dependencyBlockerCount": preview.get("dependencyBlockerCount", 0),
        "currentMatchesCreateValues": preview.get("currentMatchesCreateValues", False),
        "diffCount": preview.get("diffCount", 0),
    }


def build_create_delete_apply_data(result: dict[str, Any], admin_user_id: int) -> dict[str, Any]:
    return {
        "status": result["status"],
        "readOnly": result.get("readOnly"),
        "dryRun": result.get("dryRun"),
        "writeBlocked": result.get("writeBlocked"),
        "deleted": result.get("deleted", False),
        "adminUserId": admin_user_id,
        "changeLogId": result.get("changeLogId"),
        "deleteChangeLogId": result.get("deleteChangeLogId"),
        "dependencyBlockerCount": result.get("dependencyBlockerCount", 0),
        "diffCount": result.get("diffCount", 0),
    }


def build_create_delete_restore_preview_data(preview: dict[str, Any], admin_user_id: int) -> dict[str, Any]:
    return {
        "status": preview["status"],
        "readOnly": preview.get("readOnly"),
        "dryRun": preview.get("dryRun"),
        "writeBlocked": preview.get("writeBlocked"),
        "adminUserId": admin_user_id,
        "changeLogId": preview.get("changeLogId"),
        "createDeleteRestoreReady": preview.get("createDeleteRestoreReady", False),
        "wouldRestore": preview.get("wouldRestore", False),
        "targetRowMissing": preview.get("targetRowMissing", False),
        "idConflict": preview.get("idConflict", False),
        "codeConflict": preview.get("codeConflict", False),
        "validationErrorCount": preview.get("validationErrorCount", 0),
        "diffCount": preview.get("diffCount", 0),
    }


def build_create_delete_restore_apply_data(result: dict[str, Any], admin_user_id: int) -> dict[str, Any]:
    return {
        "status": result["status"],
        "readOnly": result.get("readOnly"),
        "dryRun": result.get("dryRun"),
        "writeBlocked": result.get("writeBlocked"),
        "restored": result.get("restored", False),
        "adminUserId": admin_user_id,
        "changeLogId": result.get("changeLogId"),
        "restoreChangeLogId": result.get("restoreChangeLogId"),
        "validationErrorCount": result.get("validationErrorCount", 0),
        "diffCount": result.get("diffCount", 0),
    }


def build_rollback_preview_data(preview: dict[str, Any], admin_user_id: int) -> dict[str, Any]:
    return {
        "status": preview["status"],
        "readOnly": preview.get("readOnly"),
        "dryRun": preview.get("dryRun"),
        "writeBlocked": preview.get("writeBlocked"),
        "adminUserId": admin_user_id,
        "changeLogId": preview.get("changeLogId"),
        "rollbackReady": preview.get("rollbackReady", False),
        "currentMatchesAfter": preview.get("currentMatchesAfter", False),
        "diffCount": preview.get("diffCount", 0),
        "errorCount": preview.get("errorCount", 0),
    }


def build_rollback_apply_data(result: dict[str, Any], admin_user_id: int) -> dict[str, Any]:
    return {
        "status": result["status"],
        "readOnly": result.get("readOnly"),
        "dryRun": result.get("dryRun"),
        "writeBlocked": result.get("writeBlocked"),
        "rolledBack": result.get("rolledBack", False),
        "adminUserId": admin_user_id,
        "changeLogId": result.get("changeLogId"),
        "rollbackChangeLogId": result.get("rollbackChangeLogId"),
        "diffCount": result.get("diffCount", 0),
    }


def build_save_snapshots_data(snapshots: dict[str, Any], admin_user_id: int) -> dict[str, Any]:
    return {
        "status": snapshots["status"],
        "readOnly": snapshots["readOnly"],
        "adminUserId": admin_user_id,
        "count": snapshots["count"],
        "total": snapshots["total"],
        "totalAll": snapshots["totalAll"],
        "limit": snapshots["limit"],
        "filters": snapshots["filters"],
    }


def build_change_preview_data(admin_user_id: int) -> dict[str, Any]:
    return {"status": "preview_only", "readOnly": True, "adminUserId": admin_user_id}
