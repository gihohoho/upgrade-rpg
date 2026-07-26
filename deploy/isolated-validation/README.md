# Isolated production validation plan and evidence — v342

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
- production Dockerfile base: `python:3.11.15-alpine3.23@sha256:ac0151f0eec4b7ba78bc47d337f328c6db706e7255b35b2327c2749f058c82fe`
- local `backend/Dockerfile`은 보존

선택 과정에서는 registry 또는 Docker mutation을 실행하지 않았습니다. `gihohoho`는 기호가 직접 확인한 고정 namespace입니다.

## Stage 2C — 완료: credential/workflow와 repository 보호 준비

- CI credential 우선안: GitHub Actions `GITHUB_TOKEN`
- local credential/PAT: deferred
- `.github/workflows/publish-backend-ghcr.yml` 생성: yes
- CI workflow/login/build/push 승인: yes/yes/yes/yes
- 실제 workflow/login/build/push 실행: no/no/no/no
- 최소 permissions, 안전 trigger, supply-chain gate, 8개 action full-SHA 설정 완료
- Codex GitHub App `gihohoho/upgrade-rpg` 단일 repository 연결
- `ghcr-production-publish`와 `main` rule 생성, required reviewer는 미구성
- GitHub Free/Pro/Team의 required reviewer는 공개 저장소에서만 지원되어 비공개 저장소에 collaborator를 추가하는 것만으로는 해결되지 않음
- source-controlled reviewer gate `false`, GHCR login 전 차단
- 선택 완료: `owner-only-source-controlled-two-step`; dependency/frontend 입력 잠금 완료
- 다음 단계: 정확한 preparation SHA 승인 후 GitHub live 설정 재확인과 별도 authorization commit

## Stage 2D — 게시 승인 모델 구성·검증 뒤 실행 결과 확인: build/push/verify

- base image pull
- backend image build
- SBOM/provenance/scan
- registry push
- pushed digest/signature 검증

각 작업은 하나씩 실행하고 결과를 확인한 뒤 다음으로 이동합니다.

정확한 preparation SHA를 기호가 승인하고 GitHub 설정을 live 재확인하기 전에는 source-controlled gate를 `false`로 유지하고 workflow를 실행하지 않습니다. authorization당 한 번 실행한 뒤 gate를 즉시 다시 닫습니다.

## Stage 3 — 완료: isolated start

- 고유 project/network 이름 사용
- 실제 production DB/secret 대신 승인된 isolated test 자원 사용
- host port 공개 없음
- Alembic 자동 실행 없음
- schema/data write 검증 없음

## Stage 4 — 완료: isolated cleanup

실제 생성 목록을 먼저 확인하고 해당 isolated resource만 제거합니다. 기존 local PostgreSQL container/volume은 절대 변경하지 않습니다.

## v321 당시 고정 상태

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

## v333 현재 결과

```txt
exact digest pull approved/executed: yes/yes
isolated container execution approved/executed: yes/yes
host ports/volumes: none/none
internal network/read-only rootfs/non-root: yes/yes/yes
health: /api/v1/health 200
actual DB connection/Alembic: no/no
temporary container/network/local image cleanup: yes/yes/yes
production runtime/deploy applied: no/no
next safe stage: review-isolated-validation-and-approve-production-deploy-plan
```

현재 sanitized evidence는 `deploy/review/isolated-image-pull-validation-v342.json`에 있습니다. v333 evidence는 이전 verified image 기록으로 보존합니다. GitHub CLI/Docker credential store의 실제 credential 값은 기록하지 않습니다.
