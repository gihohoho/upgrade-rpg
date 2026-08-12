#!/usr/bin/env python3
"""Generate a legacy path dependency report for the Upgrade RPG project.

This is a documentation/helper tool, not a runtime migration.
It scans text files in the current repository and writes a deterministic markdown
report that helps decide which legacy paths must not be moved before Vue/FastAPI/DB
transition work begins.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

PROJECT_VERSION = "v334"
REPORT_PATH = Path("docs/generated/LEGACY_PATH_DEPENDENCIES.md")

IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "dist",
    "build",
    ".idea",
    ".vscode",
}

IGNORED_PREFIXES = {
    ("docs", "archive"),
    ("docs", "handoff"),
}

TEXT_EXTENSIONS = {
    ".html",
    ".js",
    ".mjs",
    ".cjs",
    ".py",
    ".sh",
    ".md",
    ".txt",
    ".json",
    ".css",
    ".yml",
    ".yaml",
    ".toml",
    ".ini",
    ".sql",
}

WATCH_TARGETS = [
    ("admin.html", "관리자 legacy 진입점", "절대 이동 금지"),
    ("index.html", "게임 legacy 진입점", "절대 이동 금지"),
    ("src/", "legacy 브라우저 JS/CSS 루트", "절대 이동 금지"),
    ("src/api/", "legacy API/client/admin helper", "Vue 이식 후보이지만 현 위치 유지"),
    ("src/api/admin/", "관리자 기능별 helper", "Vue 관리자 이식 후보이지만 현 위치 유지"),
    ("src/data/", "게임 seed/부트스트랩 기준 데이터", "DB seed 준비 전 이동 금지"),
    ("src/rules/", "게임 규칙 모듈", "콘텐츠 개발 보류, 현 위치 유지"),
    ("src/state/", "legacy 상태", "Vue store 후보, 현 위치 유지"),
    ("src/systems/", "전투/아이템/스탯 domain logic", "domain module 후보, 현 위치 유지"),
    ("src/ui/", "legacy DOM 렌더링", "Vue component 대체 후보, 현 위치 유지"),
    ("src/styles/", "legacy CSS", "Vue CSS 분해 후보, 현 위치 유지"),
    ("backend/app/api/routes/", "FastAPI route 파일", "route path/contract 보호"),
    ("backend/app/services/", "FastAPI service/facade 파일", "service contract 보호"),
    ("backend/seeds/", "현재 seed 산출물", "사용자 승인 전 변경 금지"),
    ("tools/run_smoke_core.sh", "핵심 smoke 실행 목록", "검증 기준 유지"),
    ("tools/smoke/", "smoke/contract 검사 파일", "경로 의존성 기준"),
]

ENTRYPOINTS = [Path("admin.html"), Path("index.html")]

PATH_LITERAL_RE = re.compile(
    r"(?:admin\.html|index\.html|src/[A-Za-z0-9_./@-]+|backend/[A-Za-z0-9_./@-]+|tools/[A-Za-z0-9_./@-]+)"
)
SCRIPT_SRC_RE = re.compile(r"<script[^>]+src=[\"']([^\"']+)[\"']", re.IGNORECASE)
LINK_HREF_RE = re.compile(r"<link[^>]+href=[\"']([^\"']+)[\"']", re.IGNORECASE)
SMOKE_COMMAND_RE = re.compile(r"^(node|python|bash)\s+([^\s#]+)", re.MULTILINE)


def iter_text_files(root: Path) -> Iterable[Path]:
    completed = subprocess.run(
        ("git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard"),
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    candidates = (
        [root / line for line in completed.stdout.splitlines() if line]
        if completed.returncode == 0
        else sorted(root.rglob("*"))
    )
    for path in candidates:
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        try:
            relative = path.relative_to(root)
        except ValueError:
            relative = path
        if any(tuple(relative.parts[: len(prefix)]) == prefix for prefix in IGNORED_PREFIXES):
            continue
        if relative == REPORT_PATH:
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        yield path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def count_watch_targets(root: Path, files: list[Path]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for target, role, decision in WATCH_TARGETS:
        needle = target.rstrip("/") if target.endswith("/") else target
        total_refs = 0
        files_with_ref: list[str] = []
        for path in files:
            text = read_text(path)
            count = text.count(needle)
            if count:
                total_refs += count
                files_with_ref.append(rel(path, root))
        exists = (root / target).exists() if not target.endswith("/") else (root / target.rstrip("/")).exists()
        rows.append(
            {
                "target": target,
                "exists": exists,
                "role": role,
                "refs": total_refs,
                "file_count": len(files_with_ref),
                "sample_files": files_with_ref[:8],
                "decision": decision,
            }
        )
    return rows


def extract_entrypoint_assets(root: Path) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for entry in ENTRYPOINTS:
        path = root / entry
        if not path.exists():
            result[entry.as_posix()] = []
            continue
        text = read_text(path)
        assets = []
        assets.extend(LINK_HREF_RE.findall(text))
        assets.extend(SCRIPT_SRC_RE.findall(text))
        # Only keep project-local legacy assets for migration decisions.
        result[entry.as_posix()] = [asset for asset in assets if asset.startswith("src/")]
    return result


def extract_core_smoke_commands(root: Path) -> list[str]:
    path = root / "tools/run_smoke_core.sh"
    if not path.exists():
        return []
    text = read_text(path)
    return [f"{kind} {command}" for kind, command in SMOKE_COMMAND_RE.findall(text)]


def collect_smoke_path_literals(root: Path) -> list[tuple[str, int]]:
    smoke_paths = []
    smoke_root = root / "tools/smoke"
    if smoke_root.exists():
        smoke_paths.extend(iter_text_files(smoke_root))
    core = root / "tools/run_smoke_core.sh"
    if core.exists():
        smoke_paths.append(core)

    counts: Counter[str] = Counter()
    for path in smoke_paths:
        text = read_text(path)
        for match in PATH_LITERAL_RE.findall(text):
            cleaned = match.rstrip("'\")`,;])}")
            counts[cleaned] += 1
    return counts.most_common(80)


def format_table(headers: list[str], rows: list[list[object]]) -> str:
    if not rows:
        rows = [["-" for _ in headers]]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines)


def render_report(root: Path) -> str:
    files = list(iter_text_files(root))
    watch_rows = count_watch_targets(root, files)
    entrypoint_assets = extract_entrypoint_assets(root)
    core_commands = extract_core_smoke_commands(root)
    path_literals = collect_smoke_path_literals(root)

    watch_table = format_table(
        ["대상", "존재", "참조 수", "참조 파일 수", "판단"],
        [
            [
                f"`{row['target']}`",
                "O" if row["exists"] else "X",
                row["refs"],
                row["file_count"],
                row["decision"],
            ]
            for row in watch_rows
        ],
    )

    sample_sections: list[str] = []
    for row in watch_rows:
        samples = row["sample_files"]
        sample_text = "<br>".join(f"`{item}`" for item in samples) if samples else "-"
        sample_sections.append(f"| `{row['target']}` | {sample_text} |")
    sample_table = "\n".join([
        "| 대상 | 참조 파일 예시 |",
        "|---|---|",
        *sample_sections,
    ])

    asset_sections: list[str] = []
    for entry, assets in entrypoint_assets.items():
        asset_sections.append(f"### `{entry}` 직접 로드 파일")
        if assets:
            asset_sections.append("\n".join(f"- `{asset}`" for asset in assets))
        else:
            asset_sections.append("- 현재 감지된 `src/` 직접 로드 파일 없음")
    assets_text = "\n\n".join(asset_sections)

    core_smoke_table = format_table(
        ["순서", "명령"],
        [[idx + 1, f"`{command}`"] for idx, command in enumerate(core_commands)],
    )

    literal_table = format_table(
        ["경로 문자열", "smoke 참조 수"],
        [[f"`{path}`", count] for path, count in path_literals[:40]],
    )

    return f"""# Legacy Path Dependencies — {PROJECT_VERSION}

이 문서는 `tools/report_legacy_path_dependencies.py`가 현재 프로젝트 파일을 스캔해서 만든 legacy 경로 의존성 보고서입니다.

목적은 Vue/FastAPI/DB 전환 전에 **움직이면 깨질 가능성이 높은 경로**를 먼저 고정하는 것입니다. 이 문서는 새 contract가 아니라 구조 전환 보조 문서입니다.

## v334 결론

- `admin.html`, `index.html`, `src/`, `backend/`, `tools/smoke/`는 아직 이동하지 않습니다.
- 새 Vue 앱은 기존 파일을 대체하지 않고 `frontend/vue-app/`에 별도로 만드는 방식이 가장 안전합니다.
- `legacy/` 폴더로 기존 파일을 옮기는 작업은 smoke 경로 alias/copy 전략이 확정된 뒤에만 진행합니다.
- 문서 구조 정리와 무관하게 DB/env/seed/auth/API body/route/write 로직은 변경하지 않습니다.

## 주요 경로 참조 요약

{watch_table}

## 참조 파일 예시

아래는 각 경로 문자열이 발견된 파일 예시입니다. 전체 목록이 아니라 처음 감지된 일부 예시입니다.

{sample_table}

## HTML 진입점 직접 로드 관계

현재 legacy 화면은 HTML이 JS/CSS를 직접 로드합니다. Vue 이식 전까지 이 순서를 유지해야 합니다.

{assets_text}

## core smoke 실행 목록

`tools/run_smoke_core.sh`가 직접 실행하는 검사 목록입니다. 파일 이동 전에는 이 목록의 경로 의존성을 먼저 확인해야 합니다.

{core_smoke_table}

## smoke 내부에서 많이 발견된 경로 문자열

{literal_table}

## Vue 앱 생성 위치 결정

### 결정

새 Vue 앱은 다음 위치에 생성하는 것이 안전합니다.

```txt
frontend/vue-app/
```

### 이유

- 기존 `src/`는 현재 Vue 소스 폴더가 아니라 legacy 브라우저 JS/CSS 폴더입니다.
- Vite/Vue 기본 `src/`와 현재 legacy `src/`가 충돌하면 기호가 나중에 파일 위치를 구분하기 어려워집니다.
- `admin.html`과 `index.html`이 루트에서 `src/...`를 직접 읽고 있어서, 현재 `src/`를 Vue 앱용으로 재사용하면 기존 smoke가 깨질 가능성이 큽니다.
- `frontend/vue-app/`는 기존 legacy와 분리되어 있어서, Vue shell을 만들어도 기존 게임/관리자 화면을 그대로 검증할 수 있습니다.

### 아직 하지 않을 것

- `admin.html` 이동
- `index.html` 이동
- 기존 `src/` 이름 변경
- `legacy/` 폴더로 대이동
- Vue 앱에서 기존 route/API body 변경
- DB/env/seed/auth/write guard 변경

## 재생성 방법

실행 위치: 프로젝트 루트
Python `.venv` 상태: `backend/.venv` 사용
새 설치 여부: 없음

```bash
python tools/report_legacy_path_dependencies.py --write
```

검사만 할 때:

실행 위치: 프로젝트 루트
Python `.venv` 상태: `backend/.venv` 사용
새 설치 여부: 없음

```bash
python tools/report_legacy_path_dependencies.py --check
```
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate/check legacy path dependency report.")
    parser.add_argument("--write", action="store_true", help="write the report to docs/current")
    parser.add_argument("--check", action="store_true", help="check that the report is up to date")
    args = parser.parse_args()

    if not args.write and not args.check:
        args.write = True

    root = Path.cwd().resolve()
    report = render_report(root)
    report_path = root / REPORT_PATH

    if args.check:
        if not report_path.exists():
            print(f"[legacy path dependencies] missing: {REPORT_PATH}", file=sys.stderr)
            return 1
        current = report_path.read_text(encoding="utf-8")
        if current != report:
            print(f"[legacy path dependencies] out of date: {REPORT_PATH}", file=sys.stderr)
            print("Run: python tools/report_legacy_path_dependencies.py --write", file=sys.stderr)
            return 1
        print(f"[legacy path dependencies] up to date: {REPORT_PATH}")
        return 0

    if args.write:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")
        print(f"[legacy path dependencies] wrote: {REPORT_PATH}")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
