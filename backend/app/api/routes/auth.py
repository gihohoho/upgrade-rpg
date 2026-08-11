from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

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


router = APIRouter()
service = AuthService()


def _email_meta(note: str) -> dict[str, object]:
    return {
        "emailProvider": "brevo-https",
        "tokenStorage": "single-use-hmac-digest-only",
        "rawTokenReturned": False,
        "note": note,
    }


@router.post("/register")
async def register(
    payload: RegisterRequest,
    session: AsyncSession = Depends(get_db_session),
):
    registered = await service.register(session, payload)
    return ok_response(
        type="auth.register",
        payload=registered,
        data={"status": "verification_required", "user": registered["user"]},
        meta=_email_meta("이메일 인증을 완료하기 전에는 access token을 발급하지 않습니다."),
    )


@router.post("/login")
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
):
    authenticated = await service.login(session, payload)
    return ok_response(
        type="auth.login",
        payload=authenticated,
        data={"status": "authenticated", "user": authenticated["user"]},
        meta={"authMode": "bearer-signed-access-token", "authVersionBound": True},
    )


@router.post("/verify-email")
async def verify_email(
    payload: EmailTokenRequest,
    session: AsyncSession = Depends(get_db_session),
):
    verified = await service.verify_email(session, payload)
    return ok_response(
        type="auth.verify_email",
        payload=verified,
        data={"status": verified["status"]},
        meta=_email_meta("HMAC digest가 일치하는 미사용·미만료 토큰을 user-first row lock 안에서 한 번만 사용합니다."),
    )


@router.post("/resend-verification", status_code=status.HTTP_202_ACCEPTED)
async def resend_verification(
    payload: EmailRequest,
    session: AsyncSession = Depends(get_db_session),
):
    accepted = await service.resend_verification(session, payload)
    return ok_response(
        type="auth.resend_verification",
        payload=accepted,
        data={"status": "accepted"},
        meta=_email_meta("계정 존재 여부와 실제 발송 여부를 응답으로 구분하지 않습니다."),
    )


@router.post("/recover-username", status_code=status.HTTP_202_ACCEPTED)
async def recover_username(
    payload: EmailRequest,
    session: AsyncSession = Depends(get_db_session),
):
    accepted = await service.recover_username(session, payload)
    return ok_response(
        type="auth.recover_username",
        payload=accepted,
        data={"status": "accepted"},
        meta=_email_meta("계정 존재 여부와 실제 발송 여부를 응답으로 구분하지 않습니다."),
    )


@router.post("/request-password-reset", status_code=status.HTTP_202_ACCEPTED)
async def request_password_reset(
    payload: EmailRequest,
    session: AsyncSession = Depends(get_db_session),
):
    accepted = await service.request_password_reset(session, payload)
    return ok_response(
        type="auth.request_password_reset",
        payload=accepted,
        data={"status": "accepted"},
        meta=_email_meta("계정 존재 여부와 실제 발송 여부를 응답으로 구분하지 않습니다."),
    )


@router.post("/reset-password")
async def reset_password(
    payload: PasswordResetRequest,
    session: AsyncSession = Depends(get_db_session),
):
    reset = await service.reset_password(session, payload)
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


@router.post("/account-deletion/request")
async def request_account_deletion(
    payload: AccountDeletionRequest,
    current_user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    requested = await service.request_account_deletion(
        session,
        current_user=current_user,
        payload=payload,
    )
    return ok_response(
        type="auth.account_deletion.request",
        payload=requested,
        data={"status": requested["status"], "accountDeleted": False},
        meta=_email_meta("현재 비밀번호가 맞을 때만 삭제 확인 메일을 한 번 전송합니다."),
    )


@router.post("/account-deletion/confirm")
async def confirm_account_deletion(
    payload: AccountDeletionConfirmRequest,
    session: AsyncSession = Depends(get_db_session),
):
    deleted = await service.confirm_account_deletion(session, payload)
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
