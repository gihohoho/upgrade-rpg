# Upgrade RPG

현재 안정 버전: **v188 admin create lifecycle split contract**

새 채팅 인수인계 ZIP: **rpg_v188_admin_create_lifecycle_split_contract_ready.zip**

현재 프로젝트는 아직 Vue가 아니라 `index.html + JS + CSS` 기반 RPG 게임입니다. 기존 게임 동작을 유지하면서 FastAPI + PostgreSQL + 관리자 페이지 구조로 단계적으로 분리 중입니다.

## 현재 핵심 상태

- 게임 localStorage 저장 유지: `idleRpgSaveV22`
- DB save snapshot dual write 유지
- master-data PostgreSQL → FastAPI → 브라우저 연결 유지
- 백엔드 실패 시 static JS fallback 유지
- 관리자 페이지 `admin.html` 분리 유지
- 관리자 edit/create/delete/restore 제한 기능 유지
- 관리자 sidebar / sticky header / 접기·펼치기 shell 유지
- 접힌 탭 공통 CSS 보정 완료
- `fieldZones` 신규 row create apply 제한 오픈 완료
- `bosses` 신규 row create apply 제한 오픈 완료
- `skills`, `dropTables` 신규 row create apply 제한 오픈 완료
- `itemTemplates`, `dropTableItems` 신규 row create apply 제한 오픈 완료
- `skillLevels`, `enhancementLevels`, `characterSkills` 신규 row create apply 제한 오픈 완료
- 관리자 신규 row 생성·삭제·복원 점검 가이드 추가 완료
- 삭제 preview 차단 기준 표시와 변경 이력 action 바로가기 추가 완료
- 생성→삭제→복원 일괄 점검 버튼 추가 완료
- 관리자 JS 분리 전 readiness 진단 UI 추가 완료
- 관리자 change logs 구현 1차 외부 파일 분리 완료
- 관리자 create lifecycle 실제 분리 전 계약 고정 완료

## 새 채팅에서 먼저 볼 파일

- `NEXT_CHAT_HANDOFF.md`
- `NEXT_CHAT_PROMPT.md`
- `docs/CURRENT_STATUS.md`
- `docs/NEXT_STEPS.md`
- `docs/PROJECT_STRUCTURE.md`
- `docs/README.md`

## smoke 실행

```bash
위치: 프로젝트 루트
bash tools/run_smoke_core.sh
```

```bash
위치: 프로젝트 루트
bash tools/run_smoke_all.sh
```

## 다음 추천 단계

다음은 `create lifecycle` 실제 분리 1단계가 좋습니다. v188에서 함수/window/DOM/확인 문구 계약을 고정했으므로, v189에서는 `src/api/admin/admin-create-lifecycle.js`를 만들고 `admin-page-readonly.js`에는 호환 wrapper를 남기는 방향이 안전합니다.

## DB / env

- DB reset / seed 필요 없음.
- DB schema 변경 없음.
- `.env`, `.gitignore` 변경 없음.
- 이 ZIP에는 `.env`, `.gitignore`를 포함하지 않았습니다.


## v185 완료

- `src/api/admin-layout-shell.js` 신규 추가
- 관리자 layout shell 기능을 `admin-page-readonly.js` 밖으로 1차 분리
- `admin-page-readonly.js`에는 기존 window export 호환 wrapper 유지
- `admin.html` script 순서: game api → layout shell → admin page
- DB reset / seed 필요 없음


## v186 완료

- `change logs` 분리 전 계약을 `contract-frozen-v186` 상태로 고정
- 변경 이력 API/window export/DOM target 진단 추가
- `getAdminChangeLogSplitContractReadiness()` 추가
- `renderAdminChangeLogSplitContractReadiness()` 추가
- 새 smoke `tools/smoke_admin_change_log_split_contract.js` 추가
- 실제 JS 파일 분리는 아직 하지 않음
- DB reset / seed 필요 없음


## v187 완료

- `src/api/admin/admin-change-logs.js` 신규 추가
- 변경 이력 필터/목록/상세/rollback/create-delete/restore 구현 1차 분리
- `admin-page-readonly.js`에는 호환 wrapper 유지
- `admin.html` script 순서: game api → layout shell → change logs → admin page
- 새 smoke `tools/smoke_admin_change_logs_split.js` 추가
- DB reset / seed 필요 없음


## v188 완료

- `create lifecycle` 실제 분리 전 계약을 `contract-frozen-v188` 상태로 고정
- 다음 후보 파일 `src/api/admin/admin-create-lifecycle.js` 고정
- 생성 초안/생성 apply/생성→삭제→복원 batch check 함수 목록 고정
- 확인 문구/DOM target/delegated action 목록 고정
- 새 smoke `tools/smoke_admin_create_lifecycle_split_contract.js` 추가
- 실제 JS 파일 분리는 아직 하지 않음
- DB reset / seed 필요 없음
