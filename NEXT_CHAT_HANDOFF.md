# Next Chat Handoff

## Current stable state

- Admin readiness version: `v250.backend-admin-rollback-snapshot`
- Backend splitStatus: `admin-schema-field-constraint-contract-v238`
- ZIP: `rpg_v246_backend_admin_write_replay_safety_contract.zip`
- DB/env/seed changes: none
- Route paths, API response bodies, schemas, authentication, and apply behavior: unchanged

## v246 completed

- Added deterministic repeated parsing checks for five preview request models.
- Verified all five apply route functions retain `_write_guard: ADMIN_WRITE_GUARD_DEP`.
- Recorded `Idempotency-Key` as unsupported; no idempotency storage, DB table, middleware, or route behavior was added.
- Isolated checks perform zero service calls and zero DB write attempts.
- Added synchronized frontend readiness `backendWriteReplaySafetyContractReady`.
- Backend/frontend `extractedFiles` and `routeContract` full ordered parity smoke remains mandatory.

## Validation

Run from project root:

```bash
python tools/smoke_backend_admin_write_replay_safety_contract.py && python tools/smoke_backend_admin_frontend_contract_parity.py && node tools/smoke_admin_readonly_page.js && python tools/smoke_backend_admin_runtime_route_contract.py && python tools/smoke_backend_admin_request_metadata_contract.py && python tools/smoke_backend_admin_schema_model_contract.py && python tools/smoke_backend_admin_schema_field_constraint_contract.py && python -m compileall -q backend/app backend/scripts tools
```

## Admin console expected

```js
({
  version: checkAdminReadOnlyPageReady().version,
  pageReady: checkAdminReadOnlyPageReady().ok,
  failedChecks: checkAdminReadOnlyPageReady().failedChecks,
  writeReplaySafetyReady: checkAdminReadOnlyPageReady().backendWriteReplaySafetyContractReady,
})
```

Expected: version `v250.backend-admin-rollback-snapshot`, `pageReady: true`, `failedChecks: []`, `writeReplaySafetyReady: true`.

## Recommended next work

`v247 backend admin preview side-effect static contract`

Before changing real write behavior, statically verify preview service methods do not call commit/flush/delete/add and that apply methods remain the only mutation boundary. Do not add an idempotency implementation until DB/storage and expiry policy are designed explicitly.
