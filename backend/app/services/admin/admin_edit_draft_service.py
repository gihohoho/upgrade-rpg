from __future__ import annotations

from typing import Any

from sqlalchemy import Boolean, Integer, Numeric, String, Text, func, inspect as sa_inspect, select
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
    ItemTemplate,
    Skill,
    SkillLevel,
)
from app.services.game_service import serialize_value


class AdminEditDraftService:
    """Guarded master-data edit preview/apply helpers.

    Split from AdminService in v203 while AdminService remains the facade used by routes.
    """
    async def preview_master_data_edit(
        self,
        session: AsyncSession,
        *,
        domain: str,
        row_id: int,
        draft: dict[str, Any],
        base_values: dict[str, Any] | None = None,
        reason: str | None = None,
        dry_run: bool = True,
    ) -> dict[str, Any]:
        """Validate an admin edit draft without mutating the database.

        The static admin page can now behave like a real edit screen, but this
        endpoint is still preview-only. It loads the current row from PostgreSQL,
        normalizes proposed scalar values, builds a diff, and returns validation
        errors/warnings. It never assigns attributes, flushes, commits, or returns
        raw JSON/assets.
        """
        config = self.MASTER_CATALOG_DOMAINS.get(domain)
        if not config:
            return self._empty_edit_preview(
                status="invalid_domain",
                domain=domain,
                domain_label=domain,
                row_id=row_id,
                warnings=["domain_invalid"],
            )

        safe_row_id = int(row_id or 0)
        if safe_row_id <= 0:
            return self._empty_edit_preview(
                status="invalid_id",
                domain=domain,
                domain_label=config["label"],
                row_id=row_id,
                warnings=["id_invalid"],
            )

        model = config["model"]
        result = await session.execute(select(model).where(model.id == safe_row_id))
        row = result.scalar_one_or_none()
        if row is None:
            return self._empty_edit_preview(
                status="not_found",
                domain=domain,
                domain_label=config["label"],
                row_id=safe_row_id,
                warnings=["row_not_found"],
            )

        safe_draft = draft if isinstance(draft, dict) else {}
        if len(safe_draft) > 80:
            # The UI only sends visible fields, but this keeps manual API calls bounded.
            safe_draft = dict(list(safe_draft.items())[:80])

        safe_base_values = base_values if isinstance(base_values, dict) else None

        column_map = self._master_edit_column_map(row)
        accepted_changes: list[dict[str, Any]] = []
        unchanged: list[dict[str, Any]] = []
        rejected_changes: list[dict[str, Any]] = []
        stale_changes: list[dict[str, Any]] = []
        warnings: list[str] = []

        for raw_key, raw_after in safe_draft.items():
            key = str(raw_key or "").strip()
            if not key:
                rejected_changes.append({"key": raw_key, "reason": "empty_field_key"})
                continue

            column = column_map.get(key)
            if column is None:
                rejected_changes.append({"key": key, "reason": "unknown_field"})
                continue

            if self._master_edit_field_is_readonly(domain, key):
                rejected_changes.append({"key": key, "label": self._humanize_field_name(key), "reason": "read_only_field"})
                continue
            if not self._master_edit_field_is_allowed(domain, key):
                rejected_changes.append({"key": key, "label": self._humanize_field_name(key), "reason": "field_not_open_for_apply_yet"})
                continue
            if key.endswith("_json"):
                rejected_changes.append({"key": key, "label": self._humanize_field_name(key), "reason": "json_edit_not_enabled_yet"})
                continue
            if self._is_asset_field(key):
                rejected_changes.append({"key": key, "label": self._humanize_field_name(key), "reason": "asset_edit_not_enabled_yet"})
                continue

            before_value = serialize_value(getattr(row, key, None))

            if safe_base_values is not None:
                if key not in safe_base_values:
                    stale_changes.append({
                        "key": key,
                        "label": self._humanize_field_name(key),
                        "base": None,
                        "current": before_value,
                        "after": raw_after,
                        "reason": "base_value_missing",
                    })
                    rejected_changes.append({
                        "key": key,
                        "label": self._humanize_field_name(key),
                        "before": before_value,
                        "after": raw_after,
                        "reason": "base_value_missing",
                    })
                    continue

                normalized_base, base_issue = self._normalize_master_edit_value(column, safe_base_values.get(key))
                base_value = serialize_value(safe_base_values.get(key) if base_issue else normalized_base)
                if base_value != before_value:
                    stale_changes.append({
                        "key": key,
                        "label": self._humanize_field_name(key),
                        "base": base_value,
                        "current": before_value,
                        "after": raw_after,
                        "reason": "current_value_changed_since_form_loaded",
                    })
                    rejected_changes.append({
                        "key": key,
                        "label": self._humanize_field_name(key),
                        "before": before_value,
                        "after": raw_after,
                        "reason": "current_value_changed_since_form_loaded",
                    })
                    continue

            normalized_after, issue = self._normalize_master_edit_value(column, raw_after)
            if issue:
                rejected_changes.append({
                    "key": key,
                    "label": self._humanize_field_name(key),
                    "before": before_value,
                    "after": raw_after,
                    "reason": issue,
                })
                continue

            relation_issue = await self._validate_master_relation_edit_value(session, domain, key, normalized_after, row, safe_draft, column_map)
            if relation_issue:
                rejected_changes.append({
                    "key": key,
                    "label": self._humanize_field_name(key),
                    "before": before_value,
                    "after": raw_after,
                    "reason": relation_issue,
                })
                continue

            relation_info = await self._describe_master_relation_edit_value(session, domain, key, normalized_after, row, safe_draft, column_map)
            normalized_after = serialize_value(normalized_after)
            change = {
                "key": key,
                "label": self._humanize_field_name(key),
                "before": before_value,
                "after": normalized_after,
                "rawAfter": raw_after,
                "type": self._master_edit_column_type(column),
            }
            if relation_info:
                change["relation"] = relation_info
            if before_value == normalized_after:
                unchanged.append(change)
            else:
                accepted_changes.append(change)

        if not safe_draft:
            warnings.append("draft_empty")
        if reason and len(str(reason)) > 300:
            warnings.append("reason_truncated_in_preview")
        if safe_base_values is None:
            warnings.append("base_values_missing_stale_guard_disabled")
        if stale_changes:
            warnings.append("current_value_changed_since_form_loaded")

        error_count = len(rejected_changes)
        diff_count = len(accepted_changes)
        title = getattr(row, "name", None) or getattr(row, "code", None) or f"#{safe_row_id}"
        return {
            "status": "preview_ready",
            "readOnly": True,
            "dryRun": True,
            "writeBlocked": True,
            "applyReady": error_count == 0 and diff_count > 0,
            "confirmTextRequired": self.MASTER_EDIT_APPLY_CONFIRM_TEXT,
            "allowedFields": sorted(self.MASTER_EDIT_ALLOWED_FIELDS.get(domain, set())),
            "wouldBeValid": error_count == 0,
            "domain": domain,
            "domainLabel": config["label"],
            "id": safe_row_id,
            "title": title,
            "reason": str(reason or "")[:300] if reason else None,
            "diffCount": diff_count,
            "errorCount": error_count,
            "unchangedCount": len(unchanged),
            "staleCount": len(stale_changes),
            "staleChanges": stale_changes[:30],
            "staleGuardEnabled": safe_base_values is not None,
            "acceptedChanges": accepted_changes,
            "rejectedChanges": rejected_changes,
            "unchangedChanges": unchanged[:30],
            "rawJsonReturned": False,
            "assetsReturned": False,
            "safeForAdminWriteUi": False,
            "warnings": warnings,
            "note": "편집 초안을 검증만 했습니다. 이 응답은 DB를 수정하지 않는 dry-run 결과입니다.",
        }

    async def apply_master_data_edit(
        self,
        session: AsyncSession,
        *,
        domain: str,
        row_id: int,
        draft: dict[str, Any],
        base_values: dict[str, Any] | None,
        reason: str | None,
        confirm_text: str,
        admin_user_id: int,
    ) -> dict[str, Any]:
        """Apply a guarded scalar master-data edit and write an audit log.

        This is the first real admin write path, so it intentionally supports only
        a small allow-list of scalar fields. It always validates through the same
        preview path first, requires an exact confirmation phrase, and stores before
        and after values in admin_change_logs so the next step can add rollback.
        """
        preview = await self.preview_master_data_edit(
            session,
            domain=domain,
            row_id=row_id,
            draft=draft,
            base_values=base_values,
            reason=reason,
            dry_run=True,
        )

        if str(confirm_text or "").strip() != self.MASTER_EDIT_APPLY_CONFIRM_TEXT:
            preview.update({
                "status": "confirmation_required",
                "readOnly": False,
                "dryRun": False,
                "writeBlocked": True,
                "applied": False,
                "applyReady": False,
                "errorCount": int(preview.get("errorCount") or 0) + 1,
                "wouldBeValid": False,
                "warnings": [*(preview.get("warnings") or []), "confirm_text_mismatch"],
                "note": "정확한 확인 문구를 입력해야 DB 적용이 가능합니다.",
            })
            return preview

        if not isinstance(base_values, dict) or not base_values:
            preview.update({
                "status": "stale_guard_base_values_required",
                "readOnly": False,
                "dryRun": False,
                "writeBlocked": True,
                "applied": False,
                "applyReady": False,
                "errorCount": int(preview.get("errorCount") or 0) + 1,
                "wouldBeValid": False,
                "staleGuardEnabled": False,
                "warnings": [*(preview.get("warnings") or []), "base_values_required_for_apply"],
                "note": "DB 적용에는 편집 화면을 열었을 때의 기준값(baseValues)이 필요합니다. 상세를 다시 열고 초안을 다시 적용하세요.",
            })
            return preview

        if preview.get("status") != "preview_ready" or preview.get("errorCount") or not preview.get("acceptedChanges"):
            preview.update({
                "status": "apply_rejected",
                "readOnly": False,
                "dryRun": False,
                "writeBlocked": True,
                "applied": False,
                "applyReady": False,
                "wouldBeValid": False,
                "warnings": [*(preview.get("warnings") or []), "preview_not_valid_for_apply"],
                "note": "검증 오류가 있거나 변경된 값이 없어 DB에 적용하지 않았습니다.",
            })
            return preview

        config = self.MASTER_CATALOG_DOMAINS.get(domain)
        if not config:
            preview.update({"status": "invalid_domain", "applied": False, "writeBlocked": True})
            return preview

        model = config["model"]
        result = await session.execute(select(model).where(model.id == int(row_id)))
        row = result.scalar_one_or_none()
        if row is None:
            preview.update({"status": "not_found", "applied": False, "writeBlocked": True})
            return preview

        column_map = self._master_edit_column_map(row)
        before_values: dict[str, Any] = {}
        after_values: dict[str, Any] = {}
        applied_changes: list[dict[str, Any]] = []

        for change in preview.get("acceptedChanges") or []:
            key = str(change.get("key") or "").strip()
            column = column_map.get(key)
            if not key or column is None or not self._master_edit_field_is_allowed(domain, key):
                continue
            before_values[key] = serialize_value(getattr(row, key, None))
            normalized_after, issue = self._normalize_master_edit_value(column, (draft or {}).get(key))
            if issue:
                continue
            setattr(row, key, normalized_after)
            after_values[key] = serialize_value(normalized_after)
            applied_changes.append({**change, "after": serialize_value(normalized_after)})

        if not applied_changes:
            await session.rollback()
            preview.update({
                "status": "nothing_to_apply",
                "readOnly": False,
                "dryRun": False,
                "writeBlocked": True,
                "applied": False,
                "applyReady": False,
                "warnings": [*(preview.get("warnings") or []), "no_applyable_changes"],
            })
            return preview

        title = getattr(row, "name", None) or getattr(row, "code", None) or f"#{row_id}"
        change_log = AdminChangeLog(
            admin_user_id=int(admin_user_id),
            target_type=f"master_data.{domain}",
            target_id=str(row_id),
            action="update",
            reason=str(reason or "")[:500] or None,
            before_json=before_values,
            after_json=after_values,
            rollback_json={"domain": domain, "id": int(row_id), "draft": before_values},
            applied=True,
        )
        session.add(change_log)
        await session.commit()
        await session.refresh(change_log)

        return {
            **preview,
            "status": "applied",
            "readOnly": False,
            "dryRun": False,
            "writeBlocked": False,
            "applied": True,
            "applyReady": False,
            "wouldBeValid": True,
            "title": title,
            "diffCount": len(applied_changes),
            "acceptedChanges": applied_changes,
            "changeLogId": change_log.id,
            "appliedByAdminUserId": int(admin_user_id),
            "note": "관리자 마스터 데이터 변경을 DB에 적용했고, admin_change_logs에 이력을 저장했습니다. 게임 런타임은 새로고침 후 최신 master-data를 다시 읽습니다.",
            "warnings": [*(preview.get("warnings") or []), "game_runtime_requires_reload"],
        }



    def _empty_edit_preview(
        self,
        *,
        status: str,
        domain: str,
        domain_label: str,
        row_id: int,
        warnings: list[str],
    ) -> dict[str, Any]:
        return {
            "status": status,
            "readOnly": True,
            "dryRun": True,
            "writeBlocked": True,
            "applyReady": False,
            "confirmTextRequired": self.MASTER_EDIT_APPLY_CONFIRM_TEXT,
            "allowedFields": [],
            "wouldBeValid": False,
            "domain": domain,
            "domainLabel": domain_label,
            "id": row_id,
            "title": "-",
            "reason": None,
            "diffCount": 0,
            "errorCount": 1,
            "unchangedCount": 0,
            "acceptedChanges": [],
            "rejectedChanges": [],
            "unchangedChanges": [],
            "rawJsonReturned": False,
            "assetsReturned": False,
            "safeForAdminWriteUi": False,
            "warnings": warnings,
        }

    def _master_edit_column_map(self, row: Any) -> dict[str, Any]:
        mapper = sa_inspect(row.__class__)
        return {column_attr.key: column_attr.columns[0] for column_attr in mapper.mapper.column_attrs}

    def _master_edit_field_is_readonly(self, domain: str, key: str) -> bool:
        normalized = str(key or "").lower()
        if self._master_relation_edit_field_is_open(domain, normalized):
            return False
        return (
            normalized in {"id", "created_at", "updated_at", "code"}
            or normalized.endswith("_id")
            or normalized.endswith("_code")
            or normalized.endswith("_json")
        )

    def _master_edit_field_is_allowed(self, domain: str, key: str) -> bool:
        allowed = self.MASTER_EDIT_ALLOWED_FIELDS.get(domain) or set()
        return str(key or "") in allowed

    def _master_relation_edit_field_is_open(self, domain: str, key: str) -> bool:
        relation_fields = self.MASTER_RELATION_EDIT_FIELDS.get(str(domain or "")) or set()
        return str(key or "") in relation_fields

    async def _validate_master_relation_edit_value(
        self,
        session: AsyncSession,
        domain: str,
        key: str,
        value: Any,
        row: Any,
        draft: dict[str, Any] | None = None,
        column_map: dict[str, Any] | None = None,
    ) -> str | None:
        if not self._master_relation_edit_field_is_open(domain, key) and key not in (self.MASTER_COMBO_GUARDED_FIELDS.get(domain) or set()):
            return None
        value_text = "" if value is None else str(value).strip()
        if domain == "itemTemplates" and key == "enhance_group_code":
            if not value_text:
                return None
            exists = await self._exists_by_code(session, EnhancementGroup, value_text)
            return None if exists else "relation_target_not_found_enhancement_group"
        if domain == "dropTableItems" and key == "drop_table_code":
            if not value_text:
                return "relation_target_required_drop_table"
            exists = await self._exists_by_code(session, DropTable, value_text)
            return None if exists else "relation_target_not_found_drop_table"
        if domain == "dropTableItems" and key == "item_template_code":
            if not value_text:
                return "relation_target_required_item_template"
            exists = await self._exists_by_code(session, ItemTemplate, value_text)
            return None if exists else "relation_target_not_found_item_template"
        if domain == "dropTables" and key in {"owner_type", "owner_code"}:
            proposed = self._build_proposed_combo_values(row, column_map or {}, draft or {}, ["owner_type", "owner_code"])
            if proposed.get("issue"):
                return proposed["issue"]
            owner_type = str(proposed.get("owner_type") or "").strip()
            owner_code = str(proposed.get("owner_code") or "").strip()
            if owner_type not in {"boss", "field"}:
                return "invalid_owner_type"
            if not owner_code:
                return "owner_code_missing"
            model = Boss if owner_type == "boss" else FieldZone
            exists = await self._exists_by_code(session, model, owner_code)
            return None if exists else "owner_code_not_found_for_owner_type"
        if domain == "skillLevels" and key in {"skill_code", "level"}:
            proposed = self._build_proposed_combo_values(row, column_map or {}, draft or {}, ["skill_code", "level"])
            if proposed.get("issue"):
                return proposed["issue"]
            skill_code = str(proposed.get("skill_code") or "").strip()
            level = proposed.get("level")
            if not skill_code:
                return "relation_target_required_skill"
            if not await self._exists_by_code(session, Skill, skill_code):
                return "relation_target_not_found_skill"
            if level is None or int(level) < 0:
                return "invalid_skill_level"
            duplicate = await self._exists_duplicate_combo(session, SkillLevel, int(getattr(row, "id", 0) or 0), SkillLevel.skill_code == skill_code, SkillLevel.level == int(level))
            return "duplicate_skill_code_level" if duplicate else None
        if domain == "enhancementLevels" and key in {"group_code", "from_level"}:
            proposed = self._build_proposed_combo_values(row, column_map or {}, draft or {}, ["group_code", "from_level"])
            if proposed.get("issue"):
                return proposed["issue"]
            group_code = str(proposed.get("group_code") or "").strip()
            from_level = proposed.get("from_level")
            if not group_code:
                return "relation_target_required_enhancement_group"
            if not await self._exists_by_code(session, EnhancementGroup, group_code):
                return "relation_target_not_found_enhancement_group"
            if from_level is None or int(from_level) < 0:
                return "invalid_enhancement_from_level"
            duplicate = await self._exists_duplicate_combo(session, EnhancementLevel, int(getattr(row, "id", 0) or 0), EnhancementLevel.group_code == group_code, EnhancementLevel.from_level == int(from_level))
            return "duplicate_enhancement_group_from_level" if duplicate else None
        if domain == "characterSkills" and key in {"character_code", "skill_code"}:
            proposed = self._build_proposed_combo_values(row, column_map or {}, draft or {}, ["character_code", "skill_code"])
            if proposed.get("issue"):
                return proposed["issue"]
            character_code = str(proposed.get("character_code") or "").strip()
            skill_code = str(proposed.get("skill_code") or "").strip()
            if not character_code:
                return "relation_target_required_character"
            if not skill_code:
                return "relation_target_required_skill"
            if not await self._exists_by_code(session, Character, character_code):
                return "relation_target_not_found_character"
            if not await self._exists_by_code(session, Skill, skill_code):
                return "relation_target_not_found_skill"
            duplicate = await self._exists_duplicate_combo(session, CharacterSkill, int(getattr(row, "id", 0) or 0), CharacterSkill.character_code == character_code, CharacterSkill.skill_code == skill_code)
            return "duplicate_character_skill_pair" if duplicate else None
        return None

    async def _describe_master_relation_edit_value(
        self,
        session: AsyncSession,
        domain: str,
        key: str,
        value: Any,
        row: Any | None = None,
        draft: dict[str, Any] | None = None,
        column_map: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        if not self._master_relation_edit_field_is_open(domain, key):
            return None
        value_text = "" if value is None else str(value).strip()
        if domain == "itemTemplates" and key == "enhance_group_code":
            if not value_text:
                return {"field": key, "targetDomain": "enhancementGroups", "targetCode": None, "targetLabel": "강화 그룹 없음"}
            target = await self._fetch_code_name(session, EnhancementGroup, value_text)
            return {"field": key, "targetDomain": "enhancementGroups", "targetCode": value_text, "targetLabel": target.get("name") if target else value_text}
        if domain == "dropTableItems" and key == "drop_table_code":
            target = await self._fetch_code_name(session, DropTable, value_text)
            return {"field": key, "targetDomain": "dropTables", "targetCode": value_text, "targetLabel": target.get("name") if target else value_text}
        if domain == "dropTableItems" and key == "item_template_code":
            target = await self._fetch_code_name(session, ItemTemplate, value_text)
            return {"field": key, "targetDomain": "itemTemplates", "targetCode": value_text, "targetLabel": target.get("name") if target else value_text}
        if domain == "dropTables" and key == "owner_type":
            return {"field": key, "targetDomain": "bosses" if value_text == "boss" else "fieldZones", "targetCode": value_text, "targetLabel": "보스" if value_text == "boss" else "필드"}
        if domain == "dropTables" and key == "owner_code":
            proposed = self._build_proposed_combo_values(row, column_map or {}, draft or {}, ["owner_type", "owner_code"]) if row is not None else {"owner_type": "boss", "owner_code": value_text}
            owner_type = str(proposed.get("owner_type") or "").strip()
            target_domain = "bosses" if owner_type == "boss" else "fieldZones"
            target_model = Boss if owner_type == "boss" else FieldZone
            target = await self._fetch_code_name(session, target_model, value_text)
            return {"field": key, "targetDomain": target_domain, "targetCode": value_text, "targetLabel": target.get("name") if target else value_text}
        if domain == "skillLevels" and key == "skill_code":
            target = await self._fetch_code_name(session, Skill, value_text)
            return {"field": key, "targetDomain": "skills", "targetCode": value_text, "targetLabel": target.get("name") if target else value_text}
        if domain == "enhancementLevels" and key == "group_code":
            target = await self._fetch_code_name(session, EnhancementGroup, value_text)
            return {"field": key, "targetDomain": "enhancementGroups", "targetCode": value_text, "targetLabel": target.get("name") if target else value_text}
        if domain == "characterSkills" and key == "character_code":
            target = await self._fetch_code_name(session, Character, value_text)
            return {"field": key, "targetDomain": "characters", "targetCode": value_text, "targetLabel": target.get("name") if target else value_text}
        if domain == "characterSkills" and key == "skill_code":
            target = await self._fetch_code_name(session, Skill, value_text)
            return {"field": key, "targetDomain": "skills", "targetCode": value_text, "targetLabel": target.get("name") if target else value_text}
        return None

    def _build_proposed_combo_values(self, row: Any, column_map: dict[str, Any], draft: dict[str, Any], keys: list[str]) -> dict[str, Any]:
        proposed: dict[str, Any] = {}
        for key in keys:
            if key in draft:
                column = column_map.get(key)
                if column is None:
                    return {"issue": f"combo_field_unknown_{key}"}
                normalized, issue = self._normalize_master_edit_value(column, draft.get(key))
                if issue:
                    return {"issue": f"combo_field_invalid_{key}"}
                proposed[key] = normalized
            else:
                proposed[key] = getattr(row, key, None)
        return proposed

    async def _exists_by_code(self, session: AsyncSession, model: Any, code: str) -> bool:
        if not code:
            return False
        result = await session.execute(select(func.count()).select_from(model).where(model.code == code))
        return int(result.scalar_one() or 0) > 0

    async def _fetch_code_name(self, session: AsyncSession, model: Any, code: str) -> dict[str, Any] | None:
        if not code:
            return None
        result = await session.execute(select(model).where(model.code == code))
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return {"code": getattr(row, "code", None), "name": getattr(row, "name", None) or getattr(row, "description", None)}

    async def _exists_duplicate_combo(self, session: AsyncSession, model: Any, current_id: int, *where_clauses: Any) -> bool:
        stmt = select(func.count()).select_from(model).where(*where_clauses)
        if current_id > 0:
            stmt = stmt.where(model.id != current_id)
        result = await session.execute(stmt)
        return int(result.scalar_one() or 0) > 0

    def _normalize_master_edit_value(self, column: Any, raw_value: Any) -> tuple[Any, str | None]:
        column_type = column.type
        nullable = bool(getattr(column, "nullable", False))
        if raw_value == "" or raw_value is None:
            if nullable:
                return None, None
            if isinstance(column_type, (String, Text)):
                return "", None
            return None, "empty_value_not_allowed"

        if isinstance(column_type, Boolean):
            if isinstance(raw_value, bool):
                return raw_value, None
            text = str(raw_value).strip().lower()
            if text in {"true", "1", "yes", "y", "on", "활성", "예"}:
                return True, None
            if text in {"false", "0", "no", "n", "off", "비활성", "아니오"}:
                return False, None
            return None, "invalid_boolean"

        if isinstance(column_type, Integer):
            try:
                text = str(raw_value).strip()
                if not text or any(ch in text for ch in [".", "e", "E"]):
                    return None, "invalid_integer"
                return int(text), None
            except (TypeError, ValueError):
                return None, "invalid_integer"

        if isinstance(column_type, Numeric):
            try:
                text = str(raw_value).strip().replace(",", "")
                if not text:
                    return None, "invalid_number"
                return float(text), None
            except (TypeError, ValueError):
                return None, "invalid_number"

        # For this dry-run stage, normal scalar fields are treated as text.
        text = str(raw_value)
        if text.startswith("data:"):
            return None, "asset_like_value_blocked"
        max_length = getattr(column_type, "length", None)
        if max_length and len(text) > int(max_length):
            return None, f"text_too_long_max_{max_length}"
        if len(text) > 2000:
            return None, "text_too_long_max_2000"
        return text, None

    @staticmethod
    def _master_edit_column_type(column: Any) -> str:
        column_type = column.type
        if isinstance(column_type, Boolean):
            return "boolean"
        if isinstance(column_type, Integer):
            return "integer"
        if isinstance(column_type, Numeric):
            return "number"
        if isinstance(column_type, Text):
            return "text"
        if isinstance(column_type, String):
            return "string"
        return column_type.__class__.__name__

