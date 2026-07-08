# NEXT CHAT HANDOFF

## 사용자/응답 방식

- 사용자는 이 게임 프로젝트의 기획/게임 제작자 이기호입니다.
- 앞으로 사용자를 **기호**라고 부릅니다.
- 기호는 코딩/터미널/경로에 익숙하지 않습니다.
- 명령어를 줄 때는 항상 먼저 실행 위치를 적습니다.
- 코드블록 안에 설명용 주석 기호를 넣지 않습니다. 설명은 코드블록 밖에서 합니다.
- 커밋 명령어는 마지막에 `git add`부터 `git push`까지 한 번에 제공합니다.

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

## 관리자 쓰기 dev key / 확인 문구

- 관리자 쓰기 dev key: `local-admin-dev-key`
- 관리자 실제 적용 확인 문구: `APPLY MASTER DATA EDIT`
- high risk 추가 확인 문구: `HIGH RISK EDIT`
- 관리자 되돌리기 확인 문구: `ROLLBACK MASTER DATA EDIT`
- 신규 row 생성 확인 문구: `CREATE MASTER DATA ROW`
- 생성 row 삭제 확인 문구: `DELETE CREATED MASTER DATA ROW`
- 삭제 row 복원 확인 문구: `RESTORE DELETED CREATED ROW`

## .env / .gitignore 처리

- 기호 로컬에는 `.env`, `.gitignore`가 이미 있습니다.
- 둘이 바뀌지 않았으면 ZIP에 굳이 포함하지 않습니다.
- 둘 중 하나라도 수정이 필요한 단계라면 ZIP에 포함하고 변경 내용을 반드시 설명합니다.

## 현재 안정 버전

- 최신 안정 버전: **v176: create apply bosses**
- 새 채팅용 ZIP: **rpg_v176_bosses_create_apply_ready.zip**
- 이 ZIP은 `bosses` 신규 row 생성 apply 제한 오픈과 생성 row 삭제/복원 안전검사 확장을 포함합니다.

## 새 채팅에서 먼저 볼 파일

1. `NEXT_CHAT_HANDOFF.md`
2. `docs/CURRENT_STATUS.md`
3. `docs/NEXT_STEPS.md`
4. `docs/README.md`
5. `docs/PROJECT_STRUCTURE.md`

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
32. `characters`, `enhancementGroups` 신규 row 실제 생성 apply 제한 오픈 완료.
33. `create` 이력 기반 생성 row 삭제 preview/apply 제한 오픈 완료.
34. `create_delete` 이력 기반 삭제 row 복원 preview/apply 제한 오픈 완료.
35. 관리자 페이지 sidebar / sticky header / 섹션 접기·펼치기 / footer 완료.
36. 접힌 섹션 공통 CSS 보정 완료.
37. `fieldZones` 신규 row create apply 제한 오픈 완료.
38. `fieldZones` 생성 row 삭제/복원 allow-list 및 dropTables dependency guard 완료.
39. `bosses` 신규 row create apply 제한 오픈 완료.
40. `bosses` 생성 row 삭제/복원 allow-list 및 dropTables dependency guard 완료.

## v176 create apply bosses

- 신규 row 실제 생성 apply 제한 도메인에 `bosses`를 추가했습니다.
- `characters`, `enhancementGroups`, `fieldZones`, `bosses`만 생성 apply가 가능합니다.
- `itemTemplates`, `skills`, `dropTables`, `dropTableItems`는 계속 생성 apply 잠금 상태입니다.
- `bosses` 생성 row 삭제/복원도 제한 allow-list에 추가했습니다.
- `bosses` 삭제 preview에서 `dropTables.owner_type=boss + owner_code` 연결 검사를 수행합니다.
- DB schema 변경 없음, DB reset / seed 필요 없음.
- `.env`, `.gitignore` 변경 없음.

## v175 create apply fieldZones

- 신규 row 실제 생성 apply 제한 도메인에 `fieldZones`를 추가했습니다.
- `fieldZones` 생성 row 삭제/복원도 제한 allow-list에 추가했습니다.
- `fieldZones` 삭제 preview에서 `dropTables.owner_type=field + owner_code` 연결 검사를 수행합니다.
- DB schema 변경 없음, DB reset / seed 필요 없음.
- `.env`, `.gitignore` 변경 없음.

## v172~v174 관리자 레이아웃 정리

### v172 admin layout navigation shell

- 관리자 페이지에 sidebar navigation shell 추가.
- 상단 header sticky 처리.
- 주요 관리자 섹션 접기/펼치기 버튼 추가.
- 접힘 상태 localStorage 저장.
- footer를 관리자 버전/상태 표시 영역으로 정리.
- 기존 edit/create/delete/restore 기능 유지.

### v173 admin layout collapse polish

- sidebar sticky top offset을 header 높이 기준으로 자동 보정.
- `필드 용어 도움말`, `신규 row 생성 준비`, `관리자 변경 이력` 기본 상태를 접기로 변경.
- 접힌 섹션을 amber 계열 색상으로 구분.

### v174 admin collapsed panel style fix

- 접힌 탭 공통 CSS 보정.
- `.section`, `.filter-panel`, `.field-help-panel` 기반 접힘 상태가 모두 같은 amber 계열 카드 스타일로 보이게 수정.
- `필드 용어 도움말`, `신규 row 생성 준비`처럼 filter/help panel 구조인 탭이 안쪽 header만 색칠되던 문제 수정.
- `getAdminLayoutShellReadiness().collapsedPanelStyleReady` 확인 상태 추가.

## DB / seed

- v176 기준 DB reset / seed 필요 없음.
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

v176 작업 후 둘 다 통과했습니다.

## 브라우저 확인용

```js
위치: 브라우저 개발자도구 Console
checkAdminReadOnlyPageReady().layoutShellReady
```

예상 결과:

```txt
true
```

```js
위치: 브라우저 개발자도구 Console
getAdminLayoutShellReadiness().collapsedPanelStyleReady
```

예상 결과:

```txt
true
```

## 다음 추천 단계

다음은 **bosses 생성/삭제/복원 브라우저 검증**이 좋습니다.

안전한 순서:

1. 브라우저에서 `bosses` 생성 preview/apply를 실제 확인.
2. 생성된 `bosses` 삭제 preview에서 `dropTables.owner_type=boss + owner_code` blocker 표시 확인.
3. 삭제/복원 apply까지 확인.
4. `itemTemplates`, `skills`, `dropTables`, `dropTableItems` 생성 apply는 아직 열지 않음.
5. 다음 코드 단계는 create/delete/restore UI의 dependency 표시 강화 또는 관리자 코드 분리 준비를 추천.
