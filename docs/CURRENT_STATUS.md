# Current Status

현재 기준: **v159 admin create blueprint readonly**

## 상태

- 기존 index.html + JS + CSS 게임 정상 동작 유지.
- FastAPI + PostgreSQL master-data 연결 유지.
- localStorage save key `idleRpgSaveV22` 유지.
- DB save snapshot dual write 유지.
- 관리자 페이지 `admin.html` 분리 유지.
- 관리자 guarded edit apply, stale guard, high risk 확인, change log, rollback 유지.

## v159 완료

- 신규 row 생성 준비용 read-only blueprint API 추가.
- 관리자 페이지에 신규 row 생성 준비 섹션 추가.
- 도메인별 필수 필드/기본값/unique/combo guard/relation 후보 표시.
- 실제 insert API는 아직 잠금 상태로 유지.
- v156 change log/rollback relation label 기능 유지.

## DB / seed

- DB reset / seed 필요 없음.
- schema 변경 없음.
- `.env`, `.gitignore` 변경 없음.
