# NEXT CHAT HANDOFF — v193

기호는 코딩/터미널/경로에 익숙하지 않으므로, 명령어는 항상 실행 위치를 먼저 적습니다.

## 현재 안정 버전

**v193 admin overview/snapshots split**

## 현재 ZIP

**rpg_v193_admin_overview_snapshots_split_ready.zip**

## v193 완료

- `src/api/admin/admin-overview-snapshots.js` 추가
- overview cards 렌더링 분리
- save snapshot 필터 read/reset/describe 분리
- save snapshot table 렌더링 분리
- readiness 카드 렌더링 분리
- 기존 window 함수명은 `admin-page-readonly.js` wrapper로 유지
- `admin.html` script 순서에 overview/snapshots 파일 추가
- `tools/smoke_admin_overview_snapshots_split.js` 추가
- core/all smoke 통과

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().version
```

예상:

```txt
v193.admin-overview-snapshots-split
```

```js
checkAdminReadOnlyPageReady().overviewSnapshotsExternalReady
```

예상:

```txt
true
```

```js
window.RpgAdminOverviewSnapshots.VERSION
```

예상:

```txt
v193.admin-overview-snapshots-split
```

## 다음 추천 단계

v194는 **admin bootstrap/bindEvents thin entry 정리**를 추천합니다.

추천 방향:

- `admin-page-readonly.js`에 남아있는 boot/bindEvents/window export를 마지막 entry 역할로 더 얇게 정리
- 바로 큰 파일 분리보다 먼저 event action map/boot readiness smoke 추가
- 안정적이면 v195에서 event handlers 일부를 별도 파일로 분리

## 주의

v193은 DB schema/env 변경이 없습니다. DB reset/seed 재실행도 필요 없습니다.
