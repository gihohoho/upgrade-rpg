# Upgrade RPG — Admin Backend Contract Ready

현재 안정 버전: **v239.2.backend-admin-schema-model-shared-collector-hotfix**

현재 ZIP: `rpg_v239_2_next_chat_handoff_final_ready.zip`

## 현재 적용 상태

- 관리자 프론트 JS thin entry / helper 분리 완료
- 관리자 백엔드 `AdminService` split 완료, facade 유지
- 관리자 route module split 완료
- `backend/app/api/routes/admin.py`는 include-router facade로 유지
- static route ownership / runtime route / operation / OpenAPI / response metadata / request metadata contract 연결 완료
- schema/model metadata contract 완료
- schema field constraint/default/required/model-config contract 완료
- 공용 admin runtime route collector 적용 완료
- API 주소, schema, 응답 body 구조, DB/env 변경 없음

## 새 채팅에서 먼저 볼 파일

1. `NEXT_CHAT_PROMPT.md` — 새 채팅에 그대로 붙여넣기 좋은 프롬프트
2. `NEXT_CHAT_HANDOFF.md` — 현재 상태와 다음 단계 요약
3. `README_BACKEND_READY.md` — 백엔드 계약 상태 요약
4. `docs/PROJECT_WORKING_RULES.md` — 작업 방식 규칙
5. `docs/NEXT_STEP_V240_REQUEST_PAYLOAD_VALIDATION.md` — 다음 추천 작업

## 관리자 콘솔 확인

```js
({
  version: checkAdminReadOnlyPageReady().version,
  pageReady: checkAdminReadOnlyPageReady().ok,
  failedChecks: checkAdminReadOnlyPageReady().failedChecks,
})
```

예상:

```js
{
  version: "v239.2.backend-admin-schema-model-shared-collector-hotfix",
  pageReady: true,
  failedChecks: []
}
```

```js
getAdminBackendServiceSplitContractReadiness().splitStatus
```

예상:

```txt
admin-schema-field-constraint-contract-v238
```

## 검증 명령

실행 위치: 프로젝트 루트

```bash
python tools/smoke_backend_admin_runtime_route_contract.py
python tools/smoke_backend_admin_request_metadata_contract.py
python tools/smoke_backend_admin_schema_model_contract.py
python tools/smoke_backend_admin_schema_field_constraint_contract.py
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

실제 DB 쓰기 없이 request parsing / validation 경계만 검증합니다.
