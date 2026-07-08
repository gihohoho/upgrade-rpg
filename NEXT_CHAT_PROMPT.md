바로 직전 채팅에서 이어서 할게. 채팅이 너무 많이 쌓여서 새 채팅을 열었어.
현재 상태 ZIP을 같이 줄게. 지금까지는 완벽하게 잘 작동하고 있어. 다음 단계 진행해줘.

중요:
나는 이 게임 프로젝트의 기획/게임 제작자 이기호야. 앞으로 나를 기호라고 불러줘.
나는 코딩/터미널/경로에 익숙하지 않아.
명령어를 줄 때는 항상 먼저 어디에서 실행해야 하는지 적어줘.

예:

위치: 프로젝트 루트
bash tools/run_smoke_core.sh

위치: backend 폴더 + 가상환경 activate 상태
source .venv/Scripts/activate
uvicorn app.main:app --reload

위치: 브라우저 개발자도구 Console
checkAdminReadOnlyPageReady();

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

관리자 실제 적용 확인 문구:
APPLY MASTER DATA EDIT

관리자 high risk 추가 확인 문구:
HIGH RISK EDIT

관리자 되돌리기 확인 문구:
ROLLBACK MASTER DATA EDIT

신규 row 생성 확인 문구:
CREATE MASTER DATA ROW

생성 row 삭제 확인 문구:
DELETE CREATED MASTER DATA ROW

삭제 row 복원 확인 문구:
RESTORE DELETED CREATED ROW

.env / .gitignore 처리:
내 로컬에는 .env, .gitignore가 이미 있어.
둘이 바뀌지 않았으면 ZIP에 굳이 포함하지 않아도 돼.
둘 중 하나라도 수정이 필요한 단계라면 ZIP에 포함하고, 무엇이 바뀌었는지 반드시 알려줘.

현재 안정 버전:
v174: admin collapsed panel style fix

최신 ZIP:
rpg_v174_admin_collapsed_panel_style_fix.zip

새 채팅에서 먼저 확인할 파일:
NEXT_CHAT_HANDOFF.md
NEXT_CHAT_PROMPT.md
docs/CURRENT_STATUS.md
docs/NEXT_STEPS.md
docs/ADMIN_CREATE_DELETE_RESTORE.md

현재 완료된 핵심:
1. master-data PostgreSQL → FastAPI → 브라우저 연결 완료.
2. master-data 기본 mode는 auto.
3. 백엔드 실패 시 static JS 데이터 fallback 유지.
4. localStorage 저장 유지.
5. save snapshot API + dual write 완료.
6. SAVE DATA dev badge 완료.
7. DB 세이브 preview/restore/backup/rollback/reload lock 완료.
8. save slot 목록, integrity verify 완료.
9. admin.html 관리자 페이지 분리 완료.
10. 관리자 overview, 세이브 스냅샷 필터, 마스터 데이터 목록/상세/relations 완료.
11. 관리자 편집 초안, 백엔드 검증, field help, value hints, impact guide 완료.
12. guarded edit apply 완료.
13. change log 상세/rollback/filter 완료.
14. admin write dev key guard 완료.
15. stale guard 완료.
16. master-data API 반영 확인 및 post-edit 자동 확인 완료.
17. DB itemTemplates.stackable 값이 인게임 신규 획득 아이템 겹치기에 연결 완료.
18. 겹친 장비 강화 시 가방이 꽉 차 있으면 강화 차단 완료.
19. 관리자 relation select / relation label / change log relation 도구 완료.
20. 신규 row 생성 준비 blueprint read-only 완료.
21. 신규 row 생성 draft 입력 UI와 preview-only 검증 API 완료.
22. characters / enhancementGroups 신규 row 실제 생성 apply 제한 오픈 완료.
23. create 이력 기반 생성 row 삭제 preview/apply 제한 오픈 완료.
24. create_delete 이력 기반 삭제 row 복원 preview/apply 제한 오픈 완료.

v172 세부 완료:
관리자 페이지 sidebar navigation shell 추가.
sticky header 추가.
주요 섹션 접기/펼치기 추가.
접힘 상태 localStorage 저장.
footer 버전/상태 영역 정리.
기존 관리자 edit/create/delete/restore 기능 유지.

DB reset/seed가 필요한 단계인지 아닌지 반드시 알려줘.
작업 후 ZIP으로 줘.
커밋 명령어도 마지막에 add부터 push까지 같이 줘.
명령어마다 반드시 실행 위치를 먼저 적어줘.
주석(#, //)들은 코드블록 밖에서 설명해줘.
가능하면 작업 후 smoke를 돌려줘.
ZIP에는 전체 프로젝트 파일/폴더를 묶어줘. 단, .env, .gitignore는 바뀐 경우에만 포함하면 돼.

smoke 실행:
위치: 프로젝트 루트
bash tools/run_smoke_core.sh

위치: 프로젝트 루트
bash tools/run_smoke_all.sh

다음 추천 단계:
v175 create apply 도메인 제한 확장
fieldZones create apply 제한 오픈부터 추천.
itemTemplates, skills, dropTables, dropTableItems는 아직 바로 열지 않는 것이 안전함.


## v173 세부 완료

- sidebar sticky top offset을 header 높이 기준으로 자동 보정했습니다.
- `필드 용어 도움말`, `신규 row 생성 준비`, `관리자 변경 이력` 기본 상태를 접기로 변경했습니다.
- 접힌 섹션은 amber 계열 색상으로 구분되도록 표시를 강화했습니다.
- DB reset / seed 필요 없습니다.


## v174 세부 완료

- 접힌 탭 공통 CSS를 보정했습니다.
- `.section`, `.filter-panel`, `.field-help-panel` 기반 접힘 상태가 모두 같은 amber 계열 카드 스타일로 보이게 했습니다.
- `필드 용어 도움말`, `신규 row 생성 준비`처럼 filter/help panel 구조인 탭이 안쪽 header만 색칠되던 문제를 수정했습니다.
- `getAdminLayoutShellReadiness().collapsedPanelStyleReady` 확인 상태를 추가했습니다.
- DB reset / seed 필요 없습니다.
