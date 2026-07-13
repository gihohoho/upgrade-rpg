#!/usr/bin/env python3
"""Generate a static FastAPI backend route map for the Vue migration.

This tool intentionally avoids importing ``app.main``. Importing the app can
create DB engines and require local packages such as asyncpg, which makes a
simple documentation check depend on the developer machine state. Instead, the
report reads the route modules that are already included by ``api_router`` and
extracts ``@router.get/post(...)`` decorators from source.

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

PROJECT_VERSION = "v275"
REPORT_PATH = Path("docs/current/BACKEND_ROUTE_MAP.md")
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
    "GET /api/v1/admin/requirements",
}

VUE_READONLY_CANDIDATES = {
    "GET /api/v1/admin/overview",
    "GET /api/v1/admin/save-snapshots",
    "GET /api/v1/admin/master-data/domains",
    "GET /api/v1/admin/master-data/catalog",
    "GET /api/v1/admin/master-data/create-blueprint",
    "GET /api/v1/admin/master-data/detail",
    "GET /api/v1/admin/master-data/relations",
    "GET /api/v1/admin/change-logs",
    "GET /api/v1/admin/change-logs/{change_log_id}",
    "GET /api/v1/game/master-data",
    "GET /api/v1/game/load",
    "GET /api/v1/game/save-slots",
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
    "GET /api/v1/game/load": "slotKey",
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
    "authentication",
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
        if route.migration_status not in {"Vue 자동 smoke 화면 사용 중", "Vue read-only 후보"}
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
    readonly_rows = candidate_rows(routes, status="Vue read-only 후보")
    postponed_rows = hold_rows(routes)

    return f"""# Backend Route Map — {PROJECT_VERSION}

이 문서는 FastAPI route 파일을 정적으로 분석해서 현재 API 목록을 정리한 자동 보고서입니다.

중요: v275는 **route 목록 문서화 + Vue read-only 후보 확정 단계**입니다. 실제 route path, 요청 body, 응답 body, DB, 인증, write 로직은 변경하지 않습니다.

## 생성 방식

- 도구: `tools/report_backend_route_map.py`
- 산출물: `docs/current/BACKEND_ROUTE_MAP.md`
- 방식: `app.main`을 import하지 않고 route 파일의 `@router.get/post(...)` decorator를 정적으로 분석합니다.
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

## Vue read-only 연결 후보

아래 route는 모두 `GET`입니다. 다만 일부는 DB 상태에 영향을 받으므로, 화면에 자동 호출하기 전에 loading/error/empty 상태를 먼저 설계해야 합니다.

{table(["route", "group", "query/body 힌트", "response type", "endpoint"], readonly_rows)}

### v275에서 확인한 Vue query 이름 주의점

- `GET /api/v1/admin/master-data/detail`의 row 식별자 query 이름은 `id`입니다.
- `GET /api/v1/admin/master-data/relations`의 row 식별자 query 이름도 `id`입니다.
- Vue wrapper에서는 사용자가 이해하기 쉽게 `rowId`를 받을 수 있지만, 실제 요청 query는 `id`로 변환해야 합니다.
- v275에서 `frontend/vue-app/src/api/adminReadOnlyApi.js`의 read-only query 변환을 이 기준에 맞췄습니다.

## Vue 연결 보류 route

아래 route는 DB 상태 확인, POST preview, Apply/write 계열이므로 Vue read-only 자동 화면에는 아직 넣지 않습니다.

{table(["route", "group", "response type", "보류 이유"], postponed_rows)}

## 전체 route map

{table(["method", "full path", "endpoint", "source", "response type", "v275 판단"], route_rows(routes))}

## v276 추천

다음 단계는 `v276 Vue admin read-only catalog mini panel`을 추천합니다.

권장 범위:

1. `GET /api/v1/admin/master-data/domains`만 먼저 Vue 관리자 shell에 연결합니다.
2. 성공/오류/빈 데이터 상태만 확인합니다.
3. 카탈로그 row 목록, 상세, 관계 조회는 그다음 단계로 미룹니다.
4. Preview/Apply/write route는 계속 보류합니다.
5. DB/Alembic/인증/env/seed는 변경하지 않습니다.
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
