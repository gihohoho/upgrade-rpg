# 새 채팅 시작용 프롬프트

아래 내용을 그대로 새 채팅의 첫 메시지로 붙여넣고, 함께 `rpg_v133_admin_edit_input_ui.zip`을 업로드해서 이어서 진행해줘.

---

바로 직전 채팅에서 이어서 할게. 채팅이 너무 많이 쌓여서 새 채팅을 열었어.
현재 상태 ZIP을 같이 줄게. 지금까지는 완벽하게 잘 작동하고 있어. 다음 단계 진행해줘.

중요:
나는 이 게임 프로젝트의 기획/게임 제작자 이기호야. 앞으로 나를 기호라고 불러줘.
나는 코딩/터미널/경로에 익숙하지 않아.
명령어를 줄 때는 항상 먼저 어디에서 실행해야 하는지 적어줘.

예:

```bash
# 위치: 프로젝트 루트
bash tools/run_smoke_core.sh
```

```bash
# 위치: backend 폴더 + 가상환경 activate 상태
source .venv/Scripts/activate
uvicorn app.main:app --reload
```

```js
// 위치: 브라우저 개발자도구 Console
checkAdminReadOnlyPageReady();
```

현재 프로젝트는 아직 Vue가 아니라 index.html + JS + CSS 기반 RPG 게임이야.
기존 게임이 완전히 정상 작동하는 상태를 유지하면서 단계적으로 백엔드 분리 중이야.
나중에는 Vue 프론트엔드 + FastAPI 백엔드 + PostgreSQL + 관리자 페이지 구조로 옮길 예정이지만, 지금은 안정성이 최우선이야.

GitHub repo:
https://github.com/gihohoho/upgrade-rpg.git

로컬 경로:
프로젝트 루트: ~/Desktop/Upgrade RPG
backend 폴더: ~/Desktop/Upgrade RPG/backend

백엔드 실행:

```bash
# 위치: backend 폴더 + 가상환경 activate 상태
source .venv/Scripts/activate
uvicorn app.main:app --reload
```

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

.env / .gitignore 처리:
내 로컬에는 .env, .gitignore가 이미 있어.
둘이 바뀌지 않았으면 ZIP에 굳이 포함하지 않아도 돼.
둘 중 하나라도 수정이 필요한 단계라면 ZIP에 포함하고, 무엇이 바뀌었는지 반드시 알려줘.

현재 안정 버전:
v133: admin edit input UI

최신 ZIP:
rpg_v133_admin_edit_input_ui.zip

새 채팅에서 먼저 확인할 파일:
NEXT_CHAT_HANDOFF.md
NEXT_CHAT_PROMPT.md
docs/CURRENT_STATUS.md
docs/NEXT_STEPS.md

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
19. v132에서 문서 정리와 smoke 실행 스크립트 정리 완료.
20. v133에서 관리자 편집 초안 입력 UI 타입 개선 완료.
    - boolean 필드 true/false select
    - number 필드 number input
    - description/admin_note textarea
    - 읽기 전용/잠금 필드 카드 표시

현재 게임 실제 세이브 슬롯:
default

수동저장 시:
localStorage idleRpgSaveV22 저장 + DB default 슬롯 갱신

관리자 실제 적용 확인 문구:
APPLY MASTER DATA EDIT

관리자 되돌리기 확인 문구:
ROLLBACK MASTER DATA EDIT

중요한 안전 원칙:
기존 게임 동작을 깨면 안 됨.
localStorage 저장은 계속 유지해야 함.
DB reset/seed가 필요한 단계인지 아닌지 반드시 알려줘.
작업 후 ZIP으로 줘.
커밋 명령어도 마지막에 같이 줘.
명령어마다 반드시 실행 위치를 먼저 적어줘.
가능하면 작업 후 smoke를 돌려줘.
ZIP에는 전체 프로젝트 파일/폴더를 묶어줘. 단, .env, .gitignore는 바뀐 경우에만 포함하면 돼.

smoke 실행:

```bash
# 위치: 프로젝트 루트
bash tools/run_smoke_core.sh
```

```bash
# 위치: 프로젝트 루트
bash tools/run_smoke_all.sh
```

다음 추천 단계:
v134 관리자 allow-list 확장

구체적으로:
skills/dropTableItems/enhancementLevels/fieldZones에서 안전한 수치/설명 필드를 조금씩 실제 수정 가능하게 확장.
관계 필드(`*_id`, `*_code`)는 아직 잠금 유지.

이 단계는 DB reset/seed 없이 백엔드 allow-list + 관리자 UI/검증 중심으로 진행하는 게 좋아.

업로드한 ZIP 기준으로 구조 확인 후, v134부터 이어서 진행해줘.
