# Next Chat Handoff

## Current stable state

- Admin readiness version: `v245.backend-admin-transport-header-observation-contract`
- Backend splitStatus: `admin-schema-field-constraint-contract-v238`
- ZIP: `rpg_v243_backend_admin_request_media_size_boundary_contract.zip`
- DB/env/seed changes: none
- Route paths, API response bodies, schemas, authentication, and apply write guards: unchanged

## v243 completed

- Added non-JSON request media boundary checks for `application/octet-stream`, `application/x-www-form-urlencoded`, and `multipart/form-data`.
- Empty binary body remains a body-level `missing` 422.
- Non-empty binary/form bodies remain `model_attributes_type` 422 responses.
- A 64 KiB JSON body is accepted in the isolated TestClient app, documenting that no explicit application body-size limit is configured.
- Production size-limit ownership is explicitly `deployment-proxy-or-server-configuration`; no risky middleware was added.
- Service call count and DB write attempt count remain zero.
- Added synchronized backend/frontend readiness marker: `backendRequestMediaSizeBoundaryContractReady`.

## Validation

Run from project root:

```bash
python tools/smoke_backend_admin_request_media_size_boundary_contract.py && python tools/smoke_backend_admin_request_content_negotiation_contract.py && python tools/smoke_backend_admin_validation_error_compatibility_contract.py && python tools/smoke_backend_admin_request_payload_validation_contract.py && node tools/smoke_admin_readonly_page.js && python -m compileall -q backend/app backend/scripts tools
```

`tools/run_smoke_core.sh` passed through the runtime-route section before the execution timeout; every remaining smoke was then run individually and passed.

## Admin console expected

```js
({
  version: checkAdminReadOnlyPageReady().version,
  pageReady: checkAdminReadOnlyPageReady().ok,
  failedChecks: checkAdminReadOnlyPageReady().failedChecks,
  mediaSizeBoundaryReady: checkAdminReadOnlyPageReady().backendRequestMediaSizeBoundaryContractReady,
})
```

Expected version: `v245.backend-admin-transport-header-observation-contract`, `pageReady: true`, `failedChecks: []`, `headerEncodingReady: true`, `transportHeaderObservationReady: true`.

## Recommended next work

`v244 backend admin request header and encoding compatibility contract`

Safely verify duplicate/odd Content-Type parameters, UTF-8 non-ASCII JSON, invalid byte encoding, and transfer/header normalization without service or DB execution. Do not introduce a production body-size limit until deployment proxy/server settings are known.


## v244 added
- Added `admin_request_header_encoding_contract.py`.
- UTF-8 Korean/symbol JSON, Content-Type parameter normalization, header-name case insensitivity, and malformed byte parsing are verified without service or DB execution.
- Environment-sensitive malformed/ambiguous encoding outcomes use explicit allowed outcomes with detailed validation.


## v245 transport header observation

- Duplicate Content-Type and Accept headers are observed as ordered raw ASGI header values; `Headers.get()` selects the first value in the current test boundary.
- Declared Content-Length mismatch and Transfer-Encoding are observation-only in TestClient; enforcement remains the deployment proxy/ASGI server responsibility.
- `tools/smoke_backend_admin_frontend_contract_parity.py` now requires complete ordered parity for backend/frontend extractedFiles and routeContract arrays plus all v240-v245 readiness links.
- No DB/env/seed/auth/write route changes.
