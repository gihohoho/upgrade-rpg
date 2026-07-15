# Current Documents — v306

- 최신 작업: `v306.postgres-next-revision-readonly-preflight`
- 현재 상태: `CURRENT_STATUS.md`
- 로드맵: `ROADMAP.md`
- baseline 완료 상태: `POSTGRES_BASELINE_COMPLETION_STATE.md`
- next revision preflight: `POSTGRES_NEXT_REVISION_PREFLIGHT.md`
- next revision 안전 계획: `POSTGRES_NEXT_REVISION_READONLY_PLAN.md`
- PostgreSQL/Alembic readiness: `POSTGRES_ALEMBIC_READINESS.md`

v306은 revision을 만들지 않고 실제 metadata candidate operation이 있는지만 읽기 전용으로 판단합니다. 기존 stamp 재실행과 새 revision/autogenerate/upgrade/downgrade는 금지합니다.
