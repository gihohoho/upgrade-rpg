#!/usr/bin/env python3
"""Smoke check for the v377 backend route map report."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/report_backend_route_map.py"
REPORT = ROOT / "docs/generated/BACKEND_ROUTE_MAP.md"
ADMIN_API = ROOT / "frontend/vue-app/src/api/adminReadOnlyApi.js"
RUN_SMOKE = ROOT / "tools/run_smoke_core.sh"

REQUIRED_TEXT = [
    "Backend Route Map — v377",
    "latest: v380.vue-auth-character-gate",
    "strict result: vue-auth-character-gate",
    "actual target v377 apply: local 1 / Neon 1",
    "private email environment: prepared",
    "source 8db9bcb / preserved",
    "source 345872a / verified",
    "protection store available / legacy no-email login compatible",
    "Naver delivery / link verification / login verified",
    "local multi-worker ownership diagnosed / direct provider healthy",
    "recovery2 roundtrip/Neon backup/apply: verified / one attempt each",
    "public backend/static: v377/v378 live",
    "v377 이메일 계정 gate, 캐릭터 슬롯, 저장 브리지",
    "전체 route 수 | 48",
    "`DELETE` | 1",
    "`GET` | 21",
    "`POST` | 26",
    "중복 method/path | 0",
    "GET /api/v1/health",
    "POST /api/v1/auth/register",
    "POST /api/v1/auth/verify-email",
    "POST /api/v1/auth/request-password-reset",
    "GET /api/v1/auth/account-deletion/preview",
    "POST /api/v1/auth/account-deletion/confirm",
    "GET /api/v1/auth/me",
    "GET /api/v1/account/characters",
    "DELETE /api/v1/account/characters/{account_character_id}",
    "GET /api/v1/account-admin/users",
    "GET /api/v1/admin/master-data/domains",
    "GET /api/v1/admin/master-data/detail",
    "GET /api/v1/admin/master-data/relations",
    "POST /api/v1/admin/master-data/create-apply",
    "POST /api/v1/game/save",
    "query 이름은 `id`",
    "migrate-vue-admin-auth-routing",
]

FORBIDDEN_TEXT = [
    "route path를 변경",
    "API 응답 body 변경",
    "Preview/Apply 요청 body 변경",
]


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def main() -> int:
    for path in [TOOL, REPORT, ADMIN_API]:
        if not path.exists():
            return fail(f"missing file: {path.relative_to(ROOT).as_posix()}")

    result = subprocess.run(
        [sys.executable, str(TOOL.relative_to(ROOT)), "--check"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        sys.stdout.write(result.stdout)
        sys.stderr.write(result.stderr)
        return fail("backend route map report is not up to date")

    report = REPORT.read_text(encoding="utf-8")
    for needle in REQUIRED_TEXT:
        if needle not in report:
            return fail(f"report missing required text: {needle}")
    for needle in FORBIDDEN_TEXT:
        if needle in report:
            return fail(f"report contains unsafe wording: {needle}")

    admin_api = ADMIN_API.read_text(encoding="utf-8")
    if "query: { domain, id: rowId }" not in admin_api:
        return fail("master detail wrapper must translate rowId to backend query id")
    if "query: { domain, id: rowId, limit }" not in admin_api:
        return fail("master relations wrapper must translate rowId to backend query id")
    if "query: { domain, rowId }" in admin_api or "query: { domain, rowId, limit }" in admin_api:
        return fail("admin read-only API must not send rowId as backend query name")

    run_smoke = RUN_SMOKE.read_text(encoding="utf-8")
    if "smoke_backend_route_map_report.py" not in run_smoke:
        return fail("core smoke should include v377 route map report smoke")

    print("OK: backend route map report smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
