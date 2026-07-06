# API 분리 계획

이 문서는 현재 HTML/JS 게임을 FastAPI 백엔드로 옮길 때 필요한 API 단위를 정리한 문서입니다.

5순위 작업에서 API 응답 형태를 아래 문서로 확정했습니다.

```txt
docs/API_RESPONSE_CONTRACT.md
src/api/api-response-contract.js
```

앞으로 FastAPI 구현, Vue 프론트 연결, 관리자 페이지 API는 위 응답 계약을 기준으로 맞춥니다.

---

## 0. 공통 응답 원칙

모든 게임 API는 아래 공통 봉투를 사용합니다.

```js
{
  ok: true,
  responseVersion: "game-api-response.v1",
  type: "combat.attack",
  requestId: null,
  serverTime: "2026-07-06T00:00:00.000Z",
  createdAt: 1780000000000,
  payload: {},
  data: {},
  logs: [],
  effects: [],
  ui: {},
  statePatch: {},
  meta: {},
  error: null
}
```

실패 시에는 `ok: false`와 `error`를 사용합니다.

---

## 1. 마스터 데이터

```txt
GET /game/master-data
```

서버가 내려줄 데이터:

```txt
캐릭터 목록
스킬 목록
스킬강화권 목록
아이템 원본 목록
보스 목록
특수보스 목록
필드존 목록
드랍 테이블
강화 규칙
마스터 데이터 버전
```

응답 타입:

```txt
game.master_data
```

이 API는 관리자 페이지와 일반 게임 화면이 같은 데이터를 보게 만드는 핵심입니다.

---

## 2. 저장 / 불러오기

```txt
GET /game/load
POST /game/save
```

저장 대상:

```txt
gameState.server
```

저장하지 않는 대상:

```txt
gameState.client
gameState.runtime 대부분
```

응답 타입:

```txt
game.load
game.save
```

---

## 3. 전투

```txt
POST /battle/attack
```

서버가 계산해야 할 것:

```txt
실제 데미지
스킬 발동 여부
몬스터 남은 체력
처치 여부
필드 리젠 시간
공격속도 성장
골드 획득
기록 갱신
```

응답 타입:

```txt
combat.attack
combat.kill
```

처치가 발생하면 `combat.attack` 응답 안에 `killResult`를 포함하거나, 서버 구현 방식에 따라 `combat.kill` 결과를 이어서 반환합니다.

---

## 4. 보스

```txt
POST /boss/summon
POST /boss/attack
```

서버가 계산해야 할 것:

```txt
보스 소환 가능 여부
보스 체력
보스 처치 여부
장비 드랍
스킬강화권 드랍
최초 장비 드랍 보너스
특수보스 쿨타임
기록 갱신
```

응답 타입:

```txt
boss.summon
combat.attack
combat.kill
```

---

## 5. 아이템

```txt
POST /item/equip
POST /item/unequip
POST /item/enhance
POST /item/discard
POST /item/move-storage
POST /item/move-trash
POST /item/empty-trash
```

서버가 판단해야 할 것:

```txt
장착 가능 슬롯
장착중 아이템 버리기 방지
강화 비용
강화 성공 확률
강화 재료 소모
보관함/인벤토리 공간
휴지통 비우기 가능 여부
```

응답 타입:

```txt
item.equip
item.unequip
item.enhance
item.move_storage
item.move_trash
item.empty_trash
```

---

## 6. 스킬

```txt
POST /skill/use-book
```

서버가 판단해야 할 것:

```txt
스킬강화권 사용 가능 여부
현재 캐릭터의 스킬인지 여부
스킬 레벨 최대치
각성 가능 여부
아이템 수량 차감
```

응답 타입:

```txt
skill_book.use
```

---

## 7. 우편

```txt
GET /mailbox
POST /mailbox/{mailId}/claim
POST /mailbox/claim-all
```

서버가 판단해야 할 것:

```txt
우편 존재 여부
보상 수령 여부
인벤토리 공간
골드 지급
아이템 지급
중복 수령 방지
```

응답 타입:

```txt
mailbox.list
mailbox.claim
mailbox.claim_all
```

---

## 8. 관리자 API

관리자 페이지에서 사용할 API입니다.

```txt
GET /admin/items
POST /admin/items
PATCH /admin/items/{id}

GET /admin/bosses
POST /admin/bosses
PATCH /admin/bosses/{id}

GET /admin/drop-tables
PATCH /admin/drop-tables/{id}

GET /admin/field-zones
PATCH /admin/field-zones/{id}

GET /admin/enhancement-rules
PATCH /admin/enhancement-rules/{id}

GET /admin/characters
POST /admin/characters
PATCH /admin/characters/{id}

GET /admin/skills
POST /admin/skills
PATCH /admin/skills/{id}
```

관리자 API는 반드시 변경 이력을 남겨야 합니다.

```txt
admin_change_logs
```

응답 타입:

```txt
admin.change
```

---

## 9. 다음 구현 기준

FastAPI 구현 시 우선순위는 아래 순서가 좋습니다.

```txt
1. GET /game/master-data
2. GET /game/load
3. POST /game/save
4. POST /item/equip / unequip / enhance
5. POST /skill/use-book
6. POST /boss/summon
7. POST /battle/attack
8. 관리자 API
```
