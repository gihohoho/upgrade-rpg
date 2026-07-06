# RPG v085 - 프론트 master-data API 브릿지 추가

## v086 요약

- `backend/scripts/check_master_data_parity.py` 추가
- JS seed JSON과 FastAPI `/api/v1/game/master-data` 응답의 데이터 동등성 검증
- 기본 경량 응답과 `--include-assets` 이미지 포함 응답 모두 확인 가능
- 게임 동작은 변경하지 않음


이번 버전은 기존 HTML/JS 게임 동작을 유지하면서, 브라우저에서 FastAPI `/api/v1/game/master-data`를 읽어올 수 있는 프론트 연결 준비층을 추가한 버전입니다.

```txt
기존 게임 동작: 정적 JS 데이터 그대로 유지
추가된 기능: 브라우저 콘솔에서 백엔드 master-data API 연결 확인
다음 단계: API 데이터와 기존 JS 데이터 비교/전환 어댑터 작성
```

확인 명령어:

위치: 프로젝트 루트

```bash
node tools/smoke_frontend_master_data_bridge.js
```

브라우저 콘솔 확인:

```js
await checkBackendMasterData();
```


## v089 요약

- `src/api/master-data-runtime-switch.js` 추가
- 기본값 OFF인 백엔드 master-data 런타임 모드 추가
- 브라우저 콘솔에서 `enableBackendMasterDataMode()` / `disableBackendMasterDataMode()`로 전환 가능
- ON 상태에서는 페이지 시작 전에 FastAPI master-data를 불러와 기존 전역 데이터 내부를 교체
- API 로딩 실패 시 기존 정적 JS 데이터로 fallback

확인 명령어:

위치: 프로젝트 루트

```bash
node tools/smoke_master_data_runtime_switch.js
```

브라우저 콘솔:

```js
enableBackendMasterDataMode();
await checkBackendMasterDataRuntimeMode();
disableBackendMasterDataMode();
```

---

# RPG v077 - 백엔드 환경 보정 / JS seed 추출 도구 추가

이 ZIP은 **Vue 프론트엔드 + FastAPI 백엔드 + PostgreSQL + 관리자 페이지**로 넘어가기 전, 현재 HTML/JavaScript 게임을 안전하게 분리하기 위한 준비본입니다.

이번 버전의 핵심은 **FastAPI 로컬환경 오류 보정 + JS 마스터 데이터 seed 추출 도구 추가**입니다. 기존 프론트 게임 동작은 건드리지 않았고, 백엔드/PostgreSQL 이전을 위한 데이터 추출 준비를 보강했습니다.

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
Docker PostgreSQL 로컬 개발환경 세팅 추가 완료
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



### v077 추가 사항

```txt
CORS_ORIGINS 파싱 안정화
asyncpg 의존성 명시
JS 마스터 데이터 seed 추출 도구 추가
seed smoke 테스트 추가
실제 로컬 실행 중 발생한 오류 해결법 문서화
```

seed 추출 명령어:

```bash
node tools/extract_seed_data.js
node tools/smoke_seed_extraction.js
```

생성 위치:

```txt
backend/seeds/generated/
```

### 로컬 개발환경 세팅 추가

새 파일:

```txt
docker-compose.yml
.gitignore
.dockerignore
docs/LOCAL_DEV_SETUP.md
docs/DOCKER_POSTGRES_GUIDE.md
docs/GIT_WORKFLOW.md
tools/check_backend_ready.py
```

Docker로 PostgreSQL과 Adminer를 실행할 수 있게 준비했습니다.

```bash
docker compose up -d
```

FastAPI DB 연결 확인 주소도 추가했습니다.

```txt
http://localhost:8000/api/v1/health/db
```

## 먼저 읽을 문서 순서

1. `README.md`
2. `docs/LOCAL_DEV_SETUP.md`
3. `docs/DOCKER_POSTGRES_GUIDE.md`
4. `docs/GIT_WORKFLOW.md`
5. `docs/BACKEND_SPLIT_STAGE2_PLAN.md`
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
14. `docs/SEED_EXTRACTION.md`
15. `docs/CHANGELOG.md`

## 프론트 실행 방법

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


## 백엔드 로컬 실행 방법

처음 1회 준비:

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate
pip install -e .[dev]
cp .env.example .env
cd ..
docker compose up -d
```

FastAPI 실행:

```bash
cd backend
source .venv/Scripts/activate
uvicorn app.main:app --reload
```

확인 주소:

```txt
http://localhost:8000/docs
http://localhost:8000/api/v1/health
http://localhost:8000/api/v1/health/db
http://localhost:8081
```

개발환경 점검:

```bash
python tools/check_backend_ready.py
python tools/check_backend_ready.py --db
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

이번 v076은 `docker-compose.yml`, 로컬 개발환경 문서, 점검 도구를 추가한 작업입니다. 기존 `index.html`과 프론트 JS 실행 흐름은 변경하지 않았습니다.

따라서 브라우저에서 따로 확인할 항목은 없습니다.

## v078 업데이트 - Seed Import 구조 추가

이번 버전은 `backend/seeds/generated/*.json` 파일을 PostgreSQL 로컬 DB에 넣기 위한 개발용 import 구조를 추가했습니다.

터미널 위치 기준:

- 프로젝트 루트: `node tools/extract_seed_data.js`, `python tools/smoke_seed_import_structure.py`
- backend 폴더: `python scripts/setup_dev_db.py --reset --seed --verify`

자세한 내용은 `docs/SEED_IMPORT.md`를 확인하세요.


## 다음 추천 작업

이제 로컬 PostgreSQL/FastAPI 실행 준비가 되었으므로 다음 단계는 아래 중 하나입니다.

```txt
1. 현재 JS 마스터 데이터 추출 도구 작성
2. bosses/zones/skills 데이터를 JSON seed로 변환
3. Alembic 첫 마이그레이션 작성
4. /game/master-data API 실제 구현
```

내 추천은 다음 단계에서 **현재 JS 마스터 데이터 추출 도구 작성 + seed JSON 생성**으로 넘어가는 것입니다.


## v079 seed import connection fix

- `backend/scripts/setup_dev_db.py`를 sync SQLAlchemy + `psycopg` 방식으로 변경했습니다.
- Windows/Docker 환경에서 `asyncpg.exceptions.ConnectionDoesNotExistError`가 seed import 중 발생하는 문제를 피하기 위한 수정입니다.
- `backend/pyproject.toml`에 `psycopg[binary]` 의존성을 추가했습니다.


> 로컬 PostgreSQL은 기본 포트 `5432`가 아니라 `55432`를 사용한다. Windows에서 기존 PostgreSQL과 충돌을 피하기 위한 프로젝트 기준이다. 자세한 내용은 `docs/LOCAL_DB_PORT_POLICY.md`를 참고한다.

## v081 - Master Data API

`/api/v1/game/master-data`가 이제 임시 `stub`이 아니라 PostgreSQL seed 데이터를 읽어 반환합니다.

확인 순서:

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
python scripts/setup_dev_db.py --reset --seed --verify
uvicorn app.main:app --reload
```

다른 터미널에서:

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
python scripts/check_master_data_api.py
```

자세한 내용은 `docs/MASTER_DATA_API.md`를 확인하세요.

## v083 - Master Data Asset Cleanup

`/api/v1/game/master-data` 기본 응답에서 긴 SVG/data URL 이미지 문자열을 제외했습니다.

브라우저 확인:

```txt
http://127.0.0.1:8000/api/v1/game/master-data
```

이미지 문자열까지 포함해서 확인해야 할 때:

```txt
http://127.0.0.1:8000/api/v1/game/master-data?includeAssets=true
```

터미널 확인:

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
python scripts/check_master_data_api.py
python scripts/check_master_data_api.py --include-assets
```

자세한 내용은 `docs/MASTER_DATA_ASSET_POLICY.md`를 확인하세요.

## v084 note

- `/api/v1/game/master-data` 기본 응답에서 최상위 asset 필드뿐 아니라 `options`, `conditions`, `rules`, `raw` 같은 중첩 JSON 안의 `data:image...` 문자열도 제거합니다.
- asset 문자열이 필요한 경우에는 `?includeAssets=true`를 사용합니다.



### v087 note

`lightsabre`처럼 기본 발동확률이 없는 스킬은 `procRate: null`로 유지합니다. `python scripts/setup_dev_db.py --reset --seed --verify`를 다시 실행해야 DB에 반영됩니다.


## v088 프론트 master-data 어댑터

`src/api/master-data-adapter.js`가 추가되었습니다. 아직 실제 게임 데이터는 기존 JS를 그대로 사용하지만, FastAPI `/api/v1/game/master-data` 응답을 기존 게임 데이터 구조에 가까운 형태로 변환해 검증할 수 있습니다.

위치: 프로젝트 루트

```bash
node tools/smoke_master_data_adapter.js
```

FastAPI 서버가 켜져 있을 때 브라우저 Console에서 다음을 실행할 수 있습니다.

```js
await checkBackendMasterDataAdapter();
```
