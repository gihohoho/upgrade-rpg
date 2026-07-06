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

