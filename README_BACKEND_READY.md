# Backend Ready Notes — v214

현재 안정 버전: **v214 backend admin route module split**

## 안정화 흐름

- v198: AdminService split contract 고정
- v199~v206: AdminService 내부 서비스 분리
- v207~v210: admin route response/params/error helper 분리
- v211~v212: admin route response data/meta helper 분리
- v213~v214: admin.py 기능별 route module 분리

## v214 변경

- `backend/app/api/routes/admin_master_data_routes.py` 추가
- `backend/app/api/routes/admin_change_log_routes.py` 추가
- `admin.py`는 router include facade로 축소
- master-data API 경로는 그대로 유지
- change-log/rollback/create-delete API 경로는 그대로 유지
- API path/schema/envelope/DB/env 변경 없음

## 실행/검증

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
python tools/smoke_backend_admin_route_module_split.py
python -m compileall -q backend/app backend/scripts tools
```

실행 위치: backend 폴더

```bash
uvicorn app.main:app --reload
```
