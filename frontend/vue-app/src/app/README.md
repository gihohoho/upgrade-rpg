# Vue app 공통 영역

v272에서는 실제 공통 bootstrap 로직을 넣지 않습니다.

현재 API 상태 확인은 `components/ReadOnlyApiStatusPanel.vue`에서 화면 단위로 처리합니다.
나중에 app provider, 전역 layout, 실제 API status 초기화가 필요할 때 이 폴더를 사용합니다.
