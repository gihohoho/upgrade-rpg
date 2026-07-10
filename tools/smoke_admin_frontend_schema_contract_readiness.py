from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / "src/api/admin-page-readonly.js").read_text(encoding="utf-8")
required = [
    "Admin request schema classes and OpenAPI components.schemas are checked for drift",
    "Route body models are checked against backend/app/schemas/admin.py class names",
    "Guarded apply schemas keep confirmText and reason fields",
    "Admin request field constraints, defaults, required fields, and Pydantic normalization behavior are checked for drift",
]
for marker in required:
    assert marker in text, f"missing frontend readiness marker: {marker}"
assert 'backendServiceSplitContract.schemaModelContractReady' in text
assert 'backendServiceSplitContract.schemaFieldConstraintContractReady' in text
print("[PASS] admin frontend schema contract readiness markers")
