# Next Steps

현재 기준: **v159 admin create blueprint readonly**

v159에서 신규 row 생성 준비 화면을 read-only로 추가했습니다. 실제 생성 적용은 아직 열지 않았습니다.

## 다음 추천 단계

### v160 관리자 생성 draft 입력 UI 준비

바로 insert apply를 열기보다, v159 blueprint를 바탕으로 생성 초안 입력 UI와 preview-only 검증부터 붙이는 단계가 안전합니다.

- blueprint 기반 생성 draft 입력 UI
- code unique 중복 preview 검증
- relation 대상 존재 preview 검증
- combo guard 중복 preview 검증
- 실제 DB insert는 계속 잠금

이 단계도 DB reset/seed 없이 진행 가능합니다.

## 이후 후보

- JSON 편집기 미리보기 전용 UI 준비
- 마스터 데이터 일괄 검색/빠른 이동 패널
- 관리자 도메인별 빠른 프리셋 필터
- change log row 간 빠른 이전/다음 이동
