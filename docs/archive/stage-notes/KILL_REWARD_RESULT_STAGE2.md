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
