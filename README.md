# Upgrade RPG v195 패키지

현재 안정 버전: **v195 admin thin entry cleanup**

새 채팅 인수인계 ZIP: **rpg_v195_admin_thin_entry_cleanup_ready.zip**

## 요약

v195에서는 `admin-page-readonly.js`를 마지막 연결 파일처럼 유지하면서, 내부 흐름을 더 얇게 정리했습니다.

새 기능 이동보다는 아래 안정화에 집중했습니다.

- click action 처리 중앙화
- window export 등록 묶음화
- 외부 관리자 모듈 configure 순서 묶음화
- thin entry readiness 추가
- 기존 `data-admin-action` 값과 기존 window 함수명 유지

## 현재 관리자 JS 분리 상태

- `src/api/game-api-client.js` — 기존 외부 API client
- `src/api/admin-layout-shell.js` — v185 분리 완료
- `src/api/admin/admin-change-logs.js` — v187 분리 완료
- `src/api/admin/admin-create-lifecycle.js` — v189.1 hotfix 포함 분리 완료
- `src/api/admin/admin-edit-draft.js` — v191 분리 완료
- `src/api/admin/admin-master-catalog.js` — v192 분리 완료
- `src/api/admin/admin-overview-snapshots.js` — v193 분리 완료
- `src/api/admin-page-readonly.js` — v195 기준 thin entry cleanup 완료

## v195에서 정리한 것

- `getAdminClickActionHandlers()` 추가
- `handleAdminClickAction()` 추가
- `registerAdminReadOnlyPageExports()` 추가
- `configureAdminExternalModules()` 추가
- `getAdminThinEntryCleanupReadiness()` 추가
- `renderAdminThinEntryCleanupReadiness()` 추가
- `checkAdminReadOnlyPageReady().thinEntryCleanupReady` 추가
- `tools/smoke_admin_thin_entry_cleanup.js` 추가

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().version
```

예상값:

```txt
v195.admin-thin-entry-cleanup
```

```js
checkAdminReadOnlyPageReady().thinEntryCleanupReady
```

예상값:

```txt
true
```

```js
getAdminThinEntryCleanupReadiness().status
```

예상값:

```txt
cleaned-v195
```

## 검증

- `bash tools/run_smoke_core.sh` 통과
- `bash tools/run_smoke_all.sh` 통과
- `node --check src/api/admin-page-readonly.js` 통과
- `python -m compileall -q backend/app` 통과

## DB / env

- DB reset 필요 없음
- seed 재실행 필요 없음
- DB schema 변경 없음
- `.env`, `.gitignore` 변경 없음
