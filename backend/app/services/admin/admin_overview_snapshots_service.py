from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, UserSaveSnapshot
from app.services.game_service import serialize_value


ADMIN_SAVE_SUMMARY_FIELDS = (
    "saveVersion",
    "gold",
    "level",
    "currentCharacterId",
    "currentZoneIndex",
    "currentZoneType",
    "inventoryItems",
    "storageItems",
    "trashItems",
    "mailboxItems",
    "createdAt",
)
ADMIN_SAVE_SUMMARY_TEXT_LIMIT = 160


class AdminOverviewSnapshotsService:
    """Overview and save snapshot read-only admin helpers.

    Split from AdminService in v199 while AdminService remains the facade used by routes.
    """

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
                "authMode": "authenticated-admin-account",
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

    def _serialize_save_snapshot_summary(self, snapshot: UserSaveSnapshot) -> dict[str, Any]:
        summary = self._serialize_admin_save_summary(snapshot.summary_json)
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
    def _serialize_admin_save_summary(value: Any) -> dict[str, Any]:
        """Return only bounded scalar fields consumed by admin diagnostics."""
        source = value if isinstance(value, dict) else {}
        summary: dict[str, Any] = {}
        for key in ADMIN_SAVE_SUMMARY_FIELDS:
            if key not in source:
                continue
            serialized = serialize_value(source.get(key))
            if isinstance(serialized, str):
                summary[key] = serialized[:ADMIN_SAVE_SUMMARY_TEXT_LIMIT]
            elif serialized is None or isinstance(serialized, bool | int | float):
                summary[key] = serialized
        return summary
