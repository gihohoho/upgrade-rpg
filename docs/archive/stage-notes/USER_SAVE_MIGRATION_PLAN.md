# User Save Migration Plan

## 단계

1. 원본 localStorage snapshot을 DB에 저장한다. 현재 단계.
2. 브라우저 수동 저장 시 localStorage + backend snapshot 동시 저장 옵션을 붙인다.
3. backend snapshot을 불러와서 기존 `applyServerSavePayload()`로 적용하는 실험 모드를 만든다.
4. 아이템 인스턴스, 인벤토리 슬롯, 장비 슬롯, 스킬 레벨, 우편함을 정규화 테이블로 나눈다.
5. 정규화 저장이 안정화되면 snapshot은 백업/롤백 용도로만 남긴다.

## 왜 snapshot부터 하는가

현재 저장 데이터는 게임 로직과 강하게 연결되어 있다. 바로 정규화하면 작은 필드 하나 누락으로도 진행 데이터가 깨질 수 있다. 그래서 먼저 원본 저장값을 그대로 백엔드에 보관해서 복구 가능한 상태를 만든다.
