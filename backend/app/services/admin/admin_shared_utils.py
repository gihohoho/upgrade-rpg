from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.game_service import serialize_value


class AdminSharedUtilsService:
    """Shared helpers used by split admin service mixins.

    Keep these methods internal-only. Admin routes must continue importing the
    AdminService facade from backend/app/services/admin_service.py.
    """

    async def _get_master_row(self, session: AsyncSession, domain: str, row_id: int) -> Any | None:
        config = self.MASTER_CATALOG_DOMAINS.get(str(domain or ""))
        safe_row_id = int(row_id or 0)
        if not config or safe_row_id <= 0:
            return None
        result = await session.execute(select(config["model"]).where(config["model"].id == safe_row_id))
        return result.scalar_one_or_none()

    async def _count(self, session: AsyncSession, model: Any, *, where_clause: Any | None = None) -> int:
        stmt = select(func.count()).select_from(model)
        if where_clause is not None:
            stmt = stmt.where(where_clause)
        result = await session.execute(stmt)
        return int(result.scalar_one() or 0)

    async def _count_where(self, session: AsyncSession, model: Any, *where_clauses: Any) -> int:
        stmt = select(func.count()).select_from(model)
        if where_clauses:
            stmt = stmt.where(*where_clauses)
        result = await session.execute(stmt)
        return int(result.scalar_one() or 0)

    async def _exists_by_code(self, session: AsyncSession, model: Any, code: str) -> bool:
        result = await session.execute(select(func.count()).select_from(model).where(model.code == code))
        return int(result.scalar_one() or 0) > 0

    async def _fetch_code_name(self, session: AsyncSession, model: Any, code: str) -> dict[str, Any] | None:
        result = await session.execute(select(model).where(model.code == code))
        row = result.scalar_one_or_none()
        if not row:
            return None
        return {"code": getattr(row, "code", None), "name": getattr(row, "name", None)}

    async def _exists_duplicate_combo(self, session: AsyncSession, model: Any, current_id: int, *where_clauses: Any) -> bool:
        stmt = select(func.count()).select_from(model).where(*where_clauses)
        stmt = stmt.where(model.id != int(current_id))
        result = await session.execute(stmt)
        return int(result.scalar_one() or 0) > 0

    async def _fetch_relation_code_options(self, session: AsyncSession, model: Any, *, current_code: Any = None, limit: int = 200) -> list[dict[str, Any]]:
        safe_limit = max(1, min(int(limit or 200), 500))
        current_text = "" if current_code is None else str(current_code)
        result = await session.execute(select(model).order_by(model.code.asc()).limit(safe_limit))
        rows = result.scalars().all()
        options = [self._serialize_relation_option(row, current_text) for row in rows]
        if current_text and not any(str(option.get("value")) == current_text for option in options):
            current = await self._fetch_code_name(session, model, current_text)
            options.insert(0, {
                "value": current_text,
                "label": f"{current_text} · {(current or {}).get('name') or '현재 DB 값'}",
                "current": True,
            })
        return options

    @staticmethod
    def _serialize_relation_option(row: Any, current_code: str) -> dict[str, Any]:
        code = str(getattr(row, "code", "") or "")
        name = getattr(row, "name", None)
        return {
            "value": code,
            "label": f"{code} · {name}" if name else code,
            "current": bool(current_code and code == current_code),
        }

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

    @staticmethod
    def _is_safe_admin_change_key(value: str) -> bool:
        allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
        return all(ch in allowed for ch in value)

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

    @staticmethod
    def _join_json_keys(named_json_values: dict[str, Any]) -> str:
        parts: list[str] = []
        for label, value in named_json_values.items():
            if isinstance(value, dict) and value:
                parts.append(f"{label}:" + ",".join(sorted(map(str, value.keys()))[:8]))
        return " | ".join(parts) if parts else "-"

    @staticmethod
    def _count_filled_items(value: Any) -> int:
        if not isinstance(value, list):
            return 0
        return len([item for item in value if item])
