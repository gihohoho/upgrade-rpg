# Current Documents — v308

- 최신 작업: `v308.runtime-config-hardening-ready`
- PostgreSQL baseline: 완료
- 다음 revision: 현재 불필요
- 현재 단계: runtime config hardening 검증

## 우선 문서

- `CURRENT_STATUS.md`
- `PROJECT_STRUCTURE.md`
- `ROADMAP.md`
- `POSTGRES_DEPLOYMENT_RUNTIME_READINESS.md`
- `POSTGRES_RUNTIME_CONFIG_HARDENING.md`
- `POSTGRES_PRODUCTION_DEPLOYMENT_TEMPLATE.md`
- `POSTGRES_DEPLOYMENT_MIGRATION_RUNBOOK.md`

v308은 실제 `.env`·DB·Docker 자원을 변경하지 않고 pool, engine shutdown, production guard, FastAPI image와 별도 운영 Compose 초안을 준비합니다.
