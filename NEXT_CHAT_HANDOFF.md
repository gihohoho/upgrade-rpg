# NEXT CHAT HANDOFF

## 사용자/응답 방식

- 사용자는 이 게임 프로젝트의 기획/게임 제작자 이기호입니다.
- 앞으로 사용자를 **기호**라고 부릅니다.
- 기호는 코딩/터미널/경로에 익숙하지 않습니다.
- 명령어를 줄 때는 항상 먼저 실행 위치를 적습니다.
- 코드블록 안에 설명용 주석 기호를 넣지 않습니다. 설명은 코드블록 밖에서 합니다.
- 커밋 명령어는 마지막에 `git add`부터 `git push`까지 한 번에 제공합니다.
- 기호가 “다음 단계”라고 하면, 앞으로 무엇을 할지 먼저 설명하고 진행합니다.

## 프로젝트 기본 정보

- 현재 프로젝트는 아직 Vue가 아니라 `index.html + JS + CSS` 기반 RPG 게임입니다.
- 기존 게임이 정상 작동하는 상태를 유지하면서 FastAPI + PostgreSQL 백엔드 분리를 단계적으로 진행 중입니다.
- 나중에는 Vue 프론트엔드 + FastAPI 백엔드 + PostgreSQL + 관리자 페이지 구조로 옮길 예정입니다.
- 안정성이 최우선입니다.

## 로컬 정보

- GitHub repo: `https://github.com/gihohoho/upgrade-rpg.git`
- 프로젝트 루트: `~/Desktop/Upgrade RPG`
- backend 폴더: `~/Desktop/Upgrade RPG/backend`
- DB 컨테이너: `upgrade_rpg_postgres`
- Adminer 컨테이너: `upgrade_rpg_adminer`
- PostgreSQL host port: `55432`
- Adminer: `8081`
- DATABASE_URL: `postgresql+asyncpg://rpg_user:rpg_password@127.0.0.1:55432/rpg_game`

## 백엔드 실행

```bash
위치: backend 폴더 + 가상환경 activate 상태
source .venv/Scripts/activate
uvicorn app.main:app --reload
```

## 저장 / 관리자 확인 문구

- localStorage save key: `idleRpgSaveV22`
- 현재 게임 실제 세이브 슬롯: `default`
- 관리자 쓰기 dev key: `local-admin-dev-key`
- 관리자 실제 적용 확인 문구: `APPLY MASTER DATA EDIT`
- high risk 추가 확인 문구: `HIGH RISK EDIT`
- 관리자 되돌리기 확인 문구: `ROLLBACK MASTER DATA EDIT`
- 신규 row 생성 확인 문구: `CREATE MASTER DATA ROW`
- 생성 row 삭제 확인 문구: `DELETE CREATED MASTER DATA ROW`
- 삭제 row 복원 확인 문구: `RESTORE DELETED CREATED ROW`
- 생성→삭제→복원 일괄 점검 확인 문구: `RUN CREATE DELETE RESTORE CHECK`

## .env / .gitignore 처리

- 기호 로컬에는 `.env`, `.gitignore`가 이미 있습니다.
- 둘이 바뀌지 않았으면 ZIP에 포함하지 않습니다.
- 둘 중 하나라도 수정이 필요한 단계라면 ZIP에 포함하고 변경 내용을 반드시 설명합니다.

## 현재 안정 버전

- 최신 안정 버전: **v187 admin change logs split**
- 새 채팅용 ZIP: **rpg_v187_admin_change_logs_split_ready.zip**

## 새 채팅에서 먼저 볼 파일

1. `NEXT_CHAT_HANDOFF.md`
2. `docs/CURRENT_STATUS.md`
3. `docs/NEXT_STEPS.md`
4. `docs/README.md`
5. `docs/PROJECT_STRUCTURE.md`

## 현재 핵심 상태

- 기존 게임 정상 동작 유지.
- master-data PostgreSQL → FastAPI → 브라우저 연결 유지.
- 백엔드 실패 시 static JS fallback 유지.
- save snapshot dual write 유지.
- 관리자 guarded edit apply / rollback / create / delete / restore 제한 흐름 유지.
- 생성→삭제→복원 일괄 점검 UI 유지.
- 관리자 JS 분리 전 readiness UI 유지.
- 관리자 layout shell은 `src/api/admin-layout-shell.js`로 실제 분리 완료.
- change logs는 `src/api/admin/admin-change-logs.js`로 실제 1차 분리 완료.
- `admin-page-readonly.js`에는 호환 wrapper가 남아 있습니다.

## 현재 create apply 열린 도메인

- `characters`
- `enhancementGroups`
- `fieldZones`
- `bosses`
- `skills`
- `dropTables`
- `itemTemplates`
- `dropTableItems`
- `skillLevels`
- `enhancementLevels`
- `characterSkills`

위 도메인들은 생성 row delete/restore도 제한적으로 열려 있습니다.

## v187 완료

- `src/api/admin/` 폴더 생성.
- `src/api/admin/admin-change-logs.js` 신규 추가.
- 변경 이력 필터/목록/상세/rollback/create-delete/restore 구현을 외부 파일로 1차 분리.
- `admin-page-readonly.js`에는 기존 window export 호환 wrapper 유지.
- `admin.html` script 순서 변경: game api → layout shell → change logs → admin page.
- 새 함수: `getAdminChangeLogsReadiness()`.
- `checkAdminReadOnlyPageReady().changeLogsExternalReady`가 true면 정상입니다.
- 새 smoke: `tools/smoke_admin_change_logs_split.js`.
- core smoke에 위 smoke를 포함했습니다.
- 새 쓰기 도메인 오픈 없음, DB schema 변경 없음, DB reset / seed 필요 없음.
- `.env`, `.gitignore` 변경 없음.

## 브라우저 확인

```js
위치: 브라우저 개발자도구 Console
checkAdminReadOnlyPageReady().version
```

예상 결과:

```txt
v187.admin-change-logs-split
```

추가 확인:

```js
위치: 브라우저 개발자도구 Console
checkAdminReadOnlyPageReady().changeLogsExternalReady
```

예상 결과:

```txt
true
```

그리고:

```js
위치: 브라우저 개발자도구 Console
window.RpgAdminChangeLogs.VERSION
```

예상 결과:

```txt
v187.admin-change-logs-split
```

## 다음 추천 단계

**v188 create lifecycle split contract**를 추천합니다.

바로 `create lifecycle` 구현을 외부 파일로 옮기지 말고, 먼저 아래 계약을 고정하는 것이 안전합니다.

- 생성 초안 관련 window export 목록
- 생성→삭제→복원 batch check 함수 목록
- 생성/삭제/복원 결과 렌더링 함수 목록
- 확인 문구 상수 목록
- DOM target 목록
- delegated action 목록
- 다음 후보 파일명 `src/api/admin/admin-create-lifecycle.js`

그 다음 v189에서 실제 `admin-create-lifecycle.js` 분리로 넘어가는 흐름이 좋습니다.
