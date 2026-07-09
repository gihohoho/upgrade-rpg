from __future__ import annotations

from typing import Any


class AdminReadinessService:
    """Small admin readiness/preview helpers kept outside the facade."""

    async def preview_change(self, target_type: str, before: dict, after: dict) -> dict:
        return {
            "targetType": target_type,
            "before": before,
            "after": after,
            "warnings": [],
            "allowed": True,
            "readOnly": True,
            "note": "현재 단계에서는 관리자 변경 적용 없이 미리보기/검증 구조만 준비합니다.",
        }


    def _build_readiness(self, master_counts: dict[str, Any], save_snapshot_summary: dict[str, Any]) -> dict[str, Any]:
        warnings: list[str] = []
        if int(master_counts.get("itemTemplates", {}).get("total") or 0) <= 0:
            warnings.append("master_item_templates_empty")
        if int(master_counts.get("skills", {}).get("total") or 0) <= 0:
            warnings.append("master_skills_empty")
        if int(save_snapshot_summary.get("totalSlots") or 0) <= 0:
            warnings.append("save_snapshots_empty")
        return {
            "ok": len(warnings) == 0,
            "warnings": warnings,
            "safeForAdminReadOnlyUi": True,
            "safeForAdminWriteUi": False,
            "guardedMasterEditApplyReady": True,
            "guardedRollbackReady": True,
            "writeUiBlockedReason": "일반 지급/삭제/관계 변경은 계속 막혀 있습니다. 단, allow-list 마스터 데이터 필드는 확인 문구와 변경 이력을 거쳐 guarded apply/rollback이 가능합니다.",
        }


