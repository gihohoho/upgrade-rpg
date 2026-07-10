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


def build_rollback_restore_payload(snapshot: dict[str, Any]) -> Any:
    if snapshot.get("schemaVersion") != 1 or "before" not in snapshot:
        raise ValueError("unsupported rollback snapshot")
    return deepcopy(snapshot["before"])
