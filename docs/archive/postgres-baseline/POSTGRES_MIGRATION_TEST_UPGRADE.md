# PostgreSQL isolated migration test DB upgrade — v298

## 대상

```txt
rpg_game_migration_empty_v290
```

## exact revision

```txt
revision: v295_initial_schema
SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
manual review: passed
```

## 실행 전 필수 상태

- source `rpg_game`: 22 tables / 748 rows / no Alembic baseline
- rehearsal DB: 22 tables / 748 rows / differences=0
- migration DB: only `alembic_version`, 0 rows, recorded revisions 없음
- revision file exact SHA 일치
- manual review manifest 결론: `approved-for-isolated-empty-migration-database-upgrade-only`

## 허용 명령

```txt
python -m alembic --config alembic.ini upgrade head
```

자식 프로세스 `DATABASE_URL`만 `rpg_game_migration_empty_v290`으로 override합니다. `backend/.env`는 수정하지 않습니다.

## 성공 조건

```txt
public tables: 23
model tables: 22
alembic_version rows: 1
current revision: v295_initial_schema
model table rows: 모두 0
schema: structurally-equivalent
differences: 0
source/rehearsal: 작업 전후 동일
```

## 아직 금지

```txt
downgrade
stamp
source DB upgrade
createdb/dropdb
pg_restore
.env/Docker volume 변경
```

## 사용자 PC 실제 실행 결과 — 2026-07-14

```txt
result: migration-test-database-upgraded-and-verified
target public tables: 23
target model tables: 22
target total rows including Alembic control row: 1
target current revision: ['v295_initial_schema']
target schema: structurally-equivalent / differences=0
source tables/rows preserved: 22/748
rehearsal tables/rows preserved: 22/748
```

다음 기준 문서: `docs/archive/postgres-baseline/POSTGRES_MIGRATION_TEST_DOWNGRADE.md`
