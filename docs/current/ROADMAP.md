# Roadmap — v300

## 완료

- PostgreSQL runtime/schema 동등성 확인
- verified backup과 isolated restore rehearsal
- empty migration DB 생성
- 최초 Alembic revision 생성·자동/수동 검토
- isolated migration DB 첫 번째 `upgrade head` 성공
- 같은 DB `downgrade base` 성공

## 현재

- 같은 isolated migration DB의 두 번째 `upgrade head`
- 첫 번째와 두 번째 upgrade schema/revision signature 비교

## 다음

1. 왕복 결과 보고서 검토
2. migration 테스트 DB 보존/삭제 정책 결정
3. existing source DB baseline stamp 전용 read-only preflight 설계
4. source DB에 `stamp`를 적용할지 별도 승인
5. 사용자 승인 전 source DB에는 upgrade/downgrade/stamp 금지
