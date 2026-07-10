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
