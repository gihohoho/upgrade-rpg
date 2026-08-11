#!/usr/bin/env python3
"""Fail-closed audit for blocking I/O in Upgrade RPG runtime code.

Only request-time/backend and browser runtime source is audited. One-shot
maintenance tools and smoke scripts intentionally remain outside this boundary:
their synchronous file/subprocess work does not block the application event loop.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "backend/app"
FRONTEND_ROOTS = (ROOT / "src", ROOT / "frontend/vue-app/src")
FRONTEND_ENTRYPOINTS = (ROOT / "index.html", ROOT / "admin.html")
VERSION = "v351.master-data-latency-focused-fix-blocking-io-audited"
RESULT = "runtime-blocking-io-audit-passed"

ROUTE_METHODS = {"delete", "get", "head", "options", "patch", "post", "put", "trace", "websocket"}
ASYNC_WITHOUT_AWAIT_ALLOWLIST = {
    "backend/app/main.py:auth_flow_error_handler",
    "backend/app/main.py:request_validation_error_handler",
    "backend/app/api/routes/auth.py:get_me",
    "backend/app/api/routes/auth.py:logout",
    "backend/app/api/routes/admin_overview_snapshot_routes.py:get_admin_requirements",
    "backend/app/api/routes/health.py:health_check",
    "backend/app/core/security.py:require_admin_user",
    "backend/app/core/security.py:require_admin_write_dev_key",
    "backend/app/services/admin/admin_readiness_service.py:AdminReadinessService.preview_change",
}
BLOCKING_EXACT_CALLS = {
    "builtins.open",
    "io.open",
    "os.popen",
    "os.system",
    "pathlib.Path.open",
    "pathlib.Path.read_bytes",
    "pathlib.Path.read_text",
    "pathlib.Path.write_bytes",
    "pathlib.Path.write_text",
    "socket.create_connection",
    "time.sleep",
    "urllib.request.urlopen",
}
BLOCKING_CALL_PREFIXES = (
    "http.client.",
    "requests.",
    "subprocess.",
)
BLOCKING_METHOD_NAMES = {"open", "read_bytes", "read_text", "write_bytes", "write_text"}
JS_BLOCKING_PATTERNS = {
    "synchronous XMLHttpRequest": re.compile(r"\.open\s*\([^;\n]{0,500},\s*false\s*\)"),
    "Atomics.wait": re.compile(r"\bAtomics\.wait\s*\("),
    "synchronous child_process": re.compile(
        r"\b(?:execFileSync|execSync|spawnSync)\s*\("
    ),
}
OFFLINE_JS_SYNC_PATTERN = re.compile(
    r"\b(?:appendFileSync|cpSync|execFileSync|execSync|mkdirSync|readFileSync|"
    r"rmSync|spawnSync|writeFileSync)\s*\("
)


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    symbol: str
    detail: str


def dotted_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = dotted_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def python_files() -> list[Path]:
    return sorted(BACKEND_ROOT.rglob("*.py"))


def frontend_files() -> list[Path]:
    files: list[Path] = [path for path in FRONTEND_ENTRYPOINTS if path.is_file()]
    for root in FRONTEND_ROOTS:
        if root.is_dir():
            files.extend(root.rglob("*.js"))
            files.extend(root.rglob("*.vue"))
    return sorted(set(files))


def build_parent_map(tree: ast.AST) -> dict[ast.AST, ast.AST]:
    return {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}


def nearest_function(node: ast.AST, parents: dict[ast.AST, ast.AST]) -> ast.AST | None:
    current = parents.get(node)
    while current is not None:
        if isinstance(current, (ast.AsyncFunctionDef, ast.FunctionDef, ast.Lambda)):
            return current
        current = parents.get(current)
    return None


def qualified_function_name(node: ast.AST, parents: dict[ast.AST, ast.AST]) -> str:
    names = [getattr(node, "name", "<lambda>")]
    current = parents.get(node)
    while current is not None:
        if isinstance(current, ast.ClassDef):
            names.append(current.name)
        current = parents.get(current)
    return ".".join(reversed(names))


def is_route_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for decorator in node.decorator_list:
        target = decorator.func if isinstance(decorator, ast.Call) else decorator
        if isinstance(target, ast.Attribute) and target.attr in ROUTE_METHODS:
            return True
    return False


def is_blocking_python_call(call: ast.Call) -> tuple[bool, str]:
    name = dotted_name(call.func)
    if name == "open":
        return True, "built-in open()"
    if name in BLOCKING_EXACT_CALLS:
        return True, name
    if any(name.startswith(prefix) for prefix in BLOCKING_CALL_PREFIXES):
        return True, name
    if isinstance(call.func, ast.Attribute) and call.func.attr in BLOCKING_METHOD_NAMES:
        return True, f"potential synchronous file method .{call.func.attr}()"
    return False, ""


def audit_backend() -> dict[str, object]:
    async_count = 0
    sync_count = 0
    route_async_count = 0
    route_sync_findings: list[Finding] = []
    blocking_findings: list[Finding] = []
    async_without_await: list[str] = []

    for path in python_files():
        relative = path.relative_to(ROOT).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        parents = build_parent_map(tree)

        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                async_count += 1
                if is_route_function(node):
                    route_async_count += 1
                symbol = qualified_function_name(node, parents)
                key = f"{relative}:{symbol}"
                suspends = any(
                    nearest_function(child, parents) is node
                    and isinstance(child, (ast.Await, ast.AsyncFor, ast.AsyncWith, ast.Yield, ast.YieldFrom))
                    for child in ast.walk(node)
                )
                if not suspends:
                    async_without_await.append(key)

                for child in ast.walk(node):
                    if not isinstance(child, ast.Call) or nearest_function(child, parents) is not node:
                        continue
                    is_blocking, detail = is_blocking_python_call(child)
                    if is_blocking:
                        blocking_findings.append(
                            Finding(relative, child.lineno, symbol, detail)
                        )

            elif isinstance(node, ast.FunctionDef):
                sync_count += 1
                if is_route_function(node):
                    route_sync_findings.append(
                        Finding(
                            relative,
                            node.lineno,
                            qualified_function_name(node, parents),
                            "FastAPI route is synchronous",
                        )
                    )

    unexpected_without_await = sorted(set(async_without_await) - ASYNC_WITHOUT_AWAIT_ALLOWLIST)
    missing_allowlist = sorted(ASYNC_WITHOUT_AWAIT_ALLOWLIST - set(async_without_await))
    return {
        "files": len(python_files()),
        "asyncFunctions": async_count,
        "syncFunctions": sync_count,
        "asyncFastApiRoutes": route_async_count,
        "syncFastApiRoutes": [asdict(item) for item in route_sync_findings],
        "blockingCallsInsideAsync": [asdict(item) for item in blocking_findings],
        "asyncWithoutAwaitAllowlist": sorted(ASYNC_WITHOUT_AWAIT_ALLOWLIST),
        "unexpectedAsyncWithoutAwait": unexpected_without_await,
        "staleAsyncWithoutAwaitAllowlist": missing_allowlist,
    }


def count_pattern(pattern: re.Pattern[str], texts: Iterable[str]) -> int:
    return sum(len(pattern.findall(text)) for text in texts)


def audit_frontend() -> dict[str, object]:
    files = frontend_files()
    entries = [(path, path.read_text(encoding="utf-8")) for path in files]
    findings: list[Finding] = []
    for path, text in entries:
        relative = path.relative_to(ROOT).as_posix()
        for detail, pattern in JS_BLOCKING_PATTERNS.items():
            for match in pattern.finditer(text):
                findings.append(
                    Finding(relative, text.count("\n", 0, match.start()) + 1, "<module>", detail)
                )

    texts = [text for _, text in entries]
    return {
        "files": len(files),
        "asyncDeclarations": count_pattern(re.compile(r"\basync\s+(?:function\s+)?[\w$(]"), texts),
        "awaitExpressions": count_pattern(re.compile(r"\bawait\b"), texts),
        "fetchCalls": count_pattern(re.compile(r"\bfetch\s*\("), texts),
        "promiseAllCalls": count_pattern(re.compile(r"\bPromise\.all\s*\("), texts),
        "blockingBrowserCalls": [asdict(item) for item in findings],
    }


def audit_offline_tooling() -> dict[str, object]:
    python_paths = sorted(
        set((ROOT / "tools").rglob("*.py"))
        | set((ROOT / "backend/scripts").rglob("*.py"))
    )
    python_blocking_calls = 0
    for path in python_paths:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.relative_to(ROOT).as_posix())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and is_blocking_python_call(node)[0]:
                python_blocking_calls += 1

    javascript_paths = sorted(
        set((ROOT / "tools").rglob("*.js"))
        | set((ROOT / "tools").rglob("*.mjs"))
        | set((ROOT / "backend/scripts").rglob("*.js"))
        | set((ROOT / "backend/scripts").rglob("*.mjs"))
    )
    javascript_sync_calls = sum(
        len(OFFLINE_JS_SYNC_PATTERN.findall(path.read_text(encoding="utf-8")))
        for path in javascript_paths
    )
    return {
        "classification": "intentional-one-shot-cli",
        "failClosedRuntimeFinding": False,
        "pythonFiles": len(python_paths),
        "pythonBlockingCalls": python_blocking_calls,
        "javascriptFiles": len(javascript_paths),
        "javascriptSyncCalls": javascript_sync_calls,
        "reason": "these commands run to completion outside backend request and browser event loops",
    }


def build_report() -> dict[str, object]:
    backend = audit_backend()
    frontend = audit_frontend()
    offline = audit_offline_tooling()
    passed = not any(
        (
            backend["syncFastApiRoutes"],
            backend["blockingCallsInsideAsync"],
            backend["unexpectedAsyncWithoutAwait"],
            backend["staleAsyncWithoutAwaitAllowlist"],
            frontend["blockingBrowserCalls"],
        )
    )
    return {
        "schemaVersion": VERSION,
        "result": RESULT if passed else "runtime-blocking-io-audit-failed",
        "passed": passed,
        "scope": {
            "runtimeFailClosedIncluded": [
                "backend/app/**/*.py",
                "index.html",
                "admin.html",
                "src/**/*.js",
                "frontend/vue-app/src/**/*.{js,vue}",
            ],
            "separatelyClassified": ["tools/**", "backend/scripts/**", "one-shot CLI and smoke code"],
            "reason": "CLI blocking calls are inventoried but do not run inside backend request or browser event loops",
        },
        "backend": backend,
        "frontend": frontend,
        "offlineTooling": offline,
    }


def print_summary(report: dict[str, object]) -> None:
    backend = report["backend"]
    frontend = report["frontend"]
    offline = report["offlineTooling"]
    assert isinstance(backend, dict)
    assert isinstance(frontend, dict)
    assert isinstance(offline, dict)
    print(
        "backend runtime: "
        f"{backend['files']} files / {backend['asyncFunctions']} async / "
        f"{backend['syncFunctions']} sync / {backend['asyncFastApiRoutes']} async routes"
    )
    print(
        "backend findings: "
        f"sync routes={len(backend['syncFastApiRoutes'])} / "
        f"blocking in async={len(backend['blockingCallsInsideAsync'])} / "
        f"unexpected async-without-await={len(backend['unexpectedAsyncWithoutAwait'])}"
    )
    print(
        "frontend runtime: "
        f"{frontend['files']} files / {frontend['asyncDeclarations']} async declarations / "
        f"{frontend['fetchCalls']} fetch calls / {frontend['promiseAllCalls']} Promise.all calls"
    )
    print(f"frontend blocking findings: {len(frontend['blockingBrowserCalls'])}")
    print(
        "offline tooling (classified, non-runtime): "
        f"{offline['pythonFiles']} Python files / {offline['pythonBlockingCalls']} blocking calls / "
        f"{offline['javascriptFiles']} JavaScript files / {offline['javascriptSyncCalls']} sync calls"
    )
    print(f"result: {report['result']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="exit non-zero when the audit fails")
    parser.add_argument("--json", action="store_true", help="print the complete JSON report")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_summary(report)
    return 1 if args.strict and not report["passed"] else 0


if __name__ == "__main__":
    sys.exit(main())
