# Admin Overview/Snapshots Split

버전: **v193 admin overview/snapshots split**

## 추가 파일

- `src/api/admin/admin-overview-snapshots.js`

## 이동한 기능

- overview cards 렌더링
- save snapshot 필터 read/reset/describe
- save snapshot table 렌더링
- readiness 카드 렌더링

## 유지한 호환성

`admin-page-readonly.js`에는 기존 함수명 wrapper를 유지했습니다.

- `readSnapshotFiltersFromDom`
- `resetSnapshotFilters`
- `describeSnapshotFilters`
- `renderCards`
- `renderSnapshotTable`
- `renderReadiness`

## 확인

```js
checkAdminReadOnlyPageReady().overviewSnapshotsExternalReady
window.RpgAdminOverviewSnapshots.VERSION
```
