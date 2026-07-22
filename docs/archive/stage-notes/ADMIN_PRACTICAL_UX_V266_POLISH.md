# Admin practical UX v266 polish

v266 applies direct user feedback to the v261-v265 UX bundle.

## Changes

- Removed the catalog `보기 방식` select and returned to one catalog list.
- Kept compact long-value handling, but shortened the inline preview width.
- Removed visible button risk text chips; risk is communicated through color and tooltip only.
- Added `admin-detail-shortcuts.js` so detail quick buttons move to their related cards or expand/scroll to field help.

## Safety

This is UI-only. It does not change DB, env, seed, auth, routes, API response bodies, write guard, or write logic.
