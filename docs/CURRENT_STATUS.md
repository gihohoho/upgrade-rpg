# Current Status

현재 기준: **v180 admin create lifecycle guide**

이 패키지 기준 ZIP: **rpg_v180_create_lifecycle_guide_ready.zip**

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

## v180 완료

- 관리자 페이지에 `신규 row 생성·삭제·복원 점검` 섹션 추가.
- 생성 blueprint 응답에 `createLifecycle` 메타데이터 추가.
- 생성/삭제/복원 가능 여부, id/code 삭제 key, combo guard, JSON/asset 잠금 필드 표시.
- 변경 이력 action 필터를 실제 저장되는 `update`, `rollback`, `create`, `create_delete`, `create_delete_restore` 기준으로 정리.
- 기존 생성/삭제/복원 guard, dev key, 확인 문구 유지.
- 새 쓰기 도메인 오픈 없음.
- DB reset / seed 없이 진행 가능.

## v179 완료

- 신규 row 실제 생성 apply 제한 도메인에 `skillLevels`, `enhancementLevels`, `characterSkills` 추가.
- 위 3개 도메인 생성 row 삭제/복원 allow-list 추가.
- `skillLevels`, `enhancementLevels`, `characterSkills`는 `code` 없는 row라 id 기반 생성 row 삭제/복원 흐름을 사용.
- `skillLevels` 생성 검증 추가/유지:
  - `skill_code`는 `skills.code`에 존재해야 함.
  - `level >= 0`
  - `skill_code + level` 중복 차단.
- `enhancementLevels` 생성 검증 추가/유지:
  - `group_code`는 `enhancementGroups.code`에 존재해야 함.
  - `from_level >= 0`
  - `to_level > from_level`
  - `success_rate >= 0`
  - `gold_cost >= 0`
  - `group_code + from_level` 중복 차단.
- `characterSkills` 생성 검증 추가/유지:
  - `character_code`는 `characters.code`에 존재해야 함.
  - `skill_code`는 `skills.code`에 존재해야 함.
  - `character_code + skill_code` 중복 차단.
  - `sort_order >= 0`
- JSON 계열 필드는 생성 입력에서 계속 잠금.
- 관리자 생성 준비 UI 안내 문구를 `characters/enhancementGroups/fieldZones/bosses/skills/dropTables/itemTemplates/dropTableItems/skillLevels/enhancementLevels/characterSkills` 기준으로 갱신.
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

현재 생성 row delete/restore가 열린 도메인:

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

## 이전 완료

- v179: `skillLevels`, `enhancementLevels`, `characterSkills` 신규 row 생성 apply 제한 오픈.
- v178: `itemTemplates`, `dropTableItems` 신규 row 생성 apply 제한 오픈.
- v177: `skills`, `dropTables` 신규 row 생성 apply 제한 오픈.
- v176: `bosses` 신규 row 생성 apply 제한 오픈.
- v175: `fieldZones` 신규 row 생성 apply 제한 오픈.
- v174: 관리자 접힌 패널 스타일 보정.
- v172~v173: 관리자 sidebar / sticky header / 섹션 접기·펼치기 shell 정리.

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
