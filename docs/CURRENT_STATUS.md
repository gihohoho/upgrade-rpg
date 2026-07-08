# Current Status

현재 기준: **v175 create apply fieldZones**

이 패키지 기준 ZIP: **rpg_v175_fieldzones_create_apply_ready.zip**

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

## v175 완료

- 신규 row 실제 생성 apply 제한 도메인에 `fieldZones` 추가.
- `fieldZones` 생성 row 삭제/복원 allow-list 추가.
- `fieldZones` 생성 row 삭제 전 `dropTables.owner_type=field + owner_code` dependency guard 추가.
- `itemTemplates`, `skills`, `dropTables`, `dropTableItems` 생성 apply는 계속 잠금 유지.
- DB reset / seed 없이 진행 가능.

## v174 완료

- 접힌 섹션 스타일을 `.section`, `.filter-panel`, `.field-help-panel` 모두에서 통일.
- `필드 용어 도움말`, `신규 row 생성 준비` 같은 filter/help 기반 탭이 안쪽 header만 색칠되던 문제 수정.
- 접힌 filter/help 패널의 padding을 보정해 카드 전체가 접힘 상태로 보이게 처리.
- `getAdminLayoutShellReadiness().collapsedPanelStyleReady` 확인 상태 추가.
- 기존 관리자 API, 적용/삭제/복원 기능, smoke 함수 유지.

## v172~v173 레이아웃 보강 요약

- sticky header 높이에 맞춰 sidebar top offset 자동 보정.
- `필드 용어 도움말`, `신규 row 생성 준비`, `관리자 변경 이력` 기본 접기 적용.
- 접힌 섹션 색상/테두리/버튼 표시 강화.
- footer 버전/상태 영역 정리.

## 제한 생성/삭제/복원 상태

현재 신규 row 실제 생성 apply가 열린 도메인:

- `characters`
- `enhancementGroups`
- `fieldZones`

현재 생성 row delete/restore가 열린 도메인:

- `characters`
- `enhancementGroups`
- `fieldZones`

아직 생성 apply를 열지 않는 것이 좋은 도메인:

- `itemTemplates`
- `skills`
- `dropTables`
- `dropTableItems`

다음 후보로 검토할 수 있는 도메인:

- `bosses`

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
