# Upgrade RPG

현재 인계 기준: **v267.next-chat-handoff-ready**

직전 기능 기준: `v266.admin-practical-ux-polish`

관리자 readiness: `v250.backend-admin-rollback-snapshot`

Backend splitStatus: `admin-schema-field-constraint-contract-v238`

## 현재 상태

- 관리자 HTML 페이지는 임시 운영/검증 도구로 충분히 안정화했습니다.
- 게임 콘텐츠 개발은 당분간 보류합니다.
- 다음 우선순위는 Vue + FastAPI + DB + 배포 직전 구조 준비입니다.
- DB, env, seed, 인증, 기존 route, API 응답 body, Write Guard, 실제 write 로직은 유지합니다.

## 먼저 볼 파일

1. `NEXT_CHAT_PROMPT.md`
2. `NEXT_CHAT_HANDOFF.md`
3. `docs/current/CURRENT_STATUS.md`
4. `docs/current/VUE_FASTAPI_DB_TRANSITION_PLAN.md`
5. `docs/current/ROADMAP.md`
6. `docs/NEXT_STEPS.md`
7. `docs/PROJECT_WORKING_RULES.md`

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
