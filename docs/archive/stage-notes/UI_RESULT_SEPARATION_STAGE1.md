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
