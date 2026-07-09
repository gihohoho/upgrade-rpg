# Next Steps

## 현재 완료: v195 admin thin entry cleanup

`admin-page-readonly.js`를 마지막 연결 파일처럼 유지하면서 click action 처리, window export 등록, 외부 모듈 configure 순서를 정리했습니다.

## 다음 추천: v196 admin field help/value hints split

다음은 비교적 안전한 읽기 전용 helper 묶음인 **field help / value hints**를 외부 파일로 분리하는 단계가 좋습니다.

추천 방향:

1. 후보 파일 생성: `src/api/admin/admin-field-help.js`
2. field help / value hint / equip slot label helper 이동
3. 기존 window 함수명은 wrapper로 유지
4. `admin-page-readonly.js`는 연결 파일 역할 유지
5. 전용 smoke 추가

## 그다음 후보

v196이 안정적이면 v197 이후 아래 중 하나로 갈 수 있습니다.

- admin common formatter/helper 분리 계약 고정
- write dev key/API base URL helper 분리
- backend admin service 파일 분리 준비

현재 관리자 프론트의 큰 JS 분리는 대부분 끝났으므로, 다음부터는 작은 helper 묶음 위주로 진행하는 게 안전합니다.
