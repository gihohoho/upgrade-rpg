# NEXT CHAT PROMPT — v239 clean package

## 현재 안정 버전

- 관리자 페이지 readiness version: `v239.2.backend-admin-schema-model-shared-collector-hotfix`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- 현재 패키지: `rpg_v239_2_next_chat_handoff_clean_ready.zip`

## 이번 단계 완료 내용

1. Runtime admin route collector를 `collect_admin_runtime_route_entries()`로 공용화
2. runtime / operation / response metadata / request metadata 계약이 같은 수집 체인을 쓰도록 정리
3. `app` → `api_router` → concrete owner router 3개 fallback 순서 유지
4. request metadata smoke가 더 이상 옛 `app.routes` 직접 검사 방식으로 `runtimeRouteCount: 0`을 내지 않도록 수정
5. OpenAPI f-string hotfix, editDraft readiness hotfix, schema/model/field constraint 계약 유지

route path, API 응답 body 구조, DB/env는 변경하지 않았습니다.

## 관리자 콘솔 확인값

```js
({
  version: checkAdminReadOnlyPageReady().version,
  pageReady: checkAdminReadOnlyPageReady().ok,
  failedChecks: checkAdminReadOnlyPageReady().failedChecks,
})
// {
//   version: "v239.2.backend-admin-schema-model-shared-collector-hotfix",
//   pageReady: true,
//   failedChecks: []
// }
```

## 검증 명령

실행 위치: 프로젝트 루트

```bash
python tools/smoke_backend_admin_request_metadata_contract.py
bash tools/run_smoke_core.sh
python -m compileall -q backend/app backend/scripts tools
```

## 서버 재실행

실행 위치: backend 폴더

```bash
uvicorn app.main:app --reload
```

DB reset/seed 재실행은 필요 없습니다.

## 다음 추천 단계

`v240 backend admin request payload and 422 validation contract`

- 정상 payload alias 직렬화 고정
- 대표 잘못된 payload의 422 validation detail 검증
- 실제 DB 쓰기 없이 request parsing 경계 검증
