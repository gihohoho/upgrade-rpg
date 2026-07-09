from __future__ import annotations

from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    AdminChangeLog,
    Boss,
    Character,
    DropTable,
    DropTableItem,
    EnhancementGroup,
    FieldZone,
    ItemTemplate,
    Skill,
)
from app.services.game_service import serialize_value


class AdminChangeLogService:
    """Admin change log listing/detail/rollback helpers.

    Split from AdminService in v202 while AdminService remains the facade used by routes.
    """
    async def list_admin_change_logs(
        self,
        session: AsyncSession,
        *,
        limit: int = 20,
        target_type: str | None = None,
        target_id: str | None = None,
        action: str | None = None,
        changed_key: str | None = None,
        applied: bool | None = None,
        sort: str | None = "created_desc",
    ) -> dict[str, Any]:
        safe_limit = max(1, min(int(limit or 20), 100))
        filters: dict[str, Any] = {
            "targetType": self._clean_filter_text(target_type),
            "targetId": self._clean_filter_text(target_id),
            "action": self._clean_filter_text(action),
            "changedKey": self._clean_filter_text(changed_key),
            "applied": applied,
            "sort": str(sort or "created_desc").strip() or "created_desc",
            "warnings": [],
        }

        try:
            filters = self._clean_admin_change_log_filters(
                target_type=target_type,
                target_id=target_id,
                action=action,
                changed_key=changed_key,
                applied=applied,
                sort=sort,
            )
            clauses = self._build_admin_change_log_where_clauses(filters)
            total = await self._count_admin_change_logs(session, clauses)
            stmt = select(AdminChangeLog)
            if clauses:
                stmt = stmt.where(*clauses)
            stmt = stmt.order_by(*self._admin_change_log_order_by(filters.get("sort") or "created_desc")).limit(safe_limit)
            result = await session.execute(stmt)
            rows = [self._serialize_admin_change_log(row) for row in result.scalars().all()]
            status = "loaded"
            warnings = list(filters.get("warnings") or [])
            debug = None
        except SQLAlchemyError as exc:
            # Local admin pages should stay readable even when an older dev DB was
            # created before admin_change_logs existed or has an older column set.
            # A failed SELECT leaves the transaction aborted on PostgreSQL, so
            # rollback before returning the safe empty diagnostic payload. Write
            # APIs still require the real table because they must persist an audit log.
            await session.rollback()
            total = 0
            rows = []
            status = "schema_unavailable"
            warnings = [*(filters.get("warnings") or []), "admin_change_logs_schema_unavailable_run_create_schema"]
            debug = {
                "errorClass": exc.__class__.__name__,
                "errorMessage": str(exc)[:500],
            }
        except Exception as exc:
            # Guard non-SQL regressions too. This endpoint is read-only diagnostics;
            # it should not break the whole admin page because of a filter/helper bug.
            try:
                await session.rollback()
            except Exception:
                pass
            total = 0
            rows = []
            status = "unavailable"
            warnings = [*(filters.get("warnings") or []), "admin_change_logs_service_exception_guarded"]
            debug = {
                "errorClass": exc.__class__.__name__,
                "errorMessage": str(exc)[:500],
            }

        payload = {
            "status": status,
            "readOnly": True,
            "count": len(rows),
            "total": total,
            "limit": safe_limit,
            "filters": {**filters, "warnings": warnings},
            "rows": rows,
            "rawBeforeAfterReturned": False,
            "warnings": warnings,
        }
        if debug:
            payload["debug"] = debug
        return payload



    async def get_admin_change_log_detail(
        self,
        session: AsyncSession,
        *,
        change_log_id: int,
    ) -> dict[str, Any]:
        """Return one admin change log with safe scalar before/after rows.

        The list endpoint intentionally hides before/after values. This detail endpoint
        is still bounded and sanitized, but it gives enough information for an admin to
        understand exactly what changed before using the guarded rollback flow.
        """
        row = await self._get_admin_change_log(session, change_log_id)
        if row is None:
            return self._empty_change_log_detail(status="not_found", change_log_id=change_log_id, warnings=["change_log_not_found"])
        detail = await self._serialize_admin_change_log_detail(session, row)
        domain, row_id = self._extract_master_change_target(row)
        rollback_available = bool(row.applied and row.action == "update" and domain and row_id and isinstance(serialize_value(row.rollback_json), dict))
        create_delete_available = bool(row.applied and row.action == "create" and domain in self.MASTER_CREATE_DELETE_ALLOWED_DOMAINS and row_id and isinstance(serialize_value(row.rollback_json), dict))
        create_delete_restore_available = bool(row.applied and row.action == "create_delete" and domain in self.MASTER_CREATE_DELETE_ALLOWED_DOMAINS and row_id and isinstance(serialize_value(row.before_json), dict) and isinstance(serialize_value(row.rollback_json), dict))
        detail["rollback"] = {
            "available": rollback_available,
            "domain": domain,
            "id": row_id,
            "confirmTextRequired": self.MASTER_EDIT_ROLLBACK_CONFIRM_TEXT,
            "note": "변경 직후 현재 DB 값이 이 변경 이력의 after 값과 일치할 때만 안전 되돌리기가 가능합니다.",
        }
        detail["createDelete"] = {
            "available": create_delete_available,
            "domain": domain,
            "id": row_id,
            "confirmTextRequired": self.MASTER_CREATE_DELETE_CONFIRM_TEXT,
            "note": "create 이력으로 만든 제한 도메인 row만, 현재값이 생성 당시 값과 같고 연결 데이터가 없을 때 삭제 되돌리기가 가능합니다.",
        }
        detail["createDeleteRestore"] = {
            "available": create_delete_restore_available,
            "domain": domain,
            "id": row_id,
            "confirmTextRequired": self.MASTER_CREATE_DELETE_RESTORE_CONFIRM_TEXT,
            "note": "create_delete 이력으로 삭제된 제한 도메인 row만, 같은 id/code 충돌이 없을 때 복원할 수 있습니다. fieldZones/bosses는 dropTables(owner_type=field/boss) 연결 검사까지 거칩니다.",
        }
        return detail

    async def preview_admin_change_log_rollback(
        self,
        session: AsyncSession,
        *,
        change_log_id: int,
        reason: str | None = None,
    ) -> dict[str, Any]:
        """Preview rollback of one guarded master-data change log.

        Rollback is deliberately stricter than normal editing: it only proceeds when
        the current DB row still matches the change log's after_json. If another edit
        already changed the row, rollback is blocked to avoid overwriting newer work.
        """
        row = await self._get_admin_change_log(session, change_log_id)
        if row is None:
            return self._empty_rollback_preview(status="not_found", change_log_id=change_log_id, warnings=["change_log_not_found"])

        domain, row_id = self._extract_master_change_target(row)
        before_json = serialize_value(row.before_json) or {}
        after_json = serialize_value(row.after_json) or {}
        rollback_json = serialize_value(row.rollback_json) or {}
        if not row.applied or row.action != "update" or not domain or not row_id or not isinstance(before_json, dict) or not isinstance(after_json, dict):
            return self._empty_rollback_preview(
                status="rollback_not_available",
                change_log_id=change_log_id,
                warnings=["change_log_is_not_guarded_master_update"],
                target_type=row.target_type,
                target_id=row.target_id,
            )
        if not isinstance(rollback_json, dict) or rollback_json.get("domain") != domain or int(rollback_json.get("id") or 0) != int(row_id):
            return self._empty_rollback_preview(
                status="rollback_metadata_invalid",
                change_log_id=change_log_id,
                warnings=["rollback_json_invalid"],
                target_type=row.target_type,
                target_id=row.target_id,
            )

        master_row = await self._get_master_row(session, domain, int(row_id))
        if master_row is None:
            return self._empty_rollback_preview(
                status="target_not_found",
                change_log_id=change_log_id,
                warnings=["target_row_not_found"],
                target_type=row.target_type,
                target_id=row.target_id,
                domain=domain,
                row_id=int(row_id),
            )

        keys = sorted(set(before_json.keys()) | set(after_json.keys()))
        current_values = self._current_master_values(master_row, keys)
        after_mismatches = []
        before_matches = []
        for key in keys:
            current = current_values.get(key)
            expected_after = serialize_value(after_json.get(key))
            expected_before = serialize_value(before_json.get(key))
            if current != expected_after:
                after_mismatches.append({
                    "key": key,
                    "label": self._humanize_field_name(key),
                    "current": current,
                    "expectedAfter": expected_after,
                    "rollbackTo": expected_before,
                })
            if current == expected_before:
                before_matches.append(key)

        changes = await self._build_change_log_changes_with_relations(session, domain, before_json, after_json)
        after_mismatches = await self._enrich_rollback_mismatches_with_relations(session, domain, after_mismatches, current_values, after_json, before_json)
        base = {
            "status": "rollback_preview_ready",
            "readOnly": False,
            "dryRun": True,
            "writeBlocked": True,
            "rollbackReady": False,
            "wouldRollback": False,
            "confirmTextRequired": self.MASTER_EDIT_ROLLBACK_CONFIRM_TEXT,
            "changeLogId": int(change_log_id),
            "targetType": row.target_type,
            "targetId": row.target_id,
            "domain": domain,
            "id": int(row_id),
            "action": row.action,
            "reason": str(reason or "")[:300] if reason else None,
            "sourceChangeReason": row.reason,
            "changes": changes,
            "changedKeys": [change["key"] for change in changes],
            "diffCount": len(changes),
            "relationChangedKeys": [change["key"] for change in changes if change.get("relation")],
            "relationChangeCount": sum(1 for change in changes if change.get("relation")),
            "relationLabelsReturned": any(change.get("relation") for change in changes),
            "currentMatchesAfter": len(after_mismatches) == 0,
            "currentMismatches": after_mismatches[:30],
            "currentMismatchCount": len(after_mismatches),
            "alreadyRolledBackFieldCount": len(before_matches),
            "rawBeforeAfterReturned": False,
            "warnings": [],
            "note": "현재 DB 값이 변경 이력의 after 값과 일치하면, before 값으로 되돌릴 수 있습니다.",
        }

        if len(before_matches) == len(keys) and keys:
            base.update({
                "status": "already_rolled_back",
                "rollbackReady": False,
                "wouldRollback": False,
                "writeBlocked": True,
                "warnings": ["target_already_matches_before_values"],
                "note": "현재 DB 값이 이미 이 변경 이력의 이전 값과 같습니다. 되돌릴 변경이 없습니다.",
            })
            return base

        if after_mismatches:
            base.update({
                "status": "rollback_blocked_current_changed",
                "rollbackReady": False,
                "wouldRollback": False,
                "writeBlocked": True,
                "warnings": ["current_db_values_do_not_match_change_log_after_values"],
                "note": "이 변경 이후 같은 행이 다시 수정된 것으로 보입니다. 최신 변경을 덮어쓰지 않기 위해 되돌리기를 차단했습니다.",
            })
            return base

        edit_preview = await self.preview_master_data_edit(
            session,
            domain=domain,
            row_id=int(row_id),
            draft=before_json,
            reason=reason,
            dry_run=True,
        )
        error_count = int(edit_preview.get("errorCount") or 0)
        accepted_changes = edit_preview.get("acceptedChanges") or []
        base.update({
            "rollbackReady": error_count == 0 and len(accepted_changes) > 0,
            "wouldRollback": error_count == 0 and len(accepted_changes) > 0,
            "errorCount": error_count,
            "acceptedChanges": accepted_changes,
            "rejectedChanges": edit_preview.get("rejectedChanges") or [],
            "unchangedChanges": edit_preview.get("unchangedChanges") or [],
            "warnings": edit_preview.get("warnings") or [],
            "note": "되돌리기 미리보기입니다. 아직 DB를 수정하지 않았습니다.",
        })
        if not base["rollbackReady"]:
            base.update({
                "status": "rollback_preview_not_valid",
                "writeBlocked": True,
                "wouldRollback": False,
            })
        return base

    async def apply_admin_change_log_rollback(
        self,
        session: AsyncSession,
        *,
        change_log_id: int,
        confirm_text: str,
        reason: str | None,
        admin_user_id: int,
    ) -> dict[str, Any]:
        """Apply a guarded rollback for one master-data change log."""
        preview = await self.preview_admin_change_log_rollback(
            session,
            change_log_id=change_log_id,
            reason=reason,
        )
        if str(confirm_text or "").strip() != self.MASTER_EDIT_ROLLBACK_CONFIRM_TEXT:
            preview.update({
                "status": "rollback_confirmation_required",
                "dryRun": False,
                "writeBlocked": True,
                "rolledBack": False,
                "rollbackReady": False,
                "wouldRollback": False,
                "warnings": [*(preview.get("warnings") or []), "rollback_confirm_text_mismatch"],
                "note": "정확한 되돌리기 확인 문구를 입력해야 DB에 적용됩니다.",
            })
            return preview
        if not preview.get("rollbackReady") or not preview.get("currentMatchesAfter"):
            preview.update({
                "status": "rollback_rejected",
                "dryRun": False,
                "writeBlocked": True,
                "rolledBack": False,
                "rollbackReady": False,
                "wouldRollback": False,
                "warnings": [*(preview.get("warnings") or []), "rollback_preview_not_safe_to_apply"],
            })
            return preview

        row = await self._get_admin_change_log(session, change_log_id)
        if row is None:
            preview.update({"status": "not_found", "rolledBack": False, "writeBlocked": True})
            return preview
        domain, row_id = self._extract_master_change_target(row)
        master_row = await self._get_master_row(session, str(domain), int(row_id or 0))
        if master_row is None:
            preview.update({"status": "target_not_found", "rolledBack": False, "writeBlocked": True})
            return preview

        before_json = serialize_value(row.before_json) or {}
        after_json = serialize_value(row.after_json) or {}
        keys = sorted(set(before_json.keys()) | set(after_json.keys()))
        current_values = self._current_master_values(master_row, keys)
        column_map = self._master_edit_column_map(master_row)
        applied_changes: list[dict[str, Any]] = []
        rollback_values: dict[str, Any] = {}
        for key, rollback_to in before_json.items():
            column = column_map.get(key)
            if column is None or not self._master_edit_field_is_allowed(str(domain), key):
                continue
            normalized_value, issue = self._normalize_master_edit_value(column, rollback_to)
            if issue:
                continue
            setattr(master_row, key, normalized_value)
            rollback_values[key] = serialize_value(normalized_value)
            applied_changes.append({
                "key": key,
                "label": self._humanize_field_name(key),
                "before": current_values.get(key),
                "after": serialize_value(normalized_value),
                "type": self._master_edit_column_type(column),
            })

        if not applied_changes:
            await session.rollback()
            preview.update({
                "status": "rollback_nothing_to_apply",
                "dryRun": False,
                "writeBlocked": True,
                "rolledBack": False,
                "warnings": [*(preview.get("warnings") or []), "no_rollback_changes_applied"],
            })
            return preview

        rollback_log = AdminChangeLog(
            admin_user_id=int(admin_user_id),
            target_type=row.target_type,
            target_id=row.target_id,
            action="rollback",
            reason=(str(reason or "")[:500] or f"Rollback change log #{change_log_id}"),
            before_json=current_values,
            after_json=rollback_values,
            rollback_json={"domain": domain, "id": int(row_id), "draft": current_values, "sourceChangeLogId": int(change_log_id)},
            applied=True,
        )
        session.add(rollback_log)
        await session.commit()
        await session.refresh(rollback_log)
        applied_changes_with_relations = await self._build_change_log_changes_with_relations(session, str(domain), current_values, rollback_values)

        preview.update({
            "status": "rolled_back",
            "dryRun": False,
            "writeBlocked": False,
            "rolledBack": True,
            "rollbackReady": False,
            "wouldRollback": False,
            "rollbackChangeLogId": rollback_log.id,
            "appliedChanges": applied_changes_with_relations,
            "acceptedChanges": applied_changes_with_relations,
            "relationChangedKeys": [change["key"] for change in applied_changes_with_relations if change.get("relation")],
            "relationChangeCount": sum(1 for change in applied_changes_with_relations if change.get("relation")),
            "relationLabelsReturned": any(change.get("relation") for change in applied_changes_with_relations),
            "diffCount": len(applied_changes_with_relations),
            "warnings": [*(preview.get("warnings") or []), "game_runtime_requires_reload"],
            "note": "관리자 변경 이력을 기준으로 DB 값을 이전 값으로 되돌렸습니다. 게임 화면은 새로고침 후 최신 master-data를 다시 읽습니다.",
        })
        return preview

    def _clean_admin_change_log_filters(
        self,
        *,
        target_type: Any = None,
        target_id: Any = None,
        action: Any = None,
        changed_key: Any = None,
        applied: Any = None,
        sort: Any = "created_desc",
    ) -> dict[str, Any]:
        safe_sort = str(sort or "created_desc").strip()
        if safe_sort not in {"created_desc", "created_asc", "target_asc", "action_asc"}:
            safe_sort = "created_desc"
        safe_changed_key = self._clean_filter_text(changed_key)
        if safe_changed_key and not self._is_safe_admin_change_key(safe_changed_key):
            safe_changed_key = None

        clean_applied: bool | None
        if applied is None or applied == "":
            clean_applied = None
        elif isinstance(applied, bool):
            clean_applied = applied
        else:
            clean_applied = str(applied).strip().lower() in {"true", "1", "yes", "applied"}

        safe_action = self._clean_filter_text(action)
        if safe_action and safe_action not in self.ADMIN_CHANGE_LOG_ACTION_FILTERS:
            safe_action = None

        active = {
            "targetType": self._clean_filter_text(target_type),
            "targetId": self._clean_filter_text(target_id),
            "action": safe_action,
            "changedKey": safe_changed_key,
            "applied": clean_applied,
            "sort": safe_sort,
            "allowedActions": sorted(self.ADMIN_CHANGE_LOG_ACTION_FILTERS),
        }
        active["hasActiveFilters"] = any(
            active.get(key) not in (None, "") for key in ("targetType", "targetId", "action", "changedKey", "applied")
        )
        return active

    def _build_admin_change_log_where_clauses(self, filters: dict[str, Any]) -> list[Any]:
        clauses: list[Any] = []
        if filters.get("targetType"):
            clauses.append(AdminChangeLog.target_type == filters["targetType"])
        if filters.get("targetId"):
            clauses.append(AdminChangeLog.target_id == filters["targetId"])
        if filters.get("action"):
            clauses.append(AdminChangeLog.action == filters["action"])
        if filters.get("applied") is not None:
            clauses.append(AdminChangeLog.applied.is_(bool(filters["applied"])))
        if filters.get("changedKey"):
            key = str(filters["changedKey"])
            clauses.append(or_(AdminChangeLog.before_json.op("?")(key), AdminChangeLog.after_json.op("?")(key)))
        return clauses

    def _admin_change_log_order_by(self, sort: str) -> tuple[Any, ...]:
        if sort == "created_asc":
            return (AdminChangeLog.created_at.asc(), AdminChangeLog.id.asc())
        if sort == "target_asc":
            return (AdminChangeLog.target_type.asc(), AdminChangeLog.target_id.asc(), AdminChangeLog.created_at.desc(), AdminChangeLog.id.desc())
        if sort == "action_asc":
            return (AdminChangeLog.action.asc(), AdminChangeLog.created_at.desc(), AdminChangeLog.id.desc())
        return (AdminChangeLog.created_at.desc(), AdminChangeLog.id.desc())

    async def _get_admin_change_log(self, session: AsyncSession, change_log_id: int) -> AdminChangeLog | None:
        safe_id = int(change_log_id or 0)
        if safe_id <= 0:
            return None
        result = await session.execute(select(AdminChangeLog).where(AdminChangeLog.id == safe_id))
        return result.scalar_one_or_none()

    def _empty_change_log_detail(self, *, status: str, change_log_id: int, warnings: list[str]) -> dict[str, Any]:
        return {
            "status": status,
            "readOnly": True,
            "id": int(change_log_id or 0),
            "changes": [],
            "changedKeys": [],
            "changedKeyCount": 0,
            "rollback": {"available": False, "confirmTextRequired": self.MASTER_EDIT_ROLLBACK_CONFIRM_TEXT},
            "rawBeforeAfterReturned": False,
            "warnings": warnings,
        }

    def _empty_rollback_preview(
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
            "rollbackReady": False,
            "wouldRollback": False,
            "confirmTextRequired": self.MASTER_EDIT_ROLLBACK_CONFIRM_TEXT,
            "changeLogId": int(change_log_id or 0),
            "targetType": target_type,
            "targetId": target_id,
            "domain": domain,
            "id": row_id,
            "changes": [],
            "changedKeys": [],
            "diffCount": 0,
            "errorCount": 1,
            "currentMatchesAfter": False,
            "currentMismatches": [],
            "currentMismatchCount": 0,
            "rawBeforeAfterReturned": False,
            "warnings": warnings,
        }

    async def _serialize_admin_change_log_detail(self, session: AsyncSession, row: AdminChangeLog) -> dict[str, Any]:
        base = self._serialize_admin_change_log(row)
        before_json = serialize_value(row.before_json) or {}
        after_json = serialize_value(row.after_json) or {}
        domain, _ = self._extract_master_change_target(row)
        changes = await self._build_change_log_changes_with_relations(session, domain, before_json, after_json)
        relation_count = sum(1 for change in changes if change.get("relation"))
        base.update({
            "status": "loaded",
            "readOnly": True,
            "changes": changes,
            "changedKeys": [change["key"] for change in changes],
            "changedKeyCount": len(changes),
            "relationChangeCount": relation_count,
            "relationChangedKeys": [change["key"] for change in changes if change.get("relation")],
            "relationLabelsReturned": relation_count > 0,
            "rawBeforeAfterReturned": False,
            "scalarChangesReturned": True,
            "rollbackRawJsonReturned": False,
            "warnings": [],
        })
        return base

    def _build_change_log_changes(self, before_json: Any, after_json: Any) -> list[dict[str, Any]]:
        before_dict = before_json if isinstance(before_json, dict) else {}
        after_dict = after_json if isinstance(after_json, dict) else {}
        keys = sorted(set(before_dict.keys()) | set(after_dict.keys()))
        return [
            {
                "key": key,
                "label": self._humanize_field_name(key),
                "before": serialize_value(before_dict.get(key)),
                "after": serialize_value(after_dict.get(key)),
            }
            for key in keys
        ]

    async def _build_change_log_changes_with_relations(self, session: AsyncSession, domain: str | None, before_json: Any, after_json: Any) -> list[dict[str, Any]]:
        changes = self._build_change_log_changes(before_json, after_json)
        if not domain:
            return changes
        before_dict = before_json if isinstance(before_json, dict) else {}
        after_dict = after_json if isinstance(after_json, dict) else {}
        for change in changes:
            key = str(change.get("key") or "")
            if not self._master_relation_edit_field_is_open(domain, key):
                continue
            before_info = await self._describe_change_log_relation_value(session, domain, key, change.get("before"), before_dict)
            after_info = await self._describe_change_log_relation_value(session, domain, key, change.get("after"), after_dict)
            change["relation"] = {
                "field": key,
                "before": before_info,
                "after": after_info,
                "targetDomain": (after_info or before_info or {}).get("targetDomain"),
                "targetCode": (after_info or before_info or {}).get("targetCode"),
                "targetLabel": (after_info or before_info or {}).get("targetLabel"),
            }
        return changes

    async def _enrich_rollback_mismatches_with_relations(
        self,
        session: AsyncSession,
        domain: str | None,
        mismatches: list[dict[str, Any]],
        current_values: dict[str, Any],
        after_json: Any,
        before_json: Any,
    ) -> list[dict[str, Any]]:
        if not domain or not mismatches:
            return mismatches
        after_context = after_json if isinstance(after_json, dict) else {}
        before_context = before_json if isinstance(before_json, dict) else {}
        current_context = {**after_context, **current_values}
        enriched: list[dict[str, Any]] = []
        for item in mismatches:
            key = str(item.get("key") or "")
            if self._master_relation_edit_field_is_open(domain, key):
                item = dict(item)
                item["relation"] = {
                    "field": key,
                    "current": await self._describe_change_log_relation_value(session, domain, key, item.get("current"), current_context),
                    "expectedAfter": await self._describe_change_log_relation_value(session, domain, key, item.get("expectedAfter"), after_context),
                    "rollbackTo": await self._describe_change_log_relation_value(session, domain, key, item.get("rollbackTo"), before_context),
                }
            enriched.append(item)
        return enriched

    async def _describe_change_log_relation_value(self, session: AsyncSession, domain: str, key: str, value: Any, context: dict[str, Any]) -> dict[str, Any] | None:
        if not self._master_relation_edit_field_is_open(domain, key):
            return None
        value_text = "" if value is None else str(value).strip()

        async def build(target_domain: str, model: Any | None, label_when_empty: str | None = None) -> dict[str, Any]:
            if not value_text:
                label = label_when_empty or "값 없음"
                return {"field": key, "targetDomain": target_domain, "targetCode": None, "targetLabel": label, "displayText": label}
            target = await self._fetch_code_name(session, model, value_text) if model is not None else None
            label = target.get("name") if target else None
            display = f"{value_text} · {label}" if label and label != value_text else value_text
            return {"field": key, "targetDomain": target_domain, "targetCode": value_text, "targetLabel": label or value_text, "displayText": display}

        if domain == "itemTemplates" and key == "enhance_group_code":
            return await build("enhancementGroups", EnhancementGroup, "강화 그룹 없음")
        if domain == "dropTableItems" and key == "drop_table_code":
            return await build("dropTables", DropTable)
        if domain == "dropTableItems" and key == "item_template_code":
            return await build("itemTemplates", ItemTemplate)
        if domain == "dropTables" and key == "owner_type":
            label = "보스" if value_text == "boss" else ("필드" if value_text == "field" else value_text or "값 없음")
            target_domain = "bosses" if value_text == "boss" else ("fieldZones" if value_text == "field" else "bosses/fieldZones")
            display = f"{value_text} · {label}" if value_text and label != value_text else label
            return {"field": key, "targetDomain": target_domain, "targetCode": value_text or None, "targetLabel": label, "displayText": display}
        if domain == "dropTables" and key == "owner_code":
            owner_type = str((context or {}).get("owner_type") or "boss").strip()
            if owner_type == "field":
                return await build("fieldZones", FieldZone)
            return await build("bosses", Boss)
        if domain == "skillLevels" and key == "skill_code":
            return await build("skills", Skill)
        if domain == "enhancementLevels" and key == "group_code":
            return await build("enhancementGroups", EnhancementGroup)
        if domain == "characterSkills" and key == "character_code":
            return await build("characters", Character)
        if domain == "characterSkills" and key == "skill_code":
            return await build("skills", Skill)
        return None

    def _extract_master_change_target(self, row: AdminChangeLog) -> tuple[str | None, int | None]:
        target_type = str(getattr(row, "target_type", "") or "")
        if not target_type.startswith("master_data."):
            return None, None
        domain = target_type.split(".", 1)[1]
        if domain not in self.MASTER_CATALOG_DOMAINS:
            return None, None
        try:
            row_id = int(getattr(row, "target_id", 0) or 0)
        except (TypeError, ValueError):
            row_id = 0
        return domain, row_id if row_id > 0 else None

    def _current_master_values(self, row: Any, keys: list[str]) -> dict[str, Any]:
        values: dict[str, Any] = {}
        for key in keys:
            values[key] = serialize_value(getattr(row, key, None))
        return values

    async def _count_admin_change_logs(self, session: AsyncSession, where_clauses: list[Any]) -> int:
        stmt = select(func.count()).select_from(AdminChangeLog)
        if where_clauses:
            stmt = stmt.where(*where_clauses)
        result = await session.execute(stmt)
        return int(result.scalar_one() or 0)

    def _serialize_admin_change_log(self, row: AdminChangeLog) -> dict[str, Any]:
        before_json = serialize_value(row.before_json) or {}
        after_json = serialize_value(row.after_json) or {}
        changed_keys = sorted(set(before_json.keys()) | set(after_json.keys())) if isinstance(before_json, dict) and isinstance(after_json, dict) else []
        domain, _ = self._extract_master_change_target(row)
        relation_changed_keys = [key for key in changed_keys if domain and self._master_relation_edit_field_is_open(domain, key)]
        return {
            "id": row.id,
            "adminUserId": row.admin_user_id,
            "targetType": row.target_type,
            "targetId": row.target_id,
            "action": row.action,
            "reason": row.reason,
            "applied": row.applied,
            "changedKeys": changed_keys,
            "changedKeyCount": len(changed_keys),
            "relationChangedKeys": relation_changed_keys,
            "relationChangeCount": len(relation_changed_keys),
            "createdAt": serialize_value(row.created_at),
            "updatedAt": serialize_value(row.updated_at),
            "rawBeforeAfterReturned": False,
        }

