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
