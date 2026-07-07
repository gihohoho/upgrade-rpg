# Next Steps

현재 기준: **v153 admin relation preview tools**

v153에서 변경 preview/초안 비교표의 relation label 표시, relation 대상 빠른 열기, relation 변경 개수 표시를 완료했습니다.

## 다음 추천 단계

### v154 관리자 변경 이력 relation label 강화

현재 편집 전 preview는 relation label이 좋아졌습니다. 다음에는 이미 저장된 change log 상세와 rollback preview에서도 relation 값이 코드만 보이지 않도록 label 표시를 확장하는 것이 좋습니다.

- change log 상세 before/after relation label 표시
- rollback preview relation label 표시
- rollback 대상 열기 버튼 추가
- 기존 rollback guard 유지

이 단계도 DB reset/seed 없이 진행 가능합니다.

## 이후 후보

- 신규 row 생성 기능 준비용 read-only 설계
- JSON 편집기 미리보기 전용 UI 준비
- 마스터 데이터 일괄 검색/빠른 이동 패널
- 관리자 도메인별 빠른 프리셋 필터
