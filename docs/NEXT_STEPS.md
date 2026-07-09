# Next Steps — after v214

추천 다음 단계는 **v215 admin overview/snapshot route module split** 입니다.

## 추천 작업

1. `backend/app/api/routes/admin_overview_snapshot_routes.py` 생성
2. `requirements`, `overview`, `save-snapshots`, `change-preview` route 이동
3. 기존 `admin.py`는 route include facade만 남기기
4. 기존 API path/schema/envelope 유지 smoke 작성
5. core smoke/seed smoke/compileall 검증

주의:
- route path는 유지
- `AdminService` facade 유지
- schema 변경 금지
- DB/env 변경 금지
