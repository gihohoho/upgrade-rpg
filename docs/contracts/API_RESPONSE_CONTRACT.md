# API 응답 형태 확정 문서

이 문서는 5순위 작업의 결과물입니다.

목표는 FastAPI 구현 전에 **서버가 어떤 형태로 응답할지**, 그리고 프론트가 **어떤 필드를 보고 화면을 갱신할지**를 미리 고정하는 것입니다.

현재 게임은 아직 실제 API를 호출하지 않습니다. 대신 v071~v073에서 만든 `Action Result` 구조를 기준으로, 나중에 FastAPI 응답으로 그대로 확장할 수 있는 표준 형태를 정했습니다.

---

## 1. 표준 응답 봉투

모든 유저용 게임 API는 아래 형태를 기본으로 사용합니다.

```js
{
  ok: true,
  responseVersion: "game-api-response.v1",
  type: "combat.attack",
  requestId: "선택값",
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

### 필드 의미

| 필드 | 의미 |
|---|---|
| `ok` | 성공 여부 |
| `responseVersion` | 응답 형태 버전 |
| `type` | 어떤 행동 결과인지 구분하는 값 |
| `requestId` | 요청 추적용 ID. 처음에는 없어도 됨 |
| `serverTime` | 서버 기준 시간 |
| `createdAt` | 결과 생성 시각 timestamp |
| `payload` | 요청에서 들어온 값 중 기록할 필요가 있는 값 |
| `data` | 실제 게임 결과 데이터 |
| `logs` | 게임 로그창에 표시할 메시지 |
| `effects` | 데미지 텍스트, 아이템 드랍 텍스트 같은 화면 효과 요청 |
| `ui` | 프론트가 어느 영역을 갱신해야 하는지 알려주는 힌트 |
| `statePatch` | 서버 반영 후 프론트 상태에 덮어쓸 값 |
| `meta` | 페이지네이션, 마스터 데이터 버전 등 부가 정보 |
| `error` | 실패 시 에러 정보. 성공 시 `null` |

---

## 2. 실패 응답 형태

실패 응답도 같은 구조를 사용하되, `ok: false`와 `error`가 들어갑니다.

```js
{
  ok: false,
  responseVersion: "game-api-response.v1",
  type: "boss.summon",
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
  error: {
    code: "COOLDOWN_ACTIVE",
    message: "특수보스 쿨타임이 아직 남아 있습니다.",
    details: {
      remainingSeconds: 120
    },
    fieldErrors: {}
  }
}
```

### 공통 에러 코드

```txt
UNKNOWN_ERROR
UNAUTHORIZED
FORBIDDEN
NOT_FOUND
VALIDATION_ERROR
CONFLICT
NOT_ENOUGH_GOLD
INVENTORY_FULL
COOLDOWN_ACTIVE
INVALID_STATE
MAX_LEVEL_REACHED
```

---

## 3. 현재 Action Result와의 연결

현재 프론트 내부 결과 객체는 대략 아래 형태입니다.

```js
{
  ok: true,
  type: "item.equip",
  payload: {},
  logs: [],
  effects: [],
  ui: {},
  data: {},
  createdAt: Date.now()
}
```

FastAPI 응답은 여기에 아래 필드를 추가한 확장형으로 보면 됩니다.

```txt
responseVersion
requestId
serverTime
statePatch
meta
error
```

즉, 현재 v071~v073에서 만들어둔 결과 객체는 버리는 구조가 아니라, 그대로 서버 응답으로 확장할 수 있습니다.

---

## 4. 확정된 행동 타입

```txt
game.load
game.save
game.master_data

combat.attack
combat.kill
boss.summon

item.equip
item.unequip
item.enhance
item.move_storage
item.move_trash
item.empty_trash

skill_book.use

mailbox.list
mailbox.claim
mailbox.claim_all

admin.change
```

---

## 5. 주요 API별 응답 형태

## 5-1. `GET /game/load`

역할:

```txt
Bearer 계정이 소유한 선택 캐릭터의 서버 저장 데이터를 불러옵니다.
```

필수 query는 `slotKey=character-1..8`과 32자리 `accountCharacterId`입니다. 서버는
Bearer 계정·슬롯 키·캐릭터 ID가 모두 일치하는지 확인합니다.

응답:

```js
{
  ok: true,
  responseVersion: "game-api-response.v1",
  type: "game.load",
  requestId: "...",
  payload: {
    status: "loaded",
    exists: true,
    userId: 7,
    slotKey: "character-2",
    slotIndex: 2,
    accountCharacterId: "32자리 캐릭터 ID",
    accountCharacter: {
      id: "32자리 캐릭터 ID",
      slotIndex: 2,
      name: "캐릭터 이름",
      characterCode: "weapon_master",
      createdAt: "2026-09-01T00:00:00Z"
    },
    clientSaveKey: "character-2",
    saveVersion: 5,
    snapshot: {
      saveVersion: 5,
      player: {},
      currentZoneIndex: 0,
      currentZoneType: "field",
      fieldEnemyHp: {},
      fieldRespawnEndAt: {}
    },
    summary: {},
    source: "localStorage",
    note: null,
    integrity: { ok: true, warnings: [] },
    createdAt: "2026-09-01T00:00:00Z",
    updatedAt: "2026-09-04T00:00:00Z"
  },
  data: {
    status: "loaded",
    userId: 7,
    slotKey: "character-2",
    accountCharacterId: "32자리 캐릭터 ID",
    exists: true,
    integrity: { ok: true, warnings: [] }
  },
  meta: { source: "postgresql" },
  error: null
}
```

프론트 처리:

```txt
v394 Vue는 data와 payload의 slotKey/accountCharacterId, payload의 characterCode를
현재 선택과 다시 대조한 뒤 payload.snapshot만 typed server state로 normalize/apply합니다.
빈 snapshot {}은 신규 기본 상태로 허용합니다. 401/403은 로그인으로 돌아가고,
network/timeout/5xx와 계약 오류는 token·캐릭터 선택을 유지한 재시도 화면으로 처리합니다.
이 GET 처리에서 save POST, Gold/아이템 보상, 난수와 revision write를 실행하지 않습니다.
```

---

## 5-2. `POST /game/save`

역할:

```txt
현재 `gameState.server` 기준 저장 데이터를 서버에 저장합니다.
```

응답:

```js
{
  ok: true,
  type: "game.save",
  data: {
    savedAt: "2026-07-06T00:00:00.000Z",
    saveVersion: 5
  },
  logs: [
    { message: "저장되었습니다.", important: false }
  ]
}
```

---

## 5-3. `GET /game/master-data`

역할:

```txt
캐릭터, 스킬, 아이템, 보스, 필드, 드랍, 강화 규칙 같은 공통 데이터를 내려줍니다.
```

응답:

```js
{
  ok: true,
  type: "game.master_data",
  data: {
    version: "2026-07-06.1",
    characters: [],
    skills: [],
    skillBooks: [],
    itemTemplates: [],
    bosses: [],
    specialBosses: [],
    fieldZones: [],
    dropTables: [],
    enhancementRules: []
  },
  meta: {
    cacheSeconds: 300
  }
}
```

관리자 페이지도 이 마스터 데이터와 같은 DB를 사용해야 합니다.

---

## 5-4. `POST /battle/attack`

역할:

```txt
공격 1회 결과를 서버에서 계산합니다.
```

응답:

```js
{
  ok: true,
  type: "combat.attack",
  data: {
    target: {
      kind: "field",
      name: "필드 몬스터",
      hpBefore: 100000,
      hpAfter: 0
    },
    totalDamage: 123456,
    normalDamage: 100000,
    skillHits: [
      { label: "[W]", damage: 23456 }
    ],
    killed: true,
    killResult: null
  },
  effects: [
    { type: "damageText", text: "[W] 23,456", extraClass: "skill-damage" }
  ],
  ui: {
    updateCombatUI: true
  },
  statePatch: {
    combat: {
      enemyHp: 0
    }
  }
}
```

처치까지 발생하면 `killResult`에 `combat.kill` 구조를 넣거나, 별도 `POST /boss/attack` 응답에서 `combat.kill`을 이어서 반환할 수 있습니다.

---

## 5-5. `combat.kill`

역할:

```txt
필드 몬스터 또는 보스 처치 결과입니다.
```

응답 예시:

```js
{
  ok: true,
  type: "combat.kill",
  data: {
    target: "boss",
    drops: [
      {
        itemName: "심연의 편린 스태프",
        dropType: "equipment",
        stacked: false,
        stored: false
      }
    ],
    rewards: {
      gold: 0
    },
    transition: {
      bossCleared: true,
      returnToField: true
    }
  },
  logs: [
    { message: "심연의 편린 스태프 획득!", important: true }
  ],
  effects: [
    { type: "itemDropText", itemName: "심연의 편린 스태프" }
  ],
  ui: {
    renderUI: true
  }
}
```

---

## 5-6. `POST /item/equip`

응답:

```js
{
  ok: true,
  type: "item.equip",
  data: {
    itemInstanceId: "item_123",
    itemName: "심연의 편린 스태프",
    slotType: "weapon",
    slotIndex: 0,
    replacedItemInstanceId: null,
    splitFromStack: false
  },
  logs: [
    { message: "심연의 편린 스태프 장착", important: false }
  ],
  ui: {
    updateFullUI: true,
    closeActionPanel: true
  },
  statePatch: {
    equipment: {},
    inventory: {}
  }
}
```

---

## 5-7. `POST /item/unequip`

응답:

```js
{
  ok: true,
  type: "item.unequip",
  data: {
    itemInstanceId: "item_123",
    itemName: "심연의 편린 스태프",
    slotIndex: 0,
    movedToInventory: true,
    stacked: false
  },
  ui: {
    updateFullUI: true,
    closeActionPanel: true
  },
  statePatch: {
    equipment: {},
    inventory: {}
  }
}
```

---

## 5-8. `POST /item/enhance`

응답:

```js
{
  ok: true,
  type: "item.enhance",
  data: {
    itemInstanceId: "item_123",
    itemName: "초월 탈리스만",
    beforeLevel: 2,
    afterLevel: 3,
    attempts: 1,
    successCount: 1,
    failCount: 0,
    goldSpent: 0,
    materialSpent: []
  },
  logs: [
    { message: "강화 성공", important: false }
  ],
  ui: {
    updateFullUI: true,
    enhanceResult: {
      title: "강화 결과",
      rows: [],
      goldSpent: 0
    }
  },
  statePatch: {
    inventory: {},
    equipment: {},
    player: {
      gold: 100000
    }
  }
}
```

---

## 5-9. `POST /skill/use-book`

응답:

```js
{
  ok: true,
  type: "skill_book.use",
  data: {
    itemInstanceId: "book_123",
    itemName: "-초월- 심연의 스킬강화권",
    characterId: "weapon_master",
    skillKey: "ironStrike",
    beforeLevel: 3,
    afterLevel: 4,
    beforeCount: 2,
    afterCount: 1,
    awakened: false
  },
  logs: [
    { message: "스킬 레벨이 상승했습니다.", important: false }
  ],
  ui: {
    renderSkills: true,
    updateFullUI: true,
    closeActionPanel: true
  },
  statePatch: {
    userCharacters: {},
    inventory: {}
  }
}
```

---

## 5-10. `POST /boss/summon`

응답:

```js
{
  ok: true,
  type: "boss.summon",
  data: {
    bossId: "boss_12",
    bossName: "12단계 보스",
    isSpecialBoss: false,
    hp: 100000000,
    maxHp: 100000000,
    transition: {
      currentZoneType: "boss",
      startAutoAttack: true
    }
  },
  ui: {
    closeBossPanel: true,
    updateCombatUI: true,
    startAutoAttack: true
  },
  statePatch: {
    combat: {
      currentBossId: "boss_12",
      currentBossHp: 100000000
    }
  }
}
```

---

## 6. 관리자 API 응답 형태

관리자 API도 기본 응답 봉투는 같습니다. 단, 관리자 변경은 반드시 `adminChangeLogId` 또는 변경 이력 정보를 포함해야 합니다.

```js
{
  ok: true,
  type: "admin.change",
  data: {
    targetType: "item_template",
    targetId: "abyss_staff",
    action: "update",
    before: {},
    after: {},
    adminChangeLogId: 1001
  },
  logs: [
    { message: "아이템 정보가 수정되었습니다.", important: false }
  ]
}
```

관리자 페이지에서 수정 가능한 값은 DB에 저장하고, 기존 코드처럼 JS 파일에 직접 박아두지 않는 방향으로 갑니다.

---

## 7. 화면 효과는 서버 판정과 분리

서버는 게임 결과를 판정하고, 프론트는 화면 효과를 표시합니다.

예:

```txt
서버: W 스킬이 발동했고 23,456 데미지를 줬다.
프론트: 그 결과를 받아서 데미지 텍스트를 몬스터 옆에 띄운다.
```

그래서 `effects`는 게임 결과가 아니라 **표시 요청**입니다.

```js
{
  type: "damageText",
  text: "[W] 23,456",
  extraClass: "skill-damage"
}
```

---

## 8. statePatch 원칙

서버가 모든 유저 상태를 매번 통째로 내려주면 무겁습니다. 그래서 변경된 부분만 `statePatch`로 내려주는 방향을 추천합니다.

예:

```js
statePatch: {
  player: {
    gold: 123456
  },
  inventory: {
    changedSlots: [0, 3, 8]
  },
  combat: {
    currentBossHp: 0
  }
}
```

초기 FastAPI 구현에서는 단순하게 전체 상태를 내려줘도 됩니다. 다만 장기적으로는 `statePatch` 방식이 더 좋습니다.

---

## 9. 이번 5순위에서 브라우저 확인이 거의 없는 이유

이번 작업은 화면/전투 동작을 바꾸는 작업이 아니라, API 응답 계약을 확정하는 작업입니다.

따라서 브라우저에서 확인할 항목은 없습니다.

대신 확인해야 할 것은 아래입니다.

```txt
응답 타입이 현재 Action Result 타입과 맞는지
FastAPI로 옮길 때 필요한 성공/실패 형태가 있는지
관리자 페이지 변경 이력까지 포함 가능한지
프론트 UI 표시 요청을 effects/ui로 표현할 수 있는지
```

이 부분은 문서와 smoke 테스트로 확인합니다.
