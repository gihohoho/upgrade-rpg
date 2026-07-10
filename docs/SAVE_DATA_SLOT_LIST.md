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
