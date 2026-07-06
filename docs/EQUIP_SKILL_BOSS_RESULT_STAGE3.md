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
