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
)
from app.services.game_service import serialize_value


class AdminMasterCatalogService:
    """Master catalog/detail/relation read-only admin helpers.

    Split from AdminService in v200 while AdminService remains the facade used by routes.
    """

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
        limit: int = 20,
        page: int = 1,
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
                "page": 1,
                "offset": 0,
                "totalPages": 1,
                "hasPrevPage": False,
                "hasNextPage": False,
                "filters": {"domain": domain, "page": 1, "limit": 0, "warnings": ["domain_invalid"]},
                "columns": [],
                "rows": [],
                "rawJsonReturned": False,
                "assetsReturned": False,
            }

        model = config["model"]
        warnings: list[str] = []
        safe_limit = max(1, min(int(limit or 20), 200))
        safe_page = max(1, int(page or 1))
        safe_offset = (safe_page - 1) * safe_limit
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
        stmt = stmt.order_by(*self._master_catalog_order_by(model, safe_sort)).offset(safe_offset).limit(safe_limit)
        result = await session.execute(stmt)
        rows = [self._serialize_master_catalog_row(domain, row) for row in result.scalars().all()]
        total_pages = max(1, (total_filtered + safe_limit - 1) // safe_limit)

        return {
            "status": "loaded",
            "readOnly": True,
            "domain": domain,
            "domainLabel": config["label"],
            "description": config.get("description"),
            "limit": safe_limit,
            "page": safe_page,
            "offset": safe_offset,
            "count": len(rows),
            "total": total_filtered,
            "totalPages": total_pages,
            "hasPrevPage": safe_page > 1,
            "hasNextPage": safe_page < total_pages,
            "totalAll": total_all,
            "filters": {
                "domain": domain,
                "query": safe_query,
                "enabled": safe_enabled,
                "sort": safe_sort,
                "page": safe_page,
                "limit": safe_limit,
                "warnings": warnings,
                "hasActiveFilters": bool(safe_query or safe_enabled != "all" or safe_page > 1),
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
        relation_edit_options = await self._build_master_relation_edit_options(session, domain, row)
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
            "relationEditOptions": relation_edit_options,
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

    async def _build_master_relation_edit_options(self, session: AsyncSession, domain: str, row: Any) -> list[dict[str, Any]]:
        if domain == "itemTemplates":
            current = getattr(row, "enhance_group_code", None)
            options = [{"value": "", "label": "없음 · 강화 그룹 연결 안 함", "current": not bool(current)}]
            options.extend(await self._fetch_relation_code_options(session, EnhancementGroup, current_code=current, limit=200))
            return [{
                "field": "enhance_group_code",
                "kind": "relation-select",
                "targetDomain": "enhancementGroups",
                "targetLabel": "강화 그룹",
                "nullable": True,
                "allowApply": True,
                "options": options,
                "note": "선택한 강화 그룹 code가 실제 enhancementGroups에 있을 때만 적용됩니다.",
            }]
        if domain == "dropTableItems":
            current_item = getattr(row, "item_template_code", None)
            current_table = getattr(row, "drop_table_code", None)
            return [
                {
                    "field": "drop_table_code",
                    "kind": "relation-select",
                    "targetDomain": "dropTables",
                    "targetLabel": "드랍 테이블",
                    "nullable": False,
                    "allowApply": True,
                    "options": await self._fetch_relation_code_options(session, DropTable, current_code=current_table, limit=300),
                    "note": "선택한 dropTables.code가 실제 존재할 때만 드랍 묶음을 변경합니다.",
                },
                {
                    "field": "item_template_code",
                    "kind": "relation-select",
                    "targetDomain": "itemTemplates",
                    "targetLabel": "아이템 템플릿",
                    "nullable": False,
                    "allowApply": True,
                    "options": await self._fetch_relation_code_options(session, ItemTemplate, current_code=current_item, limit=300),
                    "note": "선택한 itemTemplates.code가 실제 존재할 때만 드랍 아이템 연결을 변경합니다.",
                },
            ]
        if domain == "dropTables":
            current_owner_type = str(getattr(row, "owner_type", None) or "boss")
            current_owner_code = getattr(row, "owner_code", None)
            boss_options = await self._fetch_relation_code_options(session, Boss, current_code=current_owner_code if current_owner_type == "boss" else None, limit=300)
            field_options = await self._fetch_relation_code_options(session, FieldZone, current_code=current_owner_code if current_owner_type == "field" else None, limit=300)
            owner_code_options = boss_options if current_owner_type == "boss" else field_options
            return [
                {
                    "field": "owner_type",
                    "kind": "relation-select",
                    "targetDomain": "bosses/fieldZones",
                    "targetLabel": "드랍 테이블 소유자 종류",
                    "nullable": False,
                    "allowApply": True,
                    "linkedField": "owner_code",
                    "options": [
                        {"value": "boss", "label": "boss · 보스 드랍 테이블", "current": current_owner_type == "boss"},
                        {"value": "field", "label": "field · 필드 드랍 테이블", "current": current_owner_type == "field"},
                    ],
                    "note": "owner_type을 바꾸면 owner_code 후보도 보스/필드 목록으로 자동 전환됩니다.",
                },
                {
                    "field": "owner_code",
                    "kind": "relation-select",
                    "targetDomain": "bosses" if current_owner_type == "boss" else "fieldZones",
                    "targetLabel": "드랍 테이블 소유자 코드",
                    "nullable": False,
                    "allowApply": True,
                    "dependsOn": "owner_type",
                    "optionGroups": {
                        "boss": boss_options,
                        "field": field_options,
                    },
                    "options": owner_code_options,
                    "note": "owner_type이 boss이면 bosses.code, field이면 fieldZones.code 중에서만 선택합니다. 백엔드가 적용 직전에 다시 존재 여부를 검사합니다.",
                },
            ]
        if domain == "skillLevels":
            current = getattr(row, "skill_code", None)
            return [{
                "field": "skill_code",
                "kind": "relation-select",
                "targetDomain": "skills",
                "targetLabel": "스킬",
                "nullable": False,
                "allowApply": True,
                "comboGuard": ["skill_code", "level"],
                "options": await self._fetch_relation_code_options(session, Skill, current_code=current, limit=300),
                "note": "스킬 코드 + 레벨 조합이 이미 존재하면 적용이 차단됩니다.",
            }]
        if domain == "enhancementLevels":
            current = getattr(row, "group_code", None)
            return [{
                "field": "group_code",
                "kind": "relation-select",
                "targetDomain": "enhancementGroups",
                "targetLabel": "강화 그룹",
                "nullable": False,
                "allowApply": True,
                "comboGuard": ["group_code", "from_level"],
                "options": await self._fetch_relation_code_options(session, EnhancementGroup, current_code=current, limit=300),
                "note": "강화 그룹 + 시작 강화 단계 조합이 이미 존재하면 적용이 차단됩니다.",
            }]
        if domain == "characterSkills":
            current_character = getattr(row, "character_code", None)
            current_skill = getattr(row, "skill_code", None)
            return [
                {
                    "field": "character_code",
                    "kind": "relation-select",
                    "targetDomain": "characters",
                    "targetLabel": "캐릭터",
                    "nullable": False,
                    "allowApply": True,
                    "comboGuard": ["character_code", "skill_code"],
                    "options": await self._fetch_relation_code_options(session, Character, current_code=current_character, limit=200),
                    "note": "캐릭터 + 스킬 조합이 이미 존재하면 적용이 차단됩니다.",
                },
                {
                    "field": "skill_code",
                    "kind": "relation-select",
                    "targetDomain": "skills",
                    "targetLabel": "스킬",
                    "nullable": False,
                    "allowApply": True,
                    "comboGuard": ["character_code", "skill_code"],
                    "options": await self._fetch_relation_code_options(session, Skill, current_code=current_skill, limit=300),
                    "note": "캐릭터 + 스킬 조합이 이미 존재하면 적용이 차단됩니다.",
                },
            ]
        return []

