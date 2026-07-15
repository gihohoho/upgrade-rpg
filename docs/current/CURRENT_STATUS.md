# Current Status — v313

## 현재 기준

- 최신 작업: `v313.backend-image-source-digest-policy`
- 기준 ZIP: `rpg_v313_backend_image_source_digest_policy_handoff_ready.zip`
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

## 운영 방향

```txt
database: managed-postgresql-selected
TLS: verify-full-with-provider-ca
public entrypoint: external-reverse-proxy-https-selected
backend replicas/workers: 1/1
max_connections review candidate: 40
```

## v312 실제 완료 증거

기호 PC에서 review sentinel 기반 Compose config render-only가 통과했습니다.

```txt
rendered services: backend
host ports/build/named volumes absent: True/True/True
managed DB service absent / backend replicas: True/1
digest/production guard/TLS/edge rendered: True/True/True/True
image pull/build executed: no
container/network/volume mutation executed: no
DB/Alembic mutation executed: no
```

민감정보 없는 요약만 `deploy/review/production-compose-config-render-v312.json`에 기록했으며 raw render는 저장하지 않았습니다.

## v313 이미지 정책

- production backend image는 `digest-only`
- repository 형식: `<approved-registry>/<approved-namespace>/upgrade-rpg-backend`
- registry provider: deferred
- target platform: deferred
- Git commit 40자리 SHA 기록 필수
- base image exact digest 승인 전 build 차단
- SBOM/provenance/signature/vulnerability review 필수
- image pull/build/push approved: no/no/no
- container start approved: no

현재 Dockerfile base image `python:3.11-slim`은 mutable tag이므로 production build 승인을 충족하지 않습니다.

## 다음 승인 경계

```txt
select-registry-repository-platform-and-base-image-digest
```

registry provider, namespace/repository, target platform, base image exact digest를 먼저 선택합니다. 선택 단계에서도 Docker pull/build/push는 실행하지 않습니다.

## 계속 금지

- 실제 production env/secret/CA/cert/key/registry credential 입력
- Docker image pull/build/push
- container/network/volume create/start/stop/remove
- managed DB 연결 또는 `max_connections` 적용
- Alembic revision/autogenerate/stamp/upgrade/downgrade
- DB create/drop/restore/reset/seed
- 인증/API route/body/write 및 게임 콘텐츠 변경
