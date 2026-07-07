from __future__ import annotations

from typing import Any

from sqlalchemy import Boolean, Integer, Numeric, String, Text, func, inspect as sa_inspect, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
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
    User,
    UserSaveSnapshot,
)
from app.services.game_service import serialize_value


class AdminService:
    """Read-only admin preparation helpers.

    The real admin page will eventually edit DB values, but this stage deliberately
    exposes only safe diagnostics. It lets the browser/admin UI verify that master
    data and save snapshots are visible from FastAPI without adding any write path.
    """

    MASTER_DATA_MODELS: tuple[tuple[str, Any], ...] = (
        ("characters", Character),
        ("skills", Skill),
        ("characterSkills", CharacterSkill),
        ("skillLevels", SkillLevel),
        ("itemTemplates", ItemTemplate),
        ("bosses", Boss),
        ("dropTables", DropTable),
        ("dropTableItems", DropTableItem),
        ("fieldZones", FieldZone),
        ("enhancementGroups", EnhancementGroup),
        ("enhancementLevels", EnhancementLevel),
    )

    MASTER_CATALOG_DOMAINS: dict[str, dict[str, Any]] = {
        "itemTemplates": {
            "label": "아이템 템플릿",
            "model": ItemTemplate,
            "search": ("code", "name", "item_type", "grade", "equip_slot", "enhance_group_code", "admin_note"),
            "defaultSort": "code_asc",
            "description": "장비/재료/강화권 등 아이템 기준 데이터",
        },
        "skills": {
            "label": "스킬",
            "model": Skill,
            "search": ("code", "name", "slot_key", "description"),
            "defaultSort": "code_asc",
            "description": "Q/W 스킬과 발동 확률/쿨타임 기준 데이터",
        },
        "skillLevels": {
            "label": "스킬 레벨",
            "model": SkillLevel,
            "search": ("skill_code",),
            "defaultSort": "id_asc",
            "description": "스킬 강화 단계별 배율/발동 보너스",
        },
        "bosses": {
            "label": "보스",
            "model": Boss,
            "search": ("code", "name", "boss_type", "description"),
            "defaultSort": "code_asc",
            "description": "일반/특수 보스 기준 데이터",
        },
        "fieldZones": {
            "label": "필드",
            "model": FieldZone,
            "search": ("code", "name", "description"),
            "defaultSort": "sort_asc",
            "description": "사냥 필드와 보상 기준 데이터",
        },
        "characters": {
            "label": "캐릭터",
            "model": Character,
            "search": ("code", "name", "description"),
            "defaultSort": "code_asc",
            "description": "캐릭터 기준 데이터",
        },
        "dropTables": {
            "label": "드랍 테이블",
            "model": DropTable,
            "search": ("code", "owner_type", "owner_code", "description"),
            "defaultSort": "code_asc",
            "description": "보스/필드별 드랍 묶음",
        },
        "dropTableItems": {
            "label": "드랍 아이템",
            "model": DropTableItem,
            "search": ("drop_table_code", "item_template_code"),
            "defaultSort": "id_asc",
            "description": "드랍 테이블 안의 아이템과 확률",
        },
        "enhancementGroups": {
            "label": "강화 그룹",
            "model": EnhancementGroup,
            "search": ("code", "name", "description"),
            "defaultSort": "code_asc",
            "description": "강화 방식 묶음",
        },
        "enhancementLevels": {
            "label": "강화 단계",
            "model": EnhancementLevel,
            "search": ("group_code",),
            "defaultSort": "id_asc",
            "description": "강화 단계별 확률/비용/결과",
        },
        "characterSkills": {
            "label": "캐릭터 스킬 연결",
            "model": CharacterSkill,
            "search": ("character_code", "skill_code"),
            "defaultSort": "id_asc",
            "description": "캐릭터별 기본 스킬 연결",
        },
    }

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


    async def preview_master_data_edit(
        self,
        session: AsyncSession,
        *,
        domain: str,
        row_id: int,
        draft: dict[str, Any],
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

        column_map = self._master_edit_column_map(row)
        accepted_changes: list[dict[str, Any]] = []
        unchanged: list[dict[str, Any]] = []
        rejected_changes: list[dict[str, Any]] = []
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

            if self._master_edit_field_is_readonly(key):
                rejected_changes.append({"key": key, "label": self._humanize_field_name(key), "reason": "read_only_field"})
                continue
            if key.endswith("_json"):
                rejected_changes.append({"key": key, "label": self._humanize_field_name(key), "reason": "json_edit_not_enabled_yet"})
                continue
            if self._is_asset_field(key):
                rejected_changes.append({"key": key, "label": self._humanize_field_name(key), "reason": "asset_edit_not_enabled_yet"})
                continue

            before_value = serialize_value(getattr(row, key, None))
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

            normalized_after = serialize_value(normalized_after)
            change = {
                "key": key,
                "label": self._humanize_field_name(key),
                "before": before_value,
                "after": normalized_after,
                "rawAfter": raw_after,
                "type": self._master_edit_column_type(column),
            }
            if before_value == normalized_after:
                unchanged.append(change)
            else:
                accepted_changes.append(change)

        if not safe_draft:
            warnings.append("draft_empty")
        if reason and len(str(reason)) > 300:
            warnings.append("reason_truncated_in_preview")

        error_count = len(rejected_changes)
        diff_count = len(accepted_changes)
        title = getattr(row, "name", None) or getattr(row, "code", None) or f"#{safe_row_id}"
        return {
            "status": "preview_ready",
            "readOnly": True,
            "dryRun": True,
            "writeBlocked": True,
            "wouldBeValid": error_count == 0,
            "domain": domain,
            "domainLabel": config["label"],
            "id": safe_row_id,
            "title": title,
            "reason": str(reason or "")[:300] if reason else None,
            "diffCount": diff_count,
            "errorCount": error_count,
            "unchangedCount": len(unchanged),
            "acceptedChanges": accepted_changes,
            "rejectedChanges": rejected_changes,
            "unchangedChanges": unchanged[:30],
            "rawJsonReturned": False,
            "assetsReturned": False,
            "safeForAdminWriteUi": False,
            "warnings": warnings,
            "note": "편집 초안을 검증만 했습니다. 이 응답은 DB를 수정하지 않는 dry-run 결과입니다.",
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

    @staticmethod
    def _master_edit_field_is_readonly(key: str) -> bool:
        normalized = str(key or "").lower()
        return normalized in {"id", "created_at", "updated_at"} or normalized.endswith("_id")

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

    async def get_readonly_overview(self, session: AsyncSession, *, admin_user_id: int, admin_username: str) -> dict[str, Any]:
        """Return a safe admin dashboard summary without returning raw save JSON."""
        master_counts = await self._get_master_data_counts(session)
        save_snapshot_summary = await self._get_save_snapshot_summary(session)
        user_summary = await self._get_user_summary(session)
        readiness = self._build_readiness(master_counts, save_snapshot_summary)

        return {
            "status": "loaded",
            "readOnly": True,
            "admin": {
                "userId": admin_user_id,
                "username": admin_username,
                "authMode": "placeholder-local-dev",
            },
            "masterData": master_counts,
            "saveSnapshots": save_snapshot_summary,
            "users": user_summary,
            "readiness": readiness,
            "nextRecommendedStep": "관리자 화면에서는 먼저 overview/save-snapshots처럼 조회 전용 API로 DB 상태를 확인한 뒤, 변경 미리보기와 변경 이력을 붙이는 순서가 안전합니다.",
        }

    async def list_save_snapshot_summaries(
        self,
        session: AsyncSession,
        *,
        limit: int = 20,
        user_id: int | None = None,
        slot_key: str | None = None,
        source: str | None = None,
        default_only: bool = False,
        sort: str = "updated_desc",
    ) -> dict[str, Any]:
        """List recent save snapshots for admin diagnostics without raw snapshots.

        The filters are intentionally metadata-only. Even when a single snapshot is
        selected, snapshot_json is not returned to the browser.
        """
        filters = self._build_snapshot_filters(
            user_id=user_id,
            slot_key=slot_key,
            source=source,
            default_only=default_only,
            sort=sort,
        )
        where_clauses = self._build_snapshot_where_clauses(filters)
        safe_limit = filters["limit"] = max(1, min(int(limit or 20), 100))

        stmt = select(UserSaveSnapshot)
        if where_clauses:
            stmt = stmt.where(*where_clauses)
        stmt = stmt.order_by(*self._snapshot_order_by(filters["sort"])).limit(safe_limit)

        result = await session.execute(stmt)
        rows = result.scalars().all()
        total_all = await self._count(session, UserSaveSnapshot)
        total_filtered = await self._count_save_snapshots(session, where_clauses)
        snapshots = [self._serialize_save_snapshot_summary(row) for row in rows]
        return {
            "status": "loaded",
            "readOnly": True,
            "limit": safe_limit,
            "count": len(snapshots),
            "total": total_filtered,
            "totalAll": total_all,
            "filters": filters,
            "snapshots": snapshots,
            "rawSnapshotReturned": False,
            "note": "관리자 준비용 조회 전용 목록입니다. 필터를 써도 snapshot_json 원본은 내려주지 않습니다.",
        }


    async def list_master_catalog_domains(self, session: AsyncSession) -> dict[str, Any]:
        """Return editable master-data domains for the admin page without row payloads."""
        domains: list[dict[str, Any]] = []
        for key, config in self.MASTER_CATALOG_DOMAINS.items():
            model = config["model"]
            total = await self._count(session, model)
            item: dict[str, Any] = {
                "key": key,
                "label": config["label"],
                "description": config.get("description"),
                "total": total,
                "searchableFields": list(config.get("search") or ()),
                "defaultSort": config.get("defaultSort") or "id_asc",
                "supportsEnabledFilter": hasattr(model, "is_enabled"),
                "rawJsonReturned": False,
                "assetsReturned": False,
            }
            if hasattr(model, "is_enabled"):
                enabled = await self._count(session, model, where_clause=(model.is_enabled.is_(True)))
                item["enabled"] = enabled
                item["disabled"] = max(0, int(total or 0) - int(enabled or 0))
            domains.append(item)
        return {
            "status": "loaded",
            "readOnly": True,
            "count": len(domains),
            "domains": domains,
            "defaultDomain": "itemTemplates",
            "rawJsonReturned": False,
            "assetsReturned": False,
            "note": "관리자 편집 화면 준비용 마스터 데이터 도메인 목록입니다. 아직 조회 전용입니다.",
        }

    async def list_master_catalog_rows(
        self,
        session: AsyncSession,
        *,
        domain: str = "itemTemplates",
        limit: int = 50,
        query: str | None = None,
        enabled: str = "all",
        sort: str | None = None,
    ) -> dict[str, Any]:
        """List safe master-data rows for the admin page.

        This intentionally returns compact row cells instead of raw model JSON or
        inline assets. It is a bolder admin-page step, but still read-only.
        """
        config = self.MASTER_CATALOG_DOMAINS.get(domain)
        if not config:
            return {
                "status": "invalid_domain",
                "readOnly": True,
                "domain": domain,
                "domainLabel": domain,
                "count": 0,
                "total": 0,
                "limit": 0,
                "filters": {"domain": domain, "warnings": ["domain_invalid"]},
                "columns": [],
                "rows": [],
                "rawJsonReturned": False,
                "assetsReturned": False,
            }

        model = config["model"]
        warnings: list[str] = []
        safe_limit = max(1, min(int(limit or 50), 200))
        safe_query = self._clean_filter_text(query)
        if safe_query and len(safe_query) > 80:
            safe_query = safe_query[:80]
            warnings.append("query_truncated_80")
        safe_enabled = enabled if enabled in {"all", "enabled", "disabled"} else "all"
        if safe_enabled != enabled:
            warnings.append("enabled_filter_fallback_all")
        safe_sort = sort or config.get("defaultSort") or "id_asc"
        if safe_sort not in {"code_asc", "name_asc", "updated_desc", "id_asc", "sort_asc"}:
            warnings.append("sort_fallback_default")
            safe_sort = config.get("defaultSort") or "id_asc"

        where_clauses = self._build_master_catalog_where_clauses(model, config, safe_query, safe_enabled, warnings)
        total_all = await self._count(session, model)
        total_filtered = await self._count_master_catalog_rows(session, model, where_clauses)

        stmt = select(model)
        if where_clauses:
            stmt = stmt.where(*where_clauses)
        stmt = stmt.order_by(*self._master_catalog_order_by(model, safe_sort)).limit(safe_limit)
        result = await session.execute(stmt)
        rows = [self._serialize_master_catalog_row(domain, row) for row in result.scalars().all()]

        return {
            "status": "loaded",
            "readOnly": True,
            "domain": domain,
            "domainLabel": config["label"],
            "description": config.get("description"),
            "limit": safe_limit,
            "count": len(rows),
            "total": total_filtered,
            "totalAll": total_all,
            "filters": {
                "domain": domain,
                "query": safe_query,
                "enabled": safe_enabled,
                "sort": safe_sort,
                "warnings": warnings,
                "hasActiveFilters": bool(safe_query or safe_enabled != "all"),
            },
            "columns": self._master_catalog_columns(domain),
            "rows": rows,
            "rawJsonReturned": False,
            "assetsReturned": False,
            "note": "관리자 마스터 데이터 카탈로그 조회 전용 목록입니다. 원본 JSON과 이미지 data URL은 내려주지 않습니다.",
        }


    async def get_master_catalog_detail(
        self,
        session: AsyncSession,
        *,
        domain: str = "itemTemplates",
        row_id: int,
    ) -> dict[str, Any]:
        """Return one sanitized master-data row for the read-only admin detail panel.

        This is intentionally not an edit endpoint. It returns normal scalar fields
        and sanitized JSON previews, but it hides inline image/data URL assets and
        still marks the response as read-only.
        """
        config = self.MASTER_CATALOG_DOMAINS.get(domain)
        if not config:
            return {
                "status": "invalid_domain",
                "readOnly": True,
                "domain": domain,
                "domainLabel": domain,
                "id": row_id,
                "title": "-",
                "fields": [],
                "jsonFields": [],
                "assetFields": [],
                "relationHints": [],
                "rawJsonReturned": False,
                "sanitizedJsonReturned": False,
                "assetsReturned": False,
                "safeForAdminWriteUi": False,
                "warnings": ["domain_invalid"],
            }

        model = config["model"]
        safe_row_id = int(row_id or 0)
        if safe_row_id <= 0:
            return {
                "status": "invalid_id",
                "readOnly": True,
                "domain": domain,
                "domainLabel": config["label"],
                "id": row_id,
                "title": "-",
                "fields": [],
                "jsonFields": [],
                "assetFields": [],
                "relationHints": [],
                "rawJsonReturned": False,
                "sanitizedJsonReturned": False,
                "assetsReturned": False,
                "safeForAdminWriteUi": False,
                "warnings": ["id_invalid"],
            }

        result = await session.execute(select(model).where(model.id == safe_row_id))
        row = result.scalar_one_or_none()
        if row is None:
            return {
                "status": "not_found",
                "readOnly": True,
                "domain": domain,
                "domainLabel": config["label"],
                "id": safe_row_id,
                "title": "-",
                "fields": [],
                "jsonFields": [],
                "assetFields": [],
                "relationHints": [],
                "rawJsonReturned": False,
                "sanitizedJsonReturned": False,
                "assetsReturned": False,
                "safeForAdminWriteUi": False,
                "warnings": ["row_not_found"],
            }

        scalar_fields, asset_fields = self._serialize_master_detail_scalar_fields(row)
        json_fields = self._serialize_master_detail_json_fields(row)
        relation_hints = await self._build_master_detail_relation_hints(session, domain, row)
        title = getattr(row, "name", None) or getattr(row, "code", None) or f"#{safe_row_id}"
        asset_hidden_count = sum(int(field.get("hiddenAssetCount") or 0) for field in json_fields)
        asset_hidden_count += sum(1 for field in asset_fields if field.get("hidden"))
        warnings: list[str] = []
        if asset_hidden_count:
            warnings.append("assets_hidden")
        if any(field.get("truncatedCount") for field in json_fields):
            warnings.append("json_preview_truncated")

        return {
            "status": "loaded",
            "readOnly": True,
            "domain": domain,
            "domainLabel": config["label"],
            "description": config.get("description"),
            "id": safe_row_id,
            "title": title,
            "fields": scalar_fields,
            "jsonFields": json_fields,
            "assetFields": asset_fields,
            "relationHints": relation_hints,
            "rawJsonReturned": False,
            "sanitizedJsonReturned": True,
            "assetsReturned": False,
            "safeForAdminWriteUi": False,
            "warnings": warnings,
            "note": "관리자 상세 보기 준비용 조회 전용 응답입니다. JSON은 안전하게 축약/마스킹되며 이미지 data URL은 내려주지 않습니다.",
        }

    async def get_master_catalog_relations(
        self,
        session: AsyncSession,
        *,
        domain: str = "itemTemplates",
        row_id: int,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Return compact related rows for one master-data record.

        This keeps the admin page read-only while making the catalog more useful:
        an admin can click one row and immediately see the connected drop tables,
        skills, enhancement rules, or item templates without exposing raw JSON or
        image assets.
        """
        config = self.MASTER_CATALOG_DOMAINS.get(domain)
        if not config:
            return self._empty_relation_response(
                status="invalid_domain",
                domain=domain,
                domain_label=domain,
                row_id=row_id,
                warnings=["domain_invalid"],
            )

        safe_row_id = int(row_id or 0)
        if safe_row_id <= 0:
            return self._empty_relation_response(
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
            return self._empty_relation_response(
                status="not_found",
                domain=domain,
                domain_label=config["label"],
                row_id=safe_row_id,
                warnings=["row_not_found"],
            )

        safe_limit = max(1, min(int(limit or 20), 80))
        groups = await self._build_master_relation_groups(session, domain, row, limit=safe_limit)
        total_related_rows = sum(int(group.get("count") or 0) for group in groups)
        title = getattr(row, "name", None) or getattr(row, "code", None) or f"#{safe_row_id}"
        return {
            "status": "loaded",
            "readOnly": True,
            "domain": domain,
            "domainLabel": config["label"],
            "id": safe_row_id,
            "title": title,
            "limitPerGroup": safe_limit,
            "groupCount": len(groups),
            "totalRelatedRows": total_related_rows,
            "groups": groups,
            "rawJsonReturned": False,
            "assetsReturned": False,
            "safeForAdminWriteUi": False,
            "warnings": [],
            "note": "관리자 상세 보기의 연결 항목 조회 전용 응답입니다. 관련 행은 축약된 목록으로만 내려갑니다.",
        }

    def _empty_relation_response(
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
            "domain": domain,
            "domainLabel": domain_label,
            "id": row_id,
            "title": "-",
            "limitPerGroup": 0,
            "groupCount": 0,
            "totalRelatedRows": 0,
            "groups": [],
            "rawJsonReturned": False,
            "assetsReturned": False,
            "safeForAdminWriteUi": False,
            "warnings": warnings,
        }

    async def _build_master_relation_groups(self, session: AsyncSession, domain: str, row: Any, *, limit: int) -> list[dict[str, Any]]:
        groups: list[dict[str, Any]] = []
        code = getattr(row, "code", None)

        if domain == "itemTemplates" and code:
            groups.append(await self._fetch_master_relation_group(session, "드랍 아이템", "dropTableItems", DropTableItem, limit, DropTableItem.item_template_code == code))
            group_code = getattr(row, "enhance_group_code", None)
            if group_code:
                groups.append(await self._fetch_master_relation_group(session, "강화 그룹", "enhancementGroups", EnhancementGroup, limit, EnhancementGroup.code == group_code))
                groups.append(await self._fetch_master_relation_group(session, "강화 단계", "enhancementLevels", EnhancementLevel, limit, EnhancementLevel.group_code == group_code))
        elif domain == "skills" and code:
            groups.append(await self._fetch_master_relation_group(session, "스킬 레벨", "skillLevels", SkillLevel, limit, SkillLevel.skill_code == code))
            groups.append(await self._fetch_master_relation_group(session, "캐릭터 스킬 연결", "characterSkills", CharacterSkill, limit, CharacterSkill.skill_code == code))
        elif domain == "skillLevels":
            skill_code = getattr(row, "skill_code", None)
            if skill_code:
                groups.append(await self._fetch_master_relation_group(session, "상위 스킬", "skills", Skill, limit, Skill.code == skill_code))
        elif domain == "characters" and code:
            groups.append(await self._fetch_master_relation_group(session, "캐릭터 스킬 연결", "characterSkills", CharacterSkill, limit, CharacterSkill.character_code == code))
        elif domain == "characterSkills":
            character_code = getattr(row, "character_code", None)
            skill_code = getattr(row, "skill_code", None)
            if character_code:
                groups.append(await self._fetch_master_relation_group(session, "캐릭터", "characters", Character, limit, Character.code == character_code))
            if skill_code:
                groups.append(await self._fetch_master_relation_group(session, "스킬", "skills", Skill, limit, Skill.code == skill_code))
        elif domain == "bosses" and code:
            groups.append(await self._fetch_master_relation_group(session, "보스 드랍 테이블", "dropTables", DropTable, limit, DropTable.owner_type == "boss", DropTable.owner_code == code))
        elif domain == "fieldZones" and code:
            groups.append(await self._fetch_master_relation_group(session, "필드 드랍 테이블", "dropTables", DropTable, limit, DropTable.owner_type == "field", DropTable.owner_code == code))
        elif domain == "dropTables" and code:
            owner_type = getattr(row, "owner_type", None)
            owner_code = getattr(row, "owner_code", None)
            if owner_type == "boss" and owner_code:
                groups.append(await self._fetch_master_relation_group(session, "대상 보스", "bosses", Boss, limit, Boss.code == owner_code))
            if owner_type == "field" and owner_code:
                groups.append(await self._fetch_master_relation_group(session, "대상 필드", "fieldZones", FieldZone, limit, FieldZone.code == owner_code))
            groups.append(await self._fetch_master_relation_group(session, "드랍 아이템", "dropTableItems", DropTableItem, limit, DropTableItem.drop_table_code == code))
        elif domain == "dropTableItems":
            drop_table_code = getattr(row, "drop_table_code", None)
            item_template_code = getattr(row, "item_template_code", None)
            if drop_table_code:
                groups.append(await self._fetch_master_relation_group(session, "드랍 테이블", "dropTables", DropTable, limit, DropTable.code == drop_table_code))
            if item_template_code:
                groups.append(await self._fetch_master_relation_group(session, "아이템 템플릿", "itemTemplates", ItemTemplate, limit, ItemTemplate.code == item_template_code))
        elif domain == "enhancementGroups" and code:
            groups.append(await self._fetch_master_relation_group(session, "강화 단계", "enhancementLevels", EnhancementLevel, limit, EnhancementLevel.group_code == code))
            groups.append(await self._fetch_master_relation_group(session, "연결 아이템", "itemTemplates", ItemTemplate, limit, ItemTemplate.enhance_group_code == code))
        elif domain == "enhancementLevels":
            group_code = getattr(row, "group_code", None)
            if group_code:
                groups.append(await self._fetch_master_relation_group(session, "강화 그룹", "enhancementGroups", EnhancementGroup, limit, EnhancementGroup.code == group_code))
                groups.append(await self._fetch_master_relation_group(session, "연결 아이템", "itemTemplates", ItemTemplate, limit, ItemTemplate.enhance_group_code == group_code))

        return [group for group in groups if group.get("count") or group.get("rows")]

    async def _fetch_master_relation_group(
        self,
        session: AsyncSession,
        label: str,
        domain: str,
        model: Any,
        limit: int,
        *where_clauses: Any,
    ) -> dict[str, Any]:
        where_list = [clause for clause in where_clauses if clause is not None]
        total = await self._count_master_catalog_rows(session, model, where_list)
        config = self.MASTER_CATALOG_DOMAINS.get(domain) or {}
        sort = config.get("defaultSort") or "id_asc"
        stmt = select(model)
        if where_list:
            stmt = stmt.where(*where_list)
        stmt = stmt.order_by(*self._master_catalog_order_by(model, sort)).limit(limit)
        result = await session.execute(stmt)
        rows = [self._serialize_master_relation_row(domain, row) for row in result.scalars().all()]
        return {
            "label": label,
            "domain": domain,
            "domainLabel": config.get("label") or domain,
            "count": total,
            "shown": len(rows),
            "limited": total > len(rows),
            "columns": self._master_catalog_columns(domain),
            "rows": rows,
            "rawJsonReturned": False,
            "assetsReturned": False,
        }

    def _serialize_master_relation_row(self, domain: str, row: Any) -> dict[str, Any]:
        catalog_row = self._serialize_master_catalog_row(domain, row)
        cells = catalog_row.get("cells") or {}
        title = getattr(row, "name", None) or getattr(row, "code", None) or f"#{getattr(row, 'id', '-') }"
        return {
            "id": getattr(row, "id", None),
            "domain": domain,
            "title": title,
            "cells": cells,
            "rawJsonReturned": False,
            "assetsReturned": False,
        }

    async def _get_master_data_counts(self, session: AsyncSession) -> dict[str, Any]:
        counts: dict[str, Any] = {}
        for key, model in self.MASTER_DATA_MODELS:
            item = {"total": await self._count(session, model)}
            if hasattr(model, "is_enabled"):
                item["enabled"] = await self._count(session, model, where_clause=(model.is_enabled.is_(True)))
                item["disabled"] = max(0, int(item["total"] or 0) - int(item["enabled"] or 0))
            counts[key] = item
        counts["summary"] = {
            "domains": len(self.MASTER_DATA_MODELS),
            "totalRows": sum(int(value.get("total") or 0) for value in counts.values() if isinstance(value, dict)),
        }
        return counts

    async def _get_save_snapshot_summary(self, session: AsyncSession) -> dict[str, Any]:
        total = await self._count(session, UserSaveSnapshot)
        default_count = await self._count(session, UserSaveSnapshot, where_clause=(UserSaveSnapshot.slot_key == "default"))
        users_with_saves_result = await session.execute(select(func.count(func.distinct(UserSaveSnapshot.user_id))))
        users_with_saves = int(users_with_saves_result.scalar_one() or 0)
        latest_result = await session.execute(select(func.max(UserSaveSnapshot.updated_at)))
        latest_updated_at = latest_result.scalar_one_or_none()
        return {
            "totalSlots": total,
            "usersWithSaves": users_with_saves,
            "defaultSlots": default_count,
            "nonDefaultSlots": max(0, int(total or 0) - int(default_count or 0)),
            "latestUpdatedAt": serialize_value(latest_updated_at),
            "rawSnapshotReturned": False,
        }

    async def _get_user_summary(self, session: AsyncSession) -> dict[str, Any]:
        total = await self._count(session, User)
        active = await self._count(session, User, where_clause=(User.is_active.is_(True)))
        admins = await self._count(session, User, where_clause=(User.is_admin.is_(True)))
        return {"total": total, "active": active, "admins": admins}

    def _build_snapshot_filters(
        self,
        *,
        user_id: int | None,
        slot_key: str | None,
        source: str | None,
        default_only: bool,
        sort: str,
    ) -> dict[str, Any]:
        warnings: list[str] = []
        safe_sort = sort if sort in {"updated_desc", "updated_asc", "user_asc", "slot_asc"} else "updated_desc"
        if safe_sort != sort:
            warnings.append("sort_fallback_updated_desc")

        safe_user_id = None
        if user_id is not None:
            try:
                parsed_user_id = int(user_id)
                if parsed_user_id >= 1:
                    safe_user_id = parsed_user_id
                else:
                    warnings.append("userId_ignored_invalid")
            except (TypeError, ValueError):
                warnings.append("userId_ignored_invalid")

        safe_slot_key = self._clean_filter_text(slot_key)
        if safe_slot_key and not self._is_safe_slot_key(safe_slot_key):
            warnings.append("slotKey_ignored_unsafe")
            safe_slot_key = None

        safe_source = self._clean_filter_text(source)
        if default_only:
            if safe_slot_key and safe_slot_key != "default":
                warnings.append("slotKey_ignored_because_defaultOnly")
            safe_slot_key = "default"

        active = {
            "userId": safe_user_id,
            "slotKey": safe_slot_key,
            "source": safe_source,
            "defaultOnly": bool(default_only),
            "sort": safe_sort,
            "warnings": warnings,
        }
        active["hasActiveFilters"] = any(
            active.get(key) not in (None, "", False) for key in ("userId", "slotKey", "source", "defaultOnly")
        )
        return active

    def _build_snapshot_where_clauses(self, filters: dict[str, Any]) -> list[Any]:
        clauses: list[Any] = []
        if filters.get("userId") is not None:
            clauses.append(UserSaveSnapshot.user_id == int(filters["userId"]))
        if filters.get("slotKey"):
            clauses.append(UserSaveSnapshot.slot_key == filters["slotKey"])
        if filters.get("source"):
            clauses.append(UserSaveSnapshot.source == filters["source"])
        return clauses

    def _snapshot_order_by(self, sort: str) -> tuple[Any, ...]:
        if sort == "updated_asc":
            return (UserSaveSnapshot.updated_at.asc(), UserSaveSnapshot.user_id, UserSaveSnapshot.slot_key)
        if sort == "user_asc":
            return (UserSaveSnapshot.user_id.asc(), UserSaveSnapshot.slot_key.asc(), UserSaveSnapshot.updated_at.desc())
        if sort == "slot_asc":
            return (UserSaveSnapshot.slot_key.asc(), UserSaveSnapshot.user_id.asc(), UserSaveSnapshot.updated_at.desc())
        return (UserSaveSnapshot.updated_at.desc(), UserSaveSnapshot.user_id, UserSaveSnapshot.slot_key)

    async def _count_save_snapshots(self, session: AsyncSession, where_clauses: list[Any]) -> int:
        stmt = select(func.count()).select_from(UserSaveSnapshot)
        if where_clauses:
            stmt = stmt.where(*where_clauses)
        result = await session.execute(stmt)
        return int(result.scalar_one() or 0)

    @staticmethod
    def _clean_filter_text(value: Any) -> str | None:
        if value is None:
            return None
        cleaned = str(value).strip()
        return cleaned or None

    @staticmethod
    def _is_safe_slot_key(value: str) -> bool:
        allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
        return all(ch in allowed for ch in value)


    def _build_master_catalog_where_clauses(
        self,
        model: Any,
        config: dict[str, Any],
        query: str | None,
        enabled: str,
        warnings: list[str],
    ) -> list[Any]:
        clauses: list[Any] = []
        if query:
            search_clauses = []
            for field in config.get("search") or ():
                column = getattr(model, field, None)
                if column is not None:
                    search_clauses.append(column.ilike(f"%{query}%"))
            if search_clauses:
                clauses.append(or_(*search_clauses))
            else:
                warnings.append("query_ignored_no_searchable_fields")
        if enabled != "all":
            if hasattr(model, "is_enabled"):
                clauses.append(model.is_enabled.is_(enabled == "enabled"))
            else:
                warnings.append("enabled_filter_ignored_for_domain")
        return clauses

    def _master_catalog_order_by(self, model: Any, sort: str) -> tuple[Any, ...]:
        if sort == "code_asc" and hasattr(model, "code"):
            return (model.code.asc(), model.id.asc())
        if sort == "name_asc" and hasattr(model, "name"):
            return (model.name.asc(), model.id.asc())
        if sort == "updated_desc" and hasattr(model, "updated_at"):
            return (model.updated_at.desc(), model.id.asc())
        if sort == "sort_asc" and hasattr(model, "sort_order"):
            return (model.sort_order.asc(), model.id.asc())
        return (model.id.asc(),)

    async def _count_master_catalog_rows(self, session: AsyncSession, model: Any, where_clauses: list[Any]) -> int:
        stmt = select(func.count()).select_from(model)
        if where_clauses:
            stmt = stmt.where(*where_clauses)
        result = await session.execute(stmt)
        return int(result.scalar_one() or 0)

    def _master_catalog_columns(self, domain: str) -> list[dict[str, str]]:
        column_map: dict[str, list[tuple[str, str]]] = {
            "itemTemplates": [("id", "ID"), ("code", "코드"), ("name", "이름"), ("itemType", "타입"), ("grade", "등급"), ("equipSlot", "장착칸"), ("stackable", "중첩"), ("enhanceGroupCode", "강화그룹"), ("jsonKeys", "JSON 키"), ("updatedAt", "수정")],
            "skills": [("id", "ID"), ("code", "코드"), ("name", "이름"), ("slotKey", "슬롯"), ("procRate", "발동"), ("cooldownSeconds", "쿨타임"), ("jsonKeys", "JSON 키"), ("updatedAt", "수정")],
            "skillLevels": [("id", "ID"), ("skillCode", "스킬"), ("level", "레벨"), ("damageMultiplier", "배율"), ("procRateBonus", "발동+"), ("jsonKeys", "JSON 키"), ("updatedAt", "수정")],
            "bosses": [("id", "ID"), ("code", "코드"), ("name", "이름"), ("tier", "티어"), ("bossType", "타입"), ("hp", "HP"), ("cooldownSeconds", "쿨타임"), ("isEnabled", "활성"), ("jsonKeys", "JSON 키"), ("updatedAt", "수정")],
            "fieldZones": [("id", "ID"), ("code", "코드"), ("name", "이름"), ("sortOrder", "순서"), ("enemyHp", "HP"), ("goldReward", "골드"), ("isEnabled", "활성"), ("jsonKeys", "JSON 키"), ("updatedAt", "수정")],
            "characters": [("id", "ID"), ("code", "코드"), ("name", "이름"), ("isEnabled", "활성"), ("jsonKeys", "JSON 키"), ("updatedAt", "수정")],
            "dropTables": [("id", "ID"), ("code", "코드"), ("ownerType", "대상"), ("ownerCode", "대상코드"), ("isEnabled", "활성"), ("jsonKeys", "JSON 키"), ("updatedAt", "수정")],
            "dropTableItems": [("id", "ID"), ("dropTableCode", "테이블"), ("itemTemplateCode", "아이템"), ("rate", "확률"), ("minQuantity", "최소"), ("maxQuantity", "최대"), ("jsonKeys", "JSON 키"), ("updatedAt", "수정")],
            "enhancementGroups": [("id", "ID"), ("code", "코드"), ("name", "이름"), ("maxLevel", "최대"), ("isEnabled", "활성"), ("jsonKeys", "JSON 키"), ("updatedAt", "수정")],
            "enhancementLevels": [("id", "ID"), ("groupCode", "그룹"), ("fromLevel", "시작"), ("toLevel", "도착"), ("successRate", "확률"), ("goldCost", "비용"), ("jsonKeys", "JSON 키"), ("updatedAt", "수정")],
            "characterSkills": [("id", "ID"), ("characterCode", "캐릭터"), ("skillCode", "스킬"), ("sortOrder", "순서"), ("isDefault", "기본"), ("updatedAt", "수정")],
        }
        return [{"key": key, "label": label} for key, label in column_map.get(domain, [("id", "ID"), ("updatedAt", "수정")])]

    def _serialize_master_catalog_row(self, domain: str, row: Any) -> dict[str, Any]:
        cells: dict[str, Any]
        if domain == "itemTemplates":
            cells = {
                "id": row.id,
                "code": row.code,
                "name": row.name,
                "itemType": row.item_type,
                "grade": row.grade,
                "equipSlot": row.equip_slot,
                "stackable": row.stackable,
                "enhanceGroupCode": row.enhance_group_code,
                "jsonKeys": self._join_json_keys({"baseStats": row.base_stats_json, "options": row.options_json}),
                "updatedAt": serialize_value(row.updated_at),
            }
        elif domain == "skills":
            cells = {"id": row.id, "code": row.code, "name": row.name, "slotKey": row.slot_key, "procRate": serialize_value(row.proc_rate), "cooldownSeconds": row.cooldown_seconds, "jsonKeys": self._join_json_keys({"options": row.options_json}), "updatedAt": serialize_value(row.updated_at)}
        elif domain == "skillLevels":
            cells = {"id": row.id, "skillCode": row.skill_code, "level": row.level, "damageMultiplier": serialize_value(row.damage_multiplier), "procRateBonus": serialize_value(row.proc_rate_bonus), "jsonKeys": self._join_json_keys({"options": row.options_json}), "updatedAt": serialize_value(row.updated_at)}
        elif domain == "bosses":
            cells = {"id": row.id, "code": row.code, "name": row.name, "tier": row.tier, "bossType": row.boss_type, "hp": serialize_value(row.hp), "cooldownSeconds": row.cooldown_seconds, "isEnabled": row.is_enabled, "jsonKeys": self._join_json_keys({"summonRules": row.summon_rules_json}), "updatedAt": serialize_value(row.updated_at)}
        elif domain == "fieldZones":
            cells = {"id": row.id, "code": row.code, "name": row.name, "sortOrder": row.sort_order, "enemyHp": serialize_value(row.enemy_hp), "goldReward": serialize_value(row.gold_reward), "isEnabled": row.is_enabled, "jsonKeys": self._join_json_keys({"entryRules": row.entry_rules_json, "farmRules": row.farm_rules_json}), "updatedAt": serialize_value(row.updated_at)}
        elif domain == "characters":
            cells = {"id": row.id, "code": row.code, "name": row.name, "isEnabled": row.is_enabled, "jsonKeys": self._join_json_keys({"meta": row.meta_json}), "updatedAt": serialize_value(row.updated_at)}
        elif domain == "dropTables":
            cells = {"id": row.id, "code": row.code, "ownerType": row.owner_type, "ownerCode": row.owner_code, "isEnabled": row.is_enabled, "jsonKeys": self._join_json_keys({"rules": row.rules_json}), "updatedAt": serialize_value(row.updated_at)}
        elif domain == "dropTableItems":
            cells = {"id": row.id, "dropTableCode": row.drop_table_code, "itemTemplateCode": row.item_template_code, "rate": serialize_value(row.rate), "minQuantity": row.min_quantity, "maxQuantity": row.max_quantity, "jsonKeys": self._join_json_keys({"conditions": row.conditions_json}), "updatedAt": serialize_value(row.updated_at)}
        elif domain == "enhancementGroups":
            cells = {"id": row.id, "code": row.code, "name": row.name, "maxLevel": row.max_level, "isEnabled": row.is_enabled, "jsonKeys": self._join_json_keys({"rules": row.rules_json}), "updatedAt": serialize_value(row.updated_at)}
        elif domain == "enhancementLevels":
            cells = {"id": row.id, "groupCode": row.group_code, "fromLevel": row.from_level, "toLevel": row.to_level, "successRate": serialize_value(row.success_rate), "goldCost": serialize_value(row.gold_cost), "jsonKeys": self._join_json_keys({"materialRules": row.material_rules_json, "resultStats": row.result_stats_json, "failRules": row.fail_rules_json}), "updatedAt": serialize_value(row.updated_at)}
        elif domain == "characterSkills":
            cells = {"id": row.id, "characterCode": row.character_code, "skillCode": row.skill_code, "sortOrder": row.sort_order, "isDefault": row.is_default, "updatedAt": serialize_value(row.updated_at)}
        else:
            cells = {"id": getattr(row, "id", None), "updatedAt": serialize_value(getattr(row, "updated_at", None))}

        return {
            "id": getattr(row, "id", None),
            "domain": domain,
            "cells": cells,
            "rawJsonReturned": False,
            "assetsReturned": False,
        }

    @staticmethod
    def _join_json_keys(named_json_values: dict[str, Any]) -> str:
        parts: list[str] = []
        for label, value in named_json_values.items():
            if isinstance(value, dict) and value:
                parts.append(f"{label}:" + ",".join(sorted(map(str, value.keys()))[:8]))
        return " | ".join(parts) if parts else "-"


    def _serialize_master_detail_scalar_fields(self, row: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        fields: list[dict[str, Any]] = []
        asset_fields: list[dict[str, Any]] = []
        mapper = sa_inspect(row.__class__)
        for column_attr in mapper.mapper.column_attrs:
            key = column_attr.key
            value = getattr(row, key, None)
            if key.endswith("_json"):
                continue
            if self._is_asset_field(key):
                asset_fields.append(self._serialize_asset_field(key, value))
                continue
            fields.append({"key": key, "label": self._humanize_field_name(key), "value": self._safe_detail_scalar_value(value)})
        return fields, asset_fields

    def _serialize_master_detail_json_fields(self, row: Any) -> list[dict[str, Any]]:
        json_fields: list[dict[str, Any]] = []
        mapper = sa_inspect(row.__class__)
        for column_attr in mapper.mapper.column_attrs:
            key = column_attr.key
            if not key.endswith("_json"):
                continue
            raw_value = serialize_value(getattr(row, key, None)) or {}
            preview, stats = self._sanitize_json_preview(raw_value)
            json_fields.append(
                {
                    "key": key,
                    "label": self._humanize_field_name(key),
                    "keys": sorted(map(str, raw_value.keys()))[:30] if isinstance(raw_value, dict) else [],
                    "preview": preview,
                    "hiddenAssetCount": stats["hiddenAssetCount"],
                    "truncatedCount": stats["truncatedCount"],
                    "maxDepthHit": stats["maxDepthHit"],
                    "rawJsonReturned": False,
                    "sanitizedPreview": True,
                }
            )
        return json_fields

    async def _build_master_detail_relation_hints(self, session: AsyncSession, domain: str, row: Any) -> list[dict[str, Any]]:
        hints: list[dict[str, Any]] = []
        code = getattr(row, "code", None)
        if domain == "itemTemplates" and code:
            hints.append({"label": "드랍 아이템 연결", "value": await self._count_where(session, DropTableItem, DropTableItem.item_template_code == code)})
            group_code = getattr(row, "enhance_group_code", None)
            if group_code:
                hints.append({"label": "강화 그룹", "value": group_code})
                hints.append({"label": "강화 단계 수", "value": await self._count_where(session, EnhancementLevel, EnhancementLevel.group_code == group_code)})
        elif domain == "skills" and code:
            hints.append({"label": "스킬 레벨 수", "value": await self._count_where(session, SkillLevel, SkillLevel.skill_code == code)})
            hints.append({"label": "캐릭터 연결 수", "value": await self._count_where(session, CharacterSkill, CharacterSkill.skill_code == code)})
        elif domain == "skillLevels":
            hints.append({"label": "스킬 코드", "value": getattr(row, "skill_code", None)})
        elif domain == "characters" and code:
            hints.append({"label": "스킬 연결 수", "value": await self._count_where(session, CharacterSkill, CharacterSkill.character_code == code)})
        elif domain == "bosses" and code:
            hints.append({"label": "보스 드랍 테이블 수", "value": await self._count_where(session, DropTable, DropTable.owner_type == "boss", DropTable.owner_code == code)})
        elif domain == "fieldZones" and code:
            hints.append({"label": "필드 드랍 테이블 수", "value": await self._count_where(session, DropTable, DropTable.owner_type == "field", DropTable.owner_code == code)})
        elif domain == "dropTables" and code:
            hints.append({"label": "드랍 아이템 수", "value": await self._count_where(session, DropTableItem, DropTableItem.drop_table_code == code)})
            hints.append({"label": "대상", "value": f"{getattr(row, 'owner_type', '-')}/{getattr(row, 'owner_code', '-')}"})
        elif domain == "dropTableItems":
            hints.append({"label": "드랍 테이블", "value": getattr(row, "drop_table_code", None)})
            hints.append({"label": "아이템 코드", "value": getattr(row, "item_template_code", None)})
        elif domain == "enhancementGroups" and code:
            hints.append({"label": "강화 단계 수", "value": await self._count_where(session, EnhancementLevel, EnhancementLevel.group_code == code)})
            hints.append({"label": "아이템 연결 수", "value": await self._count_where(session, ItemTemplate, ItemTemplate.enhance_group_code == code)})
        elif domain == "enhancementLevels":
            hints.append({"label": "강화 그룹", "value": getattr(row, "group_code", None)})
        elif domain == "characterSkills":
            hints.append({"label": "캐릭터", "value": getattr(row, "character_code", None)})
            hints.append({"label": "스킬", "value": getattr(row, "skill_code", None)})
        return hints

    async def _count_where(self, session: AsyncSession, model: Any, *where_clauses: Any) -> int:
        stmt = select(func.count()).select_from(model)
        if where_clauses:
            stmt = stmt.where(*where_clauses)
        result = await session.execute(stmt)
        return int(result.scalar_one() or 0)

    @staticmethod
    def _is_asset_field(key: str) -> bool:
        return key in {"image_url", "icon_url"} or key.endswith("_image_url") or key.endswith("_icon_url")

    def _serialize_asset_field(self, key: str, value: Any) -> dict[str, Any]:
        value_text = "" if value is None else str(value)
        hidden = bool(value_text)
        kind = "data-url" if value_text.startswith("data:") else ("url" if value_text else "empty")
        return {
            "key": key,
            "label": self._humanize_field_name(key),
            "kind": kind,
            "hidden": hidden,
            "length": len(value_text),
            "value": "[asset hidden]" if hidden else None,
        }

    def _safe_detail_scalar_value(self, value: Any) -> Any:
        serialized = serialize_value(value)
        if isinstance(serialized, str):
            if serialized.startswith("data:"):
                return "[asset hidden:data-url]"
            if len(serialized) > 1000:
                return serialized[:1000] + "…[truncated]"
        return serialized

    def _sanitize_json_preview(self, value: Any) -> tuple[Any, dict[str, int]]:
        stats = {"hiddenAssetCount": 0, "truncatedCount": 0, "maxDepthHit": 0}
        return self._sanitize_json_value(value, stats, depth=0), stats

    def _sanitize_json_value(self, value: Any, stats: dict[str, int], *, depth: int) -> Any:
        serialized = serialize_value(value)
        if depth > 5:
            stats["maxDepthHit"] += 1
            return "[max depth hidden]"
        if isinstance(serialized, str):
            if serialized.startswith("data:"):
                stats["hiddenAssetCount"] += 1
                return "[asset hidden:data-url]"
            if len(serialized) > 600:
                stats["truncatedCount"] += 1
                return serialized[:600] + "…[truncated]"
            return serialized
        if isinstance(serialized, list):
            max_items = 60
            values = [self._sanitize_json_value(item, stats, depth=depth + 1) for item in serialized[:max_items]]
            if len(serialized) > max_items:
                stats["truncatedCount"] += 1
                values.append(f"…[{len(serialized) - max_items} more hidden]")
            return values
        if isinstance(serialized, dict):
            max_items = 80
            result: dict[str, Any] = {}
            for index, key in enumerate(sorted(serialized.keys(), key=lambda item: str(item))):
                if index >= max_items:
                    stats["truncatedCount"] += 1
                    result["…"] = f"[{len(serialized) - max_items} more keys hidden]"
                    break
                result[str(key)] = self._sanitize_json_value(serialized[key], stats, depth=depth + 1)
            return result
        return serialized

    @staticmethod
    def _humanize_field_name(key: str) -> str:
        return key.replace("_", " ")

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
            "writeUiBlockedReason": "변경 이력/되돌리기/권한 정책이 붙기 전까지 관리자 쓰기 화면은 막아둡니다.",
        }

    async def _count(self, session: AsyncSession, model: Any, *, where_clause: Any | None = None) -> int:
        stmt = select(func.count()).select_from(model)
        if where_clause is not None:
            stmt = stmt.where(where_clause)
        result = await session.execute(stmt)
        return int(result.scalar_one() or 0)

    def _serialize_save_snapshot_summary(self, snapshot: UserSaveSnapshot) -> dict[str, Any]:
        summary = serialize_value(snapshot.summary_json) or {}
        snapshot_json = serialize_value(snapshot.snapshot_json) or {}
        player = snapshot_json.get("player") if isinstance(snapshot_json, dict) else {}
        player = player if isinstance(player, dict) else {}
        return {
            "id": snapshot.id,
            "userId": snapshot.user_id,
            "slotKey": snapshot.slot_key,
            "isDefault": snapshot.slot_key == "default",
            "clientSaveKey": snapshot.client_save_key,
            "saveVersion": snapshot.save_version,
            "summary": summary,
            "counts": {
                "inventoryItems": self._count_filled_items(player.get("inventory")),
                "storageItems": self._count_filled_items(player.get("storage")),
                "trashItems": self._count_filled_items(player.get("trash")),
                "mailboxItems": self._count_filled_items(player.get("mailbox")),
            },
            "source": snapshot.source,
            "note": snapshot.note,
            "createdAt": serialize_value(snapshot.created_at),
            "updatedAt": serialize_value(snapshot.updated_at),
            "rawSnapshotReturned": False,
        }

    @staticmethod
    def _count_filled_items(value: Any) -> int:
        if not isinstance(value, list):
            return 0
        return len([item for item in value if item])
