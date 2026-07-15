# NEXT CHAT HANDOFF — Upgrade RPG v313

## 기준 ZIP

- `rpg_v313_backend_image_source_digest_policy_handoff_ready.zip`

## 현재 기준

- 최신 작업: `v313.backend-image-source-digest-policy`
- readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

## PostgreSQL/Alembic 고정 상태

```txt
classification: alembic-managed-baseline-complete
source rpg_game: public 23/749, application 22/748
current revision: v295_initial_schema
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
v305 completion: passed
v306 candidate operations: 0 / next revision required no
```

source/rehearsal stamp, 새 revision, upgrade/downgrade는 다시 실행하지 않습니다.

## Runtime 고정 상태

```txt
v307 live DB health and local Docker readiness: passed
v308 pool/lifecycle/production guard/Dockerfile/Compose: applied
v309 runtime engine AST inspector: passed
v310 production static validation baseline: passed
remaining local production warnings: 9
```

## 운영 방향 확정

```txt
database: managed-postgresql-selected
TLS: verify-full-with-provider-ca
public entrypoint: external-reverse-proxy-https-selected
backend replicas/workers: 1/1
reverse proxy product: deferred
```

production Compose는 backend-only이며 bundled PostgreSQL/Adminer/named DB volume/host ports/build가 없습니다.

## v312 사용자 PC 실제 결과

기호 PC에서 다음 명령이 통과했습니다.

```txt
python tools/render_production_compose_config.py --execute --confirm-stage v312-config-render-only
```

결과:

```txt
rendered services: backend
host ports/build/named volumes absent: True/True/True
managed DB service absent / backend replicas: True/1
digest/production guard/TLS/edge rendered: True/True/True/True
image pull/build executed: no
container/network/volume mutation executed: no
DB/Alembic mutation executed: no
result: production-compose-config-render-verified-no-runtime-mutation
```

config render approved/executed: yes/yes입니다. 민감정보 없는 안전 요약만 `deploy/review/production-compose-config-render-v312.json`에 저장했고 raw render는 저장하지 않았습니다.

## v313 변경

- `deploy/backend-image-source-digest-policy.example.json` 추가
- `docs/current/BACKEND_IMAGE_SOURCE_DIGEST_POLICY.md` 추가
- `tools/check_backend_image_source_digest_policy.py` 추가
- fail-closed 전용 smoke 추가
- production image reference를 registry/namespace/repository + exact SHA-256 digest 형식으로 고정
- Git commit, target platform, base image digest 기록 필수
- SBOM/provenance/signature/vulnerability review 필수
- 현재 Dockerfile base `python:3.11-slim`은 mutable tag로 분류
- registry provider, target platform, base image digest는 deferred
- pull/build/push approved: no/no/no
- container start approved: no

## 다음 첫 작업

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_backend_image_source_digest_policy.py --strict
```

정상 결과 핵심:

```txt
config render evidence verified: True
registry/repository/platform: deferred / <placeholder> / deferred
production reference mode: digest-only
current base image: python:3.11-slim
base image digest pinned/approved: False/False
supply-chain gates required: 4/4
image pull/build/push approved: no/no/no
result: backend-image-source-digest-policy-verified-provider-and-build-blocked
next safe stage: select-registry-repository-platform-and-base-image-digest
```

## 다음 안전 순서

1. registry provider 선택
2. namespace/repository identity 선택
3. production target platform 선택
4. base image exact digest 검토
5. credential 보관 방식 검토
6. 별도 승인 후 base image pull
7. 별도 승인 후 backend image build
8. SBOM/provenance/vulnerability review
9. 별도 승인 후 push와 digest/signature 검증
10. managed PostgreSQL provider와 reverse proxy 제품 선택
11. isolated start와 cleanup 각각 별도 승인

## 계속 금지

- 실제 `backend/.env`, production env, JWT/Admin secret 변경
- 실제 password/CA/cert/key/registry credential 생성·입력·커밋
- Docker image pull/build/push
- Docker container/network/volume create/start/stop/remove
- `docker compose ... up/down/run/start/stop/rm`
- managed PostgreSQL 실제 연결/query/설정 변경
- source/rehearsal stamp 재실행
- Alembic revision/autogenerate/upgrade/downgrade
- DB create/drop/restore/reset/seed
- 인증/API route path/response body/write logic
- Vue Preview/Apply/write 연결
- 게임 콘텐츠/밸런스 변경
