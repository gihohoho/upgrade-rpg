# Current Status

현재 기준: **v177 create apply skills/dropTables**

이 패키지 기준 ZIP: **rpg_v177_skills_droptables_create_apply_ready.zip**

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

## v177 완료

- 신규 row 실제 생성 apply 제한 도메인에 `skills` 추가.
- 신규 row 실제 생성 apply 제한 도메인에 `dropTables` 추가.
- `skills`, `dropTables` 생성 row 삭제/복원 allow-list 추가.
- `skills` 생성 row 삭제 전 아래 dependency guard 추가.
  - `skillLevels.skill_code`
  - `characterSkills.skill_code`
  - `userCharacterSkills.skill_code`
- `dropTables` 생성 row 삭제 전 아래 dependency guard 추가.
  - `dropTableItems.drop_table_code`
- 관리자 생성 준비 UI 안내 문구를 `characters/enhancementGroups/fieldZones/bosses/skills/dropTables` 기준으로 갱신.
- `itemTemplates`, `dropTableItems` 생성 apply는 계속 잠금 유지.
- DB reset / seed 없이 진행 가능.

## 이전 완료

- v176: `bosses` 신규 row 생성 apply 제한 오픈.
- v175: `fieldZones` 신규 row 생성 apply 제한 오픈.
- v174: 관리자 접힌 패널 스타일 보정.
- v172~v173: 관리자 sidebar / sticky header / 섹션 접기·펼치기 shell 정리.

## 제한 생성/삭제/복원 상태

현재 신규 row 실제 생성 apply가 열린 도메인:

- `characters`
- `enhancementGroups`
- `fieldZones`
- `bosses`
- `skills`
- `dropTables`

현재 생성 row delete/restore가 열린 도메인:

- `characters`
- `enhancementGroups`
- `fieldZones`
- `bosses`
- `skills`
- `dropTables`

아직 생성 apply를 열지 않는 것이 좋은 도메인:

- `itemTemplates`
- `dropTableItems`
- `skillLevels`
- `enhancementLevels`
- `characterSkills`

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
