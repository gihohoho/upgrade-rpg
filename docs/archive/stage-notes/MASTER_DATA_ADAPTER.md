# Master Data Adapter

## 목적

`GET /api/v1/game/master-data` 응답을 기존 브라우저 게임 코드가 쓰던 데이터 구조에 가까운 형태로 변환하는 준비 단계입니다.

이번 단계에서는 실제 게임 런타임을 API 데이터로 교체하지 않습니다. 기존 게임 동작은 그대로 유지하고, 브라우저 콘솔/테스트 도구로만 변환 결과를 확인합니다.

## 추가 파일

```txt
src/api/master-data-adapter.js
tools/smoke/game/smoke_master_data_adapter.js
docs/MASTER_DATA_ADAPTER.md
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
