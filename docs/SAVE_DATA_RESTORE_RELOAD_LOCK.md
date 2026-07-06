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
