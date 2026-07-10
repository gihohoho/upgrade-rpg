"""Static smoke test for the v083 master-data API implementation.

Run from the project root:

    python tools/smoke/game/smoke_master_data_api_structure.py
"""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def assert_contains(path: Path, snippets: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    missing = [snippet for snippet in snippets if snippet not in text]
    if missing:
        raise AssertionError(f"{path.relative_to(PROJECT_ROOT)} missing snippets: {missing}")


def main() -> None:
    assert_contains(
        PROJECT_ROOT / "backend" / "app" / "api" / "routes" / "game.py",
        [
            "payload=master_data",
            "source\": \"postgresql",
            "includeAssets",
            "Query(",
            "Depends(get_db_session)",
            "GameService",
        ],
    )
    assert_contains(
        PROJECT_ROOT / "backend" / "app" / "services" / "game_service.py",
        [
            "async def get_master_data",
            "include_assets",
            "assetPolicy",
            "_asset_value",
            "itemTemplates",
            "dropTableItems",
            "enhancementRules",
            "serialize_value",
            "select(Boss)",
        ],
    )
    assert_contains(
        PROJECT_ROOT / "backend" / "scripts" / "check_master_data_api.py",
        [
            "DEFAULT_URL",
            "EXPECTED_MINIMUM_COUNTS",
            "ASSET_MARKERS",
            "--include-assets",
            "master-data API check passed",
        ],
    )
    print("master-data API structure smoke test passed")


if __name__ == "__main__":
    main()
