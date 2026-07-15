# Production deployment review template — v312

`deploy/docker-compose.production.yml`은 로컬 `docker-compose.yml`을 대체하지 않는 운영 검토 template입니다. 현재 승인 범위는 review sentinel을 사용한 `docker compose config`뿐입니다.

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
- `production-architecture-selection.example.json`: v312 운영 방향 선택값
- `reverse-proxy/README.md`: reverse proxy/HTTPS 고정 계약과 제품 선택 전 확인사항
- `isolated-validation/README.md`: config/pull/build/start/cleanup 승인 경계
- `secrets/README.md`: 실제 secret을 Git/ZIP/build context에 넣지 않는 규칙

## 현재 승인된 명령 범위

```txt
docker compose config: approved through the project safety wrapper
Docker image pull/build: not approved
Docker container/network/volume create/start/stop/remove: not approved
managed DB connection/write: not approved
```

wrapper:

```txt
python tools/render_production_compose_config.py --execute --confirm-stage v312-config-render-only
```

## 아직 결정하지 않은 것

- 관리형 PostgreSQL 공급자/상품/region/private network
- 실제 provider CA와 endpoint
- backend image registry/source/digest
- reverse proxy 제품, DNS, certificate 운영 방식
- 실제 production secret 값

## 계속 금지

- 실제 production env/secret/CA/cert/key 생성·입력·커밋
- Docker pull/build/up/down 또는 resource 변경
- 실제 managed DB 연결
- PostgreSQL `max_connections` 변경
- 자동 migration 추가
