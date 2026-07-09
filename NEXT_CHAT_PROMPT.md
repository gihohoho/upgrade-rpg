바로 직전 채팅에서 이어서 진행합니다.

중요:
- 사용자는 게임 프로젝트의 기획/게임 제작자 이기호이며, 앞으로 기호라고 부릅니다.
- 기호는 코딩/터미널/경로에 익숙하지 않습니다.
- 명령어를 줄 때는 항상 먼저 어디에서 실행해야 하는지 적습니다.
- 주석 기호가 들어간 설명은 코드블록 안에 넣지 말고 코드블록 밖에서 설명합니다.
- 커밋 명령어는 마지막에 add부터 push까지 한 번에 알려줍니다.

현재 안정 버전:
v195: admin thin entry cleanup

현재 인수인계 ZIP:
rpg_v195_admin_thin_entry_cleanup_ready.zip

먼저 확인할 파일:
- NEXT_CHAT_HANDOFF.md
- docs/CURRENT_STATUS.md
- docs/NEXT_STEPS.md
- docs/README.md
- docs/PROJECT_STRUCTURE.md

현재 관리자 JS 분리 상태:
- `src/api/admin-layout-shell.js` — v185 분리 완료
- `src/api/admin/admin-change-logs.js` — v187 분리 완료
- `src/api/admin/admin-create-lifecycle.js` — v189.1 hotfix 포함 분리 완료
- `src/api/admin/admin-edit-draft.js` — v191 분리 완료
- `src/api/admin/admin-master-catalog.js` — v192 분리 완료
- `src/api/admin/admin-overview-snapshots.js` — v193 분리 완료
- `src/api/admin-page-readonly.js` — v195 기준 thin entry cleanup 완료

다음 추천 단계:
v196 admin field help/value hints split.
`src/api/admin/admin-field-help.js`를 만들고 field help / value hint / equip slot label helper를 분리하는 방향 추천.

검증 기준:
- `bash tools/run_smoke_core.sh`
- `bash tools/run_smoke_all.sh`
- `node --check` 주요 관리자 JS
- `python -m compileall -q backend/app`
