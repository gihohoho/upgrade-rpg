# 프로젝트 기반 작업 역사

> 완료된 단계별 메모를 검색 가능한 한 파일로 통합한 읽기 전용 역사입니다.
> 현재 작업 판단에는 `docs/current/`와 루트 `NEXT_CHAT_HANDOFF.md`를 사용하세요.
> 원본 파일은 Git commit `270d57bd234ede18cee7168f4b5da36b1a08df18` 이전 이력에서 복원할 수 있습니다.

## 통합된 원본

- `docs/archive/stage-notes/BACKEND_SPLIT_CHECKLIST.md`
- `docs/archive/stage-notes/BACKEND_SPLIT_STAGE2_PLAN.md`
- `docs/archive/stage-notes/CODE_MAP.md`
- `docs/archive/stage-notes/DECISION_LOG.md`
- `docs/archive/stage-notes/FRONTEND_MASTER_DATA_BRIDGE.md`
- `docs/archive/stage-notes/HANDOFF_CLEANUP_NOTES_V246.md`
- `docs/archive/stage-notes/LOCAL_DB_PORT_POLICY.md`
- `docs/archive/stage-notes/NEXT_STEP_V240_REQUEST_PAYLOAD_VALIDATION.md`
- `docs/archive/stage-notes/ROOT_CHANGELOG_THROUGH_V320.md`

---

## 원본: `docs/archive/stage-notes/BACKEND_SPLIT_CHECKLIST.md`

# 백엔드 분리 준비 체크리스트

## 1순위. 상태 분리

상태: 완료

완료된 내용:

- `gameState.server` 추가
- `gameState.client` 추가
- `gameState.runtime` 추가
- 기존 전역 변수 호환 유지
- 저장/불러오기용 헬퍼 추가

확인할 것:

- 게임 시작 가능
- 저장/불러오기 가능
- 필드 이동 가능
- 보스 소환 가능
- 아이템 장착/해제 가능
- 강화 가능

---

## 2순위. bosses.js 역할 분리

상태: 1차 완료

완료된 내용:

- 아이콘 유틸 분리: `src/utils/icon-utils.js`
- 고티어 보스 생성 공식 분리: `src/data/boss-factories.js`
- 보스 원본 데이터 파일 축소: `src/data/bosses.js`
- 심연의 편린 특수 옵션 규칙 분리: `src/rules/abyss-fragment-rules.js`
- 보스 표시 후처리 분리: `src/rules/boss-display-rules.js`
- 드랍률 보정/최초 보너스 규칙 분리: `src/rules/boss-drop-rules.js`
- 후처리 실행 파일 추가: `src/data/boss-bootstrap.js`

남은 작업:

- [ ] 아이템 원본을 `items.js` 또는 DB seed 형태로 완전 분리
- [ ] 드랍 테이블을 `drop-rules.js` 또는 DB seed 형태로 완전 분리
- [ ] `boss-drop-rules.js`의 전역 UI/player 의존 제거

---

## 3순위. 캐릭터별 스킬 구조 준비

상태: 1차 완료

완료된 내용:

- `src/data/skills.js` 추가
- 현재 기본 캐릭터 `weapon_master` 등록
- 현재 스킬 8개를 스킬 마스터 데이터로 분리
- Q/SQ, W/SW 각성 정보를 스킬 데이터 내부로 이동
- 스킬강화권 매핑을 `skillBookMasterData`로 분리
- `player.currentCharacterId`, `player.ownedCharacterIds`, `player.userCharacters` 구조 추가
- 기존 코드 호환용 `player.skills` 유지
- `renderSkills()`가 중앙 스킬 데이터 기반으로 스킬 UI를 그리도록 변경
- `item-system.js`의 스킬강화권 사용 로직이 중앙 스킬 데이터/현재 캐릭터 스킬을 참조하도록 변경
- `combat-system.js`가 `player.skills` 대신 현재 캐릭터 스킬 헬퍼를 우선 사용하도록 변경

남은 작업:

- [ ] 전투 공식 전체를 `skillMasterData` 기반으로 완전 데이터화
- [ ] 스킬 타입별 처리기 분리: 패시브/확률딜/버프/진각성
- [ ] 관리자 페이지에서 스킬 발동률/계수/쿨타임 수정 가능하게 DB화

---

## 4순위. 시스템 함수와 UI 분리

상태: 3차 완료

완료된 내용:

- `src/systems/action-result-system.js` 추가
- `playerAttack()`이 공격 결과 객체를 생성하도록 변경
- 스킬 발동 내역/총 피해량/대상/처치 여부를 결과 객체에 저장
- 스킬 데미지 텍스트를 즉시 출력하지 않고 결과 객체의 `effects`로 전달
- `actionReinforce(times)`가 강화 결과 객체를 생성하도록 변경
- 강화 로그/강화 결과창/UI 갱신 요청을 결과 객체로 모은 뒤 `applyActionResultUi()`에서 처리
- 보스/필드 처치, 드랍, 골드/성장 보상을 `combat.kill` 결과 객체로 1차 정리

남은 작업:

- [x] `killEnemy()`의 보스 처치/드랍/필드 보상 로직 결과 객체화
- [x] `actionEquipDirect()` / `actionUnequipDirect()` 결과 객체화
- [x] 스킬강화권 사용 결과 객체화
- [x] 보스 소환 결과 객체화
- [ ] 보관함/휴지통/우편 이동 결과 객체화
- [ ] 시스템 함수 내부의 직접 UI 호출 추가 축소

완료 기준:

- 핵심 함수가 `renderUI()`에 직접 의존하지 않는다.
- 핵심 함수가 `document.getElementById()`에 직접 의존하지 않는다.
- 결과 객체만으로 UI를 다시 그릴 수 있다.

---

### 4순위 2차 완료

- `killEnemy()` 중심으로 처치/드랍/보상 결과를 객체화했습니다.

### 4순위 3차 완료

- 장착/해제, 스킬강화권 사용, 보스 소환 결과를 객체화했습니다.
- 남은 4순위 후속 후보: 보관함/휴지통/우편 이동, 보스 제거, 토글 명령어 결과 객체화.

## 5순위. API 응답 형태 확정

상태: 완료

완료된 내용:

- `docs/contracts/API_RESPONSE_CONTRACT.md` 추가
- `src/api/api-response-contract.js` 추가
- `src/api/API_PLAN.md`를 확정 응답 형태 기준으로 갱신
- 저장/불러오기 응답 형태 정리
- 마스터 데이터 응답 형태 정리
- 공격/처치/보스 소환 응답 형태 정리
- 장착/해제/강화 응답 형태 정리
- 스킬강화권 사용 응답 형태 정리
- 관리자 변경 응답 형태 정리
- 실패 응답과 공통 에러 코드 정리
- `tools/smoke/frontend/smoke_api_response_contract.js` 추가

완료 기준:

- FastAPI 구현 전에 프론트가 예상 응답 형태를 알 수 있다.
- 관리자 페이지와 유저 게임 화면이 같은 마스터 데이터를 사용할 수 있다.
- 현재 Action Result 구조와 FastAPI 응답 형태의 연결 기준이 있다.

브라우저 확인:

- 이번 5순위는 문서/계약/미사용 헬퍼 추가 작업이라 브라우저에서 따로 확인할 항목은 없습니다.



## v075 추가 완료 항목

```txt
[x] 관리자 페이지 요구사항 V1 문서화
[x] PostgreSQL DB 설계 초안 작성
[x] FastAPI backend/ 프로젝트 뼈대 생성
[x] 공통 API 응답 헬퍼 작성
[x] SQLAlchemy 모델 초안 작성
[x] API 라우터 stub 작성
[x] backend 구조 smoke 검사 추가
```


## v078 진행 상태

- [x] seed JSON을 PostgreSQL에 넣기 위한 import 스크립트 추가
- [x] 로컬 DB reset/create/seed/verify 명령어 정리
- [x] seed import 문서 추가
- [x] 큰 숫자 HP/골드 저장을 위한 DB 타입 보정

다음 단계:

- [ ] `/game/master-data` API가 DB에서 실제 마스터 데이터를 읽도록 구현

---

## 원본: `docs/archive/stage-notes/BACKEND_SPLIT_STAGE2_PLAN.md`

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
docs/archive/stage-notes/CSS_AUDIT.md
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
docs/contracts/API_RESPONSE_CONTRACT.md
src/api/api-response-contract.js
tools/smoke/frontend/smoke_api_response_contract.js
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

---

## 원본: `docs/archive/stage-notes/CODE_MAP.md`

# 코드 탐색 지도

이 문서는 ZIP을 받은 사람이 빠르게 파일 역할과 주요 함수를 찾을 수 있도록 만든 탐색용 문서입니다.

## 전체 흐름

```txt
index.html
→ src/state/game-state.js
→ src/data/bosses.js, src/data/zones.js
→ src/systems/stat-system.js
→ src/ui/render-ui.js
→ src/systems/item-system.js
→ src/systems/combat-system.js
→ src/app/main.js
```

현재는 `import/export`가 아니라 HTML script 순서에 의존합니다. script 순서를 바꾸면 게임이 깨질 수 있습니다.

---

## `src/app/main.js`

게임 시작/저장/불러오기/테스트 기능/우편/기록관 처리 파일입니다.

백엔드 분리 관점:

- `saveGame()` / `loadGame()`이 FastAPI 저장/불러오기 연결의 첫 진입점입니다.
- 테스트 기능은 나중에 관리자/개발자 기능으로 분리해야 합니다.

주요 함수:

- `toggleTestCostMode()` - line 6
- `applyToggleButtonVisual()` - line 26
- `refreshOnOffButtonVisuals()` - line 33
- `ensurePlayerRecords()` - line 46
- `cloneRecordObject()` - line 62
- `refreshRecordSnapshot()` - line 66
- `getRecordSnapshotForView()` - line 86
- `forceRefreshRecordSnapshot()` - line 90
- `addGold()` - line 94
- `getRecordItemBaseName()` - line 101
- `getRecordItemLevel()` - line 109
- `getRecordItemKeys()` - line 113
- `advanceItemDryStreak()` - line 122
- `recordItemAcquired()` - line 129
- `recordMonsterKill()` - line 150
- `recordBossKill()` - line 157
- `recordEnhanceFailure()` - line 164
- `tickPlayTimeRecord()` - line 170
- `startPlayTimeRecordTimer()` - line 178
- `migrateSaveData()` - line 186
- `saveGame()` - line 225
- `manualSaveGame()` - line 242
- `openSponsorPage()` - line 255
- `ensureMailbox()` - line 259
- `sendMail()` - line 263
- `getOneHourGoldAmount()` - line 274
- `sendOneHourGoldMail()` - line 284
- `createMailTalismanItem()` - line 294
- `sendTalismanMail()` - line 308
- `claimMail()` - line 318
- `claimAllMail()` - line 360
- `loadGame()` - line 416
- `resetGame()` - line 445
- `closeResetModal()` - line 450
- `confirmResetGame()` - line 455
- `buildStatHtml()` - line 520
- `combinePercentIncForTooltip()` - line 535
- `getStatTooltipHTML()` - line 539
- `giveBeginnerItem()` - line 694
- `updateCodexRevealButton()` - line 721
- `toggleCodexRevealMode()` - line 729
- `toggleTestBuffMode()` - line 739
- `moveToRecentField()` - line 758
- `addPureAtk()` - line 771
- `setBaseAtkAspdMax()` - line 781
- `getDefaultSkillState()` - line 788
- `resetSkillsOnly()` - line 801
- `updateSpecialBossNoCooldownButton()` - line 811
- `applySpecialBossNoCooldownMode()` - line 819
- `toggleSpecialBossNoCooldownMode()` - line 829
- `clearSpecialBossCooldowns()` - line 836
- `isTestDropForMode()` - line 844
- `getTestBossPool()` - line 848
- `isTestItemModalOpened()` - line 855
- `openTestItemModal()` - line 860
- `openTestSpecialItemModal()` - line 870
- `openTestModalBase()` - line 880
- `closeTestItemModal()` - line 893
- `renderTestBossList()` - line 899
- `renderTestItemList()` - line 949

---

## `src/data/bosses.js`

보스/특수보스/드랍/아이템 생성 규칙이 섞여 있는 데이터 파일입니다. 다음 분리 대상입니다.

백엔드 분리 관점:

- 다음 작업에서 가장 먼저 나눌 파일입니다.
- 보스 데이터, 아이템 원본, 드랍 규칙, 아이콘 유틸, 게임 규칙을 분리해야 합니다.

주요 함수:

- `bossRoundB()` - line 10
- `bossExpBetween()` - line 14
- `bossHighBaseAtk()` - line 25
- `bossHighBaseSmult()` - line 30
- `bossHighBaseCrit()` - line 35
- `bossHighBaseAtkInc()` - line 40
- `bossHighBaseNdmg()` - line 45
- `bossHighBaseCost()` - line 49
- `bossHighBaseIlv()` - line 53
- `makeHighNormalDrop()` - line 57
- `makeHighTalisman()` - line 96
- `makeHighEmblem()` - line 110
- `makeHighBoss()` - line 123
- `iconTextUrl()` - line 2076
- `getSpecialEquipIconInfo()` - line 2091
- `getSpecialEquipIconUrl()` - line 2101
- `getSkillBookIconText()` - line 2107
- `getAbyssFragmentSpecialStats()` - line 2122
- `applyAbyssFragmentStats()` - line 2152
- `applyGeneratedThumbnails()` - line 2162
- `getNormalBossSkillDropRate()` - line 2217
- `isFirstEquipSkillGuaranteeBoss()` - line 2226
- `shouldGrantFirstEquipSkillBook()` - line 2230
- `markFirstEquipSkillBookGranted()` - line 2238
- `grantFirstEquipSkillBookIfNeeded()` - line 2245
- `stripBossTitleShortcuts()` - line 2338

---

## `src/data/zones.js`

필드존 데이터 파일입니다. 비교적 순수 데이터에 가까운 편입니다.

---

## `src/state/game-state.js`

게임 상태 정의. 백엔드 분리 준비 1순위가 적용된 핵심 파일입니다.

백엔드 분리 관점:

- `gameState.server`는 DB 저장 후보입니다.
- `gameState.client`는 프론트 화면 상태입니다.
- `gameState.runtime`은 전투 중 임시 상태입니다.

주요 함수:

- `createDefaultPlayerState()` - line 24
- `createDefaultServerState()` - line 77
- `createDefaultClientState()` - line 89
- `createDefaultRuntimeState()` - line 101
- `bindStateAlias()` - line 134
- `bindNestedStateAlias()` - line 146
- `ensurePlayerStateShape()` - line 187
- `ensureProgressStateShape()` - line 231
- `ensureGameStateShape()` - line 241
- `getServerSavePayload()` - line 249
- `applyServerSavePayload()` - line 261
- `resetRuntimeState()` - line 272
- `getStateSplitDebugSnapshot()` - line 279

---

## `src/systems/combat-system.js`

필드 전투/보스 전투/스킬 발동/처치/드랍 처리 파일입니다.

백엔드 분리 관점:

- 게임 결과에 영향을 주는 계산은 최종적으로 FastAPI로 이동할 후보입니다.
- 다음 단계에서는 UI 호출을 줄이고 결과 객체를 반환하도록 바꾸는 것이 좋습니다.

주요 함수:

- `normalizeFieldState()` - line 2
- `getFieldEnemyHp()` - line 7
- `setFieldEnemyHp()` - line 25
- `scheduleFieldRespawn()` - line 31
- `syncCurrentFieldHp()` - line 52
- `enterTown()` - line 57
- `enterBossZone()` - line 66
- `startAutoAttack()` - line 82
- `rollSkillProc()` - line 89
- `playerAttack()` - line 94
- `killEnemy()` - line 276
- `changeZone()` - line 458
- `showItemDropText()` - line 474
- `showDamageText()` - line 489

---


## `src/systems/action-result-system.js`

역할:

- 백엔드 분리 준비용 결과 객체 유틸
- 전투/강화 결과를 API 응답에 가까운 형태로 모음
- 현재 프론트 UI에는 `applyActionResultUi()`로 반영

주요 함수:

```txt
createGameActionResult()
failGameActionResult()
addResultLog()
addResultEffect()
requestUiRefresh()
setEnhanceResultView()
applyActionResultUi()
createCombatAttackResult()
addCombatSkillHit()
queueDamageText()
```

## `src/systems/item-system.js`

장착/해제/강화/판매/보관함/휴지통/스킬강화권 사용 처리 파일입니다.

백엔드 분리 관점:

- 게임 결과에 영향을 주는 계산은 최종적으로 FastAPI로 이동할 후보입니다.
- 다음 단계에서는 UI 호출을 줄이고 결과 객체를 반환하도록 바꾸는 것이 좋습니다.

주요 함수:

- `getBaseStackName()` - line 1
- `isEmblemStackItem()` - line 5
- `isTalismanStackItem()` - line 9
- `getTalismanSlotIndexByName()` - line 13
- `getSpecialStackSlotIndex()` - line 17
- `getSpecialStackIconText()` - line 24
- `ensureSpecialStackIdentity()` - line 34
- `normalizeSpecialStackItem()` - line 48
- `normalizeSpecialStackArray()` - line 57
- `normalizePlayerSpecialStackItems()` - line 62
- `isZeroLevelStackableItem()` - line 78
- `prepareStackableItem()` - line 85
- `findStackableItem()` - line 94
- `addStackableItemToInventory()` - line 104
- `mergeStackableIntoArray()` - line 119
- `isBeginnerLiberationStaff()` - line 131
- `getNormalEquipAllowedSlots()` - line 136
- `getNormalEquipTargetIndex()` - line 148
- `actionEquipDirect()` - line 179
- `actionUnequipDirect()` - line 277
- `actionEquipToggle()` - line 302
- `actionUseSelected()` - line 307
- `getSelectedItemPack()` - line 314
- `getZeroLevelMaterialCount()` - line 322
- `consumeZeroLevelMaterials()` - line 332
- `renderEnhanceResultLog()` - line 351
- `actionReinforce()` - line 362
- `actionSell()` - line 537
- `actionBulkSell()` - line 589
- `bulkMoveInventoryToTrash()` - line 593
- `closeBulkTrashModal()` - line 602
- `confirmBulkMoveInventoryToTrash()` - line 607
- `actionMoveStorage()` - line 652
- `emptyTrash()` - line 711
- `closeTrashEmptyModal()` - line 720
- `confirmEmptyTrash()` - line 725

---

## `src/systems/stat-system.js`

공격력/스탯/강화 확률/장비 능력치 계산 파일입니다.

백엔드 분리 관점:

- 게임 결과에 영향을 주는 계산은 최종적으로 FastAPI로 이동할 후보입니다.
- 다음 단계에서는 UI 호출을 줄이고 결과 객체를 반환하도록 바꾸는 것이 좋습니다.

주요 함수:

- `getClampedFieldAttackSpeed()` - line 17
- `getBaseAttackByAttackSpeed()` - line 24
- `getRandomInt()` - line 30
- `formatCompactNumber()` - line 34
- `formatNumber()` - line 63
- `getCodexCompletionBonusPercent()` - line 70
- `scaleSpecialArrayToLast()` - line 142
- `scaleSpecialIntegerArrayToLast()` - line 152
- `clampEnhanceLevel()` - line 166
- `isAbyssFragmentSpecialEquip()` - line 173
- `isTranscendAbyssFragmentSpecialEquip()` - line 178
- `isEnhanceableSpecialEquip()` - line 183
- `getSpecialEquipEnhanceCost()` - line 187
- `formatNumberDecimal()` - line 194
- `calcSpecialEquipStats()` - line 202
- `clampLevel()` - line 343
- `roundToRawB()` - line 350
- `expBetween()` - line 354
- `lagrangeInterpolate()` - line 361
- `highTierBaseAtk()` - line 376
- `highTierAtk20()` - line 384
- `highTierAtk11()` - line 402
- `highTierBaseSmult()` - line 407
- `highTierSmult20()` - line 415
- `highTierBaseCrit()` - line 428
- `highTierCrit20()` - line 437
- `highTierBaseAtkInc()` - line 445
- `highTierBaseNdmg()` - line 453
- `highTierBaseSdmg()` - line 460
- `highTierBaseAllDmg()` - line 467
- `getEquipGroup()` - line 474
- `getHighTierBaseByGroup()` - line 484
- `calcItemStats()` - line 493
- `getEnhanceCost()` - line 635
- `getBaseEnhanceProb()` - line 642
- `getEnhanceProb()` - line 653
- `addPercentMultiplicative()` - line 660
- `getTotals()` - line 664

---

## `src/ui/render-ui.js`

화면 표시/툴팁/패널/도감/랭킹/보스 UI 렌더링 파일입니다.

백엔드 분리 관점:

- 이 파일은 프론트에 남는 영역입니다.
- 나중에 Vue 전환 시 컴포넌트로 나눌 대상입니다.

주요 함수:

- `getCleanStackName()` - line 85
- `isEmblemLike()` - line 89
- `isTalismanLike()` - line 93
- `getDisplayNameWithLevel()` - line 97
- `isDisplayStackable()` - line 105
- `isTalismanBLike()` - line 109
- `isTalismanALike()` - line 114
- `getTalismanCategoryInfo()` - line 119
- `getSlotBadgeHtml()` - line 149
- `toggleStorage()` - line 166
- `toggleTrash()` - line 178
- `closeAllGameplayModals()` - line 190
- `toggleMailbox()` - line 218
- `toggleInv()` - line 230
- `formatPercentFixed1()` - line 236
- `formatPercentSmart()` - line 241
- `buildSpecialEquipStatsHtml()` - line 256
- `getGoldRewardDisplay()` - line 295
- `getEnhanceProbDisplay()` - line 304
- `getUniqueTooltipHTML()` - line 317
- `addLog()` - line 332
- `getSkillBookInfo()` - line 342
- `buildSkillBookTooltipHtml()` - line 359
- `buildSkillBookActionHtml()` - line 380
- `showItemTooltip()` - line 393
- `hideTooltip()` - line 465
- `closeActionPanel()` - line 469
- `refreshActionPanelStats()` - line 476
- `selectItem()` - line 754
- `getMailboxRewardText()` - line 778
- `renderMailbox()` - line 790
- `renderUI()` - line 816
- `updateCombatUI()` - line 947
- `updateGoldUI()` - line 971
- `formatRecordDuration()` - line 976
- `formatRecordDurationNoSeconds()` - line 989
- `formatRecordGoldNumber()` - line 998
- `formatRecordCountNumber()` - line 1003
- `formatRecordSnapshotTime()` - line 1007
- `getRecordTopEntry()` - line 1014
- `getCodexBaseName()` - line 1028
- `getCodexCategory()` - line 1035
- `getCodexItems()` - line 1044
- `getCollectionStats()` - line 1092
- `renderTownRecordModal()` - line 1103
- `renderTownCodexModal()` - line 1140
- `setCodexViewFilter()` - line 1201
- `getEquippedItemLevelTotal()` - line 1206
- `getCurrentRankingHourKey()` - line 1217
- `refreshRankingSnapshot()` - line 1223
- `formatRankingRefreshTime()` - line 1238
- `renderTownRankingModal()` - line 1245
- `openTownRecordModal()` - line 1272
- `openTownCodexModal()` - line 1278
- `openTownRankingModal()` - line 1284
- `closeTownModal()` - line 1290
- `renderTownHub()` - line 1295
- `updateFullUI()` - line 1308
- `getBossByIdForReturn()` - line 1406
- `captureSpecialBossReturnState()` - line 1411
- `restoreSpecialBossReturnState()` - line 1426
- `updateAutoSpecialBossButton()` - line 1495
- `openAutoSpecialBossModal()` - line 1503
- `closeAutoSpecialBossModal()` - line 1510
- `toggleAutoSpecialBoss()` - line 1515
- `renderAutoSpecialBossList()` - line 1526
- `startAutoSpecialBoss()` - line 1544
- `tryStartAutoSpecialBoss()` - line 1558
- `toggleAutoBoss()` - line 1594
- `removeBoss()` - line 1607
- `toggleEquipDrop()` - line 1629
- `getCanonicalBossForSummon()` - line 1642
- `summonBoss()` - line 1648
- `toggleBossPanel()` - line 1721
- `toggleSpecialBossPanel()` - line 1736
- `toggleFieldZone()` - line 1751
- `renderBossZone()` - line 1766
- `renderSpecialBossZone()` - line 1810
- `renderFieldZone()` - line 1856
- `formatSkillProcRateText()` - line 1948
- `buildSkillProcChanceHtml()` - line 1953
- `renderSkills()` - line 1961

---

## 보스/드랍 데이터 분리 지도 v0.67

| 파일 | 현재 역할 | 다음 이전 대상 |
| --- | --- | --- |
| `src/utils/icon-utils.js` | 아이콘 URL 생성 | Vue/프론트 유틸 유지 가능 |
| `src/data/boss-factories.js` | 고티어 보스/장비 생성 공식 | seed 생성 스크립트 또는 DB 기본값 |
| `src/data/bosses.js` | 일반/특수 보스 원본 데이터 | PostgreSQL `bosses`, `drop_tables`, `drop_table_items` |
| `src/rules/abyss-fragment-rules.js` | 심연의 편린 특수 옵션 부여 | PostgreSQL `item_options` 또는 FastAPI item service |
| `src/rules/boss-display-rules.js` | 썸네일/타이틀 등 표시 후처리 | Vue 표시 로직 |
| `src/rules/boss-drop-rules.js` | 드랍률 보정, 최초 장비 보너스 | FastAPI drop/battle service |
| `src/data/boss-bootstrap.js` | 보스 데이터 후처리 실행 순서 | 앱 초기화 또는 seed 후처리 |


---

## v0.68 추가: `src/data/skills.js`

캐릭터/스킬/스킬강화권 마스터 데이터를 모아둔 파일입니다.

백엔드 분리 관점:

- 나중에 PostgreSQL의 `characters`, `skills`, `character_skills`, `skill_books` 테이블로 옮길 후보입니다.
- 캐릭터 추가 시 가장 먼저 수정하거나 DB화해야 할 파일입니다.

주요 데이터:

- `characterMasterData` - 캐릭터 목록과 캐릭터별 스킬 연결
- `skillMasterData` - 스킬 이름, 단축키, 이미지, 설명, 발동률, 계수, 각성 정보
- `skillBookMasterData` - 스킬강화권 이름과 대상 스킬 연결

주요 함수:

- `getDefaultCharacterId()`
- `getCharacterDefinition(characterId)`
- `getSkillDefinition(skillId)`
- `getCharacterSkillIds(characterId)`
- `createDefaultCharacterSkillState(characterId)`
- `getDefaultSkillState(characterId)`
- `createSkillBookMapping()`
- `getSkillBookDefinition(itemName)`
- `getSkillBookDisplayInfo(itemName)`
- `isAwakeningSkillBook(itemName)`
- `getSkillMaxLevel(skillId)`
- `normalizePlayerCharacterState(player)`
- `getCurrentCharacterId(player)`
- `getCurrentUserCharacter(player)`
- `getCurrentCharacterSkills(player)`
- `getSkillState(skillId, player)`
- `getRenderableSkillList(player)`

---

## v0.68 변경: `src/state/game-state.js`

캐릭터 추가 준비를 위해 player에 아래 구조가 추가되었습니다.

```txt
player.currentCharacterId
player.ownedCharacterIds
player.userCharacters
```

기존 코드 호환을 위해 `player.skills`는 유지됩니다.

---

## v0.68 변경: `src/ui/render-ui.js`

`renderSkills()`가 기존 하드코딩 배열 대신 `getRenderableSkillList(player)`를 우선 사용합니다.

`getSkillBookInfo()`는 기존 이름을 유지하지만 내부 정보는 `src/data/skills.js`의 `getSkillBookDisplayInfo()`에서 가져옵니다.

---

## v0.68 변경: `src/systems/item-system.js`

스킬강화권 사용 시 `getCurrentCharacterSkills(player)`와 `getSkillBookDefinition(itemName)`을 우선 사용합니다.

---

## v0.68 변경: `src/systems/combat-system.js`

전투 중 스킬 레벨을 읽을 때 `player.skills` 직접 접근보다 `getCurrentCharacterSkills(player)`를 우선 사용합니다.

아직 스킬 공식 전체가 완전히 데이터 기반으로 바뀐 것은 아닙니다.

---

## CSS 점검 문서

CSS 중복/SCSS 전환 판단은 아래 문서에 정리했습니다.

```txt
docs/archive/stage-notes/CSS_AUDIT.md
```


## v069 추가 문서

- `docs/archive/stage-notes/SKILL_DAMAGE_TEXT_FIX.md`: 기존 저장 스킬 데이터가 캐릭터별 스킬 구조로 이관되지 않아 스킬 데미지 텍스트가 안 보일 수 있는 문제와 수정 내용을 설명합니다.


## 4순위 2차 관련 문서

- `docs/archive/stage-notes/KILL_REWARD_RESULT_STAGE2.md`
  - `killEnemy()` 처치/드랍/보상 결과 객체화 내용 정리
- `src/systems/action-result-system.js`
  - `createEnemyKillResult()`, `addDropAward()`, `addRewardGold()`, `addBlockedReward()` 추가
- `src/systems/combat-system.js`
  - `killEnemy()`가 `combat.kill` 결과 객체를 만들고 UI 요청을 모으도록 변경


## v073 결과 객체화 추가 지점

- `src/systems/action-result-system.js`: `item.equip`, `item.unequip`, `skill_book.use`, `boss.summon` 결과 객체 생성 헬퍼와 UI 요청 처리 확장
- `src/systems/item-system.js`: `actionEquipDirect()`, `actionUnequipDirect()` 결과 객체화
- `src/ui/render-ui.js`: `summonBoss()` 결과 객체화
- `docs/archive/stage-notes/EQUIP_SKILL_BOSS_RESULT_STAGE3.md`: 4순위 3차 작업 상세


---

## API 계약 파일

| 파일 | 역할 | 비고 |
|---|---|---|
| `src/api/API_PLAN.md` | FastAPI로 만들 API 목록과 우선순위 | 5순위에서 확정 응답 형태 기준으로 갱신 |
| `src/api/api-response-contract.js` | API 응답 버전, 행동 타입, 에러 코드, 응답 생성 헬퍼 | 현재 `index.html`에서 로드하지 않음. 미래 FastAPI/Vue 연결 기준 |
| `docs/contracts/API_RESPONSE_CONTRACT.md` | 서버-프론트 응답 형태 계약서 | FastAPI 구현 전 반드시 참고 |
| `tools/smoke/frontend/smoke_api_response_contract.js` | 응답 계약 헬퍼/예시 검증 | `node tools/smoke/frontend/smoke_api_response_contract.js` |


---

## v075 backend/ 구조

```txt
backend/app/main.py
→ FastAPI 앱 생성, CORS, 라우터 연결

backend/app/core/config.py
→ .env 설정 로딩

backend/app/core/response.py
→ game-api-response.v1 공통 응답 생성

backend/app/api/routes/game.py
→ game.master_data / game.load / game.save stub

backend/app/api/routes/admin.py
→ admin.requirements / admin.change-preview stub

backend/app/models/
→ PostgreSQL SQLAlchemy 모델 초안

backend/sql/schema_draft.sql
→ DB 설계 초안 SQL
```

---

## 원본: `docs/archive/stage-notes/DECISION_LOG.md`

# 기술 선택 결정 기록

## 선택한 최종 구조

```txt
Vue 프론트엔드
FastAPI 백엔드
PostgreSQL DB
Vue 기반 관리자 페이지
```

## Vue를 유지하는 이유

- 게임 UI를 컴포넌트로 나누기 좋습니다.
- 기존 프론트 구조를 Vue로 옮기기 자연스럽습니다.
- 관리자 페이지도 같은 기술로 만들 수 있습니다.
- HTML/CSS/JS 역할 구분이 비교적 직관적입니다.

## FastAPI를 선택하는 이유

- 게임 계산/판정 API를 만들기 좋습니다.
- 전투, 드랍, 강화 같은 서버 판정을 작게 나눌 수 있습니다.
- 자동 API 문서가 생겨 테스트하기 좋습니다.
- Python 기반이라 데이터 변환/배치 작업도 편합니다.

## PostgreSQL을 선택하는 이유

- 유저, 아이템, 장비, 보스, 드랍률처럼 관계가 많은 데이터에 적합합니다.
- JSONB를 사용할 수 있어 아이템 특수 옵션처럼 유연한 데이터도 처리할 수 있습니다.
- 관리자 페이지에서 수정 가능한 마스터 데이터 관리에 적합합니다.

## 지금 바로 하지 않는 것

### 바로 Vue 전환

현재 전투/드랍/강화 로직이 프론트 JS에 강하게 연결되어 있어서, 먼저 백엔드 분리 준비를 합니다.

### 바로 FastAPI 전체 이전

아직 데이터/로직/UI가 일부 섞여 있으므로, 먼저 순수 데이터화와 결과 객체화를 진행합니다.

### 바로 PostgreSQL 입력

현재 JS 데이터를 먼저 JSON/seed 형태로 추출한 뒤 DB에 넣는 것이 안전합니다.

---

## 원본: `docs/archive/stage-notes/FRONTEND_MASTER_DATA_BRIDGE.md`

# Frontend Master Data Bridge

## 목적

`v085`는 현재 HTML/JS 게임을 바로 DB 데이터로 교체하지 않고, 브라우저에서 FastAPI master-data API를 안전하게 읽어올 수 있는 준비층을 추가한다.

현재 게임 동작은 기존 JS 데이터 기준으로 그대로 유지한다. 이 단계는 다음 단계에서 `src/data/*.js`의 정적 데이터를 API 데이터로 대체하기 위한 연결 확인 단계다.

## 추가 파일

```txt
src/api/game-api-client.js
src/api/master-data-bridge.js
tools/smoke/game/smoke_frontend_master_data_bridge.js
```

## 브라우저 전역 객체

브라우저 콘솔에서 아래 객체와 함수를 사용할 수 있다.

```txt
RpgGameApi
RpgMasterDataBridge
checkBackendMasterData()
loadBackendMasterData()
getCachedBackendMasterData()
```

## 기본 API 주소

기본 API 주소는 다음과 같다.

```txt
http://127.0.0.1:8000/api/v1
```

변경이 필요하면 브라우저 콘솔에서 아래처럼 설정할 수 있다.

```js
RpgGameApi.setApiBaseUrl("http://127.0.0.1:8000/api/v1");
```

설정값은 `localStorage`의 아래 키에 저장된다.

```txt
upgradeRpgApiBaseUrl
```

## 브라우저에서 확인하기

FastAPI 서버를 켠 뒤, 게임 화면을 브라우저에서 열고 개발자도구 콘솔에서 실행한다.

```js
await checkBackendMasterData();
```

정상이라면 콘솔에 다음 로그가 나온다.

```txt
[Upgrade RPG] master-data API check passed
```

이미지 data URL까지 포함해서 확인하려면 아래를 실행한다.

```js
await checkBackendMasterData({ includeAssets: true });
```

## 터미널 정적 검사

위치: 프로젝트 루트

```bash
node tools/smoke/game/smoke_frontend_master_data_bridge.js
```

정상이라면 다음 문구가 나온다.

```txt
frontend master-data bridge smoke test passed
```

## 주의

이 단계에서는 아직 게임 화면이 API 데이터를 사용하지 않는다. 기존 게임 동작 안정성을 위해 API 데이터는 `window.backendMasterDataSnapshot`에만 저장한다.

다음 단계에서 이 snapshot과 기존 `src/data/*.js` 데이터의 차이를 비교하고, 안전하게 전환할 수 있는 어댑터를 만든다.

---

## 원본: `docs/archive/stage-notes/HANDOFF_CLEANUP_NOTES_V246.md`

# Handoff Cleanup Notes — v246

## 정리한 항목

- 루트 README, backend readiness, current status, next steps를 v246 기준으로 갱신
- 오래된 `NEXT_STEP_V240_REQUEST_PAYLOAD_VALIDATION.md`를 `docs/archive/stage-notes/`로 이동
- Windows 가상환경 `backend/.venv` 제거
- `__pycache__`, `.pyc`, pytest/ruff/mypy 캐시 제거
- 실제 로컬 설정인 `backend/.env`를 전달 ZIP에서 제거하고 `.env.example`만 유지
- FastAPI TestClient용 `httpx2`를 backend dev 의존성에 기록

## 유지한 항목

- 기능 코드와 route 구조
- DB/schema/seed
- API 주소와 응답 body
- 인증 및 write guard
- 단계별 smoke 파일과 과거 기록 문서

## 패키징 원칙

다음 파일은 Git과 전달 ZIP에 포함하지 않습니다.

```text
.env
backend/.env
.venv/
backend/.venv/
node_modules/
__pycache__/
*.pyc
*.zip
```

---

## 원본: `docs/archive/stage-notes/LOCAL_DB_PORT_POLICY.md`

# Local DB Port Policy

## Decision

로컬 개발용 PostgreSQL은 호스트 포트 `55432`를 사용한다.

```txt
Host PC: 127.0.0.1:55432
Docker container: postgres:5432
```

`docker-compose.yml` 기준:

```yaml
ports:
  - "55432:5432"
```

`backend/.env` 기준:

```env
DATABASE_URL="postgresql+asyncpg://rpg_user:rpg_password@127.0.0.1:55432/rpg_game"
```

## Why

Windows 개발 환경에서 기본 PostgreSQL 포트 `5432`가 다른 로컬 PostgreSQL 또는 기존 서비스와 충돌할 수 있었다.
실제로 Docker 컨테이너 내부 접속은 정상인데 Python에서 `127.0.0.1:5432` 접속 시 비밀번호 오류가 발생했다.

따라서 이 프로젝트는 로컬 호스트 포트를 `55432`로 고정한다.

## Commands

위치: **프로젝트 루트**

```bash
docker compose down -v --remove-orphans
docker compose up -d --force-recreate
docker ps
```

`docker ps`에서 아래처럼 보이면 정상이다.

```txt
0.0.0.0:55432->5432/tcp
```

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
python -c "import psycopg; conn=psycopg.connect('postgresql://<user>:<password>@127.0.0.1:55432/rpg_game'); print(conn.execute('select 1').fetchone()); conn.close()"
python scripts/setup_dev_db.py --reset --seed --verify
```

---

## 원본: `docs/archive/stage-notes/NEXT_STEP_V240_REQUEST_PAYLOAD_VALIDATION.md`

# Next Step — v240 Backend Admin Request Payload and 422 Validation Contract

## 목표

관리자 route의 request parsing 경계를 고정합니다. 실제 DB 쓰기는 실행하지 않고, FastAPI/Pydantic validation 단계까지만 검증합니다.

## 검증 후보

- 정상 payload가 alias 기준으로 들어왔을 때 올바른 model로 parsing되는지 확인
- `confirmText`, `reason`, `dryRun`, `baseValues` alias 유지 확인
- invalid payload의 대표 `422 validation detail` 구조 확인
- apply 계열 route의 `X-Admin-Dev-Key` write guard 유지 확인

## 지켜야 할 것

- route path 변경 없음
- API 응답 body 구조 변경 없음
- DB/env 변경 없음
- 실제 apply 쓰기 실행 없음

## smoke 후보

- `tools/smoke/contracts/smoke_backend_admin_request_payload_validation_contract.py`

## 버전 후보

- readiness version: `v240.backend-admin-request-payload-validation-contract`
- splitStatus: 큰 구조 변경이 아니라면 `admin-schema-field-constraint-contract-v238` 유지 가능

---

## 원본: `docs/archive/stage-notes/ROOT_CHANGELOG_THROUGH_V320.md`

# v320.github-actions-ghcr-workflow-prepared-gated

- GitHub Actions를 외부 action 8개 full-SHA allowlist와 full-length SHA 강제로 변경하고 `ghcr-production-publish` environment의 `main` rule을 구성.
- `workflow_dispatch` 전용 backend GHCR workflow를 추가하되 source-controlled reviewer gate를 `false`로 고정해 GHCR login 전에 차단.
- 루트 build context, checksum-pinned Trivy 0.70.0, pushed exact-digest 재검사, BuildKit provenance/SBOM 검사 후 Cosign sign/verify 순서로 공급망 흐름을 보강.
- YAML AST로 exact trigger/job/permission/action/step을 검사하고 workflow 전체 소스와 파싱된 실행 의미를 별도 SHA-256으로 잠가 quoted trigger, 추가 write/secret 유출 step, `|| true`, SHA/checksum/gate 변조를 차단하는 smoke 추가.
- action/run step별 잠금과 parsed secret 경로 allowlist를 더하고, 루트 Docker context에서 모든 `.env`/`*.env`/`.envrc` 파일을 제외해 미추적 secret 전송을 차단.
- Python 범위 의존성, unpinned pip upgrade, mutable Dockerfile frontend 때문에 deterministic build lock은 아직 미완료이며 첫 게시 전에 별도 해결해야 함을 fail-closed 계획에 기록.
- 실행 중인 개발 서버 재사용, GitHub 설정 권한, 숨김 파일/.env 작업 권한, 보안 회전 체크리스트를 지속 handoff 규칙에 반영.
- GitHub Free/Pro/Team의 required reviewer는 공개 저장소에서만 지원되므로 비공개 저장소에 collaborator를 추가하는 것만으로는 해결되지 않음을 기록.
- workflow, Docker build/push, registry, DB, Alembic 실행은 하지 않음. 다음 단계는 `github-enterprise-cloud-required-reviewer`, `owner-only-source-controlled-two-step`, `keep-publishing-disabled` 중 게시 승인 모델 선택이며, 선택 전에는 hard gate를 `false`로 유지.

# v319.github-connector-actions-settings-reviewed

- ChatGPT Codex Connector를 `gihohoho/upgrade-rpg` 저장소 하나에만 연결하고 Codex repository 조회를 검증.
- GitHub Actions 설정과 environment를 읽기 전용으로 검토해 현재 모든 action 허용, full-length SHA 강제 꺼짐, read-only 기본 `GITHUB_TOKEN`, publish environment 부재를 기록.
- 연결·검토 완료 상태와 아직 승인되지 않은 repository 설정/environment/workflow 변경을 분리한 v319 fail-closed 검사와 smoke 추가.
- `.github/workflows/`, workflow 실행, Docker/registry/DB/Alembic mutation은 없음.

# v318.github-actions-action-sha-candidates-reviewed

- 9개 허용 action의 최신 정식 release tag와 upstream 40자리 commit SHA를 검토 후보로 고정.
- 검토 후보와 사용자 승인값을 분리하고 workflow 생성·실행 승인 `false`를 유지하는 fail-closed 검사 추가.
- Windows smoke 호환성 문제를 수정하고 전체 core smoke 통과.
- `.github/workflows/`, workflow 실행, Docker/registry/DB/Alembic mutation은 없음.

# v317.github-actions-ghcr-static-workflow-plan

- GitHub Actions/GHCR publish의 `workflow_dispatch` only, exact main SHA, protected environment, concurrency 정적 정책 추가.
- validate/build-scan job은 `contents: read`, publish/attest/sign job만 `packages`, `attestations`, `id-token` write를 받도록 최소 permissions 설계.
- local OCI, SPDX JSON SBOM, Trivy HIGH/CRITICAL, provenance, SBOM attestation, Sigstore keyless signature와 verification을 fail-closed gate로 고정.
- 모든 action은 검토된 40자리 commit SHA가 필요하며 실제 SHA가 미승인인 동안 workflow 생성을 차단.
- ZIP/Git 명령 안내를 중단하고 Codex가 NEXT_CHAT 갱신과 add/commit/push를 직접 수행하는 협업 규칙 반영.
- 필요한 extension/repository 권한/설치는 사용자에게 요청하고 해결되지 않으면 다음 작업에서도 다시 요청하도록 인계 규칙 반영.
- `.github/workflows/`, workflow 실행, Docker/registry/DB/Alembic mutation은 없음.

# v316.codex-handoff-audit-fix

- v315 커밋의 strict checker와 실제 추적 파일을 대조해 superseded 활성 파일 정리 누락을 수정.
- 보관본이 있는 v313 문서/정책/checker와 더 이상 실행되지 않는 v313 smoke를 활성 경로에서 제거.
- 로컬 작업 폴더에서는 금지 경로의 Git 추적 여부만 확인하고, 추출된 ZIP에서는 금지 경로의 실제 존재를 계속 차단하도록 검사 모드를 분리.
- ZIP 모드에 `backend/.env` fixture를 추가해 secret 경로 검사가 fail-closed로 유지됨을 검증.
- 실제 `.env` 내용, workflow, token/PAT, Docker, registry, DB, Alembic은 읽거나 변경·실행하지 않음.

# v315.codex-ghcr-namespace-handoff-ready

- GitHub/GHCR namespace를 사용자 확인값 `gihohoho`로 고정.
- backend repository를 `ghcr.io/gihohoho/upgrade-rpg-backend`로 고정.
- Codex용 루트 `AGENTS.md`, v315 prompt/handoff, read-only checker/smoke 추가.
- CI credential 우선안을 GitHub Actions `GITHUB_TOKEN`, local credential/PAT는 deferred로 기록.
- v313/v314 이미지 정책 문서와 JSON을 archive/review로 이동하고 superseded checker를 정리.
- `docs/` 루트의 archive 중복 사본을 제거하고 현재/보관 문서 인덱스를 단일화.
- 실제 workflow, token, Docker login/pull/build/push, DB/Alembic mutation은 실행하지 않음.

# v314.ghcr-amd64-base-image-selection

- Selected GitHub Container Registry (`ghcr.io`) with private `upgrade-rpg-backend` repository naming.
- Kept `<github-account-or-organization>` unresolved and fail-closed; no account or organization name was invented.
- Selected `linux/amd64` as the production target platform.
- Added `backend/Dockerfile.production` pinned to `python:3.11.15-slim-bookworm@sha256:28255a3ace7eb4c48bc1b57b90af29e1bc82b4fd6c60614a8e3dce61b87ff941` while preserving the local Dockerfile.
- Added v314 selection JSON, read-only checker, fail-closed smoke, current documentation, and handoff synchronization.
- Did not run registry login, Docker pull/build/push, container/network/volume mutation, DB connection, or Alembic mutation.

# v313.backend-image-source-digest-policy

- 기호 PC에서 통과한 v312 Compose config render-only 안전 요약을 `deploy/review/production-compose-config-render-v312.json`에 기록했습니다.
- architecture/capacity plan의 config render 상태를 approved/executed `yes/yes`로 동기화했습니다.
- production backend image를 registry/namespace/repository + exact SHA-256 digest 형식으로 고정했습니다.
- source Git commit, target platform, base image digest, SBOM, provenance, signature, vulnerability review 게이트를 추가했습니다.
- 현재 `python:3.11-slim`은 mutable tag이므로 base image digest 승인 전 build가 차단됩니다.
- registry credential, Docker pull/build/push, container/network/volume, DB, Alembic mutation은 실행하지 않았습니다.

# v312.production-managed-postgres-reverse-proxy-config-render-ready

- 기호 승인에 따라 운영 기본 방향을 관리형 PostgreSQL + provider CA verify-full + 외부 reverse proxy HTTPS + backend 1 replica/1 worker로 확정.
- production Compose에서 bundled PostgreSQL, Adminer, named DB volume, host ports, build를 제거하고 backend-only exact-digest image template로 전환.
- `production-architecture-selection.example.json`, reverse proxy 경계 문서, v312 selection checker 추가.
- 실제 `.env`/secret을 읽지 않고 정확히 `docker compose config`만 호출하는 confirmation-gated wrapper 추가.
- Docker CLI가 없는 handoff 환경에서는 실제 config를 실행하지 않았고, fake Docker smoke로 config 외 명령 미호출과 임시 review 파일 정리를 검증.
- image pull/build, container/network/volume mutation, managed DB 연결, Alembic/DB mutation은 계속 미승인.

# v311.production-capacity-tls-network-isolated-plan

- Added a review-only production capacity input and a read-only fail-closed checker.
- Calculated the current 1 replica × 1 worker SQLAlchemy steady/burst connections as 5/15.
- Added 10 non-application reserve connections and 20% safety margin, producing minimum 30 and review candidate 40.
- Added scale scenarios: 2 replicas require minimum 50; 2 replicas × 2 workers require minimum 90.
- Recorded managed PostgreSQL as the preferred review path and documented bundled PostgreSQL TLS requirements as an unapproved alternative.
- Documented reverse proxy HTTPS-only, backend/PostgreSQL internal-network, image digest approval, and isolated config/build/run/cleanup stages.
- Added dedicated smoke, core registration, synchronized current/handoff documents, and no Docker/DB/env/Alembic mutation.

# v310.production-secrets-tls-container-static-validation-preflight

- 운영 secret/TLS/container template 정적 checker와 smoke 추가
- production variable placeholder inventory 및 password/CA Compose secret 경계 추가
- backend container healthcheck 추가
- 실제 deployment env/secret 파일 Git·Docker context 제외
- 완료된 PostgreSQL baseline 문서를 archive로 이동해 docs/current 정리
- v309 사용자 PC strict + health 통과 상태를 handoff에 반영
- 실제 DB/.env/Docker/Alembic mutation 없음

# v309 - Runtime engine source-binding inspector fix

- Fixed a false positive where the readiness checker only recognized a single-line `create_async_engine(settings.database_url...)` call.
- Replaced the brittle string match with Python AST inspection of positional and `url=`/`database_url=` arguments.
- Added a dedicated multiline regression smoke and wired it into the core smoke runner.
- Kept FastAPI runtime, pool policy, DB, `.env`, Docker, Alembic history, API contracts, and game content unchanged.

# v308 - FastAPI/PostgreSQL runtime config hardening

- Recorded the user PC v307 `--strict --require-health` success with exact `rpg_game`, PostgreSQL 16.14, healthy Docker, and 12 production-hardening warnings.
- Added five environment-backed SQLAlchemy async pool options while preserving local defaults.
- Added FastAPI lifespan shutdown disposal with no startup migration or schema mutation.
- Added a fail-closed production settings guard for DEBUG and local/default or short JWT/admin secrets.
- Added a non-root FastAPI Dockerfile and a separate production Compose review template without Adminer or PostgreSQL host-port publication.
- Added a read-only v308 verifier, dedicated smoke, readiness/current/handoff documentation, and a new handoff ZIP.
- Did not edit the real `.env`, run Docker build/up/down, change DB schema/data, add revisions, alter API contracts, auth/write behavior, Vue, or game content.

# v307 - PostgreSQL/FastAPI deployment runtime readiness

- Added a read-only runtime readiness checker for exact `rpg_game`, `postgresql+asyncpg`, live revision, FastAPI startup mutation boundaries, Docker running/healthy state, env key inventory, and DB health contract.
- Added a production-hardening warning classification for pool policy, engine disposal lifecycle, local secrets, published Adminer/PostgreSQL ports, image digest, TLS, and FastAPI container image.
- Added a manual deployment migration runbook that keeps migrations out of server startup and requires backup, isolated rehearsal, and separate approval.
- Added dedicated v307 smoke, core registration, readiness/current/handoff documentation, and a new handoff ZIP.
- No `.env`, Docker container/volume, DB schema/data, Alembic revision/history, API route/body, auth, write logic, seed, Vue, or game content was changed.

# v306 - PostgreSQL next revision read-only preflight

- Recorded the user PC v305 completion result as `postgres-baseline-completion-state-verified`.
- Added a read-only next-revision preflight that verifies the single Alembic graph, approved model/env source hashes, canonical schema equivalence, Alembic metadata candidate operations, and PostgreSQL sequence ownership.
- Runs metadata comparison inside a PostgreSQL read-only transaction with an SQL statement guard; no revision file or Alembic mutation command is executed.
- Returns either no-new-revision-required or separate-schema-change-intent-review and never auto-approves autogenerate/upgrade/downgrade.
- Added dedicated smoke, core registration, readiness/current/handoff documentation, and v306 ZIP handoff.
- Did not change DB schema/data, `.env`, Docker resources, seed, auth, API routes/bodies, Write Guard, Vue write integration, or game content.

# v305 - PostgreSQL baseline completion state lock

- Confirmed the user PC v304 source post-check result: source 23/749, application 22/748, current `v295_initial_schema`, v304 execution report verified.
- Added `tools/check_postgres_baseline_completion_state.py`, a read-only completion checker for source/rehearsal/migration state, v302/v304 reports, application digests, and the exact single-revision set.
- Added a regression smoke that blocks legacy pre-stamp classification, missing reports, changed migration endpoint, and unapproved extra revisions.
- Updated current/readiness/handoff documents to `alembic-managed-baseline-complete`.
- Added a separate next-revision read-only plan; no revision generation, autogenerate, upgrade, downgrade, stamp retry, DB create/drop/restore, `.env`, seed, auth, API, or game-content change was performed.

# v304 - PostgreSQL source baseline stamp final guard

- Added an exact-source `rpg_game` baseline stamp guard with read-only pre/post inspection.
- Pinned revision, backup SHA-256, verified rehearsal result, and approved application schema/data digests.
- Added exact confirmation flags for the future source-only `stamp head` approval boundary.
- Added post-stamp recovery classification that prevents automatic retries after a partial report failure.
- Added dedicated source stamp smoke coverage and updated handoff/current-status documentation.
- Did not execute source stamp, upgrade, downgrade, DB create/drop/restore, `.env`, Docker, API/write, auth, seed, or game-content changes.

# v303 - Restore rehearsal stamp post-check recovery

- Recorded the user-approved v302 rehearsal-only `stamp head` execution.
- Identified the immediate v302 `--inspect` failure as a post-stamp inspector bug: it reused the pre-stamp 22-table validator and rejected the expected `alembic_version` table.
- Updated `--inspect` to recognize both pre-stamp and post-stamp states without running any mutation or subprocess.
- Pinned the actual user-confirmed pre-stamp application schema/data digests and require 22 application tables / 748 rows to remain identical after stamp.
- Independently revalidate source `rpg_game`, the verified v300 migration endpoint, exact revision/SHA-256, and the local v302 execution report when present.
- Added report-missing recovery classification without retrying stamp, rollback, upgrade, downgrade, DB create/drop/restore, or source mutation.
- Expanded dedicated smoke coverage for pre-stamp, post-stamp with verified report, and post-stamp report-missing states.
- Kept source stamp, API/write/auth/seed/game-content changes, `.env`, and Docker resources untouched.

# v302 - Restore rehearsal baseline stamp guard ready

- Recorded the user-PC v301 source preflight success.
- Added `tools/stamp_postgres_restore_rehearsal_database.py`, pinned to `rpg_game_restore_rehearsal_v290`, `v295_initial_schema`, and exact revision SHA-256.
- Added read-only full application schema and row-content SHA-256 signatures for all 22 tables / 748 rows.
- Added postconditions allowing only `alembic_version` 1 table / 1 row while requiring source and migration DB signatures to remain identical.
- Added exact `--confirm-target` and `--confirm-revision` execution confirmations; actual stamp was not executed.
- Added dedicated simulated smoke, core registration, current/handoff documentation, and v302 ZIP handoff.
- Kept DB schema/data, `.env`, Docker resources, seed, auth, API routes/bodies, Write Guard, Preview/Apply bodies, and game content unchanged.

## v300.postgres-migration-roundtrip-reupgrade-ready

- v298 first upgrade와 v299 downgrade report를 모두 요구하는 두 번째 `upgrade head` 왕복 검증 가드 추가
- 첫/두 번째 upgrade의 table list, row counts, revision, schema classification, differences exact signature 비교
- source/rehearsal DB 보존, no retry, no stamp/downgrade/create/drop/restore 경계 유지
- 전용 smoke, core 등록, readiness/current/handoff 문서 v300 동기화

## v299.postgres-migration-test-downgrade-base-ready

- 사용자 PC에서 v298 isolated `upgrade head` 성공 결과 반영
- exact reviewed revision과 v298 upgrade report를 요구하는 `downgrade base` 실행 가드 추가
- target DB가 빈 `alembic_version` placeholder로 복귀하는지 검증
- source/rehearsal DB 작업 전후 보존, 자동 retry/upgrade/stamp/create/drop/restore 차단
- 전용 smoke, core 등록, readiness/current/handoff 문서 v299 동기화

# Changelog

## v298.postgres-initial-alembic-manual-review-upgrade-ready

- 사용자 review bundle의 exact revision SHA-256과 bundle SHA-256을 재검증
- `v295_initial_schema`를 SQLAlchemy model과 수동 교차 검토: 22 tables / 209 columns / 42 indexes / 21 FK / 6 Unique
- 타입, 길이, nullable, PK/FK/ondelete/onupdate, unique, index, server default 일치 확인
- PostgreSQL FLOAT 2개가 v289 DOUBLE PRECISION alias 정책과 일치함을 확인
- downgrade index/table 대응과 FK dependency reverse order 검증
- 검토된 revision 파일과 machine-readable manual review manifest를 프로젝트 기준 파일로 포함
- `tools/upgrade_postgres_migration_test_database.py` 추가: exact reviewed revision을 `rpg_game_migration_empty_v290`에만 `upgrade head`하도록 준비
- 실제 upgrade/downgrade/stamp/source DB mutation은 실행하지 않음
- manual review/upgrade guard smoke, core 등록, v298 문서/handoff 동기화

## v297.postgres-initial-alembic-op-f-parser-recovery

- 사용자 실제 v296 결과 `unexpected Alembic operations: upgrade=['f'], downgrade=['f']`를 재현하고 원인을 확인
- Alembic generated revision의 nested `op.f(...)`를 naming helper로 분리해 operation allowlist false positive 제거
- 실제 create/drop/index/constraint operation 검사와 execute/data/destructive operation 차단 유지
- 전용 smoke가 `op.create_index(op.f(...))`, `op.drop_index(op.f(...))`를 생성하고 `f`가 operation count에 포함되지 않음을 검증
- 실패 시 생성 revision/review artifact 정리, empty `alembic_version` placeholder 재사용, DB/env/Alembic apply 경계 유지
- v297 current/readiness/handoff 문서 동기화

## v296.postgres-initial-alembic-revision-placeholder-recovery

- v295 autogenerate가 남긴 정확히 `alembic_version` 1 table / 0 rows / no revision 상태를 안전한 recovery workspace로 인정
- `--inspect-workspace` 읽기 전용 진단과 placeholder 재사용 경계 추가
- 다른 application table/row/revision이 있으면 실행 전 차단
- upgrade/downgrade/stamp, DB create/drop/restore 미실행

## v295.postgres-initial-alembic-revision-create-review-tool

- 실제 v294 empty migration test DB 생성 성공 결과를 현재 기준에 반영
- `backend/alembic/script.py.mako` 표준 revision 템플릿 추가
- `tools/create_postgres_initial_alembic_revision.py` 추가
- child process `DATABASE_URL`을 `rpg_game_migration_empty_v290`으로만 override하고 `.env`는 유지
- deterministic revision ID `v295_initial_schema`와 예상 파일명 고정
- 생성된 revision의 22 tables / 209 columns / nullable / PK / FK / unique / index 자동 검토
- upgrade destructive/data operations와 downgrade create/data operations 차단
- source/rehearsal/migration DB before/after 동일 확인
- schema-only local review JSON/bundle 생성, Git/Docker/전달 ZIP 제외
- Alembic upgrade/downgrade/stamp와 DB create/drop/restore는 실행하지 않음
- 전용 smoke, core smoke 등록, v295 문서/handoff 동기화

## v294.postgres-migration-empty-database-create-tool

- 실제 v293 restore rehearsal 성공 결과를 현재 기준에 반영
- `tools/create_postgres_migration_test_database.py` 추가
- exact backup/SHA-256, restore report, source/rehearsal live 상태를 생성 전 재검증
- `rpg_game_migration_empty_v290`이 없을 때만 `createdb` 1회 허용
- owner `rpg_user`, `template0`, source와 같은 locale metadata 적용
- 생성 후 0 tables / 0 rows / alembic_version 없음 확인
- source/rehearsal before/after 동일 확인
- pg_restore/dropdb/Alembic revision/upgrade/downgrade/stamp 차단
- 전용 smoke와 core smoke 등록, v294 문서/handoff 동기화

# v292 - PostgreSQL empty restore rehearsal database creation tool

- Added `tools/create_postgres_restore_rehearsal_database.py` for the user-approved existence-check-and-create-empty-DB boundary.
- Requires the verified v291 backup, recomputes SHA-256, rechecks the 22-table/748-row source baseline, and checks `pg_database` before any mutation.
- Creates only `rpg_game_restore_rehearsal_v290` when absent, with owner `rpg_user`, template `template0`, and source-compatible encoding/collation/locale metadata.
- Verifies the target has zero public tables and no `alembic_version`, then confirms the source remains 22 tables / 748 rows.
- Stops when the target already exists and never runs `pg_restore`, `dropdb`, `.env` edits, Docker changes, Alembic mutations, API/auth/write changes, or game-content changes.
- Added dedicated smoke coverage, core-smoke registration, current-state documentation, and v292 handoff synchronization.

# v291 - PostgreSQL backup creation and archive verification tool

- Added `tools/create_postgres_backup.py` for the user-approved source backup step only.
- Re-runs schema/preflight gates, pins `rpg_game`/`rpg_user`/`upgrade_rpg_postgres`, streams a custom-format dump to a private partial file, validates the archive with `pg_restore --list`, and publishes it only after validation.
- Adds SHA-256, TOC, source table/row snapshot, and manifest sidecars under ignored `local-backups/postgres/`.
- Refuses overwrite/collision and does not restore, create/drop databases, change Docker resources, edit `.env`, run Alembic mutations, or change API/auth/write/game content.
- Added a dedicated smoke and core-smoke registration; the handoff ZIP excludes all backup artifacts.

# v290 - PostgreSQL backup/restore read-only preflight gate

- Added `tools/check_postgres_backup_restore_preflight.py` to re-run the schema-equivalence gate, check host/existing-container `pg_dump`, `pg_restore`, `createdb`, and `dropdb` availability, and report whether the project is ready to request backup execution approval.
- Fixed the backup policy at `local-backups/postgres/` with KST timestamped PostgreSQL custom-format dump names and SHA-256 sidecars; added `/local-backups/` to Git/Docker exclusions.
- Fixed isolated database boundaries: source `rpg_game`, restore rehearsal `rpg_game_restore_rehearsal_v290`, and empty migration test `rpg_game_migration_empty_v290`.
- Added restore before/after table and row-count comparison planning, separate empty-DB Alembic validation planning, a dedicated smoke, and core-smoke registration.
- The handoff sandbox could not connect because `psycopg` and PostgreSQL client/Docker tooling were unavailable there; this is recorded as non-authoritative and no zero-difference claim was made.
- Did not create a dump, restore data, create/drop a database, modify Docker resources, edit `.env`, create/apply/stamp migrations, or change routes/auth/write/game content.

# v289 - PostgreSQL FLOAT alias normalization and handoff cleanup

- Normalized PostgreSQL `FLOAT` aliases in the read-only schema checker so SQLAlchemy `FLOAT` and reflected `DOUBLE PRECISION` are compared as the same storage type.
- Added smoke coverage for `FLOAT`, `FLOAT(24)`, `FLOAT(25)`, `REAL`, and `DOUBLE PRECISION` normalization.
- Updated and registered the canonical next-chat handoff smoke.
- Removed generated `backend/idle_rpg_backend.egg-info/`, added `*.egg-info/` to `.gitignore`, removed duplicate `backend/env.example`, and synchronized current/root/handoff docs.
- Did not change PostgreSQL schema/data, Docker resources, `.env`, seed, Alembic revisions, routes, response bodies, authentication, or write logic.

# v288 - PostgreSQL schema equivalence read-only preflight

- Added `tools/check_postgres_schema_equivalence.py` to compare live PostgreSQL tables, columns, types, nullability, PK, FK, unique constraints, indexes, and check constraints with SQLAlchemy metadata.
- Added `docs/current/POSTGRES_SCHEMA_EQUIVALENCE_CHECK.md` and a dedicated core smoke.
- Kept DB schema/data, Docker resources, env, seed, revisions, migration apply/stamp, API contracts, auth, and write behavior unchanged.

# v287 - Windows subprocess decode fix and baseline strategy confirmation

- Fixed the user-reproduced Windows `cp949`/UTF-8 mixed Docker output `UnicodeDecodeError` with `tools/_safe_subprocess.py`.
- Applied safe decoding to PostgreSQL runtime, prerequisite, and Alembic read-only checkers.
- Recorded the actual DB result: PostgreSQL 16.14, 22 model/public tables, 748 rows, no `alembic_version`, healthy DB endpoint.
- Confirmed `existing-schema-without-alembic-baseline` and the existing-data-preserving baseline strategy.

# v286 - PostgreSQL/Alembic baseline strategy plan

- Added a decision matrix for empty DB, existing create_all schema with preserved data, and schema drift.
- Requires backup/restore rehearsal and separate empty-DB migration verification before any baseline stamp.
- Kept revision creation, upgrade, downgrade, stamp, DB schema/data, Docker resources, and env unchanged.

# v285 - PostgreSQL runtime read-only state checker

- Added `tools/check_postgres_runtime_readonly_state.py` for read-only Docker status, PostgreSQL schema/table/row counts, model-table comparison, Alembic version state, and FastAPI DB health.
- Added automatic classifications: `empty-database`, `existing-schema-without-alembic-baseline`, `schema-drift`, and `alembic-managed`.
- Added a dedicated smoke and registered it in core smoke.
- The checker never starts/stops Docker, mutates SQL data/schema, edits env, or runs migration mutation commands.

# v284 - Alembic asyncpg online env fix

- Fixed the user-reproduced `sqlalchemy.exc.MissingGreenlet` from `python -m alembic current`.
- Replaced sync `engine_from_config()` with `async_engine_from_config()`, async connection handling, and `connection.run_sync()`.
- Added `tools/check_alembic_readonly_state.py` for read-only `history`, `heads`, and `current` collection.
- Added a dedicated Alembic async env smoke and registered it in core smoke.
- Recorded that the actual backend virtualenv is `backend/.venv`.
- Kept DB schema/data, Docker volume, env, seed, revisions, migration apply/stamp, routes, API bodies, auth, and write logic unchanged.

# v283 - PostgreSQL/Alembic prerequisite checker

- Added `tools/check_postgres_alembic_prerequisites.py`, a read-only local checker for Python, virtualenv, Docker, Compose, SQLAlchemy, Alembic, asyncpg, psycopg, and required project files.
- Added `docs/current/POSTGRES_ALEMBIC_LOCAL_CHECKLIST.md` with exact install locations, `.venv` states, and dangerous commands that remain forbidden.
- The checker never connects to the DB, starts Docker, changes `.env`, or runs migrations.

# v282 - PostgreSQL/Alembic readiness report

- Added `tools/report_postgres_alembic_readiness.py` and `docs/current/POSTGRES_ALEMBIC_READINESS.md`.
- Documented 22 SQLAlchemy tables, PostgreSQL-specific types, asyncpg/psycopg responsibilities, Docker settings, and the current Alembic state with zero revisions.
- Recorded missing `versions/` and `script.py.mako`, create_all ownership, async online execution verification risk, and destructive reset/down-volume commands.
- Added `tools/smoke/backend/smoke_postgres_alembic_readiness.py`.
- Kept DB schema/data, Docker volumes, env, seed, route paths, response bodies, auth, Write Guard, write logic, and game content unchanged.

# v281 - Vue admin related-row detail navigation

- Added read-only related-row detail navigation from the relations panel.
- Preserves prior selections in a local `selectionHistory` stack and adds `이전 상세로` without changing routes or write behavior.
- Clears history when the domain/catalog selection is reset.

# v280 - Vue admin read-only relations panel

- Added `AdminMasterRelationsPanel.vue` for `GET /admin/master-data/relations`.
- Displays backend-provided relation groups, compact columns/rows, counts, limited indicators, and loading/error/empty/success states.
- Uses `limit=20`, cancels stale requests, and never requests raw JSON/assets or mutation APIs.
- Added a dedicated read-only relations/navigation smoke.
- Kept DB, env, seed, auth, route paths, API response bodies, Write Guard, Preview/Apply request bodies, and actual write logic unchanged.

# v279 - Vue admin read-only detail panel

- Added `AdminMasterDetailPanel.vue` for `GET /admin/master-data/detail`.
- Displays scalar fields, relation hints, sanitized JSON previews, asset hiding state, and warnings without calling relations or write APIs.
- Improved `/admin/requirements` summary from `-` to `준비 완료` using the existing `readOnlyOverviewReady` response field.
- Kept DB, env, seed, auth, route paths, API response bodies, Write Guard, Preview/Apply request bodies, and actual write logic unchanged.

# v278 - Vue admin catalog query controls

- Added search, enabled/disabled filtering, safe sort selection, and previous/next pagination using the existing catalog GET query contract.
- Resets filters/page when the domain changes and clears stale detail selection whenever the catalog is reloaded.
- Keeps page size at 20 and cancels stale requests with `AbortController`.
- Added no library or framework.

# v277 - Vue admin read-only catalog mini panel

- Added `AdminMasterDomainPanel.vue` for `GET /admin/master-data/domains`.
- Added `AdminMasterCatalogMiniPanel.vue` for the selected domain first page using `limit=20`, `page=1`, `sort=id_asc`.
- Added loading/error/empty/success states, domain selection, generic backend column/row rendering, and stale request cancellation.
- Added dedicated Vue read-only catalog smoke and documentation.
- Kept DB, env, seed, auth, route paths, API response bodies, Write Guard, Preview/Apply request bodies, and actual write logic unchanged.

# v276 - Vue admin read-only domain panel

- Connected `GET /admin/master-data/domains` to the Vue admin shell.
- Parsed the actual response from `payload.domains` and `payload.defaultDomain`.
- Added domain counts, retry, and loading/error/empty/success states.
- No new library or framework was added.

## v275.backend-route-map-report

- Added `tools/report_backend_route_map.py` to generate/check a deterministic backend route map without importing `app.main`.
- Added `docs/current/BACKEND_ROUTE_MAP.md` with all 27 FastAPI routes, GET/POST counts, Vue read-only candidates, and postponed Preview/Apply/write routes.
- Added `tools/smoke/backend/smoke_backend_route_map_report.py` and included it in `tools/run_smoke_core.sh`.
- Updated `frontend/vue-app/src/api/adminReadOnlyApi.js` so master-data detail/relations wrappers translate `rowId` to the backend query name `id`.
- Confirmed that route paths, API response bodies, DB, env, seed, auth, Write Guard, Preview/Apply request bodies, write logic, existing smoke/contract meaning, and game content remain unchanged.

## v274.backend-structure-plan

- Added `tools/report_backend_structure_plan.py` to generate/check a deterministic backend structure plan.
- Added `docs/current/BACKEND_STRUCTURE_PLAN.md` with current route/service/schema/model/db/core responsibilities.
- Added `tools/smoke/backend/smoke_backend_structure_plan.py` to guard that the structure plan stays up to date.
- Confirmed that route paths, API response bodies, DB, env, seed, auth, Write Guard, Preview/Apply request bodies, write logic, existing smoke/contract meaning, and game content remain unchanged.

## v272.vue-readonly-api-smoke-screen

- Added `healthReadOnlyApi` for safe `GET /health` and prepared `GET /health/db` without auto-calling DB health.
- Added `ReadOnlyApiStatusPanel.vue` to show loading/success/error states and a retry button inside the Vue shell.
- Connected `/game` to safe `GET /health` status checking and `/admin` to safe `GET /health` plus `GET /admin/requirements` status checking.
- Added `smoke_vue_readonly_api_status_panel.py` and included it in `tools/run_smoke_vue_shell.sh`.
- Kept legacy `index.html`, `admin.html`, root `src/`, route paths, API response bodies, DB, env, seed, auth, Write Guard, Preview/Apply body, write logic, and game content unchanged.

## v269.legacy-path-dependency-report

- Added `tools/report_legacy_path_dependencies.py` to generate/check a legacy path dependency report before Vue/FastAPI/DB transition work.
- Added `docs/current/LEGACY_PATH_DEPENDENCIES.md` with current high-risk legacy path references, HTML direct-load relationships, and core smoke path dependencies.
- Decided that the future Vue app should be created under `frontend/vue-app/` instead of reusing the root `src/` folder.
- Kept `admin.html`, `index.html`, existing `src/`, backend routes/services, DB, env, seed, auth, API response bodies, write guards, and actual write logic unchanged.

## v268 - Project structure transition prep

- 현재 ZIP 기준으로 `admin.html`, `index.html`, `src`, `backend`, `tools`, `docs`의 역할을 다시 정리했습니다.
- Vue/FastAPI/DB 전환을 위해 보존/이식/대체 후보를 문서화했습니다.
- smoke/contract가 직접 참조하는 legacy 경로 의존성을 1차 분석했습니다.
- `admin.html`, `index.html`, `src/api`, `src/api/admin`, `backend/app/api/routes`, `backend/app/services`는 당장 이동하지 않는 것으로 결정했습니다.
- `docs/current/PROJECT_STRUCTURE.md`, `docs/current/VUE_FASTAPI_DB_TRANSITION_PLAN.md`, `docs/current/NEXT_STEPS.md`, `docs/current/ROADMAP.md`, 인계 문서를 갱신했습니다.
- 런타임 코드, DB, env, seed, route path, API response body, auth, write guard, 실제 write 로직은 변경하지 않았습니다.

## v266 - Admin practical UX polish after feedback

- v262의 `보기 방식` 선택은 롤백해 `마스터 데이터 카탈로그`를 다시 단일 목록으로 정리했습니다.
- 카탈로그 필터 행은 기존처럼 한 줄에 더 잘 들어가도록 `보기 방식` 필드를 제거하고 버튼 위험도 텍스트 chip을 제거했습니다.
- 버튼 위험도는 `조회/Preview/적용주의/고위험` 문구를 버튼 안에 추가하지 않고 색상과 tooltip으로만 전달하도록 변경했습니다.
- 긴 값 미리보기 너비를 기존보다 줄여 표 셀이 덜 늘어나게 했습니다. 전체 값은 기존 `전체` 모달에서 확인합니다.
- 상세 화면 상단의 `API 반영 확인`, `연결 항목`, `필드 도움말` 바로가기 버튼은 클릭 시 관련 카드/섹션으로 이동하거나 펼쳐지도록 보완했습니다.
- 새 파일 `src/api/admin/admin-detail-shortcuts.js`를 추가했습니다. 이 파일은 화면 이동/펼치기만 담당하며 API 호출, fetch, write 로직을 사용하지 않습니다.
- DB/env/seed/API body/route/auth/write guard/실제 write 로직은 변경하지 않았습니다.

## v260 - Admin catalog date/limit/json keys UX

- `마스터 데이터 카탈로그`의 수정 시각 계열 셀은 화면에 `YYYY-MM-DD` 일자만 표시하고, 값 옆 `?` tooltip에서 초 단위 상세 시각을 확인하도록 정리했습니다.
- 카탈로그 `표시 개수` 선택지를 `10`, `30`, `50`, `100` 네 개로 제한하고 기본값을 `10`으로 변경했습니다.
- `JSON 키` 셀은 앞 3개 키만 chip으로 표시하고 남은 키는 `외 N개`로 접으며, 전체 키 목록은 `?` tooltip에서 확인하도록 변경했습니다.
- 새 문서 `docs/archive/stage-notes/ADMIN_CATALOG_DATE_LIMIT_JSON_KEYS_UX.md`를 추가했습니다.
- DB/env/seed/API body/route/auth/write guard/실제 write 로직은 변경하지 않았습니다.

## v259 - Admin catalog compact help UX

- `마스터 데이터 카탈로그` 필터와 결과 목록을 하나의 섹션으로 합쳐 같은 탭 안에서 조회 조건과 결과를 확인하도록 정리했습니다.
- 카탈로그 셀의 긴 설명문을 제거하고 `normal · 일반 장비`, `6 · 특수무기`처럼 핵심 라벨만 표시하도록 변경했습니다.
- 자세한 설명은 표 제목/입력칸 옆 `?` 도움말과 tooltip으로 이동했습니다.
- `필드 용어 도움말`을 기본 필드, 아이템·장비, 스킬·전투·보상, 관계·드랍·강화 기준으로 확장했습니다.
- `formatCatalogCellValue()`를 추가해 카탈로그/관계 표가 공통 compact 표시 규칙을 사용하도록 했습니다.
- 새 Smoke `smoke_admin_catalog_help_compact_ux.js`를 추가하고 전체 Smoke에 포함했습니다.
- DB/env/seed/API body/route/auth/write guard/실제 write 로직은 변경하지 않았습니다.

## v258 - Admin workspace navigation UX

- 관리자 페이지 상단에 `Admin Workspace` 작업 시작 허브를 추가했습니다.
- 조회·상세 확인, 신규 row 생성, 편집·적용 검토, Preview 화면 점검, 변경 이력·Rollback 5개 업무 모드로 화면 진입점을 분리했습니다.
- 업무 모드를 누르면 관련 섹션만 펼쳐지고, 확인 순서/주의사항/주요 버튼을 안내하는 모달이 표시됩니다.
- 사이드바에도 업무 모드 바로가기를 추가해 긴 관리자 페이지에서 목적지를 빠르게 찾을 수 있습니다.
- 전체 보기/보조 섹션 접기 버튼을 추가해 한 화면에 너무 많은 정보가 보이는 문제를 줄였습니다.
- 새 UI는 `src/api/admin/admin-workspace-navigation.js`에 분리했으며 API 호출, fetch, apply/write helper 호출을 하지 않습니다.
- DB/env/seed/API body/route/auth/write guard/실제 write 로직은 변경하지 않았습니다.

## v257 - Admin readiness pageReady alias

- `checkAdminReadOnlyPageReady()` 반환 객체에 `pageReady` 별칭을 추가했습니다.
- 기존 `ok` 필드는 그대로 유지하여 기존 Smoke/호출과 호환됩니다.
- 기호가 브라우저 콘솔에서 `ready.pageReady`를 바로 확인할 수 있도록 ReadOnly smoke에 alias 검사를 추가했습니다.
- DB/env/seed/API body/route/auth/write guard/실제 write 로직은 변경하지 않았습니다.

## v250.1 - frontend readiness return hotfix

- Fixed four v247-v250 readiness values that were calculated internally but omitted from `getAdminBackendServiceSplitContractReadiness()` return object.
- Strengthened backend/frontend parity smoke to verify internal calculation, internal return, public calculation, and final public return for every registered contract readiness value.
- No DB, env, seed, route, schema, response body, authentication, or write-guard changes.

## v246.2 - Backend editable-install packaging hotfix

- Added an explicit setuptools build backend and package discovery rule.
- Editable installs now include only `backend/app*` and exclude `alembic`, `seeds`, `sql`, and tests from package discovery.
- Added `tools/smoke/backend/smoke_backend_packaging_contract.py` to prevent the flat-layout discovery error from returning.
- No DB, API route, response body, authentication, seed, or write-guard changes.

# Changelog

## v246.1 — project cleanup and handoff refresh

- Refreshed root/readiness/current-status/next-step documents to v246.
- Removed packaged Windows `.venv`, local `backend/.env`, Python caches, and compiled files.
- Moved the completed v240 next-step note to `docs/archive/stage-notes/`.
- Added `httpx2` to backend dev dependencies for FastAPI TestClient smoke contracts.
- Kept runtime code, DB, seed, routes, schemas, response bodies, authentication, and write guards unchanged.

## v246.backend-admin-write-replay-safety-contract

- Added isolated repeated-preview parsing checks for all five preview request models.
- Verified all five apply route functions still bind `_write_guard` to `ADMIN_WRITE_GUARD_DEP`.
- Explicitly records that `Idempotency-Key` is not currently supported; no replay-protection behavior is claimed or added.
- Service calls and DB write attempts remain zero.
- Added backend/frontend parity coverage and admin readiness marker `backendWriteReplaySafetyContractReady`.
- Route paths, API response bodies, schemas, DB, env, seed, authentication, and splitStatus are unchanged.

## v245.backend-admin-transport-header-observation-contract

- Added `admin_request_transport_header_observation_contract.py` and its smoke test.
- Observes duplicate `Content-Type`/`Accept`, declared `Content-Length`, and `Transfer-Encoding` at the ASGI/TestClient boundary without claiming wire-level enforcement.
- Keeps service and DB execution counts at zero.
- Added `backendRequestTransportHeaderObservationContractReady` to admin readiness.
- Strengthened backend/frontend parity smoke to compare the complete ordered `extractedFiles` and `routeContract` lists and all v240-v245 readiness links.
- No route, response body, DB, env, seed, authentication, or write-guard changes.

## v245.backend-admin-transport-header-observation-contract

- Added isolated FastAPI contract coverage for UTF-8 Korean/symbol payloads.
- Added Content-Type parameter and header-name case normalization checks.
- Added malformed UTF-8 byte compatibility outcomes without service or DB execution.
- Kept route paths, response bodies, DB, env, seed, auth, and write guards unchanged.

# Changelog

## v245.backend-admin-transport-header-observation-contract

- Added `admin_request_media_size_boundary_contract.py` and its smoke test.
- Frozen octet-stream, URL-encoded form, multipart form, empty binary, and arbitrary binary request parsing boundaries without calling admin services or the DB.
- Added a 64 KiB JSON probe to document that the FastAPI application currently has no explicit request-body size limit.
- Declared request-size enforcement ownership as deployment proxy/server configuration rather than silently changing live API behavior.
- Added backend/frontend readiness synchronization and `backendRequestMediaSizeBoundaryContractReady`.
- Kept route paths, response bodies, schemas, write guards, DB, env, seed, and splitStatus unchanged.

## v242.1 frontend/runtime compatibility hotfix

- Fixed the `json-without-content-type` contract for Starlette/FastAPI version differences.
- Accepts either a decoded JSON `200` response or a stable `422 model_attributes_type` response.
- Still strictly validates response content type, payload, and stable error fields.
- DB, env, seed, routes, response bodies, auth, and write guards are unchanged.

## v242.backend-admin-request-content-negotiation-contract

- Added isolated FastAPI request-boundary checks for `application/json; charset=utf-8` and JSON bodies without a Content-Type header.
- Added stable 422 checks for top-level JSON arrays/strings.
- Froze the difference between an empty JSON object (`body.domain` missing) and a completely empty body (`body` missing).
- Verified that both `Accept: application/json` and `Accept: text/plain` keep the default JSON response content type.
- Service calls and DB writes remain zero; route paths, API response bodies, DB, env, seed, auth, and write guards are unchanged.

## v239.2 final handoff cleanup

- Updated next-chat prompt and handoff docs with the latest confirmed working state.
- Added project working rules and v240 request payload validation planning doc.
- Cleaned transient caches/log candidates from the handoff package.
- No runtime code, API path, response body, DB, or env changes.


## v239.2.backend-admin-schema-model-shared-collector-hotfix

- Updated the admin schema/model contract to reuse `collect_admin_runtime_route_entries()` instead of scanning `app.routes` directly.
- Fixes Windows/FastAPI environments where request metadata passed but schema/model route body checks returned `actualModel: None`.
- Added a smoke guard so the schema/model contract cannot reintroduce a direct `app.routes` scan.
- Kept v239.1 Pydantic required-field compatibility helpers unchanged.
- No API path, response body, DB, or env changes.

## v239 - backend admin shared runtime route collector hotfix

- Centralized admin runtime route collection in `collect_admin_runtime_route_entries()`.
- Request metadata now reuses the same app/api_router/owner-router fallback chain as runtime, operation, and response metadata contracts.
- Fixes Windows/FastAPI environments where runtime route smoke passed but request metadata still saw `runtimeRouteCount: 0`.
- API paths, response bodies, DB schema, and environment files remain unchanged.


## v238.6 - backend admin runtime mounted-app hotfix

- Runtime admin route collector now traverses Starlette/FastAPI containers that expose child routes through `node.app.routes` or `node.app.router.routes`.
- Admin page readiness now exposes `failedChecks` and `readinessChecks` so `ok: false` identifies the exact blocking checks.
- API paths, response bodies, DB schema, and environment files remain unchanged.

## v238.9 - backend admin OpenAPI f-string hotfix

- Reworked the default OpenAPI operation-id helper to normalize the route path before interpolation.
- Removes the Python syntax error caused by a regex backslash inside an f-string expression on Windows/Python versions that reject it.
- Runtime, operation, OpenAPI, response metadata, request metadata, and compile smokes pass.
- API paths, response bodies, DB schema, and environment files remain unchanged.

## v240 frontend readiness contract hotfix

- Fixed the admin page static backend split contract so the v240 payload validation file and 422 rule are included.
- Prevented `backendServiceSplitContractReady` from cascading all backend readiness checks to false.
- Added smoke assertions that keep the frontend and backend contract lists synchronized.

## v241.backend-admin-validation-error-compatibility-contract

- Added `admin_request_payload_validation_contract.py` to freeze normal admin request alias serialization.
- Added representative FastAPI 422 `detail` checks for all 10 admin body request schemas.
- Validation runs in an isolated FastAPI app and stops before service or database execution.
- Preserved all admin route paths, response body shapes, write guards, DB settings, env settings, and seed data.
- Added the v240 smoke to `tools/run_smoke_core.sh` and updated admin readiness version.


## v241
- Added malformed JSON, empty body, and unsupported content-type FastAPI 422 compatibility contract.
- Stable contract fields: type, loc, msg. Excluded version-sensitive input and ctx.
- No DB/env/seed/route/response-body changes.

## v247-v250 admin preview/mutation/diff/rollback safety
- Added static preview side-effect and apply mutation-boundary contracts.
- Added deterministic pure admin diff engine.
- Added detached, fingerprinted rollback snapshot helpers.
- Kept DB, env, seed, routes, schemas, response bodies, auth, and write guards unchanged.

## v250.2 project organization and preview integration

- docs를 current/contracts/handoff/archive 역할로 정리
- smoke 파일을 frontend/contracts/backend/game으로 분류하고 모든 참조 경로 갱신
- backend 계약을 기준으로 frontend extractedFiles/routeContract를 동기화하는 도구 추가
- preview 응답에 optional unifiedDiff/rollbackSnapshot 필드 추가
- 생성/수정/rollback/create-delete/restore 관리자 UI에 공통 Diff 표시
- 기존 API 필드, DB, env, seed, 인증, write guard 변경 없음

## v261-v265.admin-practical-ux-bundle

- 관리자 첫 진입 화면에 처음 사용하는 추천 순서와 버튼 안전도 안내를 추가했습니다.
- 마스터 데이터 카탈로그에 기본 보기/자세히 보기/JSON 보기 프리셋을 추가했습니다.
- 긴 카탈로그 값은 표에서 축약하고 `전체` 버튼으로 모달에서 확인하도록 개선했습니다.
- 관리자 버튼에 조회/Preview/적용주의/고위험 위험도 라벨을 자동 표시합니다.
- 선택한 마스터 데이터 상세 화면에 요약과 다음 행동 안내를 추가했습니다.
- DB/env/seed/auth/route/API body/Write Guard/실제 write 로직은 변경하지 않았습니다.
## v267.next-chat-handoff-ready

- 다음 채팅에서 바로 이어갈 수 있도록 root/docs handoff prompt를 최신 v266 기준으로 정리했습니다.
- 오래된 v250/v260 중심 인계 문구를 v267/Vue-FastAPI-DB 전환 방향으로 갱신했습니다.
- `docs/current/VUE_FASTAPI_DB_TRANSITION_PLAN.md`를 추가했습니다.
- `docs/current/CURRENT_STATUS.md`, `docs/current/ROADMAP.md`, `docs/current/NEXT_STEPS.md`, `README.md`, `README_BACKEND_READY.md`를 최신 방향에 맞게 정리했습니다.
- 런타임 코드, DB, env, seed, 인증, route, API 응답 body, Write Guard, 실제 write 로직은 변경하지 않았습니다.

## v271.vue-readonly-api-client

- Added Vue read-only API client preparation files under `frontend/vue-app/src/api/`.
- Added GET-only route constants for admin/game/health read APIs.
- Added `requestReadOnly` fetch wrapper without write methods.
- Updated AdminShell/GameShell to display prepared GET route lists without auto-calling APIs.
- Added Vue read-only API smoke coverage.
- Updated current docs, handoff docs, and next-step guidance for v272.
- Did not change DB/env/seed/auth/API response body/route paths/write logic/Write Guard/Preview Apply bodies/game content.

## v270.vue-app-basic-shell

- Added a separated Vite + Vue shell under `frontend/vue-app/`.
- Added basic Vue Router routes for `/game` and `/admin` without replacing legacy `index.html` or `admin.html`.
- Added `GameShell.vue`, `AdminShell.vue`, `ShellCard.vue`, and base shell CSS.
- Added Vue shell structure smoke: `tools/smoke/frontend/smoke_vue_shell_structure.py`.
- Added Vue shell smoke runner: `tools/run_smoke_vue_shell.sh`.
- Documented required user install step: `npm install` in `frontend/vue-app`.
- Preserved DB, env, seed, auth, route paths, API response bodies, write guards, write logic, Preview/Apply request bodies, and existing smoke/contract meaning.
## v273.local-dev-cors-vue-fix

- Fixed the local Vue dev server CORS issue reported from `http://127.0.0.1:5173` to `http://127.0.0.1:8000/api/v1/*`.
- Added local/debug fallback CORS origins in `backend/app/core/config.py` so older local `.env` values that omit Vite port `5173` do not block read-only Vue API checks.
- Production CORS behavior remains explicit: production/debug-false settings do not auto-append local dev origins.
- Added `tools/smoke/backend/smoke_backend_local_cors.py` and included it in `tools/run_smoke_core.sh`.
- Added `docs/current/LOCAL_DEV_CORS.md`.
- Did not change `.env`, DB, seed, auth, route paths, API response body, write logic, Write Guard, Preview/Apply request bodies, or game content.



## v293.postgres-restore-rehearsal-execute-tool

- Added `tools/restore_postgres_rehearsal_database.py`.
- Pinned restore source to the exact verified v291 custom archive and SHA-256.
- Required the v292 target DB to exist and remain empty before restore.
- Added single-transaction/exit-on-error pg_restore boundary without create, clean, or drop.
- Added target table/row/table-count/schema-equivalence verification and source before/after checks.
- Added `tools/smoke/backend/smoke_postgres_restore_rehearsal.py` and core smoke registration.
- Updated current/readiness/handoff documentation to v293.
- Did not execute restore in the handoff build environment and did not include local backup artifacts in the ZIP.

## v296.postgres-initial-alembic-revision-placeholder-recovery

- v295 first autogenerate attempt가 만든 empty `alembic_version` placeholder를 정상 recovery state로 분류
- `--inspect-workspace` read-only 진단 추가
- application table/row/revision 존재 시 generation 전 차단
- pristine 0-table DB에서 새 control table 생성 차단
- existing placeholder 재사용 후 revision/autoreview 성공 경계 수정
- PostgreSQL readiness, handoff, smoke, current docs v296 동기화
