# 다음 채팅 인계 — Upgrade RPG v268 structure transition prep

## 최신 ZIP

`rpg_v268_project_structure_transition_prep.zip`

이 ZIP은 v267 handoff ZIP을 기준으로 v268 구조 점검과 Vue/FastAPI/DB 전환 준비 문서를 갱신한 버전입니다.

## 현재 안정 기준

- 이번 작업 기준: `v268.project-structure-transition-prep`
- 직전 기능 기준: `v266.admin-practical-ux-polish`
- readiness version: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`

## v266까지의 결론

관리자 HTML 페이지는 임시 운영/검증 도구로 충분히 안정화했습니다.

현재 관리자 페이지에서 가능한 것:

- 마스터 데이터 카탈로그 조회
- 마스터 데이터 상세 확인
- 신규 row 생성 Preview
- 편집 Preview
- ChangeLog 조회
- Rollback Preview
- 생성 row 삭제 Preview
- 삭제 row 복원 Preview
- Preview fixture 점검
- Live Preview API 응답 표시 점검
- 공통 Diff/Snapshot/Preview summary 렌더링
- 초보자용 Admin Workspace

v266 사용자 피드백 반영:

- 카탈로그 보기 방식 3분할은 제거했습니다.
- 긴 값 모달은 유지하되 미리보기 폭을 줄였습니다.
- 버튼 위험도 텍스트 chip은 제거하고 색상/tooltip만 남겼습니다.
- 상세 화면 바로가기 버튼은 관련 섹션을 펼치고 스크롤 이동하도록 보완했습니다.

## v268에서 한 일

v268은 문서/구조 분석 중심 작업입니다.

완료:

- 현재 파일/폴더 구조 분석
- `admin.html`, `index.html`, `src/`, `backend/`, `tools/`, `docs/` 역할 정리
- Vue 전환 시 보존/이식/대체 후보 분류
- smoke/contract 경로 의존성 1차 분석
- 실제 파일 대이동 보류 결정
- Vue/FastAPI/DB 전환 계획 확장
- `docs/NEXT_STEPS.md`, `docs/current/PROJECT_STRUCTURE.md`, `docs/current/VUE_FASTAPI_DB_TRANSITION_PLAN.md` 등 갱신

## v268 핵심 결론

당장 `legacy/` 폴더로 대이동하지 않습니다.

이유:

- `admin.html`은 smoke/문서/도구에서 많이 참조합니다.
- `index.html`도 게임 smoke와 관리자 URL helper에서 참조합니다.
- `src/api`와 `src/api/admin`은 frontend/admin smoke가 직접 확인합니다.
- `backend/app/api/routes`와 `backend/app/services`는 backend contract가 직접 확인합니다.
- `tools/run_smoke_core.sh`는 contract 등록 여부 확인에 쓰입니다.

따라서 다음 단계는 기존 legacy 구조 옆에 Vue 앱을 추가할 수 있는지 확인하는 방향이 안전합니다.

## 앞으로의 방향

사용자가 명확히 정했습니다.

당분간 게임 콘텐츠 개발은 하지 않습니다.

보류:

- 장비/스킬/보스/필드/드랍/강화/밸런스 신규 개발

우선:

- Vue + FastAPI + DB + 배포 직전 구조 완성 준비
- 프로젝트 구조 정리
- legacy HTML/JS 경계 확정
- FastAPI 구조 정리 계획
- PostgreSQL/Alembic 도입 준비
- 인증 설계 준비
- Vue 앱 초기 세팅과 관리자 이식 계획

## 다음 추천 작업

다음 채팅에서는 `v269 legacy 경로 의존성 자동 목록화 + Vue 앱 생성 위치 결정`부터 시작하는 것이 좋습니다.

권장 순서:

1. ZIP 압축 해제
2. 현재 문서 확인
3. smoke가 직접 읽는 경로 목록 자동 추출
4. 이동 금지/이식 후보/나중 대체 후보 재분류
5. `frontend/vue-app/` 생성 여부 결정
6. 생성한다면 기존 `admin.html`, `index.html`, `src/`는 그대로 유지
7. Vue 기본 검증과 기존 core smoke 검증을 분리
8. 전체 smoke/compileall 확인
9. 새 ZIP 생성

## 반드시 유지할 것

- DB 변경 금지
- env 변경 금지
- seed 변경 금지
- 인증 변경 금지
- 기존 route path 변경 금지
- API 응답 body 변경 금지
- Write Guard 변경 금지
- 실제 write 로직 변경 금지
- 관리자 Preview/Apply 요청 body 변경 금지
- 기존 Smoke/Contract 의미 변경 금지

## 주요 문서

- `NEXT_CHAT_PROMPT.md`
- `NEXT_CHAT_HANDOFF.md`
- `docs/current/CURRENT_STATUS.md`
- `docs/current/VUE_FASTAPI_DB_TRANSITION_PLAN.md`
- `docs/current/PROJECT_STRUCTURE.md`
- `docs/current/ROADMAP.md`
- `docs/NEXT_STEPS.md`
- `docs/PROJECT_WORKING_RULES.md`

## 검증 결과

v268은 문서 중심 작업입니다.
런타임 코드 변경은 하지 않았습니다.

확인한 검증:

- `python -m compileall -q backend/app backend/scripts tools`
- JS 문법 검사
- `bash tools/run_smoke_core.sh`
- ZIP 무결성 검사
