#!/usr/bin/env python3
"""Current handoff contract without duplicating historical release narratives."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
VERSION = "v377.local-email-auth-unblocked"
RESULT = "local-email-auth-unblocked"
NEXT_STAGE = "configure-v377-local-brevo-provider"
SOURCE_HEAD = "v377_auth_email_public_security"
LOCAL_APPLIED_HEAD = SOURCE_HEAD
NEON_APPLIED_HEAD = "v295_initial_schema"


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"missing handoff file: {relative}")
    return path.read_text(encoding="utf-8")


def require_markers(relative: str, *markers: str) -> None:
    text = read(relative)
    for marker in markers:
        if marker not in text:
            raise AssertionError(f"{relative} missing marker: {marker}")


def main() -> int:
    for relative in ("AGENTS.md", "NEXT_CHAT_HANDOFF.md", "docs/current/CURRENT_STATUS.md"):
        require_markers(
            relative,
            VERSION,
            RESULT,
            NEXT_STAGE,
            SOURCE_HEAD,
            LOCAL_APPLIED_HEAD,
            NEON_APPLIED_HEAD,
            "email-validator",
            "Brevo",
            "v351",
        )

    prompt = read("NEXT_CHAT_PROMPT.md")
    for marker in ("AGENTS.md", "NEXT_CHAT_HANDOFF.md", "docs/current/CURRENT_STATUS.md"):
        if marker not in prompt:
            raise AssertionError(f"NEXT_CHAT_PROMPT.md missing reading-order marker: {marker}")
    if "latest:" in prompt:
        raise AssertionError("NEXT_CHAT_PROMPT.md must not duplicate mutable status")

    require_markers(
        "NEXT_CHAT_HANDOFF.md",
        "바로 할 일",
        "Linux runtime/musllinux/dev lock",
        "synthetic fixture",
        "migration",
        "local v377 apply",
        "owner bootstrap",
        "docs/reference/",
        "docs/generated/",
        "docs/archive/history/",
    )
    require_markers(
        "docs/current/CURRENT_STATUS.md",
        "8db9bcb",
        "stale",
        "cross-driver fingerprint",
        "attempt marker",
        "recovery1",
        "인증 POST",
        "Neon",
        "공개 전 필수 보강",
        "rate limit",
        "durable outbox/queue",
        "미인증 계정",
        "실행하지 않은 것",
    )
    require_markers(
        "docs/DOCUMENTATION_SYSTEM.md",
        "AGENTS.md",
        "NEXT_CHAT_HANDOFF.md",
        "docs/generated/",
        "docs/archive/history/",
        "작업 종료 문서 마감",
    )
    require_markers(
        "AGENTS.md",
        "Obsidian의 ignored 로컬 vault 설정",
        "Codex가 탐색 효율 중심으로 유지",
        "비기능 포맷 변경",
        "실행 효율과 자체 피드백",
        "성공한 `git push` 뒤",
    )
    require_markers(
        "NEXT_CHAT_PROMPT.md",
        "configure-v377-local-brevo-provider",
        "다시 전면 감사하지 말고",
    )
    require_markers(
        "NEXT_CHAT_HANDOFF.md",
        "실질적인 이메일 인증 기능 rollout을 승인",
        "이 범위는 다시 승인받지 않습니다",
        "Brevo 가입",
    )

    for obsolete in (
        "docs/handoff",
        "docs/archive/stage-notes",
        "docs/current/ROADMAP.md",
        "docs/current/NEXT_STEPS.md",
    ):
        if (ROOT / obsolete).exists():
            raise AssertionError(f"obsolete documentation path remains: {obsolete}")

    print("next-chat handoff smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
