# Admin Settings Helpers Split

v197에서는 관리자 페이지의 settings/helper 계열 기능을 외부 JS 파일로 분리했습니다.

## 추가 파일

- `src/api/admin/admin-settings-helpers.js`

## 분리 범위

- `getCurrentAdminPageUrl()`
- `getGamePageUrl()`
- `syncLocationHints()`
- `copyCurrentAdminPageUrl()`
- `syncApiInput()`
- `saveApiBaseUrlFromInput()`
- `resetApiBaseUrl()`
- `syncAdminWriteDevKeyInput()`
- `saveAdminWriteDevKeyFromInput()`
- `clearAdminWriteDevKey()`
- `requireAdminWriteDevKeyForUi()`

## 호환 유지

기존 window 함수명은 `admin-page-readonly.js` wrapper를 통해 그대로 유지했습니다.

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().settingsHelpersExternalReady
window.RpgAdminSettingsHelpers.VERSION
```

예상:

```txt
true
v197.admin-settings-helpers-split
```

## 검증

- `tools/smoke/frontend/smoke_admin_settings_helpers_split.js`
- `bash tools/run_smoke_core.sh`
- `bash tools/run_smoke_all.sh`

## DB / env

DB reset/seed는 필요 없습니다.
