# Vue Pinia store

v379부터 Pinia를 공통 상태 관리 기준으로 사용합니다.

- `app.ts`: navigation과 Vue 전환 단계처럼 앱 전체에서 공유하는 UI 상태
- 계정, 캐릭터, 게임 runtime은 기능을 이식할 때 각각 별도 store로 추가
- 서버 snapshot과 저장 revision은 임의의 UI 상태와 섞지 않음
- component 안에서 직접 전역 객체를 만들지 않음

기존 `src/state/`를 한 번에 복사하지 않고, 기능별 계약과 회귀 검사를 확인하면서 typed store 또는 Vue 독립 domain module로 나눕니다.
