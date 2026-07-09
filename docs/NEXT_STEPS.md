# Next Steps — after v210

다음 추천 단계는 **v211 admin route response data builder 준비**다.

## 추천 순서

1. `backend/app/api/routes/admin_response_data_helpers.py` 생성
2. `admin.py`의 반복 `data={...}` 요약 생성 중 위험 낮은 부분부터 helper로 이동
3. route path/schema/API 응답 구조 그대로 유지
4. static smoke로 route path와 응답 key 보존 확인
5. 이후 기능별 sub-router 분리 검토

## 주의

`admin.py`를 바로 여러 파일로 쪼개면 기존 static smoke 영향이 크다. route contract smoke를 먼저 더 강하게 만든 뒤 분리하는 것이 안전하다.
