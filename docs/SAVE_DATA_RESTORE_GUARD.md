# Save Data Restore Guard

v106 adds a safe restore guard for backend save snapshots.

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
