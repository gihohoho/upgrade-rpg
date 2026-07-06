# 백엔드 분리 준비 2차 계획서

## 목표

현재 게임 코드를 FastAPI/PostgreSQL로 옮기기 전에, 프론트 코드 내부를 아래 기준으로 정리합니다.

```txt
서버에 저장할 데이터
화면에서만 필요한 데이터
실행 중 임시 데이터
순수 마스터 데이터
게임 판정 로직
화면 표시 로직
```

이 구분이 되어야 나중에 백엔드와 DB로 옮길 때 게임이 덜 깨집니다.

---

## 완료된 작업

### 1순위. 상태 분리

`src/state/game-state.js`에 아래 구조를 추가했습니다.

```js
gameState.server
gameState.client
gameState.runtime
```

의미:

```txt
gameState.server  = FastAPI/PostgreSQL 저장 대상
gameState.client  = 화면에서만 필요한 UI 상태
gameState.runtime = 실행 중 임시 상태
```

---

### 2순위. bosses.js 역할 분리

기존 `bosses.js`에서 여러 역할을 분리했습니다.

```txt
src/data/bosses.js
src/data/boss-factories.js
src/data/boss-bootstrap.js
src/utils/icon-utils.js
src/rules/abyss-fragment-rules.js
src/rules/boss-display-rules.js
src/rules/boss-drop-rules.js
```

아직 아이템 원본/드랍 테이블 완전 분리는 남아 있습니다.

---

### 3순위. 캐릭터별 스킬 구조 준비

`src/data/skills.js`를 추가해서 현재 스킬/스킬강화권/캐릭터 정보를 중앙화했습니다.

현재 구조:

```txt
characterMasterData
skillMasterData
skillBookMasterData
```

유저 상태 구조:

```txt
player.currentCharacterId
player.ownedCharacterIds
player.userCharacters
player.skills
```

기존 코드 호환을 위해 `player.skills`는 유지하되, 실제 기준 구조는 아래로 잡았습니다.

```txt
player.userCharacters[player.currentCharacterId].skills
```

---

## 완료된 작업: 4순위 시스템 함수와 UI 분리 1차

### 현재 문제

`combat-system.js`, `item-system.js`는 아직 게임 계산과 화면 갱신을 동시에 처리합니다.

예:

```txt
전투 계산
드랍 판정
아이템 지급
로그 출력
데미지 텍스트 표시
renderUI 호출
```

이것이 한 함수 안에 섞여 있습니다.

### 목표

계산 함수는 결과만 반환하고, UI는 그 결과를 받아서 표시하도록 나눕니다.

이번 1차에서는 전체 함수를 완전히 분리하지 않고, 전투/강화에 먼저 `Action Result` 구조를 도입했습니다.

예상 형태:

```js
{
  ok: true,
  damage: 12345,
  skillProcs: [],
  killed: true,
  rewards: [],
  logs: []
}
```

### 1차 적용 대상

```txt
playerAttack()
actionReinforce(times)
```

추가 파일:

```txt
src/systems/action-result-system.js
```

다음 4순위 2차 대상:

```txt
killEnemy()
actionEquipDirect()
actionUnequipDirect()
스킬강화권 사용 로직
```

---

## CSS 관련 참고

CSS 점검 결과는 아래 문서에 정리했습니다.

```txt
docs/CSS_AUDIT.md
```

현재는 바로 SCSS로 바꾸기보다 CSS 유지 후, Vue/Vite 전환 시점에 SCSS 도입을 추천합니다.


## 완료된 작업: 4순위 시스템 함수와 UI 분리 2차

처치/드랍/보상 흐름에 `combat.kill` 결과 객체를 추가했습니다.

- 보스 처치 드랍 결과를 `data.drops`에 기록
- 드랍 로그/드랍 텍스트 표시 요청을 `logs`/`effects`에 기록
- 필드 처치 골드/성장 보상을 `data.rewards`에 기록
- 특수보스 쿨타임/전투 종료 전환 정보를 결과 객체에 기록

다음 후속 후보는 장착/해제, 스킬강화권 사용, 보스 소환 결과 객체화입니다.


## 4순위 3차 완료 메모

- 장착/해제, 스킬강화권 사용, 보스 소환 결과 객체화를 완료했습니다.
- 핵심 플레이 흐름의 Action Result 기반이 넓어졌으므로 다음 큰 단계는 5순위 API 응답 형태 확정입니다.


---

## 5순위 완료 메모: API 응답 형태 확정

FastAPI 구현 전에 프론트와 백엔드가 맞춰야 할 응답 형태를 확정했습니다.

추가 파일:

```txt
docs/API_RESPONSE_CONTRACT.md
src/api/api-response-contract.js
tools/smoke_api_response_contract.js
```

확정한 기준:

```txt
ok / responseVersion / type / requestId / serverTime
payload / data / logs / effects / ui / statePatch / meta / error
```

이번 단계는 실제 화면 동작을 바꾸지 않는 계약 작업이므로 브라우저 확인 항목은 없습니다.

다음 큰 단계 후보:

```txt
1. 보관함/휴지통/우편 이동 결과 객체화
2. FastAPI 프로젝트 뼈대 생성
3. PostgreSQL 테이블 초안 작성
4. 마스터 데이터 JSON/Seed 추출
```
