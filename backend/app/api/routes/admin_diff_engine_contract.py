from __future__ import annotations
from typing import Any
from app.services.admin.admin_diff_engine import build_admin_diff

ADMIN_DIFF_ENGINE_CONTRACT={"version":"v249.backend-admin-diff-engine","status":"admin-diff-engine-v249"}

def get_admin_diff_engine_contract_readiness() -> dict[str, Any]:
    before={"name":"검","stats":{"atk":10,"tags":["a","b"]},"removed":1}
    after={"name":"검+1","stats":{"atk":12,"tags":["a","c"]},"added":True}
    before_copy=repr(before); after_copy=repr(after)
    first=build_admin_diff(before,after); second=build_admin_diff(before,after)
    paths=[item["path"] for item in first]
    expected=["$.added","$.name","$.removed","$.stats.atk","$.stats.tags[1]"]
    checks=[
        {"key":"deterministic","ok":first==second},
        {"key":"ordered-paths","ok":paths==expected,"actual":paths,"expected":expected},
        {"key":"input-not-mutated","ok":repr(before)==before_copy and repr(after)==after_copy},
        {"key":"no-change-empty","ok":build_admin_diff({"a":1},{"a":1})==[]},
    ]
    failed=[item for item in checks if not item["ok"]]
    return {"ok":not failed,"version":ADMIN_DIFF_ENGINE_CONTRACT["version"],"status":ADMIN_DIFF_ENGINE_CONTRACT["status"],"checks":checks,"failedChecks":failed,"dbWriteAttemptCount":0}
