# NEXT CHAT HANDOFF

## 사용자/응답 방식

- 사용자는 이 게임 프로젝트의 기획/게임 제작자 이기호입니다.
- 앞으로 사용자를 기호라고 부릅니다.
- 기호는 코딩/터미널/경로에 익숙하지 않습니다.
- 명령어를 줄 때는 항상 먼저 실행 위치를 적습니다.

예:

```bash
위치: 프로젝트 루트
bash tools/run_smoke_core.sh
```

```bash
위치: backend 폴더 + 가상환경 activate 상태
source .venv/Scripts/activate
uvicorn app.main:app --reload
```

```js
위치: 브라우저 개발자도구 Console
checkAdminReadOnlyPageReady();
```

## 프로젝트 기본 정보

- 현재 프로젝트는 아직 Vue가 아니라 `index.html + JS + CSS` 기반 RPG 게임입니다.
- 기존 게임이 정상 작동하는 상태를 유지하면서 FastAPI + PostgreSQL 백엔드 분리를 단계적으로 진행 중입니다.
- 나중에는 Vue 프론트엔드 + FastAPI 백엔드 + PostgreSQL + 관리자 페이지 구조로 옮길 예정입니다.
- 안정성이 최우선입니다.

## GitHub / 로컬 경로

- GitHub repo: `https://github.com/gihohoho/upgrade-rpg.git`
- 프로젝트 루트: `~/Desktop/Upgrade RPG`
- backend 폴더: `~/Desktop/Upgrade RPG/backend`

## 백엔드 실행

```bash
위치: backend 폴더 + 가상환경 activate 상태
source .venv/Scripts/activate
uvicorn app.main:app --reload
```

## PostgreSQL / Docker

- DB 컨테이너: `upgrade_rpg_postgres`
- Adminer 컨테이너: `upgrade_rpg_adminer`
- PostgreSQL host port: `55432`
- Adminer: `8081`
- DATABASE_URL: `postgresql+asyncpg://rpg_user:rpg_password@127.0.0.1:55432/rpg_game`

## 저장 관련

- localStorage save key: `idleRpgSaveV22`
- 현재 게임 실제 세이브 슬롯: `default`
- 수동저장 시 localStorage `idleRpgSaveV22` 저장 + DB `default` 슬롯 갱신

## 관리자 쓰기 dev key

- 관리자 쓰기 dev key: `local-admin-dev-key`
- 관리자 실제 적용 확인 문구: `APPLY MASTER DATA EDIT`
- high risk 추가 확인 문구: `HIGH RISK EDIT`
- 관리자 되돌리기 확인 문구: `ROLLBACK MASTER DATA EDIT`

- 생성 row 삭제 확인 문구: `DELETE CREATED MASTER DATA ROW`

## .env / .gitignore 처리

- 기호 로컬에는 `.env`, `.gitignore`가 이미 있습니다.
- 둘이 바뀌지 않았으면 ZIP에 굳이 포함하지 않습니다.
- 둘 중 하나라도 수정이 필요한 단계라면 ZIP에 포함하고 변경 내용을 반드시 설명합니다.

## 현재 안정 버전

- 최신 안정 버전: **v168: admin create delete rollback**
- 최신 ZIP 이름: **rpg_v168_admin_create_delete_rollback.zip**

v162는 v159의 신규 row 생성 blueprint 위에 생성 draft 입력 UI와 preview-only 백엔드 검증 API를 추가한 버전입니다. 실제 DB insert는 아직 잠금 상태입니다.

## 지금까지 완료된 핵심

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

## v162 세부 완료

- 관리자 신규 row 생성 준비 섹션에 생성 초안 입력 UI 추가.
- blueprint 필드 기반으로 input 자동 구성.
- boolean 필드는 true/false select.
- number 필드는 number input.
- description/admin_note는 textarea.
- preset 필드는 select.
- relation 필드는 실제 후보 목록 기반 select.
- relation 후보 검색/필터 지원.
- dropTables의 owner_type 변경 시 owner_code 후보 목록 자동 전환.
- `POST /api/v1/admin/master-data/create-preview` 추가.
- create-preview는 preview-only입니다.
- code unique 중복 검사 추가.
- relation 대상 존재 검사 추가.
- combo guard 중복 검사 추가.
- 실제 DB insert / commit / change log / rollback은 아직 열지 않았습니다.

## 유지된 안전장치

- 기존 게임 동작 유지.
- localStorage 저장 유지.
- DB save snapshot dual write 유지.
- dev key guard 유지.
- `APPLY MASTER DATA EDIT` 확인 문구 유지.
- high risk 변경 시 `HIGH RISK EDIT` 추가 확인 유지.
- rollback 시 `ROLLBACK MASTER DATA EDIT` 확인 문구 유지.
- stale guard 유지.
- post-edit master-data API verify 유지.

## DB / seed

- v162는 DB reset / seed 필요 없음.
- DB schema 변경 없음.
- `.env`, `.gitignore` 변경 없음.

## smoke 실행

```bash
위치: 프로젝트 루트
bash tools/run_smoke_core.sh
```

```bash
위치: 프로젝트 루트
bash tools/run_smoke_all.sh
```

v162 작업 후 둘 다 통과했습니다.

## 브라우저 확인용

```js
위치: 브라우저 개발자도구 Console
checkAdminReadOnlyPageReady().createDraftPreviewReady
```

예상 결과:

```txt
true
```

```js
위치: 브라우저 개발자도구 Console
getAdminCreateBlueprintReadiness()
```

예상 결과에 들어있어야 하는 값:

```txt
previewReady: true
createApplyReady: false
```

## 다음 추천 단계

### v163 관리자 신규 row 생성 apply 준비

바로 모든 도메인의 실제 생성 기능을 열기보다는, relation 의존도가 낮은 도메인부터 한 개씩 실제 insert apply를 여는 것이 안전합니다.

추천 순서:

1. `characters` 또는 `enhancementGroups`처럼 관계 의존도가 낮은 도메인부터 시작.
2. 생성 확인 문구 추가.
3. admin dev key guard 연결.
4. create change log 기록.
5. 생성 성공 후 새 row 상세 자동 열기.
6. rollback은 삭제가 아니라 soft-disabled 또는 별도 안전 정책을 먼저 설계.

## 다음 채팅에서 먼저 확인할 파일

- `NEXT_CHAT_HANDOFF.md`
- `NEXT_CHAT_PROMPT.md`
- `docs/CURRENT_STATUS.md`
- `docs/NEXT_STEPS.md`
- `docs/ADMIN_CREATE_DRAFT_PREVIEW.md`

추가 완료: v165 admin create apply limited. `characters`, `enhancementGroups` 신규 row 생성 apply만 제한적으로 열림. 생성 확인 문구는 `CREATE MASTER DATA ROW`. create rollback/delete는 아직 잠금. DB reset/seed 필요 없음.

## v168 세부 완료

- `create-apply`로 생성된 제한 도메인 row 삭제 되돌리기 preview/apply 추가.
- 대상 도메인: `characters`, `enhancementGroups`.
- 현재값이 생성 당시 값과 다르면 삭제 차단.
- 연결 데이터 blocker가 있으면 삭제 차단.
- 실제 삭제 적용은 관리자 쓰기 dev key와 `DELETE CREATED MASTER DATA ROW` 확인 문구 필요.
- 삭제 성공 시 `admin_change_logs.action=create_delete` 기록.
- DB reset / seed 필요 없음.

## 다음 추천 단계

- v169 create_delete 이력 기반 restore preview 설계, 또는 fieldZones처럼 relation 의존도가 낮은 도메인의 create apply 제한 확장.
