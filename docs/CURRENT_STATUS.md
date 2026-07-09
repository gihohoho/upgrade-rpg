# Current Status

현재 기준: **v193 admin overview/snapshots split**

이 패키지 기준 ZIP: **rpg_v193_admin_overview_snapshots_split_ready.zip**

## 완료된 관리자 JS 분리

- v185: layout shell 분리
- v187: change logs 분리
- v189.1: create lifecycle 분리 + helper export hotfix
- v191: edit draft 분리
- v192: master catalog/detail 분리
- v193: overview/snapshots 분리

## v193 완료 내용

- `src/api/admin/admin-overview-snapshots.js` 추가
- overview cards 렌더링 이동
- save snapshot 필터 read/reset/describe 이동
- save snapshot table 렌더링 이동
- readiness 카드 렌더링 이동
- `admin-page-readonly.js`에는 기존 함수명 wrapper 유지
- `admin.html` script 순서 갱신
- overview/snapshots split smoke 추가

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().version
checkAdminReadOnlyPageReady().overviewSnapshotsExternalReady
window.RpgAdminOverviewSnapshots.VERSION
```

예상:

```txt
v193.admin-overview-snapshots-split
true
v193.admin-overview-snapshots-split
```

## DB / env

- DB reset 필요 없음
- seed 재실행 필요 없음
- DB schema 변경 없음
- `.env`, `.gitignore` 변경 없음
