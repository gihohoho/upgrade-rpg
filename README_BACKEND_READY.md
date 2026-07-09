# Backend Ready Notes — v204

현재 안정 버전: **v204 backend admin shared utils service split**

## 완료 흐름

- v198: backend admin service split contract 고정
- v199.1: overview/save snapshots service 분리 + hotfix
- v200: master catalog/detail/relations service 분리
- v201: create lifecycle service 분리
- v202: change logs/detail/rollback service 분리
- v203: edit draft preview/apply service 분리
- v204: shared utils service 분리

## v204 변경

- `backend/app/services/admin/admin_shared_utils.py` 추가
- 공용 count/relation/serialization/helper를 shared utils로 이동
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
