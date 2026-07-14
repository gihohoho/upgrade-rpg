# Roadmap — v304

## 완료

- PostgreSQL runtime/schema 동등성 확인
- verified backup 및 isolated restore rehearsal
- empty migration DB 생성
- 최초 Alembic revision 생성·자동/수동 검토
- isolated migration DB `upgrade head -> downgrade base -> upgrade head`
- first/second upgrade signatures identical
- v301 source baseline preflight 통과
- v302 rehearsal `stamp head` 실행 및 검증
- v303 rehearsal post-check 및 v302 report verified

## 현재

- source DB 전용 v304 final guard 준비 완료
- exact target/revision/backup/rehearsal result confirmation 고정
- source/rehearsal 전체 application schema/data digest 비교
- 실제 source stamp는 미승인

## 다음 안전 순서

1. v304 source `--inspect` 실제 결과 확인
2. target `rpg_game` 재확인
3. revision과 SHA-256 재확인
4. backup SHA-256 및 로컬 evidence 재확인
5. rehearsal report verified 및 migration endpoint 재확인
6. source/rehearsal application digests 동일 확인
7. 사용자 별도 승인 후 source에서만 `stamp head`
8. source application digests 동일 확인
9. `alembic_version` 1 table/1 row만 추가 확인
10. rehearsal/migration DB 무변경 확인
11. source post-check와 v304 report 검증

## 계속 금지

- 승인 없는 source stamp
- source upgrade/downgrade
- rehearsal stamp 재실행
- migration test DB 추가 변경
- DB create/drop/restore
- `.env`/Docker volume 변경
