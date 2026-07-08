# Next Steps

현재 기준: **v162 admin create draft preview**

v162에서 신규 row 생성 초안 입력 UI와 preview-only 검증 API를 추가했습니다. 실제 생성 적용은 아직 열지 않았습니다.

## 다음 추천 단계

### v163 관리자 신규 row 생성 apply 준비

바로 전체 도메인을 insert 가능하게 열기보다는, 가장 안전한 도메인부터 한 개씩 실제 생성 apply를 여는 단계가 좋습니다.

추천 순서:

1. `characters` 또는 `enhancementGroups`처럼 relation 의존도가 낮은 도메인부터 시작
2. 생성 확인 문구 추가
3. admin dev key guard 연결
4. create change log 기록
5. 생성 row 상세 자동 열기
6. rollback은 삭제가 아니라 soft-disabled 또는 별도 안전 정책을 먼저 설계

## 이후 후보

- 생성 apply 전 high risk 추가 확인
- 생성 change log 상세/필터
- JSON 편집기 미리보기 전용 UI
- 마스터 데이터 일괄 검색/빠른 이동 패널
- 관리자 도메인별 빠른 프리셋 필터
