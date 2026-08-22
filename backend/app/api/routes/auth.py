from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_errors import AuthFlowHTTPException, auth_error
from app.core.response import ok_response
from app.core.security import CurrentUser, get_current_user
from app.db.session import get_db_session
from app.schemas.auth import (
    AccountDeletionConfirmRequest,
    AccountDeletionRequest,
    EmailRequest,
    EmailTokenRequest,
    LoginRequest,
    PasswordResetRequest,
    RegisterRequest,
)
from app.services.auth_service import AuthService
from app.services.auth_request_protection import (
    AUTH_IP_PROTECTION_STATE_KEY,
    AuthIPProtectionState,
    AuthProtectionContext,
    AuthProtectionUnavailable,
    AuthRateLimited,
    auth_request_protection,
    combine_auth_protection_contexts,
)


router = APIRouter()
service = AuthService()
protection = auth_request_protection


async def _check_protection(
    *,
    request: Request,
    action: str,
    subject_kind: str,
    subject_value: str | int,
) -> AuthProtectionContext:
    try:
        request_state = request.scope.get("state")
        ip_state = (
            request_state.get(AUTH_IP_PROTECTION_STATE_KEY)
            if isinstance(request_state, dict)
            else None
        )
        if (
            not isinstance(ip_state, AuthIPProtectionState)
            or ip_state.action != action
            or ip_state.protection is not protection
        ):
            raise AuthProtectionUnavailable("auth_ip_context_missing_or_mismatched")
        subject_context = await protection.check_subject(
            action=action,
            subject_kind=subject_kind,  # type: ignore[arg-type]
            subject_value=subject_value,
        )
        return combine_auth_protection_contexts(ip_state.context, subject_context)
    except AuthRateLimited as exc:
        retry_after = str(exc.retry_after_seconds)
        raise auth_error(
            429,
            "auth_rate_limited",
            "요청이 너무 많습니다. 잠시 후 다시 시도해주세요.",
            headers={"Retry-After": retry_after, "Cache-Control": "no-store"},
        ) from exc
    except AuthProtectionUnavailable as exc:
        if str(exc) == "email_validation_unavailable":
            raise auth_error(
                503,
                "email_validation_unavailable",
                "이메일 검증 구성요소가 아직 준비되지 않았습니다.",
                headers={"Cache-Control": "no-store"},
            ) from exc
        raise auth_error(
            503,
            "auth_protection_unavailable",
            "계정 요청 보호 기능을 확인할 수 없습니다. 잠시 후 다시 시도해주세요.",
            headers={"Cache-Control": "no-store"},
        ) from exc


async def _record_failure(context: AuthProtectionContext) -> None:
    try:
        await protection.record_failure(context)
    except AuthProtectionUnavailable as exc:
        raise auth_error(
            503,
            "auth_protection_unavailable",
            "계정 요청 보호 기능을 확인할 수 없습니다. 잠시 후 다시 시도해주세요.",
            headers={"Cache-Control": "no-store"},
        ) from exc


async def _record_success(context: AuthProtectionContext) -> None:
    try:
        await protection.record_success(context)
    except AuthProtectionUnavailable as exc:
        raise auth_error(
            503,
            "auth_protection_unavailable",
            "계정 요청 보호 기능을 확인할 수 없습니다. 잠시 후 다시 시도해주세요.",
            headers={"Cache-Control": "no-store"},
        ) from exc


def _email_meta(note: str) -> dict[str, object]:
    return {
        "emailProvider": "brevo-https",
        "deliveryMode": "durable-semantic-outbox-single-attempt",
        "tokenStorage": "single-use-hmac-digest-only",
        "rawTokenReturned": False,
        "note": note,
    }


@router.post("/register", status_code=status.HTTP_202_ACCEPTED)
async def register(
    request: Request,
    payload: RegisterRequest,
    session: AsyncSession = Depends(get_db_session),
):
    await _check_protection(
        request=request,
        action="register",
        subject_kind="email",
        subject_value=payload.email,
    )
    registered = await service.register(session, payload)
    return ok_response(
        type="auth.register",
        payload=registered,
        data={"status": "verification_required", "user": registered["user"]},
        meta=_email_meta("이메일 인증을 완료하기 전에는 access token을 발급하지 않습니다."),
    )


@router.post("/login")
async def login(
    request: Request,
    payload: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
):
    rate_context = await _check_protection(
        request=request,
        action="login",
        subject_kind="identifier",
        subject_value=payload.identifier,
    )
    try:
        authenticated = await service.login(session, payload)
    except AuthFlowHTTPException as exc:
        code = str(exc.detail.get("code") if isinstance(exc.detail, dict) else "")
        if code == "invalid_credentials":
            await _record_failure(rate_context)
        elif code in {"account_suspended", "email_verification_required"}:
            await _record_success(rate_context)
        raise
    await _record_success(rate_context)
    return ok_response(
        type="auth.login",
        payload=authenticated,
        data={"status": "authenticated", "user": authenticated["user"]},
        meta={"authMode": "bearer-signed-access-token", "authVersionBound": True},
    )


@router.post("/verify-email")
async def verify_email(
    request: Request,
    payload: EmailTokenRequest,
    session: AsyncSession = Depends(get_db_session),
):
    raw_token = payload.token.get_secret_value()
    rate_context = await _check_protection(
        request=request,
        action="verify-email",
        subject_kind="token",
        subject_value=raw_token,
    )
    try:
        verified = await service.verify_email(session, payload)
    except AuthFlowHTTPException as exc:
        code = str(exc.detail.get("code") if isinstance(exc.detail, dict) else "")
        if code == "email_action_token_invalid":
            await _record_failure(rate_context)
        raise
    await _record_success(rate_context)
    return ok_response(
        type="auth.verify_email",
        payload=verified,
        data={"status": verified["status"]},
        meta=_email_meta("HMAC digest가 일치하는 미사용·미만료 토큰을 user-first row lock 안에서 한 번만 사용합니다."),
    )


@router.post("/resend-verification", status_code=status.HTTP_202_ACCEPTED)
async def resend_verification(
    request: Request,
    payload: EmailRequest,
    session: AsyncSession = Depends(get_db_session),
):
    await _check_protection(
        request=request,
        action="resend-verification",
        subject_kind="email",
        subject_value=payload.email,
    )
    accepted = await service.resend_verification(session, payload)
    return ok_response(
        type="auth.resend_verification",
        payload=accepted,
        data={"status": "accepted"},
        meta=_email_meta("계정 존재 여부와 실제 발송 여부를 응답으로 구분하지 않습니다."),
    )


@router.post("/recover-username", status_code=status.HTTP_202_ACCEPTED)
async def recover_username(
    request: Request,
    payload: EmailRequest,
    session: AsyncSession = Depends(get_db_session),
):
    await _check_protection(
        request=request,
        action="recover-username",
        subject_kind="email",
        subject_value=payload.email,
    )
    accepted = await service.recover_username(session, payload)
    return ok_response(
        type="auth.recover_username",
        payload=accepted,
        data={"status": "accepted"},
        meta=_email_meta("계정 존재 여부와 실제 발송 여부를 응답으로 구분하지 않습니다."),
    )


@router.post("/request-password-reset", status_code=status.HTTP_202_ACCEPTED)
async def request_password_reset(
    request: Request,
    payload: EmailRequest,
    session: AsyncSession = Depends(get_db_session),
):
    await _check_protection(
        request=request,
        action="request-password-reset",
        subject_kind="email",
        subject_value=payload.email,
    )
    accepted = await service.request_password_reset(session, payload)
    return ok_response(
        type="auth.request_password_reset",
        payload=accepted,
        data={"status": "accepted"},
        meta=_email_meta("계정 존재 여부와 실제 발송 여부를 응답으로 구분하지 않습니다."),
    )


@router.post("/reset-password")
async def reset_password(
    request: Request,
    payload: PasswordResetRequest,
    session: AsyncSession = Depends(get_db_session),
):
    rate_context = await _check_protection(
        request=request,
        action="reset-password",
        subject_kind="token",
        subject_value=payload.token.get_secret_value(),
    )
    try:
        reset = await service.reset_password(session, payload)
    except AuthFlowHTTPException as exc:
        code = str(exc.detail.get("code") if isinstance(exc.detail, dict) else "")
        if code == "email_action_token_invalid":
            await _record_failure(rate_context)
        raise
    await _record_success(rate_context)
    return ok_response(
        type="auth.reset_password",
        payload=reset,
        data={"status": reset["status"]},
        meta=_email_meta("비밀번호 변경과 authVersion 증가를 같은 DB transaction으로 처리합니다."),
    )


@router.get("/me")
async def get_me(current_user: CurrentUser = Depends(get_current_user)):
    user = service.serialize_current_user(current_user)
    return ok_response(
        type="auth.me",
        payload={"status": "authenticated", "user": user},
        data={"status": "authenticated", "user": user},
        meta={"authMode": "bearer-signed-access-token", "authVersionBound": True},
    )


@router.post("/logout")
async def logout(current_user: CurrentUser = Depends(get_current_user)):
    return ok_response(
        type="auth.logout",
        payload={
            "status": "client_token_discard_required",
            "userId": current_user.id,
            "serverRevoked": False,
        },
        data={"status": "logged_out_on_client"},
        meta={
            "logoutMode": "client-token-discard",
            "note": "비밀번호 재설정 시에는 authVersion 증가로 기존 access token을 모두 폐기합니다.",
        },
    )


@router.get("/account-deletion/preview")
async def preview_account_deletion(
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    preview = await service.preview_account_deletion(
        session,
        current_user=current_user,
    )
    return ok_response(
        type="auth.account_deletion.preview",
        payload=preview,
        data={
            "status": preview["status"],
            "characterCount": preview["characterCount"],
            "saveSnapshotCount": preview["saveSnapshotCount"],
        },
        meta={"readOnly": True, "rawSnapshotReturned": False},
    )


@router.post("/account-deletion/request", status_code=status.HTTP_202_ACCEPTED)
async def request_account_deletion(
    request: Request,
    payload: AccountDeletionRequest,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    rate_context = await _check_protection(
        request=request,
        action="account-deletion-request",
        subject_kind="user",
        subject_value=current_user.id,
    )
    try:
        requested = await service.request_account_deletion(
            session,
            current_user=current_user,
            payload=payload,
        )
    except AuthFlowHTTPException as exc:
        code = str(exc.detail.get("code") if isinstance(exc.detail, dict) else "")
        if code == "invalid_credentials":
            await _record_failure(rate_context)
        raise
    await _record_success(rate_context)
    return ok_response(
        type="auth.account_deletion.request",
        payload=requested,
        data={"status": requested["status"], "accountDeleted": False},
        meta=_email_meta("현재 비밀번호가 맞을 때만 삭제 확인 메일을 한 번 전송합니다."),
    )


@router.post("/account-deletion/confirm")
async def confirm_account_deletion(
    request: Request,
    payload: AccountDeletionConfirmRequest,
    session: AsyncSession = Depends(get_db_session),
):
    rate_context = await _check_protection(
        request=request,
        action="account-deletion-confirm",
        subject_kind="token",
        subject_value=payload.token.get_secret_value(),
    )
    try:
        deleted = await service.confirm_account_deletion(session, payload)
    except AuthFlowHTTPException as exc:
        code = str(exc.detail.get("code") if isinstance(exc.detail, dict) else "")
        if code in {"email_action_token_invalid", "account_deletion_confirmation_required"}:
            await _record_failure(rate_context)
        raise
    await _record_success(rate_context)
    return ok_response(
        type="auth.account_deletion.confirm",
        payload=deleted,
        data={"status": deleted["status"], "deletedUserId": deleted["deletedUserId"]},
        meta={
            "hardDelete": True,
            "adminDeleteBlocked": True,
            "localCacheCleanupRequired": True,
            "rawTokenReturned": False,
        },
    )
