# Upgrade RPG

현재 인계 기준: **v268.project-structure-transition-prep**

직전 기능 기준: `v266.admin-practical-ux-polish`

관리자 readiness: `v250.backend-admin-rollback-snapshot`

Backend splitStatus: `admin-schema-field-constraint-contract-v238`

## 현재 상태

- 관리자 HTML 페이지는 임시 운영/검증 도구로 충분히 안정화했습니다.
- 게임 콘텐츠 개발은 당분간 보류합니다.
- v268에서는 프로젝트 구조와 Vue/FastAPI/DB 전환 준비 문서를 갱신했습니다.
- 실제 파일 대이동은 하지 않았습니다.
- `admin.html`, `index.html`, `src/`, `backend/`, `tools/` 기존 경로는 smoke/contract가 많이 참조하므로 유지합니다.
- DB, env, seed, 인증, 기존 route, API 응답 body, Write Guard, 실제 write 로직은 유지합니다.

## 먼저 볼 파일

1. `NEXT_CHAT_PROMPT.md`
2. `NEXT_CHAT_HANDOFF.md`
3. `docs/current/CURRENT_STATUS.md`
4. `docs/current/VUE_FASTAPI_DB_TRANSITION_PLAN.md`
5. `docs/current/PROJECT_STRUCTURE.md`
6. `docs/current/ROADMAP.md`
7. `docs/NEXT_STEPS.md`
8. `docs/PROJECT_WORKING_RULES.md`

## v268 핵심 결론

당장 `legacy/` 폴더로 이동하지 않습니다.

이유:

- `admin.html` 참조가 많습니다.
- `index.html` 참조가 많습니다.
- `src/api`와 `src/api/admin`을 smoke가 직접 확인합니다.
- `backend/app/api/routes`와 `backend/app/services`를 contract가 직접 확인합니다.
- `tools/run_smoke_core.sh` 포함 여부를 여러 smoke가 확인합니다.

다음 단계는 기존 구조 옆에 Vue 앱을 만들 수 있는지 확인하는 것입니다.

## 핵심 검증

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
```

실행 위치: 프로젝트 루트

```bash
python -m compileall -q backend/app backend/scripts tools
```

## 서버 실행

실행 위치: `backend` 폴더

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

그다음 프로젝트 루트의 `admin.html` 또는 `index.html`을 브라우저에서 엽니다.
