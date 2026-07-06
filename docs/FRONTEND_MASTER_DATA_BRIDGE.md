# Frontend Master Data Bridge

## 목적

`v085`는 현재 HTML/JS 게임을 바로 DB 데이터로 교체하지 않고, 브라우저에서 FastAPI master-data API를 안전하게 읽어올 수 있는 준비층을 추가한다.

현재 게임 동작은 기존 JS 데이터 기준으로 그대로 유지한다. 이 단계는 다음 단계에서 `src/data/*.js`의 정적 데이터를 API 데이터로 대체하기 위한 연결 확인 단계다.

## 추가 파일

```txt
src/api/game-api-client.js
src/api/master-data-bridge.js
tools/smoke_frontend_master_data_bridge.js
```

## 브라우저 전역 객체

브라우저 콘솔에서 아래 객체와 함수를 사용할 수 있다.

```txt
RpgGameApi
RpgMasterDataBridge
checkBackendMasterData()
loadBackendMasterData()
getCachedBackendMasterData()
```

## 기본 API 주소

기본 API 주소는 다음과 같다.

```txt
http://127.0.0.1:8000/api/v1
```

변경이 필요하면 브라우저 콘솔에서 아래처럼 설정할 수 있다.

```js
RpgGameApi.setApiBaseUrl("http://127.0.0.1:8000/api/v1");
```

설정값은 `localStorage`의 아래 키에 저장된다.

```txt
upgradeRpgApiBaseUrl
```

## 브라우저에서 확인하기

FastAPI 서버를 켠 뒤, 게임 화면을 브라우저에서 열고 개발자도구 콘솔에서 실행한다.

```js
await checkBackendMasterData();
```

정상이라면 콘솔에 다음 로그가 나온다.

```txt
[Upgrade RPG] master-data API check passed
```

이미지 data URL까지 포함해서 확인하려면 아래를 실행한다.

```js
await checkBackendMasterData({ includeAssets: true });
```

## 터미널 정적 검사

위치: 프로젝트 루트

```bash
node tools/smoke_frontend_master_data_bridge.js
```

정상이라면 다음 문구가 나온다.

```txt
frontend master-data bridge smoke test passed
```

## 주의

이 단계에서는 아직 게임 화면이 API 데이터를 사용하지 않는다. 기존 게임 동작 안정성을 위해 API 데이터는 `window.backendMasterDataSnapshot`에만 저장한다.

다음 단계에서 이 snapshot과 기존 `src/data/*.js` 데이터의 차이를 비교하고, 안전하게 전환할 수 있는 어댑터를 만든다.
