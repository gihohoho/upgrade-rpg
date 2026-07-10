from __future__ import annotations
from typing import Any
from app.services.admin.admin_rollback_snapshot import build_rollback_restore_payload, build_rollback_snapshot

ADMIN_ROLLBACK_SNAPSHOT_CONTRACT={"version":"v250.backend-admin-rollback-snapshot","status":"admin-rollback-snapshot-v250"}

def get_admin_rollback_snapshot_contract_readiness() -> dict[str, Any]:
    before={"name":"검","stats":{"atk":10}}; after={"name":"검+1","stats":{"atk":12}}
    first=build_rollback_snapshot(domain="items",target_id=1,before=before,after=after)
    second=build_rollback_snapshot(domain="items",target_id=1,before=before,after=after)
    before["stats"]["atk"]=999; after["name"]="changed"
    restored=build_rollback_restore_payload(first); restored["stats"]["atk"]=777
    checks=[
        {"key":"deterministic-fingerprint","ok":first["fingerprint"]==second["fingerprint"]},
        {"key":"snapshot-detached","ok":first["before"]["stats"]["atk"]==10 and first["after"]["name"]=="검+1"},
        {"key":"restore-detached","ok":first["before"]["stats"]["atk"]==10},
        {"key":"schema-version","ok":first["schemaVersion"]==1},
    ]
    failed=[item for item in checks if not item["ok"]]
    return {"ok":not failed,"version":ADMIN_ROLLBACK_SNAPSHOT_CONTRACT["version"],"status":ADMIN_ROLLBACK_SNAPSHOT_CONTRACT["status"],"checks":checks,"failedChecks":failed,"dbWriteAttemptCount":0}
