# Upgrade RPG v193 패키지

현재 안정 버전: **v193 admin overview/snapshots split**

새 채팅 인수인계 ZIP: **rpg_v193_admin_overview_snapshots_split_ready.zip**

## 요약

v193에서는 관리자 `overview/snapshots` 구현을 실제 외부 JS 파일로 1차 분리했습니다.

새 파일:

- `src/api/admin/admin-overview-snapshots.js`

기존 호환 wrapper는 `src/api/admin-page-readonly.js`에 유지했습니다.

## 현재 관리자 JS 분리 상태

- `src/api/game-api-client.js` — 기존 외부 API client
- `src/api/admin-layout-shell.js` — v185 분리 완료
- `src/api/admin/admin-change-logs.js` — v187 분리 완료
- `src/api/admin/admin-create-lifecycle.js` — v189.1 hotfix 포함 분리 완료
- `src/api/admin/admin-edit-draft.js` — v191 분리 완료
- `src/api/admin/admin-master-catalog.js` — v192 분리 완료
- `src/api/admin/admin-overview-snapshots.js` — v193 분리 완료
- `src/api/admin-page-readonly.js` — bootstrap/bindEvents/window wrapper 중심 entry 파일

## v193에서 분리한 기능

- overview cards 렌더링
- save snapshot 필터 read/reset/describe
- save snapshot table 렌더링
- readiness 카드 렌더링

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().version
```

예상값:

```txt
v193.admin-overview-snapshots-split
```

```js
checkAdminReadOnlyPageReady().overviewSnapshotsExternalReady
```

예상값:

```txt
true
```

```js
window.RpgAdminOverviewSnapshots.VERSION
```

예상값:

```txt
v193.admin-overview-snapshots-split
```

## 검증

- `bash tools/run_smoke_core.sh` 통과
- `bash tools/run_smoke_all.sh` 통과
- `node --check` 주요 관리자 JS 통과
- `python -m compileall -q backend/app` 통과

## DB / env

- DB reset 필요 없음
- seed 재실행 필요 없음
- DB schema 변경 없음
- `.env`, `.gitignore` 변경 없음
