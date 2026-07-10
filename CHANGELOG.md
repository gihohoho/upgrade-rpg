## v239.2 final handoff cleanup

- Updated next-chat prompt and handoff docs with the latest confirmed working state.
- Added project working rules and v240 request payload validation planning doc.
- Cleaned transient caches/log candidates from the handoff package.
- No runtime code, API path, response body, DB, or env changes.


## v239.2.backend-admin-schema-model-shared-collector-hotfix

- Updated the admin schema/model contract to reuse `collect_admin_runtime_route_entries()` instead of scanning `app.routes` directly.
- Fixes Windows/FastAPI environments where request metadata passed but schema/model route body checks returned `actualModel: None`.
- Added a smoke guard so the schema/model contract cannot reintroduce a direct `app.routes` scan.
- Kept v239.1 Pydantic required-field compatibility helpers unchanged.
- No API path, response body, DB, or env changes.

## v239 - backend admin shared runtime route collector hotfix

- Centralized admin runtime route collection in `collect_admin_runtime_route_entries()`.
- Request metadata now reuses the same app/api_router/owner-router fallback chain as runtime, operation, and response metadata contracts.
- Fixes Windows/FastAPI environments where runtime route smoke passed but request metadata still saw `runtimeRouteCount: 0`.
- API paths, response bodies, DB schema, and environment files remain unchanged.


## v238.6 - backend admin runtime mounted-app hotfix

- Runtime admin route collector now traverses Starlette/FastAPI containers that expose child routes through `node.app.routes` or `node.app.router.routes`.
- Admin page readiness now exposes `failedChecks` and `readinessChecks` so `ok: false` identifies the exact blocking checks.
- API paths, response bodies, DB schema, and environment files remain unchanged.

## v238.9 - backend admin OpenAPI f-string hotfix

- Reworked the default OpenAPI operation-id helper to normalize the route path before interpolation.
- Removes the Python syntax error caused by a regex backslash inside an f-string expression on Windows/Python versions that reject it.
- Runtime, operation, OpenAPI, response metadata, request metadata, and compile smokes pass.
- API paths, response bodies, DB schema, and environment files remain unchanged.

## v240.backend-admin-request-payload-validation-contract

- Added `admin_request_payload_validation_contract.py` to freeze normal admin request alias serialization.
- Added representative FastAPI 422 `detail` checks for all 10 admin body request schemas.
- Validation runs in an isolated FastAPI app and stops before service or database execution.
- Preserved all admin route paths, response body shapes, write guards, DB settings, env settings, and seed data.
- Added the v240 smoke to `tools/run_smoke_core.sh` and updated admin readiness version.
