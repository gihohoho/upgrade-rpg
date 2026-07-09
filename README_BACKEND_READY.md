# Backend Ready Notes — v202

현재 안정 버전: **v202 backend admin change log service split**

## 현재 상태

- v198: backend admin service split contract 고정
- v199.1: overview/save snapshots service 분리 + hotfix
- v200: master catalog/detail/relations service 분리
- v201: create lifecycle service 분리
- v202: change logs/detail/rollback service 분리

## v202 변경

- `backend/app/services/admin/admin_change_log_service.py` 추가
- `AdminChangeLogService` mixin 추가
- `AdminService` facade 유지
- change logs 목록/상세/rollback 관련 메서드 이동
- `/admin/change-logs` schema guard 유지
- rollback apply 성공 경로 `return preview` 보강
- `routes/admin.py` URL/path 변경 없음
- schema/API 응답 구조 변경 없음

## 검증 명령

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
```

실행 위치: 프로젝트 루트

```bash
python tools/smoke_backend_admin_change_log_service_split.py
python tools/smoke_backend_admin_service_split_contract.py
python -m compileall -q backend/app backend/scripts tools
```

## DB / env

DB schema/env 변경 없음. DB reset/seed 재실행 필요 없음.
