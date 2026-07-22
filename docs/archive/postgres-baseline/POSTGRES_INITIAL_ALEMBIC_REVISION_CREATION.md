# PostgreSQL 최초 Alembic revision `op.f` parser 복구 — v297

## 실제 원인

v296은 기존 빈 `alembic_version` placeholder를 정상적으로 재사용해 revision 파일을 생성했습니다. 하지만 자동 검토 함수가 revision 함수 내부의 모든 `op.*` 호출을 migration operation으로 수집하면서, 아래와 같은 nested naming helper까지 실제 작업으로 오판했습니다.

```python
op.create_index(op.f("ix_example"), "example", ["value"], unique=False)
op.drop_index(op.f("ix_example"), table_name="example")
```

`op.f(...)`는 constraint/index 이름이 naming convention 처리를 이미 마쳤음을 나타내는 Alembic helper입니다. 테이블이나 데이터를 변경하는 operation이 아닙니다.

사용자 실제 결과:

```txt
result: blocked-or-failed
reason: unexpected Alembic operations: upgrade=['f'], downgrade=['f']
```

실패 처리에서 생성된 revision Python 파일과 review artifact는 자동 정리됐습니다. DB에는 기존 `alembic_version` 1 table / 0 rows / recorded revision 없음 상태만 유지됩니다.

## v297 수정

```txt
ALEMBIC_NON_OPERATION_HELPERS = {'f'}
```

- nested `op.f(...)`를 operation count와 allowlist 검사에서 제외
- `op.create_table`, `op.create_index`, `op.drop_index`, `op.drop_table`은 계속 실제 operation으로 검사
- `op.execute`, `bulk_insert`, destructive upgrade, constructive downgrade는 계속 차단
- smoke fake revision에도 실제 Alembic 형태의 nested `op.f(...)`를 넣어 재현 및 회귀 검증
- operation 결과에 `f`가 다시 나타나면 smoke 실패

## 고정 경계

```txt
source DB: rpg_game (read-only)
rehearsal DB: rpg_game_restore_rehearsal_v290 (read-only)
revision workspace: rpg_game_migration_empty_v290
revision ID: v295_initial_schema
```

- `backend/.env` 미수정
- child process `DATABASE_URL`만 target override
- 기존 empty `alembic_version` placeholder 재사용
- revision row 기록 없음
- application table mutation 없음
- upgrade/downgrade/stamp/createdb/dropdb/pg_restore 없음

## 실행

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/create_postgres_initial_alembic_revision.py --inspect-workspace && python tools/create_postgres_initial_alembic_revision.py --execute
```

## 성공 기대값

```txt
result: initial-alembic-revision-created-and-automatically-reviewed
revision ID: v295_initial_schema
upgrade create_table: 22
downgrade drop_table: 22
reviewed tables/columns: 22 / 209
migration DB tables before/after: 1 / 1
migration workspace before/after: empty-alembic-version-placeholder / empty-alembic-version-placeholder
migration DB alembic_version before/after: True / True
alembic_version rows before/after: 0 / 0
```

review bundle:

```txt
local-review-artifacts/alembic/v295_initial_schema_review_bundle.zip
```

이 bundle 수동 검토 전에는 generated revision commit 또는 `upgrade head`를 실행하지 않습니다.

## v297 실제 성공 결과

사용자 환경에서 revision 생성과 자동 검토가 성공했습니다.

```txt
revision ID: v295_initial_schema
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
upgrade create_table: 22
upgrade create_index: 42
downgrade drop_table: 22
reviewed tables/columns: 22 / 209
migration DB tables before/after: 1 / 1
alembic_version rows before/after: 0 / 0
```

v298에서 review bundle의 exact revision을 수동 교차 검토했고 통과했습니다. 이후 기준은 아래 문서입니다.

```txt
docs/current/POSTGRES_INITIAL_ALEMBIC_REVISION_MANUAL_REVIEW.md
docs/archive/postgres-baseline/POSTGRES_MIGRATION_TEST_UPGRADE.md
```
