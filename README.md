# RPG v075 - 백엔드 기초 설계 / FastAPI 뼈대 + PostgreSQL 초안

이 ZIP은 **Vue 프론트엔드 + FastAPI 백엔드 + PostgreSQL + 관리자 페이지**로 넘어가기 전, 현재 HTML/JavaScript 게임을 안전하게 분리하기 위한 준비본입니다.

이번 버전의 핵심은 **관리자 페이지 요구사항 V1 고정 + PostgreSQL DB 설계 초안 + FastAPI 프로젝트 뼈대 생성**입니다. 기존 프론트 게임 동작은 건드리지 않고, 앞으로 서버/DB/관리자 페이지를 만들 기준을 추가했습니다.

## 현재 완료된 작업

```txt
1순위 상태 분리 완료
2순위 bosses.js 역할 분리 1차 완료
3순위 캐릭터별 스킬 구조 준비 1차 완료
4순위 1차 공격/강화 결과 객체화 완료
4순위 2차 처치/드랍/보상 결과 객체화 완료
4순위 3차 장착/해제/스킬강화권/보스소환 결과 객체화 완료
5순위 API 응답 형태 확정 완료
관리자 페이지 요구사항 V1 문서화 완료
PostgreSQL DB 설계 초안 추가 완료
FastAPI backend/ 뼈대 추가 완료
```

## 이번 버전의 핵심 변경

### FastAPI 백엔드 뼈대 추가

새 폴더:

```txt
backend/
```

포함 내용:

```txt
FastAPI 앱 기본 구조
PostgreSQL SQLAlchemy 모델 초안
Alembic 마이그레이션 폴더
공통 API 응답 헬퍼
관리자/게임 라우터 stub
.env.example
pyproject.toml
```

### 관리자 페이지 요구사항 V1 고정

새 문서:

```txt
docs/ADMIN_REQUIREMENTS_V1.md
```

관리자에서 수정해야 하는 항목을 DB/FastAPI 설계 기준으로 고정했습니다.

### PostgreSQL DB 설계 초안 추가

새 문서/SQL:

```txt
docs/DB_SCHEMA_DRAFT.md
backend/sql/schema_draft.sql
```

### 스킬 데이터 중앙화

새 파일:

```txt
src/data/skills.js
```

이 파일에 아래 정보를 모았습니다.

```txt
캐릭터 마스터 데이터
스킬 마스터 데이터
스킬강화권 마스터 데이터
```

### 캐릭터 추가 준비

현재 기본 캐릭터:

```txt
weapon_master
```

유저 스킬 상태는 앞으로 아래 구조를 기준으로 봅니다.

```txt
player.userCharacters[player.currentCharacterId].skills
```

기존 코드 호환을 위해 아래도 계속 유지합니다.

```txt
player.skills
```

## 먼저 읽을 문서 순서

1. `README.md`
2. `docs/BACKEND_SPLIT_STAGE2_PLAN.md`
3. `docs/BACKEND_SPLIT_CHECKLIST.md`
4. `docs/SKILL_STRUCTURE_READY.md`
5. `docs/CSS_AUDIT.md`
6. `docs/CODE_MAP.md`
7. `docs/ADMIN_REQUIREMENTS_V1.md`
8. `docs/DB_SCHEMA_DRAFT.md`
9. `docs/BACKEND_ARCHITECTURE.md`
10. `docs/BACKEND_API_ROUTES_DRAFT.md`
11. `docs/ADMIN_PAGE_REQUIREMENTS.md`
12. `docs/DECISION_LOG.md`
13. `docs/API_RESPONSE_CONTRACT.md`
14. `docs/CHANGELOG.md`

## 실행 방법

현재 버전은 아직 Vue 프로젝트가 아니라 일반 HTML/JS 구조입니다.

```txt
index.html을 브라우저에서 열면 됩니다.
```

로컬 서버로 여는 것을 추천합니다.

```bash
python -m http.server 5500
```

브라우저 접속:

```txt
http://localhost:5500
```

## 현재 구조

```txt
index.html
src/
  api/
    API_PLAN.md
    api-response-contract.js
  app/
    main.js
  data/
    skills.js
    bosses.js
    boss-factories.js
    boss-bootstrap.js
    zones.js
  rules/
    abyss-fragment-rules.js
    boss-display-rules.js
    boss-drop-rules.js
  state/
    game-state.js
    STATE_SPLIT_READY.md
  styles/
    style.css
  systems/
    combat-system.js
    item-system.js
    stat-system.js
  ui/
    render-ui.js
  utils/
    icon-utils.js

docs/
  BACKEND_SPLIT_STAGE2_PLAN.md
  BACKEND_SPLIT_CHECKLIST.md
  SKILL_STRUCTURE_READY.md
  CSS_AUDIT.md
  CODE_MAP.md
  ADMIN_PAGE_REQUIREMENTS.md
  DECISION_LOG.md
  CHANGELOG.md
```

## 개발 방향

최종 목표는 아래 구조입니다.

```txt
Vue 프론트엔드
+ FastAPI 백엔드
+ PostgreSQL DB
+ 관리자 페이지
```

단, 지금 바로 Vue로 갈아엎는 것보다 아래 순서가 안전합니다.

```txt
1. 현재 JS 구조 정리
2. 백엔드로 보낼 상태/계산/데이터 분리
3. PostgreSQL에 넣을 마스터 데이터 추출
4. FastAPI 저장/불러오기 API 제작
5. 전투/드랍/강화 판정을 서버로 이동
6. 관리자 페이지 제작
7. 마지막에 Vue 화면 전환
```

## 이번 버전에서 추가된 핵심 문서/폴더

```txt
backend/
docs/ADMIN_REQUIREMENTS_V1.md
docs/DB_SCHEMA_DRAFT.md
docs/BACKEND_ARCHITECTURE.md
docs/BACKEND_API_ROUTES_DRAFT.md
backend/sql/schema_draft.sql
```

## 브라우저 확인 여부

이번 v075는 `backend/` 폴더와 설계 문서를 추가한 작업입니다. 기존 `index.html`과 프론트 JS 실행 흐름은 변경하지 않았습니다.

따라서 브라우저에서 따로 확인할 항목은 없습니다.

## 다음 추천 작업

이제 서버/DB 뼈대가 생겼으므로 다음 단계는 아래 중 하나입니다.

```txt
1. 현재 JS 마스터 데이터 추출 도구 작성
2. bosses/zones/skills 데이터를 JSON seed로 변환
3. Alembic 첫 마이그레이션 작성
4. /game/master-data API 실제 구현
```

내 추천은 다음 단계에서 **현재 JS 마스터 데이터 추출 도구 작성 + seed JSON 생성**으로 넘어가는 것입니다.
