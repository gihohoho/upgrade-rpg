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
