# Next Steps

현재 기준: **v156 admin change log relation tools**

v156에서 저장된 change log 상세와 rollback preview까지 relation label/대상 열기 표시를 확장했습니다.

## 다음 추천 단계

### v157 관리자 신규 row 생성 준비용 read-only 설계

바로 생성 기능을 열기보다, 먼저 도메인별 생성 가능 필드/필수 필드/관계 후보를 읽기 전용으로 보여주는 설계 단계가 안전합니다.

- 도메인별 create blueprint 조회
- 필수 필드/기본값 표시
- relation select 후보 표시
- 실제 DB insert는 아직 잠금
- smoke로 생성 준비 UI만 검증

이 단계도 DB reset/seed 없이 진행 가능합니다.

## 이후 후보

- JSON 편집기 미리보기 전용 UI 준비
- 마스터 데이터 일괄 검색/빠른 이동 패널
- 관리자 도메인별 빠른 프리셋 필터
- change log row 간 빠른 이전/다음 이동
