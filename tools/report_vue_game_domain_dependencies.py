#!/usr/bin/env python3
"""Generate the v384 legacy game-domain dependency inventory."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PROJECT_VERSION = "v384"
REPORT_PATH = Path("docs/generated/VUE_GAME_DOMAIN_DEPENDENCIES.md")

LEGACY_FILES = [
    Path("src/state/game-state.js"),
    Path("src/systems/action-result-system.js"),
    Path("src/systems/combat-system.js"),
    Path("src/systems/item-system.js"),
    Path("src/systems/stat-system.js"),
    Path("src/rules/abyss-fragment-rules.js"),
    Path("src/rules/boss-display-rules.js"),
    Path("src/rules/boss-drop-rules.js"),
]

DEPENDENCY_PATTERNS = {
    "window": re.compile(r"\bwindow\b"),
    "document": re.compile(r"\bdocument\b"),
    "storage": re.compile(r"\b(?:localStorage|sessionStorage)\b"),
    "random": re.compile(r"\bMath\.random\s*\("),
    "clock": re.compile(r"\bDate\.now\s*\("),
    "timer": re.compile(r"\b(?:setTimeout|clearTimeout|setInterval|clearInterval)\s*\("),
}

MIGRATION_MAP = {
    "src/state/game-state.js": (
        "state + compatibility",
        "기본 server/client/runtime state, normalize, save payload, slot 계산",
        "`window` alias와 legacy 선택 캐릭터 hook",
    ),
    "src/systems/action-result-system.js": (
        "result + UI adapter",
        "result/log/effect/UI 요청 조립",
        "현재 시각 생성과 DOM/UI effect 적용",
    ),
    "src/systems/combat-system.js": (
        "combat + runtime + UI",
        "공격속도/기본공격 계산, 필드 HP·respawn 전이, 위치 clamp",
        "난수, timer, 현재 시각, 전투 orchestration과 DOM",
    ),
    "src/systems/item-system.js": (
        "inventory + item + UI",
        "빈 칸 유지·배치·비우기·정렬 slot 계산",
        "drop/enhance 난수·시각, 전역 player/data와 DOM",
    ),
    "src/systems/stat-system.js": (
        "stat + seed lookup",
        "공격속도 clamp·기본 공격력·큰 수 표기",
        "전역 player/data, 난수 stat 생성과 test flag",
    ),
    "src/rules/abyss-fragment-rules.js": (
        "rule + seed mutation",
        "심연의 편린 이름별 특수 능력치",
        "전역 special boss seed 순회·변경",
    ),
    "src/rules/boss-display-rules.js": (
        "display mutation",
        "이번 단계 이전 없음",
        "전역 boss seed와 이미지 helper를 이용한 표시 후처리",
    ),
    "src/rules/boss-drop-rules.js": (
        "drop rule + award orchestration",
        "일반 보스 스킬 드랍률과 최초 장비 보너스 대상 판정",
        "난수·시각, 전역 player/inventory/기록/UI",
    ),
}

DOMAIN_FILES = [
    "action-result.ts",
    "combat-math.ts",
    "field-state.ts",
    "inventory-slots.ts",
    "rules.ts",
    "state.ts",
    "types.ts",
]


def markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(str(cell) for cell in row) + " |" for row in rows)
    return "\n".join(lines)


def read_sources(root: Path) -> list[tuple[Path, str]]:
    missing = [path.as_posix() for path in LEGACY_FILES if not (root / path).is_file()]
    if missing:
        raise FileNotFoundError(f"missing legacy domain sources: {missing}")
    return [(path, (root / path).read_text(encoding="utf-8")) for path in LEGACY_FILES]


def render_report(root: Path) -> str:
    sources = read_sources(root)
    rows: list[list[object]] = []
    total_lines = 0
    total_functions = 0
    totals = {name: 0 for name in DEPENDENCY_PATTERNS}

    for path, source in sources:
        line_count = len(source.splitlines())
        function_count = len(re.findall(r"\bfunction\s+[A-Za-z_$][\w$]*\s*\(", source))
        counts = {name: len(pattern.findall(source)) for name, pattern in DEPENDENCY_PATTERNS.items()}
        total_lines += line_count
        total_functions += function_count
        for name, value in counts.items():
            totals[name] += value
        role, migrated, remaining = MIGRATION_MAP[path.as_posix()]
        rows.append([
            f"`{path.as_posix()}`",
            line_count,
            function_count,
            counts["window"],
            counts["document"],
            counts["random"],
            counts["clock"],
            counts["timer"],
            role,
            migrated,
            remaining,
        ])

    domain_list = "\n".join(f"- `frontend/vue-app/src/game/domain/{name}`" for name in DOMAIN_FILES)
    return f"""# Vue Game Domain Dependencies — {PROJECT_VERSION}

이 문서는 legacy 게임 계산을 Vue UI에서 분리하기 위한 정적 의존성 목록입니다. 생성기는 source를 읽기만 하며 게임, backend, DB, 배포를 변경하지 않습니다.

## 범위와 결과

- legacy JavaScript: **{len(sources)}개 / {total_lines:,}줄 / named function {total_functions}개**
- 직접 browser 의존: `window` {totals['window']}회, `document` {totals['document']}회, storage {totals['storage']}회
- 비결정적 runtime 의존: `Math.random()` {totals['random']}회, `Date.now()` {totals['clock']}회, timer API {totals['timer']}회
- 판단: 계산과 DOM·timer·난수가 섞인 파일을 통째로 Vue store로 옮기지 않고, 순수 계산과 상태 전이부터 typed domain으로 분리합니다.

## 파일별 경계

{markdown_table([
    'legacy source', '줄', '함수', 'window', 'document', 'random', 'clock', 'timer', '역할', 'v384 분리', '남은 adapter 의존'
], rows)}

숫자는 source text의 직접 호출·참조 횟수입니다. 전역 `player`, seed 목록, UI helper처럼 선언 위치가 다른 암묵적 전역은 마지막 두 열에서 역할 단위로 기록했습니다.

## v384 typed domain

{domain_list}

고정한 경계:

1. domain은 Vue, Pinia, Router를 import하지 않습니다.
2. domain은 `window`, `document`, storage, fetch를 직접 사용하지 않습니다.
3. 난수와 현재 시각은 계산 함수 안에서 생성하지 않고 호출자가 값으로 주입합니다.
4. slot/state 전이는 입력 배열·객체를 직접 바꾸지 않고 새 값을 반환합니다.
5. legacy state·UI·timer는 아직 교체하지 않으며 다음 UI 단계가 adapter를 통해 이 domain을 호출합니다.

## 동등성 기준

- 기본 player/server/client/runtime state와 save payload shape
- 인벤토리·보관함·휴지통의 빈 칸 유지, 첫 빈 칸, 비우기, 수동 정렬
- 공격속도 clamp·기본 공격력·기본 공격 간격, 큰 수 표기, 기본 공격 피해식
- 필드 respawn 만료 시 HP 복구
- 보스 스킬 드랍률, 최초 장비 보너스 대상, 심연의 편린 특수 능력치
- action result/log/effect/UI request shape

검사는 고정 입력을 legacy 함수와 typed domain에 각각 넣어 JSON 결과를 비교합니다. 난수와 시각은 표본값을 주입해 결정론적으로 검사합니다.

## 생성·검사

```bash
python tools/report_vue_game_domain_dependencies.py
python tools/report_vue_game_domain_dependencies.py --check
node tools/smoke/frontend/smoke_vue_game_domain_foundation.js
```

## 다음 안전 단계

`next safe stage: migrate-vue-game-serialized-save-queue-foundation`

v394에서 선택 캐릭터 server snapshot의 GET, identity 검증, typed normalize/apply와 loading·retry·session-invalid 경계를 연결했습니다. 다음은 Gold/아이템 보상·난수 드랍과 분리해 자동·수동·전환 저장의 단일 직렬 queue를 준비하며, legacy 공개 화면, 관리자 Apply, DB write와 production 배포는 변경하지 않습니다.
"""


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the generated report is stale")
    args = parser.parse_args(argv)
    root = Path.cwd()
    report = render_report(root)
    output = root / REPORT_PATH

    if args.check:
        if not output.is_file() or output.read_text(encoding="utf-8") != report:
            print(f"outdated report: {REPORT_PATH.as_posix()}", file=sys.stderr)
            return 1
        print(f"OK: {REPORT_PATH.as_posix()} is up to date")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8", newline="\n")
    print(f"wrote {REPORT_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
