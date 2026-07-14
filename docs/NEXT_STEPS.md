# Next Steps — v298

## 완료

- schema equivalence differences=0
- verified custom backup 생성
- isolated restore rehearsal 22 tables / 748 rows / differences=0
- `rpg_game_migration_empty_v290` 생성
- 최초 revision `v295_initial_schema` 생성
- revision SHA-256 고정
- 모델/revision 22 tables / 209 columns / 42 indexes 수동 검토 통과
- downgrade dependency order 검토 통과
- source/rehearsal DB 작업 전후 동일

## 현재 읽기 전용 단계

```bash
python tools/upgrade_postgres_migration_test_database.py --inspect
```

성공 기준:

```txt
result: ready-for-separate-upgrade-approval
migration tables: ['alembic_version']
recorded revisions: []
```

## 다음 별도 승인

- `rpg_game_migration_empty_v290`에서만 `alembic upgrade head`
- upgrade 후 22 model tables + `alembic_version`, differences=0 검증
- 그다음 migration DB downgrade 별도 승인
- downgrade/upgrade 왕복 완료 후 source DB baseline stamp 여부 검토

## 계속 금지

원본 DB `upgrade/stamp`, migration DB `downgrade`, `dropdb`, `.env`, seed, 인증, API body/route/write guard, 게임 콘텐츠 변경.
