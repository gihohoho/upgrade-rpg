# Roadmap — v294

## 완료 흐름

- v268~v281 구조/route/Vue 관리자 GET 이식
- v282~v289 PostgreSQL/Alembic readiness, runtime, schema equivalence, FLOAT normalization
- v290 backup/restore read-only gate와 분리 DB 경계
- v291 verified custom backup 생성과 TOC/SHA/source snapshot 검증
- v292 빈 restore rehearsal DB 생성
- v293 isolated restore 및 22 tables / 748 rows / differences=0 검증 완료
- v294 empty migration test DB 생성 도구와 안전 경계 준비

## 현재 단계

사용자가 아래 명령으로 `rpg_game_migration_empty_v290`을 생성합니다.

```bash
python tools/create_postgres_migration_test_database.py --execute
```

성공 기준:

```txt
target tables/rows: 0 / 0
alembic_version: 없음
source before/after: 22 / 748 동일
rehearsal before/after: 22 / 748 동일
```

## 이후 승인 경계

1. 최초 Alembic revision 생성 명령과 target URL 경계 설계
2. revision 파일 생성만 실행
3. 생성된 revision 전체 수동 검토
4. empty migration DB에서 `upgrade head`
5. schema equivalence 검사
6. downgrade/upgrade 왕복 검증
7. 기존 `rpg_game` baseline stamp 여부 최종 결정
8. 필요할 때만 rehearsal/migration DB `dropdb` 별도 승인

각 revision/upgrade/downgrade/stamp/drop 단계는 실제 결과를 확인하고 별도 승인합니다.
