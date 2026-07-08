# 새 채팅 시작용 프롬프트

아래 내용을 그대로 새 채팅의 첫 메시지로 붙여넣고, 함께 `rpg_v156_admin_change_log_relation_tools.zip`을 업로드해서 이어서 진행해줘.

---

바로 직전 채팅에서 이어서 할게. 채팅이 너무 많이 쌓여서 새 채팅을 열었어.
현재 상태 ZIP을 같이 줄게. 지금까지는 완벽하게 잘 작동하고 있어. 다음 단계 진행해줘.

중요:
나는 이 게임 프로젝트의 기획/게임 제작자 이기호야. 앞으로 나를 기호라고 불러줘.
나는 코딩/터미널/경로에 익숙하지 않아.
명령어를 줄 때는 항상 먼저 어디에서 실행해야 하는지 적어줘.
주석(`#`, `//`)은 명령어 코드블록 안에 넣지 말고 코드블록 밖에서 설명해줘.

현재 프로젝트는 아직 Vue가 아니라 index.html + JS + CSS 기반 RPG 게임이야.
기존 게임이 완전히 정상 작동하는 상태를 유지하면서 단계적으로 백엔드 분리 중이야.
나중에는 Vue 프론트엔드 + FastAPI 백엔드 + PostgreSQL + 관리자 페이지 구조로 옮길 예정이지만, 지금은 안정성이 최우선이야.

GitHub repo:
https://github.com/gihohoho/upgrade-rpg.git

로컬 경로:
프로젝트 루트: ~/Desktop/Upgrade RPG
backend 폴더: ~/Desktop/Upgrade RPG/backend

백엔드 실행 위치: backend 폴더 + 가상환경 activate 상태

```bash
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
v156: admin change log relation tools

최신 ZIP:
rpg_v156_admin_change_log_relation_tools.zip

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
21. v134에서 admin safe selects + allow-list 확장 완료.
22. v135에서 마스터 데이터 카탈로그 페이지네이션 + 슬롯 이름 표시 완료.
23. v138에서 관리자 적용 직전 비교 UI + high risk 추가 확인 완료.
24. v141에서 관리자 관계 필드 안전 편집 완료.
25. v144에서 조합 관계 필드 안전 편집과 중복 조합 검증 완료.
26. v147에서 dropTables.owner_code 안전 편집과 owner_type 연동 select 완료.
27. v150에서 relation select 검색/필터 UI 완료.
28. v150에서 마스터 카탈로그 Enter 조회/페이지 자동 초기화 완료.
29. v151에서 변경 preview relation label 강화 완료.
30. v152에서 relation 대상 빠른 열기 버튼 완료.
31. v153에서 relation 변경 개수 표시 완료.
32. v156에서 change log 상세/rollback preview relation label 강화 완료.

v156 세부 완료:
- v147 관계 필드 안전 편집 유지.
- v150 relation select 후보 검색/필터 유지.
- v153 변경 preview relation label/대상 열기 유지.
- 변경 이력 목록/상세에서 relation 변경 개수 표시.
- 변경 이력 상세 before/after 값에 relation 대상 이름 label 표시.
- rollback preview의 되돌릴 값과 현재값 안전 검사 표에 relation label 표시.
- relation 대상이 열 수 있는 도메인이면 대상 열기 버튼 표시.

현재 게임 실제 세이브 슬롯:
default

수동저장 시:
localStorage idleRpgSaveV22 저장 + DB default 슬롯 갱신

관리자 실제 적용 확인 문구:
APPLY MASTER DATA EDIT

관리자 high risk 추가 확인 문구:
HIGH RISK EDIT

관리자 되돌리기 확인 문구:
ROLLBACK MASTER DATA EDIT

중요한 안전 원칙:
기존 게임 동작을 깨면 안 됨.
localStorage 저장은 계속 유지해야 함.
DB reset/seed가 필요한 단계인지 아닌지 반드시 알려줘.
작업 후 ZIP으로 줘.
커밋 명령어도 마지막에 같이 줘.
명령어마다 반드시 실행 위치를 먼저 적어줘.
주석(`#`, `//`)은 명령어 코드블록 안에 넣지 말고 코드블록 밖에서 설명해줘.
가능하면 작업 후 smoke를 돌려줘.
ZIP에는 전체 프로젝트 파일/폴더를 묶어줘. 단, .env, .gitignore는 바뀐 경우에만 포함하면 돼.

smoke 실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
```

smoke 실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_all.sh
```

다음 추천 단계:
v157 관리자 신규 row 생성 준비용 read-only 설계

구체적으로:
이미 저장된 change log 상세와 rollback preview에서도 relation 값이 코드만 보이지 않도록 before/after에 대상 이름 label을 붙여줘.

rollback 대상도 열 수 있으면 대상 열기 버튼을 붙이고, 기존 rollback guard는 그대로 유지해줘.

이 단계도 가능하면 DB reset/seed 없이 관리자 UI 편의 기능 중심으로 진행해줘.

업로드한 ZIP 기준으로 구조 확인 후, v148부터 이어서 진행해줘.
