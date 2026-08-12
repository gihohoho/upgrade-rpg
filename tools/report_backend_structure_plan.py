#!/usr/bin/env python3
"""Generate the backend structure transition plan for Upgrade RPG.

This tool is documentation-only. It inspects the current FastAPI backend file
layout and writes a deterministic markdown report for the Vue/FastAPI/DB
transition. It does not move files, rewrite routes, or change runtime behavior.
"""
from __future__ import annotations

import argparse
import ast
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_VERSION = "v274"
REPORT_PATH = Path("docs/generated/BACKEND_STRUCTURE_PLAN.md")

ROOTS = {
    "routes": Path("backend/app/api/routes"),
    "services": Path("backend/app/services"),
    "admin_services": Path("backend/app/services/admin"),
    "schemas": Path("backend/app/schemas"),
    "models": Path("backend/app/models"),
    "db": Path("backend/app/db"),
    "core": Path("backend/app/core"),
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

READONLY_ROUTE_HINTS = [
    "health.py",
    "admin.py",
    "admin_master_data_routes.py",
    "admin_overview_snapshot_routes.py",
    "admin_change_log_routes.py",
]

CONTRACT_ROUTE_HINTS = [
    "contract",
    "request_",
    "response_",
    "route_",
    "schema_",
    "validation_",
    "write_replay",
]


def rel(path: Path) -> str:
    return path.as_posix()


def list_py_files(path: Path) -> list[Path]:
    if not path.exists():
        return []
    return sorted(p for p in path.rglob("*.py") if p.is_file())


def first_docstring(path: Path) -> str:
    try:
        module = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:
        return ""
    return ast.get_docstring(module) or ""


def extract_router_includes(path: Path) -> list[str]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if ".include_router(" in stripped or stripped.startswith("api_router.include_router"):
            lines.append(stripped)
    return lines


def categorize_route(path: Path) -> str:
    name = path.name
    lowered = name.lower()
    if name == "health.py":
        return "safe-readonly"
    if name in READONLY_ROUTE_HINTS:
        return "admin-readonly-or-facade"
    if any(hint in lowered for hint in CONTRACT_ROUTE_HINTS):
        return "contract/readiness 보호"
    if name == "game.py":
        return "game API 후보"
    if "helper" in lowered or "params" in lowered or "services" in lowered:
        return "route helper 보호"
    return "검토 필요"


def categorize_service(path: Path) -> str:
    parts = path.parts
    name = path.name
    if "admin" in parts:
        if name == "README.md":
            return "admin service 설명"
        if "readiness" in name or "contract" in name:
            return "contract/readiness 보호"
        if "preview" in name or "rollback" in name or "diff" in name:
            return "admin preview/diff/snapshot 보호"
        if "create" in name or "edit" in name or "change_log" in name:
            return "admin workflow service 보호"
        return "admin service helper"
    if name == "admin_service.py":
        return "AdminService facade 유지"
    if "contract" in name or "split" in name:
        return "service split contract 보호"
    if name == "game_service.py":
        return "game service 후보"
    return "검토 필요"


def route_rows() -> list[list[str]]:
    rows = []
    for path in list_py_files(ROOTS["routes"]):
        rows.append([
            f"`{rel(path)}`",
            categorize_route(path),
            "이동 금지 / route path 유지",
        ])
    return rows


def service_rows() -> list[list[str]]:
    rows = []
    for path in sorted(ROOTS["services"].rglob("*")) if ROOTS["services"].exists() else []:
        if "__pycache__" in path.parts:
            continue
        if not path.is_file():
            continue
        if path.suffix not in {".py", ".md"}:
            continue
        rows.append([
            f"`{rel(path)}`",
            categorize_service(path),
            "facade 유지 후 단계적 분리",
        ])
    return rows


def simple_rows(key: str, decision: str) -> list[list[str]]:
    return [[f"`{rel(path)}`", decision] for path in list_py_files(ROOTS[key])]


def table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        rows = [["-"] * len(headers)]
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        out.append("| " + " | ".join(row) + " |")
    return "\n".join(out)


def render_report(root: Path) -> str:
    route_files = list_py_files(ROOTS["routes"])
    service_files = [
        p
        for p in ROOTS["services"].rglob("*")
        if p.is_file() and p.suffix in {".py", ".md"} and "__pycache__" not in p.parts
    ] if ROOTS["services"].exists() else []
    schema_files = list_py_files(ROOTS["schemas"])
    model_files = list_py_files(ROOTS["models"])
    db_files = list_py_files(ROOTS["db"])
    core_files = list_py_files(ROOTS["core"])

    router_includes = extract_router_includes(Path("backend/app/api/router.py"))
    admin_includes = extract_router_includes(Path("backend/app/api/routes/admin.py"))

    protected_list = "\n".join(f"- {item}" for item in PROTECTED_ITEMS)
    router_block = "\n".join(f"- `{item}`" for item in router_includes) or "- 없음"
    admin_block = "\n".join(f"- `{item}`" for item in admin_includes) or "- 없음"

    return f"""# Backend Structure Plan — {PROJECT_VERSION}

이 문서는 현재 `backend/` 구조를 실제 파일 기준으로 점검하고, Vue/FastAPI/DB 전환 전에 무엇을 유지하고 무엇을 나중에 정리할지 정리한 문서입니다.

중요: v274는 **문서화/분석 단계**입니다. 실제 route path, API body, DB, 인증, write 로직은 변경하지 않습니다.

## v274 결론

- `backend/app/api/routes/`는 지금처럼 route path/contract 보호 대상으로 유지합니다.
- `backend/app/services/admin_service.py` facade는 유지합니다.
- `backend/app/services/admin/`의 분리된 service들은 당장 이동하지 않습니다.
- `backend/app/schemas/`, `backend/app/models/`, `backend/app/db/`는 PostgreSQL/Alembic 준비 전까지 구조 변경하지 않습니다.
- Vue에서는 당분간 안전한 `GET` read-only API만 연결합니다.
- Preview/Apply/write API는 인증/권한/Write Guard 설계 전까지 Vue에서 확장하지 않습니다.

## 절대 변경 금지 유지 항목

{protected_list}

## 현재 backend 파일 수

| 영역 | 파일 수 | 판단 |
|---|---:|---|
| `backend/app/api/routes/` | {len(route_files)} | route path/contract 보호 |
| `backend/app/services/` | {len(service_files)} | facade 유지 후 단계적 정리 |
| `backend/app/schemas/` | {len(schema_files)} | API body 안정성 때문에 보존 |
| `backend/app/models/` | {len(model_files)} | DB 전환 전 보존 |
| `backend/app/db/` | {len(db_files)} | Alembic/DB 계획 전 보존 |
| `backend/app/core/` | {len(core_files)} | 설정/응답/CORS/security 보호 |

## 현재 route include 구조

`backend/app/api/router.py` 기준:

{router_block}

`backend/app/api/routes/admin.py` 기준:

{admin_block}

이 구조 때문에 `health`, `game`, `admin` route prefix는 전환 중에도 그대로 유지해야 합니다.

## Route 파일별 판단

{table(["파일", "현재 성격", "v274 판단"], route_rows())}

## Service 파일별 판단

{table(["파일", "현재 성격", "v274 판단"], service_rows())}

## Schema 파일 판단

{table(["파일", "v274 판단"], simple_rows("schemas", "API 응답/요청 body 안정성 때문에 보존"))}

## Model 파일 판단

{table(["파일", "v274 판단"], simple_rows("models", "PostgreSQL/Alembic 실제 전환 전 보존"))}

## DB/Core 파일 판단

{table(["파일", "v274 판단"], simple_rows("db", "DB 연결/세션 준비 영역, 실제 변경 보류") + simple_rows("core", "설정/응답/security 영역, 변경 시 smoke 필요"))}

## Vue read-only API와 backend 연결 판단

현재 Vue에서 연결해도 되는 안전 범위:

- `GET /api/v1/health`
- `GET /api/v1/admin/requirements`

다음에 연결 후보로 검토할 수 있는 범위:

- 관리자 카탈로그 조회용 `GET` API
- 관리자 상세 조회용 `GET` API
- snapshot 목록 조회용 `GET` API
- change log 조회용 `GET` API

아직 연결하지 말아야 할 범위:

- create preview/apply
- edit preview/apply
- rollback preview/apply
- delete/restore preview/apply
- save snapshot write 계열
- 인증/권한이 필요한 관리자 write 계열

## FastAPI 구조 정리 순서 제안

1. 현재 route map 자동 보고서 작성
2. read-only route 목록만 Vue에 단계적으로 연결
3. service facade 의존성 문서화
4. DB/Alembic 도입 전 seed/source-of-truth 문서화
5. 인증/권한 설계 문서화
6. Write Guard와 관리자 Preview/Apply body 보호 계약 재확인
7. 그 후에만 service 파일 이동 또는 route module 재배치 검토

## v275 추천 작업

`v275 Backend route map 자동 보고서 + Vue read-only route 후보 확정`

v275에서 해도 되는 일:

- `backend/app/api/routes/`의 실제 route 목록을 자동 추출하는 도구 추가
- `docs/generated/BACKEND_ROUTE_MAP.md` 생성
- Vue에서 연결 가능한 `GET` 후보를 문서로 분류

v275에서 아직 하지 말아야 할 일:

- route path 변경
- response body 변경
- write API Vue 연결
- 인증 추가
- DB/Alembic 실제 migration 생성
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if the report is not up to date")
    args = parser.parse_args()

    root = Path.cwd()
    report = render_report(root)
    path = root / REPORT_PATH

    if args.check:
        if not path.exists():
            print(f"missing report: {REPORT_PATH}", file=sys.stderr)
            return 1
        current = path.read_text(encoding="utf-8")
        if current != report:
            print(f"outdated report: {REPORT_PATH}", file=sys.stderr)
            return 1
        print(f"OK: {REPORT_PATH} is up to date")
        return 0

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")
    print(f"wrote {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
