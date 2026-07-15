# Current Status — v306

## 기준

- 최신 작업: `v306.postgres-next-revision-readonly-preflight`
- 기준 ZIP: `rpg_v306_postgres_next_revision_readonly_preflight_ready.zip`
- readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

## 실제 PostgreSQL/Alembic 상태

```txt
classification: alembic-managed-baseline-complete
source rpg_game: public 23/749, application 22/748, revision v295_initial_schema
rehearsal: 23/749, revision v295_initial_schema, v302 report verified
migration: 23/1, revision v295_initial_schema, differences=0
v304 source report: verified
v305 completion check: postgres-baseline-completion-state-verified
```

## v306 준비 내용

```txt
tools/check_postgres_next_revision_preflight.py
tools/smoke/backend/smoke_postgres_next_revision_preflight.py
docs/current/POSTGRES_NEXT_REVISION_PREFLIGHT.md
```

v306은 revision을 생성하지 않고 다음을 읽기 전용으로 확인합니다.

- exact single Alembic base/head/revision file
- approved model/env source snapshot 13 files
- canonical schema 22/22, differences=0
- read-only Alembic metadata comparison
- type/server default/nullable/index/constraint candidate operations
- PostgreSQL sequence ownership

## 다음 첫 작업

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv` 켜짐

```bash
python tools/check_postgres_next_revision_preflight.py --strict
```

정상 변경 없음 기대 결과:

```txt
Alembic candidate operations: 0
next revision required: no
result: next-revision-not-required-current-schema-equivalent
next safe stage: keep-single-baseline-no-new-revision
```

후보가 발견되면 자동 생성하지 않고 `separate-schema-change-intent-review`로 중지합니다.
