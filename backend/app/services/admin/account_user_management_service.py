from __future__ import annotations

from collections import defaultdict
import math
from typing import Any, Iterable

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from app.models import AdminChangeLog, User, UserSaveSnapshot
from app.services.account_character_service import account_character_metadata
from app.services.game_service import serialize_value


ACCOUNT_CHARACTER_SLOT_COUNT = 8
ADMIN_SUMMARY_INTEGER_MAX = 1_000_000_000
ADMIN_SUMMARY_GOLD_MAX = 10**100
ADMIN_SUMMARY_ZONE_TYPES = frozenset({"town", "field", "boss", "boss_empty"})


class AccountUserManagementService:
    """Safe account administration without exposing credential or raw-save fields."""

    USER_SORTS = {
        "created_desc": (User.created_at.desc(), User.id.desc()),
        "created_asc": (User.created_at.asc(), User.id.asc()),
        "username_asc": (User.username.asc(), User.id.asc()),
        "username_desc": (User.username.desc(), User.id.desc()),
        "updated_desc": (User.updated_at.desc(), User.id.desc()),
    }

    async def get_bootstrap_status(
        self,
        session: AsyncSession,
        *,
        current_user_id: int,
    ) -> dict[str, Any]:
        current = await session.get(User, int(current_user_id))
        if current is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="로그인 계정을 찾을 수 없습니다.")

        initialized_admin_count = await self._count_initialized_admins(session)
        can_bootstrap = bool(
            initialized_admin_count == 0
            and current.is_active
            and current.password_hash
            and self._has_verified_email_identity(current)
        )
        return {
            "status": "ready" if can_bootstrap else "locked",
            "readOnly": True,
            "bootstrapRequired": initialized_admin_count == 0,
            "canBootstrap": can_bootstrap,
            "initializedAdminCount": initialized_admin_count,
            "currentUser": self._serialize_user(current),
            "reason": self._bootstrap_block_reason(current, initialized_admin_count),
        }

    async def bootstrap_first_admin(
        self,
        session: AsyncSession,
        *,
        current_user_id: int,
        reason: str | None,
    ) -> dict[str, Any]:
        # Lock every existing account in stable order. Bootstrap is one-time and this
        # prevents two authenticated accounts from promoting themselves concurrently.
        result = await session.execute(select(User).order_by(User.id).with_for_update())
        users = list(result.scalars().all())
        current = next((row for row in users if int(row.id) == int(current_user_id)), None)
        if current is None:
            await session.rollback()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="로그인 계정을 찾을 수 없습니다.")

        initialized_admin_count = sum(1 for row in users if self._is_initialized_admin(row))
        block_reason = self._bootstrap_block_reason(current, initialized_admin_count)
        if block_reason:
            await session.rollback()
            return {
                "status": "blocked",
                "readOnly": False,
                "applied": False,
                "bootstrapRequired": initialized_admin_count == 0,
                "canBootstrap": False,
                "initializedAdminCount": initialized_admin_count,
                "currentUser": self._serialize_user(current),
                "reason": block_reason,
            }

        before = {"isAdmin": bool(current.is_admin)}
        current.is_admin = True
        after = {"isAdmin": True}
        change_log = AdminChangeLog(
            admin_user_id=int(current.id),
            target_type="user",
            target_id=str(current.id),
            action="update",
            reason=(str(reason or "최초 관리자 bootstrap").strip()[:500] or "최초 관리자 bootstrap"),
            before_json=before,
            after_json=after,
            rollback_json={"userId": int(current.id), **before},
            applied=True,
        )
        session.add(change_log)
        await session.commit()
        await session.refresh(current)
        await session.refresh(change_log)
        return {
            "status": "applied",
            "readOnly": False,
            "applied": True,
            "bootstrapRequired": False,
            "canBootstrap": False,
            "initializedAdminCount": 1,
            "currentUser": self._serialize_user(current),
            "changeLogId": int(change_log.id),
        }

    async def list_users(
        self,
        session: AsyncSession,
        *,
        page: int,
        limit: int,
        query: str | None,
        account_status: str,
        sort: str,
    ) -> dict[str, Any]:
        safe_page = max(1, int(page or 1))
        safe_limit = max(1, min(int(limit or 20), 100))
        safe_query = str(query or "").strip()[:120]
        safe_status = account_status if account_status in {"all", "active", "suspended"} else "all"
        safe_sort = sort if sort in self.USER_SORTS else "created_desc"

        clauses: list[Any] = []
        if safe_query:
            folded_query = safe_query.casefold()
            clauses.append(
                or_(
                    func.lower(User.username).contains(folded_query, autoescape=True),
                    func.lower(User.email_canonical).contains(folded_query, autoescape=True),
                )
            )
        if safe_status == "active":
            clauses.append(User.is_active.is_(True))
        elif safe_status == "suspended":
            clauses.append(User.is_active.is_(False))

        count_stmt = select(func.count()).select_from(User)
        rows_stmt = select(User)
        if clauses:
            count_stmt = count_stmt.where(*clauses)
            rows_stmt = rows_stmt.where(*clauses)
        total = int((await session.execute(count_stmt)).scalar_one() or 0)
        rows_stmt = (
            rows_stmt.order_by(*self.USER_SORTS[safe_sort])
            .offset((safe_page - 1) * safe_limit)
            .limit(safe_limit)
        )
        users = list((await session.execute(rows_stmt)).scalars().all())
        snapshots = await self._snapshots_by_user(session, [int(row.id) for row in users])

        return {
            "status": "loaded",
            "readOnly": True,
            "page": safe_page,
            "limit": safe_limit,
            "count": len(users),
            "total": total,
            "totalPages": max(1, (total + safe_limit - 1) // safe_limit),
            "filters": {
                "query": safe_query,
                "status": safe_status,
                "sort": safe_sort,
            },
            "users": [
                self._serialize_user(row, character_slots=self._build_character_slots(snapshots.get(int(row.id), [])))
                for row in users
            ],
            "safeFieldPolicy": "account-metadata-and-character-summary-only",
            "rawSaveReturned": False,
        }

    async def get_user_detail(
        self,
        session: AsyncSession,
        *,
        user_id: int,
    ) -> dict[str, Any]:
        user = await session.get(User, int(user_id))
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="회원 정보를 찾을 수 없습니다.")
        snapshots = await self._snapshots_by_user(session, [int(user.id)])
        slots = self._build_character_slots(snapshots.get(int(user.id), []))
        return {
            "status": "loaded",
            "readOnly": True,
            "user": self._serialize_user(
                user,
                character_slots=slots,
                include_full_email=True,
            ),
            "characterSlots": slots,
            "safeFieldPolicy": "account-metadata-and-character-summary-only",
            "rawSaveReturned": False,
        }

    async def preview_status_change(
        self,
        session: AsyncSession,
        *,
        admin_user_id: int,
        user_id: int,
        base_is_active: bool,
        next_is_active: bool,
        reason: str,
    ) -> dict[str, Any]:
        user = await session.get(User, int(user_id))
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="회원 정보를 찾을 수 없습니다.")
        active_admin_count = await self._count_active_admins(session)
        return self._build_status_preview(
            user,
            admin_user_id=admin_user_id,
            base_is_active=base_is_active,
            next_is_active=next_is_active,
            reason=reason,
            active_admin_count=active_admin_count,
        )

    async def apply_status_change(
        self,
        session: AsyncSession,
        *,
        admin_user_id: int,
        user_id: int,
        base_is_active: bool,
        next_is_active: bool,
        reason: str,
        confirm_text: str,
    ) -> dict[str, Any]:
        # Lock the target and all active administrators so the last-admin rule cannot
        # race with another suspension request.
        lock_stmt = (
            select(User)
            .where(
                or_(
                    User.id == int(user_id),
                    User.id == int(admin_user_id),
                    (
                        User.is_admin.is_(True)
                        & User.is_active.is_(True)
                        & User.password_hash.is_not(None)
                        & User.email_canonical.is_not(None)
                        & User.email_verified_at.is_not(None)
                    ),
                )
            )
            .order_by(User.id)
            .execution_options(populate_existing=True)
            .with_for_update()
        )
        locked_users = list((await session.execute(lock_stmt)).scalars().all())
        actor = next(
            (row for row in locked_users if int(row.id) == int(admin_user_id)),
            None,
        )
        if actor is None or not self._is_login_capable_active_admin(actor):
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="관리자 권한 또는 계정 상태가 변경되었습니다. 다시 로그인해주세요.",
            )
        user = next((row for row in locked_users if int(row.id) == int(user_id)), None)
        if user is None:
            await session.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="회원 정보를 찾을 수 없습니다.")
        active_admin_count = sum(
            1
            for row in locked_users
            if self._is_login_capable_active_admin(row)
        )
        preview = self._build_status_preview(
            user,
            admin_user_id=admin_user_id,
            base_is_active=base_is_active,
            next_is_active=next_is_active,
            reason=reason,
            active_admin_count=active_admin_count,
        )
        if not preview["applyReady"]:
            await session.rollback()
            return {**preview, "readOnly": False, "applied": False}

        expected_confirmation = str(preview["confirmationText"])
        if str(confirm_text or "").strip() != expected_confirmation:
            await session.rollback()
            return {
                **preview,
                "status": "confirmation_required",
                "readOnly": False,
                "writeBlocked": True,
                "applied": False,
                "message": "화면에 표시된 확인 문구를 정확히 입력해 주세요.",
            }

        before = {"isActive": bool(user.is_active)}
        user.is_active = bool(next_is_active)
        after = {"isActive": bool(user.is_active)}
        change_log = AdminChangeLog(
            admin_user_id=int(admin_user_id),
            target_type="user",
            target_id=str(user.id),
            action="update",
            reason=str(reason).strip()[:500],
            before_json=before,
            after_json=after,
            rollback_json={"userId": int(user.id), **before},
            applied=True,
        )
        session.add(change_log)
        await session.commit()
        await session.refresh(user)
        await session.refresh(change_log)
        return {
            **preview,
            "status": "applied",
            "readOnly": False,
            "writeBlocked": False,
            "applied": True,
            "applyReady": False,
            "user": self._serialize_user(user),
            "changeLogId": int(change_log.id),
        }

    def _build_status_preview(
        self,
        user: User,
        *,
        admin_user_id: int,
        base_is_active: bool,
        next_is_active: bool,
        reason: str,
        active_admin_count: int,
    ) -> dict[str, Any]:
        blockers: list[str] = []
        current_is_active = bool(user.is_active)
        desired_is_active = bool(next_is_active)
        if bool(base_is_active) != current_is_active:
            blockers.append("stale_account_status")
        if desired_is_active == current_is_active:
            blockers.append("no_status_change")
        if int(user.id) == int(admin_user_id) and not desired_is_active:
            blockers.append("cannot_suspend_self")
        if (
            user.is_admin
            and user.password_hash
            and self._has_verified_email_identity(user)
            and current_is_active
            and not desired_is_active
            and int(active_admin_count) <= 1
        ):
            blockers.append("cannot_suspend_last_active_admin")

        confirmation_text = self._status_confirmation_text(user.username, desired_is_active)
        return {
            "status": "ready" if not blockers else ("stale" if "stale_account_status" in blockers else "blocked"),
            "readOnly": True,
            "writeBlocked": bool(blockers),
            "applied": False,
            "applyReady": not blockers,
            "user": self._serialize_user(user),
            "before": {"isActive": current_is_active},
            "after": {"isActive": desired_is_active},
            "reason": str(reason).strip()[:500],
            "confirmationText": confirmation_text,
            "blockers": blockers,
            "activeAdminCount": int(active_admin_count),
        }

    @staticmethod
    def _status_confirmation_text(username: str, next_is_active: bool) -> str:
        action = "계정 활성화" if next_is_active else "계정 정지"
        return f"{action}: {username}"

    @staticmethod
    def _is_initialized_admin(user: User) -> bool:
        # One-shot bootstrap stays locked once an owner admin exists, even if
        # that account still needs to finish email verification.
        return bool(user.is_admin and user.password_hash)

    @staticmethod
    def _has_verified_email_identity(user: User) -> bool:
        return bool(
            str(getattr(user, "email_canonical", None) or "").strip()
            and getattr(user, "email_verified_at", None)
        )

    @classmethod
    def _is_login_capable_active_admin(cls, user: User) -> bool:
        return bool(
            user.is_admin
            and user.is_active
            and user.password_hash
            and cls._has_verified_email_identity(user)
        )

    @classmethod
    def _bootstrap_block_reason(cls, user: User, initialized_admin_count: int) -> str | None:
        if initialized_admin_count > 0:
            return "이미 로그인 가능한 관리자가 있어 최초 관리자 bootstrap이 잠겼습니다."
        if not user.is_active:
            return "비활성 계정은 최초 관리자가 될 수 없습니다."
        if not user.password_hash:
            return "비밀번호가 설정된 로그인 계정만 최초 관리자가 될 수 있습니다."
        if not cls._has_verified_email_identity(user):
            return "이메일 인증을 완료한 로그인 계정만 최초 관리자가 될 수 있습니다."
        return None

    async def _count_initialized_admins(self, session: AsyncSession) -> int:
        stmt = (
            select(func.count())
            .select_from(User)
            .where(
                User.is_admin.is_(True),
                User.password_hash.is_not(None),
            )
        )
        return int((await session.execute(stmt)).scalar_one() or 0)

    async def _count_active_admins(self, session: AsyncSession) -> int:
        stmt = (
            select(func.count())
            .select_from(User)
            .where(
                User.is_admin.is_(True),
                User.is_active.is_(True),
                User.password_hash.is_not(None),
                User.email_canonical.is_not(None),
                User.email_verified_at.is_not(None),
            )
        )
        return int((await session.execute(stmt)).scalar_one() or 0)

    async def _snapshots_by_user(
        self,
        session: AsyncSession,
        user_ids: Iterable[int],
    ) -> dict[int, list[UserSaveSnapshot]]:
        ids = sorted({int(value) for value in user_ids})
        grouped: dict[int, list[UserSaveSnapshot]] = defaultdict(list)
        if not ids:
            return grouped
        stmt = (
            select(UserSaveSnapshot)
            .options(
                load_only(
                    UserSaveSnapshot.id,
                    UserSaveSnapshot.user_id,
                    UserSaveSnapshot.slot_key,
                    UserSaveSnapshot.save_version,
                    UserSaveSnapshot.summary_json,
                    UserSaveSnapshot.updated_at,
                )
            )
            .where(UserSaveSnapshot.user_id.in_(ids))
            .order_by(UserSaveSnapshot.updated_at.desc(), UserSaveSnapshot.id.desc())
        )
        for row in (await session.execute(stmt)).scalars().all():
            grouped[int(row.user_id)].append(row)
        return grouped

    def _build_character_slots(self, snapshots: Iterable[UserSaveSnapshot]) -> list[dict[str, Any]]:
        slots: list[dict[str, Any]] = [
            {"slotIndex": index, "isEmpty": True}
            for index in range(1, ACCOUNT_CHARACTER_SLOT_COUNT + 1)
        ]
        occupied: set[int] = set()
        for snapshot in snapshots:
            summary = snapshot.summary_json if isinstance(snapshot.summary_json, dict) else {}
            metadata = account_character_metadata(snapshot)
            if metadata is None:
                continue
            slot_index = int(metadata["slotIndex"])
            if slot_index in occupied:
                continue
            occupied.add(slot_index)
            slots[slot_index - 1] = {
                "slotIndex": slot_index,
                "isEmpty": False,
                "characterId": self._safe_text(metadata.get("id"), 80),
                "name": self._safe_text(metadata.get("name"), 80),
                "characterCode": self._safe_text(metadata.get("characterCode"), 80),
                "characterCreatedAt": self._safe_text(metadata.get("createdAt"), 80),
                "saveVersion": self._safe_bounded_int(snapshot.save_version),
                "level": self._safe_bounded_int(summary.get("level")),
                "gold": self._safe_gold(summary.get("gold")),
                "currentZoneIndex": self._safe_bounded_int(summary.get("currentZoneIndex")),
                "currentZoneType": self._safe_zone_type(summary.get("currentZoneType")),
                "lastSavedAt": serialize_value(snapshot.updated_at),
            }
        return slots

    @staticmethod
    def _safe_bounded_int(value: Any) -> int | None:
        if isinstance(value, bool) or not isinstance(value, int):
            return None
        return value if 0 <= value <= ADMIN_SUMMARY_INTEGER_MAX else None

    @staticmethod
    def _safe_gold(value: Any) -> int | float | None:
        if isinstance(value, bool) or not isinstance(value, int | float):
            return None
        if isinstance(value, float) and not math.isfinite(value):
            return None
        return value if 0 <= value <= ADMIN_SUMMARY_GOLD_MAX else None

    @staticmethod
    def _safe_zone_type(value: Any) -> str | None:
        return value if isinstance(value, str) and value in ADMIN_SUMMARY_ZONE_TYPES else None

    @staticmethod
    def _safe_text(value: Any, limit: int) -> str | None:
        if not isinstance(value, str):
            return None
        text = value.strip()
        return text[:limit] or None

    @staticmethod
    def _serialize_user(
        user: User,
        *,
        character_slots: list[dict[str, Any]] | None = None,
        include_full_email: bool = False,
    ) -> dict[str, Any]:
        slots = character_slots or []
        email = str(
            getattr(user, "email_original", None)
            or getattr(user, "email_canonical", None)
            or ""
        ).strip() or None
        email_verified = bool(email and getattr(user, "email_verified_at", None))
        serialized = {
            "id": int(user.id),
            "username": str(user.username),
            "maskedEmail": AccountUserManagementService._mask_email(email),
            "emailVerified": email_verified,
            "isActive": bool(user.is_active),
            "status": "active" if user.is_active else "suspended",
            "isAdmin": bool(user.is_admin),
            "characterSlotsUsed": sum(1 for slot in slots if not slot.get("isEmpty")),
            "characterSlotCapacity": ACCOUNT_CHARACTER_SLOT_COUNT,
            "createdAt": serialize_value(user.created_at),
            "updatedAt": serialize_value(user.updated_at),
        }
        if include_full_email:
            serialized["email"] = email
        return serialized

    @staticmethod
    def _mask_email(value: str | None) -> str | None:
        email = str(value or "").strip()
        if "@" not in email:
            return None
        local, domain = email.rsplit("@", 1)
        if not local or not domain:
            return None
        return f"{local[:1]}{'*' * max(3, min(len(local) - 1, 8))}@{domain}"
