from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
service = (ROOT / "backend/app/services/admin/admin_change_log_service.py").read_text(encoding="utf-8")
route = (ROOT / "backend/app/api/routes/admin.py").read_text(encoding="utf-8")
client = (ROOT / "src/api/admin/admin-change-logs.js").read_text(encoding="utf-8")
setup = (ROOT / "backend/scripts/setup_dev_db.py").read_text(encoding="utf-8")

assert "from sqlalchemy.exc import SQLAlchemyError" in service, "SQLAlchemyError import missing"
assert "except SQLAlchemyError as exc:" in service or "except SQLAlchemyError:" in service, "change-log schema guard catch missing"
assert "await session.rollback()" in service, "failed PostgreSQL transaction rollback missing"
assert 'status = "schema_unavailable"' in service, "schema_unavailable status missing"
assert "admin_change_logs_schema_unavailable_run_create_schema" in service, "schema unavailable warning missing"
assert '"warnings": logs.get("warnings", [])' in route, "route data warnings missing"
assert "admin_change_logs_route_exception_guarded" in route, "route-level exception guard missing"
assert 'payload.status === "schema_unavailable"' in client, "frontend schema unavailable render guard missing"
assert "python scripts/setup_dev_db.py --create-schema --verify" in client, "frontend recovery command hint missing"
assert '"admin_change_logs": AdminChangeLog' in setup, "setup verify admin_change_logs count missing"

print("admin change logs schema guard smoke test passed")
