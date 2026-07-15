# Smoke tests

- `frontend/`: 관리자 브라우저/JS 계약
- `contracts/`: 관리자 백엔드 계약
- `backend/`: 패키징과 백엔드 기반
- `game/`: 저장/런타임/시드/마스터 데이터

## v306 PostgreSQL next revision preflight

- `backend/smoke_postgres_next_revision_preflight.py`
- single head, approved model source hash, canonical schema, read-only Alembic metadata diff, sequence ownership을 검증합니다.
- 실제 revision/autogenerate/upgrade/downgrade/stamp는 실행하지 않습니다.

## v305 PostgreSQL baseline completion state

```bash
python tools/smoke/backend/smoke_postgres_baseline_completion_state.py
```

완료 상태, execution report, exact revision set, read-only mutation boundary를 검증합니다.
