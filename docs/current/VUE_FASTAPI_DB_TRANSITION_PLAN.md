# Vue/FastAPI/DB 전환 준비 계획 — v269

## 목적

지금까지 만든 HTML/JS 기반 게임과 관리자 도구를 바로 갈아엎지 않고, 검증된 기능과 계약을 보존한 상태에서 Vue + FastAPI + PostgreSQL 구조로 옮길 준비를 합니다.

v269의 핵심 결론은 다음입니다.

- 실제 파일 대이동은 아직 하지 않습니다.
- `admin.html`, `index.html`, `src/`, `backend/`, `tools/` 경로 의존성이 큽니다.
- legacy 경로 의존성을 자동 목록화하는 도구를 추가했습니다.
- 새 Vue 앱 위치는 `frontend/vue-app/`로 결정했습니다.
- 다음 단계에서 사용자 승인 후 Vue 기본 shell만 생성하는 것이 안전합니다.

## 절대 원칙

1. 먼저 분석하고 문서화합니다.
2. 실제 파일 이동은 smoke 영향 범위를 확인한 뒤 진행합니다.
3. 기존 route path와 API response body는 유지합니다.
4. 기존 관리자 Preview/Apply 안전장치는 유지합니다.
5. Write Guard와 실제 write 로직은 사용자 승인 없이 변경하지 않습니다.
6. DB/env/seed/인증은 사용자 승인 없이 변경하지 않습니다.
7. 게임 콘텐츠 신규 개발은 전환 구조가 안정화된 뒤 진행합니다.

## 현재 legacy 기준

아래 파일/폴더는 Vue 전환 전까지 기준 동작과 검증 대상으로 유지합니다.

| 대상 | 현재 역할 | 당장 처리 |
|---|---|---|
| `index.html` | 실제 게임 화면 | 이동/삭제 금지 |
| `admin.html` | 관리자 운영/검증 화면 | 이동/삭제 금지 |
| `src/api/admin/*.js` | 관리자 기능별 브라우저 helper | 이동 금지, Vue 이식 후보로 분석 |
| `src/api/admin-page-readonly.js` | 관리자 메인 glue/helper | 이동 금지, Vue 분해 계획 필요 |
| `src/api/game-api-client.js` | API client | Vue API client 설계 참고 |
| `src/data/` | 현재 게임 데이터 | DB seed 기준 자료로 보존 |
| `src/rules/` | 게임 규칙 | 콘텐츠 개발 보류, 나중에 domain module로 보존/이식 |
| `src/state/` | legacy 게임 상태 | Vue store 후보 |
| `src/systems/` | 전투/아이템/스탯 시스템 | Vue와 독립적인 domain module 후보 |
| `src/ui/` | legacy DOM 렌더링 | Vue component로 대체 후보 |
| `src/styles/` | legacy CSS | 점진 분해 후보 |

## v269 자동 분석 도구

추가한 도구:

```txt
tools/report_legacy_path_dependencies.py
```

생성 문서:

```txt
docs/current/LEGACY_PATH_DEPENDENCIES.md
```

실행 위치: 프로젝트 루트

```bash
python tools/report_legacy_path_dependencies.py --write
```

검사만 할 때:

실행 위치: 프로젝트 루트

```bash
python tools/report_legacy_path_dependencies.py --check
```

이 도구는 새 contract가 아닙니다. 구조 전환 전에 “어떤 경로를 움직이면 위험한지” 확인하기 위한 보조 도구입니다.

## Vue 앱 위치 결정

결정:

```txt
frontend/vue-app/
```

### 선택 이유

- 기존 `src/`는 Vue 소스가 아니라 legacy 브라우저 JS/CSS입니다.
- `admin.html`과 `index.html`이 `src/...` 파일을 직접 로드합니다.
- Vue/Vite 기본 구조도 `src/`를 쓰기 때문에 root `src/`를 재사용하면 혼란과 smoke 실패 가능성이 큽니다.
- `frontend/vue-app/`는 기존 legacy를 건드리지 않고 Vue shell을 만들 수 있습니다.

### v270에서 만들 구조 초안

```txt
frontend/vue-app/
├── package.json
├── vite.config.js
├── index.html
└── src/
    ├── app/
    ├── pages/
    │   ├── AdminShell.vue
    │   └── GameShell.vue
    ├── components/
    ├── api/
    ├── stores/
    ├── router/
    └── styles/
```

## 권장 최종 구조 초안

아래는 목표 구조 초안입니다. v269에서는 아직 만들지 않았습니다.

```txt
.
├── legacy/
│   ├── index.html
│   ├── admin.html
│   └── src/
├── frontend/
│   └── vue-app/
├── backend/
├── docs/
└── tools/
```

단, `legacy/`로 실제 이동하는 작업은 아직 하지 않습니다.

먼저 다음이 필요합니다.

1. Vue shell 생성
2. legacy smoke 유지 확인
3. Vue 기본 검증 추가
4. alias/copy/symlink 전략 검토
5. 사용자 승인

## 단계별 전환 로드맵

### Phase 0 — 현재 legacy 고정

목표:

- 현재 동작을 안정 기준으로 고정합니다.
- 관리자 HTML 페이지와 게임 HTML 페이지를 계속 사용할 수 있게 둡니다.

유지:

- `admin.html`
- `index.html`
- `src/`
- `backend/app/api/routes/` 기존 route path
- `backend/app/services/` 기존 의미
- `tools/run_smoke_core.sh`

### Phase 1 — 구조/경로 의존성 문서화

v268에서 시작했고 v269에서 자동화했습니다.

완료:

- 현재 파일/폴더 역할 정리
- Vue 이식/legacy 보존 대상 분류
- smoke 경로 의존성 분석
- 자동 보고서 생성 도구 추가
- 실제 이동 보류 결정

### Phase 2 — Vue 앱 초기 세팅 준비

다음 v270 후보입니다.

권장 방식:

- 기존 root `admin.html`/`index.html`은 유지합니다.
- 새 Vue 앱은 `frontend/vue-app/`에 별도로 만듭니다.
- 처음에는 기존 화면을 대체하지 않고 “껍데기 shell”만 만듭니다.

주의:

- 기존 route path/API 응답 body 변경 금지
- 기존 admin preview/apply 요청 body 변경 금지
- 기존 smoke 의미 변경 금지

### Phase 3 — Vue API client/interceptor 설계

참고 대상:

- `src/api/game-api-client.js`
- `src/api/master-data-*.js`
- `src/api/save-data-*.js`
- `src/api/admin/*.js`

계획:

- Vue용 API client를 새로 만들되, 기존 API route와 response body를 그대로 사용합니다.
- 인증 도입 전에는 인증 없는 API client shell만 준비합니다.
- 인증/토큰/interceptor는 별도 승인 후 진행합니다.

### Phase 4 — 관리자 페이지 Vue 이식 계획

순서:

1. AdminShell 생성
2. 읽기 전용 catalog/detail만 shell에 배치
3. 기존 `admin.html` 유지
4. Preview 기능 이식 전 요청 body/response body 계약 재검증
5. Apply/write 관련 기능은 가장 마지막에 이식

### Phase 5 — 게임 화면 Vue 이식 계획

순서:

1. GameShell 생성
2. HUD/layout부터 component화
3. 기존 state/rules/systems는 domain module로 먼저 보존
4. DOM 직접 조작을 Vue component로 대체
5. 저장/로드/슬롯 검증 후 전환

### Phase 6 — PostgreSQL/Alembic 준비

현재 DB 도입 준비 파일은 있으나 실제 DB 구조 변경은 하지 않습니다.

도입 원칙:

- migration은 DB 구조 변경용입니다.
- seed는 초기/테스트 데이터용입니다.
- 운영 데이터 변경은 관리자 Preview/Apply 흐름으로 처리합니다.
- rollback snapshot 정책은 DB 변경 전에 별도 검토합니다.

아직 하지 않을 것:

- 실제 DB schema 변경
- seed 변경
- 운영 데이터 변경
- rollback snapshot 정책 변경

### Phase 7 — 인증 설계 준비

인증은 고위험 항목입니다.

준비 순서:

1. 사용자 유형 정의
2. 관리자 권한 정의
3. 로그인/토큰 저장 방식 결정
4. FastAPI dependency 설계
5. Vue route guard 설계
6. 기존 Write Guard와의 관계 정리
7. smoke/contract 설계
8. 실제 구현

아직 하지 않을 것:

- 인증 코드 추가
- 기존 API에 인증 강제
- 기존 write guard 변경

### Phase 8 — 배포 직전 안정화 계획

배포 전 체크 후보:

- 환경 변수 문서화
- 로컬/운영 DB 분리
- migration 실행 절차
- seed 실행 절차
- 관리자 write 권한 보호
- error response contract
- CORS 정책
- 정적 파일/SPA fallback 정책
- 백업/복구 정책
- smoke/contract CI화

## 문서 정리 계획

현재 `docs/` 루트에는 단계별 문서가 많이 남아 있습니다. 하지만 일부 smoke가 `docs/archive`와 handoff 문서를 확인하고 있으므로 즉시 대량 이동하지 않습니다.

권장 정리 방식:

1. `docs/current/`를 현재 기준 canonical 문서로 사용합니다.
2. `docs/handoff/`는 다음 채팅용 복사본으로 유지합니다.
3. 오래된 단계 문서는 `docs/archive/stage-notes/`로 이동하되, 먼저 smoke 영향 확인을 합니다.
4. 문서 이동 후에는 관련 smoke를 반드시 확인합니다.
5. 문서 이동은 한 번에 많이 하지 말고 묶음별로 진행합니다.

## 다음 작업 권장

다음 단계는 `v270 Vue 앱 기본 shell 생성`입니다.

v270에서 할 일:

1. 사용자 승인 후 `frontend/vue-app/` 생성
2. Vue/Vite 기본 실행 확인
3. legacy smoke와 Vue smoke 분리
4. 기존 `admin.html`/`index.html`/`src/` 유지
5. DB/env/seed/auth/API/write 로직 변경 없음
