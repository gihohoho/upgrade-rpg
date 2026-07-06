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
docs/CSS_AUDIT.md
```


## v069 추가 문서

- `docs/SKILL_DAMAGE_TEXT_FIX.md`: 기존 저장 스킬 데이터가 캐릭터별 스킬 구조로 이관되지 않아 스킬 데미지 텍스트가 안 보일 수 있는 문제와 수정 내용을 설명합니다.


## 4순위 2차 관련 문서

- `docs/KILL_REWARD_RESULT_STAGE2.md`
  - `killEnemy()` 처치/드랍/보상 결과 객체화 내용 정리
- `src/systems/action-result-system.js`
  - `createEnemyKillResult()`, `addDropAward()`, `addRewardGold()`, `addBlockedReward()` 추가
- `src/systems/combat-system.js`
  - `killEnemy()`가 `combat.kill` 결과 객체를 만들고 UI 요청을 모으도록 변경


## v073 결과 객체화 추가 지점

- `src/systems/action-result-system.js`: `item.equip`, `item.unequip`, `skill_book.use`, `boss.summon` 결과 객체 생성 헬퍼와 UI 요청 처리 확장
- `src/systems/item-system.js`: `actionEquipDirect()`, `actionUnequipDirect()` 결과 객체화
- `src/ui/render-ui.js`: `summonBoss()` 결과 객체화
- `docs/EQUIP_SKILL_BOSS_RESULT_STAGE3.md`: 4순위 3차 작업 상세


---

## API 계약 파일

| 파일 | 역할 | 비고 |
|---|---|---|
| `src/api/API_PLAN.md` | FastAPI로 만들 API 목록과 우선순위 | 5순위에서 확정 응답 형태 기준으로 갱신 |
| `src/api/api-response-contract.js` | API 응답 버전, 행동 타입, 에러 코드, 응답 생성 헬퍼 | 현재 `index.html`에서 로드하지 않음. 미래 FastAPI/Vue 연결 기준 |
| `docs/API_RESPONSE_CONTRACT.md` | 서버-프론트 응답 형태 계약서 | FastAPI 구현 전 반드시 참고 |
| `tools/smoke_api_response_contract.js` | 응답 계약 헬퍼/예시 검증 | `node tools/smoke_api_response_contract.js` |


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
