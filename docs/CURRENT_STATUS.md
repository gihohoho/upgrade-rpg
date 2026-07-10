# Current Status — v246

현재 기준: **v246.backend-admin-write-replay-safety-contract**

Backend splitStatus: `admin-schema-field-constraint-contract-v238`

## 완료된 흐름

- 관리자 frontend thin entry/helper 분리
- backend `AdminService` facade/service split
- 관리자 route module/facade 분리
- route ownership/runtime/operation/OpenAPI/response/request metadata 계약
- schema/model/field constraint 계약
- request payload와 대표 FastAPI 422 계약
- malformed JSON·빈 body·Content-Type/Accept 계약
- media type·size policy·UTF-8/header encoding 계약
- transport header 관찰 계약
- preview replay parsing과 apply write guard 계약
- backend/frontend 계약 전체 parity smoke

## 안전 상태

- DB/env/seed 변경 없음
- route path/API 응답 body/schema/인증 변경 없음
- 실제 service 호출 및 DB write 없이 request 경계 검사
- `Idempotency-Key` 현재 미지원

## 관리자 콘솔 기대값

```js
({
  version: checkAdminReadOnlyPageReady().version,
  pageReady: checkAdminReadOnlyPageReady().ok,
  failedChecks: checkAdminReadOnlyPageReady().failedChecks,
  writeReplaySafetyReady:
    checkAdminReadOnlyPageReady().backendWriteReplaySafetyContractReady,
})
```

```js
{
  version: "v246.backend-admin-write-replay-safety-contract",
  pageReady: true,
  failedChecks: [],
  writeReplaySafetyReady: true
}
```
