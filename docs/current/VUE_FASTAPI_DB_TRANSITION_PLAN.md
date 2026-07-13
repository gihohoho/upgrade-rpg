# Vue/FastAPI/DB 전환 준비 계획 — v268

## 목적

지금까지 만든 HTML/JS 기반 게임과 관리자 도구를 바로 갈아엎지 않고, 검증된 기능과 계약을 보존한 상태에서 Vue + FastAPI + PostgreSQL 구조로 옮길 준비를 합니다.

v268의 핵심 결론은 다음입니다.

- 실제 파일 대이동은 아직 하지 않습니다.
- `admin.html`, `index.html`, `src/`, `backend/`, `tools/` 경로 의존성이 매우 큽니다.
- 먼저 현재 구조/역할/경로 의존성을 문서화했습니다.
- 다음 단계부터는 새 Vue 앱을 “기존 legacy 옆에” 만드는 방식이 가장 안전합니다.

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

## v268에서 확인한 이동 위험도

`tools/smoke`와 문서/코드가 아래 경로를 직접 읽거나 문자열로 확인합니다.

| 경로/문자열 | 참조 수 | 참조 파일 수 | 위험도 |
|---|---:|---:|---|
| `admin.html` | 166 | 84 | 매우 높음 |
| `index.html` | 82 | 48 | 높음 |
| `src/api` | 589 | 167 | 매우 높음 |
| `src/api/admin` | 352 | 128 | 매우 높음 |
| `backend/app/api/routes` | 350 | 73 | 매우 높음 |
| `backend/app/services` | 258 | 89 | 매우 높음 |
| `tools/run_smoke_core.sh` | 75 | 70 | 매우 높음 |

따라서 “폴더를 예쁘게 옮기는 작업”은 지금 하면 위험합니다. 먼저 새 구조를 옆에 만들고, 기존 구조는 그대로 두는 방식으로 가야 합니다.

## 권장 최종 구조 초안

아래는 목표 구조 초안입니다. v268에서는 아직 만들지 않았습니다.

```txt
.
├── legacy/
│   ├── index.html
│   ├── admin.html
│   └── src/
├── frontend/
│   └── vue-app/
│       ├── package.json
│       ├── vite.config.js
│       └── src/
│           ├── app/
│           ├── pages/
│           ├── components/
│           ├── api/
│           ├── stores/
│           ├── router/
│           └── styles/
├── backend/
│   └── app/
│       ├── api/
│       │   └── v1/
│       │       ├── admin/
│       │       ├── game/
│       │       └── auth/
│       ├── core/
│       ├── models/
│       ├── schemas/
│       ├── services/
│       ├── repositories/
│       └── contracts/
├── docs/
└── tools/
```

단, 실제 이동은 아래 순서가 끝난 뒤에만 진행합니다.

1. 기존 smoke가 직접 읽는 경로 전체 목록화
2. 새 위치에서 legacy 경로를 어떻게 유지할지 결정
3. 임시 alias/copy/symlink 중 안전한 방식 결정
4. core smoke 통과
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

v268에서 시작한 단계입니다.

완료/진행:

- 현재 파일/폴더 역할 정리
- Vue 이식/legacy 보존 대상 분류
- smoke 경로 의존성 1차 분석
- 실제 이동 보류 결정

다음 보완:

- `tools/smoke/**/*.js`, `tools/smoke/**/*.py`가 직접 읽는 경로를 자동 목록화하는 점검 스크립트 추가 검토
- 문서 archive 정책 확정

### Phase 2 — Vue 앱 초기 세팅 준비

권장 방식:

- 기존 root `admin.html`/`index.html`은 유지합니다.
- 새 Vue 앱은 `frontend/vue-app/`에 별도로 만듭니다.
- 처음에는 기존 화면을 대체하지 않고 “껍데기 shell”만 만듭니다.

초기 후보 구조:

```txt
frontend/vue-app/src/
├── app/
├── pages/
│   ├── AdminPage.vue
│   └── GamePage.vue
├── components/
├── api/
├── stores/
├── router/
└── styles/
```

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
- 인증 도입 전에는 인증 없는 API client부터 만듭니다.
- 인증 토큰/interceptor는 별도 단계에서 설계합니다.

### Phase 4 — 관리자 페이지 Vue 이식 계획

관리자 이식 우선순위:

1. 읽기 전용 overview/readiness
2. 마스터 데이터 카탈로그
3. 상세 조회
4. Preview 결과 공통 렌더러
5. Diff/Snapshot 공통 렌더러
6. 신규 row 생성 Preview
7. 기존 row 편집 Preview
8. ChangeLog/Rollback Preview
9. 실제 Apply/write 계열은 마지막

안전 원칙:

- Preview/Apply 요청 body는 기존과 동일해야 합니다.
- Write Guard는 유지해야 합니다.
- 실제 write 로직은 사용자가 명시 승인하기 전 변경하지 않습니다.

### Phase 5 — 게임 화면 Vue 이식 계획

게임 콘텐츠 개발은 보류합니다.

이식 순서 후보:

1. 게임 상태 표시 UI
2. 인벤토리/장비 UI
3. 전투 로그/결과 UI
4. 필드/보스 선택 UI
5. 강화/스킬 UI
6. save/load UI

주의:

- 장비/스킬/보스/필드/드랍/밸런스 수치 추가/변경 금지
- 먼저 legacy와 같은 결과를 내는지 확인합니다.

### Phase 6 — PostgreSQL/Alembic 준비

현재 존재:

- `docker-compose.yml`
- `backend/alembic/`
- `backend/alembic.ini`
- `backend/app/db/`
- `backend/seeds/generated/`
- `backend/sql/schema_draft.sql`

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
4. 문서 이동 후에는 `tools/smoke/game/smoke_docs_index_archive.js`를 반드시 확인합니다.
5. 문서 이동은 한 번에 많이 하지 말고 묶음별로 진행합니다.

## 다음 작업 권장

다음 단계는 `v269 legacy 경로 의존성 자동 목록화 + Vue 앱 생성 위치 결정`입니다.

v269에서 할 일:

1. smoke가 직접 읽는 파일 경로 목록을 자동 추출합니다.
2. `frontend/vue-app/` 생성 여부를 결정합니다.
3. Vue 앱을 만들더라도 legacy 동작은 건드리지 않습니다.
4. 새 Vue 앱 생성 후에는 기존 core smoke와 별도 Vue 기본 검증을 나눠 실행합니다.
