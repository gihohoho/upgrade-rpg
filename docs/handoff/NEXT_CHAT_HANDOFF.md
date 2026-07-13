# NEXT CHAT HANDOFF — Upgrade RPG v269

## 현재 최신 ZIP

- `rpg_v269_legacy_path_dependency_report.zip`

반드시 이 ZIP을 기준으로 작업합니다.

## 사용자/응답 방식

- 사용자는 코딩을 거의 모릅니다.
- 설명은 항상 한국어로 쉽고 자세하게 합니다.
- 터미널 명령을 줄 때는 반드시 실행 위치를 먼저 적습니다.
- git 명령은 아래처럼 한 줄 블록으로 줍니다.

```bash
git status && git add . && git commit -m "..." && git push
```

## 현재 기준

- 현재 작업 기준: `v269.legacy-path-dependency-report`
- 직전 기능 기준: `v266.admin-practical-ux-polish`
- 직전 구조 기준: `v268.project-structure-transition-prep`
- readiness version: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`

## v269 완료 내용

- legacy 경로 의존성 자동 목록화 도구 추가
- `docs/current/LEGACY_PATH_DEPENDENCIES.md` 생성
- Vue 앱 생성 위치를 `frontend/vue-app/`로 결정
- 기존 `admin.html`, `index.html`, `src/` 이동하지 않기로 확정
- 실제 Vue 앱 생성은 아직 하지 않음
- DB/env/seed/auth/API body/route/write guard/실제 write 로직 변경 없음

## 새로 추가된 주요 파일

- `tools/report_legacy_path_dependencies.py`
- `docs/current/LEGACY_PATH_DEPENDENCIES.md`

## 현재 핵심 결론

현재 root `src/`는 Vue 앱 소스 폴더가 아닙니다. `admin.html`과 `index.html`이 직접 로드하는 legacy JS/CSS 폴더입니다.

따라서 Vue 앱은 root `src/`를 재사용하지 않고 아래 경로에 새로 만듭니다.

```txt
frontend/vue-app/
```

## 절대 변경 금지 / 고위험 항목

아래는 사용자 명시 승인 없이는 변경하지 않습니다.

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

## 다음 추천 작업

다음 작업은 `v270 Vue 앱 기본 shell 생성`입니다.

권장 목표:

- `frontend/vue-app/`에 Vite + Vue 기본 프로젝트 생성
- 기존 `admin.html`, `index.html`, `src/`는 그대로 유지
- Vue에는 실제 관리자/게임 로직을 아직 연결하지 않음
- `AdminShell.vue`, `GameShell.vue` 같은 빈 shell과 router만 준비
- Vue 실행/빌드 검증과 기존 legacy smoke를 분리
- DB/env/seed/auth/API/write 로직 변경 없음

## 검증 기준

코드나 구조를 건드렸다면 최소 다음을 확인합니다.

실행 위치: 프로젝트 루트

```bash
python tools/report_legacy_path_dependencies.py --check
```

실행 위치: 프로젝트 루트

```bash
python -m compileall -q backend/app backend/scripts tools
```

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
```

Vue 앱을 만든 뒤에는 별도 위치에서 Vue 검증도 실행합니다.

실행 위치: `frontend/vue-app` 폴더

```bash
npm run build
```
