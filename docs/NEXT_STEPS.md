# Next Steps — v293

## 완료

- schema equivalence 차이 0개 확인
- backup/restore preflight 통과
- verified custom backup 생성 완료
- SHA-256/TOC/source snapshot/manifest 검증 완료
- 빈 target `rpg_game_restore_rehearsal_v290` 생성 완료
- target 0 tables, source 22 tables / 748 rows 유지 확인
- v293 isolated restore 도구와 전용 smoke 준비

## 현재 사용자 실행 단계

1. `python tools/restore_postgres_rehearsal_database.py --execute`
2. target 22 tables / 748 rows 확인
3. table별 row count가 backup snapshot과 동일한지 확인
4. target schema equivalence differences=0 확인
5. source before/after 동일 확인
6. 콘솔 결과만 공유

## 다음 별도 승인

- restore rehearsal DB 보존 또는 `dropdb`
- 별도 empty migration DB 생성
- 최초 Alembic revision 생성/수동 검토
- empty DB upgrade/downgrade
- 기존 DB baseline stamp 여부 결정

## 계속 금지

원본 DB 변경, 자동 target 삭제, Alembic revision/upgrade/downgrade/stamp, `.env`, seed, 인증, API body/route/write guard, 게임 콘텐츠 변경.
