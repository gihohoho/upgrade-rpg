# Admin Edit Impact Guide

v126 adds a small impact guide to the guarded admin edit draft UI.

## Purpose

The admin page can already edit a narrow allow-list of master-data fields. This guide explains what a changed field is likely to affect before the user runs backend validation or applies the change.

This is meant to prevent confusion such as:

- `stackable=true` changes DB/runtime item stacking rules, but existing saved items are not automatically merged.
- Boss `hp` changes are reflected in game after the game page reloads.
- Drop `rate` and quantity changes affect future drop results.

## Where it appears

Admin page:

```text
Master Data Catalog
→ View an item/boss/field/etc.
→ Admin Edit Draft
→ Change a value
→ In-game impact guide appears above the validation/apply buttons
```

## Current guide examples

### stackable

`stackable` changes inventory stacking behavior for newly acquired +0 matching items.

Important notes:

- Existing saved items are not automatically merged.
- New drops can stack into an existing matching slot.
- Stacked equipment needs one empty slot before enhancement, because one item is separated before enhancement.

### 보스 체력 / Boss HP

Changing `bosses.hp` changes the boss maximum HP in combat after the game page reloads and reads the latest master-data.

### 드랍 확률 / Drop table items

Changing `rate`, `min_quantity`, or `max_quantity` affects future drop results.

### Enhancement levels

Changing `success_rate` or `gold_cost` affects enhancement difficulty and gold cost.

## Safety

This guide does not write anything.

The actual write path is still guarded by:

- backend validation,
- allow-list fields,
- confirmation text,
- `admin_change_logs`,
- rollback safety checks.

## DB reset / seed

DB reset / seed 필요 없음.

This version only changes the admin page UI guide and smoke tests.
