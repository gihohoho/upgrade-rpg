# Upgrade RPG v222 패키지

현재 안정 버전: **v222 backend admin service facade MRO contract**

새 채팅 인수인계 ZIP: **rpg_v222_backend_admin_service_facade_contract_ready.zip**

## 이번 v221~v222에서 정리한 것

v221~v222에서는 `backend/app/services/admin_service.py`를 더 읽기 쉬운 진짜 facade 형태로 정리하고, 앞으로 mixin 상속 순서가 실수로 바뀌지 않도록 별도 contract/smoke를 추가했습니다.

- v221: `AdminService` 상속 목록을 다중 줄 MRO로 정리
- v221: `admin_service.py`에 `__all__ = ["AdminService"]` 명시
- v222: `backend/app/services/admin_service_facade_contract.py` 추가
- v222: AdminService facade class / mixin order / line limit / legacy marker 제거 상태를 contract로 검증
- v222: `backend/app/services/admin_service_split_contract.py`에 facade contract 파일과 split group 추가
- v222: 관리자 readiness 버전/flag 갱신
- API path/schema/응답 구조 변경 없음
- DB/env 변경 없음

## 주요 변경 파일

- `backend/app/services/admin_service.py`
- `backend/app/services/admin_service_facade_contract.py`
- `backend/app/services/admin_service_split_contract.py`
- `src/api/admin-page-readonly.js`
- `tools/smoke_backend_admin_service_facade_contract.py`
- `tools/run_smoke_core.sh`
- 기존 backend admin smoke 일부

## 관리자 콘솔 확인

```js
checkAdminReadOnlyPageReady().version
// v222.backend-admin-service-facade-contract
```

```js
checkAdminReadOnlyPageReady().backendServiceFacadeContractReady
// true
```

```js
getAdminBackendServiceSplitContractReadiness().splitStatus
// admin-service-facade-contract-v222
```

## 검증 명령

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
python tools/smoke_backend_admin_service_facade_contract.py
python tools/smoke_seed_import_long_asset_columns.py
python tools/smoke_seed_import_structure.py
python -m compileall -q backend/app backend/scripts tools
```

참고: 이번 패키지에서는 `run_smoke_core.sh`가 v220 smoke까지 통과하는 로그를 확인했고, 도구 시간 제한 때문에 v222 전용 smoke/마지막 tail smoke/seed/compileall은 별도 명령으로 통과 확인했습니다.
