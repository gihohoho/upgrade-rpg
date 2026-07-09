# NEXT CHAT HANDOFF — v197

기호는 코딩/터미널/경로에 익숙하지 않으므로, 명령어는 항상 실행 위치를 먼저 적습니다.

## 현재 안정 버전

**v197 admin settings/helpers split**

## 현재 ZIP

**rpg_v197_admin_settings_helpers_split_ready.zip**

## v197 완료

- `src/api/admin/admin-settings-helpers.js` 추가
- API base URL helper 분리
- admin write dev key helper 분리
- 현재 관리자 페이지 URL / 게임 URL / 주소 복사 helper 분리
- 기존 window 함수명 유지
- `admin.html` script 순서 갱신
- `checkAdminReadOnlyPageReady().settingsHelpersExternalReady` 추가
- `window.RpgAdminSettingsHelpers.VERSION` 추가
- `tools/smoke_admin_settings_helpers_split.js` 추가
- 기존 URL helper smoke도 새 분리 구조에 맞게 갱신
- core/all smoke 통과

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().version
```

예상:

```txt
v197.admin-settings-helpers-split
```

```js
checkAdminReadOnlyPageReady().settingsHelpersExternalReady
```

예상:

```txt
true
```

```js
window.RpgAdminSettingsHelpers.VERSION
```

예상:

```txt
v197.admin-settings-helpers-split
```

## 다음 추천 단계

v198은 **admin entry final cleanup / backend admin service split 준비**가 좋습니다.

추천 방향:

- `admin-page-readonly.js`에 남은 entry 역할 확인
- 불필요한 legacy marker/중복 export 정리 가능 범위 점검
- 또는 백엔드 `admin_service.py`가 커졌다면 service split contract부터 진행
- 기존 window 함수명은 유지
- 전용 smoke 추가

## 주의

v197은 DB schema/env 변경이 없습니다. DB reset/seed 재실행도 필요 없습니다.
