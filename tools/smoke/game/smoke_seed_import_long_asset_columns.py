"""Static smoke test for long image/icon URL DB columns.

Run from the project root:

    python tools/smoke/game/smoke_seed_import_long_asset_columns.py
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def assert_contains(path: Path, snippets: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    missing = [snippet for snippet in snippets if snippet not in text]
    if missing:
        raise AssertionError(f"{path.relative_to(ROOT)} missing snippets: {missing}")


def assert_not_contains(path: Path, snippets: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    present = [snippet for snippet in snippets if snippet in text]
    if present:
        raise AssertionError(f"{path.relative_to(ROOT)} still contains snippets: {present}")


def main() -> None:
    assert_contains(ROOT / "backend" / "app" / "models" / "item.py", ["icon_url: Mapped[str | None] = mapped_column(Text, nullable=True)"])
    assert_contains(ROOT / "backend" / "app" / "models" / "skill.py", ["icon_url: Mapped[str | None] = mapped_column(Text, nullable=True)"])
    assert_contains(ROOT / "backend" / "app" / "models" / "character.py", ["image_url: Mapped[str | None] = mapped_column(Text, nullable=True)"])
    assert_contains(ROOT / "backend" / "app" / "models" / "boss.py", ["image_url: Mapped[str | None] = mapped_column(Text, nullable=True)"])
    assert_contains(ROOT / "backend" / "scripts" / "setup_dev_db.py", ["--verbose-sql", "echo=args.verbose_sql"])
    assert_not_contains(ROOT / "backend" / "app" / "models" / "item.py", ["icon_url: Mapped[str | None] = mapped_column(String(500)"])
    assert_not_contains(ROOT / "backend" / "app" / "models" / "skill.py", ["icon_url: Mapped[str | None] = mapped_column(String(500)"])
    print("long asset column smoke test passed")


if __name__ == "__main__":
    main()
