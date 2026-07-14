# Roadmap — v299

## 완료

- PostgreSQL runtime/schema 동등성 확인
- verified backup과 isolated restore rehearsal
- empty migration DB 생성
- 최초 Alembic revision 생성·자동/수동 검토
- isolated migration DB 첫 번째 `upgrade head` 성공

## 현재

- isolated migration DB `downgrade base` 실행·검증

## 다음

1. 같은 DB에서 두 번째 `upgrade head`
2. 첫 upgrade와 두 번째 upgrade의 schema/revision 결과 비교
3. 필요 시 두 번째 downgrade 또는 테스트 DB 보존/삭제 정책 결정
4. 기존 `rpg_game`의 baseline stamp 전략 검토
5. 사용자 별도 승인 전 source DB에는 migration mutation 금지
