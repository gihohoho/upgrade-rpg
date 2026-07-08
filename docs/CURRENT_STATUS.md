# Current Status

현재 기준: **v174 admin collapsed panel style fix**

## 상태

- 기존 index.html + JS + CSS 게임 정상 동작 유지.
- FastAPI + PostgreSQL master-data 연결 유지.
- localStorage save key `idleRpgSaveV22` 유지.
- DB save snapshot dual write 유지.
- 관리자 페이지 `admin.html` 분리 유지.
- 관리자 guarded edit apply, stale guard, high risk 확인, change log, rollback 유지.
- 신규 row create/delete/restore 제한 흐름 유지.

## v174 완료

- 접힌 섹션 스타일을 `.section`, `.filter-panel`, `.field-help-panel` 모두에서 통일.
- `필드 용어 도움말`, `신규 row 생성 준비` 같은 filter/help 기반 탭이 안쪽 header만 색칠되던 문제 수정.
- 접힌 filter/help 패널의 padding을 보정해 카드 전체가 접힘 상태로 보이게 처리.
- `getAdminLayoutShellReadiness().collapsedPanelStyleReady` 확인 상태 추가.
- 기존 관리자 API, 적용/삭제/복원 기능, smoke 함수 유지.

## DB / seed

- DB reset / seed 필요 없음.
- schema 변경 없음.
- `.env`, `.gitignore` 변경 없음.


## v173 보강

- sticky header 높이에 맞춰 sidebar top offset을 자동 보정.
- 필드 용어 도움말, 신규 row 생성 준비, 관리자 변경 이력 기본 접기 적용.
- 접힌 섹션 색상/테두리/버튼 표시 강화.


## v174 보강

- 접힌 탭 공통 CSS 보정.
- `.filter-panel` / `.field-help-panel` 기반 접힘 스타일 통일.
- DB reset / seed 필요 없음.
