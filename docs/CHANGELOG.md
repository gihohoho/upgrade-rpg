# Changelog

## v184 - Admin JS Split Readiness

- 관리자 페이지에 `관리자 JS 분리 준비` 섹션을 추가했습니다.
- 실제 파일 분리는 하지 않고 script 순서, 필수 global, export 계약, 분리 후보 묶음을 진단합니다.
- `getAdminJsSplitReadiness()`와 `renderAdminJsSplitReadiness()`를 추가했습니다.
- `checkAdminReadOnlyPageReady()`에 `adminJsSplitReadinessReady`와 `adminJsSplitReadiness`를 추가했습니다.
- 첫 실제 분리 후보를 DB 쓰기와 무관한 `layout shell`로 잡았습니다.
- 새 smoke `tools/smoke_admin_js_split_readiness.js`를 추가하고 core smoke에 포함했습니다.
- 새 쓰기 도메인은 열지 않았고 DB schema 변경 없음, DB reset / seed 필요 없음.

## v183 - Admin Create Lifecycle Batch Check

- 관리자 `신규 row 생성·삭제·복원 점검` 섹션에 일괄 점검 카드를 추가했습니다.
- 현재 생성 초안을 기준으로 생성 preview → 생성 apply → 삭제 preview → 삭제 apply → 복원 preview → 복원 apply를 순서대로 실행할 수 있습니다.
- 일괄 점검 전용 확인 문구 `RUN CREATE DELETE RESTORE CHECK`를 추가했습니다.
- dev key, 생성 확인 문구, 브라우저 confirm, 기존 백엔드 preview guard를 모두 유지했습니다.
- 단계별 결과 테이블과 요약 카드를 표시합니다.
- 새 쓰기 도메인은 열지 않았고 기존 create/delete/restore guard는 유지했습니다.
- DB schema 변경 없음, DB reset / seed 필요 없음.

## v182 - Admin Create Lifecycle Result Summary

- 생성 row 삭제 preview/apply 결과 상단에 요약 카드를 추가했습니다.
- 삭제 결과에서 현재값 불일치, 연결 검사 수, 차단 guard 수, 차단 row 수를 바로 볼 수 있게 했습니다.
- 삭제 row 복원 preview/apply 결과 상단에 요약 카드를 추가했습니다.
- 복원 결과에서 id/code 충돌, validation error, relation 값 수를 바로 볼 수 있게 했습니다.
- 백엔드 응답에 `dependencyCheckCount`, `dependencyBlockerGuardCount`, `restoreConflictCount` 보조 count를 추가했습니다.
- 새 쓰기 도메인은 열지 않았고 기존 create/delete/restore guard는 유지했습니다.
- DB schema 변경 없음, DB reset / seed 필요 없음.

## v181 - Admin Create Lifecycle Guard Helper

- `createLifecycle` 메타데이터에 도메인별 삭제 preview 차단 기준을 추가했습니다.
- 관리자 `신규 row 생성·삭제·복원 점검` 섹션에 삭제 차단 기준 카드를 추가했습니다.
- 변경 이력 action 필터 바로가기 버튼을 추가했습니다.
- `checkAdminReadOnlyPageReady()`에 `createLifecycleDependencyGuideReady` 상태를 추가했습니다.
- 새 쓰기 도메인은 열지 않았고 기존 create/delete/restore guard는 유지했습니다.
- DB schema 변경 없음, DB reset / seed 필요 없음.

## v180 - Admin Create Lifecycle Guide

- 관리자 페이지에 `신규 row 생성·삭제·복원 점검` 섹션을 추가했습니다.
- 생성 blueprint 응답에 `createLifecycle` 메타데이터를 추가했습니다.
- 생성/삭제/복원 가능 여부, id/code 삭제 key, combo guard, JSON/asset 잠금 필드를 한 화면에서 확인할 수 있습니다.
- 변경 이력 action 필터를 실제 저장되는 `update`, `rollback`, `create`, `create_delete`, `create_delete_restore` 기준으로 정리했습니다.
- 새 쓰기 도메인을 열지 않았고 기존 create/delete/restore guard는 유지했습니다.
- DB schema 변경 없음, DB reset / seed 필요 없음.

## v179 - Create Apply Level and Link Tables

- `skillLevels`, `enhancementLevels`, `characterSkills` 신규 row 생성 apply 제한 오픈.
- 위 3개 도메인 생성 row 삭제/복원 allow-list 추가.
- code 없는 relation/level row라 id 기반 생성 row 삭제/복원 guard 추가.
- `skillLevels`는 `skill_code + level` 중복을 차단합니다.
- `enhancementLevels`는 `group_code + from_level`, `to_level`, 확률/비용 검증을 강화했습니다.
- `characterSkills`는 `character_code + skill_code`, `sort_order` 검증을 강화했습니다.
- DB schema 변경 없음, DB reset / seed 필요 없음.

## v178 - Create Apply ItemTemplates and DropTableItems

- `itemTemplates`, `dropTableItems` 신규 row 생성 apply 제한 오픈.
- `itemTemplates` 생성 row 삭제 guard에 `dropTableItems.item_template_code`, `itemInstances.template_code` 연결 검사 추가.
- `dropTableItems`는 code 없는 leaf row라 id 기반 생성 row 삭제/복원 흐름을 제한 오픈.
- `dropTableItems` 생성 검증에 rate/min/max 수량 guard 추가.
- DB schema 변경 없음, DB reset / seed 필요 없음.

## v177 - Create Apply Skills and DropTables

- 신규 row 생성 apply 제한 도메인에 `skills`와 `dropTables`를 추가했습니다.
- `characters`, `enhancementGroups`, `fieldZones`, `bosses`, `skills`, `dropTables`만 실제 생성 apply가 가능합니다.
- `itemTemplates`, `dropTableItems` 생성 apply는 계속 잠금 상태입니다.
- `skills`, `dropTables` 생성 row 삭제/복원 allow-list를 추가했습니다.
- `skills` 삭제 preview에서 `skillLevels.skill_code`, `characterSkills.skill_code`, `userCharacterSkills.skill_code` 연결을 검사합니다.
- `dropTables` 삭제 preview에서 `dropTableItems.drop_table_code` 연결을 검사합니다.
- 관리자 생성 준비 UI 안내 문구를 새 allow-list에 맞춰 갱신했습니다.
- DB reset / seed는 필요 없습니다.

## v176 - Create Apply Bosses

- 신규 row 생성 apply 제한 도메인에 `bosses`를 추가했습니다.
- `characters`, `enhancementGroups`, `fieldZones`, `bosses`만 실제 생성 apply가 가능합니다.
- `itemTemplates`, `skills`, `dropTables`, `dropTableItems` 생성 apply는 계속 잠금 상태입니다.
- `bosses` 생성 row 삭제/복원 allow-list를 추가했습니다.
- `bosses` 삭제 preview에서 `dropTables.owner_type=boss + owner_code` 연결을 검사해 사용 중인 보스는 삭제를 차단합니다.
- 관리자 생성 준비 UI 안내 문구를 새 allow-list에 맞춰 갱신했습니다.
- DB reset / seed는 필요 없습니다.

## v175 - Create Apply FieldZones

- 신규 row 생성 apply 제한 도메인에 `fieldZones`를 추가했습니다.
- `characters`, `enhancementGroups`, `fieldZones`만 실제 생성 apply가 가능합니다.
- `itemTemplates`, `skills`, `dropTables`, `dropTableItems` 생성 apply는 계속 잠금 상태입니다.
- `fieldZones` 생성 row 삭제/복원 allow-list를 추가했습니다.
- `fieldZones` 삭제 preview에서 `dropTables.owner_type=field + owner_code` 연결을 검사해 사용 중인 필드는 삭제를 차단합니다.
- 관리자 생성 준비 UI 안내 문구를 새 allow-list에 맞춰 갱신했습니다.
- DB reset / seed는 필요 없습니다.

## v174 - Admin Collapsed Panel Style Fix

- 접힌 섹션 스타일을 `.section`, `.filter-panel`, `.field-help-panel` 모두에서 통일했습니다.
- `필드 용어 도움말`, `신규 row 생성 준비` 같은 filter/help 기반 탭이 접혔을 때 내부 header만 색칠되던 문제를 수정했습니다.
- 접힌 filter/help 패널은 padding을 제거하고 header가 전체 너비를 차지하도록 보정했습니다.
- `getAdminLayoutShellReadiness()`에 `collapsedPanelStyleReady` 상태를 추가했습니다.
- 기존 관리자 기능과 DB schema는 변경하지 않았습니다.
- DB reset / seed는 필요 없습니다.

## v172 - Admin Layout Navigation Shell

- 관리자 페이지에 sidebar navigation shell을 추가했습니다.
- 상단 header를 sticky 형태로 정리했습니다.
- 주요 섹션에 접기/펼치기 버튼을 추가했습니다.
- 접힌 섹션 상태는 브라우저 localStorage에 저장합니다.
- footer를 현재 버전/상태 표시 영역으로 정리했습니다.
- 기존 edit/create/delete/restore API 기능은 변경하지 않았습니다.
- DB reset / seed는 필요 없습니다.


## v168 - Admin Create Delete Rollback

- `create-apply`로 만든 제한 도메인 row 삭제 되돌리기 preview/apply API를 추가했습니다.
- 대상은 `characters`, `enhancementGroups`의 `action=create` 이력으로 제한했습니다.
- 삭제 preview에서 현재값이 생성 당시 값과 같은지 검사합니다.
- 삭제 preview에서 연결 데이터 blocker 수를 `dependencyBlockerCount`로 표시합니다.
- 연결 데이터가 하나라도 있으면 삭제를 차단합니다.
- 실제 삭제는 dev key와 `DELETE CREATED MASTER DATA ROW` 확인 문구가 필요합니다.
- 삭제 성공 시 `admin_change_logs`에 `action=create_delete`로 기록합니다.
- DB reset / seed는 필요 없습니다.

## v162 - Admin Create Draft Preview

- 신규 row 생성 준비 화면에 blueprint 기반 생성 초안 입력 UI를 추가했습니다.
- 생성 초안은 boolean/select/number/textarea/relation select 타입으로 입력합니다.
- relation select 후보 검색과 owner_type → owner_code 연동 갱신을 지원합니다.
- `POST /api/v1/admin/master-data/create-preview` preview-only API를 추가했습니다.
- code unique 중복, relation 대상 존재, combo guard 중복을 백엔드에서 검증합니다.
- 실제 DB insert, commit, change log, rollback은 아직 잠금 상태입니다.
- DB reset / seed는 필요 없습니다.

## v159 - Admin Create Blueprint Read-only

- 관리자 신규 row 생성 준비용 read-only blueprint API를 추가했습니다.
- 관리자 페이지에 신규 row 생성 준비 섹션을 추가했습니다.
- 도메인별 필수 필드, unique 필드, combo guard, 기본값 draft JSON을 표시합니다.
- relation 필드는 대상 후보 개수를 보여주지만 실제 insert는 아직 잠금 상태입니다.
- JSON 필드는 생성 적용 전까지 잠금으로 표시합니다.
- 기존 edit apply, rollback, change log, localStorage 저장 구조는 유지합니다.
- DB reset / seed는 필요 없습니다.

## v156 - Admin Change Log Relation Tools

- 변경 이력 목록에 relation 변경 개수 배지를 추가했습니다.
- 변경 이력 상세 before/after 값에 relation 대상 이름 label을 표시합니다.
- 변경 이력 상세 relation 값에서 대상 열기 버튼을 사용할 수 있습니다.
- rollback preview의 되돌릴 값 표에서 relation label과 대상 열기 버튼을 표시합니다.
- rollback 현재값 안전 검사 표에서도 relation label을 표시합니다.
- 백엔드 change log detail / rollback preview 응답에 relation metadata를 추가했습니다.
- 기존 rollback guard, dev key, 확인 문구, localStorage 저장 구조는 유지합니다.
- DB reset / seed는 필요 없습니다.

## v153 - Admin Relation Preview Tools

- 변경 preview와 초안 before/after 표에서 relation 값에 대상 이름 label을 함께 표시합니다.
- relation 변경 행에 `relation` 배지를 표시합니다.
- 변경 요약 배너에 relation 변경 개수 표시를 추가했습니다.
- relation 대상이 열 수 있는 도메인이면 `대상 열기` 버튼을 표시합니다.
- `대상 열기`는 code로 카탈로그를 조회한 뒤 해당 상세를 엽니다.
- 기존 preview/apply 백엔드 검증, dev key, 확인 문구, high risk 추가 확인, stale guard는 유지합니다.
- DB reset / seed는 필요 없습니다.

## v150 - Admin Relation Search Tools

- 관계 필드 relation select 검색 input을 추가했습니다.
- 검색은 프론트 UI 안에서만 후보 목록을 좁히며 DB를 수정하지 않습니다.
- 검색 결과가 현재 선택값을 숨기더라도 현재 선택값은 유지되게 했습니다.
- owner_type 변경 시 owner_code 후보 목록과 검색 상태가 같이 안전하게 갱신됩니다.
- 마스터 데이터 카탈로그 검색/페이지 입력에서 Enter 조회를 지원합니다.
- 카탈로그 domain, 표시 개수, 활성 상태, 정렬 변경 시 페이지를 1로 되돌립니다.
- DB reset / seed는 필요 없습니다.

## v147 - Admin Owner Code Relation Tools

- `dropTables.owner_code`를 relation select 기반으로 안전하게 편집할 수 있게 했습니다.
- `owner_type=boss`이면 bosses 목록, `owner_type=field`이면 fieldZones 목록에서만 owner_code를 선택합니다.
- `owner_type`을 바꾸면 `owner_code` 후보 목록도 자동으로 보스/필드 목록으로 전환됩니다.
- preview/apply 공통으로 `owner_type + owner_code` 대상 존재 여부를 백엔드에서 다시 검사합니다.
- 초안 검증 결과에서 relation target label을 함께 표시합니다.
- 기존 dev key, 확인 문구, high risk 추가 확인, stale guard, change log/rollback을 유지합니다.
- DB reset / seed는 필요 없습니다.

## v144 - Admin Combo Relation Guard

- `dropTableItems.drop_table_code` relation select 편집 추가.
- `skillLevels.skill_code`, `skillLevels.level` 편집 추가.
- `enhancementLevels.group_code`, `enhancementLevels.from_level` 편집 추가.
- `characterSkills.character_code`, `characterSkills.skill_code` 편집 추가.
- preview/apply 공통으로 관계 대상 존재 여부 검증.
- `skill_code + level`, `group_code + from_level`, `character_code + skill_code` 중복 조합 검증 추가.
- 관리자 UI relation note에 중복 조합 검사 항목 표시.
- DB reset / seed는 필요 없음.

## v141 - Admin Relation Safe Edit

- 관리자 편집 초안에 relation select 타입을 추가했습니다.
- `itemTemplates.enhance_group_code`를 enhancementGroups 목록 기반 select로 편집할 수 있게 했습니다.
- `dropTableItems.item_template_code`를 itemTemplates 목록 기반 select로 편집할 수 있게 했습니다.
- `dropTables.owner_type`을 boss/field select로 편집할 수 있게 했습니다.
- 백엔드 preview/apply 공통 검증에서 관계 대상 존재 여부를 다시 검사합니다.
- 관계 필드 변경은 high risk/medium risk 안내와 기존 확인 문구, stale guard, change log를 그대로 거칩니다.
- DB reset / seed는 필요 없습니다.

## v138 - Admin Safe Apply Review

- 관리자 편집 초안 아래에 적용 직전 비교 UI를 추가했습니다.
- 실제로 바뀐 필드만 before/after 형태로 보여줍니다.
- 변경 필드를 risk high / medium / low 순으로 정렬해 위험한 변경을 먼저 보이게 했습니다.
- high risk 변경이 있으면 기존 확인 문구 외에 `HIGH RISK EDIT` 추가 확인 문구를 요구합니다.
- 초안 검증 결과의 변경 표에도 위험도 컬럼을 추가했습니다.
- 마스터 데이터 카탈로그에서 현재 상세로 열어둔 행을 `선택됨` 배지와 강조 배경으로 표시합니다.
- DB reset/seed는 필요 없습니다.

## v135 - Master Catalog Pagination + Slot Labels

- 관리자 마스터 데이터 카탈로그에 페이지네이션을 추가했습니다.
- 기본 표시 개수를 20개로 바꿨습니다.
- 기본 정렬을 ID순으로 바꿨습니다.
- 카탈로그 API에 page/offset/totalPages/hasPrevPage/hasNextPage를 추가했습니다.
- equip_slot 숫자 프리셋 6~14를 인게임 특수 장비 슬롯 이름으로 표시합니다.
- DB reset/seed는 필요 없습니다.

## v134 - Admin Safe Selects + Allow-list Expansion

- 관리자 편집 초안에 preset select 타입을 추가했습니다.
- `itemTemplates.item_type`, `itemTemplates.equip_slot`, `skills.slot_key`를 실제 적용 allow-list에 추가했습니다.
- `item_type`, `equip_slot`, `boss_type`, `slot_key`는 오타 방지를 위해 select 프리셋으로 입력하게 했습니다.
- 현재 DB 값이 프리셋에 없으면 select 맨 위에 현재 DB 값으로 표시하게 했습니다.
- 편집 필드마다 `risk high / medium / low` 배지를 표시했습니다.
- field help / value hint / impact guide에 아이템 분류, 장착 슬롯, 스킬 슬롯 설명을 추가했습니다.
- 관계 필드, JSON 필드, id/code 필드는 계속 잠금 유지했습니다.
- DB reset / seed는 필요 없습니다.

# v133 - Admin Edit Input UI

- 관리자 편집 초안 입력 UI를 필드 타입에 맞게 개선했습니다.
- boolean 필드는 checkbox 대신 true/false select로 표시합니다.
- number 필드는 number input으로 표시합니다.
- description/admin_note는 textarea로 표시합니다.
- allow-list 밖 필드는 입력칸 대신 읽기 전용/잠금 필드 카드로 표시하고 잠금 사유를 보여줍니다.
- 백엔드 API/DB schema/seed/localStorage는 변경하지 않았습니다.
- DB reset / seed는 필요 없습니다.


# v132 - handoff cleanup

- 새 채팅 인수인계용 `NEXT_CHAT_HANDOFF.md` 추가.
- 현재 상태 요약 `docs/CURRENT_STATUS.md` 추가.
- 다음 단계 추천 `docs/NEXT_STEPS.md` 추가.
- 문서 루트 정리: 자주 보지 않는 기록성 문서를 `docs/archive/stage-notes/`로 이동.
- `tools/run_smoke_core.sh`, `tools/run_smoke_all.sh` 추가.
- 기능 로직 변경 없음. DB reset/seed 필요 없음.


## v131 - Admin Edit Stale Guard

- 관리자 편집 적용 전에 편집 화면을 열었을 때의 기준값과 현재 DB 값이 같은지 검사하는 stale guard를 추가했습니다.
- 프론트 편집 초안 검증/적용 요청에 `baseValues`를 함께 보내고, 백엔드는 현재 DB 값이 달라졌으면 `staleChanges`로 차단합니다.
- 오래된 화면에서 최신 DB 값을 덮어쓰는 실수를 막기 위해 실제 적용에는 `baseValues`가 필요합니다.
- 관리자 화면의 초안 검증 결과에 `stale guard`, `stale count`, `오래된 초안 검사` 표를 추가했습니다.
- DB reset / seed는 필요 없습니다.

## v130 - Admin Write Dev Key Guard

- 관리자 실제 적용/되돌리기 API에 `X-Admin-Dev-Key` 임시 잠금장치를 추가했습니다.
- 관리자 페이지에 `관리자 쓰기 dev key 잠금` 영역을 추가했습니다.
- 읽기/미리보기 API는 그대로 열어두고, DB를 바꾸는 apply/rollback apply만 헤더 검사를 통과해야 합니다.
- DB reset / seed는 필요 없습니다.


## v129 - admin change log filters

- 관리자 변경 이력에 target type, row id, action, changed field, applied, sort 필터를 추가했습니다.
- `GET /api/v1/admin/change-logs`에 `action`, `changedKey`, `applied`, `sort` query를 추가했습니다.
- raw before/after JSON은 계속 숨기고 compact rows + 상세 scalar 변경값만 노출합니다.
- DB reset/seed는 필요 없습니다.

## v128
- 관리자 마스터 데이터 실제 적용 후 선택 항목 상세를 다시 불러오고 `/api/v1/game/master-data` 응답을 자동 비교합니다.
- 변경 이력 되돌리기 성공 후에도 되돌린 대상의 master-data API 반영 상태를 자동 확인합니다.
- 자동 확인 결과에 `contextLabel`과 `autoAfterWrite` 정보를 붙여 수동 확인과 구분할 수 있게 했습니다.
- 이 기능은 진단만 수행하며 DB 추가 수정/localStorage 수정/현재 게임 런타임 수정은 하지 않습니다.
- DB reset/seed는 필요 없습니다.

## v127
- 관리자 상세 화면에 `인게임 master-data API 반영 확인` 진단을 추가했습니다.
- 선택한 마스터 데이터 상세 값이 `/api/v1/game/master-data` 응답에도 같은 값으로 내려오는지 비교합니다.
- DB 적용 후 게임 새로고침 전에 DB → FastAPI master-data 응답까지 반영됐는지 확인할 수 있습니다.
- 이 기능은 조회만 수행하며 DB/localStorage/현재 게임 런타임은 수정하지 않습니다.
- Console helper `verifySelectedMasterDataApi()`를 추가했습니다.
- DB reset/seed는 필요 없습니다.

## v124
- 관리자 페이지에서 수정한 `itemTemplates.stackable` 값을 인게임 신규 획득 장비 겹치기 로직에 연결했습니다.
- master-data adapter가 보스 드랍 아이템에 `stackable`, `templateKey`, `itemTemplateCode` 런타임 필드를 붙입니다.
- 일반 장비 드랍도 `addStackableItemToInventory()`를 통과하게 하여 `stackable=true`인 같은 +0 아이템은 count로 겹칩니다.
- 기존 세이브 전체를 자동 병합하지는 않지만, 새 stackable 드랍이 기존 같은 +0 아이템과 만나면 그 슬롯에 겹치고 stackable 값을 보강합니다.
- 겹쳐진 일반 장비를 강화할 때 스택 전체가 강화되지 않도록 1개만 분리해서 강화합니다.
- 인벤토리/보관함/휴지통 슬롯 배지에서 일반 장비도 `count > 1`이면 `xN`을 표시합니다.
- DB reset/seed는 필요 없습니다.

## v122
- 관리자 편집 초안에서 allow-list 필드만 실제 DB 적용할 수 있는 guarded apply를 추가했습니다.
- 새 API `POST /api/v1/admin/master-data/edit-apply`를 추가했습니다.
- 실제 적용에는 확인 문구 `APPLY MASTER DATA EDIT`가 필요합니다.
- 적용 성공 시 `admin_change_logs`에 before/after/rollback 정보를 저장합니다.
- 새 API `GET /api/v1/admin/change-logs`와 관리자 페이지 변경 이력 표를 추가했습니다.
- code, *_code, *_id, *_json, 이미지/asset, 관계 필드는 계속 잠금 상태입니다.
- DB reset/seed는 필요 없습니다.

## v121
- 관리자 페이지의 `grade` 설명을 현재 DB 구조에 맞게 수정했습니다.
- 현재 `itemTemplates.grade`는 normal/rare/epic 희귀도명이 아니라 기존 JS `item.tier`를 옮긴 숫자형 진행 등급입니다.
- 카탈로그/상세/편집 초안에 실제 값 해석 힌트를 추가했습니다. 예: `grade=12` → `tier 12`.
- `enhance_group_code`와 `admin_note`도 값에 따라 간단한 해석 힌트를 표시합니다.
- Console helper `getAdminFieldValueHint()`를 추가했습니다.
- DB reset/seed는 필요 없습니다.

## v120
- 관리자 페이지에 `필드 용어 도움말` 섹션을 추가했습니다.
- `grade`, `enhance group code`, `admin note`의 의미를 관리자 화면에서 바로 확인할 수 있게 했습니다.
- 마스터 데이터 카탈로그 표 제목, 상세 필드, 편집 초안 입력칸 옆에 `?` 도움말 배지를 표시합니다.
- Console helper `getAdminFieldHelp()`와 `listAdminFieldHelp()`를 추가했습니다.
- 화면 설명만 추가했으며 DB/localStorage/게임 런타임은 수정하지 않습니다.
- DB reset/seed는 필요 없습니다.

## v119
- 관리자 편집 초안 입력칸을 활성화하고, 값을 바꾼 뒤 백엔드 dry-run 검증을 할 수 있게 했습니다.
- `POST /api/v1/admin/master-data/edit-preview` API를 추가했습니다.
- 편집 초안 검증은 현재 DB 값과 초안 값을 비교해 변경될 값/오류/변경 없음 항목을 반환합니다.
- `id`, `created_at`, `updated_at`, JSON 필드, 이미지/아이콘 asset 필드는 수정 불가로 검증합니다.
- 실제 DB 저장 버튼은 계속 disabled이며, DB reset/seed는 필요 없습니다.

## v118
- 관리자 마스터 데이터 상세 화면에 `관리자 편집 초안` 잠금 폼을 추가했습니다.
- 선택한 항목의 일반 필드를 disabled 입력칸으로 보여주며, 저장/되돌리기 버튼은 아직 잠금 상태입니다.
- `getAdminEditDraftReadiness()` Console 헬퍼를 추가해 편집 초안이 읽기 전용으로 잠겨 있는지 확인할 수 있습니다.
- 관리자 페이지 상단에 섹션 바로가기 nav를 추가했습니다.
- 문서가 너무 쌓이지 않도록 기록성 MD 파일을 `docs/archive/stage-notes/`로 이동하고 `docs/README.md` 문서 인덱스를 추가했습니다.
- DB reset/seed는 필요 없습니다.

## v117
- 관리자 마스터 데이터 상세 화면에 실제 연결 항목 조회를 추가했습니다.
- `GET /api/v1/admin/master-data/relations` API를 추가했습니다.
- 아이템/스킬/보스/필드/드랍/강화 데이터의 연결 행을 축약된 읽기 전용 목록으로 확인할 수 있습니다.
- 연결 항목의 `보기` 버튼으로 관련 마스터 데이터 상세로 이동할 수 있습니다.
- 원본 JSON과 이미지 data URL은 계속 숨기며, 관리자 쓰기 UI도 계속 차단합니다.
- DB reset/seed는 필요 없습니다.

## v113
- 관리자 페이지 주소 안내를 고정 `5500` 포트가 아니라 현재 게임이 열린 주소 기준으로 계산하도록 수정했습니다.
- `SAVE DATA → admin` overview 모달에 실제 관리자 페이지 URL 표시와 `주소 복사` 버튼을 추가했습니다.
- `admin.html` 상단에 현재 관리자 페이지 주소를 표시하고 복사할 수 있게 했습니다.
- 관리자 페이지의 `게임으로 돌아가기` 링크도 같은 host/port 기준 `index.html`로 보정합니다.
- DB reset/seed는 필요 없습니다.

## v111
- 관리자 페이지 준비를 위해 읽기 전용 `/api/v1/admin/overview` API를 추가했습니다.
- 최근 세이브 스냅샷 요약을 조회하는 `/api/v1/admin/save-snapshots` API를 추가했습니다.
- 관리자 조회 API는 `snapshot_json` 원본을 내려주지 않고 요약/카운트만 반환합니다.
- 브라우저에서 `openAdminReadOnlyOverviewModal()`로 관리자 준비 overview 모달을 열 수 있게 했습니다.
- SAVE DATA 개발 배지에 `admin` 버튼을 추가했습니다. 이 버튼은 조회 전용이며 localStorage/DB를 수정하지 않습니다.
- DB reset/seed는 필요 없습니다.

## v108
- DB 세이브/백업 복구 직후 새로고침할 때 `beforeunload` 자동 저장이 기존 런타임 상태를 다시 localStorage에 덮어쓰는 문제를 수정했습니다.
- 복구 성공 시 `pending_reload` 잠금을 남겨서 새로고침 전 자동저장/수동저장이 복구된 localStorage 값을 덮어쓰지 못하게 했습니다.
- 새로고침 후 게임이 복구된 세이브를 읽으면 잠금을 해제하고 상태를 `applied_after_reload`로 기록합니다.

## v106
- 백엔드 DB 세이브를 localStorage에 덮어쓰기 전에 미리보기 모달로 비교할 수 있게 했습니다.
- 복구 실행 전 현재 localStorage 세이브를 자동 백업합니다.
- 복구 후 바로 런타임에 적용하지 않고 새로고침 후 적용되도록 했습니다.

## v105
- 백엔드 DB 세이브를 실제 게임에 적용하기 전에 localStorage 세이브와 비교하는 preview/compare 브릿지를 추가했습니다.
- `previewBackendSaveSnapshot()`으로 레벨, 골드, 필드, 인벤토리/창고/우편/장착 슬롯 차이를 확인할 수 있습니다.
- 이 단계에서는 DB 세이브를 localStorage나 게임 상태에 덮어쓰지 않습니다.

## v104
- MD/SAVE dev badge 위치를 하단 HUD 바로 위로 올리고, 접힌 상태에서는 우측 상단에 show 버튼이 가지런히 붙도록 조정했습니다.
- SAVE DATA 배지 버튼 행이 줄바꿈되지 않도록 폭과 레이아웃을 조정했습니다.

# 변경 기록

## v103 - 개발자 배지 하단 HUD 위 배치

- `MASTER DATA`와 `SAVE DATA` 개발자 배지를 하단 HUD 내부가 아니라 하단 인터페이스 바로 위쪽에 고정 배치했습니다.
- 데스크톱에서는 오른쪽 스킬칸 위에 두 배지가 나란히 보이도록 정렬했습니다.
- 좁은 화면에서는 두 배지가 겹치지 않도록 세로로 분리되게 했습니다.
- 배지 위치만 변경했으며 master-data/save-data 로직은 변경하지 않았습니다.

## v101 - SAVE DATA 개발자 배지

- 수동 저장의 백엔드 DB 동기화 상태를 화면에서 확인하는 `SAVE DATA` 개발자 배지를 추가했습니다.
- 배지에서 즉시 `sync`, `load`, `dual`, `local` 작업을 실행할 수 있습니다.
- 저장 정책/상태 변경 시 배지가 즉시 갱신되도록 `upgrade-rpg:backend-save-sync-*` 이벤트를 추가했습니다.
- 백엔드 저장값 `load`는 아직 게임 상태에 적용하지 않고 조회만 합니다.



## v098 - Master-data dev badge toggle alignment

- `hide/show` 토글 버튼 문구를 `hide MD` / `show MD`로 명확하게 바꿨습니다.
- 토글 버튼을 MASTER DATA 배지 상단 정가운데 탭처럼 배치했습니다.
- 배지를 숨겨도 같은 위치에 `show MD` 탭이 남아, Console 없이 화면에서 다시 펼칠 수 있습니다.
- 토글과 배지를 하나의 wrapper 안에서 함께 배치해 버튼이 위로 뜨거나 겹치는 현상을 줄였습니다.


## v095 - Backend master-data dev badge

- 브라우저 화면 하단에 master-data 상태 확인용 개발자 배지를 추가했다.
- 배지는 `file://`, `localhost`, `127.0.0.1` 환경에서 기본 표시된다.
- `applied`, `static_js_mode`, `failed_fallback_to_static_js` 같은 runtime state와 mode/assets/counts 요약을 표시한다.
- Console 헬퍼 `refreshBackendMasterDataDevBadge()`, `showBackendMasterDataDevBadge()`, `hideBackendMasterDataDevBadge()`, `toggleBackendMasterDataDevBadge()`를 추가했다.

## v087 - Preserve nullable skill proc rate

- Preserved missing skill `baseProcRate` values as database `NULL` instead of converting them to `0`.
- Updated `skills.proc_rate` to be nullable in SQLAlchemy and schema draft.
- Added documentation and a smoke test for nullable master-data fields.
- Intended to make `check_master_data_parity.py` pass for `lightsabre.procRate`.


## v086 - Master Data Parity Checker

- `backend/scripts/check_master_data_parity.py`를 추가했습니다.
- 현재 JS 마스터 데이터에서 생성된 `backend/seeds/generated/*.json`과 FastAPI `/api/v1/game/master-data` 응답을 비교할 수 있습니다.
- 기본 경량 응답과 `--include-assets` 이미지 포함 응답을 모두 검사할 수 있습니다.
- characters, skills, itemTemplates, bosses, fieldZones, dropTables, dropTableItems, enhancementRules의 개수와 주요 필드를 비교합니다.
- `tools/smoke_master_data_parity_checker.py`와 `docs/MASTER_DATA_PARITY_CHECKER.md`를 추가했습니다.

## v085 - Frontend Master Data Bridge

- `src/api/game-api-client.js`와 `src/api/master-data-bridge.js`를 추가했습니다.
- 기존 게임 동작은 유지하면서 브라우저 콘솔에서 FastAPI master-data API를 읽어올 수 있게 했습니다.
- `checkBackendMasterData()`, `loadBackendMasterData()`, `getCachedBackendMasterData()` 전역 함수를 추가했습니다.
- `tools/smoke_frontend_master_data_bridge.js`와 `docs/FRONTEND_MASTER_DATA_BRIDGE.md`를 추가했습니다.

## v084 - Master Data Nested Asset Cleanup

- 기본 master-data 응답에서 최상위 asset 필드뿐 아니라 중첩 JSON 내부의 긴 `data:image/...` 문자열도 제거하도록 정리했습니다.
- `?includeAssets=true` 요청에서는 기존처럼 asset 문자열을 포함합니다.
- `tools/smoke_master_data_nested_asset_cleanup.py`와 관련 문서를 추가했습니다.

## v082 - Seed Import Long Asset URL Fix

- `item_templates.icon_url`에 SVG `data:image` 문자열이 500자를 넘어 seed import가 실패하던 문제를 수정했습니다.
- `characters.image_url`, `skills.icon_url`, `item_templates.icon_url`, `bosses.image_url` 컬럼을 `Text` 타입으로 변경했습니다.
- `backend/sql/schema_draft.sql`의 이미지/아이콘 URL 컬럼도 `TEXT`로 맞췄습니다.
- `backend/scripts/setup_dev_db.py`의 SQL 로그 출력을 기본 비활성화했습니다. 긴 seed 데이터가 터미널을 가득 채우는 것을 막고, 필요할 때만 `--verbose-sql`로 볼 수 있습니다.
- `tools/smoke_seed_import_long_asset_columns.py`를 추가했습니다.

## v078 - Seed Import Structure

- `backend/scripts/setup_dev_db.py` 추가
  - 로컬 DB reset/schema 생성/seed import/verify 지원
  - `--dry-run`으로 DB 접속 없이 seed JSON 개수 확인 가능
- `docs/SEED_IMPORT.md` 추가
- `tools/smoke_seed_import_structure.py` 추가
- 매우 큰 HP/골드/강화비용을 고려해 DB 초안/모델의 관련 컬럼을 `NUMERIC(40,0)` 계열로 보정
- `user_mailbox_messages` 테이블을 SQL 초안에 보강


## v077 - Backend env fix + seed extractor

- `backend/app/core/config.py`를 수정해 `CORS_ORIGINS`를 JSON 리스트 형식과 쉼표 문자열 형식 모두 처리할 수 있게 했습니다.
- `backend/.env.example`의 `CORS_ORIGINS` 예시를 안전한 JSON 리스트 형식으로 수정했습니다.
- `backend/pyproject.toml` 버전을 `0.1.1`로 올리고 `asyncpg` 의존성을 명시했습니다.
- `tools/extract_seed_data.js`를 추가해 현재 JS 마스터 데이터를 `backend/seeds/generated/*.json`으로 추출할 수 있게 했습니다.
- `tools/smoke_seed_extraction.js`를 추가해 생성된 seed JSON 기본 검증을 할 수 있게 했습니다.
- `backend/seeds/README.md`, `docs/SEED_EXTRACTION.md`를 추가했습니다.
- Docker/FastAPI 로컬 실행 중 실제로 발생한 `CORS_ORIGINS` 파싱 오류와 `asyncpg` 누락 오류 해결법을 문서에 반영했습니다.
- 기존 프론트 게임 동작은 변경하지 않았습니다.

## v074 - 5순위: API 응답 형태 확정

- `docs/API_RESPONSE_CONTRACT.md`를 추가해 FastAPI 응답 표준 봉투를 확정했습니다.
- `src/api/api-response-contract.js`를 추가해 응답 버전, 행동 타입, 에러 코드, 응답 생성 헬퍼를 정리했습니다.
- `src/api/API_PLAN.md`를 확정 응답 형태 기준으로 갱신했습니다.
- 저장/불러오기, 마스터 데이터, 전투, 처치/드랍, 장착/해제/강화, 스킬강화권, 보스 소환, 관리자 변경 응답 예시를 정리했습니다.
- 실패 응답 형태와 공통 에러 코드를 정리했습니다.
- `tools/smoke_api_response_contract.js`를 추가해 응답 계약 헬퍼와 예시 응답을 자동 검증할 수 있게 했습니다.
- 현재 게임 동작에 영향을 주는 파일은 변경하지 않았습니다. 따라서 브라우저 확인 항목은 없습니다.

## v073 - 4순위 3차: 장착/해제/스킬강화권/보스소환 결과 객체화

- `actionEquipDirect()`에 `item.equip` / `skill_book.use` 결과 객체를 도입했습니다.
- `actionUnequipDirect()`에 `item.unequip` 결과 객체를 도입했습니다.
- `summonBoss()`에 `boss.summon` 결과 객체를 도입했습니다.
- `applyActionResultUi()`가 보스 패널 닫기, 특수보스 패널 닫기, 자동공격 시작 요청을 처리할 수 있게 확장했습니다.
- 장착/해제/스킬강화권/보스소환 성공·실패 사유를 `data.reason` 또는 상세 데이터로 남기도록 정리했습니다.
- 기존 UI 동작은 유지하면서 FastAPI 응답 구조로 옮기기 쉬운 중간 계층을 확장했습니다.
- `tools/smoke_action_results.js`를 추가해 주요 결과 객체 생성 여부를 자동 확인할 수 있게 했습니다.

## v072 - 4순위 2차: 처치/드랍/보상 결과 객체화

- `killEnemy()`에 `combat.kill` 결과 객체를 도입했습니다.
- 보스 처치 시 장비/탈리스만/휘장/스킬강화권 드랍 결과를 `data.drops`, `logs`, `effects`에 모으도록 정리했습니다.
- 최초 장비 보너스 스킬강화권 지급 로직이 선택적으로 Action Result에 기록되도록 개선했습니다.
- 필드 몬스터 처치 시 골드/공격속도/순수공격력 성장 보상을 `data.rewards`에 기록하도록 했습니다.
- `applyActionResultUi()`에 `renderUI` 요청 처리를 추가했습니다.
- 기존 게임 동작은 유지하고, FastAPI 응답 구조로 옮기기 위한 중간 계층만 추가했습니다.
