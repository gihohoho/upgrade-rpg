from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
import secrets
import time
from typing import Any, Callable

from fastapi import HTTPException, status
from sqlalchemy import and_, delete, exists, func, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.core.auth_errors import AuthFlowHTTPException, auth_error as _auth_error
from app.core.security import CurrentUser, create_access_token, hash_password, verify_password
from app.models import (
    AdminChangeLog,
    AdminUserRole,
    ItemInstance,
    User,
    UserCharacterSkill,
    UserEmailActionToken,
    UserEquipmentSlot,
    UserInventorySlot,
    UserMailboxMessage,
    UserProfile,
    UserSaveSnapshot,
)
from app.schemas.auth import (
    AccountDeletionConfirmRequest,
    AccountDeletionRequest,
    EmailRequest,
    EmailTokenRequest,
    EmailValidationUnavailable,
    LoginRequest,
    NormalizedEmail,
    PasswordResetRequest,
    RegisterRequest,
    normalize_email_identity,
)
from app.services.auth_email_outbox import (
    EMAIL_PURPOSE_ACCOUNT_DELETION,
    EMAIL_PURPOSE_PASSWORD_RESET,
    EMAIL_PURPOSE_USERNAME_RECOVERY,
    EMAIL_PURPOSE_VERIFY,
    AuthEmailOutboxService,
)


ACCOUNT_CHARACTER_SLOT_KEYS = tuple(f"character-{index}" for index in range(1, 9))


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


class AuthService:
    def __init__(
        self,
        *,
        email_delivery: Any | None = None,
        email_normalizer: Callable[[str], NormalizedEmail] | None = None,
        token_secret: str | None = None,
        token_factory: Callable[[], str] | None = None,
        now_factory: Callable[[], datetime] | None = None,
        provider_ready: bool | None = None,
        public_frontend_origin: str | None = None,
        abuse_secret: str | None = None,
        email_outbox: AuthEmailOutboxService | None = None,
        monotonic_factory: Callable[[], float] | None = None,
        sleep: Callable[[float], Any] | None = None,
        discovery_floor_ms: int | None = None,
        discovery_jitter_ms: int | None = None,
    ) -> None:
        self.email_normalizer = email_normalizer or normalize_email_identity
        self.email_outbox = email_outbox or AuthEmailOutboxService(
            email_delivery=email_delivery,
            token_secret=token_secret,
            abuse_secret=abuse_secret,
            token_factory=token_factory,
            now_factory=now_factory,
            provider_ready=provider_ready,
            public_frontend_origin=public_frontend_origin,
        )
        self.now_factory = now_factory or (lambda: datetime.now(UTC))
        self.monotonic_factory = monotonic_factory or time.monotonic
        self.sleep = sleep or asyncio.sleep
        self.discovery_floor_ms = int(
            settings.auth_discovery_response_floor_ms
            if discovery_floor_ms is None
            else discovery_floor_ms
        )
        self.discovery_jitter_ms = int(
            settings.auth_discovery_response_jitter_ms
            if discovery_jitter_ms is None
            else discovery_jitter_ms
        )

    @staticmethod
    def serialize_current_user(current_user: CurrentUser) -> dict[str, Any]:
        return {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "emailVerified": current_user.email_verified,
            "isAdmin": current_user.is_admin,
        }

    @staticmethod
    def serialize_user(user: User) -> dict[str, Any]:
        email = str(user.email_original or user.email_canonical or "").strip() or None
        return {
            "id": user.id,
            "username": user.username,
            "email": email,
            "emailVerified": bool(email and user.email_verified_at),
            "isAdmin": bool(user.is_admin),
        }

    async def register(self, session: AsyncSession, payload: RegisterRequest) -> dict[str, Any]:
        identity = self._normalize_email(payload.email)
        self._require_delivery_ready()
        exact_existing = (
            await session.execute(
                select(User).where(
                    User.username == payload.username,
                    User.email_canonical == identity.canonical,
                )
            )
        ).scalar_one_or_none()
        if exact_existing is not None:
            if not self._registration_expired(exact_existing):
                recovered = await self._retry_pending_registration(
                    session,
                    payload=payload,
                    identity=identity,
                    candidate=exact_existing,
                )
                if recovered is not None:
                    return recovered
            reclaimed = await self._reclaim_expired_registration_conflicts(
                session,
                username=payload.username,
                email_canonical=identity.canonical,
            )
            if not reclaimed:
                raise self._account_identity_conflict()

        conflicting_id = (
            await session.execute(
                select(User.id)
                .where(
                    or_(
                        User.username == payload.username,
                        User.email_canonical == identity.canonical,
                    )
                )
                .limit(1)
            )
        ).scalar_one_or_none()
        if conflicting_id is not None:
            reclaimed = await self._reclaim_expired_registration_conflicts(
                session,
                username=payload.username,
                email_canonical=identity.canonical,
            )
            if not reclaimed:
                await session.rollback()
                await self._dummy_registration_password_check(payload)
                raise self._account_identity_conflict()

        await session.rollback()
        password_hash = await run_in_threadpool(
            hash_password,
            payload.password.get_secret_value(),
        )
        user = User(
            username=payload.username,
            email_original=identity.original,
            email_canonical=identity.canonical,
            email_verified_at=None,
            password_hash=password_hash,
            auth_version=0,
            is_active=True,
            is_admin=False,
        )
        session.add(user)
        try:
            await session.flush()
            session.add(UserProfile(user_id=user.id))
            await self.email_outbox.enqueue(
                session,
                purpose=EMAIL_PURPOSE_VERIFY,
                canonical_email=identity.canonical,
                user_id=int(user.id),
            )
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            recovered = await self._retry_pending_registration(
                session,
                payload=payload,
                identity=identity,
            )
            if recovered is not None:
                return recovered
            raise self._account_identity_conflict() from exc
        except Exception:
            await session.rollback()
            raise

        return self._verification_required_result(self.serialize_user(user))

    async def _retry_pending_registration(
        self,
        session: AsyncSession,
        *,
        payload: RegisterRequest,
        identity: NormalizedEmail,
        candidate: User | None = None,
    ) -> dict[str, Any] | None:
        if candidate is None:
            candidate = (
                await session.execute(
                    select(User).where(
                        User.username == payload.username,
                        User.email_canonical == identity.canonical,
                    )
                )
            ).scalar_one_or_none()
        if candidate is None:
            return None

        candidate_id = int(candidate.id)
        candidate_hash = str(candidate.password_hash or "")
        candidate_is_retry_eligible = bool(
            candidate.is_active
            and candidate.email_verified_at is None
            and candidate_hash
        )
        await session.rollback()
        if candidate_hash:
            password_ok = await run_in_threadpool(
                verify_password,
                payload.password.get_secret_value(),
                candidate_hash,
            )
        else:
            await run_in_threadpool(
                hash_password,
                payload.password.get_secret_value(),
            )
            password_ok = False
        if not candidate_is_retry_eligible or not password_ok:
            return None

        locked_user = (
            await session.execute(
                select(User)
                .where(User.id == candidate_id)
                .execution_options(populate_existing=True)
                .with_for_update()
            )
        ).scalar_one_or_none()
        if (
            locked_user is None
            or str(locked_user.username) != payload.username
            or str(locked_user.email_canonical or "") != identity.canonical
            or not locked_user.is_active
            or locked_user.email_verified_at is not None
            or not locked_user.password_hash
        ):
            await session.rollback()
            return None
        if str(locked_user.password_hash) != candidate_hash:
            password_ok = await run_in_threadpool(
                verify_password,
                payload.password.get_secret_value(),
                str(locked_user.password_hash),
            )
            if not password_ok:
                await session.rollback()
                return None

        try:
            await self.email_outbox.enqueue(
                session,
                purpose=EMAIL_PURPOSE_VERIFY,
                canonical_email=identity.canonical,
                user_id=int(locked_user.id),
            )
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        return self._verification_required_result(self.serialize_user(locked_user))

    @staticmethod
    async def _dummy_registration_password_check(payload: RegisterRequest) -> None:
        await run_in_threadpool(
            hash_password,
            payload.password.get_secret_value(),
        )

    async def _reclaim_expired_registration_conflicts(
        self,
        session: AsyncSession,
        *,
        username: str,
        email_canonical: str,
    ) -> bool:
        """Release only abandoned identities that never became usable accounts."""
        await session.rollback()
        conflicts = list(
            (
                await session.execute(
                    select(User)
                    .where(
                        or_(
                            User.username == username,
                            User.email_canonical == email_canonical,
                        )
                    )
                    .order_by(User.id)
                    .execution_options(populate_existing=True)
                    .with_for_update()
                )
            ).scalars()
        )
        if not conflicts:
            await session.rollback()
            return False

        cutoff = self._now() - timedelta(hours=int(settings.unverified_account_ttl_hours))
        reclaimable_ids: list[int] = []
        for candidate in conflicts:
            created_at = getattr(candidate, "created_at", None)
            if (
                candidate.is_admin
                or not candidate.is_active
                or candidate.email_verified_at is not None
                or not candidate.email_canonical
                or not candidate.password_hash
                or created_at is None
                or _as_utc(created_at) > cutoff
            ):
                await session.rollback()
                return False
            owned_data_present = bool(
                (
                    await session.execute(
                        select(
                            or_(
                                exists().where(
                                    AdminUserRole.user_id == int(candidate.id)
                                ),
                                exists().where(
                                    UserSaveSnapshot.user_id == int(candidate.id)
                                ),
                                exists().where(ItemInstance.user_id == int(candidate.id)),
                                exists().where(
                                    UserInventorySlot.user_id == int(candidate.id)
                                ),
                                exists().where(
                                    UserEquipmentSlot.user_id == int(candidate.id)
                                ),
                                exists().where(
                                    UserCharacterSkill.user_id == int(candidate.id)
                                ),
                                exists().where(
                                    UserMailboxMessage.user_id == int(candidate.id)
                                ),
                            )
                        )
                    )
                ).scalar_one()
            )
            if owned_data_present or await self._admin_audit_count(
                session,
                user_id=int(candidate.id),
            ):
                await session.rollback()
                return False
            reclaimable_ids.append(int(candidate.id))

        await session.execute(delete(User).where(User.id.in_(reclaimable_ids)))
        await session.commit()
        return True

    def _registration_expired(self, user: User) -> bool:
        created_at = getattr(user, "created_at", None)
        if created_at is None:
            return False
        cutoff = self._now() - timedelta(hours=int(settings.unverified_account_ttl_hours))
        return bool(
            user.email_verified_at is None
            and user.email_canonical
            and _as_utc(created_at) <= cutoff
        )

    @staticmethod
    def _verification_required_result(user: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": "verification_required",
            "user": dict(user),
            "accessTokenIssued": False,
            "emailRequestAccepted": True,
        }

    @staticmethod
    def _account_identity_conflict() -> AuthFlowHTTPException:
        return _auth_error(
            status.HTTP_409_CONFLICT,
            "account_identity_already_used",
            "이미 사용 중인 아이디 또는 이메일입니다.",
        )

    async def login(self, session: AsyncSession, payload: LoginRequest) -> dict[str, Any]:
        identifier = str(payload.identifier).strip()
        if "@" in identifier:
            identity = self._normalize_email(identifier)
            clause = User.email_canonical == identity.canonical
        else:
            clause = User.username == identifier
        user = (await session.execute(select(User).where(clause))).scalar_one_or_none()
        password = payload.password.get_secret_value()

        if user is None or not user.password_hash:
            await run_in_threadpool(hash_password, password)
            raise self._invalid_credentials()
        password_ok = await run_in_threadpool(verify_password, password, user.password_hash)
        if not password_ok:
            raise self._invalid_credentials()
        if not user.is_active:
            raise _auth_error(
                status.HTTP_403_FORBIDDEN,
                "account_suspended",
                "현재 이용이 중지된 계정입니다.",
            )
        if not user.email_canonical or not user.email_verified_at:
            raise _auth_error(
                status.HTTP_403_FORBIDDEN,
                "email_verification_required",
                "이메일 인증을 완료한 뒤 로그인해주세요.",
            )

        token, expires_in = create_access_token(
            user.id,
            auth_version=int(user.auth_version or 0),
        )
        return {
            "status": "authenticated",
            "user": self.serialize_user(user),
            "accessToken": token,
            "tokenType": "bearer",
            "expiresIn": expires_in,
        }

    async def verify_email(
        self,
        session: AsyncSession,
        payload: EmailTokenRequest,
    ) -> dict[str, Any]:
        user, _token_row = await self._lock_action_token(
            session,
            raw_token=payload.token.get_secret_value(),
            purpose=EMAIL_PURPOSE_VERIFY,
        )
        now = self._now()
        user.email_verified_at = user.email_verified_at or now
        user.auth_version = int(user.auth_version or 0) + 1
        await self._consume_outstanding_tokens(session, user_id=user.id, now=now)
        await session.commit()
        return {
            "status": "email_verified",
            "user": self.serialize_user(user),
        }

    async def resend_verification(
        self,
        session: AsyncSession,
        payload: EmailRequest,
    ) -> dict[str, Any]:
        started_at = self.monotonic_factory()
        identity = self._normalize_email(payload.email)
        self._require_delivery_ready()
        user = (
            await session.execute(
                select(User).where(User.email_canonical == identity.canonical)
            )
        ).scalar_one_or_none()
        eligible_user_id = (
            int(user.id)
            if user and user.is_active and user.password_hash and not user.email_verified_at
            else None
        )
        try:
            await self.email_outbox.enqueue(
                session,
                purpose=EMAIL_PURPOSE_VERIFY,
                canonical_email=identity.canonical,
                user_id=eligible_user_id,
            )
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        await self._finish_discovery_delay(started_at)
        return self._generic_discovery_result("verification_email_if_eligible")

    async def recover_username(
        self,
        session: AsyncSession,
        payload: EmailRequest,
    ) -> dict[str, Any]:
        started_at = self.monotonic_factory()
        identity = self._normalize_email(payload.email)
        self._require_delivery_ready()
        user = (
            await session.execute(
                select(User).where(User.email_canonical == identity.canonical)
            )
        ).scalar_one_or_none()
        eligible_user_id = (
            int(user.id)
            if user and user.is_active and user.password_hash and user.email_verified_at
            else None
        )
        try:
            await self.email_outbox.enqueue(
                session,
                purpose=EMAIL_PURPOSE_USERNAME_RECOVERY,
                canonical_email=identity.canonical,
                user_id=eligible_user_id,
            )
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        await self._finish_discovery_delay(started_at)
        return self._generic_discovery_result("username_email_if_eligible")

    async def request_password_reset(
        self,
        session: AsyncSession,
        payload: EmailRequest,
    ) -> dict[str, Any]:
        started_at = self.monotonic_factory()
        identity = self._normalize_email(payload.email)
        self._require_delivery_ready()
        user = (
            await session.execute(
                select(User).where(User.email_canonical == identity.canonical)
            )
        ).scalar_one_or_none()
        eligible_user_id = (
            int(user.id)
            if user and user.is_active and user.password_hash and user.email_verified_at
            else None
        )
        try:
            await self.email_outbox.enqueue(
                session,
                purpose=EMAIL_PURPOSE_PASSWORD_RESET,
                canonical_email=identity.canonical,
                user_id=eligible_user_id,
            )
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        await self._finish_discovery_delay(started_at)
        return self._generic_discovery_result("password_reset_email_if_eligible")

    async def reset_password(
        self,
        session: AsyncSession,
        payload: PasswordResetRequest,
    ) -> dict[str, Any]:
        password_hash = await run_in_threadpool(
            hash_password,
            payload.password.get_secret_value(),
        )
        user, _token_row = await self._lock_action_token(
            session,
            raw_token=payload.token.get_secret_value(),
            purpose=EMAIL_PURPOSE_PASSWORD_RESET,
        )
        if not user.is_active or not user.email_verified_at:
            await session.rollback()
            raise _auth_error(
                status.HTTP_403_FORBIDDEN,
                "account_not_resettable",
                "현재 비밀번호를 재설정할 수 없는 계정입니다.",
            )
        now = self._now()
        user.password_hash = password_hash
        user.auth_version = int(user.auth_version or 0) + 1
        await self._consume_outstanding_tokens(session, user_id=user.id, now=now)
        await session.commit()
        return {
            "status": "password_reset",
            "accessTokensRevoked": True,
        }

    async def preview_account_deletion(
        self,
        session: AsyncSession,
        *,
        current_user: CurrentUser,
    ) -> dict[str, Any]:
        user = await session.get(User, int(current_user.id))
        if user is None:
            raise _auth_error(
                status.HTTP_401_UNAUTHORIZED,
                "account_not_found",
                "로그인 계정을 찾을 수 없습니다.",
            )
        audit_count = await self._admin_audit_count(session, user_id=user.id)
        self._assert_deletable(user, audit_count=audit_count)
        save_snapshot_count = int(
            (
                await session.execute(
                    select(func.count(UserSaveSnapshot.id)).where(
                        UserSaveSnapshot.user_id == user.id
                    )
                )
            ).scalar_one()
            or 0
        )
        character_count = int(
            (
                await session.execute(
                    select(func.count(UserSaveSnapshot.id)).where(
                        UserSaveSnapshot.user_id == user.id,
                        UserSaveSnapshot.slot_key.in_(ACCOUNT_CHARACTER_SLOT_KEYS),
                    )
                )
            ).scalar_one()
            or 0
        )
        return {
            "status": "preview",
            "username": str(user.username),
            "maskedEmail": self.mask_email(user.email_canonical or user.email_original),
            "characterCount": character_count,
            "saveSnapshotCount": save_snapshot_count,
            "deletionScope": [
                "회원 계정과 프로필",
                "8개 캐릭터 슬롯과 모든 서버 저장",
                "인벤토리·장비·스킬·우편 데이터",
                "사용 중인 로그인 토큰과 이메일 작업 토큰",
            ],
            "rawSnapshotReturned": False,
        }

    async def request_account_deletion(
        self,
        session: AsyncSession,
        *,
        current_user: CurrentUser,
        payload: AccountDeletionRequest,
    ) -> dict[str, Any]:
        self._require_delivery_ready()
        user = await session.get(User, int(current_user.id))
        if user is None or not user.password_hash:
            raise self._invalid_credentials()
        audit_count = await self._admin_audit_count(session, user_id=user.id)
        self._assert_deletable(user, audit_count=audit_count)
        password_ok = await run_in_threadpool(
            verify_password,
            payload.password.get_secret_value(),
            user.password_hash,
        )
        if not password_ok:
            raise self._invalid_credentials()
        try:
            await self.email_outbox.enqueue(
                session,
                purpose=EMAIL_PURPOSE_ACCOUNT_DELETION,
                canonical_email=str(user.email_canonical),
                user_id=int(user.id),
            )
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        return {
            "status": "confirmation_email_queued",
            "accountDeleted": False,
            "emailRequestAccepted": True,
        }

    async def confirm_account_deletion(
        self,
        session: AsyncSession,
        payload: AccountDeletionConfirmRequest,
    ) -> dict[str, Any]:
        if payload.confirm_text != "계정 삭제":
            await session.rollback()
            raise _auth_error(
                422,
                "account_deletion_confirmation_required",
                "계정 삭제 확인 문구가 올바르지 않습니다.",
            )
        user, _token_row = await self._lock_action_token(
            session,
            raw_token=payload.token.get_secret_value(),
            purpose=EMAIL_PURPOSE_ACCOUNT_DELETION,
        )
        audit_count = await self._admin_audit_count(session, user_id=user.id)
        self._assert_deletable(user, audit_count=audit_count)
        deleted_user_id = int(user.id)
        await session.execute(delete(User).where(User.id == deleted_user_id))
        await session.commit()
        return {
            "status": "deleted",
            "deletedUserId": deleted_user_id,
        }

    async def _lock_action_token(
        self,
        session: AsyncSession,
        *,
        raw_token: str,
        purpose: str,
    ) -> tuple[User, UserEmailActionToken]:
        digest = self.digest_email_token(raw_token)
        candidate = (
            await session.execute(
                select(
                    UserEmailActionToken.id,
                    UserEmailActionToken.user_id,
                ).where(
                    UserEmailActionToken.token_digest == digest,
                    UserEmailActionToken.purpose == purpose,
                )
            )
        ).one_or_none()
        if candidate is None:
            await session.rollback()
            raise _auth_error(
                status.HTTP_400_BAD_REQUEST,
                "email_action_token_invalid",
                "메일 링크가 만료되었거나 이미 사용되었습니다.",
            )

        candidate_token_id = int(candidate[0])
        candidate_user_id = int(candidate[1])
        user = (
            await session.execute(
                select(User)
                .where(User.id == candidate_user_id)
                .execution_options(populate_existing=True)
                .with_for_update()
            )
        ).scalar_one_or_none()
        if user is None:
            await session.rollback()
            raise _auth_error(
                status.HTTP_400_BAD_REQUEST,
                "email_action_token_invalid",
                "메일 링크가 만료되었거나 이미 사용되었습니다.",
            )

        token_row = (
            await session.execute(
                select(UserEmailActionToken)
                .where(
                    UserEmailActionToken.id == candidate_token_id,
                    UserEmailActionToken.user_id == int(user.id),
                    UserEmailActionToken.token_digest == digest,
                    UserEmailActionToken.purpose == purpose,
                )
                .execution_options(populate_existing=True)
                .with_for_update()
            )
        ).scalar_one_or_none()
        now = self._now()
        if (
            token_row is None
            or token_row.consumed_at is not None
            or _as_utc(token_row.expires_at) <= now
        ):
            await session.rollback()
            raise _auth_error(
                status.HTTP_400_BAD_REQUEST,
                "email_action_token_invalid",
                "메일 링크가 만료되었거나 이미 사용되었습니다.",
            )
        return user, token_row

    async def _consume_outstanding_tokens(
        self,
        session: AsyncSession,
        *,
        user_id: int,
        now: datetime,
        purpose: str | None = None,
    ) -> None:
        clauses = [
            UserEmailActionToken.user_id == int(user_id),
            UserEmailActionToken.consumed_at.is_(None),
        ]
        if purpose is not None:
            clauses.append(UserEmailActionToken.purpose == purpose)
        await session.execute(
            update(UserEmailActionToken).where(*clauses).values(consumed_at=now)
        )

    async def _admin_audit_count(self, session: AsyncSession, *, user_id: int) -> int:
        normalized_user_id = int(user_id)
        return int(
            (
                await session.execute(
                    select(func.count(AdminChangeLog.id)).where(
                        or_(
                            AdminChangeLog.admin_user_id == normalized_user_id,
                            and_(
                                AdminChangeLog.target_type == "user",
                                AdminChangeLog.target_id == str(normalized_user_id),
                            ),
                        )
                    )
                )
            ).scalar_one()
            or 0
        )

    @staticmethod
    def _assert_deletable(user: User, *, audit_count: int) -> None:
        if user.is_admin or int(audit_count) > 0:
            raise _auth_error(
                status.HTTP_403_FORBIDDEN,
                "admin_account_deletion_blocked",
                "관리자 또는 관리자 감사 이력이 있는 계정은 직접 삭제할 수 없습니다.",
            )

    def _normalize_email(self, value: str) -> NormalizedEmail:
        try:
            return self.email_normalizer(value)
        except EmailValidationUnavailable as exc:
            raise _auth_error(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                "email_validation_unavailable",
                "이메일 검증 구성요소가 아직 준비되지 않았습니다.",
            ) from exc
        except ValueError as exc:
            raise _auth_error(
                422,
                "invalid_email",
                "올바른 이메일 주소를 입력해주세요.",
            ) from exc

    def _require_delivery_ready(self) -> None:
        try:
            self.email_outbox.require_ready()
        except RuntimeError as exc:
            code = str(exc)
            if code == "email_token_secret_unavailable":
                raise _auth_error(
                    status.HTTP_503_SERVICE_UNAVAILABLE,
                    code,
                    "이메일 보안 설정이 아직 준비되지 않았습니다.",
                ) from exc
            if code == "auth_abuse_secret_unavailable":
                raise _auth_error(
                    status.HTTP_503_SERVICE_UNAVAILABLE,
                    code,
                    "계정 요청 보호 설정이 아직 준비되지 않았습니다.",
                ) from exc
            raise _auth_error(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                "email_delivery_unavailable",
                "이메일 발송 설정이 아직 준비되지 않았습니다.",
            ) from exc

    def digest_email_token(self, raw_token: str) -> str:
        try:
            return self.email_outbox.digest_email_token(raw_token)
        except RuntimeError as exc:
            raise _auth_error(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                "email_token_secret_unavailable",
                "이메일 보안 설정이 아직 준비되지 않았습니다.",
            ) from exc

    async def _finish_discovery_delay(self, started_at: float) -> None:
        jitter_ms = (
            secrets.randbelow(self.discovery_jitter_ms + 1)
            if self.discovery_jitter_ms > 0
            else 0
        )
        target_seconds = max(0, self.discovery_floor_ms + jitter_ms) / 1000
        remaining = target_seconds - max(0.0, self.monotonic_factory() - started_at)
        if remaining > 0:
            await self.sleep(remaining)

    def _now(self) -> datetime:
        return _as_utc(self.now_factory())

    @staticmethod
    def mask_email(value: str | None) -> str | None:
        email = str(value or "").strip()
        if "@" not in email:
            return None
        local, domain = email.rsplit("@", 1)
        if not local or not domain:
            return None
        visible = local[:1]
        return f"{visible}{'*' * max(3, min(len(local) - 1, 8))}@{domain}"

    @staticmethod
    def _generic_discovery_result(kind: str) -> dict[str, Any]:
        return {
            "status": "accepted",
            "request": kind,
            "accountDisclosed": False,
            "emailRequestAccepted": True,
        }

    @staticmethod
    def _invalid_credentials() -> HTTPException:
        return _auth_error(
            status.HTTP_401_UNAUTHORIZED,
            "invalid_credentials",
            "아이디 또는 비밀번호가 올바르지 않습니다.",
        )
