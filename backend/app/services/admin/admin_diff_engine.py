from __future__ import annotations

from copy import deepcopy
from typing import Any

_MISSING = object()


def build_admin_diff(before: Any, after: Any, *, path: str = "$") -> list[dict[str, Any]]:
    """Return a deterministic, JSON-safe recursive diff without mutating inputs."""
    changes: list[dict[str, Any]] = []
    if isinstance(before, dict) and isinstance(after, dict):
        for key in sorted(set(before) | set(after), key=str):
            old = before.get(key, _MISSING)
            new = after.get(key, _MISSING)
            child = f"{path}.{key}"
            if old is _MISSING:
                changes.append({"path": child, "op": "add", "before": None, "after": deepcopy(new)})
            elif new is _MISSING:
                changes.append({"path": child, "op": "remove", "before": deepcopy(old), "after": None})
            else:
                changes.extend(build_admin_diff(old, new, path=child))
        return changes
    if isinstance(before, list) and isinstance(after, list):
        max_len = max(len(before), len(after))
        for index in range(max_len):
            child = f"{path}[{index}]"
            if index >= len(before):
                changes.append({"path": child, "op": "add", "before": None, "after": deepcopy(after[index])})
            elif index >= len(after):
                changes.append({"path": child, "op": "remove", "before": deepcopy(before[index]), "after": None})
            else:
                changes.extend(build_admin_diff(before[index], after[index], path=child))
        return changes
    if before != after or type(before) is not type(after):
        changes.append({"path": path, "op": "replace", "before": deepcopy(before), "after": deepcopy(after)})
    return changes
