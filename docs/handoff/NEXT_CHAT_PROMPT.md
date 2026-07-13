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

git 명령은 git status && git add . && git commit -m "..." && git push 형태로 한 줄 블록으로 주세요.

필요한 라이브러리나 파일은 설치/추가해도 됩니다.
다만 새로 설치해야 하는 파일/라이브러리/프레임워크가 있으면 사용자가 확인할 사항과 함께 반드시 알려주세요.

여러 단계를 한 번에 진행해도 됩니다.
다만 위험한 작업은 반드시 작게 나누고 검증 후 진행해주세요.

========================
현재 최신 기준
========================

최신 ZIP:
rpg_v271_vue_readonly_api_client.zip

직전 기능 기준:
v271.vue-readonly-api-client

readiness version:
v250.backend-admin-rollback-snapshot

backend splitStatus:
admin-schema-field-constraint-contract-v238

========================
v271까지 완료된 핵심 상태
========================

관리자 페이지는 임시 운영/검증 도구로 충분한 수준까지 안정화했습니다.

기존 실제 화면:

- 게임: 루트 index.html
- 관리자: 루트 admin.html
- legacy JS/CSS: 루트 src/

Vue 전환 준비:

- v270에서 frontend/vue-app/에 Vite + Vue 기본 shell 추가
- /game, /admin Vue route 추가
- v271에서 frontend/vue-app/src/api/에 읽기 전용 API client 준비 구조 추가
- AdminShell/GameShell에 GET route 준비 목록 표시
- 아직 Vue shell에서 실제 API를 자동 호출하지 않음

v271에서 추가된 주요 파일:

- frontend/vue-app/src/api/config.js
- frontend/vue-app/src/api/readOnlyRoutes.js
- frontend/vue-app/src/api/readOnlyClient.js
- frontend/vue-app/src/api/adminReadOnlyApi.js
- frontend/vue-app/src/api/gameReadOnlyApi.js
- frontend/vue-app/src/api/index.js
- docs/current/VUE_READONLY_API_CLIENT.md
- tools/smoke/frontend/smoke_vue_readonly_api_client.py

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

1. Vue 읽기 전용 API 화면 연결
2. loading/error/success 상태 구조 만들기
3. FastAPI 구조 정리 계획 수립
4. PostgreSQL/Alembic 도입 준비
5. 인증 설계 준비
6. 관리자 페이지 Vue 이식 계획
7. 게임 화면 Vue 이식 계획
8. 배포 직전 안정화 계획

========================
다음 단계 추천 작업
========================

다음 채팅의 첫 작업은 v272로 진행해주세요.

추천 작업명:

v272 Vue read-only API smoke 화면 연결

작업 목표:

- Vue shell에서 실제 GET API를 아주 작게 연결합니다.
- 처음에는 /health 또는 /admin/requirements처럼 안전한 조회 API만 사용합니다.
- loading/error/success 상태 표시를 만듭니다.
- 실패해도 shell이 깨지지 않도록 합니다.
- Preview/Apply/write 요청은 계속 제외합니다.
- 인증/interceptor는 아직 실제 구현하지 않습니다.
- 기존 admin.html/index.html은 계속 유지합니다.

추천 산출물:

- Vue read-only API status component 또는 composable
- docs/current/VUE_READONLY_API_CLIENT.md 갱신
- docs/current/CURRENT_STATUS.md 갱신
- docs/NEXT_STEPS.md 갱신
- Vue shell/API smoke 갱신

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
