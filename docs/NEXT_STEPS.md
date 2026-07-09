# Next Steps

## 현재 완료: v193 admin overview/snapshots split

`overview/snapshots` 구현을 `src/api/admin/admin-overview-snapshots.js`로 1차 분리했습니다.

## 다음 추천: v194 admin bootstrap/bindEvents thin entry readiness

이제 `admin-page-readonly.js`에는 bootstrap, bindEvents, window export, 일부 공통 helper 중심으로 남아 있습니다.

추천 순서:

1. event action map / boot readiness smoke 추가
2. bindEvents 안의 action handler 목록을 진단 가능하게 고정
3. 이후 안정적이면 event handlers 일부를 별도 파일로 분리

바로 큰 분리를 해도 가능하지만, 현재 entry 파일은 모든 외부 모듈을 연결하는 마지막 관문이라 먼저 readiness를 고정하는 편이 안전합니다.
