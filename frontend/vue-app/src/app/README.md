# Vue app 공통 영역

공통 bootstrap은 `src/main.ts`에서 Vue, Pinia, typed Router와 전역 style을 등록합니다. `App.vue`는 반응형 sidebar·진행 상태·공통 header를, route별 page와 component는 계정·관리자·게임 화면을 맡습니다.

게임 UI는 `stores/game.ts`의 표시 상태와 `game/adapters/`의 순수 view model을 사용합니다. 전투 runtime과 server snapshot 저장은 화면 preview 상태에 섞지 않고 각각 controller와 단일 직렬 queue 경계로 연결합니다.

v396의 글자·명암 token은 `styles/base.css`, modal 접근성은 `composables/useModalAccessibility.ts`에서 관리합니다. v397은 `game/save/localRecovery.ts`의 token 없는 저장소 경계와 game store의 복구 선택 gate를 연결합니다. 관리자 helper와 typed API를 재사용하며 v398은 보유 아이템 snapshot과 sparse slot·중복 항목 선택·읽기 전용 정렬을 연결합니다. 다음은 가방↔보관함 이동과 수동 정렬입니다.
