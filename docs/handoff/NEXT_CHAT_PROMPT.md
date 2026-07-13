# 다음 채팅 시작 프롬프트 — Upgrade RPG v268 기준

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
rpg_v268_project_structure_transition_prep.zip

이번 작업 기준:
v268.project-structure-transition-prep

직전 기능 기준:
v266.admin-practical-ux-polish

readiness version:
v250.backend-admin-rollback-snapshot

backend splitStatus:
admin-schema-field-constraint-contract-v238

========================
v268까지 완료된 핵심 상태
========================

관리자 페이지는 임시 운영/검증 도구로 충분한 수준까지 안정화했습니다.

완료된 주요 관리자 기능:

- 마스터 데이터 카탈로그/상세 조회
- 신규 row 생성 Preview
- 기존 row 편집 Preview
- ChangeLog 조회
- Rollback Preview
- 생성 row 삭제 Preview
- 삭제 row 복원 Preview
- 공통 Unified Diff 렌더러
- 공통 Rollback Snapshot 표시
- Snapshot fingerprint/무결성 검사
- Preview 결과 요약 공통 렌더러
- 고정 fixture Preview 점검 패널
- 실제 Preview API 응답 표시 점검 패널
- Admin Workspace / 업무 모드 / 초보자 안내
- 카탈로그 compact UX
- 날짜/JSON 키 축약 표시
- 긴 값 모달 보기
- 상세 화면 바로가기 버튼 보완

v268에서 완료한 작업:

- 현재 프로젝트 구조 실제 분석
- `admin.html`, `index.html`, `src`, `backend`, `tools`, `docs` 역할 정리
- Vue 전환 시 보존/이식/대체 후보 분류
- smoke/contract 경로 의존성 1차 분석
- 실제 파일 대이동 보류 결정
- `docs/current/PROJECT_STRUCTURE.md` 갱신
- `docs/current/VUE_FASTAPI_DB_TRANSITION_PLAN.md` 확장
- `docs/NEXT_STEPS.md` 갱신
- `docs/current/ROADMAP.md` 갱신
- `README.md`, `NEXT_CHAT_HANDOFF.md`, `NEXT_CHAT_PROMPT.md` 갱신

v268 핵심 결론:

- 당장 `legacy/` 폴더로 대이동하지 않습니다.
- `admin.html`, `index.html`, `src/api`, `src/api/admin`, `backend/app/api/routes`, `backend/app/services`, `tools/run_smoke_core.sh` 경로 의존성이 큽니다.
- 다음 단계는 기존 legacy 구조 옆에 Vue 앱을 추가할 수 있는지 확인하는 방향이 안전합니다.

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

1. legacy 경로 의존성 자동 목록화
2. Vue 앱 생성 위치 결정
3. FastAPI 구조 정리 계획 구체화
4. PostgreSQL/Alembic 도입 준비
5. 인증 설계 준비
6. Vue 앱 초기 세팅
7. 관리자 페이지 Vue 이식 계획
8. 게임 화면 Vue 이식 계획
9. 배포 직전 안정화 계획

========================
다음 단계 추천 작업
========================

다음 채팅의 첫 작업은 v269로 진행해주세요.

추천 작업명:

v269 legacy 경로 의존성 자동 목록화 + Vue 앱 생성 위치 결정

작업 목표:

- smoke가 직접 읽는 파일 경로를 자동으로 목록화합니다.
- 이동 금지/이식 후보/나중 대체 후보를 더 정확히 나눕니다.
- `frontend/vue-app/` 생성 여부와 생성 시점을 확정합니다.
- Vue 앱을 만들더라도 기존 `admin.html`, `index.html`, `src/`는 그대로 둡니다.
- Vue 기본 검증 명령과 기존 core smoke 검증을 분리합니다.
- 문서 archive 이동은 아직 하지 말고, 먼저 smoke 영향 분석을 끝냅니다.

추천 산출물:

- `docs/current/LEGACY_PATH_DEPENDENCY_REPORT.md` 신규 작성 또는 유사 문서 작성
- `docs/current/VUE_FASTAPI_DB_TRANSITION_PLAN.md` 보완
- `docs/NEXT_STEPS.md` 갱신
- 필요하다면 `tools/`에 경로 의존성 분석 스크립트 추가
- 아직 실제 legacy 대이동은 하지 않기

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
3. 서버 재실행 명령 — 실행 위치 포함
4. git 명령 — 프로젝트 루트에서 한 줄
5. 다음 추천 단계

작업 후에는 새 ZIP도 같이 만들어주세요.
