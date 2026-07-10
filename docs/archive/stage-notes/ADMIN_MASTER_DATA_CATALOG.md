# v115 - Admin master data catalog

This stage adds a bolder but still read-only admin step: the standalone `admin.html`
page can browse selected master-data domains from PostgreSQL.

## What changed

- Added read-only backend APIs:
  - `GET /api/v1/admin/master-data/domains`
  - `GET /api/v1/admin/master-data/catalog`
- Added safe admin catalog filters to `admin.html`:
  - domain
  - limit
  - search query
  - enabled status
  - sort
- Added frontend API helpers:
  - `listAdminMasterCatalogDomains()`
  - `listAdminMasterCatalogRows()`
- Added browser console helpers:
  - `readAdminMasterCatalogFilters()`
  - `resetAdminMasterCatalogFilters()`
- Added static smoke test:
  - `tools/smoke/frontend/smoke_admin_master_data_catalog.js`

## Safety rules

This version is still read-only.

- No DB mutation.
- No localStorage mutation.
- No game runtime mutation.
- No admin 지급/수정/삭제 action.
- Raw model JSON blobs are not returned.
- Inline image/data URL assets are not returned.

The API returns compact table cells for admin browsing only. This prepares the
future admin edit screen without exposing write actions yet.

## DB reset / seed

Not required. Existing master-data tables are queried only.

## Local check

```bash
# Location: backend folder + virtualenv activated
python scripts/check_admin_readonly_api.py
```

```bash
# Location: project root
node tools/smoke/frontend/smoke_admin_master_data_catalog.js
```
