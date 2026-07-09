# Next Steps — after v208

## 추천 v209

**admin route query dependency cleanup**

- `backend/app/api/routes/admin.py`의 반복 Query 기본값/limit/sort 부분을 안전하게 정리
- route path/schema/API 응답 구조 유지
- 기존 static smoke가 보는 문자열을 보존
- v209 전용 smoke test 추가

## 이후 후보

**admin router submodule split 준비**

- 바로 파일을 쪼개기 전에 route contract smoke를 강화
- `admin.py`를 facade router로 만들지 검토
- 기존 smoke가 `admin.py`를 직접 grep하는 부분이 많으므로 급하게 진행하지 말 것
