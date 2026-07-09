# Backend Admin Overview/Snapshots Service Split

버전: **v199 backend admin overview/snapshots service split**

## 목적

백엔드 `admin_service.py`가 커진 상태라, 가장 안전한 조회 전용 묶음인 overview/save snapshots 기능부터 외부 서비스 파일로 분리했습니다.

## 추가 파일

- `backend/app/services/admin/__init__.py`
- `backend/app/services/admin/admin_overview_snapshots_service.py`
- `tools/smoke_backend_admin_overview_snapshots_service_split.py`

## 분리한 기능

- `get_readonly_overview`
- `list_save_snapshot_summaries`
- `_get_master_data_counts`
- `_get_save_snapshot_summary`
- `_get_user_summary`
- `_build_snapshot_filters`
- `_build_snapshot_where_clauses`
- `_snapshot_order_by`
- `_count_save_snapshots`
- `_serialize_save_snapshot_summary`
- `_count_filled_items`

## 유지한 것

- `backend/app/api/routes/admin.py` 변경 없음
- `backend/app/schemas/admin.py` 변경 없음
- `AdminService` facade 유지
- API route public method 이름 유지
- DB schema/env 변경 없음

## 검증

실행 위치: 프로젝트 루트

```bash
python tools/smoke_backend_admin_overview_snapshots_service_split.py
```

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
```
