# Admin Change Log Filters

v129 adds filters to the admin change-log area.

## Purpose

After guarded master-data edits and rollbacks are enabled, `admin_change_logs` grows quickly. This stage makes it easier to find a specific change without exposing raw before/after JSON.

## UI filters

The admin page now supports:

- limit
- target type, for example `master_data.bosses`
- target row ID
- action: `guarded_update` or `guarded_rollback`
- changed field, for example `hp`, `stackable`, `admin_note`
- applied status
- sort order

## API

`GET /api/v1/admin/change-logs` accepts:

- `limit`
- `targetType`
- `targetId`
- `action`
- `changedKey`
- `applied`
- `sort`

The response still returns compact rows only. Raw `before_json` and `after_json` are not returned.

## Safety

No DB reset or seed is required.

This stage only changes query/read behavior and the admin page UI. It does not add new write paths.
