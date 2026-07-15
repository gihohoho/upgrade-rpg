# NEXT CHAT HANDOFF — Upgrade RPG v311

## 기준 ZIP

- `rpg_v311_production_capacity_tls_network_plan_handoff_ready.zip`

## 현재 기준

- 최신 작업: `v311.production-capacity-tls-network-isolated-plan`
- readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

## 실제 완료 상태

```txt
classification: alembic-managed-baseline-complete
source rpg_game: public 23/749, application 22/748
current revision: v295_initial_schema
rehearsal: 23/749 / v302 report verified
migration DB: 23/1 / differences=0
v306 candidate operations: 0 / next revision required no
v307 live DB health and Docker readiness: passed
v308 pool/lifecycle/production guard/Dockerfile/Compose: applied
v309 runtime engine AST inspector: user PC passed
v310 production static validation: passed
remaining production warnings: 9
```

## v311 변경

- `deploy/production-capacity-plan.example.json` review-only 계산 입력 추가
- 현재 1 replica × 1 worker, pool 5 + overflow 10 확인
- application steady/burst 5/15 계산
- non-application reserve 10, safety margin 20% 계산
- recommended minimum `max_connections=30`, review 후보 `40`
- 확장 시 2 replicas 최소 50, 2 replicas × 2 workers 최소 90 계산
- 관리형 PostgreSQL 우선 검토, bundled PostgreSQL TLS 대안 경계 문서화
- reverse proxy HTTPS 443 only와 backend/PostgreSQL 내부 network 경계 문서화
- isolated container config/build/run/cleanup Stage 0~4 승인 경계 문서화
- `tools/check_production_capacity_tls_network_plan.py`와 전용 smoke 추가

## 다음 첫 작업

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_production_capacity_tls_network_plan.py --strict
```

정상 결과:

```txt
recommended/candidate max_connections: 30/40
future 2-replica / 2x2-worker minimums: 50/90
TLS database mode: managed-postgresql-preferred
reverse proxy only / DB internal: True/True
isolated container execution approved: no
result: production-capacity-tls-network-plan-verified-execution-blocked
next safe stage: approve-provider-and-isolated-container-config-render-only
```

## 다음 안전 순서

1. 실제 예상 사용자/트래픽과 replica 목표 검토
2. 관리형 PostgreSQL 또는 bundled PostgreSQL 운영 방향 승인
3. reverse proxy 제품, DNS, HTTPS certificate 운영 방향 승인
4. image digest source와 승인 기록 형식 확정
5. 별도 승인 후 Docker `compose config` render-only 단계
6. render 결과 통과 후에만 pull/build 별도 승인
7. isolated project/resource 검토 후에만 up/down 별도 승인

## 계속 금지

- 실제 production env/secret/CA/cert/key 입력
- production Compose config/build/pull/up/down
- Docker container/volume 변경
- PostgreSQL `max_connections` 실제 변경
- source/rehearsal stamp 재실행
- Alembic revision/autogenerate/upgrade/downgrade
- DB create/drop/restore/reset/seed
- 인증/API route/body/write 변경
- 게임 콘텐츠와 Vue write 연결
