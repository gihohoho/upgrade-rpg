# Runtime stacked enhance space guard

## 목적

v124에서 DB `itemTemplates.stackable=true` 아이템을 신규 획득 시 인게임에서 겹치도록 연결했다.
이후 겹쳐진 장비를 강화할 때는 1개만 분리해 강화해야 하므로, 가방/보관함이 꽉 찬 상태에서는 강화가 진행되면 안 된다.

v125에서는 이 규칙을 일반 stackable 장비뿐 아니라 탈리스만/빛나는 휘장 같은 특수 stackable 장비에도 동일하게 적용한다.

## 동작

- `count <= 1` 아이템은 기존 강화 흐름을 유지한다.
- `count > 1`인 겹친 장비를 강화하려면 현재 위치한 컨테이너에 빈 칸이 1칸 필요하다.
- 인벤토리에서 선택한 아이템은 `player.inventory.length < player.maxInventorySize`일 때만 분리 강화 가능하다.
- 보관함에서 선택한 아이템은 `player.storage.length < player.maxStorageSize`일 때만 분리 강화 가능하다.
- 가방/보관함이 꽉 찬 상태라면 강화 전에 중단하고 안내 문구를 표시한다.

## 적용 대상

- DB `stackable=true`로 겹쳐진 일반 장비
- 탈리스만 스택
- 빛나는 휘장 스택

## 안내 문구

```txt
[시스템] 겹쳐진 장비를 강화하려면 먼저 1칸의 빈 공간이 필요합니다.
```

## DB 변경 여부

DB reset/seed 불필요.
런타임 강화 로직만 수정한다.
