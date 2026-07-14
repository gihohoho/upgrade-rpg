# Roadmap — v302

## 완료

- PostgreSQL runtime/schema 동등성 확인
- verified backup 및 isolated restore rehearsal
- empty migration DB 생성
- 최초 Alembic revision 생성·자동/수동 검토
- isolated migration DB `upgrade head`
- 같은 DB `downgrade base`
- 같은 DB 두 번째 `upgrade head`
- 첫/두 번째 upgrade signature 동일 확인
- v301 source baseline stamp read-only preflight 사용자 실제 통과

## 현재

- restore rehearsal DB stamp 전용 v302 guard 준비 완료
- exact target/revision/command boundary 고정
- application schema와 전체 row-content SHA-256 비교 준비
- 실제 stamp 실행은 미승인

## 다음 안전 순서

1. v302 `--inspect` 사용자 실제 결과 확인
2. target `rpg_game_restore_rehearsal_v290` 재확인
3. revision `v295_initial_schema`와 SHA-256 재확인
4. pre-stamp schema/data digests 수집 확인
5. 사용자 별도 승인 후 rehearsal에서만 `stamp head`
6. application schema/data digests 동일 확인
7. `alembic_version` 1 table/1 row만 추가 확인
8. source/migration DB 무변경 확인
9. rehearsal 결과 통과 뒤 원본 source stamp guard 설계
10. 원본 source stamp는 다시 별도 명시 승인

## 계속 금지

- 원본 `rpg_game` upgrade/downgrade/stamp
- restore rehearsal stamp 사전 승인 없는 실행
- migration test DB 추가 변경
- DB create/drop/restore
- `.env`/Docker volume 변경
