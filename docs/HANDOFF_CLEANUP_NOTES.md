# Handoff Cleanup Notes — v246

## 정리한 항목

- 루트 README, backend readiness, current status, next steps를 v246 기준으로 갱신
- 오래된 `NEXT_STEP_V240_REQUEST_PAYLOAD_VALIDATION.md`를 `docs/archive/stage-notes/`로 이동
- Windows 가상환경 `backend/.venv` 제거
- `__pycache__`, `.pyc`, pytest/ruff/mypy 캐시 제거
- 실제 로컬 설정인 `backend/.env`를 전달 ZIP에서 제거하고 `.env.example`만 유지
- FastAPI TestClient용 `httpx2`를 backend dev 의존성에 기록

## 유지한 항목

- 기능 코드와 route 구조
- DB/schema/seed
- API 주소와 응답 body
- 인증 및 write guard
- 단계별 smoke 파일과 과거 기록 문서

## 패키징 원칙

다음 파일은 Git과 전달 ZIP에 포함하지 않습니다.

```text
.env
backend/.env
.venv/
backend/.venv/
node_modules/
__pycache__/
*.pyc
*.zip
```
