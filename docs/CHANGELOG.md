# 변경 기록


## v098 - Master-data dev badge toggle alignment

- `hide/show` 토글 버튼 문구를 `hide MD` / `show MD`로 명확하게 바꿨습니다.
- 토글 버튼을 MASTER DATA 배지 상단 정가운데 탭처럼 배치했습니다.
- 배지를 숨겨도 같은 위치에 `show MD` 탭이 남아, Console 없이 화면에서 다시 펼칠 수 있습니다.
- 토글과 배지를 하나의 wrapper 안에서 함께 배치해 버튼이 위로 뜨거나 겹치는 현상을 줄였습니다.


## v095 - Backend master-data dev badge

- 브라우저 화면 하단에 master-data 상태 확인용 개발자 배지를 추가했다.
- 배지는 `file://`, `localhost`, `127.0.0.1` 환경에서 기본 표시된다.
- `applied`, `static_js_mode`, `failed_fallback_to_static_js` 같은 runtime state와 mode/assets/counts 요약을 표시한다.
- Console 헬퍼 `refreshBackendMasterDataDevBadge()`, `showBackendMasterDataDevBadge()`, `hideBackendMasterDataDevBadge()`, `toggleBackendMasterDataDevBadge()`를 추가했다.

## v087 - Preserve nullable skill proc rate

- Preserved missing skill `baseProcRate` values as database `NULL` instead of converting them to `0`.
- Updated `skills.proc_rate` to be nullable in SQLAlchemy and schema draft.
- Added documentation and a smoke test for nullable master-data fields.
- Intended to make `check_master_data_parity.py` pass for `lightsabre.procRate`.


## v086 - Master Data Parity Checker

- `backend/scripts/check_master_data_parity.py`를 추가했습니다.
- 현재 JS 마스터 데이터에서 생성된 `backend/seeds/generated/*.json`과 FastAPI `/api/v1/game/master-data` 응답을 비교할 수 있습니다.
- 기본 경량 응답과 `--include-assets` 이미지 포함 응답을 모두 검사할 수 있습니다.
- characters, skills, itemTemplates, bosses, fieldZones, dropTables, dropTableItems, enhancementRules의 개수와 주요 필드를 비교합니다.
- `tools/smoke_master_data_parity_checker.py`와 `docs/MASTER_DATA_PARITY_CHECKER.md`를 추가했습니다.

## v085 - Frontend Master Data Bridge

- `src/api/game-api-client.js`와 `src/api/master-data-bridge.js`를 추가했습니다.
- 기존 게임 동작은 유지하면서 브라우저 콘솔에서 FastAPI master-data API를 읽어올 수 있게 했습니다.
- `checkBackendMasterData()`, `loadBackendMasterData()`, `getCachedBackendMasterData()` 전역 함수를 추가했습니다.
- `tools/smoke_frontend_master_data_bridge.js`와 `docs/FRONTEND_MASTER_DATA_BRIDGE.md`를 추가했습니다.

## v084 - Master Data Nested Asset Cleanup

- 기본 master-data 응답에서 최상위 asset 필드뿐 아니라 중첩 JSON 내부의 긴 `data:image/...` 문자열도 제거하도록 정리했습니다.
- `?includeAssets=true` 요청에서는 기존처럼 asset 문자열을 포함합니다.
- `tools/smoke_master_data_nested_asset_cleanup.py`와 관련 문서를 추가했습니다.

## v082 - Seed Import Long Asset URL Fix

- `item_templates.icon_url`에 SVG `data:image` 문자열이 500자를 넘어 seed import가 실패하던 문제를 수정했습니다.
- `characters.image_url`, `skills.icon_url`, `item_templates.icon_url`, `bosses.image_url` 컬럼을 `Text` 타입으로 변경했습니다.
- `backend/sql/schema_draft.sql`의 이미지/아이콘 URL 컬럼도 `TEXT`로 맞췄습니다.
- `backend/scripts/setup_dev_db.py`의 SQL 로그 출력을 기본 비활성화했습니다. 긴 seed 데이터가 터미널을 가득 채우는 것을 막고, 필요할 때만 `--verbose-sql`로 볼 수 있습니다.
- `tools/smoke_seed_import_long_asset_columns.py`를 추가했습니다.

## v078 - Seed Import Structure

- `backend/scripts/setup_dev_db.py` 추가
  - 로컬 DB reset/schema 생성/seed import/verify 지원
  - `--dry-run`으로 DB 접속 없이 seed JSON 개수 확인 가능
- `docs/SEED_IMPORT.md` 추가
- `tools/smoke_seed_import_structure.py` 추가
- 매우 큰 HP/골드/강화비용을 고려해 DB 초안/모델의 관련 컬럼을 `NUMERIC(40,0)` 계열로 보정
- `user_mailbox_messages` 테이블을 SQL 초안에 보강


## v077 - Backend env fix + seed extractor

- `backend/app/core/config.py`를 수정해 `CORS_ORIGINS`를 JSON 리스트 형식과 쉼표 문자열 형식 모두 처리할 수 있게 했습니다.
- `backend/.env.example`의 `CORS_ORIGINS` 예시를 안전한 JSON 리스트 형식으로 수정했습니다.
- `backend/pyproject.toml` 버전을 `0.1.1`로 올리고 `asyncpg` 의존성을 명시했습니다.
- `tools/extract_seed_data.js`를 추가해 현재 JS 마스터 데이터를 `backend/seeds/generated/*.json`으로 추출할 수 있게 했습니다.
- `tools/smoke_seed_extraction.js`를 추가해 생성된 seed JSON 기본 검증을 할 수 있게 했습니다.
- `backend/seeds/README.md`, `docs/SEED_EXTRACTION.md`를 추가했습니다.
- Docker/FastAPI 로컬 실행 중 실제로 발생한 `CORS_ORIGINS` 파싱 오류와 `asyncpg` 누락 오류 해결법을 문서에 반영했습니다.
- 기존 프론트 게임 동작은 변경하지 않았습니다.

## v074 - 5순위: API 응답 형태 확정

- `docs/API_RESPONSE_CONTRACT.md`를 추가해 FastAPI 응답 표준 봉투를 확정했습니다.
- `src/api/api-response-contract.js`를 추가해 응답 버전, 행동 타입, 에러 코드, 응답 생성 헬퍼를 정리했습니다.
- `src/api/API_PLAN.md`를 확정 응답 형태 기준으로 갱신했습니다.
- 저장/불러오기, 마스터 데이터, 전투, 처치/드랍, 장착/해제/강화, 스킬강화권, 보스 소환, 관리자 변경 응답 예시를 정리했습니다.
- 실패 응답 형태와 공통 에러 코드를 정리했습니다.
- `tools/smoke_api_response_contract.js`를 추가해 응답 계약 헬퍼와 예시 응답을 자동 검증할 수 있게 했습니다.
- 현재 게임 동작에 영향을 주는 파일은 변경하지 않았습니다. 따라서 브라우저 확인 항목은 없습니다.

## v073 - 4순위 3차: 장착/해제/스킬강화권/보스소환 결과 객체화

- `actionEquipDirect()`에 `item.equip` / `skill_book.use` 결과 객체를 도입했습니다.
- `actionUnequipDirect()`에 `item.unequip` 결과 객체를 도입했습니다.
- `summonBoss()`에 `boss.summon` 결과 객체를 도입했습니다.
- `applyActionResultUi()`가 보스 패널 닫기, 특수보스 패널 닫기, 자동공격 시작 요청을 처리할 수 있게 확장했습니다.
- 장착/해제/스킬강화권/보스소환 성공·실패 사유를 `data.reason` 또는 상세 데이터로 남기도록 정리했습니다.
- 기존 UI 동작은 유지하면서 FastAPI 응답 구조로 옮기기 쉬운 중간 계층을 확장했습니다.
- `tools/smoke_action_results.js`를 추가해 주요 결과 객체 생성 여부를 자동 확인할 수 있게 했습니다.

## v072 - 4순위 2차: 처치/드랍/보상 결과 객체화

- `killEnemy()`에 `combat.kill` 결과 객체를 도입했습니다.
- 보스 처치 시 장비/탈리스만/휘장/스킬강화권 드랍 결과를 `data.drops`, `logs`, `effects`에 모으도록 정리했습니다.
- 최초 장비 보너스 스킬강화권 지급 로직이 선택적으로 Action Result에 기록되도록 개선했습니다.
- 필드 몬스터 처치 시 골드/공격속도/순수공격력 성장 보상을 `data.rewards`에 기록하도록 했습니다.
- `applyActionResultUi()`에 `renderUI` 요청 처리를 추가했습니다.
- 기존 게임 동작은 유지하고, FastAPI 응답 구조로 옮기기 위한 중간 계층만 추가했습니다.

# Changelog

## v071 - 4순위 1차: Action Result 도입

- `src/systems/action-result-system.js`를 추가했습니다.
- `index.html`에 `action-result-system.js` 로드를 추가했습니다.
- `combat-system.js`의 `playerAttack()`이 전투 결과 객체를 생성하도록 변경했습니다.
- 스킬 데미지 텍스트를 결과 객체의 `effects`에 담은 뒤 UI 반영 단계에서 표시하도록 변경했습니다.
- `item-system.js`의 `actionReinforce(times)`가 강화 결과 객체를 생성하고 반환하도록 변경했습니다.
- 강화 로그/결과창/UI 갱신 요청을 `applyActionResultUi()`를 통해 처리하도록 변경했습니다.
- `docs/UI_RESULT_SEPARATION_STAGE1.md`를 추가했습니다.

주의:

- 이번 작업은 4순위 1차입니다.
- `killEnemy()`, 드랍 판정, 장착/해제, 스킬강화권 사용 로직은 아직 완전한 결과 객체 구조로 바꾸지 않았습니다.
- 기존 게임 동작을 유지하는 것을 우선했습니다.


## v069 - skill save migration fix

- v068 스킬 구조 변경 후 기존 저장 데이터의 `player.skills`가 새 캐릭터별 스킬 구조로 완전히 이관되지 않을 수 있는 문제를 보정했습니다.
- `src/data/skills.js`에 레거시 스킬 상태 병합 로직을 추가했습니다.
- 일반 Q 스킬은 기존 v065~v068과 동일하게 데미지 텍스트 표시 대상에서 제외했습니다.
- CSS 중복은 아직 실제 CSS 코드를 병합하지 않았습니다. 문서상으로 “전체 자동 압축은 위험, 완전히 동일한 선택자부터 선별 병합” 원칙을 유지합니다.

# 변경 이력

## v066-docs-maintenance

목적:

- 기호가 요청한 유지보수/탐색/계획 문서 보강
- ZIP을 받은 뒤 무엇을 먼저 봐야 하는지 명확히 정리
- 다음 작업자가 빠르게 구조를 파악할 수 있게 문서 추가

추가된 문서:

```txt
README.md
docs/BACKEND_SPLIT_STAGE2_PLAN.md
docs/BACKEND_SPLIT_CHECKLIST.md
docs/CODE_MAP.md
docs/ADMIN_PAGE_REQUIREMENTS.md
docs/DECISION_LOG.md
docs/CHANGELOG.md
```

기능 코드 변경:

```txt
없음
```

기존 v066 상태 분리 작업은 유지했습니다.

---

## v066_backend_ready_state_split

목적:

- 백엔드 분리 준비 2차 정리 중 1순위 상태 분리 적용

변경:

- `gameState.server` 추가
- `gameState.client` 추가
- `gameState.runtime` 추가
- 기존 전역 변수 호환 유지
- 저장/불러오기용 헬퍼 추가
- `src/state/STATE_SPLIT_READY.md` 추가

## v0.67 - 백엔드 분리 준비 2순위: bosses.js 역할 분리

- `src/data/bosses.js`를 순수 보스/드랍 원본 데이터 중심으로 축소했습니다.
- 고티어 보스/장비 생성 공식은 `src/data/boss-factories.js`로 분리했습니다.
- 아이콘 생성 유틸은 `src/utils/icon-utils.js`로 분리했습니다.
- 심연의 편린 특수 옵션 규칙은 `src/rules/abyss-fragment-rules.js`로 분리했습니다.
- 보스 표시용 후처리는 `src/rules/boss-display-rules.js`로 분리했습니다.
- 드랍률 보정/최초 장비 보너스 규칙은 `src/rules/boss-drop-rules.js`로 분리했습니다.
- 후처리 실행 순서는 `src/data/boss-bootstrap.js`에서 관리합니다.
- 기존 `bossList`, `specialBossList`, `getNormalBossSkillDropRate()`, `grantFirstEquipSkillBookIfNeeded()` 이름은 유지했습니다.


## v0.68 - 백엔드 분리 준비 3순위: 캐릭터별 스킬 구조 준비

- `src/data/skills.js`를 추가했습니다.
- 기본 캐릭터 `weapon_master`를 등록했습니다.
- 현재 스킬 8개를 `skillMasterData`로 분리했습니다.
- Q/SQ, W/SW 각성 정보를 스킬 데이터 내부로 이동했습니다.
- 스킬강화권 매핑을 `skillBookMasterData`로 분리했습니다.
- 기존 `skillBookMapping` 이름은 호환용으로 유지했습니다.
- `player.currentCharacterId`, `player.ownedCharacterIds`, `player.userCharacters` 구조를 추가했습니다.
- 기존 `player.skills` 접근은 유지하되, 현재 캐릭터 스킬 객체와 동기화되도록 했습니다.
- `renderSkills()`가 중앙 스킬 데이터 기반으로 스킬 UI를 그리도록 변경했습니다.
- `item-system.js`의 스킬강화권 사용 로직이 중앙 스킬 데이터와 현재 캐릭터 스킬을 참조하도록 변경했습니다.
- `combat-system.js`가 현재 캐릭터 스킬 헬퍼를 우선 사용하도록 변경했습니다.
- `docs/SKILL_STRUCTURE_READY.md`를 추가했습니다.
- `docs/CSS_AUDIT.md`를 추가했습니다.

주의:

- 이번 작업은 스킬 구조 변경 1차입니다.
- 전투 공식 전체를 완전히 데이터 기반으로 바꾸지는 않았습니다.
- 다음 단계에서 `combat-system.js`, `item-system.js`의 UI 호출 제거와 결과 객체화를 진행하는 것이 좋습니다.


## v070 - 스킬 데미지 텍스트 위치 수정 + CSS 안전 병합

### 수정

- `src/systems/combat-system.js`
  - 스킬 데미지 텍스트가 `.enemy-display(width: 100%)` 기준으로 계산되어 화면 밖으로 나갈 수 있던 문제를 수정했습니다.
  - 데미지 텍스트 기준점을 `#enemy-image-placeholder`로 변경했습니다.
  - 전투 영역 밖으로 텍스트가 나가지 않도록 위치 보정 함수를 추가했습니다.

### CSS

- `src/styles/style.css`
  - 최종 적용값이 유지되는 안전 중복 규칙 38개를 병합/제거했습니다.
  - 병합 후 CSS 파싱 오류가 없는지 확인했습니다.

### 문서

- `docs/DAMAGE_TEXT_POSITION_FIX.md` 추가
- `docs/CSS_MERGE_REPORT.md` 추가


## v075 - Backend Foundation Draft

### Added

```txt
backend/ FastAPI 프로젝트 뼈대 추가
docs/ADMIN_REQUIREMENTS_V1.md 추가
docs/DB_SCHEMA_DRAFT.md 추가
docs/BACKEND_ARCHITECTURE.md 추가
docs/BACKEND_API_ROUTES_DRAFT.md 추가
backend/sql/schema_draft.sql 추가
tools/smoke_backend_foundation.js 추가
```

### Notes

```txt
기존 프론트 게임 동작은 변경하지 않음
관리자 페이지 요구사항을 DB/FastAPI 설계 기준으로 고정
PostgreSQL + SQLAlchemy + Alembic 기반 초안 작성
```

## v076 - Dev Environment Setup

### Added

```txt
docker-compose.yml 추가
.gitignore 추가
.dockerignore 추가
docs/LOCAL_DEV_SETUP.md 추가
docs/DOCKER_POSTGRES_GUIDE.md 추가
docs/GIT_WORKFLOW.md 추가
tools/check_backend_ready.py 추가
```

### Backend

```txt
backend/.env.example 보강
/api/v1/health/db 엔드포인트 추가
backend/README.md 로컬 실행 안내 보강
```

### Notes

```txt
기존 프론트 게임 실행 흐름은 변경하지 않음
Docker PostgreSQL + Adminer 로컬 실행 준비 완료
다음 단계는 JS 마스터 데이터 추출 도구 작성 + seed JSON 생성 추천
```


## v079 seed import connection fix

- `backend/scripts/setup_dev_db.py`를 sync SQLAlchemy + `psycopg` 방식으로 변경했습니다.
- Windows/Docker 환경에서 `asyncpg.exceptions.ConnectionDoesNotExistError`가 seed import 중 발생하는 문제를 피하기 위한 수정입니다.
- `backend/pyproject.toml`에 `psycopg[binary]` 의존성을 추가했습니다.


## v080 - Local DB Port Fix

- 로컬 Docker PostgreSQL 호스트 포트를 `5432`에서 `55432`로 변경했다.
- `backend/.env.example`, `backend/app/core/config.py`, `backend/alembic.ini`의 기본 DB 주소를 `127.0.0.1:55432` 기준으로 맞췄다.
- Windows 환경에서 기존 로컬 PostgreSQL과 포트 충돌이 나지 않도록 `docs/LOCAL_DB_PORT_POLICY.md`를 추가했다.
- 이번 변경은 기존 프론트 게임 기능에는 영향을 주지 않는다.

## v081 - Master Data API DB 연결

- `/api/v1/game/master-data`의 임시 stub 응답을 제거하고 PostgreSQL seed 테이블을 실제로 읽도록 변경했습니다.
- `payload`에 characters, skills, itemTemplates, bosses, fieldZones, dropTables, enhancementRules 등을 포함합니다.
- `meta.counts`와 `payload.counts`로 주요 마스터 데이터 개수를 확인할 수 있습니다.
- `backend/scripts/check_master_data_api.py`를 추가해 서버 실행 후 API 응답을 터미널에서 점검할 수 있게 했습니다.
- `docs/MASTER_DATA_API.md` 문서를 추가했습니다.

## v082 - Seed Import Long Asset Fix

- seed import 중 `item_templates.icon_url` 등 긴 SVG data URL이 `VARCHAR(500)` 제한에 걸리던 문제를 수정했습니다.
- `characters.image_url`, `skills.icon_url`, `item_templates.icon_url`, `bosses.image_url` 컬럼을 `TEXT` 기준으로 변경했습니다.
- `setup_dev_db.py` 기본 SQL 로그 출력을 줄이고, 필요할 때만 `--verbose-sql`로 긴 SQL 로그를 볼 수 있게 했습니다.

## v083 - Master Data Asset Cleanup

- `/api/v1/game/master-data` 기본 응답에서 긴 SVG/data URL 이미지 문자열을 제외합니다.
- 기본 응답에서는 `imageUrl`, `iconUrl`이 `null`로 내려가고, `hasImage`, `hasIcon`으로 원본 이미지 존재 여부를 확인합니다.
- 이미지 문자열까지 필요한 경우 `?includeAssets=true`를 붙여 요청할 수 있습니다.
- `payload.assetPolicy`와 `meta.assetPolicy`를 추가해 현재 asset 포함 정책을 응답에 명시합니다.
- `scripts/check_master_data_api.py`가 기본 응답에 긴 data URL이 포함되지 않는지도 검사합니다.
- `docs/MASTER_DATA_ASSET_POLICY.md` 문서를 추가했습니다.

## v084 - Master Data Nested Asset Cleanup

- `v083`에서 최상위 `imageUrl`/`iconUrl`은 제거됐지만, `options`, `conditions`, `rules`, `raw` 같은 중첩 JSON 안에 남아 있던 `data:image...` 문자열을 추가로 제거했습니다.
- 기본 `/api/v1/game/master-data` 응답에서는 모든 중첩 inline image data URL을 `null`로 내려줍니다.
- `?includeAssets=true` 요청에서는 최상위 asset 필드와 중첩 JSON 안의 asset 문자열을 모두 포함합니다.
- `tools/smoke_master_data_nested_asset_cleanup.py`를 추가했습니다.

## v085 - Frontend Master Data Bridge

- 브라우저에서 FastAPI `/api/v1/game/master-data`를 호출할 수 있는 프론트 API 클라이언트를 추가했습니다.
- `src/api/game-api-client.js`, `src/api/master-data-bridge.js`를 추가했습니다.
- 기존 게임 동작은 아직 정적 JS 데이터를 그대로 사용하며, API 데이터는 검증/캐시용 snapshot으로만 보관합니다.
- 브라우저 콘솔에서 `await checkBackendMasterData()`로 백엔드 master-data 연결을 확인할 수 있습니다.
- `tools/smoke_frontend_master_data_bridge.js` 정적 검증 도구와 `docs/FRONTEND_MASTER_DATA_BRIDGE.md` 문서를 추가했습니다.

## v088 - Frontend master-data adapter

- Added `src/api/master-data-adapter.js`.
- Converts `/api/v1/game/master-data` payload into legacy-like browser data structures without changing live gameplay yet.
- Added browser console helpers: `checkBackendMasterDataAdapter()`, `loadAdaptedBackendMasterData()`, `getCachedAdaptedBackendMasterData()`.
- Added `tools/smoke_master_data_adapter.js` to verify adapter structure, counts, boss split, field count, item count, and nullable skill proc rate preservation.
- Documented the adapter in `docs/MASTER_DATA_ADAPTER.md`.

## v089 - Backend master-data runtime switch

- Added `src/api/master-data-runtime-switch.js`.
- Backend master-data runtime mode is OFF by default and can be enabled from the browser console.
- Console helpers: `enableBackendMasterDataMode()`, `disableBackendMasterDataMode()`, `checkBackendMasterDataRuntimeMode()`.
- When enabled, FastAPI master-data is fetched with `includeAssets=true`, adapted to legacy-like structures, and injected before the original game initialization runs.
- Injection mutates existing legacy objects/arrays instead of reassigning top-level `const` declarations.
- If API loading fails, the game falls back to the existing static JS data.
- Added `tools/smoke_master_data_runtime_switch.js` and `docs/MASTER_DATA_RUNTIME_SWITCH.md`.

## v090 - Backend master-data runtime validator

- Added `src/api/master-data-runtime-validator.js`.
- Added browser console helpers: `checkBackendMasterDataRuntimeIntegrity()`, `assertBackendMasterDataRuntimeIntegrity()`, `getBackendMasterDataRuntimeDebugSnapshot()`.
- The validator checks backend runtime mode state, active global master-data counts, applied backend data counts, core DOM availability, and sample boss/field/skill values.
- Added `tools/smoke_master_data_runtime_validator.js` and `docs/MASTER_DATA_RUNTIME_VALIDATOR.md`.
- Existing game behavior remains unchanged. The validator only inspects runtime state.

## v091 - Backend master-data browser checklist

- Added `src/api/master-data-browser-checklist.js`.
- Added browser console helpers: `runBackendMasterDataBrowserChecklist()`, `assertBackendMasterDataBrowserChecklist()`, `printBackendMasterDataManualChecklist()`.
- The checklist verifies backend master-data mode state, required helper functions, core DOM ids, rendered boss/field/inventory/equipment panels, sample data, and nullable `lightsabre` proc rate preservation.
- Added `tools/smoke_master_data_browser_checklist.js` and `docs/MASTER_DATA_BROWSER_CHECKLIST.md`.
- Existing game behavior remains unchanged. The checklist only inspects and optionally re-renders existing panels.
## v092 - Backend master-data auto boot policy

- Added `src/api/master-data-boot-policy.js`.
- Added default `auto` boot policy with static JS fallback.
- Added API request timeout support through `AbortController`.
- Updated runtime switch to hydrate missing image/icon assets from already-loaded static JS data when API assets are excluded.
- Added `tools/smoke_master_data_auto_boot_policy.js`.



## v093 - Browser checklist optional modal fix

- `#test-special-item-modal`을 필수 DOM에서 선택 DOM으로 변경했다.
- 특수 장비 지급 모달 요소가 동적 생성/생략되는 구조에서도 백엔드 master-data checklist가 불필요하게 실패하지 않도록 보정했다.
- 체크리스트 버전을 `v093.backend-master-data-browser-checklist`로 갱신했다.
- 수동 체크리스트 중복 문구를 제거했다.


### v093 추가 보정 - Master-data bridge timeout summary

- `src/api/master-data-bridge.js`의 `checkMasterDataApi()` summary에서 정의되지 않은 `timeoutMs` 변수를 참조하던 문제를 수정했다.
- `snapshot.timeoutMs`를 사용하도록 변경해 브라우저와 Node smoke test 모두 안정적으로 동작하게 했다.

## v094 - Field zone asset fallback

- 백엔드 master-data 기본 응답에서 assets를 제외할 때 필드존 이미지가 `undefined`가 되어 `file:///.../undefined` 요청이 발생하던 문제를 수정했다.
- `master-data-adapter`가 field zone의 `img`/`hasImage` 필드를 명시하도록 보강했다.
- `master-data-runtime-switch`가 기존 정적 `zones` 데이터에서 field zone 이미지 값을 보정하도록 추가했다.
- `renderFieldZone()`에 최후 방어용 기본 이미지 fallback을 추가했다.
- `tools/smoke_field_zone_asset_fallback.js`와 `docs/MASTER_DATA_FIELD_ZONE_ASSET_FALLBACK.md`를 추가했다.


## v096 - Master-data dev badge HUD position

- 개발자용 master-data 배지를 bottom HUD 내부로 이동했다.
- 배지 위치를 중앙 능력치 패널 오른쪽, 프로필 사진의 반대편에 배치했다.
- `hide` 버튼으로 숨긴 배지를 `showBackendMasterDataDevBadge()`로 다시 표시할 수 있음을 문서화했다.
- 작은 화면에서는 배지가 오른쪽 위로 이동하도록 반응형 위치를 보정했다.

## v097 - Master-data dev badge controls polish

- 개발자용 master-data 배지의 버튼 줄 넘침 문제를 수정했다.
- `hide` 버튼을 배지 내부에서 분리해 배지 위쪽의 별도 토글 버튼으로 이동했다.
- 배지를 숨긴 뒤에도 화면의 `show MD` 버튼으로 다시 표시할 수 있게 했다.
- `auto` / `static` 버튼에 현재 적용 중인 모드를 나타내는 활성 스타일을 추가했다.
- `refresh` 버튼의 의미를 명확히 하기 위해 `updated` 시간을 표시하고 문서를 보강했다.

## v099 - Save Snapshot API Bridge

- Added `user_save_snapshots` table/model for raw localStorage save snapshots.
- Implemented `POST /api/v1/game/save` and `GET /api/v1/game/load` as DB-backed snapshot APIs.
- Added browser helpers: `pushLocalSaveToBackend()`, `loadBackendSaveSnapshot()`, and `checkBackendSaveSnapshotBridge()`.
- Added static and live smoke tests for the save snapshot bridge.
