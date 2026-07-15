# Isolated production validation plan — v316

이 폴더는 승인 경계와 안전한 검사 도구만 보관합니다. 실제 production secret, CA, certificate, key, registry credential 또는 production env 파일을 두지 않습니다.

## Stage 0 — 완료: 정적 검증과 운영 방향 선택

- 관리형 PostgreSQL 선택
- 외부 reverse proxy HTTPS 선택
- backend 1 replica / 1 Uvicorn worker 선택
- pool 5 + overflow 10, `max_connections` review 후보 40 유지
- 실제 Docker, DB, Alembic mutation 없음

## Stage 1 — 완료: config render only

기호 PC에서 아래 안전 wrapper가 통과했습니다.

```txt
python tools/render_production_compose_config.py --execute --confirm-stage v312-config-render-only
```

완료 상태:

```txt
compose config render approved/executed: yes/yes
rendered services: backend
host ports/build/named volumes absent: True/True/True
image pull/build executed: no
container/image/network/volume mutation executed: no
```

민감정보 없는 요약 증거만 `deploy/review/production-compose-config-render-v312.json`에 기록했습니다. raw render는 저장하지 않았습니다.

## Stage 2A — 완료: image source/digest policy

- production image는 digest-only
- source commit, base image digest, backend image digest 기록 필수
- SBOM/provenance/signature/vulnerability review 필수
- 실제 image build/push는 실행하지 않음

## Stage 2B — 완료: GHCR/platform/base digest/namespace 선택

- registry provider: GitHub Container Registry (`ghcr.io`)
- namespace: `gihohoho`
- repository: `ghcr.io/gihohoho/upgrade-rpg-backend`
- repository visibility: private
- target platform: `linux/amd64`
- production Dockerfile base: `python:3.11.15-slim-bookworm@sha256:28255a3ace7eb4c48bc1b57b90af29e1bc82b4fd6c60614a8e3dce61b87ff941`
- local `backend/Dockerfile`은 보존

선택 과정에서는 registry 또는 Docker mutation을 실행하지 않았습니다. `gihohoho`는 기호가 직접 확인한 고정 namespace입니다.

## Stage 2C — 현재: credential/workflow 정적 계획

- CI credential 우선안: GitHub Actions `GITHUB_TOKEN`
- local credential/PAT: deferred
- `.github/workflows/` 생성 승인: no
- Docker login/pull/build/push 승인: no/no/no/no
- 다음 단계: 최소 permissions, 안전 trigger, supply-chain gate를 문서와 fail-closed 검사로 설계

## Stage 2D — 각각 별도 승인 필요: pull/build/push

- base image pull
- backend image build
- SBOM/provenance/scan
- registry push
- pushed digest/signature 검증

각 작업은 하나씩 실행하고 결과를 확인한 뒤 다음으로 이동합니다.

## Stage 3 — 별도 승인 필요: isolated start

- 고유 project/network 이름 사용
- 실제 production DB/secret 대신 승인된 isolated test 자원 사용
- host port 공개 없음
- Alembic 자동 실행 없음
- schema/data write 검증 없음

## Stage 4 — 별도 승인 필요: isolated cleanup

실제 생성 목록을 먼저 확인하고 해당 isolated resource만 제거합니다. 기존 local PostgreSQL container/volume은 절대 변경하지 않습니다.

## 현재 고정 상태

```txt
actual Docker config command executed on user PC: yes (config only)
actual Docker image pull/build/push executed: no/no/no
actual Docker container/network/volume mutation executed: no
actual production secret/registry credential used: no
actual CA/certificate/key created: no
actual DB connection/write executed: no
actual Alembic command executed: no
isolated container execution approved: no
```
