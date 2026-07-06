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
