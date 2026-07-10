from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
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
backend_route_contract = list(contract.get("routeContract", []))
frontend_route_contract = re.findall(r'"([^"]+)"', frontend_route_match.group("body"))
assert backend_route_contract == frontend_route_contract, {
    "missingFrontendRouteContractItems": [item for item in backend_route_contract if item not in frontend_route_contract],
    "extraFrontendRouteContractItems": [item for item in frontend_route_contract if item not in backend_route_contract],
    "backendRouteContractCount": len(backend_route_contract),
    "frontendRouteContractCount": len(frontend_route_contract),
}

required_readiness_links = [
    ("admin_request_payload_validation_contract.py", "requestPayloadValidationContractReady", "backendRequestPayloadValidationContractReady"),
    ("admin_validation_error_compatibility_contract.py", "validationErrorCompatibilityContractReady", "backendValidationErrorCompatibilityContractReady"),
    ("admin_request_content_negotiation_contract.py", "requestContentNegotiationContractReady", "backendRequestContentNegotiationContractReady"),
    ("admin_request_media_size_boundary_contract.py", "requestMediaSizeBoundaryContractReady", "backendRequestMediaSizeBoundaryContractReady"),
    ("admin_request_header_encoding_contract.py", "requestHeaderEncodingContractReady", "backendRequestHeaderEncodingContractReady"),
    ("admin_request_transport_header_observation_contract.py", "requestTransportHeaderObservationContractReady", "backendRequestTransportHeaderObservationContractReady"),
    ("admin_write_replay_safety_contract.py", "writeReplaySafetyContractReady", "backendWriteReplaySafetyContractReady"),
    ("admin_preview_side_effect_contract.py", "previewSideEffectContractReady", "backendPreviewSideEffectContractReady"),
    ("admin_service_mutation_boundary_contract.py", "serviceMutationBoundaryContractReady", "backendServiceMutationBoundaryContractReady"),
    ("admin_diff_engine.py", "adminDiffEngineContractReady", "backendAdminDiffEngineContractReady"),
    ("admin_rollback_snapshot.py", "adminRollbackSnapshotContractReady", "backendAdminRollbackSnapshotContractReady"),
]
split_readiness_return_match = re.search(
    r"function getAdminBackendServiceSplitContractReadiness\(\) \{.*?return \{(?P<body>.*?)\n    \};",
    frontend_source,
    re.S,
)
if not split_readiness_return_match:
    raise AssertionError("frontend split readiness return object not found")
split_readiness_return_body = split_readiness_return_match.group("body")

page_readiness_result_match = re.search(
    r"const result = \{(?P<body>.*?)\n    \};",
    frontend_source,
    re.S,
)
if not page_readiness_result_match:
    raise AssertionError("frontend page readiness result object not found")
page_readiness_result_body = page_readiness_result_match.group("body")

missing_readiness_links = []
for file_name, internal, public in required_readiness_links:
    missing_parts = []
    if file_name not in frontend_source:
        missing_parts.append("file")
    if internal not in frontend_source:
        missing_parts.append("internal-calculation")
    if not re.search(rf"\b{re.escape(internal)}\b", split_readiness_return_body):
        missing_parts.append("internal-return")
    if public not in frontend_source:
        missing_parts.append("public-calculation")
    if not re.search(rf"\b{re.escape(public)}\b", page_readiness_result_body):
        missing_parts.append("public-return")
    if missing_parts:
        missing_readiness_links.append({
            "file": file_name,
            "internal": internal,
            "public": public,
            "missing": missing_parts,
        })
assert not missing_readiness_links, {"missingFrontendReadinessLinks": missing_readiness_links}

print("backend/frontend admin contract parity smoke test passed")
