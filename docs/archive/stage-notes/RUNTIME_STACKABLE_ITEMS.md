# Runtime Stackable Items

## v124 목적

관리자 페이지에서 바꾼 `itemTemplates.stackable` 값을 인게임 신규 획득 아이템 겹치기 로직에 연결했습니다.

이전 상태:

```txt
관리자 stackable=true
→ DB 값 변경됨
→ master-data API로 내려옴
→ 하지만 인게임 신규 장비 획득 시에는 아직 별도 슬롯으로 들어감
```

v124 이후:

```txt
관리자 stackable=true
→ DB 값 변경됨
→ master-data API로 내려옴
→ 보스 드랍 아이템에 stackable=true 런타임 필드가 붙음
→ 신규 획득 시 같은 +0 아이템은 count로 겹침
```

## 적용 범위

- 신규 보스 드랍 장비부터 적용합니다.
- 기존 세이브 전체를 자동 병합하지 않습니다.
- 새로 획득한 `stackable=true` 아이템이 기존 세이브의 같은 +0 아이템과 만나면 그 슬롯에 겹치고, 기존 아이템에도 `stackable=true`를 보강합니다.
- `stackable=false` 아이템은 기존처럼 슬롯을 각각 차지합니다.

## 강화 안전장치

일반 장비가 `stackable=true`이고 count가 2개 이상인 상태에서 강화하면, 스택 전체가 한 번에 강화되지 않도록 1개만 분리해서 강화합니다.

단, 스택에서 1개를 분리하려면 인벤토리/보관함에 빈 칸이 1칸 필요합니다.

## 장착 안전장치

겹쳐진 일반 장비를 장착하면 1개만 장착하고, 나머지 수량은 기존 슬롯에 남습니다.

## 표시

인벤토리/보관함/휴지통 슬롯 배지는 일반 장비도 `count > 1`이면 `xN`을 표시합니다.

예:

```txt
샤이닝 인텔리전스 x3
```

## DB reset / seed 필요 여부

필요 없습니다.

DB 구조 변경 없이 기존 `itemTemplates.stackable` 값을 런타임에서 사용합니다.
