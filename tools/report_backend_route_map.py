#!/usr/bin/env python3
"""Generate a static FastAPI backend route map without importing the app.

This tool intentionally avoids importing ``app.main``. Importing the app can
create DB engines and require local packages such as asyncpg, which makes a
simple documentation check depend on the developer machine state. Instead, the
report reads the route modules that are already included by ``api_router`` and
extracts FastAPI route decorators from source.

The output is documentation-only. It does not change route paths, request
bodies, response bodies, DB, authentication, or write behavior.
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_VERSION = "v377"
REPORT_PATH = Path("docs/generated/BACKEND_ROUTE_MAP.md")
CONFIG_PATH = Path("backend/app/core/config.py")

ROUTE_MODULES = [
    {
        "group": "health",
        "file": Path("backend/app/api/routes/health.py"),
        "prefix": "",
        "include": "api_router.include_router(health.router, tags=['health'])",
    },
    {
        "group": "game",
        "file": Path("backend/app/api/routes/game.py"),
        "prefix": "/game",
        "include": "api_router.include_router(game.router, prefix='/game', tags=['game'])",
    },
    {
        "group": "auth",
        "file": Path("backend/app/api/routes/auth.py"),
        "prefix": "/auth",
        "include": "api_router.include_router(auth.router, prefix='/auth', tags=['auth'])",
    },
    {
        "group": "account",
        "file": Path("backend/app/api/routes/account.py"),
        "prefix": "/account",
        "include": "api_router.include_router(account.router, prefix='/account', tags=['account'])",
    },
    {
        "group": "account-admin",
        "file": Path("backend/app/api/routes/account_admin.py"),
        "prefix": "/account-admin",
        "include": "api_router.include_router(account_admin.router, prefix='/account-admin', tags=['account-admin'])",
    },
    {
        "group": "admin",
        "file": Path("backend/app/api/routes/admin_overview_snapshot_routes.py"),
        "prefix": "/admin",
        "include": "admin.py include_router(admin_overview_snapshot_router)",
    },
    {
        "group": "admin",
        "file": Path("backend/app/api/routes/admin_master_data_routes.py"),
        "prefix": "/admin",
        "include": "admin.py include_router(admin_master_data_router)",
    },
    {
        "group": "admin",
        "file": Path("backend/app/api/routes/admin_change_log_routes.py"),
        "prefix": "/admin",
        "include": "admin.py include_router(admin_change_log_router)",
    },
]

VUE_SAFE_AUTO_CHECKS = {
    "GET /api/v1/health",
}

LEGACY_ACCOUNT_ACTIVE_ROUTES = {
    "POST /api/v1/auth/register",
    "POST /api/v1/auth/login",
    "POST /api/v1/auth/verify-email",
    "POST /api/v1/auth/resend-verification",
    "POST /api/v1/auth/recover-username",
    "POST /api/v1/auth/request-password-reset",
    "POST /api/v1/auth/reset-password",
    "GET /api/v1/auth/me",
    "POST /api/v1/auth/logout",
    "GET /api/v1/auth/account-deletion/preview",
    "POST /api/v1/auth/account-deletion/request",
    "POST /api/v1/auth/account-deletion/confirm",
    "GET /api/v1/account/characters",
    "POST /api/v1/account/characters",
    "DELETE /api/v1/account/characters/{account_character_id}",
    "GET /api/v1/game/load",
    "GET /api/v1/game/save-slots",
    "POST /api/v1/game/save",
    "GET /api/v1/account-admin/bootstrap-status",
    "POST /api/v1/account-admin/bootstrap",
    "GET /api/v1/account-admin/users",
    "GET /api/v1/account-admin/users/{user_id}",
    "POST /api/v1/account-admin/users/{user_id}/status-preview",
    "POST /api/v1/account-admin/users/{user_id}/status-apply",
}

VUE_READONLY_CANDIDATES = {
    "GET /api/v1/game/master-data",
}

DB_CHECK_ONLY = {
    "GET /api/v1/health/db",
}

QUERY_HINTS = {
    "GET /api/v1/admin/save-snapshots": "limit, userId, slotKey, source, defaultOnly, sort",
    "GET /api/v1/admin/master-data/catalog": "domain, limit, page, query, enabled, sort",
    "GET /api/v1/admin/master-data/create-blueprint": "domain",
    "GET /api/v1/admin/master-data/detail": "domain, id",
    "GET /api/v1/admin/master-data/relations": "domain, id, limit",
    "GET /api/v1/admin/change-logs": "limit, targetType, targetId, action, changedKey, applied, sort",
    "GET /api/v1/admin/change-logs/{change_log_id}": "path: change_log_id; Vue wrapper may expose changeLogId and translate it",
    "GET /api/v1/game/master-data": "includeAssets",
    "GET /api/v1/game/load": "slotKey, accountCharacterId",
    "GET /api/v1/account-admin/users": "page, limit, query, status, sort",
}

PROTECTED_ITEMS = [
    "route path",
    "API response body",
    "Preview/Apply request body",
    "Write Guard",
    "actual write logic",
    "DB schema",
    "env",
    "seed",
    "credential secrecy",
    "existing smoke/contract meaning",
]

ROUTE_DECORATOR_NAMES = {"get", "post", "put", "patch", "delete"}


@dataclass(frozen=True)
class RouteInfo:
    group: str
    source_file: str
    line: int
    method: str
    local_path: str
    prefixed_path: str
    full_path: str
    endpoint: str
    type_marker: str
    migration_status: str
    query_hint: str

    @property
    def key(self) -> str:
        return f"{self.method} {self.full_path}"


def normalize_join(*parts: str) -> str:
    joined = "/".join(str(part).strip("/") for part in parts if str(part).strip("/"))
    return "/" + joined if joined else "/"


def extract_api_prefix(root: Path) -> str:
    config = root / CONFIG_PATH
    if not config.exists():
        return "/api/v1"
    text = config.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r'api_prefix:\s*str\s*=\s*["\']([^"\']+)["\']', text)
    return match.group(1) if match else "/api/v1"


def get_source_segment(source: str, node: ast.AST) -> str:
    try:
        return ast.get_source_segment(source, node) or ""
    except Exception:
        return ""


def extract_type_marker(source_segment: str) -> str:
    match = re.search(r'type\s*=\s*["\']([^"\']+)["\']', source_segment)
    return match.group(1) if match else "-"


def decorator_route(decorator: ast.AST) -> tuple[str, str] | None:
    if not isinstance(decorator, ast.Call):
        return None
    func = decorator.func
    if not isinstance(func, ast.Attribute):
        return None
    if not isinstance(func.value, ast.Name) or func.value.id != "router":
        return None
    method = func.attr.lower()
    if method not in ROUTE_DECORATOR_NAMES:
        return None
    if not decorator.args or not isinstance(decorator.args[0], ast.Constant):
        return None
    value = decorator.args[0].value
    if not isinstance(value, str):
        return None
    return method.upper(), value


def route_status(key: str, method: str, path: str) -> str:
    lowered = path.lower()
    if key in VUE_SAFE_AUTO_CHECKS:
        return "Vue 자동 smoke 화면 사용 중"
    if key in LEGACY_ACCOUNT_ACTIVE_ROUTES:
        return "legacy 계정/관리자 화면 사용 중"
    if key in DB_CHECK_ONLY:
        return "DB 연결 확인용 GET, 자동 화면 연결 보류"
    if key in VUE_READONLY_CANDIDATES:
        return "Vue read-only 후보"
    if method != "GET" and "preview" in lowered:
        return "POST preview 후보, 요청 body 계약/화면 설계 전 보류"
    if method != "GET" and ("apply" in lowered or lowered.endswith("/save")):
        return "write/Apply 계열, 인증/Write Guard 설계 전 보류"
    if method != "GET":
        return "비-GET route, Vue read-only 범위 밖"
    return "GET route, 추가 검토 필요"


def collect_routes(root: Path) -> list[RouteInfo]:
    api_prefix = extract_api_prefix(root)
    routes: list[RouteInfo] = []
    for module in ROUTE_MODULES:
        source_path = root / module["file"]
        source_text = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source_text, filename=source_path.as_posix())
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in node.decorator_list:
                route = decorator_route(decorator)
                if route is None:
                    continue
                method, local_path = route
                prefixed_path = normalize_join(module["prefix"], local_path)
                full_path = normalize_join(api_prefix, prefixed_path)
                key = f"{method} {full_path}"
                segment = get_source_segment(source_text, node)
                routes.append(
                    RouteInfo(
                        group=str(module["group"]),
                        source_file=module["file"].as_posix(),
                        line=getattr(decorator, "lineno", getattr(node, "lineno", 0)),
                        method=method,
                        local_path=local_path,
                        prefixed_path=prefixed_path,
                        full_path=full_path,
                        endpoint=node.name,
                        type_marker=extract_type_marker(segment),
                        migration_status=route_status(key, method, full_path),
                        query_hint=QUERY_HINTS.get(key, "-"),
                    )
                )
    return sorted(routes, key=lambda item: (item.full_path, item.method, item.source_file, item.line))


def table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        rows = [["-"] * len(headers)]
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        out.append("| " + " | ".join(row) + " |")
    return "\n".join(out)


def route_rows(routes: list[RouteInfo]) -> list[list[str]]:
    return [
        [
            f"`{route.method}`",
            f"`{route.full_path}`",
            f"`{route.endpoint}`",
            f"`{route.source_file}:{route.line}`",
            route.type_marker,
            route.migration_status,
        ]
        for route in routes
    ]


def candidate_rows(routes: list[RouteInfo], *, status: str) -> list[list[str]]:
    return [
        [
            f"`{route.method} {route.full_path}`",
            route.group,
            route.query_hint,
            route.type_marker,
            f"`{route.endpoint}`",
        ]
        for route in routes
        if route.migration_status == status
    ]


def hold_rows(routes: list[RouteInfo]) -> list[list[str]]:
    return [
        [
            f"`{route.method} {route.full_path}`",
            route.group,
            route.type_marker,
            route.migration_status,
        ]
        for route in routes
        if route.migration_status
        not in {
            "Vue 자동 smoke 화면 사용 중",
            "legacy 계정/관리자 화면 사용 중",
            "Vue read-only 후보",
        }
    ]


def render_report(root: Path) -> str:
    routes = collect_routes(root)
    method_counts: dict[str, int] = {}
    group_counts: dict[str, int] = {}
    for route in routes:
        method_counts[route.method] = method_counts.get(route.method, 0) + 1
        group_counts[route.group] = group_counts.get(route.group, 0) + 1

    duplicates = sorted({route.key for route in routes if [item.key for item in routes].count(route.key) > 1})
    protected = "\n".join(f"- {item}" for item in PROTECTED_ITEMS)
    method_count_rows = [[f"`{key}`", str(value)] for key, value in sorted(method_counts.items())]
    group_count_rows = [[f"`{key}`", str(value)] for key, value in sorted(group_counts.items())]
    duplicate_text = "없음" if not duplicates else "\n".join(f"- `{item}`" for item in duplicates)

    auto_rows = candidate_rows(routes, status="Vue 자동 smoke 화면 사용 중")
    active_rows = candidate_rows(routes, status="legacy 계정/관리자 화면 사용 중")
    readonly_rows = candidate_rows(routes, status="Vue read-only 후보")
    postponed_rows = hold_rows(routes)

    return f"""# Backend Route Map — {PROJECT_VERSION}

이 문서는 FastAPI route 파일을 정적으로 분석해서 현재 API 목록을 정리한 자동 보고서입니다.

중요: v377은 **v371 이메일 계정 주기 위에 지속성 rate limit, JSON 파싱 전 body cap, semantic mail outbox와 안전한 미인증 identity 회수를 추가한 source-prepared 단계**입니다. 이 보고서 생성은 DB, 인증 상태와 저장 데이터를 변경하지 않습니다.

## 생성 방식

- 도구: `tools/report_backend_route_map.py`
- 산출물: `docs/generated/BACKEND_ROUTE_MAP.md`
- 방식: `app.main`을 import하지 않고 route 파일의 GET/POST/PUT/PATCH/DELETE decorator를 정적으로 분석합니다.
- 이유: 단순 문서 생성이 `asyncpg` 같은 로컬 DB 의존성 설치 상태에 막히지 않게 하기 위해서입니다.

## 보호 항목

{protected}

## Route 수 요약

| 기준 | 값 |
|---|---:|
| 전체 route 수 | {len(routes)} |
| 중복 method/path | {len(duplicates)} |

### Method별 수

{table(["method", "count"], method_count_rows)}

### Group별 수

{table(["group", "count"], group_count_rows)}

중복 method/path:

{duplicate_text}

## Vue에서 이미 자동 smoke 화면에 쓰는 route

{table(["route", "group", "query/body 힌트", "response type", "endpoint"], auto_rows)}

## legacy 계정·관리자 화면에서 사용하는 route

아래 경로는 v377 이메일 계정 gate, 캐릭터 슬롯, 저장 브리지 또는 관리자 회원관리 화면에 연결됩니다. 이메일 인증·복구 링크처럼 명시적으로 public인 경로를 제외한 계정·게임 저장·관리자 경로는 실제 Bearer 인증을 요구합니다.

{table(["route", "group", "query/body 힌트", "response type", "endpoint"], active_rows)}

## Vue read-only 연결 후보

아래 route는 모두 `GET`입니다. 다만 일부는 DB 상태에 영향을 받으므로, 화면에 자동 호출하기 전에 loading/error/empty 상태를 먼저 설계해야 합니다.

{table(["route", "group", "query/body 힌트", "response type", "endpoint"], readonly_rows)}

### query 이름 주의점

- `GET /api/v1/admin/master-data/detail`의 row 식별자 query 이름은 `id`입니다.
- `GET /api/v1/admin/master-data/relations`의 row 식별자 query 이름도 `id`입니다.
- Vue wrapper에서는 사용자가 이해하기 쉽게 `rowId`를 받을 수 있지만, 실제 요청 query는 `id`로 변환해야 합니다.
- `GET /api/v1/game/load`는 `slotKey`와 `accountCharacterId`가 모두 필요합니다.

## Vue 연결 보류 route

아래 route는 DB 상태 확인, 기존 관리자 Preview/Apply 또는 아직 Vue에 연결하지 않은 경로입니다.

{table(["route", "group", "response type", "보류 이유"], postponed_rows)}

## 전체 route map

{table(["method", "full path", "endpoint", "source", "response type", "v377 판단"], route_rows(routes))}

## 다음 추천 단계

`next safe stage: prepare-v377-private-email-environment`

v377 source 검증 뒤에도 private environment/DB artifact preparation, isolated migration roundtrip, fresh local/Neon backup과 exact apply, Brevo 설정·테스트 메일과 배포는 순서대로 남습니다. owner bootstrap은 이 rollout과 분리된 별도 one-shot입니다.

권장 범위:

1. ignored dotenv와 기존 DB security artifact를 private ACL로 고정하고 email/abuse secret을 값 출력 없이 준비합니다.
2. 고정 DB의 synthetic v295 fixture로 v377 upgrade→v295 downgrade→v377 re-upgrade를 한 번 검증합니다.
3. 같은 source SHA의 완료 보고서와 fresh backup을 강제한 뒤 local, Neon을 exact v377로 적용합니다.
4. Brevo sender/API key와 Render secret을 구성하고 실제 테스트 메일로 발송·링크 흐름을 확인합니다.
5. 서버측 session/revoke, save revision/CAS, CSP/XSS·브라우저 token과 개인정보 정책은 공개 회원가입을 열기 전에 마저 완료합니다.
6. backend image와 legacy static은 모든 공개 gate가 닫힌 뒤 같은 exact-SHA 단위로 게시·배포합니다.
"""


def write_report(root: Path, text: str) -> None:
    output = root / REPORT_PATH
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8", newline="\n")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the report is out of date")
    args = parser.parse_args(argv)

    root = Path.cwd()
    text = render_report(root)
    output = root / REPORT_PATH

    if args.check:
        if not output.exists():
            print(f"missing report: {REPORT_PATH.as_posix()}", file=sys.stderr)
            return 1
        current = output.read_text(encoding="utf-8")
        if current != text:
            print(f"outdated report: {REPORT_PATH.as_posix()}", file=sys.stderr)
            return 1
        print(f"OK: {REPORT_PATH.as_posix()} is up to date")
        return 0

    write_report(root, text)
    print(f"wrote {REPORT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
