"""Smoke test for default master-data nested inline asset cleanup.

Run from the project root:

    python tools/smoke_master_data_nested_asset_cleanup.py
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.services.game_service import serialize_master_value  # noqa: E402


INLINE_SVG = "data:image/svg+xml;charset=UTF-8,%3Csvg%3E..."

sample = {
    "topIcon": INLINE_SVG,
    "nested": {
        "raw": {
            "img": INLINE_SVG,
            "name": "짙은 심연의 편린 스태프",
        },
        "list": ["safe", INLINE_SVG],
    },
}

without_assets = serialize_master_value(sample, include_assets=False)
with_assets = serialize_master_value(sample, include_assets=True)

assert without_assets["topIcon"] is None
assert without_assets["nested"]["raw"]["img"] is None
assert without_assets["nested"]["list"][1] is None
assert without_assets["nested"]["raw"]["name"] == "짙은 심연의 편린 스태프"
assert with_assets["topIcon"] == INLINE_SVG
assert with_assets["nested"]["raw"]["img"] == INLINE_SVG

print("master-data nested asset cleanup smoke test passed")
