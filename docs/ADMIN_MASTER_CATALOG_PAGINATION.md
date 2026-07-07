# Admin Master Catalog Pagination

현재 기준: **v138 admin safe apply review**

v135에서는 관리자 `마스터 데이터 카탈로그`에 페이지네이션을 추가했습니다.

## 변경 내용

- 기본 표시 개수: 20개
- 기본 정렬: ID순
- 페이지 입력칸 추가
- 처음/이전/다음/끝 이동 버튼 추가
- API 응답에 page, offset, totalPages, hasPrevPage, hasNextPage 추가
- 카탈로그 상단에 현재 표시 범위와 전체 페이지 수 표시

## 슬롯 표시 개선

`equip_slot` 프리셋에서 숫자 슬롯을 `특수 슬롯 6`처럼 보여주지 않고 인게임 장비창 이름으로 표시합니다.

- 6: 특수무기
- 7: 특수목걸이
- 8: 특수반지
- 9: 무기아바타
- 10: 오라아바타
- 11: 클론 레어 아바타
- 12: 탈리스만 A
- 13: 탈리스만 B
- 14: 휘장

## DB reset / seed

필요 없습니다. 이번 단계는 관리자 UI와 조회 API 페이징 중심 변경입니다.
