# 백엔드 분리 준비 2차 정리 - 1순위 완료 기록

## 적용 범위

이번 수정은 1순위인 `game-state.js` 상태 분리를 적용한 버전입니다.

기존 전역 변수 이름은 유지했습니다.

- `player`
- `currentZoneIndex`
- `currentZoneType`
- `fieldEnemyHp`
- `fieldRespawnEndAt`
- `selectedSlot`
- `currentBoss`
- `currentBossHp`
- `currentEnemy`
- 기타 전투/패널 상태

따라서 기존 파일들이 바로 깨지지 않도록 호환성을 유지했습니다.

## 새 구조

실제 상태는 `window.gameState` 아래 3개 영역으로 나뉩니다.

```js
gameState.server
```

서버/DB에 저장해야 하는 상태입니다.

- `player`
- `progress.currentZoneIndex`
- `progress.currentZoneType`
- `progress.fieldEnemyHp`
- `progress.fieldRespawnEndAt`

```js
gameState.client
```

브라우저 화면에서만 필요한 상태입니다.

- `selectedSlot`
- 인벤토리/보스/특수보스/필드 패널 열림 상태

```js
gameState.runtime
```

실행 중에만 필요한 임시 상태입니다.

- 현재 전투 중인 보스
- 현재 보스 HP
- 현재 필드 몬스터 HP
- 자동공격 타이머
- 버프 상태
- 자동보스/특수보스 상태

## 추가된 헬퍼 함수

```js
ensureGameStateShape()
```

상태 구조가 깨졌거나 저장 데이터가 오래된 형태일 때 기본값을 보정합니다.

```js
getServerSavePayload(saveVersion)
```

localStorage 또는 나중에 FastAPI 저장 API로 보낼 서버 저장용 데이터만 추출합니다.

```js
applyServerSavePayload(data)
```

기존 저장 데이터를 `gameState.server` 구조에 주입합니다.

```js
resetRuntimeState()
```

전투/버프/타이머 같은 실행 중 임시 상태를 초기화합니다.

```js
getStateSplitDebugSnapshot()
```

개발 중 상태 분리를 확인하는 디버그용 함수입니다.

## main.js 변경점

`saveGame()`은 이제 직접 `player`, `currentZoneIndex` 등을 묶지 않고, 가능하면 `getServerSavePayload()`를 사용합니다.

`loadGame()`은 가능하면 `applyServerSavePayload()`를 사용해서 저장 데이터를 새 구조에 넣습니다.

## 아직 남은 2~5순위

1순위는 완료했지만 아래 작업은 아직 실제 코드 수정 전입니다.

1. `bosses.js` 순수 데이터화
   - 보스 데이터 / 아이템 원본 / 드랍 규칙 / 아이콘 유틸 / 최초 보너스 규칙 분리

2. 캐릭터별 스킬 구조 변경
   - 현재 `player.skills`는 유지
   - 다음 단계에서 `characters`, `skills`, `characterSkills`, `userCharacterSkills` 형태로 확장 예정

3. 시스템 함수와 UI 분리
   - `combat-system.js`, `item-system.js` 내부의 `renderUI()`, `updateFullUI()`, `document.getElementById()` 호출 줄이기
   - 계산 함수는 결과 객체만 반환하도록 변경 예정

4. API 응답 형태 확정
   - 공격 결과
   - 보스 처치 결과
   - 아이템 강화 결과
   - 스킬 강화권 사용 결과
   - 우편 수령 결과

## 다음 추천 작업

다음 작업은 2순위인 `bosses.js` 분리입니다.

추천 분리 파일:

```txt
src/data/bosses.js
src/data/items.js
src/data/drop-rules.js
src/utils/icon-utils.js
src/rules/boss-rules.js
```

이 작업이 끝나면 PostgreSQL의 `bosses`, `item_templates`, `drop_tables`, `drop_table_items`로 옮기기 쉬워집니다.
