# Vue Game Domain Dependencies — v384

이 문서는 legacy 게임 계산을 Vue UI에서 분리하기 위한 정적 의존성 목록입니다. 생성기는 source를 읽기만 하며 게임, backend, DB, 배포를 변경하지 않습니다.

## 범위와 결과

- legacy JavaScript: **8개 / 3,481줄 / named function 163개**
- 직접 browser 의존: `window` 15회, `document` 19회, storage 0회
- 비결정적 runtime 의존: `Math.random()` 21회, `Date.now()` 14회, timer API 12회
- 판단: 계산과 DOM·timer·난수가 섞인 파일을 통째로 Vue store로 옮기지 않고, 순수 계산과 상태 전이부터 typed domain으로 분리합니다.

## 파일별 경계

| legacy source | 줄 | 함수 | window | document | random | clock | timer | 역할 | v384 분리 | 남은 adapter 의존 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `src/state/game-state.js` | 373 | 20 | 3 | 0 | 0 | 0 | 0 | state + compatibility | 기본 server/client/runtime state, normalize, save payload, slot 계산 | `window` alias와 legacy 선택 캐릭터 hook |
| `src/systems/action-result-system.js` | 179 | 18 | 0 | 0 | 0 | 1 | 0 | result + UI adapter | result/log/effect/UI 요청 조립 | 현재 시각 생성과 DOM/UI effect 적용 |
| `src/systems/combat-system.js` | 654 | 24 | 6 | 6 | 12 | 7 | 12 | combat + runtime + UI | 공격속도/기본공격 계산, 필드 HP·respawn 전이, 위치 clamp | 난수, timer, 현재 시각, 전투 orchestration과 DOM |
| `src/systems/item-system.js` | 1206 | 49 | 0 | 13 | 6 | 5 | 0 | inventory + item + UI | 빈 칸 유지·배치·비우기·정렬 slot 계산 | drop/enhance 난수·시각, 전역 player/data와 DOM |
| `src/systems/stat-system.js` | 814 | 40 | 6 | 0 | 1 | 0 | 0 | stat + seed lookup | 공격속도 clamp·기본 공격력·큰 수 표기 | 전역 player/data, 난수 stat 생성과 test flag |
| `src/rules/abyss-fragment-rules.js` | 49 | 2 | 0 | 0 | 0 | 0 | 0 | rule + seed mutation | 심연의 편린 이름별 특수 능력치 | 전역 special boss seed 순회·변경 |
| `src/rules/boss-display-rules.js` | 55 | 2 | 0 | 0 | 0 | 0 | 0 | display mutation | 이번 단계 이전 없음 | 전역 boss seed와 이미지 helper를 이용한 표시 후처리 |
| `src/rules/boss-drop-rules.js` | 151 | 8 | 0 | 0 | 2 | 1 | 0 | drop rule + award orchestration | 일반 보스 스킬 드랍률과 최초 장비 보너스 대상 판정 | 난수·시각, 전역 player/inventory/기록/UI |

숫자는 source text의 직접 호출·참조 횟수입니다. 전역 `player`, seed 목록, UI helper처럼 선언 위치가 다른 암묵적 전역은 마지막 두 열에서 역할 단위로 기록했습니다.

## v384 typed domain

- `frontend/vue-app/src/game/domain/action-result.ts`
- `frontend/vue-app/src/game/domain/combat-math.ts`
- `frontend/vue-app/src/game/domain/field-state.ts`
- `frontend/vue-app/src/game/domain/inventory-slots.ts`
- `frontend/vue-app/src/game/domain/rules.ts`
- `frontend/vue-app/src/game/domain/state.ts`
- `frontend/vue-app/src/game/domain/types.ts`

고정한 경계:

1. domain은 Vue, Pinia, Router를 import하지 않습니다.
2. domain은 `window`, `document`, storage, fetch를 직접 사용하지 않습니다.
3. 난수와 현재 시각은 계산 함수 안에서 생성하지 않고 호출자가 값으로 주입합니다.
4. slot/state 전이는 입력 배열·객체를 직접 바꾸지 않고 새 값을 반환합니다.
5. legacy state·UI·timer는 아직 교체하지 않으며 다음 UI 단계가 adapter를 통해 이 domain을 호출합니다.

## 동등성 기준

- 기본 player/server/client/runtime state와 save payload shape
- 인벤토리·보관함·휴지통의 빈 칸 유지, 첫 빈 칸, 비우기, 수동 정렬
- 공격속도 clamp와 기본 공격력, 큰 수 표기, 기본 공격 피해식
- 필드 respawn 만료 시 HP 복구
- 보스 스킬 드랍률, 최초 장비 보너스 대상, 심연의 편린 특수 능력치
- action result/log/effect/UI request shape

검사는 고정 입력을 legacy 함수와 typed domain에 각각 넣어 JSON 결과를 비교합니다. 난수와 시각은 표본값을 주입해 결정론적으로 검사합니다.

## 생성·검사

```bash
python tools/report_vue_game_domain_dependencies.py
python tools/report_vue_game_domain_dependencies.py --check
node tools/smoke/frontend/smoke_vue_game_domain_foundation.js
```

## 다음 안전 단계

`next safe stage: migrate-vue-game-inventory-equipment-ui-foundation`

v387에서 보스 전투 UI와 rule adapter를 연결했습니다. 다음은 실제 item write 없이 인벤토리·장비 UI와 slot adapter 기반을 준비하며, legacy 공개 화면, 저장 load/save, 전투 timer, 관리자 Apply, DB write와 production 배포는 변경하지 않습니다.
