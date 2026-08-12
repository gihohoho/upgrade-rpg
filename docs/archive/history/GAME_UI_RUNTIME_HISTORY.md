# 게임 UI·런타임 개발 역사

> 완료된 단계별 메모를 검색 가능한 한 파일로 통합한 읽기 전용 역사입니다.
> 현재 작업 판단에는 `docs/current/`와 루트 `NEXT_CHAT_HANDOFF.md`를 사용하세요.
> 원본 파일은 Git commit `270d57bd234ede18cee7168f4b5da36b1a08df18` 이전 이력에서 복원할 수 있습니다.

## 통합된 원본

- `docs/archive/stage-notes/CSS_AUDIT.md`
- `docs/archive/stage-notes/CSS_MERGE_REPORT.md`
- `docs/archive/stage-notes/DAMAGE_TEXT_POSITION_FIX.md`
- `docs/archive/stage-notes/DEV_BADGE_BOTTOM_DOCK.md`
- `docs/archive/stage-notes/EQUIP_SKILL_BOSS_RESULT_STAGE3.md`
- `docs/archive/stage-notes/KILL_REWARD_RESULT_STAGE2.md`
- `docs/archive/stage-notes/RUNTIME_STACKABLE_ITEMS.md`
- `docs/archive/stage-notes/RUNTIME_STACKED_ENHANCE_SPACE_GUARD.md`
- `docs/archive/stage-notes/SKILL_DAMAGE_TEXT_FIX.md`
- `docs/archive/stage-notes/SKILL_STRUCTURE_READY.md`
- `docs/archive/stage-notes/UI_RESULT_SEPARATION_STAGE1.md`

---

## 원본: `docs/archive/stage-notes/CSS_AUDIT.md`

# CSS 점검 보고서

## 점검 대상

```txt
src/styles/style.css
```

## 요약 결론

현재 CSS는 같은 클래스/선택자가 여러 곳에서 반복됩니다.
다만 전부 버그라고 보기는 어렵고, 일부는 아래 목적의 의도된 누적 스타일입니다.

```txt
기본 스타일 정의
특정 패널에서만 덮어쓰기
버전별 추가 패치
모바일/하단 HUD 보정
토글 ON/OFF 상태 보정
```

하지만 파일이 커진 상태라서 유지보수성은 떨어지고 있습니다.

## 검사 결과

단순 선택자 기준 검사 결과:

```txt
전체 선택자 수: 약 535개
고유 클래스 수: 약 231개
2회 이상 등장한 클래스 수: 약 105개
완전히 같은 선택자가 2회 이상 등장한 항목: 약 93개
```

많이 반복되는 클래스 예시:

```txt
damage-text: 21회
inv-header: 12회
town-hub-btn: 11회
gold-box: 10회
item-slot: 9회
unique-stat-row: 9회
skill-slots-grid: 8회
sys-btn: 8회
inv-grid-50: 7회
action-btn: 6회
```

완전히 같은 선택자가 여러 번 등장하는 예시:

```txt
#item-action-panel
#mailbox-panel
#trash-panel
#inv-panel
#storage-panel
.gold-box
.hud-center-stats
.action-btns
.hud-sys-btns
```

## 주의해서 볼 부분

### 1. `.skill-slots-grid`

여러 위치에서 반복됩니다.

```txt
기본 그리드
스킬 슬롯 wrapper
쿨타임 텍스트
하단 HUD 보정
추가 패치
```

현재 게임이 정상 동작한다면 바로 합치기보다, 스킬 UI를 Vue 컴포넌트로 옮길 때 함께 정리하는 것이 안전합니다.

### 2. `.sys-btn`

기본 버튼 스타일과 테스트 패널/아이템 리스트/토글 상태 스타일이 섞여 있습니다.

관리자 페이지까지 고려하면 나중에 아래처럼 분리하는 게 좋습니다.

```txt
.btn
.btn--system
.btn--test
.btn--toggle
.btn--danger
.btn--primary
```

### 3. 패널 ID 선택자

아래 선택자들이 여러 번 반복됩니다.

```txt
#inv-panel
#storage-panel
#trash-panel
#mailbox-panel
#item-action-panel
```

패널 공통 스타일을 하나로 묶고, 각 패널 차이만 별도 클래스로 빼는 게 좋습니다.

예상 구조:

```txt
.panel
.panel--inventory
.panel--storage
.panel--trash
.panel--mailbox
.panel--action
```

## SCSS로 바꾸는 게 좋을까?

현재 단계에서는 바로 SCSS로 바꾸는 것보다 **CSS 유지 + 구조 정리 문서화**가 더 안전합니다.

이유:

```txt
현재 프로젝트는 아직 Vite/Vue 빌드 환경이 아닙니다.
SCSS를 쓰려면 빌드 도구가 필요합니다.
지금은 index.html에서 CSS를 직접 불러오는 구조입니다.
백엔드 분리 준비 중이라 CSS 빌드 환경까지 동시에 바꾸면 테스트 범위가 커집니다.
```

## 추천 방향

### 지금 당장

```txt
CSS 유지
중복 선택자 위치 문서화
위험한 통합은 보류
```

### 다음 정리 단계

```txt
style.css를 기능별 CSS 파일로 나누기
예: base.css, layout.css, hud.css, inventory.css, combat.css, modal.css, admin.css
```

### Vue/Vite로 넘어갈 때

그때 SCSS 도입을 추천합니다.

```txt
Vue/Vite 전환 후 SCSS 사용 추천
컴포넌트별 scoped style 또는 SCSS partial 사용
변수, mixin, 공통 버튼 스타일 관리
```

## 최종 판단

```txt
지금: CSS 유지가 좋음
중기: CSS 파일 분리 추천
Vue/Vite 전환 후: SCSS 도입 추천
```

## 중복 선택자 정리 원칙

현재 CSS에는 같은 클래스명 또는 같은 선택자가 여러 번 등장합니다. 다만 아래 두 개는 의미가 다릅니다.

```txt
2회 이상 등장한 클래스 수
→ 같은 클래스명이 여러 문맥에서 쓰인다는 뜻입니다.
→ 예: .item-slot, .gold-box 등이 기본/상태/미디어쿼리/자식 선택자에서 반복될 수 있습니다.
→ 이것만 보고 하나로 합치면 위험합니다.

완전히 같은 선택자가 2회 이상 등장한 항목
→ 선택자 문자열 자체가 같은 규칙이 여러 번 선언되었다는 뜻입니다.
→ 이 항목은 병합 후보가 맞지만, 뒤쪽 선언이 앞쪽 선언을 덮어쓰는 의도일 수 있어서 값 비교 후 선별 병합해야 합니다.
```

권장 순서:

```txt
1. 완전히 같은 선택자 + 충돌 없는 속성부터 병합
2. 같은 클래스지만 상태/반응형/자식 선택자가 다른 규칙은 유지
3. Vue/Vite 전환 전까지는 SCSS 전환보다 CSS 파일 분리를 우선
4. SCSS는 Vue 전환 후 도입
```



## v070 추가 정리 결과

`style.css`에서 최종 CSS 적용값이 유지되는 것으로 검증된 안전 중복 규칙만 병합했습니다.

```txt
병합/제거한 안전 중복 규칙: 38개
영향을 받은 선택자 그룹: 30개
병합 후 완전 동일 중복 블록: 0개
남은 중복 선택자: 55개
```

남은 중복 선택자는 cascade 순서, 상태별 스타일, 향후 CSS 파일 분리 가능성을 고려해 이번 작업에서는 유지했습니다. 자세한 기준은 `docs/archive/stage-notes/CSS_MERGE_REPORT.md`를 참고하세요.

---

## 원본: `docs/archive/stage-notes/CSS_MERGE_REPORT.md`

# CSS 중복 병합 리포트

## 목적

`src/styles/style.css`에서 완전히 같은 선택자가 여러 번 등장하는 항목 중, 현재 적용 결과를 바꾸지 않는 범위만 안전하게 병합했습니다.

## 병합 기준

이번 작업에서는 모든 중복 선택자를 무조건 합치지 않았습니다.

CSS는 뒤에 나온 규칙이 앞의 규칙을 덮어쓸 수 있기 때문에, 같은 선택자가 여러 번 등장한다고 해서 항상 하나로 합쳐도 되는 것은 아닙니다.

이번 병합 기준은 다음과 같습니다.

1. 같은 선택자가 뒤에서 동일 속성을 다시 선언하여 앞 선언이 최종 결과에 영향을 주지 않는 경우
2. 앞 선언을 뒤 선택자로 옮겨도 중간에 같은 속성을 건드리는 규칙이 없어 최종 결과가 유지되는 경우
3. 병합 후 같은 선택자의 최종 선언값이 병합 전과 동일한 경우

## 병합 결과

- 병합/제거한 안전 중복 규칙 수: 38개
- 영향을 받은 선택자 그룹 수: 30개
- CSS 파싱 오류: 0개
- 병합 후 완전히 동일한 중복 규칙 블록: 0개

## 병합 후 남겨둔 중복

아직 같은 선택자가 2회 이상 등장하는 항목은 남아 있습니다.

남겨둔 이유는 다음 중 하나입니다.

- 나중에 나온 규칙이 의도적으로 앞 규칙을 덮어쓰고 있음
- 중간에 같은 속성을 가진 다른 선택자가 있어서 위치를 옮기면 cascade 결과가 바뀔 수 있음
- 반응형/상태별 확장 가능성이 있어 수동 확인이 필요함

따라서 남은 중복은 다음 CSS 정리 단계에서 기능별 파일 분리와 함께 다시 보는 것이 안전합니다.

추천 다음 단계:

```txt
src/styles/base.css
src/styles/layout.css
src/styles/hud.css
src/styles/inventory.css
src/styles/combat.css
src/styles/modal.css
src/styles/town.css
```

## 검증 방식

병합 전/후로 top-level CSS 규칙을 파싱해서, 각 선택자의 최종 선언값이 동일한지 비교했습니다.

확인한 항목:

- CSS 파싱 오류 없음
- 병합 대상 선택자의 최종 선언값 동일
- JavaScript 문법 검사 통과

## 참고

SCSS 전환은 아직 보류합니다.

현재 프로젝트는 `index.html + style.css` 직접 로딩 구조이므로, SCSS를 쓰려면 빌드 도구를 추가해야 합니다. 지금 목표는 백엔드 분리 준비이므로, CSS는 일단 일반 CSS 상태에서 안전하게 정리하고, Vue/Vite 전환 시점에 SCSS 도입을 다시 검토하는 것이 좋습니다.

---

## 원본: `docs/archive/stage-notes/DAMAGE_TEXT_POSITION_FIX.md`

# 스킬 데미지 텍스트 표시 위치 수정 기록

## 문제

스킬이 발동해도 `[W]`, `[R]`, `[T]`, `[F]`, `[D]`, `[SQ]`, `[SW]`, `진각성` 데미지 텍스트가 화면에 보이지 않는 문제가 확인되었습니다.

## 원인

전투 데미지 텍스트 위치가 `.enemy-display`의 전체 너비를 기준으로 계산되고 있었습니다.

```js
const rect = document.querySelector(".enemy-display").getBoundingClientRect();
dEl.style.left = rect.left - zRect.left + rect.width + 18 + ...
```

현재 CSS에서 `.enemy-display`는 `width: 100%`이기 때문에, `rect.width`가 전투 영역 전체 폭이 될 수 있습니다. 그 결과 데미지 텍스트가 화면 오른쪽 바깥으로 배치되어 실제로는 생성되어도 보이지 않을 수 있었습니다.

## 수정 내용

`src/systems/combat-system.js`에 아래 보조 함수를 추가했습니다.

- `getDamageTextAnchorRect()`
- `clampDamageTextPosition()`
- `getBattleZoneSize()`

이제 데미지 텍스트는 `.enemy-display` 전체가 아니라 `#enemy-image-placeholder`, 즉 몬스터 이미지 근처를 기준으로 표시됩니다.

또한 전투 영역 밖으로 나가지 않도록 좌표를 보정합니다.

## 주의

검신 캐릭터의 일반 Q 스킬은 지속형/패시브형 추가 데미지이므로, 기존 의도대로 `[Q] 데미지` 텍스트를 띄우지 않습니다.

텍스트 표시 대상은 기존과 동일하게 다음 계열입니다.

- W
- R
- T
- F
- D
- SQ
- SW
- 진각성
- E 버프 발동/종료 메시지

## 확인 방법

1. 스킬 레벨이 있는 상태로 필드 또는 보스 전투를 진행합니다.
2. W/R/T/F/D/SQ/SW/진각성 발동 시 몬스터 이미지 오른쪽 근처에 데미지 텍스트가 보이는지 확인합니다.
3. Q 일반 패시브 데미지는 텍스트가 뜨지 않는 것이 정상입니다.

---

## 원본: `docs/archive/stage-notes/DEV_BADGE_BOTTOM_DOCK.md`

# v103 - 개발자 배지 하단 HUD 위 배치

## 목적

`MASTER DATA` 배지와 `SAVE DATA` 배지를 하단 인터페이스 내부가 아니라, 하단 HUD 바로 위쪽에 고정 배치한다.

기존에는 배지가 하단 HUD 안쪽이나 오른쪽 슬롯 근처에 섞여 보여서 스킬칸/버튼과 겹치거나 어색하게 보일 수 있었다.

## 배치 기준

데스크톱 기준:

```txt
[ MASTER DATA ] [ SAVE DATA ]
-----------------------------
        하단 HUD / 스킬칸
```

- `SAVE DATA`: 오른쪽 하단 HUD 위쪽
- `MASTER DATA`: `SAVE DATA` 왼쪽
- 두 배지 모두 `position: fixed`로 화면 기준 배치
- `bottom: 158px` 기준으로 하단 HUD 바로 위에 위치

## 모바일/좁은 화면 처리

폭이 좁아지면 두 배지를 가로로 무리하게 넣지 않고, `MASTER DATA`를 더 위로 올려 세로로 분리한다.

```txt
[ MASTER DATA ]
[ SAVE DATA ]
---------------
하단 HUD
```

## 변경 파일

```txt
src/api/master-data-dev-badge.js
src/api/save-data-dev-badge.js
tools/smoke/game/smoke_master_data_dev_badge.js
tools/smoke/game/smoke_save_data_dev_badge.js
```

## 영향 범위

- 개발자용 배지 위치만 변경한다.
- master-data 로딩, save-data 저장/동기화 로직은 변경하지 않는다.
- DB reset/seed import는 필요 없다.

---

## 원본: `docs/archive/stage-notes/EQUIP_SKILL_BOSS_RESULT_STAGE3.md`

# 4순위 3차 - 장착/해제/스킬강화권/보스소환 결과 객체화

## 목적

백엔드 분리 전에 프론트 전용 함수가 직접 UI를 갱신하는 부분을 줄이고, FastAPI 응답으로 옮기기 쉬운 `Action Result` 구조를 확장합니다.

이번 단계는 기존 게임 동작을 유지하면서 아래 행동의 결과를 객체로 남기는 것이 목적입니다.

```txt
item.equip
item.unequip
skill_book.use
boss.summon
```

## 변경 파일

```txt
src/systems/action-result-system.js
src/systems/item-system.js
src/ui/render-ui.js
```

## 추가된 결과 타입

### item.equip

장비 장착 성공/실패 결과를 기록합니다.

주요 데이터:

```txt
itemName
targetSlotIndex
equippedItem
replacedItem
splitFromStack
returnedOldEquip
mergedOldEquip
reason
```

### item.unequip

장비 해제 성공/실패 결과를 기록합니다.

주요 데이터:

```txt
itemName
slotIndex
mergedIntoInventory
reason
```

### skill_book.use

스킬강화권 사용 성공/실패 결과를 기록합니다.

주요 데이터:

```txt
itemName
skillKey
beforeLevel
afterLevel
beforeCount
afterCount
awakeningBook
wasUpgraded
isUpgraded
reason
```

### boss.summon

일반보스/특수보스 소환 성공/실패 결과를 기록합니다.

주요 데이터:

```txt
bossId
bossName
isSpecialBoss
currentBossHp
currentBossMaxHp
transition
cooldownUntil
cooldownRemainMs
reason
```

## 기존 동작 유지 원칙

이번 작업은 기능 변경이 아닙니다.

기존과 동일하게 아래 UI 동작을 유지합니다.

```txt
장착/해제 후 액션 패널 닫기
장착/해제 후 전체 UI 갱신
전투 중 장착/해제 후 자동공격 재시작
스킬강화권 사용 후 스킬창/전체 UI 갱신
보스 소환 후 보스 패널 닫기
보스 소환 후 자동공격 시작
```

다만 이제 직접 UI 함수를 흩뿌려 호출하기보다, `Action Result`에 UI 요청을 모은 뒤 `applyActionResultUi()`에서 처리합니다.

## 다음 단계

4순위 후속 후보:

```txt
보관함/휴지통/우편 이동 결과 객체화
removeBoss 결과 객체화
toggle 계열 명령어 결과 객체화
```

하지만 백엔드 분리 준비 관점에서는 이제 핵심 플레이 흐름의 결과 객체 기반은 상당 부분 깔렸으므로, 다음 큰 단계는 `5순위 API 응답 형태 확정`으로 넘어갈 수 있습니다.

---

## 원본: `docs/archive/stage-notes/KILL_REWARD_RESULT_STAGE2.md`

# 4순위 2차: 처치/드랍/보상 결과 객체화

## 목적

`killEnemy()`는 기존에 아래 작업을 한 함수 안에서 모두 처리했습니다.

- 보스/필드 몬스터 처치 판정
- 드랍 확률 판정
- 아이템 지급
- 골드/성장 보상 지급
- 로그 출력
- 드랍 텍스트 표시
- UI 갱신

FastAPI로 옮기려면 서버가 먼저 결과를 계산하고, 프론트는 그 결과를 받아 화면에 표시하는 구조가 필요합니다.
이번 단계에서는 기존 동작을 유지하면서 `combat.kill` 결과 객체를 추가했습니다.

## 추가/변경된 핵심 구조

### `createEnemyKillResult()`

위치: `src/systems/action-result-system.js`

처치 결과를 API 응답에 가까운 형태로 만듭니다.

```js
{
  ok: true,
  type: "combat.kill",
  payload: {
    zoneType,
    zoneIndex,
    targetName
  },
  logs: [],
  effects: [],
  ui: {},
  data: {
    drops: [],
    rewards: {},
    transition: {}
  }
}
```

### `addDropAward()`

드랍 아이템 로그와 드랍 텍스트 표시 요청을 결과 객체에 모읍니다.

```js
addDropAward(result, itemName, message, {
  stacked: true,
  stored: false,
  dropType: "skill_book"
});
```

### `addRewardGold()`

필드 몬스터 처치 골드 보상을 결과 객체에 기록합니다.

### `addBlockedReward()`

가방/보관함이 꽉 차서 보상을 받지 못한 경우를 결과 객체에 기록합니다.

## 이번 단계에서 객체화한 범위

### 보스 처치

- 일반 장비 드랍
- 탈리스만 드랍
- 빛나는 휘장 등 개별확률 특수장비 드랍
- 스킬강화권 드랍
- 최초 장비 보너스 스킬강화권 지급
- 가방/보관함 부족으로 인한 보상 실패 기록
- 특수보스 쿨타임 적용 정보
- 처치 후 이동/재소환 전환 정보

### 필드 처치

- 골드 보상
- 공격속도 성장
- 순수공격력 노가다 성장
- 필드 몬스터 리스폰 예정 시각
- UI 갱신 요청

## 아직 남은 작업

이번 단계는 `killEnemy()` 중심입니다. 아래는 다음 단계 후보입니다.

- 장착/해제 결과 객체화
- 스킬강화권 사용 결과 객체화
- 보스 소환/특수보스 소환 결과 객체화
- 우편/보관함/휴지통 이동 결과 객체화
- `combat.kill` 결과를 FastAPI 응답 스키마로 확정

## 주의사항

이번 단계에서도 실제 게임 판정은 아직 프론트에서 이뤄집니다.
최종적으로는 다음 판정들이 FastAPI 서버로 이동해야 합니다.

- 드랍 확률 `Math.random()`
- 아이템 지급
- 골드 지급
- 특수보스 쿨타임 적용
- 필드 성장 판정

---

## 원본: `docs/archive/stage-notes/RUNTIME_STACKABLE_ITEMS.md`

# Runtime Stackable Items

## v124 목적

관리자 페이지에서 바꾼 `itemTemplates.stackable` 값을 인게임 신규 획득 아이템 겹치기 로직에 연결했습니다.

이전 상태:

```txt
관리자 stackable=true
→ DB 값 변경됨
→ master-data API로 내려옴
→ 하지만 인게임 신규 장비 획득 시에는 아직 별도 슬롯으로 들어감
```

v124 이후:

```txt
관리자 stackable=true
→ DB 값 변경됨
→ master-data API로 내려옴
→ 보스 드랍 아이템에 stackable=true 런타임 필드가 붙음
→ 신규 획득 시 같은 +0 아이템은 count로 겹침
```

## 적용 범위

- 신규 보스 드랍 장비부터 적용합니다.
- 기존 세이브 전체를 자동 병합하지 않습니다.
- 새로 획득한 `stackable=true` 아이템이 기존 세이브의 같은 +0 아이템과 만나면 그 슬롯에 겹치고, 기존 아이템에도 `stackable=true`를 보강합니다.
- `stackable=false` 아이템은 기존처럼 슬롯을 각각 차지합니다.

## 강화 안전장치

일반 장비가 `stackable=true`이고 count가 2개 이상인 상태에서 강화하면, 스택 전체가 한 번에 강화되지 않도록 1개만 분리해서 강화합니다.

단, 스택에서 1개를 분리하려면 인벤토리/보관함에 빈 칸이 1칸 필요합니다.

## 장착 안전장치

겹쳐진 일반 장비를 장착하면 1개만 장착하고, 나머지 수량은 기존 슬롯에 남습니다.

## 표시

인벤토리/보관함/휴지통 슬롯 배지는 일반 장비도 `count > 1`이면 `xN`을 표시합니다.

예:

```txt
샤이닝 인텔리전스 x3
```

## DB reset / seed 필요 여부

필요 없습니다.

DB 구조 변경 없이 기존 `itemTemplates.stackable` 값을 런타임에서 사용합니다.

---

## 원본: `docs/archive/stage-notes/RUNTIME_STACKED_ENHANCE_SPACE_GUARD.md`

# Runtime stacked enhance space guard

## 목적

v124에서 DB `itemTemplates.stackable=true` 아이템을 신규 획득 시 인게임에서 겹치도록 연결했다.
이후 겹쳐진 장비를 강화할 때는 1개만 분리해 강화해야 하므로, 가방/보관함이 꽉 찬 상태에서는 강화가 진행되면 안 된다.

v125에서는 이 규칙을 일반 stackable 장비뿐 아니라 탈리스만/빛나는 휘장 같은 특수 stackable 장비에도 동일하게 적용한다.

## 동작

- `count <= 1` 아이템은 기존 강화 흐름을 유지한다.
- `count > 1`인 겹친 장비를 강화하려면 현재 위치한 컨테이너에 빈 칸이 1칸 필요하다.
- 인벤토리에서 선택한 아이템은 `player.inventory.length < player.maxInventorySize`일 때만 분리 강화 가능하다.
- 보관함에서 선택한 아이템은 `player.storage.length < player.maxStorageSize`일 때만 분리 강화 가능하다.
- 가방/보관함이 꽉 찬 상태라면 강화 전에 중단하고 안내 문구를 표시한다.

## 적용 대상

- DB `stackable=true`로 겹쳐진 일반 장비
- 탈리스만 스택
- 빛나는 휘장 스택

## 안내 문구

```txt
[시스템] 겹쳐진 장비를 강화하려면 먼저 1칸의 빈 공간이 필요합니다.
```

## DB 변경 여부

DB reset/seed 불필요.
런타임 강화 로직만 수정한다.

---

## 원본: `docs/archive/stage-notes/SKILL_DAMAGE_TEXT_FIX.md`

# 스킬 데미지 텍스트 회귀 점검 및 수정

## 발견된 문제

v068에서 스킬을 캐릭터별 구조로 분리하면서 기존 저장 데이터와 새 구조 사이의 이관 경로가 부족했습니다.

기존 저장 데이터는 주로 아래 위치에 실제 스킬 레벨을 저장했습니다.

```txt
player.skills
```

v068 이후 전투/스킬 UI는 아래 새 구조를 우선 사용합니다.

```txt
player.userCharacters[player.currentCharacterId].skills
```

기존 저장 데이터를 불러올 때 `userCharacters`가 기본값으로 먼저 생성되면, 실제 스킬 레벨이 들어 있는 `player.skills`가 새 캐릭터 스킬 구조로 충분히 병합되지 않을 수 있었습니다.
그 결과 스킬 레벨이 기본값처럼 보이고, W/R/T/F/D/SQ/SW/진각성 등 발동형 스킬 데미지 텍스트가 안 뜨는 것처럼 보일 수 있습니다.

## 수정 내용

`src/data/skills.js`에 기존 스킬 저장값을 현재 캐릭터 스킬 상태로 병합하는 보정 로직을 추가했습니다.

추가된 주요 함수:

```txt
cloneSkillState()
isMeaningfulLegacySkillState()
shouldPreferLegacySkillState()
mergeLegacySkillsIntoCharacterSkills()
```

`normalizePlayerCharacterState()`는 이제 다음을 보장합니다.

```txt
기존 저장 player.skills
→ 현재 캐릭터 player.userCharacters[currentCharacterId].skills로 병합
→ player.skills는 다시 현재 캐릭터 skills와 같은 객체를 바라봄
```

## Q 스킬 텍스트 참고

현재 v065~v069 기준으로 일반 Q 스킬(광검 마스터리)은 매 공격마다 붙는 패시브형 추가 데미지라서 데미지 텍스트에 별도로 표시하지 않습니다.
텍스트로 표시되는 대표 스킬은 W/R/T/F/D/SQ/SW/진각성처럼 확률 발동형 스킬입니다.

일반 Q까지 `[Q] 34T`처럼 매 공격 표시하려면 별도의 표시 정책 변경이 필요합니다.
이 작업은 기능 변경에 해당하므로 이번 회귀 수정에는 포함하지 않았습니다.

---

## 원본: `docs/archive/stage-notes/SKILL_STRUCTURE_READY.md`

# 스킬 구조 변경 1차 완료 문서

## 목적

앞으로 캐릭터가 추가될 때를 대비해 스킬 관련 정보를 한 곳으로 모았습니다.

현재 게임의 핵심 전제는 아래와 같습니다.

```txt
캐릭터마다 달라지는 것은 스킬뿐입니다.
아이템, 장비, 보스, 드랍, 강화, 필드, 인벤토리는 공통 시스템입니다.
```

## 추가된 파일

```txt
src/data/skills.js
```

이 파일은 앞으로 DB의 아래 테이블로 옮길 후보입니다.

```txt
characters
skills
character_skills
skill_books
```

## 현재 구조

### 캐릭터 마스터 데이터

```js
characterMasterData
```

현재 기본 캐릭터는 아래 ID를 사용합니다.

```txt
weapon_master
```

### 스킬 마스터 데이터

```js
skillMasterData
```

현재 스킬 8개가 등록되어 있습니다.

```txt
Q  - 광검 마스터리
W  - 극 귀검술 - 참철식
E  - 오버 드라이브
R  - 발도
T  - 환영검무
F  - 극 귀검술 - 심검
D  - 극 귀검술 - 폭풍식
M  - 천제극섬
```

Q/W 각성 정보도 각 스킬 데이터 안에 들어 있습니다.

```txt
Q → SQ 극 귀검술 - 유성락
W → SW 극 발검술 - 무형참
```

### 스킬강화권 마스터 데이터

```js
skillBookMasterData
```

스킬강화권 이름과 대상 스킬의 연결을 이 파일에서 관리합니다.

기존 `skillBookMapping` 이름은 호환을 위해 유지하지만, 실제 원본은 `skillBookMasterData`입니다.

## 유저 스킬 상태

기존 코드는 아직 `player.skills`를 많이 사용합니다.

그래서 이번 단계에서는 기존 코드가 깨지지 않게 아래 구조를 같이 유지합니다.

```txt
player.currentCharacterId
player.ownedCharacterIds
player.userCharacters
player.skills
```

실제 기준 구조는 아래입니다.

```txt
player.userCharacters[player.currentCharacterId].skills
```

기존 호환 구조는 아래입니다.

```txt
player.skills
```

현재는 두 값이 같은 스킬 객체를 바라보게 동기화합니다.

## 주요 헬퍼 함수

```txt
getDefaultCharacterId()
getCharacterDefinition(characterId)
getSkillDefinition(skillId)
getCharacterSkillIds(characterId)
createDefaultCharacterSkillState(characterId)
getDefaultSkillState(characterId)
createSkillBookMapping()
getSkillBookDefinition(itemName)
getSkillBookDisplayInfo(itemName)
isAwakeningSkillBook(itemName)
getSkillMaxLevel(skillId)
normalizePlayerCharacterState(player)
getCurrentCharacterId(player)
getCurrentUserCharacter(player)
getCurrentCharacterSkills(player)
getSkillState(skillId, player)
getRenderableSkillList(player)
```

## 이번에 바뀐 파일

```txt
index.html
src/data/skills.js
src/state/game-state.js
src/ui/render-ui.js
src/systems/item-system.js
src/systems/combat-system.js
src/app/main.js
```

## 안전 장치

기존 코드 호환을 위해 아래 이름은 계속 유지했습니다.

```txt
player.skills
skillBookMapping
getSkillBookInfo()
renderSkills()
```

## 아직 남은 작업

이번 작업은 스킬 구조 변경 1차입니다.

아직 전투 공식 전체를 완전히 데이터 기반으로 바꾸지는 않았습니다.
현재 `combat-system.js`에는 기존 스킬 공식이 남아 있습니다.

다음 단계에서 더 분리하려면 아래 작업이 필요합니다.

```txt
스킬 발동률을 skillMasterData 기준으로 계산
스킬 데미지 계수를 skillMasterData 기준으로 계산
버프형/딜형/진각성형 스킬 처리 공통화
FastAPI 응답 형태에 맞는 스킬 발동 결과 객체 설계
```

## 캐릭터 추가 시 예상 방식

나중에 캐릭터를 추가할 때는 아래 순서로 확장합니다.

```txt
1. characterMasterData에 새 캐릭터 추가
2. skillMasterData에 새 캐릭터 스킬 추가
3. characterMasterData[캐릭터ID].skillIds에 스킬 연결
4. 관리자 페이지에서 캐릭터/스킬을 DB로 관리하도록 전환
```

---

## 원본: `docs/archive/stage-notes/UI_RESULT_SEPARATION_STAGE1.md`

# 4순위 1차: 시스템 함수와 UI 분리 준비

## 목적

이번 단계는 `combat-system.js`, `item-system.js`를 바로 FastAPI 코드처럼 완전히 분리하는 작업이 아닙니다.
기존 게임 동작을 유지하면서, 핵심 함수가 나중에 서버 API 응답으로 바뀔 수 있도록 **결과 객체(Action Result)** 를 먼저 도입하는 단계입니다.

## 추가 파일

```txt
src/systems/action-result-system.js
```

역할:

- 전투/강화 같은 게임 액션의 결과 객체 생성
- 로그, 데미지 텍스트, 강화 결과창, UI 갱신 요청을 결과 객체에 담기
- 결과 객체를 현재 프론트 UI에 반영하는 `applyActionResultUi()` 제공

## 결과 객체 기본 형태

```js
{
  ok: true,
  type: "item.enhance",
  payload: {},
  logs: [],
  effects: [],
  ui: {},
  data: {},
  createdAt: 1234567890
}
```

이 구조는 나중에 FastAPI 응답 형태로 바꾸기 쉽습니다.

## combat-system.js 변경

### 적용 범위

```txt
playerAttack()
```

변경 내용:

- 공격 결과 객체 생성: `createCombatAttackResult()`
- 스킬 발동 내역 저장: `data.skillHits`
- 총 피해량 저장: `data.totalDamage`
- 대상/남은 HP/처치 여부 저장: `data.target`, `data.remainingHp`, `data.killed`
- 스킬 데미지 텍스트는 즉시 출력하지 않고 `effects`에 먼저 담은 뒤 `applyActionResultUi()`에서 처리

아직 남은 UI 의존:

- `killEnemy()` 내부 드랍/로그/UI 호출
- 일부 버프 처리 중 `updateFullUI()` 호출
- `updateCombatUI()` 호출

이 부분은 4순위 2차에서 더 줄이는 것이 안전합니다.

## item-system.js 변경

### 적용 범위

```txt
actionReinforce(times)
```

변경 내용:

- 강화 결과 객체 생성: `createGameActionResult("item.enhance")`
- 강화 성공/실패/중단 사유를 `data`에 저장
- 로그는 `logs`에 저장
- 강화 결과창 표시 정보는 `ui.enhanceResult`에 저장
- UI 갱신 요청은 `ui.updateFullUI`, `ui.refreshActionPanelStats`에 저장
- 마지막에 `applyActionResultUi()`로 현재 화면에 반영

## 이번 단계에서 일부러 하지 않은 것

아래 작업은 한 번에 처리하면 회귀 위험이 커서 미뤘습니다.

```txt
killEnemy() 완전 결과 객체화
드랍 판정 결과 객체화
장착/해제 결과 객체화
스킬강화권 사용 결과 객체화
전투 공식 전체 데이터화
```

## 다음 4순위 2차 후보

```txt
1. killEnemy() 결과 객체화
2. 드랍 결과를 rewards 배열로 모으기
3. actionEquipDirect() / actionUnequipDirect() 결과 객체화
4. 스킬강화권 사용 결과 객체화
5. combat-system.js에서 updateFullUI() 직접 호출 줄이기
```

## 확인 포인트

브라우저에서 아래를 확인합니다.

```txt
- 자동 전투가 정상 작동하는지
- W/R/T/F/D/SQ/SW/진각성 데미지 텍스트가 보이는지
- 보스 처치/드랍이 기존처럼 동작하는지
- 일반 장비 강화가 정상 작동하는지
- 탈리스만/휘장 강화가 정상 작동하는지
- 강화 결과창 로그가 기존처럼 보이는지
```
