#!/usr/bin/env python3
"""Current handoff contract without duplicating historical release narratives."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
VERSION = "v372.documentation-system-consolidated"
RESULT = "documentation-system-consolidated"
NEXT_STAGE = "owner-approve-email-validator-install-and-review-v371-migration-source"
SOURCE_HEAD = "v371_email_identity_lifecycle"
APPLIED_HEAD = "v295_initial_schema"


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
            APPLIED_HEAD,
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
        "package 설치",
        "migration",
        "DB write",
        "owner bootstrap",
        "docs/reference/",
        "docs/generated/",
        "docs/archive/history/",
    )
    require_markers(
        "docs/current/CURRENT_STATUS.md",
        "source-prepared 즉시 수정 blocker는 없습니다",
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
        "Obsidian",
        ".obsidian/",
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
