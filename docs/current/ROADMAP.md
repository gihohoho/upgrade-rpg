# Roadmap — v301

## 완료

- PostgreSQL runtime/schema 동등성 확인
- verified backup 및 isolated restore rehearsal
- empty migration DB 생성
- 최초 Alembic revision 생성·자동/수동 검토
- isolated migration DB `upgrade head`
- 같은 DB `downgrade base`
- 같은 DB 두 번째 `upgrade head`
- 첫/두 번째 upgrade signature 동일 확인

## 현재

- source baseline stamp 읽기 전용 preflight
- source 22 tables / 748 rows / differences=0 / no Alembic 재확인
- backup/revision/round-trip evidence 고정 확인

## 다음 안전 순서

1. v301 preflight 사용자 실제 결과 확인
2. restore rehearsal DB stamp 전용 v302 guard 준비
3. 사용자 별도 승인 후 restore rehearsal에서만 `stamp head`
4. stamp 전후 application schema/data 무변경과 Alembic row 1개 추가 확인
5. 필요 시 rehearsal stamp 상태 보존/정리 정책 결정
6. 원본 source stamp 전용 guard 설계
7. 원본 source stamp는 다시 별도 명시 승인

## 계속 금지

- 원본 `rpg_game` upgrade/downgrade/stamp
- restore rehearsal stamp 사전 승인 없는 실행
- DB create/drop/restore
- `.env`/Docker volume 변경
