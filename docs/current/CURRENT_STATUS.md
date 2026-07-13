# 현재 상태 — v268 structure transition prep

## 안정 기준

- 최신 인계 ZIP: `rpg_v268_project_structure_transition_prep.zip`
- 이번 작업 기준: `v268.project-structure-transition-prep`
- 직전 기능 기준: `v266.admin-practical-ux-polish`
- 관리자 readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`

## v268 핵심 결론

관리자 페이지와 게임 화면은 아직 Vue가 아닙니다.

현재 구조는 다음 legacy 경로에 강하게 묶여 있습니다.

- `admin.html`
- `index.html`
- `src/`
- `backend/app/api/routes/`
- `backend/app/services/`
- `tools/run_smoke_core.sh`

따라서 v268에서는 실제 파일 대이동을 하지 않았습니다. 대신 현재 구조와 Vue/FastAPI/DB 전환 계획을 문서로 정리했습니다.

## 관리자 페이지 상태

현재 `admin.html` 기반 관리자 페이지는 임시 운영/검증 도구로 충분히 안정화했습니다.

가능한 작업:

- 마스터 데이터 카탈로그 조회
- 상세 확인
- 신규 row 생성 Preview
- 편집 Preview
- ChangeLog 조회
- Rollback Preview
- 생성 row 삭제 Preview
- 삭제 row 복원 Preview
- Preview fixture 점검
- Live Preview API 응답 표시 점검
- 공통 Diff/Snapshot/Preview Summary 표시

## v266 UX 상태 유지

- Admin Workspace와 초보자 안내 유지
- 카탈로그 보기 방식 3분할 제거 상태 유지
- 긴 값은 짧은 미리보기 + 모달 전체 보기 유지
- 버튼 위험도는 텍스트 chip 없이 색상/tooltip 중심 유지
- 상세 화면 바로가기 버튼은 실제 섹션 펼침/스크롤 이동 유지

## v268 문서 갱신 상태

갱신/추가된 핵심 문서:

- `docs/current/PROJECT_STRUCTURE.md`
- `docs/PROJECT_STRUCTURE.md`
- `docs/current/VUE_FASTAPI_DB_TRANSITION_PLAN.md`
- `docs/NEXT_STEPS.md`
- `docs/current/ROADMAP.md`
- `docs/current/CURRENT_STATUS.md`
- `README.md`
- `NEXT_CHAT_HANDOFF.md`
- `NEXT_CHAT_PROMPT.md`

## 현재 방향

당분간 게임 콘텐츠 개발은 하지 않습니다.

보류:

- 장비 추가
- 스킬 추가
- 보스 추가
- 필드 추가
- 드랍률/밸런스 조정
- 강화 수치 조정
- 신규 콘텐츠 기획 반영

우선:

1. legacy 경로 의존성 자동 목록화
2. Vue 앱 생성 위치 결정
3. FastAPI 구조 정리 계획 구체화
4. PostgreSQL/Alembic 도입 준비
5. 인증 설계 준비
6. 관리자 페이지 Vue 이식 계획
7. 게임 화면 Vue 이식 계획
8. 배포 직전 안정화 계획

## 안전 원칙

다음은 사용자 승인 없이 변경하지 않습니다.

- DB 구조
- env
- seed
- 인증
- 기존 route path
- API 응답 body
- Write Guard
- 실제 write 로직
- 관리자 Preview/Apply 요청 body
- 기존 Smoke/Contract 의미

## v268 검증 메모

문서 중심 작업이므로 런타임 동작은 변경하지 않았습니다.

검증 기준:

- `python -m compileall -q backend/app backend/scripts tools`
- JS 문법 검사
- `bash tools/run_smoke_core.sh`
- ZIP 무결성 검사
