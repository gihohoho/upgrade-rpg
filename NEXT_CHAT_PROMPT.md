바로 직전 채팅에서 이어서 할게. 채팅이 너무 많이 쌓여서 새 채팅을 열었어.
현재 상태 ZIP을 같이 줄게. 지금까지는 완벽하게 잘 작동하고 있어. 다음 단계 진행해줘.

중요:
나는 이 게임 프로젝트의 기획/게임 제작자 이기호야. 앞으로 나를 기호라고 불러줘.
나는 코딩/터미널/경로에 익숙하지 않아.
명령어를 줄 때는 항상 먼저 어디에서 실행해야 하는지 적어줘.
주석 기호가 들어간 설명은 코드블록 안에 넣지 말고 코드블록 밖에서 설명해줘.
커밋 명령어는 마지막에 add부터 push까지 한 번에 알려줘.

현재 프로젝트는 아직 Vue가 아니라 index.html + JS + CSS 기반 RPG 게임이야.
기존 게임이 완전히 정상 작동하는 상태를 유지하면서 단계적으로 백엔드 분리 중이야.
나중에는 Vue 프론트엔드 + FastAPI 백엔드 + PostgreSQL + 관리자 페이지 구조로 옮길 예정이지만, 지금은 안정성이 최우선이야.

현재 안정 버전:
v191: admin edit draft split

현재 인수인계 ZIP:
rpg_v191_admin_edit_draft_split_ready.zip

먼저 확인할 파일:
NEXT_CHAT_HANDOFF.md
docs/CURRENT_STATUS.md
docs/NEXT_STEPS.md
docs/README.md
docs/PROJECT_STRUCTURE.md

현재 완료:
- layout shell 분리 완료
- change logs 분리 완료
- create lifecycle 분리 완료(v189.1 hotfix 포함)
- edit draft 분리 완료(v191)

다음 추천 단계:
v192 master detail/catalog split contract.

바로 실제 분리하지 말고, master catalog/detail/relations/API verify 관련 함수/window/DOM 계약을 먼저 고정하는 방향을 추천.
후보 파일명:
- src/api/admin/admin-master-catalog.js
- src/api/admin/admin-master-detail.js
