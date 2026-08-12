# 저장 시스템 개발 역사

> 완료된 단계별 메모를 검색 가능한 한 파일로 통합한 읽기 전용 역사입니다.
> 현재 작업 판단에는 `docs/current/`와 루트 `NEXT_CHAT_HANDOFF.md`를 사용하세요.
> 원본 파일은 Git commit `270d57bd234ede18cee7168f4b5da36b1a08df18` 이전 이력에서 복원할 수 있습니다.

## 통합된 원본

- `docs/archive/stage-notes/SAVE_DATA_BADGE_RESTORE_ACTIONS.md`
- `docs/archive/stage-notes/SAVE_DATA_DEV_BADGE.md`
- `docs/archive/stage-notes/SAVE_DATA_DUAL_WRITE.md`
- `docs/archive/stage-notes/SAVE_DATA_INTEGRITY_VERIFY.md`
- `docs/archive/stage-notes/SAVE_DATA_PREVIEW_COMPARE.md`
- `docs/archive/stage-notes/SAVE_DATA_RESTORE_GUARD.md`
- `docs/archive/stage-notes/SAVE_DATA_RESTORE_RELOAD_LOCK.md`
- `docs/archive/stage-notes/SAVE_DATA_SLOT_LIST.md`
- `docs/archive/stage-notes/SAVE_SNAPSHOT_API.md`
- `docs/archive/stage-notes/USER_SAVE_MIGRATION_PLAN.md`

---

## 원본: `docs/archive/stage-notes/SAVE_DATA_BADGE_RESTORE_ACTIONS.md`

# Save Data Badge Restore Actions

v107 adds restore-related controls to the local development `SAVE DATA` badge.

## Goal

The restore preview was already available from the browser Console in v106. v107 makes the same safe flow reachable from the on-screen development badge, so the game owner can test save restore without typing Console commands.

Existing gameplay save behavior is unchanged:

```txt
Game save button
→ localStorage save remains the source used by the running game
→ backend DB save is attempted only in dual mode
→ backend restore still requires preview + backup + reload
```

## New SAVE DATA badge buttons

| Button | What it does |
|---|---|
| `preview` | Opens the DB save restore preview modal. It only compares `localStorage` and backend DB save data first. |
| `backup` | Restores the most recent pre-restore localStorage backup after browser confirmation. Reload is still required. |

The existing buttons remain:

| Button | What it does |
|---|---|
| `sync DB` | Pushes the current `localStorage` save to backend DB immediately. |
| `load DB` | Loads backend DB save data for inspection only. |
| `dual` | Enables manual save dual write. |
| `local` | Keeps manual save localStorage-only. |

## Modal additions

The restore preview modal now shows:

- a stronger reload warning,
- latest backup summary,
- `최근 백업으로 되돌리기` button,
- escaped preview values before inserting them into modal HTML.

## Safety notes

- No database reset is needed.
- No seed import is needed.
- Backend restore still does not mutate the live in-memory game state directly.
- Restore writes into `idleRpgSaveV22`, then the user must reload the page.
- Before DB restore, the existing local save is backed up automatically.

---

## 원본: `docs/archive/stage-notes/SAVE_DATA_DEV_BADGE.md`

# SAVE DATA 개발자 배지

v101에서 추가된 로컬 개발용 저장 상태 배지입니다.

## 목적

수동 저장 버튼을 눌렀을 때 기존 `localStorage` 저장뿐 아니라 백엔드 DB 저장까지 성공했는지 브라우저 화면에서 바로 확인하기 위한 도구입니다.

기존 게임 저장 구조는 그대로 유지됩니다.

```txt
수동 저장 버튼
→ localStorage 저장
→ 백엔드 DB 저장 시도
→ SAVE DATA 배지에 상태 표시
```

## 표시 위치

로컬 개발 환경에서 화면에 작은 `SAVE DATA` 배지가 표시됩니다.

대상 환경:

```txt
file://
localhost
127.0.0.1
```

## 표시 내용

```txt
SAVE DATA synced
mode: manual_dual slot: default
Lv:1 · G:100 · Inv:12 · Sto:3
loaded: loaded · v5
updated: 16:45:10 · saved: 16:45:08
```

주요 상태:

| state | 의미 |
|---|---|
| `synced` | 백엔드 DB 저장 성공 |
| `never_synced` | 아직 백엔드 저장을 한 적 없음 |
| `failed_fallback_to_local_storage` | 로컬 저장은 성공했지만 백엔드 저장 실패 |
| `skipped_local_only_mode` | localStorage 전용 모드라 백엔드 저장을 건너뜀 |

## 버튼 역할

| 버튼 | 역할 |
|---|---|
| `sync` | 현재 localStorage 저장값을 즉시 백엔드 DB에 저장 |
| `load` | 백엔드 DB에 저장된 세이브 스냅샷을 조회만 함. 아직 게임에 적용하지 않음 |
| `dual` | 수동 저장 시 localStorage와 백엔드 DB에 함께 저장 |
| `local` | 기존 방식처럼 localStorage에만 저장 |
| `hide SAVE` | 배지를 접음 |
| `show SAVE` | 접힌 배지를 다시 펼침 |

## Console 함수

브라우저 개발자도구 Console에서 사용할 수 있습니다.

```js
refreshBackendSaveDataDevBadge();
showBackendSaveDataDevBadge();
hideBackendSaveDataDevBadge();
toggleBackendSaveDataDevBadge();
```

저장 정책/상태 확인 함수는 v100에서 추가된 것을 그대로 사용합니다.

```js
getBackendSaveSyncPolicy();
getBackendSaveSyncStatus();
enableBackendSaveDualWrite();
disableBackendSaveDualWrite();
await syncLatestLocalSaveToBackend();
await loadBackendSaveSnapshot();
```

## 주의

`load` 버튼은 백엔드 저장값을 **조회만** 합니다.

아직 백엔드 저장값을 실제 게임 상태에 복원하지 않습니다. 복원 기능은 다음 단계에서 별도로 안전장치와 함께 추가합니다.

## v102: 기본 모드와 테스트 혼동 방지

v102부터 로컬 개발 환경에서 SAVE DATA 기본 모드는 `manual_dual`입니다.

v101 테스트 중 `local` 버튼을 누른 상태가 localStorage에 남아 있으면 다음 접속 때도 계속 local로 시작할 수 있었습니다. v102는 최초 적용 시 그 이전 local 상태를 한 번 `manual_dual`로 되돌립니다. 이후 사용자가 다시 `local` 버튼을 누르면 그 선택은 유지됩니다.

버튼 이름도 명확하게 바꿨습니다.

- `sync DB`: 현재 localStorage 저장값을 백엔드 DB로 즉시 전송합니다.
- `load DB`: 백엔드 DB 저장값을 조회만 합니다. 아직 게임에 적용하지 않습니다.
- `dual`: 성장/시스템 → 수동 저장 시 localStorage와 백엔드 DB에 함께 저장합니다.
- `local`: 성장/시스템 → 수동 저장 시 localStorage에만 저장합니다.

수동 저장에는 60초 쿨타임이 있습니다. 쿨타임 중 다시 누르면 실제 저장 로직이 실행되지 않기 때문에 DB 저장도 시도하지 않습니다. 이 경우 배지는 `skipped_manual_save_cooldown`으로 표시합니다.

`skipped_local_only_mode`는 현재 `local` 모드라서 백엔드 저장을 일부러 건너뛰었다는 뜻입니다. DB 저장 테스트는 반드시 `dual` 버튼이 활성화된 상태에서 진행합니다.

## v107: 복구 미리보기 버튼 추가

v107부터 SAVE DATA 배지에 복구 관련 버튼이 추가됐습니다.

| 버튼 | 역할 |
|---|---|
| `preview` | Console 명령어 없이 DB 세이브 복구 미리보기 모달을 엽니다. |
| `backup` | 가장 최근 복구 전 백업을 localStorage로 되돌립니다. 누르면 브라우저 확인창이 먼저 뜹니다. |

배지에는 `restore: ... · backups:n` 줄도 표시됩니다. 복구 완료 후에는 `restored_needs_reload`, 백업 복구 후에는 `backup_restored_needs_reload` 상태를 확인할 수 있습니다.

주의: `preview`에서 DB 세이브로 복구해도 즉시 게임 화면 상태가 바뀌는 것은 아닙니다. 기존 안전장치대로 localStorage만 바꾸고, 새로고침 후 적용됩니다.

## v110: 저장 후 무결성 검증

v110부터 `sync DB`와 수동 저장의 백엔드 이중 저장은 저장 직후 DB 세이브를 다시 조회해서 localStorage와 완전히 같은지 확인합니다.

| state | 의미 |
|---|---|
| `synced_verified` | DB 저장 성공 + DB 재조회 후 localStorage와 완전 동일 확인 |
| `saved_verify_failed` | DB 저장 후 검증 실패. `preview`로 차이를 확인해야 함 |

추가 Console 함수:

```js
await verifyBackendSaveSnapshotIntegrity();
await pushLocalSaveToBackendAndVerify();
await checkBackendSaveIntegrityReady();
```

---

## 원본: `docs/archive/stage-notes/SAVE_DATA_DUAL_WRITE.md`

# v100 Save Data Dual Write

이번 단계는 기존 `localStorage` 저장을 유지하면서, **수동 저장 버튼을 눌렀을 때 백엔드 DB에도 세이브 스냅샷을 저장**하는 단계입니다.

```txt
수동 저장 버튼 클릭
→ 기존 localStorage 저장 완료
→ FastAPI /api/v1/game/save 저장 시도
→ 성공하면 DB에도 저장
→ 실패해도 localStorage 저장은 유지
```

## 기본 모드

기본 모드는 `manual_dual`입니다.

```txt
manual_dual: 수동 저장 시 localStorage + backend DB 이중 저장
local_only: 기존 localStorage 저장만 사용
```

브라우저 Console에서 현재 정책을 확인할 수 있습니다.

```js
getBackendSaveSyncPolicy();
getBackendSaveSyncStatus();
```

## 모드 변경

백엔드 이중 저장 켜기:

```js
enableBackendSaveDualWrite();
```

로컬 저장 전용으로 끄기:

```js
disableBackendSaveDualWrite();
```

## 수동 동기화

현재 localStorage 저장값을 바로 백엔드로 보내려면:

```js
await syncLatestLocalSaveToBackend();
```

저장 브릿지 상태 확인:

```js
await checkBackendSaveSyncPolicy();
```

## 실패 처리

백엔드 저장 실패는 게임 저장 실패가 아닙니다.

```txt
localStorage 저장 성공
backend DB 저장 실패
→ 게임 진행 데이터는 브라우저에 안전하게 남아 있음
→ 로그에 백엔드 저장 실패 안내만 표시
```

## 실행 확인

위치: **프로젝트 루트**

```bash
node tools/smoke/game/smoke_save_data_dual_write.js
```

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
source .venv/Scripts/activate
uvicorn app.main:app --reload
```

게임 화면에서 수동 저장 버튼을 누른 뒤 Console에서 확인합니다.

```js
getBackendSaveSyncStatus();
await loadBackendSaveSnapshot();
```

## v102: 테스트 기준 정리

DB 저장 테스트는 `dual` 모드에서 진행합니다.

1. SAVE DATA 배지에서 `dual` 버튼이 활성화되어 있는지 확인합니다.
2. 성장/시스템 → 수동 저장을 누릅니다.
3. SAVE DATA 배지가 `synced`로 바뀌는지 확인합니다.

`local` 모드는 백엔드 저장을 끄는 안전 모드입니다. 이 상태에서 성장/시스템 → 수동 저장을 누르면 localStorage 저장만 하고 DB 저장은 시도하지 않으며, 상태는 `skipped_local_only_mode`가 됩니다.

수동 저장에는 60초 쿨타임이 있으므로 연속 테스트 중에는 `sync DB` 버튼으로 DB 전송만 따로 확인할 수 있습니다.

---

## 원본: `docs/archive/stage-notes/SAVE_DATA_INTEGRITY_VERIFY.md`

# Save Data Integrity Verify

v110 stabilizes the save snapshot API before moving toward an admin page.

## Goal

Manual save already dual-writes to:

```txt
localStorage key: idleRpgSaveV22
backend slot: default
```

This step keeps that behavior, but adds a verification pass after DB save:

```txt
1. saveGame() writes localStorage
2. POST /api/v1/game/save stores the DB snapshot
3. GET /api/v1/game/load reloads the DB snapshot
4. Browser compares localStorage snapshot and DB snapshot
5. SAVE DATA state becomes synced_verified only if they are exactly equal
```

## Added backend integrity metadata

`save`, `load`, and `save-slots` responses now include lightweight integrity metadata.

```txt
integrity.snapshotSha256
integrity.snapshotBytes
integrity.saveVersion
integrity.snapshotSaveVersion
integrity.summaryKeys
integrity.counts.inventoryItems
integrity.counts.storageItems
integrity.counts.trashItems
integrity.counts.mailboxItems
integrity.warnings
integrity.ok
```

The hash is calculated from deterministic JSON, so it is useful for debugging and future admin screens.

## Added backend request guard

`slotKey` is now validated before saving.

Allowed characters:

```txt
A-Z a-z 0-9 . _ -
```

This blocks unsafe path-like slot names such as `../bad-slot`.

## Added browser helpers

```js
await verifyBackendSaveSnapshotIntegrity();
await pushLocalSaveToBackendAndVerify();
await checkBackendSaveIntegrityReady();
```

## SAVE DATA badge state

Manual save or `SAVE DATA → sync DB` now tries to verify after saving.

```txt
synced_verified
→ DB save completed
→ DB snapshot loaded again
→ localStorage and DB snapshot are exactly equal

saved_verify_failed
→ DB save request completed or partially completed
→ but verification failed
→ use SAVE DATA → preview to inspect the difference
```

## DB reset / seed

No DB reset or seed import is required.

This version only adds validation, computed response metadata, and browser-side verification.
It does not change the database table shape.

---

## 원본: `docs/archive/stage-notes/SAVE_DATA_PREVIEW_COMPARE.md`

# v105 Save Data Preview / Compare

백엔드 DB에 저장된 세이브를 실제 게임에 덮어쓰기 전에, 현재 브라우저 localStorage 세이브와 DB 세이브를 비교하는 안전 점검 단계입니다.

## 목적

아직 DB 세이브를 게임에 자동 적용하지 않습니다.

이 단계에서는 다음만 확인합니다.

- 현재 브라우저 localStorage 세이브 존재 여부
- 백엔드 DB 세이브 존재 여부
- 레벨, 골드, 필드, 인벤토리 수, 창고 수, 우편 수, 장착 슬롯 수 차이
- 원본 JSON 스냅샷이 완전히 같은지 여부

## 브라우저 Console 함수

```js
await previewBackendSaveSnapshot();
```

결과 객체의 주요 필드:

- `local`: 현재 브라우저 저장 요약
- `backend`: DB 저장 요약
- `comparison.diffCount`: 주요 항목 차이 개수
- `comparison.sameRawSnapshot`: 원본 JSON까지 완전히 같은지 여부
- `recommendation`: 다음 행동 추천

## recommendation 의미

- `same_snapshot_safe`: localStorage와 DB 저장값이 완전히 같음
- `backend_empty_push_local_first`: DB에 저장값이 없으므로 먼저 수동 저장 또는 `sync DB` 필요
- `different_review_before_restore`: localStorage와 DB 값이 다르므로 복구 전에 반드시 확인 필요
- `minor_or_hidden_difference_review_raw`: 주요 요약은 같지만 원본 JSON에 차이가 있음
- `local_missing`: 브라우저 localStorage 저장값이 없음

## 주의

이 기능은 비교 전용입니다. DB 세이브를 게임에 적용하거나 localStorage를 덮어쓰지 않습니다.

---

## 원본: `docs/archive/stage-notes/SAVE_DATA_RESTORE_GUARD.md`

# Save Data Restore Guard

v106 adds a safe restore guard for backend save snapshots. v108 adds a reload lock so the restored localStorage value cannot be overwritten by the game auto-save before the reload finishes.

## Goal

Backend save data must not overwrite the browser save automatically. The restore flow is now:

1. Load backend save snapshot.
2. Compare it with current `localStorage` save.
3. Show a preview modal.
4. Create an automatic backup of the current local save.
5. Write the backend snapshot into `localStorage` only after confirmation.
6. Require page reload before the restored save is applied to the running game.

## Browser helpers

```js
await openBackendSaveRestorePreviewModal();
await restoreBackendSaveSnapshotToLocal();
listBackendSaveRestoreBackups();
restoreBackendSaveBackupToLocal();
getBackendSaveRestoreStatus();
await checkBackendSaveRestoreGuard();
```

## Notes

- This does not apply the save to the already-running game state.
- After restore, reload the page.
- Before overwriting `idleRpgSaveV22`, the current value is backed up under a timestamped localStorage key.
- Up to 5 restore backups are kept.

## v107 - Badge and modal UI actions

v107 connects the v106 restore guard to the on-screen `SAVE DATA` development badge.

New badge actions:

```txt
preview → openBackendSaveRestorePreviewModal()
backup  → restoreBackendSaveBackupToLocal()
```

The preview modal also includes a latest-backup summary and a `최근 백업으로 되돌리기` button. The backup restore action still asks for browser confirmation and still requires a page reload after it writes back to localStorage.

Preview values are escaped before being inserted into the modal HTML.


## v108 - Reload lock fix

Problem found during browser testing:

```txt
restore button writes backend/backup save into idleRpgSaveV22
→ page reload starts
→ existing beforeunload auto-save runs
→ current in-memory game state overwrites idleRpgSaveV22 again
→ restored save appears not to apply
```

v108 fixes this by adding a pending restore lock:

1. DB/backup restore writes the target snapshot into `idleRpgSaveV22`.
2. The restore guard records `upgradeRpgBackendSaveRestorePendingReload`.
3. While this lock exists, `saveGame()` skips automatic, unload, and manual save writes.
4. After reload, `loadGame()` reads the restored `idleRpgSaveV22`.
5. The lock is cleared and restore status becomes `applied_after_reload`.

Additional helpers:

```js
getPendingBackendSaveRestore();
shouldSkipSaveGameForBackendRestore("idleRpgSaveV22");
clearBackendSaveRestorePendingReload();
```

---

## 원본: `docs/archive/stage-notes/SAVE_DATA_RESTORE_RELOAD_LOCK.md`

# Save Data Restore Reload Lock

v108 fixes the browser reload edge case found after v107.

## Why this was needed

The restore buttons were writing the correct data into `localStorage`, but the game also has this safety behavior:

```txt
beforeunload → saveGame()
```

So when the user clicked `DB 세이브로 복구` or `최근 백업으로 되돌리기` and then reloaded, the old in-memory game state saved itself during unload and overwrote the restored `idleRpgSaveV22`.

## Fix

After a restore succeeds, v108 creates a pending reload lock:

```txt
upgradeRpgBackendSaveRestorePendingReload
```

While this lock exists, `saveGame()` returns early and does not overwrite `idleRpgSaveV22`. This protects against:

- `beforeunload` save,
- 60-second auto-save interval,
- manual save button before reload.

After the next page load, the game reads the restored save and then clears the lock through `completeBackendSaveRestoreReloadApply()`.

## DB reset / seed

Not needed. This is a frontend-only restore safety fix.

---

## 원본: `docs/archive/stage-notes/SAVE_DATA_SLOT_LIST.md`

# Save Data Slot List

v109 adds a safe DB save-slot list layer.

## Goal

This step prepares the save system for future multi-slot saves and the admin page without changing the current game boot/save behavior.

The browser game still uses:

```txt
localStorage key: idleRpgSaveV22
backend default slot: default
```

## Added backend API

```txt
GET /api/v1/game/save-slots
```

The API returns slot metadata only.
It does **not** return the full `snapshot_json`, so it is safer and lighter for UI/admin lists.

Returned slot fields include:

```txt
slotKey
isDefault
clientSaveKey
saveVersion
summary
source
note
createdAt
updatedAt
integrity
```

From v110, `integrity` contains checksum/size metadata for debugging. It still does not include full `snapshot_json`.
```

## Added browser helpers

```js
await listBackendSaveSlots();
await openBackendSaveSlotsModal();
await checkBackendSaveSlotsReady();
```

## SAVE DATA badge

The development `SAVE DATA` badge now has a `slots` button.

```txt
slots
→ opens the DB save-slot list modal
→ only reads DB metadata
→ does not restore or overwrite localStorage
```

## Test examples

위치: backend 폴더 + 가상환경 activate 상태

```bash
python scripts/check_save_snapshot_api.py
```

위치: 프로젝트 루트

```bash
node tools/smoke/game/smoke_save_data_slot_list.js
```

## DB reset / seed

No DB reset or seed import is required.

This version only adds a read API over the existing `user_save_snapshots` table.

---

## 원본: `docs/archive/stage-notes/SAVE_SNAPSHOT_API.md`

# v099 Save Snapshot API

## 목적

`master-data`는 PostgreSQL/FastAPI에서 읽는 흐름까지 연결되었다. 다음 단계는 유저 진행 데이터를 한 번에 정규화하기 전에, 현재 브라우저 `localStorage` 저장값을 그대로 DB에 보관하는 안전한 다리 구조를 만드는 것이다.

현재 브라우저 저장 키:

```txt
idleRpgSaveV22
```

## 이번 단계에서 하는 일

현재 localStorage 저장 구조를 바로 깨지 않기 위해, `snapshot_json`에 원본 payload를 그대로 저장한다.

```txt
localStorage idleRpgSaveV22
→ POST /api/v1/game/save
→ user_save_snapshots.snapshot_json
```

불러올 때도 아직 게임에 자동 적용하지 않고, API 응답으로만 확인한다.

```txt
GET /api/v1/game/load
→ 마지막 저장 snapshot 반환
```

## API

### POST /api/v1/game/save

위치: FastAPI 서버

```json
{
  "saveVersion": 5,
  "clientSaveKey": "idleRpgSaveV22",
  "slotKey": "default",
  "snapshot": {},
  "summary": {},
  "source": "localStorage-manual-push",
  "note": null
}
```

### GET /api/v1/game/load

```txt
/api/v1/game/load?slotKey=default
```

응답의 `payload.snapshot`에 저장했던 원본 save payload가 들어온다.

## 브라우저 Console 함수

FastAPI 서버가 켜진 상태에서 게임 화면 Console에서 실행한다.

```js
await checkBackendSaveSnapshotBridge();
await pushLocalSaveToBackend();
await loadBackendSaveSnapshot();
```

주의: `loadBackendSaveSnapshot()`은 아직 게임에 적용하지 않는다. 저장된 값을 확인만 한다.

## 확인 명령어

### 정적 검사

위치: 프로젝트 루트

```bash
python tools/smoke/game/smoke_save_snapshot_api_structure.py
node tools/smoke/game/smoke_save_data_bridge.js
```

### 실제 API 검사

FastAPI 서버 실행:

위치: backend 폴더 + 가상환경 activate 상태

```bash
source .venv/Scripts/activate
uvicorn app.main:app --reload
```

새 터미널에서:

위치: backend 폴더 + 가상환경 activate 상태

```bash
source .venv/Scripts/activate
python scripts/check_save_snapshot_api.py
```

## 다음 단계

이 API가 안정적으로 동작하면, 다음 단계에서 브라우저 수동 저장 버튼이나 자동 저장 흐름에 백엔드 저장을 선택적으로 연결한다. 기본 localStorage 저장은 계속 유지한다.

---

## 원본: `docs/archive/stage-notes/USER_SAVE_MIGRATION_PLAN.md`

# User Save Migration Plan

## 단계

1. 원본 localStorage snapshot을 DB에 저장한다. 현재 단계.
2. 브라우저 수동 저장 시 localStorage + backend snapshot 동시 저장 옵션을 붙인다.
3. backend snapshot을 불러와서 기존 `applyServerSavePayload()`로 적용하는 실험 모드를 만든다.
4. 아이템 인스턴스, 인벤토리 슬롯, 장비 슬롯, 스킬 레벨, 우편함을 정규화 테이블로 나눈다.
5. 정규화 저장이 안정화되면 snapshot은 백업/롤백 용도로만 남긴다.

## 왜 snapshot부터 하는가

현재 저장 데이터는 게임 로직과 강하게 연결되어 있다. 바로 정규화하면 작은 필드 하나 누락으로도 진행 데이터가 깨질 수 있다. 그래서 먼저 원본 저장값을 그대로 백엔드에 보관해서 복구 가능한 상태를 만든다.
