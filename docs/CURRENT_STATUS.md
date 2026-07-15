# Current Status — v312

## 현재 기준

- 최신 작업: `v312.production-managed-postgres-reverse-proxy-config-render-ready`
- 기준 ZIP: `rpg_v312_managed_postgres_reverse_proxy_config_render_ready.zip`
- readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

## PostgreSQL/Alembic 완료 상태

```txt
classification: alembic-managed-baseline-complete
source rpg_game: public 23/749, application 22/748
current revision: v295_initial_schema
v305 completion: passed
v306 candidate operations: 0 / next revision required no
```

## Runtime 완료 상태

```txt
v307 strict + require-health: passed
local Docker PostgreSQL: running/healthy
FastAPI live DB health: ok
v308 pool/lifecycle/production guard/Dockerfile/Compose: applied
v309 runtime engine AST binding fix: passed
v310 static validation baseline: passed
remaining local-vs-production warnings: 9
```

## v312 확정과 변경

- `managed-postgresql-selected`
- `verify-full-with-provider-ca`
- `external-reverse-proxy-https-selected`
- backend replicas/workers `1/1`
- production Compose service는 backend 하나
- bundled PostgreSQL/Adminer/named volume/host ports/build 제거
- exact digest `BACKEND_IMAGE`, provider CA, external edge network 필수
- config render approved: yes
- config render executed on user PC: no
- image pull/build/container start approved: no

## 다음 첫 작업

```bash
python tools/check_production_managed_postgres_reverse_proxy_selection.py --strict
python tools/render_production_compose_config.py --execute --confirm-stage v312-config-render-only
```

두 번째 명령은 Docker resource를 만들지 않고 config만 렌더링합니다. handoff 제작 환경에는 Docker CLI가 없어 실제 실행 결과는 아직 없습니다.

## 다음 승인 경계

config render가 통과한 뒤 backend image registry/source/digest 검토로 이동합니다. pull/build는 다시 별도 승인합니다.

## 계속 금지

- 실제 production env/secret/CA/cert/key 입력
- image pull/build
- container/network/volume create/start/stop/remove
- managed DB 연결 또는 `max_connections` 적용
- Alembic revision/autogenerate/stamp/upgrade/downgrade
- DB create/drop/restore/reset/seed
- 인증/API route/body/write 및 게임 콘텐츠 변경
