# Current Status

현재 기준: **v183 admin create lifecycle batch check**

이 패키지 기준 ZIP: **rpg_v183_create_lifecycle_batch_check_ready.zip**

## 현재 상태

- 기존 `index.html + JS + CSS` 게임 정상 동작 유지.
- FastAPI + PostgreSQL master-data 연결 유지.
- master-data 기본 mode는 `auto` 유지.
- 백엔드 실패 시 static JS 데이터 fallback 유지.
- localStorage save key `idleRpgSaveV22` 유지.
- DB save snapshot dual write 유지.
- 관리자 페이지 `admin.html` 분리 유지.
- 관리자 guarded edit apply, stale guard, high risk 확인, change log, rollback 유지.
- 신규 row create/delete/restore 제한 흐름 유지.
- 관리자 페이지 레이아웃 shell, sidebar, sticky header, 접기/펼치기 유지.

## v183 완료

- 관리자 `신규 row 생성·삭제·복원 점검` 섹션에 일괄 점검 카드를 추가.
- 현재 생성 초안 기준으로 아래 순서를 한 번에 실행하는 버튼 추가.
  - 생성 preview
  - 생성 apply
  - 삭제 preview
  - 삭제 apply
  - 복원 preview
  - 복원 apply
- 일괄 점검 전용 확인 문구 추가: `RUN CREATE DELETE RESTORE CHECK`.
- dev key, 생성 확인 문구, 브라우저 confirm을 모두 통과해야 실행되도록 유지.
- 단계별 결과 테이블과 요약 카드를 표시.
- 기존 개별 생성/삭제/복원 버튼은 그대로 유지.
- 기존 생성 row 삭제/복원 결과 요약 카드 유지.
- 새 쓰기 도메인 오픈 없음.
- DB reset / seed 없이 진행 가능.

## v182 완료

- 생성 row 삭제 preview/apply 결과 상단에 큰 요약 카드 추가.
- 삭제 결과에서 현재값 불일치, 연결 검사 수, 차단 guard 수, 차단 row 수를 바로 표시.
- 삭제 row 복원 preview/apply 결과 상단에 큰 요약 카드 추가.
- 복원 결과에서 id/code 충돌, validation error, relation 값 수를 바로 표시.
- 백엔드 응답에 `dependencyCheckCount`, `dependencyBlockerGuardCount`, `restoreConflictCount` 보조 count 추가.
- 새 쓰기 도메인 오픈 없음.
- DB reset / seed 없이 진행 가능.

## 제한 생성/삭제/복원 상태

현재 신규 row 실제 생성 apply가 열린 도메인:

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

현재 생성 row delete/restore가 열린 도메인도 위와 같습니다.

## 이전 완료

- v183: 생성→삭제→복원 일괄 점검 UI.
- v182: 생성 row 삭제/복원 결과 요약 카드와 blocker count 표시 강화.
- v181: 생성 lifecycle 삭제 차단 기준 표시 + 변경 이력 action 바로가기.
- v180: 생성·삭제·복원 브라우저 점검 UI.
- v179: `skillLevels`, `enhancementLevels`, `characterSkills` 신규 row 생성 apply 제한 오픈.
- v178: `itemTemplates`, `dropTableItems` 신규 row 생성 apply 제한 오픈.
- v177: `skills`, `dropTables` 신규 row 생성 apply 제한 오픈.
- v176: `bosses` 신규 row 생성 apply 제한 오픈.
- v175: `fieldZones` 신규 row 생성 apply 제한 오픈.
- v174: 관리자 접힌 패널 스타일 보정.

## DB / seed

- DB reset / seed 필요 없음.
- DB schema 변경 없음.
- `.env`, `.gitignore` 변경 없음.

## smoke

아래 둘 다 통과한 상태입니다.

```bash
위치: 프로젝트 루트
bash tools/run_smoke_core.sh
```

```bash
위치: 프로젝트 루트
bash tools/run_smoke_all.sh
```
