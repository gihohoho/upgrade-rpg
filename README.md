# RPG Admin Backend Split Ready

현재 안정 버전: **v234 backend admin request metadata contract**

## 현재 적용 상태

- 관리자 백엔드 서비스 분리 완료
- 관리자 route module 분리 완료
- `AdminService`는 facade로 유지
- `backend/app/api/routes/admin.py`는 include-router facade로 유지
- static route ownership / runtime route / operation / OpenAPI / response metadata contract 연결 완료
- v234에서 request/dependency metadata contract 추가 완료
- API 주소, schema, 응답 body 구조, DB/env 변경 없음

## 새 채팅에서 먼저 볼 파일

1. `NEXT_CHAT_PROMPT.md` — 새 채팅에 그대로 붙여넣기 좋은 프롬프트
2. `NEXT_CHAT_HANDOFF.md` — 현재 상태와 다음 단계 요약
3. `docs/CURRENT_STATUS.md` — 현재 안정 상태
4. `docs/NEXT_STEPS.md` — 다음 추천 작업
5. `docs/PROJECT_STRUCTURE.md` — 주요 폴더/파일 역할

## 관리자 콘솔 확인

```js
checkAdminReadOnlyPageReady().version
```

예상:

```txt
v239.2.backend-admin-schema-model-shared-collector-hotfix
```

```js
checkAdminReadOnlyPageReady().backendRequestMetadataContractReady
checkAdminReadOnlyPageReady().backendRuntimeRequestMetadataReady
checkAdminReadOnlyPageReady().backendOpenApiRequestMetadataReady
checkAdminReadOnlyPageReady().backendWriteGuardDependencyMetadataReady
```

예상:

```txt
true
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
bash tools/run_smoke_core.sh
python tools/smoke_backend_admin_request_metadata_contract.py
python tools/smoke_backend_admin_response_metadata_contract.py
python tools/smoke_seed_import_long_asset_columns.py
python tools/smoke_seed_import_structure.py
python -m compileall -q backend/app backend/scripts tools
```

## 서버 재실행

실행 위치: backend 폴더

```bash
uvicorn app.main:app --reload
```

DB reset/seed 재실행은 필요 없습니다.
