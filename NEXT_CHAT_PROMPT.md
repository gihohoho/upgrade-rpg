바로 직전 채팅에서 이어서 할게. 채팅이 너무 많이 쌓여서 새 채팅을 열었어.
현재 상태 ZIP을 같이 줄게. 지금까지는 완벽하게 잘 작동하고 있어. 다음 단계 진행해줘.

중요:
나는 이 게임 프로젝트의 기획/게임 제작자 이기호야. 앞으로 나를 기호라고 불러줘.
나는 코딩/터미널/경로에 익숙하지 않아.
명령어를 줄 때는 항상 먼저 어디에서 실행해야 하는지 적어줘.
주석 기호가 들어간 설명은 코드블록 안에 넣지 말고 코드블록 밖에서 설명해줘.
커밋 명령어는 마지막에 add부터 push까지 한 번에 알려줘.
앞으로 다음 단계로 넘어갈 때는 무엇을 할지 먼저 설명해줘.

현재 프로젝트는 아직 Vue가 아니라 index.html + JS + CSS 기반 RPG 게임이야.
기존 게임이 완전히 정상 작동하는 상태를 유지하면서 단계적으로 백엔드 분리 중이야.
나중에는 Vue 프론트엔드 + FastAPI 백엔드 + PostgreSQL + 관리자 페이지 구조로 옮길 예정이지만, 지금은 안정성이 최우선이야.

GitHub repo:
https://github.com/gihohoho/upgrade-rpg.git

로컬 경로:
프로젝트 루트: ~/Desktop/Upgrade RPG
backend 폴더: ~/Desktop/Upgrade RPG/backend

백엔드 실행:
위치: backend 폴더 + 가상환경 activate 상태
source .venv/Scripts/activate
uvicorn app.main:app --reload

PostgreSQL/Docker 정보:
DB 컨테이너: upgrade_rpg_postgres
Adminer 컨테이너: upgrade_rpg_adminer
PostgreSQL host port: 55432
Adminer: 8081
DATABASE_URL:
postgresql+asyncpg://rpg_user:rpg_password@127.0.0.1:55432/rpg_game

localStorage save key:
idleRpgSaveV22

관리자 쓰기 dev key:
local-admin-dev-key

관리자 확인 문구:
관리자 실제 적용 확인 문구: APPLY MASTER DATA EDIT
관리자 high risk 추가 확인 문구: HIGH RISK EDIT
관리자 되돌리기 확인 문구: ROLLBACK MASTER DATA EDIT
신규 row 생성 확인 문구: CREATE MASTER DATA ROW
생성 row 삭제 확인 문구: DELETE CREATED MASTER DATA ROW
삭제 row 복원 확인 문구: RESTORE DELETED CREATED ROW
생성→삭제→복원 일괄 점검 확인 문구: RUN CREATE DELETE RESTORE CHECK

.env / .gitignore 처리:
내 로컬에는 .env, .gitignore가 이미 있어.
둘이 바뀌지 않았으면 ZIP에 굳이 포함하지 않아도 돼.
둘 중 하나라도 수정이 필요한 단계라면 ZIP에 포함하고, 무엇이 바뀌었는지 반드시 알려줘.

현재 안정 버전:
v187: admin change logs split

현재 인수인계 ZIP:
rpg_v187_admin_change_logs_split_ready.zip

새 채팅에서 먼저 확인할 파일:
NEXT_CHAT_HANDOFF.md
docs/CURRENT_STATUS.md
docs/NEXT_STEPS.md
docs/README.md
docs/PROJECT_STRUCTURE.md

현재 핵심 상태:
1. 기존 게임 정상 동작 유지.
2. master-data PostgreSQL → FastAPI → 브라우저 연결 유지.
3. 백엔드 실패 시 static JS fallback 유지.
4. save snapshot dual write 유지.
5. 관리자 guarded edit apply / rollback / create / delete / restore 제한 흐름 유지.
6. 생성→삭제→복원 일괄 점검 UI 유지.
7. 관리자 JS 분리 전 readiness UI 유지.
8. 관리자 layout shell은 src/api/admin-layout-shell.js로 실제 분리 완료.
9. change logs는 src/api/admin/admin-change-logs.js로 실제 1차 분리 완료.

현재 create apply 열린 도메인:
characters, enhancementGroups, fieldZones, bosses, skills, dropTables, itemTemplates, dropTableItems, skillLevels, enhancementLevels, characterSkills

v187 완료:
- src/api/admin/ 폴더 생성.
- src/api/admin/admin-change-logs.js 신규 추가.
- 변경 이력 필터/목록/상세/rollback/create-delete/restore 구현을 외부 파일로 1차 분리.
- admin-page-readonly.js에는 기존 window export 호환 wrapper 유지.
- admin.html script 순서를 game-api-client.js → admin-layout-shell.js → admin/admin-change-logs.js → admin-page-readonly.js 로 변경.
- 새 함수 getAdminChangeLogsReadiness() 추가.
- checkAdminReadOnlyPageReady().changeLogsExternalReady 가 true면 정상.
- 새 smoke tools/smoke_admin_change_logs_split.js 추가 및 core smoke 포함.
- DB reset / seed 필요 없음.
- .env, .gitignore 변경 없음.

다음 추천 단계:
v188 create lifecycle split contract.

권장 방향:
1. 바로 create lifecycle 구현을 외부 파일로 옮기지 말고 계약부터 고정.
2. 생성 초안/window export/DOM target/delegated action 목록 정리.
3. runAdminCreateLifecycleBatchCheck, 생성/삭제/복원 결과 렌더링 함수 목록 고정.
4. 다음 후보 파일명 src/api/admin/admin-create-lifecycle.js 로 고정.
5. 새 smoke tools/smoke_admin_create_lifecycle_split_contract.js 추가.
6. 안정적이면 v189에서 실제 create lifecycle 파일 분리.
