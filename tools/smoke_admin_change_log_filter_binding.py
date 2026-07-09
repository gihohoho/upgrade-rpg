#!/usr/bin/env python3
"""Smoke test for AdminService change-log filter binding.

A previous hotfix accidentally left _clean_admin_change_log_filters decorated as
@staticmethod while it still expected self. That made /admin/change-logs fail
before any DB query and bypassed the SQLAlchemy schema guard. This test catches
that exact regression without requiring a running PostgreSQL server.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.admin_service import AdminService  # noqa: E402


def main() -> None:
    service = AdminService()
    filters = service._clean_admin_change_log_filters(
        target_type="itemTemplates",
        target_id="123",
        action="update",
        changed_key="name",
        applied=True,
        sort="created_desc",
    )
    assert filters["targetType"] == "itemTemplates"
    assert filters["targetId"] == "123"
    assert filters["action"] == "update"
    assert filters["changedKey"] == "name"
    assert filters["applied"] is True
    assert filters["sort"] == "created_desc"
    assert filters["hasActiveFilters"] is True
    print("smoke_admin_change_log_filter_binding: OK")


if __name__ == "__main__":
    main()
