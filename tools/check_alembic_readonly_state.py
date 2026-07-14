#!/usr/bin/env python3
"""Collect read-only Alembic history/heads/current results.

This helper never creates, upgrades, downgrades, stamps, or edits a migration.
`current` opens a DB connection only to read the current Alembic revision state.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class CommandResult:
    command: str
    returncode: int
    ok: bool
    output: str


def run_command(backend: Path, *args: str) -> CommandResult:
    command = [sys.executable, "-m", "alembic", *args]
    completed = subprocess.run(
        command,
        cwd=backend,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=15,
    )
    output = (completed.stdout or "").strip()
    return CommandResult(
        command=" ".join(command),
        returncode=completed.returncode,
        ok=completed.returncode == 0,
        output=output,
    )


def describe(result: CommandResult) -> str:
    if result.ok and result.output:
        return result.output
    if result.ok:
        return "(출력 없음: 현재 revision/head가 아직 없을 수 있습니다.)"
    return result.output or f"exit={result.returncode}"



def display_lines(result: CommandResult, limit: int = 18) -> list[str]:
    lines = describe(result).splitlines()
    if len(lines) <= limit:
        return lines
    omitted = len(lines) - limit
    return [f"... 중간 traceback {omitted}줄 생략 ...", *lines[-limit:]]


def diagnosis(result: CommandResult) -> str:
    text = result.output
    if result.ok:
        if " current" in result.command and not text:
            return "DB 연결은 성공했지만 현재 Alembic revision stamp가 없는 상태일 수 있습니다."
        if not text:
            return "revision 파일이 0개라 출력이 없는 현재 상태일 수 있습니다."
        return "읽기 전용 명령이 정상 완료되었습니다."
    if "MissingGreenlet" in text:
        return "Alembic env가 asyncpg URL을 동기 엔진으로 열고 있습니다. v284 env.py 적용 여부를 확인하세요."
    if "ConnectionRefusedError" in text or "Connect call failed" in text:
        return "PostgreSQL 컨테이너가 꺼져 있거나 127.0.0.1:55432 포트에서 대기하지 않는 상태입니다."
    if "InvalidPasswordError" in text or "password authentication failed" in text:
        return "DB 계정/비밀번호가 현재 설정과 일치하지 않습니다. .env를 수정하기 전에 실제 compose 설정을 확인하세요."
    if "InvalidCatalogNameError" in text or "does not exist" in text:
        return "연결 대상 DB가 아직 없거나 이름이 다를 수 있습니다. 삭제/초기화 명령은 실행하지 마세요."
    if "ModuleNotFoundError" in text and "asyncpg" in text:
        return 'backend .venv에서 python -m pip install -e ".[dev]"로 의존성을 맞추세요.'
    return "출력의 마지막 오류를 확인하세요. 이 도구는 DB 구조를 변경하지 않았습니다."


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    parser.add_argument("--strict", action="store_true", help="Return 1 when any read-only command fails")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    backend = root / "backend"
    results = [
        run_command(backend, "history"),
        run_command(backend, "heads"),
        run_command(backend, "current"),
    ]

    if args.json:
        print(
            json.dumps(
                {
                    "readOnly": True,
                    "schemaChanged": False,
                    "commands": [asdict(item) for item in results],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print("Alembic read-only state check")
        print("DB schema/migration history is not changed by this command.\n")
        for item in results:
            status = "OK" if item.ok else "ERROR"
            short_command = item.command.split(" -m alembic ", 1)[-1]
            print(f"[{status}] alembic {short_command}")
            for line in display_lines(item):
                print(f"       {line}")
            print(f"       진단: {diagnosis(item)}")
            print()

        if all(item.ok for item in results):
            print("읽기 전용 Alembic 상태 수집이 완료되었습니다.")
        else:
            print("오류가 있는 명령은 출력 내용을 그대로 확인하세요. DB 변경은 수행되지 않았습니다.")

    return 1 if args.strict and any(not item.ok for item in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
