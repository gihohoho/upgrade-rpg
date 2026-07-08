# Changelog

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

# Changelog

## v153 - Admin Relation Preview Tools

- 관계 필드 relation select 검색 input을 추가했습니다.
- 검색은 프론트 UI 안에서만 후보 목록을 좁히며 DB를 수정하지 않습니다.
- 검색 결과가 현재 선택값을 숨기더라도 현재 선택값은 유지되게 했습니다.
- owner_type 변경 시 owner_code 후보 목록과 검색 상태가 같이 안전하게 갱신됩니다.
- 마스터 데이터 카탈로그 검색/페이지 입력에서 Enter 조회를 지원합니다.
- 카탈로그 domain, 표시 개수, 활성 상태, 정렬 변경 시 페이지를 1로 되돌립니다.
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

## v138 - Admin Safe Apply Review

- 관리자 편집 초안 아래에 적용 직전 비교 UI를 추가했습니다.
- 실제로 바뀐 필드만 before/after 형태로 보여줍니다.
- 변경 필드를 risk high / medium / low 순으로 정렬해 위험한 변경을 먼저 보이게 했습니다.
- high risk 변경이 있으면 기존 확인 문구 외에 `HIGH RISK EDIT` 추가 확인 문구를 요구합니다.
- 초안 검증 결과의 변경 표에도 위험도 컬럼을 추가했습니다.
- 마스터 데이터 카탈로그에서 현재 상세로 열어둔 행을 `선택됨` 배지와 강조 배경으로 표시합니다.
- DB reset/seed는 필요 없습니다.

## v071 - 4순위 1차: Action Result 도입

- `src/systems/action-result-system.js`를 추가했습니다.
- `index.html`에 `action-result-system.js` 로드를 추가했습니다.
- `combat-system.js`의 `playerAttack()`이 전투 결과 객체를 생성하도록 변경했습니다.
- 스킬 데미지 텍스트를 결과 객체의 `effects`에 담은 뒤 UI 반영 단계에서 표시하도록 변경했습니다.
- `item-system.js`의 `actionReinforce(times)`가 강화 결과 객체를 생성하고 반환하도록 변경했습니다.
- 강화 로그/결과창/UI 갱신 요청을 `applyActionResultUi()`를 통해 처리하도록 변경했습니다.
- `docs/UI_RESULT_SEPARATION_STAGE1.md`를 추가했습니다.

주의:

- 이번 작업은 4순위 1차입니다.
- `killEnemy()`, 드랍 판정, 장착/해제, 스킬강화권 사용 로직은 아직 완전한 결과 객체 구조로 바꾸지 않았습니다.
- 기존 게임 동작을 유지하는 것을 우선했습니다.


## v069 - skill save migration fix

- v068 스킬 구조 변경 후 기존 저장 데이터의 `player.skills`가 새 캐릭터별 스킬 구조로 완전히 이관되지 않을 수 있는 문제를 보정했습니다.
- `src/data/skills.js`에 레거시 스킬 상태 병합 로직을 추가했습니다.
- 일반 Q 스킬은 기존 v065~v068과 동일하게 데미지 텍스트 표시 대상에서 제외했습니다.
- CSS 중복은 아직 실제 CSS 코드를 병합하지 않았습니다. 문서상으로 “전체 자동 압축은 위험, 완전히 동일한 선택자부터 선별 병합” 원칙을 유지합니다.

# 변경 이력

## v066-docs-maintenance

목적:

- 기호가 요청한 유지보수/탐색/계획 문서 보강
- ZIP을 받은 뒤 무엇을 먼저 봐야 하는지 명확히 정리
- 다음 작업자가 빠르게 구조를 파악할 수 있게 문서 추가

추가된 문서:

```txt
README.md
docs/BACKEND_SPLIT_STAGE2_PLAN.md
docs/BACKEND_SPLIT_CHECKLIST.md
docs/CODE_MAP.md
docs/ADMIN_PAGE_REQUIREMENTS.md
docs/DECISION_LOG.md
docs/CHANGELOG.md
```

기능 코드 변경:

```txt
없음
```

기존 v066 상태 분리 작업은 유지했습니다.

---

## v066_backend_ready_state_split

목적:

- 백엔드 분리 준비 2차 정리 중 1순위 상태 분리 적용

변경:

- `gameState.server` 추가
- `gameState.client` 추가
- `gameState.runtime` 추가
- 기존 전역 변수 호환 유지
- 저장/불러오기용 헬퍼 추가
- `src/state/STATE_SPLIT_READY.md` 추가

## v0.67 - 백엔드 분리 준비 2순위: bosses.js 역할 분리

- `src/data/bosses.js`를 순수 보스/드랍 원본 데이터 중심으로 축소했습니다.
- 고티어 보스/장비 생성 공식은 `src/data/boss-factories.js`로 분리했습니다.
- 아이콘 생성 유틸은 `src/utils/icon-utils.js`로 분리했습니다.
- 심연의 편린 특수 옵션 규칙은 `src/rules/abyss-fragment-rules.js`로 분리했습니다.
- 보스 표시용 후처리는 `src/rules/boss-display-rules.js`로 분리했습니다.
- 드랍률 보정/최초 장비 보너스 규칙은 `src/rules/boss-drop-rules.js`로 분리했습니다.
- 후처리 실행 순서는 `src/data/boss-bootstrap.js`에서 관리합니다.
- 기존 `bossList`, `specialBossList`, `getNormalBossSkillDropRate()`, `grantFirstEquipSkillBookIfNeeded()` 이름은 유지했습니다.


## v0.68 - 백엔드 분리 준비 3순위: 캐릭터별 스킬 구조 준비

- `src/data/skills.js`를 추가했습니다.
- 기본 캐릭터 `weapon_master`를 등록했습니다.
- 현재 스킬 8개를 `skillMasterData`로 분리했습니다.
- Q/SQ, W/SW 각성 정보를 스킬 데이터 내부로 이동했습니다.
- 스킬강화권 매핑을 `skillBookMasterData`로 분리했습니다.
- 기존 `skillBookMapping` 이름은 호환용으로 유지했습니다.
- `player.currentCharacterId`, `player.ownedCharacterIds`, `player.userCharacters` 구조를 추가했습니다.
- 기존 `player.skills` 접근은 유지하되, 현재 캐릭터 스킬 객체와 동기화되도록 했습니다.
- `renderSkills()`가 중앙 스킬 데이터 기반으로 스킬 UI를 그리도록 변경했습니다.
- `item-system.js`의 스킬강화권 사용 로직이 중앙 스킬 데이터와 현재 캐릭터 스킬을 참조하도록 변경했습니다.
- `combat-system.js`가 현재 캐릭터 스킬 헬퍼를 우선 사용하도록 변경했습니다.
- `docs/SKILL_STRUCTURE_READY.md`를 추가했습니다.
- `docs/CSS_AUDIT.md`를 추가했습니다.

주의:

- 이번 작업은 스킬 구조 변경 1차입니다.
- 전투 공식 전체를 완전히 데이터 기반으로 바꾸지는 않았습니다.
- 다음 단계에서 `combat-system.js`, `item-system.js`의 UI 호출 제거와 결과 객체화를 진행하는 것이 좋습니다.


## v070 - 스킬 데미지 텍스트 위치 수정 + CSS 안전 병합

### 수정

- `src/systems/combat-system.js`
  - 스킬 데미지 텍스트가 `.enemy-display(width: 100%)` 기준으로 계산되어 화면 밖으로 나갈 수 있던 문제를 수정했습니다.
  - 데미지 텍스트 기준점을 `#enemy-image-placeholder`로 변경했습니다.
  - 전투 영역 밖으로 텍스트가 나가지 않도록 위치 보정 함수를 추가했습니다.

### CSS

- `src/styles/style.css`
  - 최종 적용값이 유지되는 안전 중복 규칙 38개를 병합/제거했습니다.
  - 병합 후 CSS 파싱 오류가 없는지 확인했습니다.

### 문서

- `docs/DAMAGE_TEXT_POSITION_FIX.md` 추가
- `docs/CSS_MERGE_REPORT.md` 추가


## v075 - Backend Foundation Draft

### Added

```txt
backend/ FastAPI 프로젝트 뼈대 추가
docs/ADMIN_REQUIREMENTS_V1.md 추가
docs/DB_SCHEMA_DRAFT.md 추가
docs/BACKEND_ARCHITECTURE.md 추가
docs/BACKEND_API_ROUTES_DRAFT.md 추가
backend/sql/schema_draft.sql 추가
tools/smoke_backend_foundation.js 추가
```

### Notes

```txt
기존 프론트 게임 동작은 변경하지 않음
관리자 페이지 요구사항을 DB/FastAPI 설계 기준으로 고정
PostgreSQL + SQLAlchemy + Alembic 기반 초안 작성
```

## v076 - Dev Environment Setup

### Added

```txt
docker-compose.yml 추가
.gitignore 추가
.dockerignore 추가
docs/LOCAL_DEV_SETUP.md 추가
docs/DOCKER_POSTGRES_GUIDE.md 추가
docs/GIT_WORKFLOW.md 추가
tools/check_backend_ready.py 추가
```

### Backend

```txt
backend/.env.example 보강
/api/v1/health/db 엔드포인트 추가
backend/README.md 로컬 실행 안내 보강
```

### Notes

```txt
기존 프론트 게임 실행 흐름은 변경하지 않음
Docker PostgreSQL + Adminer 로컬 실행 준비 완료
다음 단계는 JS 마스터 데이터 추출 도구 작성 + seed JSON 생성 추천
```


## v079 seed import connection fix

- `backend/scripts/setup_dev_db.py`를 sync SQLAlchemy + `psycopg` 방식으로 변경했습니다.
- Windows/Docker 환경에서 `asyncpg.exceptions.ConnectionDoesNotExistError`가 seed import 중 발생하는 문제를 피하기 위한 수정입니다.
- `backend/pyproject.toml`에 `psycopg[binary]` 의존성을 추가했습니다.


## v080 - Local DB Port Fix

- 로컬 Docker PostgreSQL 호스트 포트를 `5432`에서 `55432`로 변경했다.
- `backend/.env.example`, `backend/app/core/config.py`, `backend/alembic.ini`의 기본 DB 주소를 `127.0.0.1:55432` 기준으로 맞췄다.
- Windows 환경에서 기존 로컬 PostgreSQL과 포트 충돌이 나지 않도록 `docs/LOCAL_DB_PORT_POLICY.md`를 추가했다.
- 이번 변경은 기존 프론트 게임 기능에는 영향을 주지 않는다.

## v081 - Master Data API DB 연결

- `/api/v1/game/master-data`의 임시 stub 응답을 제거하고 PostgreSQL seed 테이블을 실제로 읽도록 변경했습니다.
- `payload`에 characters, skills, itemTemplates, bosses, fieldZones, dropTables, enhancementRules 등을 포함합니다.
- `meta.counts`와 `payload.counts`로 주요 마스터 데이터 개수를 확인할 수 있습니다.
- `backend/scripts/check_master_data_api.py`를 추가해 서버 실행 후 API 응답을 터미널에서 점검할 수 있게 했습니다.
- `docs/MASTER_DATA_API.md` 문서를 추가했습니다.

## v082 - Seed Import Long Asset Fix

- seed import 중 `item_templates.icon_url` 등 긴 SVG data URL이 `VARCHAR(500)` 제한에 걸리던 문제를 수정했습니다.
- `characters.image_url`, `skills.icon_url`, `item_templates.icon_url`, `bosses.image_url` 컬럼을 `TEXT` 기준으로 변경했습니다.
- `setup_dev_db.py` 기본 SQL 로그 출력을 줄이고, 필요할 때만 `--verbose-sql`로 긴 SQL 로그를 볼 수 있게 했습니다.

## v083 - Master Data Asset Cleanup

- `/api/v1/game/master-data` 기본 응답에서 긴 SVG/data URL 이미지 문자열을 제외합니다.
- 기본 응답에서는 `imageUrl`, `iconUrl`이 `null`로 내려가고, `hasImage`, `hasIcon`으로 원본 이미지 존재 여부를 확인합니다.
- 이미지 문자열까지 필요한 경우 `?includeAssets=true`를 붙여 요청할 수 있습니다.
- `payload.assetPolicy`와 `meta.assetPolicy`를 추가해 현재 asset 포함 정책을 응답에 명시합니다.
- `scripts/check_master_data_api.py`가 기본 응답에 긴 data URL이 포함되지 않는지도 검사합니다.
- `docs/MASTER_DATA_ASSET_POLICY.md` 문서를 추가했습니다.

## v084 - Master Data Nested Asset Cleanup

- `v083`에서 최상위 `imageUrl`/`iconUrl`은 제거됐지만, `options`, `conditions`, `rules`, `raw` 같은 중첩 JSON 안에 남아 있던 `data:image...` 문자열을 추가로 제거했습니다.
- 기본 `/api/v1/game/master-data` 응답에서는 모든 중첩 inline image data URL을 `null`로 내려줍니다.
- `?includeAssets=true` 요청에서는 최상위 asset 필드와 중첩 JSON 안의 asset 문자열을 모두 포함합니다.
- `tools/smoke_master_data_nested_asset_cleanup.py`를 추가했습니다.

## v085 - Frontend Master Data Bridge

- 브라우저에서 FastAPI `/api/v1/game/master-data`를 호출할 수 있는 프론트 API 클라이언트를 추가했습니다.
- `src/api/game-api-client.js`, `src/api/master-data-bridge.js`를 추가했습니다.
- 기존 게임 동작은 아직 정적 JS 데이터를 그대로 사용하며, API 데이터는 검증/캐시용 snapshot으로만 보관합니다.
- 브라우저 콘솔에서 `await checkBackendMasterData()`로 백엔드 master-data 연결을 확인할 수 있습니다.
- `tools/smoke_frontend_master_data_bridge.js` 정적 검증 도구와 `docs/FRONTEND_MASTER_DATA_BRIDGE.md` 문서를 추가했습니다.

## v088 - Frontend master-data adapter

- Added `src/api/master-data-adapter.js`.
- Converts `/api/v1/game/master-data` payload into legacy-like browser data structures without changing live gameplay yet.
- Added browser console helpers: `checkBackendMasterDataAdapter()`, `loadAdaptedBackendMasterData()`, `getCachedAdaptedBackendMasterData()`.
- Added `tools/smoke_master_data_adapter.js` to verify adapter structure, counts, boss split, field count, item count, and nullable skill proc rate preservation.
- Documented the adapter in `docs/MASTER_DATA_ADAPTER.md`.

## v089 - Backend master-data runtime switch

- Added `src/api/master-data-runtime-switch.js`.
- Backend master-data runtime mode is OFF by default and can be enabled from the browser console.
- Console helpers: `enableBackendMasterDataMode()`, `disableBackendMasterDataMode()`, `checkBackendMasterDataRuntimeMode()`.
- When enabled, FastAPI master-data is fetched with `includeAssets=true`, adapted to legacy-like structures, and injected before the original game initialization runs.
- Injection mutates existing legacy objects/arrays instead of reassigning top-level `const` declarations.
- If API loading fails, the game falls back to the existing static JS data.
- Added `tools/smoke_master_data_runtime_switch.js` and `docs/MASTER_DATA_RUNTIME_SWITCH.md`.

## v090 - Backend master-data runtime validator

- Added `src/api/master-data-runtime-validator.js`.
- Added browser console helpers: `checkBackendMasterDataRuntimeIntegrity()`, `assertBackendMasterDataRuntimeIntegrity()`, `getBackendMasterDataRuntimeDebugSnapshot()`.
- The validator checks backend runtime mode state, active global master-data counts, applied backend data counts, core DOM availability, and sample boss/field/skill values.
- Added `tools/smoke_master_data_runtime_validator.js` and `docs/MASTER_DATA_RUNTIME_VALIDATOR.md`.
- Existing game behavior remains unchanged. The validator only inspects runtime state.

## v091 - Backend master-data browser checklist

- Added `src/api/master-data-browser-checklist.js`.
- Added browser console helpers: `runBackendMasterDataBrowserChecklist()`, `assertBackendMasterDataBrowserChecklist()`, `printBackendMasterDataManualChecklist()`.
- The checklist verifies backend master-data mode state, required helper functions, core DOM ids, rendered boss/field/inventory/equipment panels, sample data, and nullable `lightsabre` proc rate preservation.
- Added `tools/smoke_master_data_browser_checklist.js` and `docs/MASTER_DATA_BROWSER_CHECKLIST.md`.
- Existing game behavior remains unchanged. The checklist only inspects and optionally re-renders existing panels.
## v092 - Backend master-data auto boot policy

- Added `src/api/master-data-boot-policy.js`.
- Added default `auto` boot policy with static JS fallback.
- Added API request timeout support through `AbortController`.
- Updated runtime switch to hydrate missing image/icon assets from already-loaded static JS data when API assets are excluded.
- Added `tools/smoke_master_data_auto_boot_policy.js`.



## v093 - Browser checklist optional modal fix

- `#test-special-item-modal`을 필수 DOM에서 선택 DOM으로 변경했다.
- 특수 장비 지급 모달 요소가 동적 생성/생략되는 구조에서도 백엔드 master-data checklist가 불필요하게 실패하지 않도록 보정했다.
- 체크리스트 버전을 `v093.backend-master-data-browser-checklist`로 갱신했다.
- 수동 체크리스트 중복 문구를 제거했다.


### v093 추가 보정 - Master-data bridge timeout summary

- `src/api/master-data-bridge.js`의 `checkMasterDataApi()` summary에서 정의되지 않은 `timeoutMs` 변수를 참조하던 문제를 수정했다.
- `snapshot.timeoutMs`를 사용하도록 변경해 브라우저와 Node smoke test 모두 안정적으로 동작하게 했다.

## v094 - Field zone asset fallback

- 백엔드 master-data 기본 응답에서 assets를 제외할 때 필드존 이미지가 `undefined`가 되어 `file:///.../undefined` 요청이 발생하던 문제를 수정했다.
- `master-data-adapter`가 field zone의 `img`/`hasImage` 필드를 명시하도록 보강했다.
- `master-data-runtime-switch`가 기존 정적 `zones` 데이터에서 field zone 이미지 값을 보정하도록 추가했다.
- `renderFieldZone()`에 최후 방어용 기본 이미지 fallback을 추가했다.
- `tools/smoke_field_zone_asset_fallback.js`와 `docs/MASTER_DATA_FIELD_ZONE_ASSET_FALLBACK.md`를 추가했다.


## v096 - Master-data dev badge HUD position

- 개발자용 master-data 배지를 bottom HUD 내부로 이동했다.
- 배지 위치를 중앙 능력치 패널 오른쪽, 프로필 사진의 반대편에 배치했다.
- `hide` 버튼으로 숨긴 배지를 `showBackendMasterDataDevBadge()`로 다시 표시할 수 있음을 문서화했다.
- 작은 화면에서는 배지가 오른쪽 위로 이동하도록 반응형 위치를 보정했다.

## v097 - Master-data dev badge controls polish

- 개발자용 master-data 배지의 버튼 줄 넘침 문제를 수정했다.
- `hide` 버튼을 배지 내부에서 분리해 배지 위쪽의 별도 토글 버튼으로 이동했다.
- 배지를 숨긴 뒤에도 화면의 `show MD` 버튼으로 다시 표시할 수 있게 했다.
- `auto` / `static` 버튼에 현재 적용 중인 모드를 나타내는 활성 스타일을 추가했다.
- `refresh` 버튼의 의미를 명확히 하기 위해 `updated` 시간을 표시하고 문서를 보강했다.

## v099 - Save Snapshot API Bridge

- Added `user_save_snapshots` table/model for raw localStorage save snapshots.
- Implemented `POST /api/v1/game/save` and `GET /api/v1/game/load` as DB-backed snapshot APIs.
- Added browser helpers: `pushLocalSaveToBackend()`, `loadBackendSaveSnapshot()`, and `checkBackendSaveSnapshotBridge()`.
- Added static and live smoke tests for the save snapshot bridge.

## v100 - Save Data Dual Write

- Added `src/api/save-data-sync-policy.js`.
- Manual save now keeps the existing localStorage save and then attempts to push the same snapshot to `POST /api/v1/game/save`.
- Backend save failure does not block or undo localStorage save; it only records a fallback status and logs a warning.
- Added browser helpers: `getBackendSaveSyncPolicy()`, `getBackendSaveSyncStatus()`, `enableBackendSaveDualWrite()`, `disableBackendSaveDualWrite()`, `syncLatestLocalSaveToBackend()`.
- Added `tools/smoke_save_data_dual_write.js` and `docs/SAVE_DATA_DUAL_WRITE.md`.
## v102 - Save Data default dual mode and cooldown status

- SAVE DATA 기본 모드를 로컬 개발 환경에서 `manual_dual`로 복구했습니다.
- v101에서 저장된 `local_only` 테스트 상태가 다음 접속까지 남아 DB 저장 테스트를 방해하는 문제를 완화했습니다.
- `dual`/`local` 버튼 클릭 시 이전 `skipped_local_only_mode` 상태가 남지 않도록 상태를 즉시 갱신합니다.
- 수동 저장 쿨타임 중에는 `skipped_manual_save_cooldown` 상태를 표시합니다.
- SAVE DATA 배지의 `sync`/`load` 버튼명을 `sync DB`/`load DB`로 명확히 바꿨습니다.

## v107 - Save Data badge restore actions

- Added `preview` and `backup` buttons to the `SAVE DATA` development badge.
- `preview` opens the DB save restore preview modal without needing browser Console commands.
- `backup` restores the latest pre-restore localStorage backup after browser confirmation.
- The restore modal now shows a stronger reload warning, latest backup summary, and a `최근 백업으로 되돌리기` button.
- Restore preview values are escaped before insertion into modal HTML.
- No DB reset or seed import is required.
- Added `tools/smoke_save_data_badge_restore_actions.js` and `docs/SAVE_DATA_BADGE_RESTORE_ACTIONS.md`.

## v109 - Save Data slot list

- Added `GET /api/v1/game/save-slots` to list DB save-slot metadata without returning full raw snapshot JSON.
- Added `GameService.list_save_slots()` and `_serialize_save_slot()`.
- Added browser helper module `src/api/save-data-slots.js`.
- Added browser helpers: `listBackendSaveSlots()`, `openBackendSaveSlotsModal()`, and `checkBackendSaveSlotsReady()`.
- Added a `slots` button to the `SAVE DATA` development badge.
- Updated `backend/scripts/check_save_snapshot_api.py` to verify the saved slot appears in the slot list.
- No DB reset or seed import is required because the existing `user_save_snapshots` table already has `slot_key`.

## v110 - Save Data integrity verify

- Added backend integrity metadata for save snapshots: `snapshotSha256`, `snapshotBytes`, summary keys, important item counts, and warnings.
- Added `slotKey` validation to reject unsafe slot names before saving.
- Added browser helper module `src/api/save-data-integrity.js`.
- Added browser helpers: `verifyBackendSaveSnapshotIntegrity()`, `pushLocalSaveToBackendAndVerify()`, and `checkBackendSaveIntegrityReady()`.
- Manual dual-write now verifies the DB snapshot after saving and records `synced_verified` or `saved_verify_failed`.
- Updated the live save snapshot API checker to verify integrity metadata and invalid slot-key rejection.
- No DB reset or seed import is required because the DB schema is unchanged.

## v112 - Admin read-only page shell

- Added `admin.html` as a static read-only admin page shell outside the game screen.
- Added `src/api/admin-page-readonly.js` to render admin overview and recent save snapshot summaries with existing read-only APIs.
- Added API base URL controls for local development.
- Added `openAdminReadOnlyPage()` and a `관리자 페이지 열기` action from the admin overview modal.
- The page does not mutate DB/localStorage/game runtime and does not render raw `snapshot_json`.
- No DB reset or seed import is required.


## v114 - Admin save snapshot filters

- Added read-only filters to `admin.html` for recent save snapshot summaries.
- Added `/admin/save-snapshots` query filters: `userId`, `slotKey`, `source`, `defaultOnly`, and `sort`.
- The filtered admin API still does not return raw `snapshot_json` and keeps `rawSnapshotReturned=false`.
- Added browser helpers `readAdminSnapshotFilters()` and `resetAdminSnapshotFilters()` for console diagnostics.
- No DB reset or seed import is required because the existing `user_save_snapshots` table is only queried.

## v115 - Admin master data catalog

- Added read-only master-data catalog APIs for the admin page: `/admin/master-data/domains` and `/admin/master-data/catalog`.
- Added admin page filters for master-data domain, search query, enabled status, limit, and sort.
- Added generic catalog rendering in `admin.html` so item templates, skills, bosses, fields, drops, enhancement data, and character links can be browsed without editing.
- The catalog deliberately keeps `rawJsonReturned=false` and `assetsReturned=false`; raw JSON blobs and inline image data URLs are not exposed.
- Added browser helpers `readAdminMasterCatalogFilters()` and `resetAdminMasterCatalogFilters()`.
- Updated `backend/scripts/check_admin_readonly_api.py` and smoke tests to include the new catalog endpoints.
- No DB reset or seed import is required because the existing master-data tables are queried only.

## v116 - admin master data detail

- 관리자 마스터 데이터 상세 조회 API 추가: `GET /api/v1/admin/master-data/detail`.
- 관리자 페이지 카탈로그 행에 `보기` 버튼 추가.
- 선택한 마스터 데이터 상세 패널 추가.
- scalar 필드, 연결 요약, 에셋 숨김 상태, JSON 안전 미리보기를 표시.
- raw JSON 전체와 이미지 data URL은 계속 숨김.
- 관리자 쓰기 UI는 계속 차단.
- DB reset/seed 불필요.

## v123 - Admin change log rollback

- Added admin change log detail API: `GET /api/v1/admin/change-logs/{change_log_id}`.
- Added guarded rollback preview/apply APIs for master-data edit logs.
- Rollback is blocked if the current DB row no longer matches the original change log `after_json`, preventing old rollback operations from overwriting newer edits.
- Added rollback controls to the admin change-log section.
- Added `ROLLBACK MASTER DATA EDIT` confirmation text for rollback apply.
- Added `stackable` true/false explanation to the admin field help and value hints.
- No DB reset or seed import is required because the existing `admin_change_logs` table is reused.

## v125 - Runtime stacked enhance space guard

- Added a shared runtime guard for enhancing stacked items that require a temporary 1-slot split.
- The guard now applies to DB `stackable=true` equipment, talisman stacks, and shining emblem stacks.
- If a stacked item has `count > 1` and its current container is full, enhancement is blocked before any item count/material is consumed.
- The user-facing message is `[시스템] 겹쳐진 장비를 강화하려면 먼저 1칸의 빈 공간이 필요합니다.`
- No DB reset or seed import is required because only runtime enhancement logic changed.
## v126 - Admin edit impact guide

- Added an in-page impact guide to the guarded admin edit draft UI.
- Changing a draft value now shows likely in-game impact before validation/apply.
- Added specific guidance for `stackable`, boss HP, field rewards, skill proc/cooldown, drop rate/quantity, and enhancement success/cost fields.
- The guide explicitly notes when game reload is needed and that existing saved stackable items are not automatically merged.
- No DB reset or seed import is required because this is admin UI guidance only.

