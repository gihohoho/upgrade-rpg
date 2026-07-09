# Upgrade RPG v226 패키지

현재 안정 버전: **v226 backend admin runtime route contract**

새 채팅 인수인계 ZIP: **rpg_v226_backend_admin_runtime_route_contract_ready.zip**

## 이번 v225~v226에서 정리한 것

v225~v226에서는 관리자 route module 분리 상태를 실제 FastAPI 앱 등록 상태까지 검증하도록 강화했습니다. 기존 v224는 route decorator가 정해진 파일에만 있는지 확인했고, 이번 단계는 `app.main`에 최종 등록된 `/api/v1/admin/...` route 목록과 static ownership map이 완전히 일치하는지 확인합니다.

- v225: `backend/app/api/routes/admin_runtime_route_contract.py` 추가
- v225: FastAPI runtime route 목록과 static route ownership map 비교
- v225: 누락/예상 밖/중복 method+path route 검증
- v225: `/api/v1/admin` prefix 유지 검증
- v226: `backend/app/services/admin_service_split_contract.py` splitStatus 갱신
- v226: `src/api/admin-page-readonly.js` readiness 버전/flag 갱신
- v226: `tools/smoke_backend_admin_runtime_route_contract.py` 추가
- v226: `tools/run_smoke_core.sh`에 runtime route smoke 연결
- route path/schema/API 응답 구조 변경 없음
- DB/env 변경 없음

## 확인 명령

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
python tools/smoke_backend_admin_runtime_route_contract.py
python tools/smoke_seed_import_long_asset_columns.py
python tools/smoke_seed_import_structure.py
python -m compileall -q backend/app backend/scripts tools
```

## 관리자 페이지 콘솔 확인

```js
checkAdminReadOnlyPageReady().version
// v226.backend-admin-runtime-route-contract
```

```js
checkAdminReadOnlyPageReady().backendRuntimeRouteContractReady
// true
```

```js
checkAdminReadOnlyPageReady().backendRuntimeRouteRegistrationReady
// true
```

```js
getAdminBackendServiceSplitContractReadiness().splitStatus
// admin-runtime-route-contract-v226
```

## 서버 재실행

실행 위치: backend 폴더

```bash
uvicorn app.main:app --reload
```

DB reset/seed 재실행은 필요 없습니다.

## 참고

`run_smoke_core.sh`는 로컬/도구 환경에서 시간이 오래 걸릴 수 있습니다. 이번 패키지에서는 core smoke가 backend route response data/meta 지점까지 통과한 뒤 도구 시간 제한에 걸렸고, 남은 tail smoke / v226 runtime route smoke / seed / compileall은 별도 실행으로 통과 확인했습니다.
