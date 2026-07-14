# Next Steps — v294

## 완료

- schema equivalence 차이 0개
- verified custom backup 생성
- restore rehearsal DB 생성
- verified restore 완료
- restore DB 22 tables / 748 rows / differences=0
- source before/after 동일
- v294 empty migration DB 생성 도구와 smoke 준비

## 현재 사용자 실행 단계

1. `python tools/create_postgres_migration_test_database.py --execute`
2. target `rpg_game_migration_empty_v290` 확인
3. target 0 tables / 0 rows 확인
4. target `alembic_version` 없음 확인
5. source와 rehearsal before/after 동일 확인
6. 콘솔 결과만 공유

## 다음 별도 승인

- 최초 Alembic revision 생성
- revision 파일 수동 검토
- empty DB `upgrade head`
- schema equivalence와 downgrade/upgrade 왕복
- 기존 DB baseline stamp 여부
- rehearsal/migration DB 삭제

## 계속 금지

원본/리허설 DB 변경, 자동 DB 삭제, Alembic revision/upgrade/downgrade/stamp, `.env`, seed, 인증, API body/route/write guard, 게임 콘텐츠 변경.
