# Production deployment review template — v321

`deploy/docker-compose.production.yml`은 로컬 `docker-compose.yml`을 대체하지 않는 운영 검토 template입니다. review sentinel 기반 `docker compose config`는 기호 PC에서 통과했습니다. CI image login/build/push는 승인됐지만 게시 승인 모델과 deterministic dependency/toolchain lock이 아직 준비되지 않아 hard gate로 차단했으며, workflow와 local Docker/container 실행은 하지 않았습니다.

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
- backend image는 검증된 exact reference `ghcr.io/gihohoho/upgrade-rpg-backend@sha256:ff939391517452a3ec477adaa0f8556d3525f9d0c6fb5f9d0df11d8f3d8461d2`로 정적 고정
- `ENVIRONMENT=production`, `DEBUG=false`
- JWT/Admin key/CORS/DATABASE_URL/CA path 필수 입력
- non-root Dockerfile, read-only filesystem, tmpfs, no-new-privileges
- `/api/v1/health` container healthcheck
- 자동 Alembic 없음
- 사전에 생성한 external reverse proxy network 이름 필수

## 관련 review-only 파일

- `production.env.example`: 검증된 backend digest만 고정하고 secret·DB·CA·network 값은 placeholder로 둔 운영 변수 inventory
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
workflow creation/execution approved: yes/yes
workflow execution: no
CI login/build/push approved: yes/yes/yes
CI login/build/push executed: no/no/no
local credential/Docker operations: deferred/not executed
```

## 정적 설계 완료

- `workflow_dispatch` only + exact `main` SHA + protected environment
- read-only validation/build-scan job과 write 권한이 격리된 publish job
- full-length action SHA 필수(사용하는 외부 action 8개 repository 설정 완료)
- SPDX SBOM, checksum-pinned Trivy HIGH/CRITICAL, pushed exact-digest 재검사
- Docker BuildKit mode=max provenance/SBOM과 Cosign keyless signature/verification
- source-controlled reviewer gate `false`, GHCR login 전 차단

## 아직 승인·실행하지 않은 것

- v321 preparation commit의 정확한 40자 SHA에 대한 기호의 명시 승인
- GitHub live 설정 재확인과 별도 authorization commit
- source-controlled gate 변경 및 workflow 첫 실행
- 관리형 PostgreSQL 공급자/상품/region/private network
- 실제 provider CA와 endpoint
- reverse proxy 제품, DNS, certificate 운영 방식
- 실제 production secret 값

## 계속 금지

- 실제 production env/secret/CA/cert/key/registry credential 생성·입력·커밋
- 정확한 preparation SHA 승인과 GitHub live 재확인 전 source-controlled gate 변경 또는 workflow 실행
- Docker login/pull/build/push/up/down 또는 resource 변경
- 실제 managed DB 연결
- PostgreSQL `max_connections` 변경
- 자동 migration 추가

기호는 `owner-only-source-controlled-two-step`을 선택했고 dependency/frontend 입력 잠금도 완료했습니다. 정확한 preparation SHA 승인과 GitHub live 재확인 전에는 source-controlled gate를 `false`로 유지합니다.
