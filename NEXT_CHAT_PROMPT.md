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

필요한 라이브러리나 파일은 설치/추가해도 됩니다.
여러 단계를 한 번에 진행해도 됩니다.

다만 위험한 작업은 반드시 작게 나누고 검증 후 진행해주세요.

========================
현재 최신 기준
========================

최신 ZIP:
rpg_v269_legacy_path_dependency_report.zip

현재 작업 기준:
v269.legacy-path-dependency-report

직전 기능 기준:
v266.admin-practical-ux-polish

직전 구조 기준:
v268.project-structure-transition-prep

readiness version:
v250.backend-admin-rollback-snapshot

backend splitStatus:
admin-schema-field-constraint-contract-v238

========================
v269까지 완료된 핵심 상태
========================

관리자 페이지는 임시 운영/검증 도구로 충분한 수준까지 안정화했습니다.

v269에서 완료한 일:

- legacy 경로 의존성 자동 목록화 도구 추가
- `docs/current/LEGACY_PATH_DEPENDENCIES.md` 생성
- 새 Vue 앱 생성 위치를 `frontend/vue-app/`로 결정
- 기존 `admin.html`, `index.html`, `src/`는 이동하지 않기로 확정
- root `src/`는 Vue 앱 소스가 아니라 legacy JS/CSS 폴더라고 문서화
- 실제 Vue 앱 생성은 아직 하지 않음
- DB/env/seed/auth/API body/route/write guard/실제 write 로직 변경 없음

새 주요 파일:

- `tools/report_legacy_path_dependencies.py`
- `docs/current/LEGACY_PATH_DEPENDENCIES.md`

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

1. Vue 앱 기본 shell 생성
2. 기존 legacy smoke와 Vue 검증 분리
3. FastAPI 구조 정리 계획 수립
4. PostgreSQL/Alembic 도입 준비
5. 인증 설계 준비
6. 관리자 페이지 Vue 이식 계획
7. 게임 화면 Vue 이식 계획
8. 배포 직전 안정화 계획

========================
다음 단계 추천 작업
========================

다음 채팅의 첫 작업은 v270으로 진행해주세요.

추천 작업명:

v270 Vue 앱 기본 shell 생성

작업 목표:

- `frontend/vue-app/`에 Vite + Vue 기본 프로젝트를 생성합니다.
- 기존 `admin.html`, `index.html`, `src/`는 절대 이동하지 않습니다.
- Vue 앱에는 처음부터 실제 관리자/게임 로직을 붙이지 않습니다.
- `AdminShell.vue`, `GameShell.vue` 같은 빈 shell과 router만 준비합니다.
- Vue 앱 실행/빌드 검증 명령을 문서화합니다.
- 기존 `bash tools/run_smoke_core.sh`가 계속 통과하는지 확인합니다.
- DB/env/seed/auth/API body/route/write guard/실제 write 로직은 변경하지 않습니다.

추천 산출물:

- `frontend/vue-app/` 기본 Vue 구조
- `frontend/vue-app/README.md`
- `docs/current/VUE_APP_SHELL_PLAN.md`
- `docs/current/VUE_FASTAPI_DB_TRANSITION_PLAN.md` 갱신
- `docs/NEXT_STEPS.md` 갱신
- 새 ZIP 생성

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
검증 원칙
========================

코드나 구조를 건드렸다면 최소 다음을 확인하세요.

- 관련 전용 smoke
- `python tools/report_legacy_path_dependencies.py --check`
- node --check 또는 JS 문법 검사
- `python -m compileall -q backend/app backend/scripts tools`
- `bash tools/run_smoke_core.sh`
- ZIP 무결성 검사

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
