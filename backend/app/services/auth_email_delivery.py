from __future__ import annotations

from dataclasses import dataclass
from html import escape
import json
import socket
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import HTTPRedirectHandler, Request, build_opener

from starlette.concurrency import run_in_threadpool

from app.core.config import Settings, settings


BREVO_SEND_EMAIL_URL = "https://api.brevo.com/v3/smtp/email"
BREVO_RESPONSE_MAX_BYTES = 64 * 1024


class EmailDeliveryError(RuntimeError):
    """Safe provider error that never contains credentials, tokens, or response bodies."""

    def __init__(self, code: str):
        self.code = str(code or "email_delivery_failed")[:80]
        super().__init__(self.code)


@dataclass(frozen=True)
class RenderedAuthEmail:
    subject: str
    html_content: str
    text_content: str


@dataclass(frozen=True)
class EmailDeliveryResult:
    provider: str
    message_id: str


class _RejectRedirectHandler(HTTPRedirectHandler):
    """Keep the Brevo credential bound to the one source-controlled API host."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        return None


def build_auth_action_url(action: str, token: str, *, origin: str | None = None) -> str:
    allowed_actions = {"verify-email", "reset-password", "delete-account"}
    if action not in allowed_actions:
        raise ValueError("unsupported_auth_email_action")
    raw_token = str(token or "").strip()
    if not raw_token or any(character.isspace() for character in raw_token):
        raise ValueError("invalid_auth_email_token")
    base = str(origin or settings.public_frontend_origin).strip().rstrip("/")
    return f"{base}/index.html#auth={action}&token={quote(raw_token, safe='')}"


def _render_game_email(
    *,
    subject: str,
    eyebrow: str,
    title: str,
    paragraphs: list[str],
    action_label: str | None = None,
    action_url: str | None = None,
    detail_label: str | None = None,
    detail_value: str | None = None,
    warning: str | None = None,
) -> RenderedAuthEmail:
    safe_subject = str(subject).replace("\r", " ").replace("\n", " ")[:160]
    safe_eyebrow = escape(eyebrow)
    safe_title = escape(title)
    safe_paragraphs = "".join(
        f'<p style="margin:0 0 14px;color:#dbe7ff;font-size:15px;line-height:1.7;">{escape(text)}</p>'
        for text in paragraphs
    )
    detail_html = ""
    if detail_label and detail_value:
        detail_html = (
            '<div style="margin:18px 0;padding:16px;border:1px solid #5177b8;'
            'background:#091528;text-align:center;">'
            f'<div style="color:#8daee8;font-size:12px;letter-spacing:.08em;">{escape(detail_label)}</div>'
            f'<div style="margin-top:7px;color:#fff3a6;font-size:22px;font-weight:800;">{escape(detail_value)}</div>'
            "</div>"
        )
    action_html = ""
    if action_label and action_url:
        safe_url = escape(action_url, quote=True)
        action_html = (
            '<div style="margin:24px 0;text-align:center;">'
            f'<a href="{safe_url}" style="display:inline-block;padding:13px 24px;'
            'border:2px solid #f2ca58;background:#10284a;color:#fff3a6;text-decoration:none;'
            f'font-weight:800;border-radius:4px;">{escape(action_label)}</a></div>'
            f'<p style="margin:0 0 14px;color:#91a7c9;font-size:12px;line-height:1.6;word-break:break-all;">'
            f'버튼이 열리지 않으면 다음 주소를 사용하세요.<br>{safe_url}</p>'
        )
    warning_html = ""
    if warning:
        warning_html = (
            '<div style="margin-top:20px;padding:13px;border-left:4px solid #d96868;'
            f'background:#2a121a;color:#ffd2d2;font-size:13px;line-height:1.6;">{escape(warning)}</div>'
        )

    html_content = f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"></head>
<body style="margin:0;padding:24px;background:#050b14;font-family:Arial,'Malgun Gothic',sans-serif;">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;"><tr><td align="center">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:620px;border:1px solid #375b91;background:#0b1422;border-collapse:collapse;box-shadow:0 0 28px rgba(42,105,190,.28);">
<tr><td style="padding:24px;border-bottom:1px solid #28466f;background:#0d1d34;text-align:center;">
<div style="color:#f2ca58;font-size:13px;font-weight:800;letter-spacing:.16em;">UPGRADE RPG</div>
<div style="margin-top:7px;color:#8db9ff;font-size:12px;">{safe_eyebrow}</div></td></tr>
<tr><td style="padding:28px 30px 30px;">
<h1 style="margin:0 0 20px;color:#ffffff;font-size:25px;line-height:1.35;text-align:center;">{safe_title}</h1>
{safe_paragraphs}{detail_html}{action_html}{warning_html}
<p style="margin:24px 0 0;color:#7185a6;font-size:11px;line-height:1.6;text-align:center;">이 메일은 Upgrade RPG 계정 요청으로 발송되었습니다. 외부 이미지와 웹폰트를 사용하지 않습니다.</p>
</td></tr></table></td></tr></table></body></html>"""

    text_lines = [safe_subject, "", *paragraphs]
    if detail_label and detail_value:
        text_lines.extend(["", f"{detail_label}: {detail_value}"])
    if action_label and action_url:
        text_lines.extend(["", action_label, action_url])
    if warning:
        text_lines.extend(["", f"주의: {warning}"])
    text_lines.extend(["", "Upgrade RPG 계정 메일 · 외부 이미지 및 웹폰트 없음"])
    return RenderedAuthEmail(
        subject=safe_subject,
        html_content=html_content,
        text_content="\n".join(text_lines),
    )


def render_email_verification(*, username: str, action_url: str) -> RenderedAuthEmail:
    return _render_game_email(
        subject="[Upgrade RPG] 이메일 인증을 완료해주세요",
        eyebrow="모험가 등록 확인",
        title="이메일 인증이 필요합니다",
        paragraphs=[
            f"{username} 모험가님의 회원가입이 접수되었습니다.",
            "아래 버튼으로 이메일 소유 확인을 마쳐야 로그인하고 캐릭터를 만들 수 있습니다.",
        ],
        action_label="이메일 인증 완료",
        action_url=action_url,
        warning="직접 요청하지 않았다면 버튼을 누르지 말고 이 메일을 삭제해주세요.",
    )


def render_username_recovery(*, username: str) -> RenderedAuthEmail:
    return _render_game_email(
        subject="[Upgrade RPG] 계정 아이디 안내",
        eyebrow="계정 정보 복구",
        title="요청하신 아이디입니다",
        paragraphs=["가입 이메일과 연결된 Upgrade RPG 아이디를 안내합니다."],
        detail_label="계정 아이디",
        detail_value=username,
        warning="직접 요청하지 않았다면 비밀번호 변경 없이 이 메일을 삭제해도 됩니다.",
    )


def render_password_reset(*, username: str, action_url: str) -> RenderedAuthEmail:
    return _render_game_email(
        subject="[Upgrade RPG] 비밀번호 재설정 안내",
        eyebrow="계정 보안 복구",
        title="새 비밀번호를 설정해주세요",
        paragraphs=[
            f"{username} 모험가님의 비밀번호 재설정 요청을 받았습니다.",
            "아래 버튼은 한 번만 사용할 수 있으며 정해진 시간이 지나면 만료됩니다.",
        ],
        action_label="비밀번호 재설정",
        action_url=action_url,
        warning="직접 요청하지 않았다면 버튼을 누르지 마세요. 현재 비밀번호는 그대로 유지됩니다.",
    )


def render_account_deletion(*, username: str, action_url: str) -> RenderedAuthEmail:
    return _render_game_email(
        subject="[Upgrade RPG] 계정 영구 삭제 확인",
        eyebrow="위험 작업 최종 확인",
        title="계정 삭제를 최종 확인해주세요",
        paragraphs=[
            f"{username} 모험가님의 계정 삭제 요청을 받았습니다.",
            "링크를 연 뒤 확인 문구를 입력해야 삭제되며, 그전까지 계정과 캐릭터는 유지됩니다.",
        ],
        action_label="계정 삭제 최종 확인",
        action_url=action_url,
        warning="삭제 후 캐릭터, 장비, 골드와 서버 저장은 복구할 수 없습니다. 직접 요청하지 않았다면 링크를 누르지 마세요.",
    )


class BrevoEmailDelivery:
    """One-attempt Brevo HTTPS transport with no automatic retry."""

    def __init__(
        self,
        *,
        current_settings: Settings | None = None,
        opener: Callable[..., Any] | None = None,
    ) -> None:
        self.settings = current_settings or settings
        self._opener = opener or build_opener(_RejectRedirectHandler()).open

    async def send(
        self,
        *,
        recipient: str,
        rendered: RenderedAuthEmail,
    ) -> EmailDeliveryResult:
        return await run_in_threadpool(
            self._send_once,
            recipient=recipient,
            rendered=rendered,
        )

    def _send_once(
        self,
        *,
        recipient: str,
        rendered: RenderedAuthEmail,
    ) -> EmailDeliveryResult:
        if not self.settings.brevo_ready:
            raise EmailDeliveryError("email_provider_not_configured")
        safe_recipient = str(recipient or "").strip()
        if not safe_recipient or "\r" in safe_recipient or "\n" in safe_recipient:
            raise EmailDeliveryError("invalid_email_recipient")

        payload = {
            "sender": {
                "name": self.settings.brevo_from_name.strip(),
                "email": self.settings.brevo_from_email.strip(),
            },
            "to": [{"email": safe_recipient}],
            "subject": rendered.subject,
            "htmlContent": rendered.html_content,
            "textContent": rendered.text_content,
        }
        request = Request(
            BREVO_SEND_EMAIL_URL,
            data=json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8"),
            method="POST",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json; charset=utf-8",
                "api-key": self.settings.brevo_api_key.get_secret_value(),
            },
        )
        try:
            with self._opener(
                request,
                timeout=int(self.settings.email_delivery_timeout_seconds),
            ) as response:
                status_code = int(getattr(response, "status", 0) or 0)
                response_bytes = response.read(BREVO_RESPONSE_MAX_BYTES + 1)
        except HTTPError as exc:
            raise EmailDeliveryError(f"brevo_http_{int(exc.code)}") from None
        except (URLError, TimeoutError, socket.timeout, OSError):
            raise EmailDeliveryError("brevo_network_error") from None
        if status_code < 200 or status_code >= 300:
            raise EmailDeliveryError("brevo_unexpected_status")
        if len(response_bytes) > BREVO_RESPONSE_MAX_BYTES:
            raise EmailDeliveryError("brevo_response_too_large")
        try:
            response_json = json.loads(response_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise EmailDeliveryError("brevo_invalid_response") from None
        message_id = response_json.get("messageId") if isinstance(response_json, dict) else None
        if not isinstance(message_id, str) or not message_id.strip():
            raise EmailDeliveryError("brevo_message_id_missing")
        return EmailDeliveryResult(provider="brevo", message_id=message_id.strip()[:160])
