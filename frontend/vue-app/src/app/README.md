# Vue app 공통 영역

v391의 공통 bootstrap은 `src/main.ts`에서 Vue, Pinia, typed Router와 전역 style을 등록합니다. `App.vue`는 반응형 sidebar·진행 상태·공통 header를, route별 page와 component는 계정·관리자·게임 화면을 맡습니다.

게임 UI는 `stores/game.ts`의 표시 상태와 `game/adapters/`의 순수 view model을 사용합니다. 전투 runtime과 server snapshot 저장은 화면 preview 상태에 섞지 않고 각각 controller와 단일 직렬 queue 경계로 연결합니다.
