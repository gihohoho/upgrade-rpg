# Next Chat Handoff

## Current stable version

- Admin readiness version: `v240.backend-admin-request-payload-validation-contract`
- Backend splitStatus: `admin-schema-field-constraint-contract-v238`
- No route path, API response body, DB, env, seed, auth, or write-guard changes.

## v240 completed

- Normal payload alias serialization is frozen for all 10 admin request body models.
- Aliases covered include `dryRun`, `confirmText`, and `baseValues`.
- Representative invalid payloads verify FastAPI 422 `detail[].type`, `loc`, and `msg`.
- Contract uses an isolated FastAPI parsing app; service calls and DB writes remain zero.
- New files:
  - `backend/app/api/routes/admin_request_payload_validation_contract.py`
  - `tools/smoke_backend_admin_request_payload_validation_contract.py`

## Verification

```bash
python tools/smoke_backend_admin_runtime_route_contract.py
python tools/smoke_backend_admin_request_metadata_contract.py
python tools/smoke_backend_admin_schema_model_contract.py
python tools/smoke_backend_admin_schema_field_constraint_contract.py
python tools/smoke_backend_admin_request_payload_validation_contract.py
bash tools/run_smoke_core.sh
python -m compileall -q backend/app backend/scripts tools
```

All individual smoke tests passed. In the packaging environment, the full core script exceeded the single-command time limit after the route-operation smoke; every remaining command was rerun individually and passed.

## Console expectation after backend restart

```js
({
  version: checkAdminReadOnlyPageReady().version,
  pageReady: checkAdminReadOnlyPageReady().ok,
  failedChecks: checkAdminReadOnlyPageReady().failedChecks,
  payloadValidationReady: checkAdminReadOnlyPageReady().backendRequestPayloadValidationContractReady,
})
```

Expected:

```js
{
  version: "v240.backend-admin-request-payload-validation-contract",
  pageReady: true,
  failedChecks: [],
  payloadValidationReady: true,
}
```

## Recommended next step

`v241 backend admin validation error compatibility contract`

Suggested scope:

1. Normalize compatibility expectations across supported FastAPI/Pydantic versions.
2. Freeze only stable 422 fields (`type`, `loc`, `msg`) and explicitly ignore unstable context/input fields.
3. Verify malformed JSON and wrong content-type behavior without reaching services or DB.
4. Preserve routes, response bodies, write guards, DB, env, and seed data.
