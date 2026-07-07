# Save Data Badge Restore Actions

v107 adds restore-related controls to the local development `SAVE DATA` badge.

## Goal

The restore preview was already available from the browser Console in v106. v107 makes the same safe flow reachable from the on-screen development badge, so the game owner can test save restore without typing Console commands.

Existing gameplay save behavior is unchanged:

```txt
Game save button
→ localStorage save remains the source used by the running game
→ backend DB save is attempted only in dual mode
→ backend restore still requires preview + backup + reload
```

## New SAVE DATA badge buttons

| Button | What it does |
|---|---|
| `preview` | Opens the DB save restore preview modal. It only compares `localStorage` and backend DB save data first. |
| `backup` | Restores the most recent pre-restore localStorage backup after browser confirmation. Reload is still required. |

The existing buttons remain:

| Button | What it does |
|---|---|
| `sync DB` | Pushes the current `localStorage` save to backend DB immediately. |
| `load DB` | Loads backend DB save data for inspection only. |
| `dual` | Enables manual save dual write. |
| `local` | Keeps manual save localStorage-only. |

## Modal additions

The restore preview modal now shows:

- a stronger reload warning,
- latest backup summary,
- `최근 백업으로 되돌리기` button,
- escaped preview values before inserting them into modal HTML.

## Safety notes

- No database reset is needed.
- No seed import is needed.
- Backend restore still does not mutate the live in-memory game state directly.
- Restore writes into `idleRpgSaveV22`, then the user must reload the page.
- Before DB restore, the existing local save is backed up automatically.
