# Backend Ready Notes — v206

현재 안정 버전: **v206 backend admin config/readiness service split**

## 완료 흐름

- v198: backend admin service split contract 고정
- v199.1: overview/save snapshots service 분리 + hotfix
- v200: master catalog/detail/relations service 분리
- v201: create lifecycle service 분리
- v202: change logs/detail/rollback service 분리
- v203: edit draft preview/apply service 분리
- v204: shared utils service 분리
- v205: config service 분리
- v206: readiness service 분리

## v205~v206 변경

- `backend/app/services/admin/admin_config.py` 추가
- `backend/app/services/admin/admin_readiness_service.py` 추가
- 큰 domain/config/allow-list/blueprint 설정을 config service로 이동
- `preview_change`, `_build_readiness`를 readiness service로 이동
- `AdminService`는 route facade로 유지
- route/schema/API/DB/env 변경 없음

## 실행 확인

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
```

실행 위치: backend 폴더

```bash
uvicorn app.main:app --reload
```

DB reset/seed 재실행은 필요 없습니다.
