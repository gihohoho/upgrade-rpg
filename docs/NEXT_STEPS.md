# Next Steps — v292

## 완료

- schema equivalence 차이 0개 확인
- backup/restore preflight 통과
- verified custom backup 생성 완료
- SHA-256/TOC/source snapshot/manifest 검증 완료
- target 존재 여부 확인 후 없을 때만 빈 DB를 생성하는 v292 도구 준비

## 현재 사용자 실행 단계

1. `python tools/create_postgres_restore_rehearsal_database.py --execute`
2. target `rpg_game_restore_rehearsal_v290` 생성 여부 확인
3. target public tables 0개 확인
4. source 22 tables / 748 rows 유지 확인
5. 콘솔 결과만 공유

## 다음 별도 승인

- verified dump를 target DB에 `pg_restore`
- restore 후 table별 row count와 schema equivalence 비교
- restore rehearsal DB 삭제 여부 결정
- 별도 empty migration DB 준비와 최초 Alembic revision 검증

## 계속 금지

원본 DB 변경, `dropdb`, Alembic revision/upgrade/downgrade/stamp, `.env`, seed, 인증, API body/route/write guard, 게임 콘텐츠 변경.
