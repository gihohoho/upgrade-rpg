# Admin Field Help

v120 단계에서는 관리자 페이지에서 자주 헷갈리는 마스터 데이터 필드에 부연설명을 표시한다.

## 목적

관리자 페이지가 읽기 전용 목록/상세/편집 초안까지 확장되면서 `grade`, `enhance group code`, `admin note`처럼 코드명만 보면 의미가 애매한 필드가 보이기 시작했다. 이 문서는 해당 설명을 화면에 같이 보여주는 기준을 정리한다.

## 추가된 화면 요소

- 관리자 페이지 상단 바로가기: `필드 도움말`
- 관리자 페이지 내부 섹션: `필드 용어 도움말`
- 카탈로그 표/상세 필드/편집 초안 필드 옆 `?` 도움말 배지
- Console helper:
  - `getAdminFieldHelp("grade")`
  - `getAdminFieldHelp("enhanceGroupCode")`
  - `getAdminFieldHelp("adminNote")`
  - `listAdminFieldHelp()`

## 주요 필드 설명

### grade

현재 프로젝트에서는 일반적인 희귀도명이 아니라, 기존 JS 아이템의 `tier` 값을 옮겨 담은 숫자형 진행 등급이다. 아이템이 어느 보스/장비 성장 구간에 속하는지, 드랍 단계와 장비 진행도를 맞출 때 참고한다.

예: `grade=1`은 1티어/초반 구간, `grade=12`는 12티어/상위 구간이다. 희귀도 이름이 필요해지면 `rarity` 같은 별도 필드로 분리하는 편이 안전하다.

### enhance group code

이 아이템이 어떤 강화 규칙 묶음을 사용할지 연결하는 코드다. 아이템의 `enhance_group_code`와 강화 그룹의 `code`가 같으면 해당 강화 그룹/강화 단계가 아이템에 적용된다.

예: `weapon_basic` 아이템 → `enhancementGroups.code=weapon_basic` → `enhancementLevels.group_code=weapon_basic` 단계 적용.

### admin note

게임 플레이 화면에는 보여주지 않는 운영자용 메모다. 데이터 작업 이유, 주의사항, 임시 설명, 나중에 확인할 내용을 적어두는 내부 기록용 필드다.

예: 밸런스 조정 예정, 이벤트 드랍 전용, 아직 미사용 데이터 등.

## 안전장치

이번 단계는 화면 설명만 추가한다.

- DB 수정 없음
- localStorage 수정 없음
- 게임 런타임 수정 없음
- 관리자 저장 버튼은 계속 잠김
- 쓰기 API 추가 없음

DB reset/seed는 필요 없습니다.

## v259 compact catalog help update

관리자 카탈로그 목록은 긴 설명문을 직접 표시하지 않고 핵심 라벨만 보여준다.

예시:

- `normal · 일반 장비`
- `skill_book · 스킬강화권`
- `6 · 특수무기`
- `true · 겹치기 가능`

자세한 설명은 다음 위치에서 확인한다.

- 카탈로그 표 제목 옆 `?` 배지
- 편집 초안 입력칸 옆 `?` 배지
- compact 값의 tooltip
- `필드 용어 도움말` 섹션

필드 도움말은 v259에서 다음 그룹으로 확장했다.

- 기본 필드: `id`, `code`, `name`, `description`, `grade`, `is_enabled`, `sort_order`, `admin_note`
- 아이템/장비: `item_type`, `equip_slot`, `stackable`, `enhance_group_code`, `base_stats`, `options`, `json_keys`
- 스킬/전투/보상: `slot_key`, `proc_rate`, `proc_rate_bonus`, `cooldown_seconds`, `damage_multiplier`, `hp`, `enemy_hp`, `gold_reward`
- 관계/드랍/강화: `owner_type`, `owner_code`, `drop_table_code`, `item_template_code`, `rate`, `min_quantity`, `max_quantity`, `from_level`, `to_level`, `success_rate`, `gold_cost`, `character_code`, `skill_code`

이 작업은 화면 설명과 표시 방식만 바꾸며 DB reset/seed는 필요 없습니다.
