# Current Status

현재 기준: **v197 admin settings/helpers split**

이 패키지 기준 ZIP: **rpg_v197_admin_settings_helpers_split_ready.zip**

## 완료된 관리자 JS 분리/정리

- v185: layout shell 분리
- v187: change logs 분리
- v189.1: create lifecycle 분리 + helper export hotfix
- v191: edit draft 분리
- v192: master catalog/detail 분리
- v193: overview/snapshots 분리
- v194: bootstrap/bindEvents thin entry 계약 고정
- v195: thin entry cleanup
- v196: field help/value hints/equip slot label 분리
- v197: settings helpers/API URL/write key/page URL helper 분리

## v197 완료 내용

- `src/api/admin/admin-settings-helpers.js` 추가
- API base URL helper 외부 파일 이동
- admin write dev key helper 외부 파일 이동
- 현재 관리자 URL / 게임 URL / 주소 복사 helper 외부 파일 이동
- 기존 window 함수명 wrapper 유지
- `checkAdminReadOnlyPageReady().settingsHelpersExternalReady` 추가
- `tools/smoke_admin_settings_helpers_split.js` 추가

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().version
checkAdminReadOnlyPageReady().settingsHelpersExternalReady
window.RpgAdminSettingsHelpers.VERSION
```

예상:

```txt
v197.admin-settings-helpers-split
true
v197.admin-settings-helpers-split
```

## DB / env

- DB reset 필요 없음
- seed 재실행 필요 없음
- DB schema 변경 없음
- `.env`, `.gitignore` 변경 없음
