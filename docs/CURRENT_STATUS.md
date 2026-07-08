# Current Status

현재 기준: **v156 admin change log relation tools**

## 상태

- 기존 index.html + JS + CSS 게임 정상 동작 유지.
- FastAPI + PostgreSQL master-data 연결 유지.
- localStorage save key `idleRpgSaveV22` 유지.
- DB save snapshot dual write 유지.
- 관리자 페이지 `admin.html` 분리 유지.
- 관리자 guarded edit apply, stale guard, high risk 확인, change log, rollback 유지.

## v156 완료

- 변경 이력 목록에 relation 변경 개수 배지 표시.
- 변경 이력 상세 before/after relation 값에 대상 이름 label 표시.
- 변경 이력 상세 relation 값에서 대상 열기 버튼 유지.
- rollback preview의 되돌릴 값 표에서 relation label과 대상 열기 버튼 표시.
- rollback 현재값 안전 검사 표에서도 relation label 표시.
- 백엔드 change log detail / rollback preview 응답에 relation metadata 추가.

## DB / seed

- DB reset / seed 필요 없음.
- schema 변경 없음.
- `.env`, `.gitignore` 변경 없음.
