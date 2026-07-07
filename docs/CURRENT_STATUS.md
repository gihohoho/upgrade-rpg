# Current Status

현재 기준: **v153 admin relation preview tools**

## 상태

- 기존 index.html + JS + CSS 게임 정상 동작 유지.
- FastAPI + PostgreSQL master-data 연결 유지.
- localStorage save key `idleRpgSaveV22` 유지.
- DB save snapshot dual write 유지.
- 관리자 페이지 `admin.html` 분리 유지.
- 관리자 guarded edit apply, stale guard, high risk 확인, change log, rollback 유지.

## v153 완료

- 변경 preview와 초안 before/after 표에서 relation 값에 대상 이름 label 표시.
- relation 변경 행에 `relation` 배지 표시.
- 변경 요약 배너에 relation 변경 개수 표시.
- relation 대상 빠른 열기 버튼 추가.
- relation 대상 빠른 열기는 code로 카탈로그를 조회한 뒤 상세를 엽니다.

## DB / seed

- DB reset / seed 필요 없음.
- schema 변경 없음.
- `.env`, `.gitignore` 변경 없음.
