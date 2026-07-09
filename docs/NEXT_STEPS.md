# Next Steps — after v212

추천 다음 단계는 **v213 admin route module split preparation** 입니다.

## 추천 작업

1. `admin.py`에 남은 기능별 endpoint 묶음 확인
2. `admin_master_data_routes.py` 분리 후보 준비
3. `admin_change_log_routes.py` 분리 후보 준비
4. 기존 API path/schema/envelope 유지 smoke 작성
5. 첫 분리는 master-data read-only route부터 진행

주의:
- route path는 유지
- `AdminService` facade 유지
- schema 변경 금지
- DB/env 변경 금지
