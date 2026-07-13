from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from typing import Any


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def build_rollback_snapshot(*, domain: str, target_id: int | str, before: Any, after: Any) -> dict[str, Any]:
    """Build a detached deterministic snapshot; no session or DB mutation is performed."""
    before_copy = deepcopy(before)
    after_copy = deepcopy(after)
    fingerprint_source = {"domain": domain, "targetId": target_id, "before": before_copy, "after": after_copy}
    return {
        "schemaVersion": 1,
        "domain": domain,
        "targetId": target_id,
        "before": before_copy,
        "after": after_copy,
        "fingerprint": sha256(_canonical_json(fingerprint_source).encode("utf-8")).hexdigest(),
    }


def verify_rollback_snapshot(snapshot: dict[str, Any]) -> bool:
    """Verify snapshot metadata and fingerprint without reading or mutating the DB."""
    if not isinstance(snapshot, dict) or snapshot.get("schemaVersion") != 1:
        return False
    required = {"domain", "targetId", "before", "after", "fingerprint"}
    if not required.issubset(snapshot):
        return False
    fingerprint_source = {
        "domain": snapshot.get("domain"),
        "targetId": snapshot.get("targetId"),
        "before": snapshot.get("before"),
        "after": snapshot.get("after"),
    }
    expected = sha256(_canonical_json(fingerprint_source).encode("utf-8")).hexdigest()
    return str(snapshot.get("fingerprint") or "") == expected


def build_rollback_restore_payload(snapshot: dict[str, Any]) -> Any:
    if not verify_rollback_snapshot(snapshot):
        raise ValueError("unsupported or corrupted rollback snapshot")
    return deepcopy(snapshot["before"])
