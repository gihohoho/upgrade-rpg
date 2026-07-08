바로 직전 채팅에서 이어서 할게. 채팅이 너무 많이 쌓여서 새 채팅을 열었어.
현재 상태 ZIP을 같이 줄게. 지금까지는 완벽하게 잘 작동하고 있어. 다음 단계 진행해줘.

중요:
나는 이 게임 프로젝트의 기획/게임 제작자 이기호야. 앞으로 나를 기호라고 불러줘.
나는 코딩/터미널/경로에 익숙하지 않아.
명령어를 줄 때는 항상 먼저 어디에서 실행해야 하는지 적어줘.
주석 기호가 들어간 설명은 코드블록 안에 넣지 말고 코드블록 밖에서 설명해줘.
커밋 명령어는 마지막에 add부터 push까지 한 번에 알려줘.

명령어 예시:

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

관리자 확인 문구:
관리자 실제 적용 확인 문구: APPLY MASTER DATA EDIT
관리자 high risk 추가 확인 문구: HIGH RISK EDIT
관리자 되돌리기 확인 문구: ROLLBACK MASTER DATA EDIT
신규 row 생성 확인 문구: CREATE MASTER DATA ROW
생성 row 삭제 확인 문구: DELETE CREATED MASTER DATA ROW
삭제 row 복원 확인 문구: RESTORE DELETED CREATED ROW

.env / .gitignore 처리:
내 로컬에는 .env, .gitignore가 이미 있어.
둘이 바뀌지 않았으면 ZIP에 굳이 포함하지 않아도 돼.
둘 중 하나라도 수정이 필요한 단계라면 ZIP에 포함하고, 무엇이 바뀌었는지 반드시 알려줘.

현재 안정 버전:
v175: create apply fieldZones

현재 인수인계 ZIP:
rpg_v175_fieldzones_create_apply_ready.zip

새 채팅에서 먼저 확인할 파일:
NEXT_CHAT_HANDOFF.md
docs/CURRENT_STATUS.md
docs/NEXT_STEPS.md
docs/README.md
docs/PROJECT_STRUCTURE.md

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
19. 관리자 편집 입력 UI 타입 개선 완료.
20. 관리자 safe select / allow-list 확장 완료.
21. 장비 슬롯 표시명을 인게임 이름으로 개선 완료.
22. 마스터 데이터 카탈로그 페이지네이션 완료.
23. 관리자 변경 전후 비교 UI + high risk 추가 확인 완료.
24. relation select 기반 안전 편집 완료.
25. 조합 관계 필드 중복 검증 완료.
26. dropTables.owner_code owner_type 연동 select 완료.
27. relation select 검색/필터 완료.
28. 변경 preview relation label / 대상 열기 완료.
29. change log / rollback preview relation label 완료.
30. 신규 row 생성 blueprint read-only 완료.
31. 신규 row 생성 draft 입력 UI + preview-only 검증 완료.
32. characters / enhancementGroups 신규 row 실제 생성 apply 제한 오픈 완료.
33. create 이력 기반 생성 row 삭제 preview/apply 제한 오픈 완료.
34. create_delete 이력 기반 삭제 row 복원 preview/apply 제한 오픈 완료.
35. 관리자 페이지 sidebar / sticky header / footer / 섹션 접기·펼치기 완료.
36. 접힌 섹션 공통 CSS 보정 완료.

v174 현재 상태:
관리자 페이지가 길어져서 v172~v174에서 레이아웃 정리를 먼저 했어.
sidebar, sticky header, 섹션 접기/펼치기, footer 상태 표시가 있고, 접힌 탭은 amber 계열로 구분돼.
스크롤 시 sidebar가 header에 가려지던 문제와 일부 탭만 색상이 이상하던 문제까지 수정 완료했어.

중요한 안전 원칙:
기존 게임 동작을 깨면 안 됨.
localStorage 저장은 계속 유지해야 함.
DB reset/seed가 필요한 단계인지 아닌지 반드시 알려줘.
작업 후 ZIP으로 줘.
명령어마다 반드시 실행 위치를 먼저 적어줘.
가능하면 작업 후 smoke를 돌려줘.
ZIP에는 전체 프로젝트 파일/폴더를 묶어줘.
단, .env, .gitignore는 바뀐 경우에만 포함하면 돼.

smoke 실행:
위치: 프로젝트 루트
bash tools/run_smoke_core.sh

위치: 프로젝트 루트
bash tools/run_smoke_all.sh

다음 추천 단계:
v176 bosses create apply 검토
먼저 fieldZones 생성/삭제/복원 브라우저 확인부터 추천.

v175에서 안전하게 할 일:
1. fieldZones create apply allow-list 추가.
2. fieldZones 생성 preview/apply smoke 추가.
3. 생성 row 삭제 dependency guard에 dropTables.owner_type=field + owner_code 검사 추가.
4. create_delete restore에도 fieldZones 복원 충돌 검증 포함.
5. itemTemplates, skills, dropTables, dropTableItems 생성 apply는 아직 열지 말 것.

현재 인수인계 패키지 작업:
- 런타임 코드 변경 없음.
- 문서/인수인계 정리 중심.
- DB reset / seed 필요 없음.
