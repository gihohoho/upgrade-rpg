from __future__ import annotations

from datetime import UTC, datetime, timedelta
import hashlib
import hmac
import secrets
from typing import Any, Callable

from fastapi import HTTPException, status
from sqlalchemy import and_, delete, func, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.core.config import LOCAL_EMAIL_TOKEN_SECRET, settings
from app.core.security import CurrentUser, create_access_token, hash_password, verify_password
from app.models import AdminChangeLog, User, UserEmailActionToken, UserProfile, UserSaveSnapshot
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
from app.services.auth_email_delivery import (
    BrevoEmailDelivery,
    EmailDeliveryError,
    build_auth_action_url,
    render_account_deletion,
    render_email_verification,
    render_password_reset,
    render_username_recovery,
)


EMAIL_PURPOSE_VERIFY = "verify_email"
EMAIL_PURPOSE_PASSWORD_RESET = "password_reset"
EMAIL_PURPOSE_ACCOUNT_DELETION = "account_deletion"
ACCOUNT_CHARACTER_SLOT_KEYS = tuple(f"character-{index}" for index in range(1, 9))


class AuthFlowHTTPException(HTTPException):
    """HTTP error carrying a stable, non-sensitive account-flow code."""


def _auth_error(status_code: int, code: str, message: str) -> AuthFlowHTTPException:
    return AuthFlowHTTPException(
        status_code=status_code,
        detail={"code": str(code), "message": str(message)},
    )


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
    ) -> None:
        self.email_delivery = email_delivery or BrevoEmailDelivery()
        self.email_normalizer = email_normalizer or normalize_email_identity
        self.token_secret = (
            str(token_secret).strip()
            if token_secret is not None
            else settings.email_token_secret.get_secret_value().strip()
        )
        self.token_factory = token_factory or (lambda: secrets.token_urlsafe(32))
        self.now_factory = now_factory or (lambda: datetime.now(UTC))
        self.provider_ready = settings.brevo_ready if provider_ready is None else bool(provider_ready)
        self.public_frontend_origin = str(
            public_frontend_origin or settings.public_frontend_origin
        ).rstrip("/")

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
            recovered = await self._retry_pending_registration(
                session,
                payload=payload,
                identity=identity,
                candidate=exact_existing,
            )
            if recovered is not None:
                return recovered
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
            raw_token, token_row = self._new_token_row(
                user_id=int(user.id),
                purpose=EMAIL_PURPOSE_VERIFY,
                expires_in_minutes=int(settings.email_verification_expire_minutes),
            )
            session.add(token_row)
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

        registered_user = self.serialize_user(user)
        try:
            await self._deliver_action_token(
                session,
                user=user,
                token_row=token_row,
                raw_token=raw_token,
            )
        except EmailDeliveryError as exc:
            raise _auth_error(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                "verification_email_delivery_failed",
                "인증 메일을 보내지 못했습니다. 잠시 후 다시 요청해주세요.",
            ) from exc
        return self._verification_required_result(registered_user)

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

        registered_user = self.serialize_user(locked_user)
        try:
            await self._create_and_deliver_for_locked_user(
                session,
                user=locked_user,
                purpose=EMAIL_PURPOSE_VERIFY,
                expires_in_minutes=int(settings.email_verification_expire_minutes),
                hide_delivery_failure=False,
            )
        except EmailDeliveryError as exc:
            raise _auth_error(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                "verification_email_delivery_failed",
                "인증 메일을 보내지 못했습니다. 잠시 후 다시 요청해주세요.",
            ) from exc
        return self._verification_required_result(registered_user)

    @staticmethod
    async def _dummy_registration_password_check(payload: RegisterRequest) -> None:
        await run_in_threadpool(
            hash_password,
            payload.password.get_secret_value(),
        )

    @staticmethod
    def _verification_required_result(user: dict[str, Any]) -> dict[str, Any]:
        return {
            "status": "verification_required",
            "user": dict(user),
            "accessTokenIssued": False,
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
        identity = self._normalize_email(payload.email)
        self._require_delivery_ready()
        user = (
            await session.execute(
                select(User).where(User.email_canonical == identity.canonical)
            )
        ).scalar_one_or_none()
        if user and user.is_active and user.password_hash and not user.email_verified_at:
            await self._issue_and_deliver(
                session,
                user=user,
                purpose=EMAIL_PURPOSE_VERIFY,
                expires_in_minutes=int(settings.email_verification_expire_minutes),
                hide_delivery_failure=True,
            )
        return self._generic_discovery_result("verification_email_if_eligible")

    async def recover_username(
        self,
        session: AsyncSession,
        payload: EmailRequest,
    ) -> dict[str, Any]:
        identity = self._normalize_email(payload.email)
        self._require_delivery_ready()
        user = (
            await session.execute(
                select(User).where(User.email_canonical == identity.canonical)
            )
        ).scalar_one_or_none()
        recipient: str | None = None
        username: str | None = None
        if user and user.is_active and user.password_hash and user.email_verified_at:
            recipient = str(user.email_canonical)
            username = str(user.username)
        await session.rollback()
        if recipient and username:
            try:
                await self.email_delivery.send(
                    recipient=recipient,
                    rendered=render_username_recovery(username=username),
                )
            except EmailDeliveryError:
                pass
        return self._generic_discovery_result("username_email_if_eligible")

    async def request_password_reset(
        self,
        session: AsyncSession,
        payload: EmailRequest,
    ) -> dict[str, Any]:
        identity = self._normalize_email(payload.email)
        self._require_delivery_ready()
        user = (
            await session.execute(
                select(User).where(User.email_canonical == identity.canonical)
            )
        ).scalar_one_or_none()
        if user and user.is_active and user.password_hash and user.email_verified_at:
            await self._issue_and_deliver(
                session,
                user=user,
                purpose=EMAIL_PURPOSE_PASSWORD_RESET,
                expires_in_minutes=int(settings.password_reset_expire_minutes),
                hide_delivery_failure=True,
            )
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
            await self._issue_and_deliver(
                session,
                user=user,
                purpose=EMAIL_PURPOSE_ACCOUNT_DELETION,
                expires_in_minutes=int(settings.account_deletion_expire_minutes),
                hide_delivery_failure=False,
            )
        except EmailDeliveryError as exc:
            raise _auth_error(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                "account_deletion_email_delivery_failed",
                "계정 삭제 확인 메일을 보내지 못했습니다. 잠시 후 다시 시도해주세요.",
            ) from exc
        return {
            "status": "confirmation_email_sent",
            "accountDeleted": False,
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

    async def _issue_and_deliver(
        self,
        session: AsyncSession,
        *,
        user: User,
        purpose: str,
        expires_in_minutes: int,
        hide_delivery_failure: bool,
    ) -> None:
        locked_user = (
            await session.execute(
                select(User)
                .where(User.id == int(user.id))
                .execution_options(populate_existing=True)
                .with_for_update()
            )
        ).scalar_one_or_none()
        if locked_user is None:
            await session.rollback()
            raise _auth_error(
                status.HTTP_404_NOT_FOUND,
                "account_not_found",
                "계정을 찾을 수 없습니다.",
            )
        user = locked_user
        await self._create_and_deliver_for_locked_user(
            session,
            user=user,
            purpose=purpose,
            expires_in_minutes=expires_in_minutes,
            hide_delivery_failure=hide_delivery_failure,
        )

    async def _create_and_deliver_for_locked_user(
        self,
        session: AsyncSession,
        *,
        user: User,
        purpose: str,
        expires_in_minutes: int,
        hide_delivery_failure: bool,
    ) -> None:
        now = self._now()
        raw_token, token_row = self._new_token_row(
            user_id=int(user.id),
            purpose=purpose,
            expires_in_minutes=expires_in_minutes,
            now=now,
        )
        session.add(token_row)
        try:
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        try:
            await self._deliver_action_token(
                session,
                user=user,
                token_row=token_row,
                raw_token=raw_token,
            )
        except EmailDeliveryError:
            if not hide_delivery_failure:
                raise

    async def _deliver_action_token(
        self,
        session: AsyncSession,
        *,
        user: User,
        token_row: UserEmailActionToken,
        raw_token: str,
    ) -> None:
        attempted_at = self._now()
        rendered = self._render_action_email(user=user, purpose=token_row.purpose, raw_token=raw_token)
        try:
            result = await self.email_delivery.send(
                recipient=str(user.email_canonical),
                rendered=rendered,
            )
        except EmailDeliveryError as exc:
            token_row.delivery_attempted_at = attempted_at
            token_row.delivery_status = "failed"
            token_row.delivery_error_code = exc.code
            token_row.provider_message_id = None
            token_row.delivered_at = None
            await self._commit_delivery_audit_best_effort(session)
            raise
        token_row.delivery_attempted_at = attempted_at
        token_row.delivery_status = "sent"
        token_row.delivery_error_code = None
        token_row.provider_message_id = str(result.message_id)[:160]
        token_row.delivered_at = self._now()
        await self._commit_delivery_audit_best_effort(session)

    @staticmethod
    async def _commit_delivery_audit_best_effort(session: AsyncSession) -> None:
        """Persist provider audit fields without changing the provider outcome."""
        try:
            await session.commit()
        except Exception:
            try:
                await session.rollback()
            except Exception:
                pass

    def _render_action_email(
        self,
        *,
        user: User,
        purpose: str,
        raw_token: str,
    ) -> Any:
        actions = {
            EMAIL_PURPOSE_VERIFY: ("verify-email", render_email_verification),
            EMAIL_PURPOSE_PASSWORD_RESET: ("reset-password", render_password_reset),
            EMAIL_PURPOSE_ACCOUNT_DELETION: ("delete-account", render_account_deletion),
        }
        action, renderer = actions[purpose]
        action_url = build_auth_action_url(
            action,
            raw_token,
            origin=self.public_frontend_origin,
        )
        return renderer(username=str(user.username), action_url=action_url)

    def _new_token_row(
        self,
        *,
        user_id: int,
        purpose: str,
        expires_in_minutes: int,
        now: datetime | None = None,
    ) -> tuple[str, UserEmailActionToken]:
        self._require_token_secret()
        raw_token = str(self.token_factory()).strip()
        if (
            len(raw_token) < 32
            or len(raw_token) > 256
            or not raw_token.isascii()
            or any(not (character.isalnum() or character in "_-") for character in raw_token)
        ):
            raise RuntimeError("unsafe_email_token_factory_output")
        issued_at = now or self._now()
        return raw_token, UserEmailActionToken(
            user_id=int(user_id),
            purpose=purpose,
            token_digest=self.digest_email_token(raw_token),
            expires_at=issued_at + timedelta(minutes=max(5, int(expires_in_minutes))),
            delivery_status="pending",
        )

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
        self._require_token_secret()
        if not self.provider_ready:
            raise _auth_error(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                "email_delivery_unavailable",
                "이메일 발송 설정이 아직 준비되지 않았습니다.",
            )

    def _require_token_secret(self) -> None:
        if (
            len(self.token_secret) < 32
            or hmac.compare_digest(self.token_secret, LOCAL_EMAIL_TOKEN_SECRET)
            or hmac.compare_digest(self.token_secret, settings.jwt_secret_key.strip())
        ):
            raise _auth_error(
                status.HTTP_503_SERVICE_UNAVAILABLE,
                "email_token_secret_unavailable",
                "이메일 보안 설정이 아직 준비되지 않았습니다.",
            )

    def digest_email_token(self, raw_token: str) -> str:
        self._require_token_secret()
        return hmac.new(
            self.token_secret.encode("utf-8"),
            str(raw_token).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

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
        }

    @staticmethod
    def _invalid_credentials() -> HTTPException:
        return _auth_error(
            status.HTTP_401_UNAUTHORIZED,
            "invalid_credentials",
            "아이디 또는 비밀번호가 올바르지 않습니다.",
        )
