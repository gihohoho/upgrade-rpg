"""Static smoke test for v208/v210 backend admin route response helper cleanup.

Run from the project root:

    python tools/smoke_backend_admin_route_response_helper.py
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTE = ROOT / "backend/app/api/routes/admin.py"
HELPER = ROOT / "backend/app/api/routes/admin_response_helpers.py"
CONTRACT = ROOT / "backend/app/services/admin_service_split_contract.py"
ENTRY = ROOT / "src/api/admin-page-readonly.js"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


route = read(ROUTE)
helper = read(HELPER)
contract = read(CONTRACT)
entry = read(ENTRY)

required_routes = [
    '@router.get("/requirements")',
    '@router.get("/overview")',
    '@router.get("/master-data/domains")',
    '@router.get("/master-data/catalog")',
    '@router.get("/master-data/create-blueprint")',
    '@router.post("/master-data/create-preview")',
    '@router.post("/master-data/create-apply")',
    '@router.get("/master-data/detail")',
    '@router.get("/master-data/relations")',
    '@router.post("/master-data/edit-preview")',
    '@router.post("/master-data/edit-apply")',
    '@router.get("/change-logs")',
    '@router.get("/change-logs/{change_log_id}")',
    '@router.post("/change-logs/{change_log_id}/create-delete-preview")',
    '@router.post("/change-logs/{change_log_id}/create-delete-apply")',
    '@router.post("/change-logs/{change_log_id}/create-delete-restore-preview")',
    '@router.post("/change-logs/{change_log_id}/create-delete-restore-apply")',
    '@router.post("/change-logs/{change_log_id}/rollback-preview")',
    '@router.post("/change-logs/{change_log_id}/rollback-apply")',
    '@router.get("/save-snapshots")',
    '@router.post("/change-preview")',
]

for pattern in required_routes:
    assert_true(pattern in route, f"route missing after helper cleanup: {pattern}")

assert_true("from app.api.routes.admin_response_helpers import admin_ok_response" in route, "admin route helper import missing")
assert_true("from app.core.response import ok_response" not in route, "admin route should not import core ok_response directly")
assert_true(route.count("return admin_ok_response(") >= 20, "admin route responses should go through admin_ok_response")
assert_true("def admin_ok_response(type: str" in helper, "admin_ok_response helper signature missing")
assert_true("return ok_response(type=type, **kwargs)" in helper, "helper must preserve ok_response envelope")
assert_true('"splitStatus": "admin-route-data-meta-helpers-v212"' in contract, "backend contract splitStatus should be v212")
assert_true('"backend/app/api/routes/admin_response_helpers.py"' in contract, "helper should be listed in backend split contract")
assert_true('const VERSION = "v212.backend-admin-route-data-meta-helpers"' in entry, "frontend readiness version should be v212")
assert_true('splitStatus: "admin-route-data-meta-helpers-v212"' in entry, "frontend splitStatus should be v212")
assert_true("routeResponseHelperReady" in entry, "frontend route response helper readiness flag missing")
assert_true("routeParamsReady" in entry, "frontend route params readiness flag missing")
assert_true("routeErrorHelperReady" in entry, "frontend route error helper readiness flag missing")

print("backend admin route response helper smoke test passed")
