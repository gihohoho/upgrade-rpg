# Production deployment review template — v313

`deploy/docker-compose.production.yml`은 로컬 `docker-compose.yml`을 대체하지 않는 운영 검토 template입니다. review sentinel 기반 `docker compose config`는 기호 PC에서 통과했지만 image pull/build/push 및 container 실행은 승인되지 않았습니다.

## 확정된 운영 방향

- 관리형 PostgreSQL
- provider CA를 이용한 TLS `verify-full`
- 외부 reverse proxy HTTPS 진입점
- backend 1 replica / Uvicorn 1 worker
- pool 5 + overflow 10
- PostgreSQL `max_connections` review 후보 40

## 현재 production Compose

- service는 `backend` 하나만 포함
- bundled PostgreSQL/Adminer/named DB volume 없음
- backend host `ports:` 없음, `8000`은 proxy network에만 expose
- backend image는 approved registry의 exact digest 필수
- `ENVIRONMENT=production`, `DEBUG=false`
- JWT/Admin key/CORS/DATABASE_URL/CA path 필수 입력
- non-root Dockerfile, read-only filesystem, tmpfs, no-new-privileges
- `/api/v1/health` container healthcheck
- 자동 Alembic 없음
- 사전에 생성한 external reverse proxy network 이름 필수

## 관련 review-only 파일

- `production.env.example`: 실제 값 없는 운영 변수 inventory
- `production-capacity-plan.example.json`: worker/pool/max_connections 계산과 승인 상태
- `production-architecture-selection.example.json`: 운영 방향과 config render 완료 상태
- `backend-image-source-digest-policy.example.json`: digest-only와 공급망 검증 게이트
- `review/production-compose-config-render-v312.json`: 사용자 PC config render 안전 요약
- `reverse-proxy/README.md`: reverse proxy/HTTPS 고정 계약과 제품 선택 전 확인사항
- `isolated-validation/README.md`: config/pull/build/push/start/cleanup 승인 경계
- `secrets/README.md`: 실제 secret을 Git/ZIP/build context에 넣지 않는 규칙

## 완료한 Docker 범위

```txt
docker compose config: completed through the project safety wrapper
Docker image pull/build/push: not approved
Docker container/network/volume create/start/stop/remove: not approved
managed DB connection/write: not approved
```

## 현재 이미지 정책

```txt
production image reference: digest-only
registry provider: deferred
target platform: deferred
base image digest approved: no
image pull/build/push approved: no/no/no
```

## 아직 결정하지 않은 것

- 관리형 PostgreSQL 공급자/상품/region/private network
- 실제 provider CA와 endpoint
- backend image registry/namespace/target platform/base digest
- reverse proxy 제품, DNS, certificate 운영 방식
- 실제 production secret 값

## 계속 금지

- 실제 production env/secret/CA/cert/key/registry credential 생성·입력·커밋
- Docker pull/build/push/up/down 또는 resource 변경
- 실제 managed DB 연결
- PostgreSQL `max_connections` 변경
- 자동 migration 추가
