from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.admin.admin_diff_engine import build_admin_field_changes

before = {"name": "검", "stats": {"atk": 10}, "removed": True, "same": 1}
after = {"name": "강한 검", "stats": {"atk": 12}, "added": "new", "same": 1}
changes = build_admin_field_changes(before, after)

assert [item["key"] for item in changes] == ["added", "name", "removed", "stats"]
assert changes[0] == {"key": "added", "before": None, "after": "new"}
assert changes[-1]["before"] == {"atk": 10}
assert changes[-1]["after"] == {"atk": 12}
assert before["stats"]["atk"] == 10
assert after["stats"]["atk"] == 12
print("[OK] backend admin ChangeLog uses shared diff projection")
