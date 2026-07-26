#!/usr/bin/env python3
"""Focused source guard for the v351 master-data latency fix."""

from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MAIN_PATH = ROOT / "backend/app/main.py"
SERVICE_PATH = ROOT / "backend/app/services/game_service.py"
BOOT_POLICY_PATH = ROOT / "src/api/master-data-boot-policy.js"
RUNTIME_SWITCH_PATH = ROOT / "src/api/master-data-runtime-switch.js"
DOC_PATH = ROOT / "docs/current/MASTER_DATA_LATENCY_AND_BLOCKING_IO_AUDIT.md"
EVIDENCE_PATH = ROOT / "deploy/review/master-data-latency-blocking-io-audit-v351.json"
VERSION = "v351.master-data-latency-focused-fix-blocking-io-audited"
RESULT = "master-data-latency-fix-blocking-io-audit-ready"
NEXT_STAGE = "prepare-v351-image-and-static-release-exact-sha-gates"
STATE_FILES = (
    ROOT / "AGENTS.md",
    ROOT / "NEXT_CHAT_PROMPT.md",
    ROOT / "NEXT_CHAT_HANDOFF.md",
    ROOT / "docs/current/CURRENT_STATUS.md",
    ROOT / "docs/handoff/NEXT_CHAT_PROMPT.md",
    ROOT / "docs/handoff/NEXT_CHAT_HANDOFF.md",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


main_source = MAIN_PATH.read_text(encoding="utf-8")
require("from starlette.middleware.gzip import GZipMiddleware" in main_source, "GZip import missing")
gzip_index = main_source.index("app.add_middleware(GZipMiddleware")
cors_index = main_source.index("app.add_middleware(\n        CORSMiddleware")
require(gzip_index < cors_index, "GZip must be registered before outer CORS middleware")
require("minimum_size=1024, compresslevel=5" in main_source, "GZip limits differ")

boot_policy = BOOT_POLICY_PATH.read_text(encoding="utf-8")
runtime_switch = RUNTIME_SWITCH_PATH.read_text(encoding="utf-8")
require("DEFAULT_TIMEOUT_MS = 5000" in boot_policy, "boot timeout must be 5000ms")
require("timeoutMs: 5000" in runtime_switch, "legacy fallback timeout must be 5000ms")
require("policy.timeoutMs || 5000" in runtime_switch, "runtime fallback timeout must be 5000ms")
require("1500" not in boot_policy, "stale 1500ms boot timeout remains")
require("1500" not in runtime_switch, "stale 1500ms runtime timeout remains")

service_tree = ast.parse(SERVICE_PATH.read_text(encoding="utf-8"))
game_service = next(
    node for node in service_tree.body if isinstance(node, ast.ClassDef) and node.name == "GameService"
)
get_master_data = next(
    node
    for node in game_service.body
    if isinstance(node, ast.AsyncFunctionDef) and node.name == "get_master_data"
)
awaited_fetches = [
    node
    for node in ast.walk(get_master_data)
    if isinstance(node, ast.Await)
    and isinstance(node.value, ast.Call)
    and isinstance(node.value.func, ast.Attribute)
    and node.value.func.attr.startswith("_fetch_")
]
require(len(awaited_fetches) == 11, "master-data must retain the 11 reviewed async fetches")
require(
    not any(
        isinstance(node, ast.Attribute)
        and node.attr in {"gather", "create_task"}
        for node in ast.walk(get_master_data)
    ),
    "one AsyncSession must not be shared across concurrent master-data tasks",
)

evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
require(evidence.get("schemaVersion") == VERSION, "evidence version differs")
require(evidence.get("result") == RESULT, "evidence result differs")
require(evidence.get("nextSafeStage") == NEXT_STAGE, "evidence next stage differs")
focused_fix = evidence.get("focusedFix") or {}
require(focused_fix.get("frontendTimeoutMilliseconds") == 5000, "evidence timeout differs")
require(focused_fix.get("backendGzipMinimumBytes") == 1024, "evidence GZip threshold differs")
require(focused_fix.get("sharedAsyncSessionConcurrencyAdded") is False, "unsafe DB concurrency marker differs")
audit = evidence.get("runtimeBlockingIoAudit") or {}
require(audit.get("passed") is True, "blocking-I/O evidence must pass")
offline = audit.get("offlineTooling") or {}
require(offline.get("classification") == "intentional-one-shot-cli", "offline tooling classification differs")
require(offline.get("pythonFiles") == 148, "offline Python inventory differs")
require(offline.get("javascriptFiles") == 94, "offline JavaScript inventory differs")
release = evidence.get("releaseBoundary") or {}
require(release.get("providerMutationExecuted") is False, "provider deploy must remain unexecuted")
require(release.get("exactShaOwnerApprovalRequired") is True, "exact SHA gate is required")

doc = DOC_PATH.read_text(encoding="utf-8")
for marker in (VERSION.split(".", 1)[0], "5,000ms", "AsyncSession", "check_runtime_blocking_io.py"):
    require(marker in doc, f"latency audit document marker missing: {marker}")

for state_path in STATE_FILES:
    state = state_path.read_text(encoding="utf-8")
    for marker in (VERSION, RESULT, NEXT_STAGE):
        require(marker in state, f"{state_path.relative_to(ROOT)} marker missing: {marker}")

require(
    (ROOT / "NEXT_CHAT_PROMPT.md").read_bytes()
    == (ROOT / "docs/handoff/NEXT_CHAT_PROMPT.md").read_bytes(),
    "NEXT_CHAT_PROMPT mirror differs",
)
require(
    (ROOT / "NEXT_CHAT_HANDOFF.md").read_bytes()
    == (ROOT / "docs/handoff/NEXT_CHAT_HANDOFF.md").read_bytes(),
    "NEXT_CHAT_HANDOFF mirror differs",
)

print("master-data latency guard smoke test passed")
