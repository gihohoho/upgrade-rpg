from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def read_required(relative_path: str) -> str:
    path = ROOT / relative_path
    if not path.exists():
        raise AssertionError(f"missing required handoff file: {relative_path}")
    return path.read_text(encoding="utf-8")


def assert_contains(relative_path: str, *needles: str) -> None:
    text = read_required(relative_path)
    for needle in needles:
        if needle not in text:
            raise AssertionError(f"{relative_path} missing expected text: {needle}")


def main() -> None:
    required_files = [
        "NEXT_CHAT_PROMPT.md",
        "NEXT_CHAT_HANDOFF.md",
        "README.md",
        "README_BACKEND_READY.md",
        "docs/README.md",
        "docs/CURRENT_STATUS.md",
        "docs/NEXT_STEPS.md",
        "docs/PROJECT_STRUCTURE.md",
        "docs/NEXT_CHAT_START_GUIDE.md",
        "docs/current/CURRENT_STATUS.md",
        "docs/current/POSTGRES_SCHEMA_EQUIVALENCE_CHECK.md",
        "docs/current/POSTGRES_ALEMBIC_BASELINE_STRATEGY.md",
        "docs/current/POSTGRES_BACKUP_RESTORE_PREP.md",
    ]
    for relative_path in required_files:
        read_required(relative_path)

    assert_contains(
        "NEXT_CHAT_PROMPT.md",
        "rpg_v289_postgres_float_normalization_handoff_ready.zip",
        "v289.postgres-float-type-normalization-handoff",
        "backend/.venv",
        "v290",
    )
    assert_contains(
        "NEXT_CHAT_HANDOFF.md",
        "FLOAT",
        "DOUBLE PRECISION",
        "748",
        "기존 데이터 보존형",
    )
    assert_contains(
        "docs/README.md",
        "현재 문서",
        "인수인계",
        "archive",
    )
    assert_contains(
        "docs/NEXT_CHAT_START_GUIDE.md",
        "backend/.venv",
        "check_postgres_schema_equivalence.py",
        "run_smoke_core.sh",
    )

    print("next chat handoff smoke test passed")


if __name__ == "__main__":
    main()
