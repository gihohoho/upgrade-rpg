# Production deployment review template — v319

`deploy/docker-compose.production.yml`은 로컬 `docker-compose.yml`을 대체하지 않는 운영 검토 template입니다. review sentinel 기반 `docker compose config`는 기호 PC에서 통과했지만 image login/pull/build/push 및 container 실행은 승인되지 않았습니다.

## 확정된 운영 방향

- 관리형 PostgreSQL
- provider CA를 이용한 TLS `verify-full`
- 외부 reverse proxy HTTPS 진입점
- backend 1 replica / Uvicorn 1 worker
- pool 5 + overflow 10
- PostgreSQL `max_connections` review 후보 40
- GitHub Container Registry (`ghcr.io`)
- GHCR namespace `gihohoho`
- private repository `ghcr.io/gihohoho/upgrade-rpg-backend`
- target platform `linux/amd64`
- production base image exact manifest digest 승인

## 현재 production Compose

- service는 `backend` 하나만 포함
- bundled PostgreSQL/Adminer/named DB volume 없음
- backend host `ports:` 없음, `8000`은 proxy network에만 expose
- backend image는 `ghcr.io/gihohoho/upgrade-rpg-backend@sha256:<approved-64-hex-digest>` 형식 필수
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
- `backend-image-ghcr-policy.example.json`: GHCR namespace, digest-only, credential/workflow 승인 경계
- `github-actions-ghcr-static-plan.example.json`: 최소 permissions, 수동 trigger, SBOM/provenance/signature/vulnerability gate
- `review/`: 완료된 v312~v314 정적 review 증거
- `reverse-proxy/README.md`: reverse proxy/HTTPS 고정 계약과 제품 선택 전 확인사항
- `isolated-validation/README.md`: config/login/pull/build/push/start/cleanup 승인 경계
- `secrets/README.md`: 실제 secret을 Git/ZIP/build context에 넣지 않는 규칙

## 현재 credential 정책

```txt
CI 우선안: GitHub Actions GITHUB_TOKEN
local credential/PAT: deferred
workflow creation approved: no
docker login approved: no
image pull/build/push approved: no/no/no
```

## 정적 설계 완료

- `workflow_dispatch` only + exact `main` SHA + protected environment
- read-only validation/build-scan job과 write 권한이 격리된 publish job
- full-length action SHA 필수(9개 검토 후보 고정, 사용자 승인 아직 안 됨)
- SPDX SBOM, Trivy HIGH/CRITICAL, provenance, keyless signature, verification gate

## 아직 결정·승인하지 않은 것

- 검토한 action별 upstream 40자리 SHA 후보의 사용자 승인
- repository action allowlist/full-length SHA 설정 변경과 publish environment 생성
- `.github/workflows/` 파일 생성과 workflow 실행
- 관리형 PostgreSQL 공급자/상품/region/private network
- 실제 provider CA와 endpoint
- reverse proxy 제품, DNS, certificate 운영 방식
- 실제 production secret 값

## 계속 금지

- 실제 production env/secret/CA/cert/key/registry credential 생성·입력·커밋
- `.github/workflows/` 생성 또는 workflow 실행
- Docker login/pull/build/push/up/down 또는 resource 변경
- 실제 managed DB 연결
- PostgreSQL `max_connections` 변경
- 자동 migration 추가
