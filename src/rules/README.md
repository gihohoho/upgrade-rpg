# src/rules 구조

게임 규칙을 데이터 파일에서 분리하기 위한 폴더입니다.

## 현재 파일

| 파일 | 역할 | 최종 이전 방향 |
| --- | --- | --- |
| `abyss-fragment-rules.js` | 심연의 편린 특수장비 옵션 부여 | item option DB / FastAPI item service |
| `boss-display-rules.js` | 보스 표시용 후처리 | Vue 표시 로직 또는 프론트 유틸 |
| `boss-drop-rules.js` | 드랍률 보정, 최초 장비 보너스 | FastAPI battle/drop service |

## 주의

`boss-drop-rules.js`는 아직 `player`, `addLog`, `showItemDropText`, `addStackableItemToInventory` 같은 프론트 전역에 의존합니다. 이번 단계는 파일 분리까지가 목표이고, 전역 의존 제거는 4순위 작업에서 진행합니다.
