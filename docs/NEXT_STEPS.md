# Next Steps

## 현재 완료: v194 admin bootstrap/bindEvents readiness

`admin-page-readonly.js`에 남은 마지막 entry 역할을 바로 분리하지 않고, bootstrap / bindEvents / window export / event action map 계약으로 먼저 고정했습니다.

## 다음 추천: v195 admin thin entry cleanup

이제 다음은 실제 기능을 크게 옮기기보다는 `admin-page-readonly.js`를 thin entry로 더 깔끔하게 정리하는 단계가 좋습니다.

추천 순서:

1. window export 묶음 정리
2. external module configure 순서 정리
3. readiness aggregation 가독성 정리
4. 기존 window 함수명은 유지
5. `checkAdminReadOnlyPageReady()`와 event action map smoke 유지

## 그다음 후보

v195가 안정적이면 v196부터는 아래 중 하나로 갈 수 있습니다.

- common helper 분리 계약 고정
- field help/value hint 분리
- admin-page-readonly.js wrapper 최종 축소

현재 entry 파일은 관리자 전체 연결 관문이라, 기능 이동보다 smoke를 유지한 정리가 안전합니다.
