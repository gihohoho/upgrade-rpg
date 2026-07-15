# Current Status — v311

## 현재 기준

- 최신 작업: `v311.production-capacity-tls-network-isolated-plan`
- 기준 ZIP: `rpg_v311_production_capacity_tls_network_plan_handoff_ready.zip`
- readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

## PostgreSQL/Alembic 완료 상태

```txt
classification: alembic-managed-baseline-complete
source rpg_game: public 23/749, application 22/748
current revision: v295_initial_schema
source/rehearsal application digest: identical
v302 rehearsal report: verified
v304 source report: verified
v305 completion: passed
v306 candidate operations: 0 / next revision required no
```

## Runtime 완료 상태

```txt
v307 strict + require-health: passed
Docker PostgreSQL: running/healthy
FastAPI live DB health: ok
v308 pool/lifecycle/production guard/Dockerfile/Compose template: applied
v309 runtime engine AST binding fix: passed
v310 production static validation: passed
remaining local-vs-production warnings: 9
```

## v311 완료 상태

- `deploy/production-capacity-plan.example.json` review-only 계산 입력 추가
- 현재 1 replica × 1 worker × pool(5+10) 기준 application burst 15 계산
- non-application reserve 10과 safety 20% 포함 recommended minimum 30 계산
- PostgreSQL `max_connections` review 후보 40 고정, 실제 적용 없음
- 2 replicas 후보 50, 2 replicas × 2 workers 후보 90 계산
- 관리형 PostgreSQL 우선 검토, bundled PostgreSQL TLS 대안 조건 문서화
- reverse proxy HTTPS 443 only, backend/PostgreSQL host port 비공개 경계 문서화
- isolated container Stage 0~4 승인 경계 문서화
- v311 읽기 전용 checker와 fail-closed smoke 추가

## 다음 첫 작업

```bash
python tools/check_production_capacity_tls_network_plan.py --strict
```

예상 결과:

```txt
recommended/candidate max_connections: 30/40
TLS database mode: managed-postgresql-preferred
result: production-capacity-tls-network-plan-verified-execution-blocked
isolated container execution approved: no
next safe stage: approve-provider-and-isolated-container-config-render-only
```

## 다음 승인 경계

1. 실제 예상 사용자/트래픽과 backend replica 목표 검토
2. 관리형 PostgreSQL 또는 bundled PostgreSQL 중 운영 방향 승인
3. reverse proxy 제품/DNS/certificate 방향 승인
4. 별도 승인 후 Docker `compose config`만 수행하는 render-only 단계
5. build/pull/up/down은 다시 별도 승인

## 계속 금지

- 실제 production secret/CA/cert/key 입력
- 실제 `.env` 수정
- production Compose config/build/pull/up/down 실행
- Docker container/volume 변경
- stamp 재실행 또는 새 revision/autogenerate/upgrade/downgrade
- DB 생성/삭제/복원/seed 또는 `max_connections` 적용
- 인증/API route/body/write 및 게임 콘텐츠 변경
