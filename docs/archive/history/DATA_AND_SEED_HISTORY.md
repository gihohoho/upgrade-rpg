# 마스터 데이터·시드 개발 역사

> 완료된 단계별 메모를 검색 가능한 한 파일로 통합한 읽기 전용 역사입니다.
> 현재 작업 판단에는 `docs/current/`와 루트 `NEXT_CHAT_HANDOFF.md`를 사용하세요.
> 원본 파일은 Git commit `270d57bd234ede18cee7168f4b5da36b1a08df18` 이전 이력에서 복원할 수 있습니다.

## 통합된 원본

- `docs/archive/stage-notes/BACKEND_API_ROUTES_DRAFT.md`
- `docs/archive/stage-notes/DB_SCHEMA_DRAFT.md`
- `docs/archive/stage-notes/MASTER_DATA_ADAPTER.md`
- `docs/archive/stage-notes/MASTER_DATA_API.md`
- `docs/archive/stage-notes/MASTER_DATA_ASSET_POLICY.md`
- `docs/archive/stage-notes/MASTER_DATA_AUTO_BOOT_POLICY.md`
- `docs/archive/stage-notes/MASTER_DATA_DEV_BADGE.md`
- `docs/archive/stage-notes/MASTER_DATA_FIELD_ZONE_ASSET_FALLBACK.md`
- `docs/archive/stage-notes/MASTER_DATA_NESTED_ASSET_CLEANUP.md`
- `docs/archive/stage-notes/MASTER_DATA_NULLABLE_FIELDS.md`
- `docs/archive/stage-notes/MASTER_DATA_PARITY_CHECKER.md`
- `docs/archive/stage-notes/MASTER_DATA_RUNTIME_SWITCH.md`
- `docs/archive/stage-notes/MASTER_DATA_RUNTIME_VALIDATOR.md`
- `docs/archive/stage-notes/SEED_EXTRACTION.md`
- `docs/archive/stage-notes/SEED_IMPORT.md`
- `docs/archive/stage-notes/SEED_IMPORT_CONNECTION_FIX.md`
- `docs/archive/stage-notes/SEED_IMPORT_LONG_ASSET_FIX.md`

---

## 원본: `docs/archive/stage-notes/BACKEND_API_ROUTES_DRAFT.md`

# FastAPI API Routes 초안

## 시스템

```txt
GET /api/v1/health
```

## 게임 데이터

```txt
GET  /api/v1/game/master-data
GET  /api/v1/game/load
POST /api/v1/game/save
```

## 전투/보스

```txt
POST /api/v1/battle/attack
POST /api/v1/battle/kill
POST /api/v1/boss/summon
POST /api/v1/boss/attack
```

## 아이템

```txt
POST /api/v1/item/equip
POST /api/v1/item/unequip
POST /api/v1/item/enhance
POST /api/v1/item/move-storage
POST /api/v1/item/move-trash
POST /api/v1/item/empty-trash
```

## 스킬강화권

```txt
POST /api/v1/skill-book/use
```

## 우편함

```txt
GET  /api/v1/mailbox
POST /api/v1/mailbox/{message_id}/claim
POST /api/v1/mailbox/claim-all
```

## 관리자 V1

```txt
GET   /api/v1/admin/requirements
GET   /api/v1/admin/items
POST  /api/v1/admin/items
PATCH /api/v1/admin/items/{code}

GET   /api/v1/admin/bosses
POST  /api/v1/admin/bosses
PATCH /api/v1/admin/bosses/{code}

GET   /api/v1/admin/drop-tables
POST  /api/v1/admin/drop-tables
PATCH /api/v1/admin/drop-tables/{code}

GET   /api/v1/admin/field-zones
PATCH /api/v1/admin/field-zones/{code}

GET   /api/v1/admin/enhancement-groups
PATCH /api/v1/admin/enhancement-groups/{code}

GET   /api/v1/admin/characters
POST  /api/v1/admin/characters
PATCH /api/v1/admin/characters/{code}

GET   /api/v1/admin/skills
POST  /api/v1/admin/skills
PATCH /api/v1/admin/skills/{code}

POST  /api/v1/admin/change-preview
POST  /api/v1/admin/change-apply
POST  /api/v1/admin/change-rollback/{change_log_id}
GET   /api/v1/admin/change-logs
```

## 구현 순서 추천

```txt
1. health
2. game.master-data
3. game.load/save
4. admin requirements/change-preview
5. admin items/bosses/drop-tables
6. item equip/unequip/enhance
7. boss summon/combat/drop
```

---

## 원본: `docs/archive/stage-notes/DB_SCHEMA_DRAFT.md`

# PostgreSQL DB 설계 초안

이 문서는 현재 게임을 PostgreSQL로 옮기기 위한 1차 설계입니다.
목표는 관리자 페이지에서 게임 수치를 바꿀 수 있게 하면서도, 유저 데이터가 꼬이지 않도록 분리하는 것입니다.

## 1. 설계 원칙

```txt
마스터 데이터 = 게임 원본 데이터
유저 데이터 = 유저가 실제로 가진 상태
관리자 변경 이력 = 누가 무엇을 어떻게 바꿨는지
```

예시:

```txt
item_templates = 심연의 편린 스태프라는 원본
item_instances = 특정 유저가 가진 +7 심연의 편린 스태프
```

## 2. 주요 테이블 그룹

### 계정/프로필

```txt
users
user_profiles
```

역할:

```txt
로그인 계정
골드
현재 캐릭터
현재 필드 진행도
기록/플래그 JSON
```

### 캐릭터/스킬

```txt
characters
skills
character_skills
skill_levels
user_character_skills
```

역할:

```txt
캐릭터 추가 대응
캐릭터별 스킬 연결
스킬 레벨별 수치
유저별 스킬 레벨/각성 상태
```

중요 원칙:

```txt
캐릭터마다 스킬만 다르고, 나머지 시스템은 공통 사용한다.
```

### 아이템/인벤토리/장비

```txt
item_templates
item_instances
user_inventory_slots
user_equipment_slots
```

역할:

```txt
아이템 원본
유저 보유 아이템
인벤토리/보관함/휴지통 슬롯
캐릭터별 장비 슬롯
```

### 보스/드랍

```txt
bosses
drop_tables
drop_table_items
```

역할:

```txt
일반 보스/특수 보스
보스별 드랍 테이블
드랍 아이템/확률/수량/조건
```

### 필드존

```txt
field_zones
```

역할:

```txt
필드명
몬스터 HP
골드 보상
입장 조건
공격력/공격속도 성장 규칙
```

### 강화

```txt
enhancement_groups
enhancement_levels
```

역할:

```txt
일반 장비 강화
심연의 편린 강화
탈리스만/휘장 강화
단계별 확률/비용/재료/증가 수치
```

### 우편/보상

```txt
user_mailbox_messages
```

역할:

```txt
관리자 보상 지급
이벤트 보상
시스템 보상
```

### 관리자/변경 이력

```txt
admin_roles
admin_user_roles
admin_change_logs
```

역할:

```txt
관리자 권한
수정 전/후 값
수정 사유
되돌리기 데이터
```

## 3. JSONB 사용 기준

PostgreSQL을 쓰되, 게임 옵션은 유연해야 하므로 일부 컬럼은 JSONB를 사용합니다.

JSONB 사용 추천:

```txt
아이템 특수 옵션
스킬 세부 옵션
보스 소환 조건
필드 성장 규칙
강화 재료 규칙
관리자 변경 전/후 데이터
```

일반 컬럼 사용 추천:

```txt
id
code
name
type
gold
level
rate
hp
created_at
updated_at
```

## 4. 관리자 페이지와 연결되는 핵심 테이블

```txt
아이템 관리      → item_templates
보스 관리        → bosses
드랍률 관리      → drop_tables, drop_table_items
필드존 관리      → field_zones
강화 규칙 관리   → enhancement_groups, enhancement_levels
캐릭터 관리      → characters
스킬 관리        → skills, character_skills, skill_levels
우편 지급        → user_mailbox_messages
변경 이력        → admin_change_logs
```

## 5. 다음 확정 작업

```txt
1. 현재 JS 데이터에서 item_templates seed 추출
2. bossList/specialBossList를 bosses + drop_tables로 변환
3. zones를 field_zones로 변환
4. skills.js를 characters/skills/character_skills/skill_levels로 변환
5. enhancement rules를 enhancement_groups/levels로 변환
6. Alembic 첫 마이그레이션 생성
```

세부 SQL 초안은 `backend/sql/schema_draft.sql`에 있습니다.


## v078 타입 보정

현재 게임의 보스 HP/필드 HP/골드 보상은 일반 `INTEGER` 범위를 넘는 값이 존재합니다.
따라서 아래 계열은 PostgreSQL에서 `NUMERIC(40,0)` 기준으로 설계합니다.

- `bosses.hp`
- `field_zones.enemy_hp`
- `field_zones.gold_reward`
- `enhancement_levels.gold_cost`
- `user_profiles.gold`

이 보정은 관리자 페이지에서 큰 수치를 직접 조정할 때도 필요합니다.

---

## 원본: `docs/archive/stage-notes/MASTER_DATA_ADAPTER.md`

# Master Data Adapter

## 목적

`GET /api/v1/game/master-data` 응답을 기존 브라우저 게임 코드가 쓰던 데이터 구조에 가까운 형태로 변환하는 준비 단계입니다.

이번 단계에서는 실제 게임 런타임을 API 데이터로 교체하지 않습니다. 기존 게임 동작은 그대로 유지하고, 브라우저 콘솔/테스트 도구로만 변환 결과를 확인합니다.

## 추가 파일

```txt
src/api/master-data-adapter.js
tools/smoke/game/smoke_master_data_adapter.js
docs/archive/stage-notes/MASTER_DATA_ADAPTER.md
```

## 로딩 순서

`index.html`에서는 아래 순서로 로드합니다.

```html
<script src="src/api/game-api-client.js"></script>
<script src="src/api/master-data-bridge.js"></script>
<script src="src/api/master-data-adapter.js"></script>
```

`master-data-adapter.js`는 `RpgMasterDataBridge`를 이용해 API 데이터를 받고, 그 데이터를 기존 JS 데이터와 비슷한 형태로 바꿉니다.

## 브라우저 콘솔 확인

FastAPI 서버가 켜져 있을 때 브라우저 개발자도구 Console에서 실행합니다.

```js
await checkBackendMasterDataAdapter();
```

정상이면 다음 로그가 나옵니다.

```txt
[Upgrade RPG] master-data adapter check passed
```

이미지 data URL까지 포함해서 확인하려면 다음처럼 실행합니다.

```js
await checkBackendMasterDataAdapter({ includeAssets: true });
```

## 변환 결과 확인

마지막 변환 결과는 아래 전역 변수에 저장됩니다.

```js
getCachedAdaptedBackendMasterData();
```

반환 구조는 대략 아래와 같습니다.

```js
{
  legacyData: {
    defaultCharacterId,
    characterMasterData,
    skillMasterData,
    itemTemplateList,
    itemTemplateMap,
    dropTables,
    bossList,
    specialBossList,
    fieldZones,
    enhancementRules
  },
  validation: {
    ok,
    counts,
    failures,
    hasInlineAsset
  }
}
```

## 검증 항목

어댑터는 최소한 아래 항목을 확인합니다.

```txt
캐릭터 1개 이상
스킬 8개 이상
아이템 템플릿 245개 이상
일반 보스 39개 이상
특수 보스 6개 이상
필드 40개 이상
lightsabre.baseProcRate null 보존
기본 응답에서 inline data URL 제거 유지
```

## 터미널 정적 검사

위치: 프로젝트 루트

```bash
node tools/smoke/game/smoke_master_data_adapter.js
```

정상이면 다음이 출력됩니다.

```txt
master-data adapter smoke test passed
```

## 다음 단계

이 어댑터 검증이 안정적으로 통과하면 다음 단계에서 실제 런타임 전환 플래그를 만들 수 있습니다.

예상 다음 단계:

```txt
API master-data 사용 모드 OFF/ON 플래그 추가
기본값 OFF
ON일 때만 API 데이터를 기존 전역 데이터에 주입
문제 발생 시 기존 JS 데이터로 즉시 fallback
```

---

## 원본: `docs/archive/stage-notes/MASTER_DATA_API.md`

# Master Data API

`v081`부터 `/api/v1/game/master-data`는 더 이상 임시 `stub` 응답만 반환하지 않습니다.
로컬 PostgreSQL에 import된 seed 테이블을 읽어서 프론트엔드가 사용할 수 있는 마스터 데이터를 내려줍니다.

## 실행 전 조건

아래 작업이 먼저 완료되어 있어야 합니다.

1. Docker PostgreSQL 실행
2. seed JSON 생성
3. seed 데이터를 PostgreSQL에 import
4. FastAPI 서버 실행

## seed import

위치: **프로젝트 루트**

```bash
node tools/extract_seed_data.js
node tools/smoke/game/smoke_seed_extraction.js
```

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
source .venv/Scripts/activate
python scripts/setup_dev_db.py --reset --seed --verify
```

## 서버 실행

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
uvicorn app.main:app --reload
```

브라우저 확인:

```txt
http://127.0.0.1:8000/api/v1/game/master-data
```

`v083`부터 기본 응답은 백신 오탐과 응답 크기 문제를 줄이기 위해 긴 SVG/data URL 이미지 문자열을 제외합니다.
이미지 문자열까지 확인해야 할 때만 아래 주소를 사용합니다.

```txt
http://127.0.0.1:8000/api/v1/game/master-data?includeAssets=true
```

## 터미널 확인 스크립트

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
python scripts/check_master_data_api.py
```

이미지 문자열 포함 응답까지 확인하고 싶다면 아래처럼 실행합니다.

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
python scripts/check_master_data_api.py --include-assets
```

정상이면 아래처럼 출력됩니다.

```txt
master-data API check passed
```

## 응답 구조

응답은 기존 `game-api-response.v1` 계약을 유지합니다.

```json
{
  "ok": true,
  "responseVersion": "game-api-response.v1",
  "type": "game.master_data",
  "payload": {
    "characters": [],
    "skills": [],
    "characterSkills": [],
    "skillLevels": [],
    "itemTemplates": [],
    "bosses": [],
    "fieldZones": [],
    "dropTables": [],
    "dropTableItems": [],
    "enhancementGroups": [],
    "enhancementLevels": [],
    "enhancementRules": {
      "groups": [],
      "levels": []
    },
    "assetPolicy": {
      "includeAssets": false,
      "mode": "metadata-only"
    },
    "counts": {}
  },
  "data": {
    "status": "loaded",
    "userId": 1
  },
  "meta": {
    "source": "postgresql",
    "counts": {}
  },
  "error": null
}
```

## 현재 포함되는 데이터

- characters
- skills
- characterSkills
- skillLevels
- itemTemplates
- bosses
- fieldZones
- dropTables
- dropTableItems
- enhancementGroups
- enhancementLevels
- enhancementRules

## 다음 단계

다음 단계에서는 프론트엔드가 아직 JS 파일에서 직접 읽는 마스터 데이터를 FastAPI API 응답으로 점진적으로 교체할 준비를 합니다.
단, 게임 화면 전체를 한 번에 API로 바꾸기보다는 먼저 읽기 전용 브릿지부터 붙이는 방식이 안전합니다.

## seed import가 0개로 보일 때

`scripts/check_master_data_api.py`에서 모든 개수가 0으로 나오면 API가 실패한 것이 아니라 seed import가 중간에 실패해 롤백됐을 수 있습니다.

특히 아래 오류가 있으면 이미지/아이콘 URL 컬럼 길이 문제입니다. v082 이상에서는 해당 컬럼을 `TEXT`로 변경했습니다.

```txt
value too long for type character varying(500)
```

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
python scripts/setup_dev_db.py --reset --seed --verify
```


## v083 asset 정책

기본 응답에서는 아래 필드가 `null`로 내려갑니다.

```txt
characters.imageUrl
skills.iconUrl
itemTemplates.iconUrl
bosses.imageUrl
```

대신 `hasImage`, `hasIcon` 값으로 원본 이미지 데이터 존재 여부를 알 수 있습니다.
긴 SVG/data URL까지 필요하면 `?includeAssets=true`를 붙여 요청합니다.
자세한 내용은 `docs/archive/stage-notes/MASTER_DATA_ASSET_POLICY.md`를 참고하세요.

---

## 원본: `docs/archive/stage-notes/MASTER_DATA_ASSET_POLICY.md`

# Master Data Asset Policy

`v083`부터 `/api/v1/game/master-data`는 기본 응답에서 긴 이미지 문자열을 제외합니다.

## 이유

현재 seed 데이터에는 아래처럼 긴 SVG data URL이 들어 있습니다.

```txt
data:image/svg+xml;charset=UTF-8,%3Csvg...
```

이 문자열은 실제 바이러스라기보다는 로컬 개발 API 응답 안에 포함된 긴 SVG 문자열입니다. 하지만 일부 백신/브라우저 보안 기능은 JSON 응답 안의 긴 SVG data URL을 의심스럽게 보고 경고를 띄울 수 있습니다.

## 기본 응답

위치: **브라우저 주소창**

```txt
http://127.0.0.1:8000/api/v1/game/master-data
```

기본 응답에서는 아래 필드가 `null`로 내려갑니다.

```txt
characters.imageUrl
skills.iconUrl
itemTemplates.iconUrl
bosses.imageUrl
```

대신 실제 이미지 데이터가 있는지 알 수 있도록 아래 값은 유지합니다.

```txt
hasImage
hasIcon
assetPolicy
```

## 이미지 문자열까지 포함해서 확인하기

위치: **브라우저 주소창**

```txt
http://127.0.0.1:8000/api/v1/game/master-data?includeAssets=true
```

이렇게 요청하면 기존처럼 긴 `imageUrl`, `iconUrl` data URL까지 포함됩니다.

## 터미널 확인

기본 경량 응답 확인:

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
python scripts/check_master_data_api.py
```

이미지 문자열 포함 응답 확인:

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
python scripts/check_master_data_api.py --include-assets
```

## 이후 방향

나중에 Vue/Vite 프론트엔드로 전환할 때는 긴 data URL을 API로 직접 내려주는 방식보다 아래 방식이 더 안전합니다.

```txt
DB/API: iconKey, imageKey, assetPath 같은 짧은 참조값 제공
Frontend: public/assets 또는 CDN/static 경로에서 이미지 로드
```

이번 v083은 그 전 단계로, 기존 seed 구조를 크게 바꾸지 않으면서 백신 오탐과 응답 크기 문제를 줄이는 안전한 조치입니다.

---

## 원본: `docs/archive/stage-notes/MASTER_DATA_AUTO_BOOT_POLICY.md`

# Master-data Auto Boot Policy

v092에서는 브라우저 게임 시작 시 백엔드 `master-data`를 자동으로 시도하는 부트 정책을 추가했습니다.

## 핵심 목표

기존에는 개발자도구에서 `enableBackendMasterDataMode()`를 직접 실행해야 백엔드 데이터를 썼습니다.
이제 기본 정책은 `auto`입니다.

```txt
auto 모드:
1. 게임 시작 전 FastAPI /api/v1/game/master-data 요청
2. 성공하면 백엔드 데이터를 기존 전역 데이터에 주입
3. 실패하면 기존 JS 데이터로 자동 fallback
```

즉 FastAPI 서버가 꺼져 있어도 게임은 멈추지 않습니다.

## 기본 정책

```txt
mode: auto
includeAssets: false
timeoutMs: 1500
fallbackToStaticJs: true
```

`includeAssets` 기본값은 `false`입니다. 백신 오탐 가능성을 줄이기 위해 기본 API 요청에는 긴 `data:image/svg+xml...` 문자열을 포함하지 않습니다.
이미지/아이콘이 비어 있는 부분은 이미 로드된 기존 JS 데이터의 asset을 복사해서 채웁니다.

## 브라우저 Console 명령어

현재 정책 확인:

```js
getBackendMasterDataBootPolicy();
printBackendMasterDataBootPolicy();
```

자동 백엔드 시도 모드:

```js
useAutoBackendMasterDataMode();
```

기존 JS 데이터만 사용:

```js
useStaticMasterDataMode();
```

백엔드 데이터 사용 모드:

```js
enableBackendMasterDataMode();
```

백엔드 필수 모드:

```js
requireBackendMasterDataMode();
```

백엔드 API에서 asset까지 포함:

```js
setBackendMasterDataIncludeAssets(true, { reload: true });
```

asset 제외로 되돌리기:

```js
setBackendMasterDataIncludeAssets(false, { reload: true });
```

요청 timeout 변경:

```js
setBackendMasterDataTimeoutMs(2500);
```

## 추천 확인 순서

1. FastAPI 서버를 켠다.
2. 게임 페이지를 새로고침한다.
3. Console에서 아래를 실행한다.

```js
await checkBackendMasterDataRuntimeMode();
runBackendMasterDataBrowserChecklist();
```

정상이라면 `state`가 `applied`이고 checklist의 `ok`가 `true`입니다.

## FastAPI가 꺼져 있을 때

FastAPI가 꺼져 있어도 `timeoutMs` 이후 기존 JS 데이터로 계속 실행됩니다.
이때 상태는 보통 아래처럼 나옵니다.

```txt
failed_fallback_to_static_js
```

이 상태는 개발 중 정상적인 fallback입니다.

---

## 원본: `docs/archive/stage-notes/MASTER_DATA_DEV_BADGE.md`

# Master Data Dev Badge

v095에서는 브라우저 화면에 백엔드 master-data 적용 상태를 보여주는 개발자용 배지를 추가했고, v096에서는 배지 위치를 bottom HUD 안의 능력치 패널 오른쪽으로 옮겼다. v097에서는 버튼 줄 넘침을 고치고, 숨김/보임을 Console 없이 화면 안에서 처리할 수 있게 했다. v098에서는 토글 버튼을 `hide MD` / `show MD`로 명확히 바꾸고 배지 상단 정가운데 탭처럼 정렬했다.

## 목적

Console을 열지 않아도 현재 게임이 어떤 master-data 모드로 실행 중인지 빠르게 확인하기 위함이다.

표시 예시:

```txt
MASTER DATA  applied
mode: auto   assets: off
counts: B:39 · S:6 · F:40 · I:245
updated: 16:45:10
```

## 기본 표시 정책

배지는 아래 환경에서 기본 표시된다.

```txt
file://
localhost
127.0.0.1
```

운영 배포 환경에서는 기본 표시하지 않는다. 필요하면 Console에서 직접 켤 수 있다.

## 화면 버튼

배지 위쪽에는 작은 토글 버튼이 별도로 표시된다.

| 버튼 | 동작 |
| --- | --- |
| hide MD | 배지를 접는다. 버튼은 배지 상단 정가운데 탭 위치에 남는다. |
| show MD | 접힌 배지를 다시 펼친다. |

배지 내부 버튼은 다음 역할을 가진다.

| 버튼 | 동작 |
| --- | --- |
| refresh | 게임 데이터를 다시 받지 않고, 현재 런타임 상태/개수만 다시 읽어 배지 표시를 갱신한다. |
| auto | auto 모드로 전환 후 새로고침한다. 현재 적용 중이면 초록색 활성 상태로 보인다. |
| static | 기존 JS 데이터 모드로 전환 후 새로고침한다. 현재 적용 중이면 초록색 활성 상태로 보인다. |

`refresh`는 백엔드 API를 다시 호출하는 버튼이 아니다. `enableBackendMasterDataMode()`, `useStaticMasterDataMode()`, API fallback, 자동 부팅 상태 변화 뒤에 배지 표시만 바로 다시 읽고 싶을 때 사용한다. 배지가 5초마다 자동 갱신되므로 평소에는 눌러도 큰 변화가 없어 보일 수 있다. v097부터 `updated` 시간이 표시되어 refresh 동작을 확인할 수 있다.

## Console 함수

화면 버튼을 사용할 수 없는 상황을 대비해 기존 Console 함수도 유지한다.

```js
refreshBackendMasterDataDevBadge();
showBackendMasterDataDevBadge();
hideBackendMasterDataDevBadge();
toggleBackendMasterDataDevBadge();
```

숨김 상태는 `localStorage`에 저장된다. 그래서 새로고침해도 계속 숨겨질 수 있다. 다시 보이게 하려면 화면의 `show MD` 버튼이나 Console의 `showBackendMasterDataDevBadge()`를 사용한다.

## 상태 의미

| state | 의미 |
| --- | --- |
| applied | 백엔드 master-data 적용 성공 |
| backend_auto_waiting_for_page_load | 페이지 로드 후 백엔드 데이터를 적용할 예정 |
| loading | 백엔드 master-data 요청 중 |
| static_js_mode | 기존 JS 데이터 사용 중 |
| failed_fallback_to_static_js | 백엔드 요청 실패 후 기존 JS 데이터로 fallback |

## 배지 위치

배지는 `#bottom-hud` 내부에 붙는다. 위치는 중앙 능력치 패널의 오른쪽이며, 왼쪽 프로필 사진과 반대편이다. `hide MD` / `show MD` 토글은 MASTER DATA 인터페이스 상단 정가운데에 탭처럼 붙어 인터페이스가 접히고 펼쳐지는 느낌으로 동작한다. 작은 화면에서는 오른쪽 위로 이동해 다른 HUD 요소와 겹침을 줄인다.

## 주의

이 배지는 개발 편의 도구이며 게임 데이터 자체를 변경하지 않는다. master-data 적용/전환은 기존 runtime switch와 boot policy가 담당한다.

---

## 원본: `docs/archive/stage-notes/MASTER_DATA_FIELD_ZONE_ASSET_FALLBACK.md`

# Master-data field zone asset fallback

## 목적

`/api/v1/game/master-data`의 기본 응답은 백신 오탐과 응답 크기를 줄이기 위해 긴 `data:image/...` 문자열을 제외합니다.
이 정책 자체는 유지하되, 백엔드 master-data 자동 적용 후 필드존 이미지가 `undefined`가 되어 브라우저가 `file:///.../undefined`를 요청하지 않도록 방어합니다.

## v094 변경 내용

- `src/api/master-data-adapter.js`
  - API field zone을 legacy 구조로 변환할 때 `img`, `hasImage` 필드를 명시합니다.
- `src/api/master-data-runtime-switch.js`
  - 백엔드 master-data 모드에서 `fieldZones`의 누락된 `img` 값을 기존 정적 `zones` 데이터에서 보정합니다.
  - `undefined` 문자열도 누락 asset으로 처리합니다.
- `src/ui/render-ui.js`
  - 최후 방어선으로 `field.img`가 없거나 `"undefined"` 문자열이면 `placehold.co` 기본 이미지를 사용합니다.

## 확인 방법

위치: 프로젝트 루트

```bash
node tools/smoke/game/smoke_field_zone_asset_fallback.js
node tools/smoke/game/smoke_master_data_runtime_switch.js
```

브라우저 Console:

```js
runBackendMasterDataBrowserChecklist();
```

정상이라면 `renderFieldZone()` 실행 중 `file:///.../undefined` 이미지 요청이 발생하지 않아야 합니다.

---

## 원본: `docs/archive/stage-notes/MASTER_DATA_NESTED_ASSET_CLEANUP.md`

# Master Data Nested Asset Cleanup

`v084`는 `v083`에서 발견된 남은 asset 문제를 보정합니다.

## 문제

`v083`에서는 `/api/v1/game/master-data` 기본 응답에서 아래 최상위 필드를 `null`로 바꿨습니다.

```txt
characters.imageUrl
skills.iconUrl
itemTemplates.iconUrl
bosses.imageUrl
```

하지만 seed 데이터에는 `options`, `conditions`, `rules`, `raw` 같은 중첩 JSON 안에도 아래와 같은 긴 data URL이 남아 있을 수 있습니다.

```txt
data:image/svg+xml;charset=UTF-8,%3Csvg...
```

그래서 기본 응답 검사에서 여전히 백신 오탐 가능성이 있는 긴 문자열이 감지될 수 있었습니다.

## 수정

기본 응답에서는 중첩 JSON 안의 inline image data URL도 재귀적으로 `null`로 바꿉니다.

```txt
includeAssets=false  → 모든 중첩 data:image... 문자열 null 처리
includeAssets=true   → 모든 중첩 data:image... 문자열 그대로 포함
```

## 확인

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
python scripts/check_master_data_api.py
```

정상이면 다음처럼 출력됩니다.

```txt
master-data API check passed
```

asset 포함 응답도 확인하려면:

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
python scripts/check_master_data_api.py --include-assets
```

---

## 원본: `docs/archive/stage-notes/MASTER_DATA_NULLABLE_FIELDS.md`

# Master Data Nullable Fields

## v087 nullable skill proc rate fix

`skills.baseProcRate` from the generated seed can be missing/null for skills that do not use a base activation probability.

Previously the local seed importer converted a missing `baseProcRate` into `0`, so the API returned:

```json
{ "code": "lightsabre", "procRate": 0 }
```

The seed parity checker correctly reported this as different from the seed source:

```json
{ "code": "lightsabre", "baseProcRate": null }
```

From v087 onward, `skills.proc_rate` is nullable and the seed importer preserves `null` values. This keeps the DB/API master data aligned with the extracted JS seed data.

Run after applying this version:

```bash
# Location: backend folder with the virtual environment activated
python scripts/setup_dev_db.py --reset --seed --verify
python scripts/check_master_data_parity.py
```

---

## 원본: `docs/archive/stage-notes/MASTER_DATA_PARITY_CHECKER.md`

# Master Data Parity Checker

## 목적

`v086`은 현재 JS 마스터 데이터에서 추출한 seed JSON과 FastAPI `/api/v1/game/master-data` 응답이 같은지 비교하는 검증 도구를 추가한다.

이 단계의 목표는 아직 게임 화면을 API 데이터로 교체하는 것이 아니다. 먼저 아래 흐름이 기존 JS 데이터와 같은 내용을 유지하는지 확인한다.

```txt
src/data/*.js
→ tools/extract_seed_data.js
→ backend/seeds/generated/*.json
→ PostgreSQL
→ FastAPI /api/v1/game/master-data
```

## 추가 파일

```txt
backend/scripts/check_master_data_parity.py
tools/smoke/game/smoke_master_data_parity_checker.py
docs/archive/stage-notes/MASTER_DATA_PARITY_CHECKER.md
```

## 실행 전 준비

1. seed JSON 생성

위치: 프로젝트 루트

```bash
node tools/extract_seed_data.js
```

2. seed DB import

위치: backend 폴더 + 가상환경 activate 상태

```bash
source .venv/Scripts/activate
python scripts/setup_dev_db.py --reset --seed --verify
```

3. FastAPI 실행

위치: backend 폴더 + 가상환경 activate 상태

```bash
uvicorn app.main:app --reload
```

## parity 검사 실행

새 터미널에서 실행한다.

위치: backend 폴더 + 가상환경 activate 상태

```bash
source .venv/Scripts/activate
python scripts/check_master_data_parity.py
```

정상이라면 다음 문구가 나온다.

```txt
master-data parity check passed
```

## 이미지 포함 응답까지 비교

기본 master-data 응답은 백신 오탐과 응답 크기 문제를 줄이기 위해 긴 `data:image/...` 문자열을 제외한다.

정확한 이미지 문자열까지 비교하려면 아래처럼 실행한다.

위치: backend 폴더 + 가상환경 activate 상태

```bash
python scripts/check_master_data_parity.py --include-assets
```

이 경우 API 요청은 다음 주소로 나간다.

```txt
http://127.0.0.1:8000/api/v1/game/master-data?includeAssets=true
```

## 비교 항목

현재 비교하는 주요 항목은 다음과 같다.

```txt
counts
characters
characterSkills
skills
skillLevels
itemTemplates
bosses
fieldZones
dropTables
dropTableItems
enhancementGroups
enhancementLevels
```

각 항목은 개수뿐 아니라 code/id, 이름, 타입, 주요 숫자 값, 드랍 테이블 연결 관계 등도 함께 비교한다.

## 실패했을 때 보는 법

실패하면 아래처럼 JSON 리포트가 출력된다.

```json
{
  "ok": false,
  "failures": []
}
```

`failures` 안의 `area`를 보면 어느 영역에서 차이가 났는지 알 수 있다.

예시:

```txt
area: itemTemplates      아이템 템플릿 차이
area: bosses             보스 데이터 차이
area: dropTableItems     드랍 아이템 연결 차이
area: counts             전체 개수 차이
```

## 터미널 정적 검사

parity checker 파일이 존재하고 기본 구조가 있는지 확인하려면 아래를 실행한다.

위치: 프로젝트 루트

```bash
python tools/smoke/game/smoke_master_data_parity_checker.py
```

정상이라면 다음 문구가 나온다.

```txt
master-data parity checker smoke test passed
```

## 다음 단계

이 parity 검사가 통과하면 다음 단계에서 기존 JS 데이터와 API 데이터를 연결하는 어댑터를 만들 수 있다.

다음 단계 후보:

```txt
v087_master_data_runtime_adapter
```

이후에는 브라우저 게임이 기존 `src/data/*.js` 정적 데이터 대신 API master-data snapshot을 읽을 수 있도록 점진 전환한다.


### v087 note

`lightsabre`처럼 기본 발동확률이 없는 스킬은 `procRate: null`로 유지합니다. `python scripts/setup_dev_db.py --reset --seed --verify`를 다시 실행해야 DB에 반영됩니다.

---

## 원본: `docs/archive/stage-notes/MASTER_DATA_RUNTIME_SWITCH.md`

# Master Data Runtime Switch

## 목적

`v089`는 FastAPI `/api/v1/game/master-data` 응답을 실제 브라우저 런타임 데이터에 주입할 수 있는 ON/OFF 스위치를 추가한다.

기본값은 반드시 OFF다.

```txt
OFF: 기존 정적 JS 데이터로 게임 실행
ON: 페이지 시작 전에 FastAPI master-data를 불러와 기존 전역 데이터 내부를 교체한 뒤 게임 실행
```

## 왜 바로 ON으로 바꾸지 않는가

아직은 마이그레이션 검증 단계다. API 데이터가 기존 JS 데이터와 같다는 parity 검사는 통과했지만, 실제 게임 루프와 UI가 API 변환 데이터를 완전히 문제없이 쓰는지는 브라우저에서 단계적으로 확인해야 한다.

따라서 기본 실행은 기존 방식으로 유지하고, 개발자도구에서만 ON/OFF를 제어한다.

## 사용법

### API 데이터 모드 켜기

위치: 브라우저 개발자도구 Console

```js
enableBackendMasterDataMode();
```

명령 실행 후 페이지가 자동 새로고침된다.

### 상태 확인

위치: 브라우저 개발자도구 Console

```js
await checkBackendMasterDataRuntimeMode();
```

정상 적용 시 `state`가 `applied` 또는 `applied_with_missing_targets`로 표시된다.

### API 데이터 모드 끄기

위치: 브라우저 개발자도구 Console

```js
disableBackendMasterDataMode();
```

명령 실행 후 페이지가 자동 새로고침된다.

## 적용 대상

현재 런타임에서 교체하는 대상은 다음과 같다.

```txt
characterMasterData
skillMasterData
bossList
specialBossList
zones
```

top-level `const` 자체를 재할당하지 않고, 객체/배열 내부만 교체한다.

## asset 정책

실제 게임 화면에는 아이콘/보스 이미지가 필요하므로, 런타임 ON 모드에서는 `includeAssets=true`로 master-data를 요청한다.

기본 API 확인 주소 `/api/v1/game/master-data`는 여전히 asset을 제외한다. 백신 오탐 가능성이 있는 긴 SVG data URL은 명시적으로 런타임 ON 모드를 켰을 때만 브라우저가 받아온다.

## 실패 시 동작

API 서버가 꺼져 있거나 adapter 검증이 실패하면 게임은 기존 정적 JS 데이터로 계속 실행된다.

상태값은 다음처럼 남는다.

```txt
failed_fallback_to_static_js
```

이 경우 FastAPI 서버와 `/api/v1/game/master-data` 응답을 먼저 확인한다.

---

## 원본: `docs/archive/stage-notes/MASTER_DATA_RUNTIME_VALIDATOR.md`

# Master Data Runtime Validator

`v090`에서는 백엔드 master-data 런타임 모드를 브라우저에서 켰을 때 실제 게임 전역 데이터와 핵심 DOM이 깨지지 않았는지 확인하는 검증 도구를 추가했습니다.

## 목적

`v089`까지는 백엔드 master-data를 기존 전역 데이터에 주입할 수 있는 스위치가 추가되었습니다.

`v090`은 그 다음 안전장치입니다.

```txt
백엔드 master-data 모드 ON
→ API 데이터 주입
→ 기존 전역 데이터 개수 확인
→ 핵심 DOM 존재 확인
→ 보스/필드/스킬 샘플 확인
```

이 검증은 게임 로직을 바꾸지 않습니다. 브라우저 Console에서 상태를 확인하는 용도입니다.

## 추가 파일

```txt
src/api/master-data-runtime-validator.js
tools/smoke/game/smoke_master_data_runtime_validator.js
docs/archive/stage-notes/MASTER_DATA_RUNTIME_VALIDATOR.md
```

## 정적 검사

위치: **프로젝트 루트**

```bash
node tools/smoke/game/smoke_master_data_runtime_validator.js
```

정상 결과:

```txt
master-data runtime validator smoke test passed
```

## 브라우저 검증 순서

먼저 FastAPI 서버를 켭니다.

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
source .venv/Scripts/activate
uvicorn app.main:app --reload
```

게임 화면을 열고 개발자도구 Console에서 백엔드 모드를 켭니다.

위치: **브라우저 개발자도구 Console**

```js
enableBackendMasterDataMode();
```

페이지가 자동 새로고침됩니다.

새로고침이 끝난 뒤 Console에서 확인합니다.

```js
checkBackendMasterDataRuntimeIntegrity({ requireBackendMode: true });
```

정상이라면 `ok: true`와 함께 아래 상태가 나옵니다.

```txt
runtimeState: "applied"
```

또는 일부 대상이 없지만 치명적이지 않은 경우:

```txt
runtimeState: "applied_with_missing_targets"
```

## 확인하는 항목

### 1. 데이터 개수

최소 기준은 다음과 같습니다.

```txt
characters >= 1
skills >= 8
itemTemplates >= 245
normalBosses >= 39
specialBosses >= 6
fieldZones >= 40
```

### 2. 런타임 상태

`requireBackendMode: true` 옵션을 주면 백엔드 master-data 모드가 실제로 적용됐는지도 검사합니다.

```txt
applied
applied_with_missing_targets
```

위 상태가 아니면 실패로 봅니다.

### 3. 핵심 DOM

게임 화면의 핵심 DOM이 존재하는지 확인합니다.

```txt
battle-zone
enemy-image-placeholder
enemy-name
enemy-hp-bar
enemy-hp-text
field-info-panel
boss-info-panel
char-panel
inventory-container
player-gold
boss-grid
special-boss-grid
field-list-container
```

### 4. 샘플 데이터

검사 결과에 다음 샘플도 포함됩니다.

```txt
firstNormalBoss
firstSpecialBoss
firstZone
lightsabreProcRate
```

`lightsabreProcRate`는 `null`이어야 합니다.

## 디버그 스냅샷

현재 상태만 간단히 보고 싶으면 Console에서 실행합니다.

```js
getBackendMasterDataRuntimeDebugSnapshot();
```

## 백엔드 모드 끄기

위치: **브라우저 개발자도구 Console**

```js
disableBackendMasterDataMode();
```

페이지가 새로고침되고 기존 정적 JS 데이터 모드로 돌아갑니다.

## 다음 단계: 브라우저 체크리스트

`v091`부터는 `runBackendMasterDataBrowserChecklist()`로 보스/필드/장비지급/인벤토리 렌더링 상태까지 한 번에 확인할 수 있습니다. 자세한 내용은 `docs/guides/MASTER_DATA_BROWSER_CHECKLIST.md`를 참고하세요.

---

## 원본: `docs/archive/stage-notes/SEED_EXTRACTION.md`

# JS 마스터 데이터 Seed 추출

## 목적

현재 게임의 마스터 데이터는 아직 브라우저 JavaScript 파일에 있습니다.

```txt
src/data/bosses.js
src/data/zones.js
src/data/skills.js
src/systems/stat-system.js
```

백엔드/PostgreSQL로 이전하려면 이 데이터를 사람이 손으로 옮기지 않고, 먼저 JSON seed 초안으로 추출해야 합니다.

## 실행 명령어

프로젝트 루트에서 실행합니다.

```bash
node tools/extract_seed_data.js
node tools/smoke/game/smoke_seed_extraction.js
```

## 출력 파일

```txt
backend/seeds/generated/characters.json
backend/seeds/generated/skills.json
backend/seeds/generated/skill_books.json
backend/seeds/generated/bosses.json
backend/seeds/generated/field_zones.json
backend/seeds/generated/item_templates.json
backend/seeds/generated/drop_tables.json
backend/seeds/generated/drop_table_items.json
backend/seeds/generated/enhancement_rules.json
backend/seeds/generated/manifest.json
```

## 현재 추출 기준

```txt
characters: 캐릭터 마스터 데이터
skills: 스킬 마스터 데이터
skill_books: 스킬강화권 매핑
bosses: 일반/특수 보스 마스터 데이터
field_zones: 필드존 마스터 데이터
item_templates: 드랍 아이템 원본 후보
drop_tables: 보스별 드랍 테이블 후보
drop_table_items: 보스별 드랍 아이템/확률 후보
enhancement_rules: 일반 장비 강화 테이블/확률 초안
```

## 아직 DB에 바로 넣지 않는 이유

현재 seed는 PostgreSQL 테이블에 넣기 전 단계입니다. 다음 작업에서 아래를 추가해야 합니다.

```txt
1. SQLAlchemy 모델과 seed JSON 필드 매칭
2. Alembic 마이그레이션 적용
3. seed import 스크립트 작성
4. /game/master-data API에서 DB 값을 읽도록 연결
```

## 관리자 페이지 요구사항과의 관계

관리자 페이지에서 수정해야 하는 값은 seed와 DB에 반드시 존재해야 합니다.

예:

```txt
보스 HP
드랍률
아이템 옵션
스킬 계수
강화 확률
필드 보상
캐릭터별 스킬 구성
```

관련 문서:

```txt
docs/archive/stage-notes/ADMIN_REQUIREMENTS_V1.md
docs/archive/stage-notes/DB_SCHEMA_DRAFT.md
docs/archive/stage-notes/BACKEND_API_ROUTES_DRAFT.md
```

---

## 원본: `docs/archive/stage-notes/SEED_IMPORT.md`

# Seed Import Guide

이 문서는 현재 JS 마스터 데이터를 PostgreSQL 로컬 DB에 넣는 절차를 설명합니다.

## 목적

`tools/extract_seed_data.js`가 생성한 JSON 파일을 PostgreSQL 테이블에 넣어, 이후 FastAPI의 `/game/master-data` API와 관리자 페이지 개발에서 사용할 수 있게 합니다.

## 실행 전 준비

아래가 끝나 있어야 합니다.

- Docker Desktop 실행 중
- `docker compose up -d`로 `upgrade_rpg_postgres` 컨테이너 실행 중
- `backend/.env` 생성 완료
- FastAPI 패키지 설치 완료

## 명령어 위치 규칙

- JS seed 추출 도구는 **프로젝트 루트**에서 실행합니다.
- DB import 스크립트는 **backend 폴더**에서 실행합니다.

## 1. seed JSON 다시 생성

위치: **프로젝트 루트**

```bash
node tools/extract_seed_data.js
node tools/smoke/game/smoke_seed_extraction.js
```

생성 위치:

```txt
backend/seeds/generated/
```

## 2. import 전 dry-run 확인

위치: **backend 폴더**

```bash
python scripts/setup_dev_db.py --dry-run
```

이 명령은 DB에 접근하지 않고 seed JSON 개수만 확인합니다.

## 3. 로컬 DB 초기화 + 테이블 생성 + seed import

위치: **backend 폴더**

```bash
python scripts/setup_dev_db.py --reset --seed --verify
```

주의:

```txt
--reset은 로컬 PostgreSQL public schema를 삭제 후 다시 만듭니다.
개발용 DB에서만 사용하세요.
```

## 4. 기존 데이터를 유지하면서 테이블만 만들기

위치: **backend 폴더**

```bash
python scripts/setup_dev_db.py --create-schema
```

## 5. seed만 다시 넣기

위치: **backend 폴더**

```bash
python scripts/setup_dev_db.py --seed --verify
```

## 현재 import 대상

- characters
- skills
- character_skills
- skill_levels
- item_templates
- bosses
- field_zones
- drop_tables
- drop_table_items
- enhancement_groups
- enhancement_levels
- admin_roles

## 큰 숫자 처리

현재 게임은 HP/골드가 매우 큰 값까지 올라갑니다. 그래서 DB 초안의 HP/골드/강화비용 계열 컬럼은 `INTEGER`가 아니라 `NUMERIC(40,0)`을 사용하도록 보정했습니다.


## 연결 오류가 날 때

만약 `--reset --seed --verify` 실행 중 아래 오류가 나오면:

```txt
asyncpg.exceptions.ConnectionDoesNotExistError: connection was closed in the middle of operation
```

`v079`부터 seed import 스크립트는 동기식 `psycopg` 방식으로 변경되어 이 문제를 피하도록 되어 있습니다.

이미 가상환경을 만든 상태라면 먼저 아래를 설치하세요.

위치: **backend 폴더**

```bash
pip install "psycopg[binary]"
```

그 다음 다시 실행합니다.

위치: **backend 폴더**

```bash
python scripts/setup_dev_db.py --reset --seed --verify
```


## 긴 이미지/아이콘 URL 처리

현재 seed에는 SVG `data:image` URL이 들어갈 수 있습니다. 일반 URL보다 길기 때문에 이미지/아이콘 컬럼은 `VARCHAR(500)`이 아니라 `TEXT` 타입을 사용합니다.

관련 컬럼:

- `characters.image_url`
- `skills.icon_url`
- `item_templates.icon_url`
- `bosses.image_url`

만약 아래 오류가 나오면 v082 이상 ZIP을 적용한 뒤 `--reset --seed --verify`를 다시 실행하세요.

```txt
value too long for type character varying(500)
```

자세한 내용은 `docs/archive/stage-notes/SEED_IMPORT_LONG_ASSET_FIX.md`를 참고하세요.

## 다음 단계

seed import가 성공하면 다음 단계는 `/game/master-data` API가 DB에서 실제 데이터를 읽어오게 만드는 작업입니다.


> 로컬 PostgreSQL은 기본 포트 `5432`가 아니라 `55432`를 사용한다. Windows에서 기존 PostgreSQL과 충돌을 피하기 위한 프로젝트 기준이다. 자세한 내용은 `docs/archive/stage-notes/LOCAL_DB_PORT_POLICY.md`를 참고한다.

---

## 원본: `docs/archive/stage-notes/SEED_IMPORT_CONNECTION_FIX.md`

# Seed Import Connection Fix

## 배경

Windows + Docker Desktop 환경에서 `python scripts/setup_dev_db.py --reset --seed --verify` 실행 중 아래 오류가 발생할 수 있었습니다.

```txt
asyncpg.exceptions.ConnectionDoesNotExistError: connection was closed in the middle of operation
```

FastAPI의 `/api/v1/health/db`는 정상인데 seed import에서만 끊기는 경우, 앱 실행용 async DB 연결 문제가 아니라 **로컬 DB 초기화/대량 seed import 스크립트가 asyncpg로 동작하면서 생기는 안정성 문제**에 가깝습니다.

## 변경 사항

`backend/scripts/setup_dev_db.py`를 동기식 SQLAlchemy + `psycopg` 드라이버 방식으로 변경했습니다.

- FastAPI 앱: 기존처럼 `postgresql+asyncpg://...` 사용 가능
- 로컬 seed import 스크립트: 내부에서 `postgresql+psycopg://...`로 변환해 사용

## 실행 위치

위치: **backend 폴더**

```bash
python scripts/setup_dev_db.py --reset --seed --verify
```

## 의존성

새 가상환경에서는 아래 명령어로 설치합니다.

위치: **backend 폴더**

```bash
pip install -e .[dev]
```

이미 가상환경을 만든 상태라면 아래만 추가로 설치해도 됩니다.

위치: **backend 폴더**

```bash
pip install "psycopg[binary]"
```

---

## 원본: `docs/archive/stage-notes/SEED_IMPORT_LONG_ASSET_FIX.md`

# Seed Import 긴 이미지/아이콘 URL 수정

## 문제

`python scripts/setup_dev_db.py --reset --seed --verify` 실행 중 아래 오류가 날 수 있었습니다.

```txt
psycopg.errors.StringDataRightTruncation: value too long for type character varying(500)
```

원인은 `item_templates.icon_url`에 들어가는 SVG `data:image` 문자열이 500자를 넘는 경우가 있기 때문입니다.
기존 DB 초안은 이미지/아이콘 URL을 일반 URL 정도로 보고 `VARCHAR(500)`으로 잡았지만, 현재 게임 seed에는 SVG data URL이 포함됩니다.

## 수정

아래 컬럼을 `TEXT` 타입으로 변경했습니다.

- `characters.image_url`
- `skills.icon_url`
- `item_templates.icon_url`
- `bosses.image_url`

로컬 개발 DB에서는 `--reset`을 다시 실행하면 새 타입으로 테이블이 생성됩니다.

## 다시 실행

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
source .venv/Scripts/activate
python scripts/setup_dev_db.py --reset --seed --verify
```

정상이면 `item_templates`가 245개로 들어가야 합니다.

## SQL 로그

긴 SVG data URL 때문에 seed import SQL 로그가 너무 길어지는 문제가 있어, `setup_dev_db.py`는 기본적으로 SQL 원문을 출력하지 않습니다.

정말 SQL 로그가 필요할 때만 아래처럼 실행합니다.

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
python scripts/setup_dev_db.py --reset --seed --verify --verbose-sql
```
