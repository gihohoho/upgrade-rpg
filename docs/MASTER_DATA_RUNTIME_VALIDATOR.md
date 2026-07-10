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
docs/MASTER_DATA_RUNTIME_VALIDATOR.md
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

`v091`부터는 `runBackendMasterDataBrowserChecklist()`로 보스/필드/장비지급/인벤토리 렌더링 상태까지 한 번에 확인할 수 있습니다. 자세한 내용은 `docs/MASTER_DATA_BROWSER_CHECKLIST.md`를 참고하세요.
