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

- 최신 안정 버전: **v185: admin layout shell split**
- 새 채팅용 ZIP: **rpg_v185_admin_layout_shell_split_ready.zip**
- 이 ZIP은 신규 row 생성·삭제·복원 일괄 점검 UI와 관리자 JS 분리 전 readiness 진단 UI를 포함합니다.

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
41. `skills`, `dropTables` 신규 row create apply 제한 오픈 완료.
42. `skills`, `dropTables` 생성 row 삭제/복원 allow-list 및 dependency guard 완료.
43. `itemTemplates`, `dropTableItems` 신규 row create apply 제한 오픈 완료.
44. `itemTemplates`, `dropTableItems` 생성 row 삭제/복원 allow-list 및 dependency guard 완료.
45. `skillLevels`, `enhancementLevels`, `characterSkills` 신규 row create apply 제한 오픈 완료.
46. `skillLevels`, `enhancementLevels`, `characterSkills` 생성 row 삭제/복원 allow-list 및 id 기반 guard 완료.
47. 신규 row 생성·삭제·복원 점검 UI와 createLifecycle 메타데이터 추가 완료.
48. change log action filter를 실제 action 값 기준으로 정리 완료.
49. 생성 lifecycle 삭제 preview 차단 기준 표시와 변경 이력 action 바로가기 완료.
50. 생성 row 삭제/복원 preview 결과 요약 카드와 dependency/conflict count 표시 강화 완료.
51. 생성→삭제→복원 일괄 점검 버튼 추가 완료.
52. 관리자 JS 분리 전 readiness 진단 UI 추가 완료.


## v185 admin layout shell split

- 관리자 페이지에 `관리자 JS 분리 준비` 섹션을 추가했습니다.
- 실제 파일 분리는 하지 않고 script 순서, 필수 global, `window.RpgAdminReadOnlyPage` export 계약을 진단합니다.
- `getAdminJsSplitReadiness()`와 `renderAdminJsSplitReadiness()`를 추가했습니다.
- `checkAdminReadOnlyPageReady().adminJsSplitReadinessReady`가 true면 정상입니다.
- 다음 실제 분리 후보는 DB 쓰기와 무관한 `layout shell`입니다.
- 새 smoke `tools/smoke_admin_js_split_readiness.js`를 추가하고 core smoke에 포함했습니다.
- 새 쓰기 도메인 오픈 없음, DB schema 변경 없음, DB reset / seed 필요 없음.
- `.env`, `.gitignore` 변경 없음.

## v183 admin create lifecycle batch check

- 생성 row 삭제 preview/apply 결과 상단에 큰 요약 카드를 추가했습니다.
- 삭제 결과에서 현재값 불일치, 연결 검사 수, 차단 guard 수, 차단 row 수를 바로 표시합니다.
- 삭제 row 복원 preview/apply 결과 상단에 큰 요약 카드를 추가했습니다.
- 복원 결과에서 id/code 충돌, validation error, relation 값 수를 바로 표시합니다.
- 백엔드 응답에 `dependencyCheckCount`, `dependencyBlockerGuardCount`, `restoreConflictCount` 보조 count를 추가했습니다.
- `checkAdminReadOnlyPageReady().createLifecycleResultSummaryReady`가 true면 정상입니다.
- 새 쓰기 도메인 오픈 없음, DB schema 변경 없음, DB reset / seed 필요 없음.
- `.env`, `.gitignore` 변경 없음.

## v181 admin create lifecycle guard helper

- `createLifecycle` 메타데이터에 `deleteDependencyGuards`, `deleteGuardMode`를 추가했습니다.
- 관리자 `신규 row 생성·삭제·복원 점검` 섹션에 삭제 preview 차단 기준을 표시합니다.
- 변경 이력 action 필터 바로가기 버튼을 추가했습니다.
  - `create` 이력 보기
  - `create_delete` 이력 보기
  - `create_delete_restore` 이력 보기
- `checkAdminReadOnlyPageReady().createLifecycleDependencyGuideReady`가 true면 정상입니다.
- 새 쓰기 도메인 오픈 없음, DB schema 변경 없음, DB reset / seed 필요 없음.
- `.env`, `.gitignore` 변경 없음.

## v180 admin create lifecycle guide

- 관리자 페이지에 `신규 row 생성·삭제·복원 점검` 섹션을 추가했습니다.
- `create-blueprint` 응답에 `createLifecycle` 메타데이터를 추가했습니다.
- 생성/삭제/복원 가능 여부, id/code 삭제 key, combo guard, JSON/asset 잠금 필드를 표시합니다.
- 변경 이력 action 필터를 실제 저장되는 `update`, `rollback`, `create`, `create_delete`, `create_delete_restore` 기준으로 정리했습니다.
- 새 쓰기 도메인을 열지 않았고 기존 dev key/확인 문구/preview guard는 유지합니다.
- DB schema 변경 없음, DB reset / seed 필요 없음.
- `.env`, `.gitignore` 변경 없음.

## v179 create apply level/link tables

- 신규 row 실제 생성 apply 제한 도메인에 `skillLevels`, `enhancementLevels`, `characterSkills`를 추가했습니다.
- 현재 `characters`, `enhancementGroups`, `fieldZones`, `bosses`, `skills`, `dropTables`, `itemTemplates`, `dropTableItems`, `skillLevels`, `enhancementLevels`, `characterSkills` 생성 apply가 가능합니다.
- `skillLevels`, `enhancementLevels`, `characterSkills` 생성 row 삭제/복원도 제한 allow-list에 추가했습니다.
- 위 3개 도메인은 `code`가 없는 relation/level row라 id 기반 삭제/복원 흐름을 사용합니다.
- `skillLevels`는 `skill_code + level` 중복을 차단합니다.
- `enhancementLevels`는 `group_code + from_level` 중복을 차단하고 `to_level > from_level`, `success_rate >= 0`, `gold_cost >= 0`을 검사합니다.
- `characterSkills`는 `character_code + skill_code` 중복을 차단하고 `sort_order >= 0`을 검사합니다.
- JSON 계열 필드는 생성 입력에서 계속 잠금 상태입니다.
- DB schema 변경 없음, DB reset / seed 필요 없음.
- `.env`, `.gitignore` 변경 없음.

## v178 create apply itemTemplates/dropTableItems

- 신규 row 실제 생성 apply 제한 도메인에 `itemTemplates`, `dropTableItems`를 추가했습니다.
- `itemTemplates`, `dropTableItems` 생성 row 삭제/복원도 제한 allow-list에 추가했습니다.
- `itemTemplates` 삭제 preview에서 `dropTableItems.item_template_code`, `itemInstances.template_code` 연결 검사를 수행합니다.
- `dropTableItems`는 code 없는 leaf row라 id 기반 삭제/복원 흐름을 제한 오픈했습니다.
- `dropTableItems` 생성 검증에서 `rate`, `min_quantity`, `max_quantity` 범위를 검사합니다.
- JSON/asset 계열 필드(`base_stats_json`, `options_json`, `conditions_json`, `icon_url`)는 생성 입력에서 계속 잠금 상태입니다.
- DB schema 변경 없음, DB reset / seed 필요 없음.
- `.env`, `.gitignore` 변경 없음.

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

- v183 기준 DB reset / seed 필요 없음.
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

v183 작업 후 둘 다 통과했습니다.

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

다음은 **change logs 분리 전 readiness/contract smoke 추가**가 좋습니다. layout shell은 이미 외부 파일로 분리되었습니다.

안전한 순서:

1. 브라우저에서 `skillLevels` 생성 preview/apply를 실제 확인.
2. `skill_code + level` 중복 검증 확인.
3. 생성된 `skillLevels` 삭제 preview에서 결과 요약 카드가 보이는지 확인.
4. 생성된 `skillLevels`가 id 기반으로 삭제/복원되는지 확인.
5. 브라우저에서 `enhancementLevels` 생성 preview/apply를 실제 확인.
6. `group_code + from_level`, `to_level > from_level`, 확률/비용 검증 확인.
7. 생성된 `enhancementLevels` 삭제/복원 preview에서 결과 요약 카드가 보이는지 확인.
8. 브라우저에서 `characterSkills` 생성 preview/apply를 실제 확인.
9. `character_code + skill_code` 중복 검증 확인.
10. 생성된 `characterSkills` 삭제/복원 preview에서 결과 요약 카드가 보이는지 확인.
11. 이후 관리자 페이지 코드 분리 준비를 추천.


## v185 admin layout shell split

- `src/api/admin-layout-shell.js` 신규 추가.
- sidebar / sticky header / section collapse / active nav를 외부 JS로 분리.
- `admin-page-readonly.js`에는 기존 window export 호환 wrapper 유지.
- `admin.html` script 로드 순서에 `src/api/admin-layout-shell.js` 추가.
- 새 smoke: `tools/smoke_admin_layout_shell_split.js`.
- 다음 추천: change logs 분리 전 contract smoke 고정.
- DB reset / seed 필요 없음.
