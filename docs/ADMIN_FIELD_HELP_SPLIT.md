# Admin Field Help Split

v196에서는 관리자 페이지의 field help/value hints/equip slot label helper를 외부 JS 파일로 분리했습니다.

## 추가 파일

- `src/api/admin/admin-field-help.js`

## 분리 범위

- `ADMIN_FIELD_HELP_DEFINITIONS`
- `ADMIN_EQUIP_SLOT_PRESET_LABELS`
- `getAdminFieldHelp()`
- `listAdminFieldHelp()`
- `renderFieldHelpBadge()`
- `renderFieldHelpInline()`
- `getAdminFieldValueHint()`
- `renderFieldValueHintInline()`
- `formatValueWithFieldHint()`
- `getAdminEquipSlotDisplayName()`

## 호환 유지

기존 window 함수명은 `admin-page-readonly.js` wrapper를 통해 그대로 유지했습니다.

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().fieldHelpExternalReady
window.RpgAdminFieldHelp.VERSION
```

예상:

```txt
true
v196.admin-field-help-split
```

## 검증

- `tools/smoke_admin_field_help_split.js`
- `bash tools/run_smoke_core.sh`
- `bash tools/run_smoke_all.sh`

## DB / env

DB reset/seed는 필요 없습니다.
