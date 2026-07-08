# Current Status

현재 기준: **v162 admin create draft preview**

## 상태

- 기존 index.html + JS + CSS 게임 정상 동작 유지.
- FastAPI + PostgreSQL master-data 연결 유지.
- localStorage save key `idleRpgSaveV22` 유지.
- DB save snapshot dual write 유지.
- 관리자 페이지 `admin.html` 분리 유지.
- 관리자 guarded edit apply, stale guard, high risk 확인, change log, rollback 유지.

## v162 완료

- 신규 row 생성 blueprint 기반 draft 입력 UI 추가.
- 생성 초안 preview-only API 추가.
- code unique 중복 검사 추가.
- relation 대상 존재 검사 추가.
- skillLevels / enhancementLevels / characterSkills combo guard 중복 검사 추가.
- dropTables owner_type + owner_code 조합 검사 추가.
- 실제 insert apply는 아직 잠금 상태로 유지.

## DB / seed

- DB reset / seed 필요 없음.
- schema 변경 없음.
- `.env`, `.gitignore` 변경 없음.
