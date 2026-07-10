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
