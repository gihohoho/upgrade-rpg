from __future__ import annotations

from typing import Any

from sqlalchemy import inspect as sa_inspect, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    AdminChangeLog,
    Boss,
    Character,
    CharacterSkill,
    DropTable,
    DropTableItem,
    EnhancementGroup,
    EnhancementLevel,
    FieldZone,
    ItemInstance,
    ItemTemplate,
    Skill,
    SkillLevel,
    UserCharacterSkill,
    UserEquipmentSlot,
    UserProfile,
)
from app.services.game_service import serialize_value


class AdminCreateLifecycleService:
    """Create/delete/restore lifecycle helpers for admin master-data rows.

    Split from AdminService in v201 while AdminService remains the facade used by routes.
    """

    def _master_create_lifecycle_dependency_guards(self, domain: str) -> list[dict[str, Any]]:
        guard_map: dict[str, list[dict[str, Any]]] = {
            "characters": [
                {"label": "캐릭터 스킬 연결", "target": "character_skills.character_code", "blocksDelete": True, "note": "기본 스킬 연결이 있으면 캐릭터 삭제를 막습니다."},
                {"label": "유저 캐릭터 스킬", "target": "user_character_skills.character_code", "blocksDelete": True, "note": "유저 진행 데이터에서 사용 중이면 삭제를 막습니다."},
                {"label": "유저 장비 슬롯", "target": "user_equipment_slots.character_code", "blocksDelete": True, "note": "장비 슬롯 데이터에서 사용 중이면 삭제를 막습니다."},
                {"label": "유저 현재 캐릭터", "target": "user_profiles.current_character_id", "blocksDelete": True, "note": "현재 선택 캐릭터로 사용 중이면 삭제를 막습니다."},
            ],
            "enhancementGroups": [
                {"label": "강화 단계", "target": "enhancement_levels.group_code", "blocksDelete": True, "note": "강화 단계가 있으면 그룹 삭제를 막습니다."},
                {"label": "아이템 강화 그룹", "target": "item_templates.enhance_group_code", "blocksDelete": True, "note": "아이템 템플릿에서 사용 중이면 삭제를 막습니다."},
            ],
            "fieldZones": [
                {"label": "필드 드랍 테이블", "target": "drop_tables.owner_type=field + owner_code", "blocksDelete": True, "note": "필드에 연결된 드랍 테이블이 있으면 삭제를 막습니다."},
            ],
            "bosses": [
                {"label": "보스 드랍 테이블", "target": "drop_tables.owner_type=boss + owner_code", "blocksDelete": True, "note": "보스에 연결된 드랍 테이블이 있으면 삭제를 막습니다."},
            ],
            "skills": [
                {"label": "스킬 레벨", "target": "skill_levels.skill_code", "blocksDelete": True, "note": "스킬 레벨이 있으면 삭제를 막습니다."},
                {"label": "캐릭터 스킬 연결", "target": "character_skills.skill_code", "blocksDelete": True, "note": "캐릭터 기본 스킬로 쓰이면 삭제를 막습니다."},
                {"label": "유저 캐릭터 스킬", "target": "user_character_skills.skill_code", "blocksDelete": True, "note": "유저 진행 데이터에서 사용 중이면 삭제를 막습니다."},
            ],
            "dropTables": [
                {"label": "드랍 아이템", "target": "drop_table_items.drop_table_code", "blocksDelete": True, "note": "드랍 아이템 row가 있으면 드랍 테이블 삭제를 막습니다."},
            ],
            "itemTemplates": [
                {"label": "드랍 아이템", "target": "drop_table_items.item_template_code", "blocksDelete": True, "note": "드랍 테이블에서 사용 중이면 아이템 템플릿 삭제를 막습니다."},
                {"label": "유저 아이템 인스턴스", "target": "item_instances.template_code", "blocksDelete": True, "note": "유저 인벤토리/창고에 생성된 아이템이면 삭제를 막습니다."},
            ],
            "dropTableItems": [
                {"label": "id 기반 leaf row", "target": "drop_table_items.id", "blocksDelete": False, "note": "하위 연결이 없는 row라 현재값 일치 검사 후 id 기준으로 삭제합니다."},
            ],
            "skillLevels": [
                {"label": "id 기반 leaf row", "target": "skill_levels.id", "blocksDelete": False, "note": "스킬을 참조하는 레벨 row라 현재값 일치 검사 후 id 기준으로 삭제합니다."},
            ],
            "enhancementLevels": [
                {"label": "id 기반 leaf row", "target": "enhancement_levels.id", "blocksDelete": False, "note": "강화 그룹을 참조하는 단계 row라 현재값 일치 검사 후 id 기준으로 삭제합니다."},
            ],
            "characterSkills": [
                {"label": "id 기반 leaf row", "target": "character_skills.id", "blocksDelete": False, "note": "캐릭터와 스킬을 연결하는 row라 현재값 일치 검사 후 id 기준으로 삭제합니다."},
            ],
        }
        return guard_map.get(domain, [])

    def _master_create_lifecycle_payload(self, domain: str) -> dict[str, Any]:
        create_unlocked = domain in self.MASTER_CREATE_APPLY_ALLOWED_DOMAINS
        delete_unlocked = domain in self.MASTER_CREATE_DELETE_ALLOWED_DOMAINS
        field_defs = self.MASTER_CREATE_BLUEPRINT_FIELDS.get(domain) or []
        has_code_field = any(str(field.get("key") or "") == "code" for field in field_defs)
        locked_fields = [str(field.get("key")) for field in field_defs if str(field.get("inputKind") or "") == "json-readonly" or str(field.get("key") or "").endswith("_json") or self._is_asset_field(str(field.get("key") or ""))]
        combo_guards: list[list[str]] = []
        for field in field_defs:
            combo_guard = field.get("comboGuard") if isinstance(field.get("comboGuard"), list) else None
            if combo_guard and combo_guard not in combo_guards:
                combo_guards.append(combo_guard)
        dependency_guards = self._master_create_lifecycle_dependency_guards(domain)
        dependency_blocker_count = sum(1 for guard in dependency_guards if guard.get("blocksDelete"))
        return {
            "createApplyUnlocked": create_unlocked,
            "createDeleteUnlocked": delete_unlocked,
            "createDeleteRestoreUnlocked": delete_unlocked,
            "identityMode": "code+id" if has_code_field else "id",
            "deleteRestoreKey": "code/id" if has_code_field else "id",
            "confirmTexts": {
                "create": self.MASTER_CREATE_APPLY_CONFIRM_TEXT,
                "deleteCreatedRow": self.MASTER_CREATE_DELETE_CONFIRM_TEXT,
                "restoreDeletedCreatedRow": self.MASTER_CREATE_DELETE_RESTORE_CONFIRM_TEXT,
            },
            "comboGuards": combo_guards,
            "lockedFieldCount": len(locked_fields),
            "lockedFields": locked_fields[:30],
            "jsonAssetLocked": bool(locked_fields),
            "deleteDependencyGuards": dependency_guards,
            "deleteDependencyGuardCount": len(dependency_guards),
            "deleteDependencyBlockerGuardCount": dependency_blocker_count,
            "deleteGuardMode": "dependency-blocking" if dependency_blocker_count else "leaf-id-current-match",
            "manualCheckRequired": True,
            "browserCheckOrder": [
                "생성 설계 불러오기",
                "relation 후보/검색 확인",
                "생성 초안 검증",
                "실제 생성 적용",
                "change log에서 create 이력 열기",
                "생성 row 삭제 미리보기/apply",
                "change log에서 create_delete 이력 열기",
                "삭제 row 복원 미리보기/apply",
            ],
        }

    async def preview_admin_create_delete_rollback(
        self,
        session: AsyncSession,
        *,
        change_log_id: int,
        reason: str | None = None,
    ) -> dict[str, Any]:
        """Preview safe deletion rollback for a row created through create-apply.

        This is intentionally narrower than update rollback. It only supports the
        limited create allow-list, blocks rows that changed after creation, and
        blocks rows with dependent data so no cascade/delete surprise can happen.
        """
        row = await self._get_admin_change_log(session, change_log_id)
        if row is None:
            return self._empty_create_delete_preview(status="not_found", change_log_id=change_log_id, warnings=["change_log_not_found"])

        domain, row_id = self._extract_master_change_target(row)
        after_json = serialize_value(row.after_json) or {}
        rollback_json = serialize_value(row.rollback_json) or {}
        if not row.applied or row.action != "create" or not domain or not row_id or not isinstance(after_json, dict):
            return self._empty_create_delete_preview(
                status="create_delete_not_available",
                change_log_id=change_log_id,
                warnings=["change_log_is_not_guarded_master_create"],
                target_type=row.target_type,
                target_id=row.target_id,
                domain=domain,
                row_id=row_id,
            )
        if domain not in self.MASTER_CREATE_DELETE_ALLOWED_DOMAINS:
            return self._empty_create_delete_preview(
                status="create_delete_domain_locked",
                change_log_id=change_log_id,
                warnings=["create_delete_domain_locked"],
                target_type=row.target_type,
                target_id=row.target_id,
                domain=domain,
                row_id=row_id,
            )
        if not isinstance(rollback_json, dict) or rollback_json.get("domain") != domain or int(rollback_json.get("id") or 0) != int(row_id) or rollback_json.get("delete") is not True:
            return self._empty_create_delete_preview(
                status="create_delete_metadata_invalid",
                change_log_id=change_log_id,
                warnings=["create_delete_rollback_json_invalid"],
                target_type=row.target_type,
                target_id=row.target_id,
                domain=domain,
                row_id=row_id,
            )

        master_row = await self._get_master_row(session, domain, int(row_id))
        if master_row is None:
            return self._empty_create_delete_preview(
                status="target_already_deleted",
                change_log_id=change_log_id,
                warnings=["target_row_not_found"],
                target_type=row.target_type,
                target_id=row.target_id,
                domain=domain,
                row_id=int(row_id),
            )

        keys = sorted(after_json.keys())
        current_values = self._current_master_values(master_row, keys)
        current_mismatches: list[dict[str, Any]] = []
        for key in keys:
            current = current_values.get(key)
            expected_after = serialize_value(after_json.get(key))
            if current != expected_after:
                current_mismatches.append({
                    "key": key,
                    "label": self._humanize_field_name(key),
                    "current": current,
                    "expectedAfter": expected_after,
                    "deleteEffect": "blocked_current_changed",
                })

        created_code = getattr(master_row, "code", None)
        dependency_checks = await self._build_create_delete_dependency_checks(session, domain, created_code, int(row_id))
        blocker_guard_count = sum(1 for check in dependency_checks if check.get("blocksDelete"))
        blocker_count = sum(int(check.get("count") or 0) for check in dependency_checks if check.get("blocksDelete"))
        changes = await self._build_change_log_changes_with_relations(session, domain, {}, after_json)
        create_delete_ready = len(current_mismatches) == 0 and blocker_count == 0
        return {
            "status": "create_delete_preview_ready" if create_delete_ready else "create_delete_blocked",
            "readOnly": False,
            "dryRun": True,
            "writeBlocked": True,
            "createDeleteReady": create_delete_ready,
            "wouldDelete": create_delete_ready,
            "confirmTextRequired": self.MASTER_CREATE_DELETE_CONFIRM_TEXT,
            "changeLogId": int(change_log_id),
            "targetType": row.target_type,
            "targetId": row.target_id,
            "domain": domain,
            "id": int(row_id),
            "code": serialize_value(created_code),
            "action": row.action,
            "reason": str(reason or "")[:300] if reason else None,
            "sourceChangeReason": row.reason,
            "changes": changes,
            "changedKeys": [change["key"] for change in changes],
            "diffCount": len(changes),
            "relationChangedKeys": [change["key"] for change in changes if change.get("relation")],
            "relationChangeCount": sum(1 for change in changes if change.get("relation")),
            "currentMatchesCreateValues": len(current_mismatches) == 0,
            "currentMismatches": current_mismatches[:30],
            "currentMismatchCount": len(current_mismatches),
            "dependencyChecks": dependency_checks,
            "dependencyCheckCount": len(dependency_checks),
            "dependencyBlockerGuardCount": blocker_guard_count,
            "dependencyBlockerCount": blocker_count,
            "rawBeforeAfterReturned": False,
            "warnings": [] if create_delete_ready else ["create_delete_has_blockers"],
            "note": "생성 row 삭제 되돌리기 미리보기입니다. 현재값이 생성 당시 값과 같고 연결 데이터가 없을 때만 삭제 적용할 수 있습니다.",
        }

    async def apply_admin_create_delete_rollback(
        self,
        session: AsyncSession,
        *,
        change_log_id: int,
        confirm_text: str,
        reason: str | None,
        admin_user_id: int,
    ) -> dict[str, Any]:
        """Delete a created row only when the create-delete preview is safe."""
        preview = await self.preview_admin_create_delete_rollback(session, change_log_id=change_log_id, reason=reason)
        if str(confirm_text or "").strip() != self.MASTER_CREATE_DELETE_CONFIRM_TEXT:
            preview.update({
                "status": "create_delete_confirmation_required",
                "dryRun": False,
                "writeBlocked": True,
                "deleted": False,
                "createDeleteReady": False,
                "wouldDelete": False,
                "warnings": [*(preview.get("warnings") or []), "create_delete_confirm_text_mismatch"],
                "note": "정확한 생성 row 삭제 확인 문구를 입력해야 DB에서 삭제할 수 있습니다.",
            })
            return preview
        if not preview.get("createDeleteReady"):
            preview.update({
                "status": "create_delete_rejected",
                "dryRun": False,
                "writeBlocked": True,
                "deleted": False,
                "createDeleteReady": False,
                "wouldDelete": False,
                "warnings": [*(preview.get("warnings") or []), "create_delete_preview_not_safe_to_apply"],
            })
            return preview

        domain = str(preview.get("domain") or "")
        row_id = int(preview.get("id") or 0)
        master_row = await self._get_master_row(session, domain, row_id)
        if master_row is None:
            preview.update({"status": "target_already_deleted", "deleted": False, "writeBlocked": True})
            return preview

        before_values = {key: serialize_value(getattr(master_row, key, None)) for key in (preview.get("changedKeys") or [])}
        delete_log = AdminChangeLog(
            admin_user_id=int(admin_user_id),
            target_type=f"master_data.{domain}",
            target_id=str(row_id),
            action="create_delete",
            reason=(str(reason or "")[:500] or f"Delete created row from change log #{change_log_id}"),
            before_json=before_values,
            after_json={},
            rollback_json={"domain": domain, "id": row_id, "restoreLocked": True, "sourceChangeLogId": int(change_log_id)},
            applied=True,
        )
        await session.delete(master_row)
        session.add(delete_log)
        await session.commit()
        await session.refresh(delete_log)

        preview.update({
            "status": "created_row_deleted",
            "dryRun": False,
            "writeBlocked": False,
            "deleted": True,
            "createDeleteReady": False,
            "wouldDelete": False,
            "deleteChangeLogId": int(delete_log.id),
            "appliedByAdminUserId": int(admin_user_id),
            "warnings": [*(preview.get("warnings") or []), "create_delete_restore_preview_enabled", "game_runtime_requires_reload"],
            "note": "create 이력으로 생성한 master-data row를 안전 검사 후 삭제했고 create_delete 이력을 저장했습니다. 삭제 복원은 별도 preview/apply 안전 검사를 통과해야 가능합니다.",
        })
        return preview

    async def preview_admin_create_delete_restore(
        self,
        session: AsyncSession,
        *,
        change_log_id: int,
        reason: str | None = None,
    ) -> dict[str, Any]:
        """Preview restoring a row that was removed by create-delete apply.

        Restore is intentionally limited to create_delete logs produced by this admin
        flow. It only restores the exact deleted id when the row is still missing and
        the original code has not been reused.
        """
        row = await self._get_admin_change_log(session, change_log_id)
        if row is None:
            return self._empty_create_delete_restore_preview(status="not_found", change_log_id=change_log_id, warnings=["change_log_not_found"])

        domain, row_id = self._extract_master_change_target(row)
        before_json = serialize_value(row.before_json) or {}
        rollback_json = serialize_value(row.rollback_json) or {}
        if not row.applied or row.action != "create_delete" or not domain or not row_id or not isinstance(before_json, dict):
            return self._empty_create_delete_restore_preview(
                status="create_delete_restore_not_available",
                change_log_id=change_log_id,
                warnings=["change_log_is_not_guarded_create_delete"],
                target_type=row.target_type,
                target_id=row.target_id,
                domain=domain,
                row_id=row_id,
            )
        if domain not in self.MASTER_CREATE_DELETE_ALLOWED_DOMAINS:
            return self._empty_create_delete_restore_preview(
                status="create_delete_restore_domain_locked",
                change_log_id=change_log_id,
                warnings=["create_delete_restore_domain_locked"],
                target_type=row.target_type,
                target_id=row.target_id,
                domain=domain,
                row_id=row_id,
            )
        if not isinstance(rollback_json, dict) or rollback_json.get("domain") != domain or int(rollback_json.get("id") or 0) != int(row_id) or rollback_json.get("sourceChangeLogId") is None:
            return self._empty_create_delete_restore_preview(
                status="create_delete_restore_metadata_invalid",
                change_log_id=change_log_id,
                warnings=["create_delete_restore_rollback_json_invalid"],
                target_type=row.target_type,
                target_id=row.target_id,
                domain=domain,
                row_id=row_id,
            )

        existing_row = await self._get_master_row(session, domain, int(row_id))
        id_conflict = existing_row is not None
        config = self.MASTER_CATALOG_DOMAINS.get(domain) or {}
        model = config.get("model")
        code = str(before_json.get("code") or "").strip()
        code_conflict = False
        if model is not None and code:
            result = await session.execute(select(model).where(model.code == code))
            code_row = result.scalar_one_or_none()
            code_conflict = code_row is not None and int(getattr(code_row, "id", 0) or 0) != int(row_id)

        validation_errors: list[dict[str, Any]] = []
        normalized_restore: dict[str, Any] = {}
        if model is None:
            validation_errors.append({"key": "domain", "label": "도메인", "reason": "invalid_restore_domain"})
        else:
            column_map = self._master_create_column_map(model)
            field_defs = {str(field["key"]): field for field in self.MASTER_CREATE_BLUEPRINT_FIELDS.get(domain, []) if field.get("key")}
            for key, value in before_json.items():
                if key not in field_defs or key not in column_map:
                    validation_errors.append({"key": key, "label": self._humanize_field_name(key), "after": serialize_value(value), "reason": "unknown_or_locked_restore_field"})
                    continue
                field_def = field_defs[key]
                if str(field_def.get("inputKind") or "") == "json-readonly" or key.endswith("_json") or self._is_asset_field(key):
                    validation_errors.append({"key": key, "label": self._humanize_field_name(key), "after": serialize_value(value), "reason": "json_or_asset_restore_field_locked"})
                    continue
                normalized, issue = self._normalize_master_edit_value(column_map[key], value)
                if issue:
                    validation_errors.append({"key": key, "label": self._humanize_field_name(key), "after": serialize_value(value), "reason": issue})
                    continue
                normalized_restore[key] = normalized
            for field_def in self.MASTER_CREATE_BLUEPRINT_FIELDS.get(domain, []) or []:
                key = str(field_def.get("key") or "")
                if field_def.get("required") and key not in normalized_restore:
                    validation_errors.append({"key": key, "label": self._humanize_field_name(key), "reason": "required_restore_field_missing"})
            relation_errors = await self._validate_master_create_relations(session, domain, normalized_restore)
            validation_errors.extend(relation_errors)

        changes = await self._build_change_log_changes_with_relations(session, domain, {}, before_json)
        restore_conflict_count = int(bool(id_conflict)) + int(bool(code_conflict)) + len(validation_errors)
        restore_ready = not id_conflict and not code_conflict and len(validation_errors) == 0 and len(normalized_restore) > 0
        warnings: list[str] = []
        if id_conflict:
            warnings.append("create_delete_restore_id_conflict")
        if code_conflict:
            warnings.append("create_delete_restore_code_conflict")
        if validation_errors:
            warnings.append("create_delete_restore_validation_errors")
        return {
            "status": "create_delete_restore_preview_ready" if restore_ready else "create_delete_restore_blocked",
            "readOnly": False,
            "dryRun": True,
            "writeBlocked": True,
            "createDeleteRestoreReady": restore_ready,
            "wouldRestore": restore_ready,
            "confirmTextRequired": self.MASTER_CREATE_DELETE_RESTORE_CONFIRM_TEXT,
            "changeLogId": int(change_log_id),
            "targetType": row.target_type,
            "targetId": row.target_id,
            "domain": domain,
            "id": int(row_id),
            "code": serialize_value(code),
            "action": row.action,
            "reason": str(reason or "")[:300] if reason else None,
            "sourceChangeReason": row.reason,
            "sourceCreateChangeLogId": int(rollback_json.get("sourceChangeLogId") or 0),
            "changes": changes,
            "changedKeys": [change["key"] for change in changes],
            "diffCount": len(changes),
            "relationChangedKeys": [change["key"] for change in changes if change.get("relation")],
            "relationChangeCount": sum(1 for change in changes if change.get("relation")),
            "targetRowMissing": not id_conflict,
            "idConflict": id_conflict,
            "codeConflict": code_conflict,
            "validationErrors": validation_errors[:30],
            "validationErrorCount": len(validation_errors),
            "restoreConflictCount": restore_conflict_count,
            "normalizedRestoreDraft": {key: serialize_value(value) for key, value in normalized_restore.items()},
            "rawBeforeAfterReturned": False,
            "warnings": warnings,
            "note": "create_delete 이력으로 삭제된 row 복원 미리보기입니다. 같은 id/code 충돌이 없고 생성 검증을 다시 통과해야만 복원 적용할 수 있습니다.",
        }

    async def apply_admin_create_delete_restore(
        self,
        session: AsyncSession,
        *,
        change_log_id: int,
        confirm_text: str,
        reason: str | None,
        admin_user_id: int,
    ) -> dict[str, Any]:
        """Restore a row deleted through create-delete apply after preview guards."""
        preview = await self.preview_admin_create_delete_restore(session, change_log_id=change_log_id, reason=reason)
        if str(confirm_text or "").strip() != self.MASTER_CREATE_DELETE_RESTORE_CONFIRM_TEXT:
            preview.update({
                "status": "create_delete_restore_confirmation_required",
                "dryRun": False,
                "writeBlocked": True,
                "restored": False,
                "createDeleteRestoreReady": False,
                "wouldRestore": False,
                "warnings": [*(preview.get("warnings") or []), "create_delete_restore_confirm_text_mismatch"],
                "note": "정확한 생성 row 복원 확인 문구를 입력해야 DB에 다시 생성할 수 있습니다.",
            })
            return preview
        if not preview.get("createDeleteRestoreReady"):
            preview.update({
                "status": "create_delete_restore_rejected",
                "dryRun": False,
                "writeBlocked": True,
                "restored": False,
                "createDeleteRestoreReady": False,
                "wouldRestore": False,
                "warnings": [*(preview.get("warnings") or []), "create_delete_restore_preview_not_safe_to_apply"],
            })
            return preview

        domain = str(preview.get("domain") or "")
        row_id = int(preview.get("id") or 0)
        config = self.MASTER_CATALOG_DOMAINS.get(domain) or {}
        model = config.get("model")
        if model is None or row_id <= 0:
            preview.update({"status": "invalid_restore_target", "restored": False, "writeBlocked": True})
            return preview

        restore_values = dict(preview.get("normalizedRestoreDraft") or {})
        row = model(id=row_id, **restore_values)
        session.add(row)
        await session.flush()

        restore_log = AdminChangeLog(
            admin_user_id=int(admin_user_id),
            target_type=f"master_data.{domain}",
            target_id=str(row_id),
            action="create_delete_restore",
            reason=(str(reason or "")[:500] or f"Restore deleted created row from change log #{change_log_id}"),
            before_json={},
            after_json={key: serialize_value(value) for key, value in restore_values.items()},
            rollback_json={"domain": domain, "id": row_id, "deleteLocked": True, "sourceDeleteChangeLogId": int(change_log_id)},
            applied=True,
        )
        session.add(restore_log)
        await session.commit()
        await session.refresh(row)
        await session.refresh(restore_log)

        preview.update({
            "status": "created_row_restored",
            "dryRun": False,
            "writeBlocked": False,
            "restored": True,
            "createDeleteRestoreReady": False,
            "wouldRestore": False,
            "restoreChangeLogId": int(restore_log.id),
            "appliedByAdminUserId": int(admin_user_id),
            "warnings": [*(preview.get("warnings") or []), "create_delete_restore_redelete_not_enabled", "game_runtime_requires_reload"],
            "note": "create_delete 이력으로 삭제했던 master-data row를 같은 id로 복원했고 create_delete_restore 이력을 저장했습니다.",
        })
        return preview

    def _empty_create_delete_restore_preview(
        self,
        *,
        status: str,
        change_log_id: int,
        warnings: list[str],
        target_type: str | None = None,
        target_id: str | None = None,
        domain: str | None = None,
        row_id: int | None = None,
    ) -> dict[str, Any]:
        return {
            "status": status,
            "readOnly": False,
            "dryRun": True,
            "writeBlocked": True,
            "createDeleteRestoreReady": False,
            "wouldRestore": False,
            "confirmTextRequired": self.MASTER_CREATE_DELETE_RESTORE_CONFIRM_TEXT,
            "changeLogId": int(change_log_id or 0),
            "targetType": target_type,
            "targetId": target_id,
            "domain": domain,
            "id": row_id,
            "changes": [],
            "changedKeys": [],
            "diffCount": 0,
            "relationChangedKeys": [],
            "relationChangeCount": 0,
            "targetRowMissing": False,
            "idConflict": False,
            "codeConflict": False,
            "validationErrors": [],
            "validationErrorCount": 0,
            "restoreConflictCount": 0,
            "rawBeforeAfterReturned": False,
            "warnings": warnings,
        }

    def _empty_create_delete_preview(
        self,
        *,
        status: str,
        change_log_id: int,
        warnings: list[str],
        target_type: str | None = None,
        target_id: str | None = None,
        domain: str | None = None,
        row_id: int | None = None,
    ) -> dict[str, Any]:
        return {
            "status": status,
            "readOnly": False,
            "dryRun": True,
            "writeBlocked": True,
            "createDeleteReady": False,
            "wouldDelete": False,
            "confirmTextRequired": self.MASTER_CREATE_DELETE_CONFIRM_TEXT,
            "changeLogId": int(change_log_id or 0),
            "targetType": target_type,
            "targetId": target_id,
            "domain": domain,
            "id": row_id,
            "changes": [],
            "changedKeys": [],
            "diffCount": 0,
            "currentMatchesCreateValues": False,
            "currentMismatches": [],
            "currentMismatchCount": 0,
            "dependencyChecks": [],
            "dependencyCheckCount": 0,
            "dependencyBlockerGuardCount": 0,
            "dependencyBlockerCount": 0,
            "rawBeforeAfterReturned": False,
            "warnings": warnings,
        }

    async def _build_create_delete_dependency_checks(self, session: AsyncSession, domain: str, code: Any, row_id: int | None = None) -> list[dict[str, Any]]:
        code_text = "" if code is None else str(code).strip()

        async def check(label: str, model: Any, column_name: str, note: str) -> dict[str, Any]:
            column = getattr(model, column_name)
            count = await self._count_where(session, model, column == code_text)
            return {"label": label, "target": f"{model.__tablename__}.{column_name}", "count": count, "blocksDelete": count > 0, "note": note}

        if domain == "dropTableItems":
            return [
                {
                    "label": "id 기반 드랍 아이템",
                    "target": "drop_table_items.id",
                    "count": 0,
                    "blocksDelete": False,
                    "note": "dropTableItems는 하위 연결이 없는 leaf row라 현재값 일치 검사 후 id 기준으로 삭제할 수 있습니다.",
                }
            ]
        if domain == "skillLevels":
            return [
                {
                    "label": "id 기반 스킬 레벨",
                    "target": "skill_levels.id",
                    "count": 0,
                    "blocksDelete": False,
                    "note": "skillLevels는 skills를 참조하는 leaf row라 현재값 일치 검사 후 id 기준으로 삭제할 수 있습니다.",
                }
            ]
        if domain == "enhancementLevels":
            return [
                {
                    "label": "id 기반 강화 단계",
                    "target": "enhancement_levels.id",
                    "count": 0,
                    "blocksDelete": False,
                    "note": "enhancementLevels는 enhancementGroups를 참조하는 leaf row라 현재값 일치 검사 후 id 기준으로 삭제할 수 있습니다.",
                }
            ]
        if domain == "characterSkills":
            return [
                {
                    "label": "id 기반 캐릭터 스킬 연결",
                    "target": "character_skills.id",
                    "count": 0,
                    "blocksDelete": False,
                    "note": "characterSkills는 캐릭터와 스킬을 연결하는 leaf row라 현재값 일치 검사 후 id 기준으로 삭제할 수 있습니다.",
                }
            ]

        if not code_text:
            return [{"label": "code", "count": 1, "blocksDelete": True, "note": "삭제 대상 code를 찾을 수 없어 삭제를 막았습니다."}]

        if domain == "characters":
            return [
                await check("캐릭터 스킬 연결", CharacterSkill, "character_code", "characterSkills에서 사용 중이면 캐릭터 삭제를 막습니다."),
                await check("유저 캐릭터 스킬", UserCharacterSkill, "character_code", "유저 스킬 데이터에서 사용 중이면 삭제를 막습니다."),
                await check("유저 장비 슬롯", UserEquipmentSlot, "character_code", "유저 장비 슬롯에서 사용 중이면 삭제를 막습니다."),
                await check("유저 현재 캐릭터", UserProfile, "current_character_id", "유저 프로필의 현재 캐릭터로 사용 중이면 삭제를 막습니다."),
            ]
        if domain == "enhancementGroups":
            return [
                await check("강화 단계", EnhancementLevel, "group_code", "enhancementLevels에서 사용 중이면 강화 그룹 삭제를 막습니다."),
                await check("아이템 강화 그룹", ItemTemplate, "enhance_group_code", "itemTemplates에서 사용 중이면 강화 그룹 삭제를 막습니다."),
            ]
        if domain == "fieldZones":
            drop_table_count = await self._count_where(session, DropTable, DropTable.owner_type == "field", DropTable.owner_code == code_text)
            return [
                {
                    "label": "필드 드랍 테이블",
                    "target": "drop_tables.owner_type=field + owner_code",
                    "count": drop_table_count,
                    "blocksDelete": drop_table_count > 0,
                    "note": "dropTables에서 owner_type=field와 owner_code로 사용 중이면 필드 삭제를 막습니다.",
                },
            ]
        if domain == "bosses":
            drop_table_count = await self._count_where(session, DropTable, DropTable.owner_type == "boss", DropTable.owner_code == code_text)
            return [
                {
                    "label": "보스 드랍 테이블",
                    "target": "drop_tables.owner_type=boss + owner_code",
                    "count": drop_table_count,
                    "blocksDelete": drop_table_count > 0,
                    "note": "dropTables에서 owner_type=boss와 owner_code로 사용 중이면 보스 삭제를 막습니다.",
                },
            ]
        if domain == "skills":
            return [
                await check("스킬 레벨", SkillLevel, "skill_code", "skillLevels에서 사용 중이면 스킬 삭제를 막습니다."),
                await check("캐릭터 스킬 연결", CharacterSkill, "skill_code", "characterSkills에서 사용 중이면 스킬 삭제를 막습니다."),
                await check("유저 캐릭터 스킬", UserCharacterSkill, "skill_code", "유저 스킬 데이터에서 사용 중이면 삭제를 막습니다."),
            ]
        if domain == "dropTables":
            return [
                await check("드랍 아이템", DropTableItem, "drop_table_code", "dropTableItems에서 사용 중이면 드랍 테이블 삭제를 막습니다."),
            ]
        if domain == "itemTemplates":
            return [
                await check("드랍 아이템", DropTableItem, "item_template_code", "dropTableItems에서 사용 중이면 아이템 템플릿 삭제를 막습니다."),
                await check("유저 아이템 인스턴스", ItemInstance, "template_code", "유저 인벤토리에 생성된 아이템 인스턴스가 있으면 삭제를 막습니다."),
            ]
        return [{"label": "도메인 잠금", "count": 1, "blocksDelete": True, "note": "이 도메인은 생성 row 삭제 되돌리기 allow-list에 없습니다."}]

    async def preview_master_data_create(
        self,
        session: AsyncSession,
        *,
        domain: str,
        draft: dict[str, Any],
        reason: str | None = None,
        dry_run: bool = True,
    ) -> dict[str, Any]:
        config = self.MASTER_CATALOG_DOMAINS.get(domain)
        if not config:
            return self._empty_create_preview(
                status="invalid_domain",
                domain=domain,
                domain_label=domain,
                warnings=["domain_invalid"],
            )

        model = config["model"]
        column_map = self._master_create_column_map(model)
        blueprint_defs = [field for field in self.MASTER_CREATE_BLUEPRINT_FIELDS.get(domain, []) if field.get("key")]
        allowed_keys = {str(field["key"]) for field in blueprint_defs}
        safe_draft = draft if isinstance(draft, dict) else {}
        if len(safe_draft) > 100:
            safe_draft = dict(list(safe_draft.items())[:100])

        accepted_fields: list[dict[str, Any]] = []
        rejected_fields: list[dict[str, Any]] = []
        normalized_values: dict[str, Any] = {}
        warnings: list[str] = []
        field_defs = {str(field["key"]): field for field in blueprint_defs}

        for key, field_def in field_defs.items():
            column = column_map.get(key)
            if column is None:
                rejected_fields.append({"key": key, "label": self._humanize_field_name(key), "reason": "column_not_found"})
                continue
            if str(field_def.get("inputKind") or "") == "json-readonly" or key.endswith("_json") or self._is_asset_field(key):
                continue
            raw_value = safe_draft.get(key, field_def.get("defaultValue"))
            normalized, issue = self._normalize_master_edit_value(column, raw_value)
            if issue:
                rejected_fields.append({"key": key, "label": self._humanize_field_name(key), "after": serialize_value(raw_value), "reason": issue})
                continue
            normalized_values[key] = normalized

        for key, field_def in field_defs.items():
            if str(field_def.get("inputKind") or "") == "json-readonly" or key.endswith("_json") or self._is_asset_field(key):
                continue
            value = normalized_values.get(key)
            if field_def.get("required") and (value is None or (isinstance(value, str) and value.strip() == "")):
                rejected_fields.append({"key": key, "label": self._humanize_field_name(key), "after": serialize_value(value), "reason": "required_field_missing"})
            if field_def.get("unique") and value is not None and str(value).strip():
                duplicate = await self._exists_duplicate_unique_value(session, model, key, value)
                if duplicate:
                    rejected_fields.append({"key": key, "label": self._humanize_field_name(key), "after": serialize_value(value), "reason": f"duplicate_unique_{key}"})

        for raw_key in safe_draft.keys():
            key = str(raw_key or "").strip()
            if not key or key in allowed_keys:
                continue
            rejected_fields.append({"key": key or raw_key, "label": self._humanize_field_name(key), "after": serialize_value(safe_draft.get(raw_key)), "reason": "unknown_or_locked_create_field"})

        relation_errors = await self._validate_master_create_relations(session, domain, normalized_values)
        rejected_fields.extend(relation_errors)

        rejected_key_reasons = {(str(item.get("key")), str(item.get("reason"))) for item in rejected_fields}
        for key, value in normalized_values.items():
            if any(item_key == key for item_key, _reason in rejected_key_reasons):
                continue
            field_def = field_defs.get(key) or {}
            relation = await self._describe_master_create_relation_value(session, domain, key, value, normalized_values)
            accepted_fields.append({
                "key": key,
                "label": self._humanize_field_name(key),
                "after": serialize_value(value),
                "type": self._master_edit_column_type(column_map[key]),
                "required": bool(field_def.get("required")),
                "unique": bool(field_def.get("unique")),
                "relation": relation,
                "inputKind": field_def.get("inputKind") or "text",
            })

        error_count = len(rejected_fields)
        relation_count = sum(1 for field in accepted_fields if field.get("relation"))
        combo_labels = self._create_combo_guard_labels(domain)
        create_apply_unlocked = domain in self.MASTER_CREATE_APPLY_ALLOWED_DOMAINS
        create_apply_ready = create_apply_unlocked and error_count == 0 and len(accepted_fields) > 0
        return {
            "status": "previewed",
            "readOnly": True,
            "dryRun": True,
            "writeBlocked": True,
            "createApplyReady": create_apply_ready,
            "createApplyUnlocked": create_apply_unlocked,
            "insertLocked": not create_apply_unlocked,
            "confirmTextRequired": self.MASTER_CREATE_APPLY_CONFIRM_TEXT,
            "allowedCreateApplyDomains": sorted(self.MASTER_CREATE_APPLY_ALLOWED_DOMAINS),
            "wouldBeValid": error_count == 0,
            "domain": domain,
            "domainLabel": config["label"],
            "reason": reason,
            "fieldCount": len(accepted_fields),
            "errorCount": error_count,
            "acceptedFields": accepted_fields,
            "rejectedFields": rejected_fields,
            "normalizedDraft": {key: serialize_value(value) for key, value in normalized_values.items()},
            "relationFieldCount": relation_count,
            "relationLabelsReturned": relation_count > 0,
            "comboGuardLabels": combo_labels,
            "comboGuardCount": len(combo_labels),
            "rawJsonReturned": False,
            "assetsReturned": False,
            "warnings": warnings,
            "note": "신규 row 생성 초안을 검증했습니다. characters/enhancementGroups/fieldZones/bosses/skills/dropTables/itemTemplates/dropTableItems/skillLevels/enhancementLevels/characterSkills는 dev key와 확인 문구를 통과하면 실제 생성 적용이 가능합니다." if create_apply_unlocked else "신규 row 생성 초안을 검증했습니다. 이 도메인의 실제 insert는 아직 잠겨 있습니다.",
        }

    async def apply_master_data_create(
        self,
        session: AsyncSession,
        *,
        domain: str,
        draft: dict[str, Any],
        reason: str | None,
        confirm_text: str,
        admin_user_id: int,
    ) -> dict[str, Any]:
        """Apply a guarded new-row insert for a very small safe domain allow-list.

        The create path is deliberately narrower than edit apply. It only opens
        relation-light domains first, validates through the same preview function,
        requires the admin dev key at the route layer, requires an exact
        confirmation phrase, and records a create change log. Create rollback/delete
        is intentionally not opened in this step.
        """
        preview = await self.preview_master_data_create(
            session,
            domain=domain,
            draft=draft,
            reason=reason,
            dry_run=True,
        )

        if domain not in self.MASTER_CREATE_APPLY_ALLOWED_DOMAINS:
            preview.update({
                "status": "create_domain_locked",
                "readOnly": False,
                "dryRun": False,
                "writeBlocked": True,
                "created": False,
                "createApplyReady": False,
                "wouldBeValid": False,
                "errorCount": int(preview.get("errorCount") or 0) + 1,
                "warnings": [*(preview.get("warnings") or []), "create_apply_domain_locked"],
                "note": "이 도메인의 실제 신규 row 생성은 아직 열지 않았습니다. 현재는 characters/enhancementGroups/fieldZones/bosses/skills/dropTables/itemTemplates/dropTableItems/skillLevels/enhancementLevels/characterSkills만 제한적으로 생성 가능합니다.",
            })
            return preview

        if str(confirm_text or "").strip() != self.MASTER_CREATE_APPLY_CONFIRM_TEXT:
            preview.update({
                "status": "create_confirmation_required",
                "readOnly": False,
                "dryRun": False,
                "writeBlocked": True,
                "created": False,
                "createApplyReady": False,
                "wouldBeValid": False,
                "errorCount": int(preview.get("errorCount") or 0) + 1,
                "warnings": [*(preview.get("warnings") or []), "create_confirm_text_mismatch"],
                "note": "정확한 생성 확인 문구를 입력해야 DB insert가 가능합니다.",
            })
            return preview

        if preview.get("status") != "previewed" or preview.get("errorCount") or not preview.get("acceptedFields"):
            preview.update({
                "status": "create_rejected",
                "readOnly": False,
                "dryRun": False,
                "writeBlocked": True,
                "created": False,
                "createApplyReady": False,
                "wouldBeValid": False,
                "warnings": [*(preview.get("warnings") or []), "create_preview_not_valid_for_apply"],
                "note": "검증 오류가 있거나 생성 가능한 필드가 없어 DB에 insert하지 않았습니다.",
            })
            return preview

        config = self.MASTER_CATALOG_DOMAINS.get(domain)
        if not config:
            preview.update({"status": "invalid_domain", "created": False, "writeBlocked": True})
            return preview

        model = config["model"]
        column_map = self._master_create_column_map(model)
        field_defs = {str(field["key"]): field for field in self.MASTER_CREATE_BLUEPRINT_FIELDS.get(domain, []) if field.get("key")}
        row_values: dict[str, Any] = {}
        after_values: dict[str, Any] = {}
        for field in preview.get("acceptedFields") or []:
            key = str(field.get("key") or "").strip()
            if not key or key not in field_defs or key not in column_map:
                continue
            field_def = field_defs[key]
            if str(field_def.get("inputKind") or "") == "json-readonly" or key.endswith("_json") or self._is_asset_field(key):
                continue
            raw_value = (draft or {}).get(key, field_def.get("defaultValue"))
            normalized, issue = self._normalize_master_edit_value(column_map[key], raw_value)
            if issue:
                continue
            row_values[key] = normalized
            after_values[key] = serialize_value(normalized)

        if not row_values:
            await session.rollback()
            preview.update({
                "status": "nothing_to_create",
                "readOnly": False,
                "dryRun": False,
                "writeBlocked": True,
                "created": False,
                "createApplyReady": False,
                "warnings": [*(preview.get("warnings") or []), "no_insertable_values"],
            })
            return preview

        row = model(**row_values)
        session.add(row)
        await session.flush()

        created_id = int(getattr(row, "id", 0) or 0)
        created_code = getattr(row, "code", None)
        created_title = getattr(row, "name", None) or created_code or f"#{created_id}"
        change_log = AdminChangeLog(
            admin_user_id=int(admin_user_id),
            target_type=f"master_data.{domain}",
            target_id=str(created_id),
            action="create",
            reason=str(reason or "")[:500] or None,
            before_json={},
            after_json=after_values,
            rollback_json={"domain": domain, "id": created_id, "delete": True},
            applied=True,
        )
        session.add(change_log)
        await session.commit()
        await session.refresh(row)
        await session.refresh(change_log)

        return {
            **preview,
            "status": "created",
            "readOnly": False,
            "dryRun": False,
            "writeBlocked": False,
            "created": True,
            "createApplyReady": False,
            "wouldBeValid": True,
            "id": created_id,
            "code": serialize_value(created_code),
            "title": serialize_value(created_title),
            "createdRow": {"domain": domain, "id": created_id, "code": serialize_value(created_code), "title": serialize_value(created_title)},
            "changeLogId": int(change_log.id),
            "appliedByAdminUserId": int(admin_user_id),
            "note": "신규 master-data row를 DB에 생성했고 admin_change_logs에 create 이력을 저장했습니다. 제한 도메인 생성 row 삭제/복원은 별도 preview/apply 안전 검사를 통과해야 가능합니다.",
            "warnings": [*(preview.get("warnings") or []), "create_delete_restore_preview_enabled", "game_runtime_requires_reload"],
        }

    def _empty_create_preview(self, *, status: str, domain: str, domain_label: str, warnings: list[str]) -> dict[str, Any]:
        return {
            "status": status,
            "readOnly": True,
            "dryRun": True,
            "writeBlocked": True,
            "createApplyReady": False,
            "createApplyUnlocked": False,
            "insertLocked": True,
            "confirmTextRequired": self.MASTER_CREATE_APPLY_CONFIRM_TEXT,
            "allowedCreateApplyDomains": sorted(self.MASTER_CREATE_APPLY_ALLOWED_DOMAINS),
            "wouldBeValid": False,
            "domain": domain,
            "domainLabel": domain_label,
            "fieldCount": 0,
            "errorCount": 1,
            "acceptedFields": [],
            "rejectedFields": [],
            "normalizedDraft": {},
            "relationFieldCount": 0,
            "relationLabelsReturned": False,
            "comboGuardLabels": [],
            "comboGuardCount": 0,
            "rawJsonReturned": False,
            "assetsReturned": False,
            "warnings": warnings,
        }

    @staticmethod
    def _master_create_column_map(model: Any) -> dict[str, Any]:
        mapper = sa_inspect(model)
        return {column_attr.key: column_attr.columns[0] for column_attr in mapper.mapper.column_attrs}

    async def _exists_duplicate_unique_value(self, session: AsyncSession, model: Any, key: str, value: Any) -> bool:
        column = getattr(model, key, None)
        if column is None:
            return False
        result = await session.execute(select(func.count()).select_from(model).where(column == value))
        return int(result.scalar_one() or 0) > 0

    def _create_combo_guard_labels(self, domain: str) -> list[str]:
        labels: list[str] = []
        for field_def in self.MASTER_CREATE_BLUEPRINT_FIELDS.get(domain, []) or []:
            combo = field_def.get("comboGuard")
            if isinstance(combo, list) and combo:
                label = " + ".join(str(item) for item in combo)
                if label not in labels:
                    labels.append(label)
        return labels

    async def _validate_master_create_relations(self, session: AsyncSession, domain: str, values: dict[str, Any]) -> list[dict[str, Any]]:
        errors: list[dict[str, Any]] = []

        def add(key: str, reason: str, value: Any = None) -> None:
            errors.append({"key": key, "label": self._humanize_field_name(key), "after": serialize_value(value if value is not None else values.get(key)), "reason": reason})

        if domain == "itemTemplates":
            code = str(values.get("enhance_group_code") or "").strip()
            if code and not await self._exists_by_code(session, EnhancementGroup, code):
                add("enhance_group_code", "relation_target_not_found_enhancement_group", code)
        elif domain == "dropTables":
            owner_type = str(values.get("owner_type") or "").strip()
            owner_code = str(values.get("owner_code") or "").strip()
            if owner_type not in {"boss", "field"}:
                add("owner_type", "invalid_owner_type", owner_type)
            if not owner_code:
                add("owner_code", "owner_code_missing", owner_code)
            elif owner_type in {"boss", "field"}:
                model = Boss if owner_type == "boss" else FieldZone
                if not await self._exists_by_code(session, model, owner_code):
                    add("owner_code", "owner_code_not_found_for_owner_type", owner_code)
        elif domain == "dropTableItems":
            drop_table_code = str(values.get("drop_table_code") or "").strip()
            item_template_code = str(values.get("item_template_code") or "").strip()
            rate = values.get("rate")
            min_quantity = values.get("min_quantity")
            max_quantity = values.get("max_quantity")
            if not drop_table_code or not await self._exists_by_code(session, DropTable, drop_table_code):
                add("drop_table_code", "relation_target_not_found_drop_table", drop_table_code)
            if not item_template_code or not await self._exists_by_code(session, ItemTemplate, item_template_code):
                add("item_template_code", "relation_target_not_found_item_template", item_template_code)
            if rate is None or float(rate) < 0:
                add("rate", "invalid_drop_rate", rate)
            if min_quantity is None or int(min_quantity) < 1:
                add("min_quantity", "invalid_min_quantity", min_quantity)
            if max_quantity is None or int(max_quantity) < 1:
                add("max_quantity", "invalid_max_quantity", max_quantity)
            if min_quantity is not None and max_quantity is not None and int(max_quantity) < int(min_quantity):
                add("max_quantity", "max_quantity_less_than_min_quantity", max_quantity)
        elif domain == "skillLevels":
            skill_code = str(values.get("skill_code") or "").strip()
            level = values.get("level")
            if not skill_code or not await self._exists_by_code(session, Skill, skill_code):
                add("skill_code", "relation_target_not_found_skill", skill_code)
            if level is None or int(level) < 0:
                add("level", "invalid_skill_level", level)
            elif skill_code and await self._exists_by_code(session, Skill, skill_code):
                duplicate = await self._exists_duplicate_combo(session, SkillLevel, 0, SkillLevel.skill_code == skill_code, SkillLevel.level == int(level))
                if duplicate:
                    add("level", "duplicate_skill_code_level", level)
        elif domain == "enhancementLevels":
            group_code = str(values.get("group_code") or "").strip()
            from_level = values.get("from_level")
            to_level = values.get("to_level")
            success_rate = values.get("success_rate")
            gold_cost = values.get("gold_cost")
            if not group_code or not await self._exists_by_code(session, EnhancementGroup, group_code):
                add("group_code", "relation_target_not_found_enhancement_group", group_code)
            if from_level is None or int(from_level) < 0:
                add("from_level", "invalid_enhancement_from_level", from_level)
            elif group_code and await self._exists_by_code(session, EnhancementGroup, group_code):
                duplicate = await self._exists_duplicate_combo(session, EnhancementLevel, 0, EnhancementLevel.group_code == group_code, EnhancementLevel.from_level == int(from_level))
                if duplicate:
                    add("from_level", "duplicate_enhancement_group_from_level", from_level)
            if to_level is None or int(to_level) <= int(from_level or 0):
                add("to_level", "invalid_enhancement_to_level", to_level)
            if success_rate is not None and float(success_rate) < 0:
                add("success_rate", "invalid_enhancement_success_rate", success_rate)
            if gold_cost is not None and float(gold_cost) < 0:
                add("gold_cost", "invalid_enhancement_gold_cost", gold_cost)
        elif domain == "characterSkills":
            character_code = str(values.get("character_code") or "").strip()
            skill_code = str(values.get("skill_code") or "").strip()
            sort_order = values.get("sort_order")
            if not character_code or not await self._exists_by_code(session, Character, character_code):
                add("character_code", "relation_target_not_found_character", character_code)
            if not skill_code or not await self._exists_by_code(session, Skill, skill_code):
                add("skill_code", "relation_target_not_found_skill", skill_code)
            if character_code and skill_code and await self._exists_by_code(session, Character, character_code) and await self._exists_by_code(session, Skill, skill_code):
                duplicate = await self._exists_duplicate_combo(session, CharacterSkill, 0, CharacterSkill.character_code == character_code, CharacterSkill.skill_code == skill_code)
                if duplicate:
                    add("skill_code", "duplicate_character_skill_pair", skill_code)
            if sort_order is not None and int(sort_order) < 0:
                add("sort_order", "invalid_character_skill_sort_order", sort_order)
        return errors

    async def _describe_master_create_relation_value(self, session: AsyncSession, domain: str, key: str, value: Any, values: dict[str, Any]) -> dict[str, Any] | None:
        value_text = "" if value is None else str(value).strip()
        if domain == "itemTemplates" and key == "enhance_group_code":
            if not value_text:
                return {"field": key, "targetDomain": "enhancementGroups", "targetCode": None, "targetLabel": "강화 그룹 없음", "displayText": "강화 그룹 없음"}
            target = await self._fetch_code_name(session, EnhancementGroup, value_text)
            label = target.get("name") if target else value_text
            return {"field": key, "targetDomain": "enhancementGroups", "targetCode": value_text, "targetLabel": label, "displayText": f"{value_text} · {label}" if label != value_text else value_text}
        if domain == "dropTables" and key == "owner_type":
            label = "보스" if value_text == "boss" else "필드"
            target_domain = "bosses" if value_text == "boss" else "fieldZones"
            return {"field": key, "targetDomain": target_domain, "targetCode": value_text, "targetLabel": label, "displayText": f"{value_text} · {label}"}
        if domain == "dropTables" and key == "owner_code":
            owner_type = str(values.get("owner_type") or "boss").strip()
            target_domain = "fieldZones" if owner_type == "field" else "bosses"
            target_model = FieldZone if owner_type == "field" else Boss
            target = await self._fetch_code_name(session, target_model, value_text)
            label = target.get("name") if target else value_text
            return {"field": key, "targetDomain": target_domain, "targetCode": value_text, "targetLabel": label, "displayText": f"{value_text} · {label}" if label != value_text else value_text}
        relation_targets = {
            ("dropTableItems", "drop_table_code"): (DropTable, "dropTables"),
            ("dropTableItems", "item_template_code"): (ItemTemplate, "itemTemplates"),
            ("skillLevels", "skill_code"): (Skill, "skills"),
            ("enhancementLevels", "group_code"): (EnhancementGroup, "enhancementGroups"),
            ("characterSkills", "character_code"): (Character, "characters"),
            ("characterSkills", "skill_code"): (Skill, "skills"),
        }
        target_def = relation_targets.get((domain, key))
        if target_def:
            model, target_domain = target_def
            target = await self._fetch_code_name(session, model, value_text)
            label = target.get("name") if target else value_text
            return {"field": key, "targetDomain": target_domain, "targetCode": value_text, "targetLabel": label, "displayText": f"{value_text} · {label}" if label != value_text else value_text}
        return None

    async def get_master_create_blueprint(self, session: AsyncSession, *, domain: str = "itemTemplates") -> dict[str, Any]:
        """Return a read-only create blueprint for a master-data domain.

        This prepares the future new-row UI without opening a DB insert path. It
        exposes required fields, safe defaults, relation candidates, and duplicate
        guard hints only. No database mutation is performed.
        """
        config = self.MASTER_CATALOG_DOMAINS.get(domain)
        if not config:
            return {
                "status": "invalid_domain",
                "readOnly": True,
                "createApplyReady": False,
                "createApplyUnlocked": False,
                "insertLocked": True,
                "confirmTextRequired": self.MASTER_CREATE_APPLY_CONFIRM_TEXT,
                "allowedCreateApplyDomains": sorted(self.MASTER_CREATE_APPLY_ALLOWED_DOMAINS),
                "createLifecycle": self._master_create_lifecycle_payload(domain),
                "domain": domain,
                "domainLabel": domain,
                "description": None,
                "fields": [],
                "requiredFields": [],
                "uniqueFields": [],
                "comboGuards": [],
                "defaultDraft": {},
                "relationOptionsReturned": False,
                "rawJsonReturned": False,
                "assetsReturned": False,
                "warnings": ["domain_invalid"],
                "note": "알 수 없는 도메인이라 신규 row 생성 설계를 만들 수 없습니다.",
            }

        blueprint_defs = list(self.MASTER_CREATE_BLUEPRINT_FIELDS.get(domain) or [])
        relation_options = await self._build_master_create_relation_options(session, domain)
        fields: list[dict[str, Any]] = []
        default_draft: dict[str, Any] = {}
        combo_guards: list[list[str]] = []
        relation_count = 0
        for field_def in blueprint_defs:
            key = str(field_def.get("key") or "")
            if not key:
                continue
            default_value = field_def.get("defaultValue")
            input_kind = str(field_def.get("inputKind") or "text")
            is_json_locked = input_kind == "json-readonly" or key.endswith("_json")
            if not is_json_locked:
                default_draft[key] = default_value
            combo_guard = field_def.get("comboGuard") if isinstance(field_def.get("comboGuard"), list) else None
            if combo_guard and combo_guard not in combo_guards:
                combo_guards.append(combo_guard)
            relation_payload = relation_options.get(key)
            if relation_payload:
                relation_count += 1
            fields.append({
                "key": key,
                "label": self._humanize_field_name(key),
                "inputKind": input_kind,
                "required": bool(field_def.get("required")),
                "unique": bool(field_def.get("unique")),
                "nullable": bool(field_def.get("nullable")) if "nullable" in field_def else not bool(field_def.get("required")),
                "defaultValue": serialize_value(default_value),
                "targetDomain": field_def.get("targetDomain"),
                "dependsOn": field_def.get("dependsOn"),
                "comboGuard": combo_guard or [],
                "relation": relation_payload,
                "locked": True,
                "futureEditable": not is_json_locked,
                "lockedReason": field_def.get("lockedReason") or "현재 단계는 생성 설계 read-only입니다. 실제 insert API는 아직 열지 않았습니다.",
                "note": field_def.get("note"),
            })

        create_apply_unlocked = domain in self.MASTER_CREATE_APPLY_ALLOWED_DOMAINS
        return {
            "status": "loaded",
            "readOnly": True,
            "createApplyReady": False,
            "createApplyUnlocked": create_apply_unlocked,
            "insertLocked": not create_apply_unlocked,
            "confirmTextRequired": self.MASTER_CREATE_APPLY_CONFIRM_TEXT,
            "allowedCreateApplyDomains": sorted(self.MASTER_CREATE_APPLY_ALLOWED_DOMAINS),
            "createLifecycle": self._master_create_lifecycle_payload(domain),
            "domain": domain,
            "domainLabel": config["label"],
            "description": config.get("description"),
            "fieldCount": len(fields),
            "requiredFields": [field["key"] for field in fields if field.get("required")],
            "uniqueFields": [field["key"] for field in fields if field.get("unique")],
            "comboGuards": combo_guards,
            "defaultDraft": default_draft,
            "fields": fields,
            "relationOptionsReturned": relation_count > 0,
            "relationFieldCount": relation_count,
            "rawJsonReturned": False,
            "assetsReturned": False,
            "warnings": [],
            "note": "신규 row 생성 설계 응답입니다. characters/enhancementGroups/fieldZones/bosses/skills/dropTables/itemTemplates/dropTableItems/skillLevels/enhancementLevels/characterSkills는 dev key와 확인 문구를 통과하면 실제 생성 적용이 가능합니다." if create_apply_unlocked else "신규 row 생성 설계 응답입니다. 이 도메인의 실제 insert는 아직 잠겨 있습니다.",
        }

    async def _build_master_create_relation_options(self, session: AsyncSession, domain: str) -> dict[str, Any]:
        if domain == "itemTemplates":
            options = [{"value": "", "label": "없음 · 강화 그룹 연결 안 함", "current": True}]
            options.extend(await self._fetch_relation_code_options(session, EnhancementGroup, limit=300))
            return {"enhance_group_code": {"targetDomain": "enhancementGroups", "targetLabel": "강화 그룹", "nullable": True, "options": options}}
        if domain == "skillLevels":
            return {"skill_code": {"targetDomain": "skills", "targetLabel": "스킬", "nullable": False, "comboGuard": ["skill_code", "level"], "options": await self._fetch_relation_code_options(session, Skill, limit=300)}}
        if domain == "dropTables":
            return {
                "owner_code": {
                    "targetDomain": "bosses/fieldZones",
                    "targetLabel": "드랍 테이블 소유자 코드",
                    "nullable": False,
                    "dependsOn": "owner_type",
                    "optionGroups": {
                        "boss": await self._fetch_relation_code_options(session, Boss, limit=300),
                        "field": await self._fetch_relation_code_options(session, FieldZone, limit=300),
                    },
                    "options": await self._fetch_relation_code_options(session, Boss, limit=300),
                }
            }
        if domain == "dropTableItems":
            return {
                "drop_table_code": {"targetDomain": "dropTables", "targetLabel": "드랍 테이블", "nullable": False, "options": await self._fetch_relation_code_options(session, DropTable, limit=300)},
                "item_template_code": {"targetDomain": "itemTemplates", "targetLabel": "아이템 템플릿", "nullable": False, "options": await self._fetch_relation_code_options(session, ItemTemplate, limit=300)},
            }
        if domain == "enhancementLevels":
            return {"group_code": {"targetDomain": "enhancementGroups", "targetLabel": "강화 그룹", "nullable": False, "comboGuard": ["group_code", "from_level"], "options": await self._fetch_relation_code_options(session, EnhancementGroup, limit=300)}}
        if domain == "characterSkills":
            return {
                "character_code": {"targetDomain": "characters", "targetLabel": "캐릭터", "nullable": False, "comboGuard": ["character_code", "skill_code"], "options": await self._fetch_relation_code_options(session, Character, limit=200)},
                "skill_code": {"targetDomain": "skills", "targetLabel": "스킬", "nullable": False, "comboGuard": ["character_code", "skill_code"], "options": await self._fetch_relation_code_options(session, Skill, limit=300)},
            }
        return {}
