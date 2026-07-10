from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend/app/services/admin_service_split_contract.py"
FRONTEND = ROOT / "src/api/admin-page-readonly.js"

backend_source = BACKEND.read_text(encoding="utf-8")
frontend_source = FRONTEND.read_text(encoding="utf-8")

module = ast.parse(backend_source)
contract = None
for node in module.body:
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "ADMIN_SERVICE_SPLIT_CONTRACT":
        contract = ast.literal_eval(node.value)
        break
if contract is None:
    raise AssertionError("ADMIN_SERVICE_SPLIT_CONTRACT not found")

frontend_block_match = re.search(
    r"const ADMIN_BACKEND_SERVICE_SPLIT_CONTRACT = \{(?P<body>.*?)\n  \};",
    frontend_source,
    re.S,
)
if not frontend_block_match:
    raise AssertionError("frontend ADMIN_BACKEND_SERVICE_SPLIT_CONTRACT not found")
frontend_block = frontend_block_match.group("body")

frontend_files_match = re.search(r"extractedFiles:\s*\[(?P<body>.*?)\n\s*\],", frontend_block, re.S)
if not frontend_files_match:
    raise AssertionError("frontend extractedFiles not found")
backend_files = set(contract.get("extractedFiles", []))
frontend_files = set(re.findall(r'"(backend/app/[^\"]+\.py)"', frontend_files_match.group("body")))
assert backend_files == frontend_files, {
    "missingFrontendFiles": sorted(backend_files - frontend_files),
    "extraFrontendFiles": sorted(frontend_files - backend_files),
}

frontend_route_match = re.search(r"routeContract:\s*\[(?P<body>.*?)\n\s*\],", frontend_block, re.S)
if not frontend_route_match:
    raise AssertionError("frontend routeContract not found")
frontend_route_text = frontend_route_match.group("body")
required_markers = [
    "Normal request payload aliases and representative FastAPI 422 validation detail",
    "Malformed JSON, empty body, and unsupported JSON content type",
    "JSON charset, absent Content-Type",
    "Non-JSON media types and request size ownership",
    "UTF-8 JSON text, Content-Type parameter normalization",
]
missing_markers = [marker for marker in required_markers if marker not in frontend_route_text]
assert not missing_markers, {"missingFrontendRouteContractMarkers": missing_markers}

print("backend/frontend admin contract parity smoke test passed")
