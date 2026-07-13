기호의 Upgrade RPG 프로젝트를 이어서 진행합니다.

이번에 첨부하는 ZIP이 현재 최신 프로젝트입니다.
반드시 이 ZIP을 기준으로 작업해주세요.

========================
사용자/응답 방식
========================

사용자는 코딩을 거의 모릅니다.
설명은 항상 한국어로 쉽고 자세하게 해주세요.

터미널 명령을 줄 때는 반드시 실행 위치를 먼저 적어주세요.
`npm install`, `npm run dev`, `npm run build` 같은 Vue/npm 명령은 `.venv`를 켤 필요가 없는지까지 같이 말해주세요.
FastAPI/Python 명령은 `.venv`를 켠 상태 기준으로 안내해주세요.

새로 설치해야 하는 파일/라이브러리/프레임워크가 있으면 사용자가 확인할 사항과 함께 반드시 알려주세요.

git 명령은 git status && git add . && git commit -m "..." && git push 형태로 한 줄 블록으로 주세요.

필요한 라이브러리나 파일은 설치/추가해도 됩니다.
여러 단계를 한 번에 진행해도 됩니다.
다만 위험한 작업은 반드시 작게 나누고 검증 후 진행해주세요.

========================
현재 최신 기준
========================

최신 ZIP:
rpg_v273_local_dev_cors_vue_fix.zip

직전 기능 기준:
v273.local-dev-cors-vue-fix

readiness version:
v250.backend-admin-rollback-snapshot

backend splitStatus:
admin-schema-field-constraint-contract-v238

========================
v273까지 완료된 핵심 상태
========================

기존 실제 화면:

- 게임: 루트 index.html
- 관리자: 루트 admin.html
- legacy JS/CSS: 루트 src/

Vue 전환 준비:

- v270에서 frontend/vue-app/에 Vite + Vue 기본 shell 추가
- /game, /admin Vue route 추가
- v271에서 frontend/vue-app/src/api/에 읽기 전용 API client 준비 구조 추가
- v272에서 Vue shell 화면에 안전한 GET API 상태 확인 패널 추가
- v273에서 Vue 개발 서버 5173 → FastAPI 8000 호출 CORS 오류 수정

v272에서 실제 화면에 연결한 API:

- /game: GET /health
- /admin: GET /health
- /admin: GET /admin/requirements

v273 CORS 수정:

- backend/app/core/config.py에서 local/debug 환경 기본 CORS origin 보강
- 오래된 로컬 .env에 5173이 없어도 Vue 개발 서버 호출 허용
- production/debug-false에서는 명시 origin만 사용
- tools/smoke/backend/smoke_backend_local_cors.py 추가

========================
지금부터의 방향
========================

당분간 게임 콘텐츠 개발은 하지 않습니다.

보류할 작업:

- 장비 추가
- 스킬 추가
- 보스 추가
- 필드 추가
- 드랍률/밸런스 조정
- 강화 수치 조정
- 신규 콘텐츠 기획 반영

앞으로 우선순위는 다음입니다.

1. FastAPI 구조 정리 계획 수립
2. PostgreSQL/Alembic 도입 준비
3. 인증 설계 준비
4. 관리자 페이지 Vue 이식 계획
5. 게임 화면 Vue 이식 계획
6. 배포 직전 안정화 계획

========================
다음 단계 추천 작업
========================

다음 채팅의 첫 작업은 v274로 진행해주세요.

추천 작업명:

v274 FastAPI 구조 정리 계획 구체화

작업 목표:

- 현재 backend/app/api/routes, backend/app/services, backend/app/schemas, backend/app/models 역할을 실제 파일 기준으로 정리합니다.
- Vue에서 앞으로 사용할 read-only API와 legacy 유지 API를 구분합니다.
- route path/API response body는 변경하지 않습니다.
- DB/Alembic/인증은 실제 변경하지 않고 계획만 문서화합니다.
- 기존 smoke/contract 의미를 깨지 않는지 영향 범위를 확인합니다.

추천 산출물:

- docs/current/FASTAPI_STRUCTURE_PLAN.md 신규 작성
- docs/current/VUE_FASTAPI_DB_TRANSITION_PLAN.md 갱신
- docs/current/CURRENT_STATUS.md 갱신
- docs/NEXT_STEPS.md 갱신
- 필요하면 구조 분석용 smoke만 추가

========================
절대 변경 금지 / 고위험 항목
========================

아래는 사용자 명시 승인 없이는 변경하지 마세요.

- DB 구조
- env
- seed
- 인증
- API 응답 body
- 기존 route path
- 실제 write 로직
- Write Guard
- 관리자 Preview/Apply 요청 body
- 기존 Smoke/Contract 의미

========================
검증 원칙
========================

코드나 구조를 건드렸다면 최소 다음을 확인하세요.

- 관련 전용 smoke
- node --check 또는 JS 문법 검사
- python -m compileall -q backend/app backend/scripts tools
- bash tools/run_smoke_core.sh
- ZIP 무결성 검사

========================
답변 형식
========================

항상 마지막에는 아래 5개를 포함해주세요.

1. 이번에 한 일
2. 검증 완료한 것
3. 서버 재실행 명령 — 실행 위치와 .venv 상태 포함
4. git 명령 — 프로젝트 루트에서 한 줄
5. 다음 추천 단계

작업 후에는 새 ZIP도 같이 만들어주세요.
