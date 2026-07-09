# Upgrade RPG v197 패키지

현재 안정 버전: **v197 admin settings/helpers split**

새 채팅 인수인계 ZIP: **rpg_v197_admin_settings_helpers_split_ready.zip**

## 요약

v197에서는 관리자 화면의 설정성 helper인 **API URL / admin write dev key / 현재 관리자 주소 / 게임 주소 / 주소 복사** 기능을 외부 JS 파일로 분리했습니다.

새 파일:

- `src/api/admin/admin-settings-helpers.js`

기존 화면 문구, 기존 버튼 action, 기존 window 함수명은 유지했습니다.

## 현재 관리자 JS 분리 상태

- `src/api/game-api-client.js` — 기존 외부 API client
- `src/api/admin-layout-shell.js` — v185 분리 완료
- `src/api/admin/admin-field-help.js` — v196 분리 완료
- `src/api/admin/admin-settings-helpers.js` — v197 분리 완료
- `src/api/admin/admin-change-logs.js` — v187 분리 완료
- `src/api/admin/admin-create-lifecycle.js` — v189.1 hotfix 포함 분리 완료
- `src/api/admin/admin-edit-draft.js` — v191 분리 완료
- `src/api/admin/admin-master-catalog.js` — v192 분리 완료
- `src/api/admin/admin-overview-snapshots.js` — v193 분리 완료
- `src/api/admin-page-readonly.js` — thin entry 유지

## v197에서 정리한 것

- `getCurrentAdminPageUrl()` 외부 모듈 wrapper 유지
- `getGamePageUrl()` 외부 모듈 wrapper 유지
- `syncLocationHints()` 외부 모듈 wrapper 유지
- `copyCurrentAdminPageUrl()` 외부 모듈 wrapper 유지
- `syncApiInput()` 외부 모듈 wrapper 유지
- `saveApiBaseUrlFromInput()` 외부 모듈 wrapper 유지
- `resetApiBaseUrl()` 외부 모듈 wrapper 유지
- `syncAdminWriteDevKeyInput()` 외부 모듈 wrapper 유지
- `saveAdminWriteDevKeyFromInput()` 외부 모듈 wrapper 유지
- `clearAdminWriteDevKey()` 외부 모듈 wrapper 유지
- `requireAdminWriteDevKeyForUi()` 외부 모듈 wrapper 유지
- `checkAdminReadOnlyPageReady().settingsHelpersExternalReady` 추가
- `tools/smoke_admin_settings_helpers_split.js` 추가

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().version
```

예상값:

```txt
v197.admin-settings-helpers-split
```

```js
checkAdminReadOnlyPageReady().settingsHelpersExternalReady
```

예상값:

```txt
true
```

```js
window.RpgAdminSettingsHelpers.VERSION
```

예상값:

```txt
v197.admin-settings-helpers-split
```

## 검증

- `bash tools/run_smoke_core.sh` 통과
- `bash tools/run_smoke_all.sh` 통과
- `node --check src/api/admin/admin-settings-helpers.js` 통과
- `node --check src/api/admin-page-readonly.js` 통과
- `python -m compileall -q backend/app` 통과

## DB / env

- DB reset 필요 없음
- seed 재실행 필요 없음
- DB schema 변경 없음
- `.env`, `.gitignore` 변경 없음
