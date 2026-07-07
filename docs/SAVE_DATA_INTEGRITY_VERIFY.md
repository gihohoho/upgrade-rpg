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
