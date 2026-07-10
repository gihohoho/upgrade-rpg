# v103 - 개발자 배지 하단 HUD 위 배치

## 목적

`MASTER DATA` 배지와 `SAVE DATA` 배지를 하단 인터페이스 내부가 아니라, 하단 HUD 바로 위쪽에 고정 배치한다.

기존에는 배지가 하단 HUD 안쪽이나 오른쪽 슬롯 근처에 섞여 보여서 스킬칸/버튼과 겹치거나 어색하게 보일 수 있었다.

## 배치 기준

데스크톱 기준:

```txt
[ MASTER DATA ] [ SAVE DATA ]
-----------------------------
        하단 HUD / 스킬칸
```

- `SAVE DATA`: 오른쪽 하단 HUD 위쪽
- `MASTER DATA`: `SAVE DATA` 왼쪽
- 두 배지 모두 `position: fixed`로 화면 기준 배치
- `bottom: 158px` 기준으로 하단 HUD 바로 위에 위치

## 모바일/좁은 화면 처리

폭이 좁아지면 두 배지를 가로로 무리하게 넣지 않고, `MASTER DATA`를 더 위로 올려 세로로 분리한다.

```txt
[ MASTER DATA ]
[ SAVE DATA ]
---------------
하단 HUD
```

## 변경 파일

```txt
src/api/master-data-dev-badge.js
src/api/save-data-dev-badge.js
tools/smoke/game/smoke_master_data_dev_badge.js
tools/smoke/game/smoke_save_data_dev_badge.js
```

## 영향 범위

- 개발자용 배지 위치만 변경한다.
- master-data 로딩, save-data 저장/동기화 로직은 변경하지 않는다.
- DB reset/seed import는 필요 없다.
