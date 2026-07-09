from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICE = ROOT / "backend/app/services/admin_service.py"
CREATE_SERVICE = ROOT / "backend/app/services/admin/admin_create_lifecycle_service.py"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_contains(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"missing expected text: {needle}")


def main() -> None:
    service = read(SERVICE)
    create_service = read(CREATE_SERVICE)

    assert_contains(service, "async def _ensure_admin_change_log_schema")
    assert_contains(service, "CREATE TABLE IF NOT EXISTS admin_change_logs")
    assert_contains(service, "ALTER TABLE admin_change_logs ADD COLUMN IF NOT EXISTS rollback_json")
    assert_contains(service, "CREATE INDEX IF NOT EXISTS ix_admin_change_logs_target_type")
    assert_contains(service, "await self._ensure_admin_change_log_schema(session)")
    assert_contains(service, "async def list_admin_change_logs")
    assert_contains(service, "async def get_admin_change_log_detail")
    assert_contains(service, "async def preview_admin_change_log_rollback")
    assert_contains(service, "async def apply_master_data_edit")
    assert_contains(service, "async def apply_admin_change_log_rollback")

    assert_contains(create_service, "async def preview_admin_create_delete_rollback")
    assert_contains(create_service, "async def preview_admin_create_delete_restore")
    assert_contains(create_service, "async def apply_master_data_create")
    assert_contains(create_service, "await self._ensure_admin_change_log_schema(session)")

    print("backend admin change-log schema guard smoke test passed")


if __name__ == "__main__":
    main()
