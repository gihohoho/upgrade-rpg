기호의 Upgrade RPG 프로젝트를 이어서 진행합니다.

이번에 첨부하는 ZIP이 현재 최신 프로젝트입니다.
반드시 이 ZIP을 기준으로 작업해주세요.

========================
사용자/응답 방식
========================

사용자는 코딩을 거의 모릅니다.
설명은 항상 한국어로 쉽고 자세하게 해주세요.

터미널 명령을 줄 때는 반드시 실행 위치를 먼저 적어주세요.
`npm install`, `npm run dev`, `npm run build` 같은 npm/Vue 명령은 `.venv`를 켤 필요가 있는지/없는지 반드시 같이 말해주세요.
FastAPI/Python 명령은 `.venv`를 켠 상태 기준으로 안내해주세요.

git 명령은 git status && git add . && git commit -m "..." && git push 형태로 한 줄 블록으로 주세요.

필요한 라이브러리나 파일은 설치/추가해도 됩니다.
여러 단계를 한 번에 진행해도 됩니다.
새로 설치해야 하는 파일/라이브러리/프레임워크가 있으면 사용자가 확인할 사항과 함께 반드시 알려주세요.

다만 위험한 작업은 반드시 작게 나누고 검증 후 진행해주세요.

========================
현재 최신 기준
========================

최신 ZIP:
rpg_v275_backend_route_map_report.zip

직전 기능 기준:
v275.backend-route-map-report

readiness version:
v250.backend-admin-rollback-snapshot

backend splitStatus:
admin-schema-field-constraint-contract-v238

========================
v275까지 완료된 핵심 상태
========================

관리자 페이지는 임시 운영/검증 도구로 충분한 수준까지 안정화했습니다.

v270~v273:

- `frontend/vue-app/`에 Vue 기본 shell 생성
- `/game`, `/admin` Vue route 준비
- Vue read-only API client 준비
- Vue shell에서 `GET /health`, `GET /admin/requirements` 상태 확인
- local CORS 오류 수정

v274:

- FastAPI 구조 정리 계획 문서화
- `backend/app/api/routes`, `services`, `schemas`, `models`, `db`, `core` 역할 분석

v275:

- FastAPI route map 자동 보고서 추가
- `docs/current/BACKEND_ROUTE_MAP.md` 생성
- 전체 route 27개 확인
- GET 15개, POST 12개 확인
- Vue read-only 연결 후보와 보류 route 분리
- `frontend/vue-app/src/api/adminReadOnlyApi.js`에서 `rowId` 입력을 backend query `id`로 변환하도록 수정

현재 Vue 자동 smoke 화면에 연결된 route:

- `GET /api/v1/health`
- `GET /api/v1/admin/requirements`

다음 연결 후보:

- `GET /api/v1/admin/master-data/domains`

계속 보류:

- 관리자 Preview 계열 POST
- 관리자 Apply/write 계열 POST
- `POST /api/v1/game/save`
- 인증/권한/Write Guard가 필요한 route

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

1. Vue read-only 관리자 패널을 매우 작게 확장
2. FastAPI 구조 정리 계획 유지
3. PostgreSQL/Alembic 도입 준비
4. 인증 설계 준비
5. 관리자 페이지 Vue 이식 계획
6. 게임 화면 Vue 이식 계획
7. 배포 직전 안정화 계획

========================
다음 단계 추천 작업
========================

다음 채팅의 첫 작업은 v276로 진행해주세요.

추천 작업명:

v276 Vue admin read-only catalog mini panel

작업 목표:

- Vue 관리자 shell에 작은 read-only 카탈로그 점검 패널을 추가합니다.
- 첫 연결은 `GET /api/v1/admin/master-data/domains`만 사용합니다.
- loading/error/empty/success 상태를 표시합니다.
- catalog row 목록, detail, relations는 아직 자동 호출하지 않습니다.
- Preview/Apply/write route는 계속 보류합니다.
- 기존 `admin.html`, `index.html`, 루트 `src/`는 유지합니다.
- route path/API response body는 변경하지 않습니다.
- DB/Alembic/인증/env/seed는 변경하지 않습니다.

추천 산출물:

- `frontend/vue-app/src/components/AdminReadOnlyCatalogMiniPanel.vue`
- `frontend/vue-app/src/pages/AdminShell.vue` 갱신
- `docs/current/VUE_ADMIN_READONLY_CATALOG_PANEL.md`
- 관련 frontend smoke 추가
- `docs/current/BACKEND_ROUTE_MAP.md` 유지 검사
- `docs/NEXT_STEPS.md`, `NEXT_CHAT_HANDOFF.md`, `NEXT_CHAT_PROMPT.md` 갱신

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
새 Contract 추가 원칙
========================

새 Contract를 추가해야 할 때는 반드시 아래 순서로 진행하세요.

1. 현재 환경에서 먼저 실제 실행
2. 환경별 차이 확인
3. Contract 작성
4. Backend readiness 등록
5. Frontend readiness 등록
6. Frontend 반환 객체 등록
7. Parity 검사
8. Admin ReadOnly 검사
9. 기존 전체 Smoke
10. compileall
11. ZIP 생성

절대 “될 것이다”라고 추측해서 Contract를 만들지 마세요.

========================
반드시 반복하지 말아야 할 실수
========================

- Frontend readiness 계산만 하고 반환 객체에 누락
- Backend Contract 추가 후 Frontend Contract 목록 누락
- Backend routeContract 추가 후 Frontend routeContract 누락
- FastAPI/Starlette/Pydantic 환경 차이를 한 결과만 정답으로 고정
- 새 Contract 후 Parity 검사 누락
- 새 Contract 후 ReadOnly 검사 누락
- run_smoke_core.sh 통과 전 ZIP 생성

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
