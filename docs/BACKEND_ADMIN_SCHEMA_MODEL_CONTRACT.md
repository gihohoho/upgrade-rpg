# Backend Admin Schema/Model Contract — v236

관리자 API의 request schema가 route 또는 OpenAPI에서 조용히 바뀌는 문제를 막는 계약입니다.

## 검증 범위

- OpenAPI `components.schemas`에 노출되는 Admin request schema 11개
- 관리자 body route 11개와 `backend/app/schemas/admin.py` 모델 이름 연결
- Pydantic 필드 alias와 OpenAPI property 이름 일치
- 쓰기 apply schema 5개의 `confirmText`와 `reason` 유지
- 허용된 비노출 레거시 모델 `AdminChangeApplyRequest` 보존

## 안전 범위

- route path 변경 없음
- API 응답 body 구조 변경 없음
- DB 변경 없음
- env 변경 없음

## 검증

실행 위치: 프로젝트 루트

```bash
python tools/smoke_backend_admin_schema_model_contract.py
bash tools/run_smoke_core.sh
python -m compileall -q backend/app backend/scripts tools
```
