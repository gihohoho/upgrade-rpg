# 현재 상태 — v269 legacy path dependency report

## 안정 기준

- 최신 인계 ZIP: `rpg_v269_legacy_path_dependency_report.zip`
- 이번 작업 기준: `v269.legacy-path-dependency-report`
- 직전 기능 기준: `v266.admin-practical-ux-polish`
- 직전 구조 기준: `v268.project-structure-transition-prep`
- 관리자 readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`

## v269 핵심 결론

v269에서는 실제 파일 이동이나 Vue 앱 생성을 하지 않았습니다.

대신 다음을 확정했습니다.

- legacy 경로 의존성을 자동 목록화하는 도구를 추가했습니다.
- 생성 보고서 `docs/current/LEGACY_PATH_DEPENDENCIES.md`를 추가했습니다.
- 새 Vue 앱 생성 위치는 `frontend/vue-app/`가 가장 안전하다고 결정했습니다.
- 현재 `src/`는 Vue 앱 소스가 아니라 legacy 브라우저 JS/CSS이므로 Vue 앱용으로 재사용하지 않습니다.
- `admin.html`, `index.html`, 기존 `src/`는 Vue 이식 전까지 그대로 유지합니다.

## v269 추가 파일

- `tools/report_legacy_path_dependencies.py`
- `docs/current/LEGACY_PATH_DEPENDENCIES.md`

## 현재 유지되는 legacy 기준

아래 경로는 smoke/contract와 HTML 직접 로드 관계가 강하므로 아직 이동하지 않습니다.

- `admin.html`
- `index.html`
- `src/`
- `src/api/`
- `src/api/admin/`
- `backend/app/api/routes/`
- `backend/app/services/`
- `backend/seeds/`
- `tools/run_smoke_core.sh`
- `tools/smoke/`

## Vue 앱 위치 결정

결정:

```txt
frontend/vue-app/
```

이유:

- 기존 root `src/`는 현재 게임/관리자 legacy JS가 들어 있는 폴더입니다.
- Vite/Vue 기본 `src/`와 충돌하면 기존 smoke와 HTML 직접 로드 경로가 깨질 수 있습니다.
- `frontend/vue-app/`는 기존 legacy와 분리되어 있어서 Vue shell을 만들어도 기존 게임/관리자 화면을 그대로 검증할 수 있습니다.

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

## 당분간 보류

게임 콘텐츠 개발은 하지 않습니다.

보류:

- 장비 추가
- 스킬 추가
- 보스 추가
- 필드 추가
- 드랍률/밸런스 조정
- 강화 수치 조정
- 신규 콘텐츠 기획 반영

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

## v269 검증 메모

문서/도구 중심 작업이므로 런타임 동작은 변경하지 않았습니다.

검증 기준:

- `python tools/report_legacy_path_dependencies.py --check`
- JS 문법 검사
- `python -m compileall -q backend/app backend/scripts tools`
- `bash tools/run_smoke_core.sh`
- ZIP 무결성 검사
