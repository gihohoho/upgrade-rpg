기호의 Upgrade RPG 프로젝트를 이어서 진행합니다.

이번에 첨부하는 ZIP이 현재 최신 프로젝트입니다.
반드시 이 ZIP을 기준으로 작업해주세요.

========================
사용자/응답 방식
========================

사용자는 코딩을 거의 모릅니다.
설명은 항상 한국어로 쉽고 자세하게 해주세요.

터미널 명령을 줄 때는 반드시 실행 위치를 먼저 적어주세요.
git 명령은 git status && git add . && git commit -m "..." && git push 형태로 한 줄 블록으로 주세요.

앞으로 계속 사용자가 확인해야 할 사항, 설치해야 할 파일, 라이브러리, 프레임워크가 있으면 꼭 빠짐없이 알려주세요.

필요한 라이브러리나 파일은 설치/추가해도 됩니다.
여러 단계를 한 번에 진행해도 됩니다.

다만 위험한 작업은 반드시 작게 나누고 검증 후 진행해주세요.

========================
현재 최신 기준
========================

최신 ZIP:
rpg_v270_vue_app_basic_shell.zip

현재 작업 기준:
v270.vue-app-basic-shell

직전 작업 기준:
v269.legacy-path-dependency-report

직전 기능 기준:
v266.admin-practical-ux-polish

readiness version:
v250.backend-admin-rollback-snapshot

backend splitStatus:
admin-schema-field-constraint-contract-v238

========================
v270까지 완료된 핵심 상태
========================

관리자 페이지는 임시 운영/검증 도구로 충분한 수준까지 안정화했습니다.

기존 실제 화면은 그대로 유지합니다.

- 게임: 루트 index.html
- 관리자: 루트 admin.html
- legacy JS/CSS: 루트 src/

v270에서 새 Vue 기본 shell을 추가했습니다.

추가 위치:
frontend/vue-app/

추가된 주요 항목:

- Vite + Vue package.json
- vite.config.js
- Vue Router 기본 구조
- App.vue
- GameShell.vue
- AdminShell.vue
- ShellCard.vue
- base.css
- Vue shell README
- Vue shell 구조 smoke

현재 Vue route:

- / → /game redirect
- /game → GameShell.vue
- /admin → AdminShell.vue

v270 Vue shell은 아직 실제 관리자/게임 기능을 대체하지 않습니다.

========================
사용자가 설치/확인해야 할 사항
========================

Vue 앱 실행 전 처음 한 번 설치가 필요합니다.

실행 위치: frontend/vue-app 폴더
npm install

Vue 개발 서버 실행:

실행 위치: frontend/vue-app 폴더
npm run dev

브라우저 확인:
http://127.0.0.1:5173

확인할 화면:

- /game
- /admin

기존 FastAPI 서버 실행:

실행 위치: backend 폴더
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

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

1. Vue API client 읽기 전용 설계
2. 기존 FastAPI route map 문서 연결
3. FastAPI 구조 정리 계획 수립
4. PostgreSQL/Alembic 도입 준비
5. 인증 설계 준비
6. 관리자 페이지 Vue 이식 계획
7. 게임 화면 Vue 이식 계획
8. 배포 직전 안정화 계획

========================
다음 단계 추천 작업
========================

다음 채팅의 첫 작업은 v271로 진행해주세요.

추천 작업명:

v271 Vue API client 읽기 전용 설계 + backend route map 연결 준비

작업 목표:

- Vue 앱 안에 API client 기본 구조를 만듭니다.
- 기존 FastAPI route path 목록과 Vue client 후보를 문서로 연결합니다.
- 처음에는 GET/읽기 전용 API만 대상으로 합니다.
- 인증/interceptor/write는 아직 구현하지 않습니다.
- 관리자 Preview/Apply 요청 body는 변경하지 않습니다.
- 기존 admin.html, index.html, 루트 src는 유지합니다.
- 기존 smoke/contract 의미를 바꾸지 않습니다.

추천 산출물:

- frontend/vue-app/src/api/README.md 갱신
- frontend/vue-app/src/api/httpClient.js 또는 동등한 읽기 전용 초안
- docs/current/VUE_API_CLIENT_PLAN.md 추가
- docs/current/VUE_APP_SHELL.md 갱신
- tools/smoke/frontend/smoke_vue_api_client_structure.py 추가 가능
- docs/NEXT_STEPS.md 갱신

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

Vue 관련 작업을 했다면 추가로 확인하세요.

- bash tools/run_smoke_vue_shell.sh
- frontend/vue-app에서 npm install 후 npm run build 가능 여부

========================
답변 형식
========================

항상 마지막에는 아래 5개를 포함해주세요.

1. 이번에 한 일
2. 검증 완료한 것
3. 서버 재실행 명령 — 실행 위치 포함
4. git 명령 — 프로젝트 루트에서 한 줄
5. 다음 추천 단계

작업 후에는 새 ZIP도 같이 만들어주세요.
