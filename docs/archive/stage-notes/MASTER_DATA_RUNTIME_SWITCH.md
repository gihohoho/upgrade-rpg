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
