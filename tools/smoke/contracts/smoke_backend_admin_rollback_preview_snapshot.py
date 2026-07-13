from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.admin.admin_preview_enrichment import enrich_admin_preview
from app.services.admin.admin_rollback_snapshot import (
    build_rollback_restore_payload,
    build_rollback_snapshot,
    verify_rollback_snapshot,
)

# When acceptedChanges exists, its current -> rollback direction is preserved.
ready = enrich_admin_preview(
    {
        "domain": "bosses",
        "acceptedChanges": [{"key": "hp", "before": 1200, "after": 1000}],
    },
    mode="rollback",
    target_id=7,
)
assert ready["rollbackSnapshot"]["before"] == {"hp": 1200}
assert ready["rollbackSnapshot"]["after"] == {"hp": 1000}
assert ready["unifiedDiff"] == [{"path": "$.hp", "op": "replace", "before": 1200, "after": 1000}]
assert verify_rollback_snapshot(ready["rollbackSnapshot"])

# A blocked preview may only expose the original ChangeLog direction. It must be reversed.
blocked = enrich_admin_preview(
    {
        "domain": "bosses",
        "changes": [{"key": "hp", "before": 1000, "after": 1200}],
    },
    mode="rollback",
    target_id=7,
)
assert blocked["rollbackSnapshot"]["before"] == {"hp": 1200}
assert blocked["rollbackSnapshot"]["after"] == {"hp": 1000}
assert blocked["unifiedDiff"][0]["before"] == 1200
assert blocked["unifiedDiff"][0]["after"] == 1000

snapshot = build_rollback_snapshot(domain="bosses", target_id=7, before={"hp": 1200}, after={"hp": 1000})
assert verify_rollback_snapshot(snapshot)
assert build_rollback_restore_payload(snapshot) == {"hp": 1200}
corrupted = dict(snapshot)
corrupted["after"] = {"hp": 999}
assert not verify_rollback_snapshot(corrupted)
try:
    build_rollback_restore_payload(corrupted)
except ValueError:
    pass
else:
    raise AssertionError("corrupted snapshot must be rejected")

print("[OK] backend rollback preview snapshot direction/integrity")
