# FastAPI API Routes 초안

## 시스템

```txt
GET /api/v1/health
```

## 게임 데이터

```txt
GET  /api/v1/game/master-data
GET  /api/v1/game/load
POST /api/v1/game/save
```

## 전투/보스

```txt
POST /api/v1/battle/attack
POST /api/v1/battle/kill
POST /api/v1/boss/summon
POST /api/v1/boss/attack
```

## 아이템

```txt
POST /api/v1/item/equip
POST /api/v1/item/unequip
POST /api/v1/item/enhance
POST /api/v1/item/move-storage
POST /api/v1/item/move-trash
POST /api/v1/item/empty-trash
```

## 스킬강화권

```txt
POST /api/v1/skill-book/use
```

## 우편함

```txt
GET  /api/v1/mailbox
POST /api/v1/mailbox/{message_id}/claim
POST /api/v1/mailbox/claim-all
```

## 관리자 V1

```txt
GET   /api/v1/admin/requirements
GET   /api/v1/admin/items
POST  /api/v1/admin/items
PATCH /api/v1/admin/items/{code}

GET   /api/v1/admin/bosses
POST  /api/v1/admin/bosses
PATCH /api/v1/admin/bosses/{code}

GET   /api/v1/admin/drop-tables
POST  /api/v1/admin/drop-tables
PATCH /api/v1/admin/drop-tables/{code}

GET   /api/v1/admin/field-zones
PATCH /api/v1/admin/field-zones/{code}

GET   /api/v1/admin/enhancement-groups
PATCH /api/v1/admin/enhancement-groups/{code}

GET   /api/v1/admin/characters
POST  /api/v1/admin/characters
PATCH /api/v1/admin/characters/{code}

GET   /api/v1/admin/skills
POST  /api/v1/admin/skills
PATCH /api/v1/admin/skills/{code}

POST  /api/v1/admin/change-preview
POST  /api/v1/admin/change-apply
POST  /api/v1/admin/change-rollback/{change_log_id}
GET   /api/v1/admin/change-logs
```

## 구현 순서 추천

```txt
1. health
2. game.master-data
3. game.load/save
4. admin requirements/change-preview
5. admin items/bosses/drop-tables
6. item equip/unequip/enhance
7. boss summon/combat/drop
```
