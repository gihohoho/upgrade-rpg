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
