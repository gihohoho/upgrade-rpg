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
v181: admin create lifecycle guard helper

현재 인수인계 ZIP:
rpg_v181_create_lifecycle_guard_helper_ready.zip

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
37. fieldZones / bosses / skills / dropTables 신규 row 실제 생성 apply 제한 오픈 완료.
38. itemTemplates / dropTableItems 신규 row 실제 생성 apply 제한 오픈 완료.
39. 생성 row 삭제/복원 guard에 itemTemplates 연결 검사와 dropTableItems id 기반 삭제/복원 지원 추가.
40. skillLevels / enhancementLevels / characterSkills 신규 row 실제 생성 apply 제한 오픈 완료.
41. skillLevels / enhancementLevels / characterSkills 생성 row 삭제/복원 id 기반 guard 추가.

v179 현재 상태:
관리자 신규 row 생성 apply는 characters/enhancementGroups/fieldZones/bosses/skills/dropTables/itemTemplates/dropTableItems/skillLevels/enhancementLevels/characterSkills까지 제한적으로 열려 있어.
itemTemplates는 JSON/asset 필드를 잠근 상태로 scalar/relation 필드만 생성 가능하고, dropTableItems는 code 없는 leaf row라 id 기반 삭제/복원 흐름이 추가되어 있어.
skillLevels/enhancementLevels/characterSkills도 code 없는 relation/level row라 id 기반 삭제/복원 흐름이 추가되어 있어.
skillLevels는 skill_code + level 중복을 막고, enhancementLevels는 group_code + from_level 중복과 to_level > from_level 검증을 하고, characterSkills는 character_code + skill_code 중복을 막아.

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
신규 row 생성·삭제·복원 점검 섹션을 보면서 skillLevels/enhancementLevels/characterSkills 생성/삭제/복원 브라우저 확인부터 추천.
그 다음 관리자 페이지 코드 분리 또는 create/delete/restore UI dependency 표시 강화 추천.

v179에서 완료된 일:
1. skillLevels create apply allow-list 추가.
2. enhancementLevels create apply allow-list 추가.
3. characterSkills create apply allow-list 추가.
4. 위 3개 도메인 생성 row 삭제/복원 allow-list 추가.
5. skillLevels/enhancementLevels/characterSkills는 id 기반 생성 row 삭제/복원 흐름 지원.
6. skillLevels skill_code + level 중복 검증 유지.
7. enhancementLevels group_code + from_level 중복, to_level, success_rate, gold_cost 검증 강화.
8. characterSkills character_code + skill_code 중복, sort_order 검증 강화.
9. JSON 계열 필드는 계속 생성 입력에서 잠금.

현재 인수인계 패키지 작업:
- DB schema 변경 없음.
- DB reset / seed 필요 없음.


v181에서 완료된 일:
1. 관리자 페이지에 신규 row 생성·삭제·복원 점검 섹션 추가.
2. create-blueprint 응답에 createLifecycle 메타데이터 추가.
3. change log action filter를 update/rollback/create/create_delete/create_delete_restore 기준으로 정리.
4. 새 쓰기 도메인 오픈 없음.
5. DB schema 변경 없음, DB reset / seed 필요 없음.


추가 최신 상태 v181:
1. createLifecycle 메타데이터에 삭제 preview 차단 기준 추가.
2. 신규 row 생성·삭제·복원 점검 섹션에서 삭제 차단 기준 표시.
3. 변경 이력 action 필터 바로가기 버튼 추가.
4. 새 쓰기 도메인 오픈 없음.
5. DB schema 변경 없음, DB reset / seed 필요 없음.
