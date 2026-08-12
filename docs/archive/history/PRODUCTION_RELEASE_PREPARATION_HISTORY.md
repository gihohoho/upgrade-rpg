# 운영·공개 배포 준비 역사

> 완료된 상세 문서를 검색 가능한 한 파일로 통합한 읽기 전용 역사입니다.
> 현재 판단에는 `docs/current/`와 `docs/generated/`를 사용하세요.
> 원본 파일은 Git commit `270d57bd234ede18cee7168f4b5da36b1a08df18` 이전 이력에서 복원할 수 있습니다.

---

## 원본: `docs/current/RENDER_ACCOUNT_AND_REGISTRY_CREDENTIAL_PLAN.md`

# Render account and registry credential plan — v338

## 읽기 전용 확인 결과

2026-07-22T15:59:18Z 기준 Render Dashboard를 읽기 전용으로 확인했습니다.

- workspace plan: `Hobby (legacy)`
- payment method: `No card on file`
- billing information: 없음
- 기존 service: 1개, 사용자가 직접 suspend, active 0
- 새 Web Service source: `Existing Image` 지원
- private registry: GitHub Container Registry 지원
- 현재 registry credential: 없음
- service/credential/token/payment/deploy mutation: 없음

sanitized evidence는 `deploy/review/render-account-readiness-v337.json`입니다. workspace ID, 기존 service 이름, 계정 정보, token, credential 값은 기록하지 않습니다.

## 추천 credential

기존 GitHub CLI OAuth token은 Render에 저장하지 않습니다. Render 전용 최소 권한 credential을 새로 사용합니다.

```txt
GitHub token type: Personal access token (classic)
Token note: render-upgrade-rpg-ghcr-read
Expiration: 365 days
Scope: read:packages only
repo/write:packages/delete:packages: off/off/off
Render credential name: upgrade-rpg-ghcr-read
Registry: GitHub
Username: gihohoho
Image: ghcr.io/gihohoho/upgrade-rpg-backend@sha256:ff939391517452a3ec477adaa0f8556d3525f9d0c6fb5f9d0df11d8f3d8461d2
```

GitHub Container Registry는 private image pull에 classic PAT의 `read:packages`를 요구합니다. Render도 private GitHub image credential에 `read:packages`를 요구합니다.

- https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
- https://render.com/docs/deploying-an-image

## 승인 범위 실행 결과 — 2026-07-23

기호가 아래 범위를 명시적으로 승인했고 모두 완료했습니다.

1. GitHub `Confirm access` 사용자 완료
2. dedicated classic PAT 생성: `read:packages` only, 만료일 2027-07-23
3. Render `upgrade-rpg-ghcr-read` credential 저장
4. verified exact digest를 입력해 `Connect` 성공
5. Render 서비스 설정 화면 진입 확인

첫 PAT는 브라우저 검사 출력에 값이 노출된 것을 감지해 Render에 저장하지 않고 즉시 GitHub에서 폐기했습니다. 교체 PAT는 값 출력 없이 Render로 직접 전달하고 GitHub의 token 표시 화면을 닫았습니다. 실제 값은 어떤 저장소 문서나 evidence에도 기록하지 않습니다.

sanitized 실행 evidence는 `deploy/review/render-private-ghcr-connect-v338.json`입니다.

이 승인에는 Web Service 최종 생성, initial deploy, 환경변수 주입, DB 생성/write/restore/migration이 포함되지 않습니다. Render `Create Web Service` 또는 `Deploy`는 별도 실행 준비 SHA 승인 전 누르지 않습니다.

---

## 원본: `docs/current/V351_PUBLIC_RELEASE_GATES.md`

# v351 공개 release gate — v355

## 현재 결론

v351 source의 master-data timeout 5초와 backend GZip 변경은 새 GHCR exact image로 게시됐고 공급망·isolated 검증과 Render 공개 배포·브라우저 통합 검증까지 통과했습니다.

```txt
source baseline: 81beaa0864c3422fb9fc2071b9c4965936ecafac
workflow run: 30226905547 / run_attempt=1 / success
lifecycle: attempt-recorded / gate=false / rerun forbidden
new exact image:
  ghcr.io/gihohoho/upgrade-rpg-backend@sha256:143be5eb21ec8c9318c7d0c4f3fbd5ac2de32439977a1d660c7247b6d3a507ac
isolated evidence:
  deploy/review/isolated-image-pull-validation-v353.json
Render backend/static deploy: approved / executed / live
content readiness: public no-fallback + guarded admin read-only verified
```

정적 계약은 `deploy/v351-public-release-gates.example.json`, fail-closed 검사는 `tools/check_v351_public_release_gates.py`입니다.

## 완료된 image 단계

사용자가 준비 SHA `b48dfd0751b12b1b3afb6474f9d35359ba2f8177`을 승인했습니다.

1. authorization `7578eb665c03ee0fcb9399929328ce684cdd1b31`
2. workflow run `30226905547` 접수
3. immediate closure `5d547126322dbe3c235e855cc9c2f7337342ae36`
4. evidence `5c842deec6d1f496679a144897f485b07428810b`
5. local/registry Trivy HIGH·CRITICAL 0건
6. SLSA BuildKit provenance, SPDX-2.3 SBOM 87 packages
7. Cosign GitHub OIDC sign/verify
8. isolated linux/amd64 runtime, UID 65532, system CA 119, health 200
9. 임시 container/network/local image cleanup

workflow는 한 번만 실행됐고 rerun하지 않습니다. Render와 DB는 이 단계에서 변경하지 않았습니다.

## v354 provider release 준비 — 완료된 역사

새 exact image를 기존 backend Web Service `srv-d9iro458nd3s73acgmsg`에 한 번 적용하고, v351 exact source를 기존 Static Site `srv-d9iu337aqgkc73am4lh0`에 한 번 배포하는 계약을 준비했습니다.

당시 상태는 둘 다 `prepared=true`, `approved=false`, `executed=false`였습니다. Static Site auto-deploy는 계속 꺼져 있습니다.

기호가 push된 v354 준비 commit `05f1af8ed1316e2cf0e0f39ac795b3ff60bccb62`를 별도 승인했고 다음을 정확히 한 번 수행했습니다.

1. clean pushed `main`과 계약 SHA 확인
2. backend existing-image exact digest 변경·수동 deploy 1회
3. `/api/v1/health`와 `/api/v1/health/db` read-only 확인
4. frontend exact source 수동 deploy 1회
5. `/index.html`, `/admin.html`, CORS 확인
6. 공개 master-data 무폴백과 관리자 guarded read-only 흐름 확인
7. sanitized evidence 기록

## v355 실행·검증 결과

- backend deploy: `dep-d9jeuf3eo5us73ba6cgg` / exact image / Live / 40.2초
- frontend deploy: `dep-d9jev7gu01pc73favje0` / exact v351 source / Live / 19.6초
- health/DB health: HTTP 200 / 200, DB health read-only 1회
- index/admin: HTTP 200 / 200
- CORS: exact frontend origin
- master-data: HTTP 200, 1,346ms, gzip, browser runtime applied, fallback 경고 없음
- admin: read-only, 11 domains / 729 rows, general write UI blocked, write key missing
- sanitized evidence: `deploy/review/render-v351-provider-release-v355.json`
- next safe stage: `select-first-content-and-balance-change-scope`

Render 설정 검사 출력에 backend/static deploy hook 값이 포함돼 두 hook을 즉시 재발급했습니다. 새 값은 기록하지 않았고 재발급은 추가 deploy를 만들지 않았습니다.

## 승인에 포함되지 않아 실행하지 않은 것

- DB write, restore, reset, seed
- Alembic revision, stamp, upgrade, downgrade
- admin write와 게임 콘텐츠·밸런스 변경
- custom domain, DNS, 결제 변경
- 자동 deploy, 자동 retry, 두 번째 deploy
- GitHub Actions 추가 dispatch 또는 rerun

실제 공개 게임이 backend master-data를 폴백 없이 로드하고 관리자 guarded read-only 흐름까지 검증됐습니다. 이제 첫 콘텐츠·밸런스 변경 범위를 기호와 선택하기 좋은 시점입니다.

현재 필요한 extension·권한·새 설치는 없습니다.

---

## 원본: `docs/archive/production-deployment/BACKEND_IMAGE_REGISTRY_BASE_SELECTION_V314.md`

# Backend image registry and base selection — v314

## 확정한 선택

```txt
registry: GitHub Container Registry (GHCR)
registry host: ghcr.io
repository: upgrade-rpg-backend
repository visibility: private
production target platform: linux/amd64
base image: python:3.11.15-slim-bookworm
base image linux/amd64 manifest digest: sha256:28255a3ace7eb4c48bc1b57b90af29e1bc82b4fd6c60614a8e3dce61b87ff941
```

## GitHub namespace 주의

현재 repository 주소는 아래 template입니다.

```txt
ghcr.io/<github-account-or-organization>/upgrade-rpg-backend
```

`<github-account-or-organization>`에는 **실제로 이 프로젝트 이미지를 소유할 GitHub 사용자 이름 또는 Organization 이름**만 넣습니다. assistant가 이름을 추측하거나 임의로 만들지 않습니다.

현재 상태:

```txt
namespace resolved: no
actual namespace applied: no
```

따라서 placeholder가 남아 있는 동안에는 registry login, image build, image push를 승인하지 않습니다. 실제 namespace가 정해지면 최종 주소는 다음 형태입니다.

```txt
ghcr.io/실제-GitHub-사용자명-또는-조직명/upgrade-rpg-backend
```

## production image reference

운영 Compose는 최종 backend image도 tag가 아니라 exact digest로만 받습니다.

```txt
ghcr.io/<github-account-or-organization>/upgrade-rpg-backend@sha256:<approved-64-hex-digest>
```

여기서 앞의 namespace placeholder와 뒤의 backend image digest는 아직 실제 값이 아닙니다.

## production base image

로컬 개발 호환성을 위해 기존 `backend/Dockerfile`은 `python:3.11-slim` 상태로 보존했습니다. 운영 빌드 전용 파일을 별도로 추가했습니다.

```txt
backend/Dockerfile.production
```

운영 Dockerfile의 첫 줄:

```dockerfile
FROM python:3.11.15-slim-bookworm@sha256:28255a3ace7eb4c48bc1b57b90af29e1bc82b4fd6c60614a8e3dce61b87ff941 AS runtime
```

- `python:3.11.15-slim-bookworm`: 사람이 읽는 고정 tag
- `sha256:28255a3ace7eb4c48bc1b57b90af29e1bc82b4fd6c60614a8e3dce61b87ff941`: `linux/amd64` manifest 고유번호
- `sha256:b18992999dbe963a45a8a4da40ac2b1975be1a776d939d098c647482bcad5cba`: Docker Hub multi-platform index 고유번호

이번 v314에서는 target platform이 `linux/amd64`이므로 운영 Dockerfile은 해당 manifest digest를 직접 고정합니다.

## 승인 상태

```txt
base image digest approved: yes
credential storage decision: deferred
pull/build/push approved: no/no/no
pull/build/push executed: no/no/no
container start approved: no
actual registry credential applied: no
actual Docker/DB/Alembic mutation: no
```

## 다음 안전 단계

```txt
resolve-ghcr-namespace-and-review-credential-storage
```

다음 단계에서는 실제 GitHub 사용자 이름 또는 Organization 이름을 확인하고, credential을 Git에 저장하지 않는 보관 방법만 먼저 결정합니다. 그 후에도 pull/build/push는 각각 별도 승인 경계입니다.

## 읽기 전용 검사

실행 위치: 프로젝트 루트
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_backend_image_registry_base_selection.py --strict
```

정상 결과 핵심:

```txt
registry provider/host: github-container-registry / ghcr.io
repository template: ghcr.io/<github-account-or-organization>/upgrade-rpg-backend
namespace resolved: False
target platform: linux/amd64
base image digest approved: True
image pull/build/push approved: no/no/no
result: ghcr-amd64-base-image-selection-verified-namespace-required-pull-build-blocked
next safe stage: resolve-ghcr-namespace-and-review-credential-storage
```

---

## 원본: `docs/archive/production-deployment/BACKEND_IMAGE_SOURCE_DIGEST_POLICY_V313.md`

# Backend image source and digest policy — v313

## v314 후속 상태

이 문서는 v313에서 선택 전 안전 경계를 만든 기록입니다. 현재 선택값은 `BACKEND_IMAGE_REGISTRY_BASE_SELECTION.md`를 우선합니다.

```txt
registry: GitHub Container Registry (ghcr.io)
repository template: ghcr.io/<github-account-or-organization>/upgrade-rpg-backend
namespace resolved: no
target platform: linux/amd64
base image digest approved: yes
pull/build/push approved: no/no/no
```

## 이번 단계에서 확정한 것

기호 PC에서 v312 Compose config render-only가 정상 통과했습니다. 해당 출력 중 민감정보가 없는 안전 요약만 다음 파일에 기록했습니다.

```txt
deploy/review/production-compose-config-render-v312.json
```

고정된 결과:

```txt
rendered services: backend
host ports/build/named volumes absent: True/True/True
managed DB service absent / backend replicas: True/1
digest/production guard/TLS/edge rendered: True/True/True/True
image pull/build executed: no
container/network/volume mutation executed: no
DB/Alembic mutation executed: no
```

raw Compose render, 실제 env, secret, registry credential은 저장하지 않았습니다.

## production backend image 계약

운영 Compose에서 사용할 backend image는 tag가 아니라 exact digest만 허용합니다.

```txt
production reference mode: digest-only
<approved-registry>/<approved-namespace>/upgrade-rpg-backend@sha256:<approved-64-hex-digest>
```

필수 기록 항목:

- 승인된 registry provider
- namespace와 repository identity
- 빌드한 Git commit 40자리 SHA
- target platform
- base image exact digest
- 생성된 backend image exact digest
- SBOM 결과
- build provenance 결과
- signature verification 결과
- vulnerability review 결과

## 현재 보류된 선택

```txt
registry provider: deferred
repository identity: placeholder only
target platform: deferred
base image digest approved: no
actual backend image digest approved: no
```

현재 Dockerfile의 base image inventory는 다음입니다.

```txt
python:3.11-slim
```

이 값은 mutable tag이므로 production build 승인 조건을 만족하지 않습니다. base image exact digest를 별도 검토하기 전에는 production image build를 실행하지 않습니다. 로컬 Dockerfile을 이번 단계에서 임의 digest로 변경하지 않은 이유는 승인되지 않은 digest를 고정하거나 로컬 개발 동작을 깨뜨리지 않기 위해서입니다.

## 공급망 검증 게이트

release 전에 다음 네 가지가 모두 필요합니다.

```txt
SBOM required: yes
provenance required: yes
signature verification required: yes
vulnerability review required: yes
```

사용할 구체적인 registry·서명·scan 도구는 provider와 배포 환경을 정한 뒤 결정합니다. 실제 도구 설치나 registry 로그인은 이번 단계에 포함하지 않습니다.

## 승인 상태

```txt
config render evidence verified: yes
image pull/build/push approved: no/no/no
image pull/build/push executed: no/no/no
container start approved: no
actual registry credential applied: no
actual image digest applied: no
actual production value applied: no
```

## 다음 안전 단계

```txt
select-registry-repository-platform-and-base-image-digest
```

다음에는 아래 네 항목을 먼저 확정합니다.

1. registry provider
2. repository namespace/name
3. production target platform
4. `python:3.11-slim`에 대응하는 승인된 base image digest

그 후에도 `pull`, `build`, `push`는 각각 분리된 승인 경계로 실행합니다.

## 읽기 전용 검사

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
base image digest pinned/approved: False/False
supply-chain gates required: 4/4
image pull/build/push approved: no/no/no
result: backend-image-source-digest-policy-verified-provider-and-build-blocked
next safe stage: select-registry-repository-platform-and-base-image-digest
```

---

## 원본: `docs/archive/production-deployment/BACKEND_READY_V320.md`

# Backend readiness — v320

## 완료

- FastAPI + PostgreSQL async runtime
- Alembic baseline `v295_initial_schema`
- live DB health, pool, lifecycle, production guard
- 관리형 PostgreSQL + provider CA `verify-full`
- 외부 reverse proxy HTTPS
- backend 1 replica / 1 worker
- production Compose config render-only 기호 PC 실제 통과
- GHCR/private/digest-only backend image 정책
- GitHub/GHCR namespace: `gihohoho`
- repository: `ghcr.io/gihohoho/upgrade-rpg-backend`
- target platform: `linux/amd64`
- production base image exact manifest digest 승인
- 로컬 Dockerfile 보존 + `backend/Dockerfile.production` 분리
- Codex용 `AGENTS.md`, GitHub Actions/GHCR workflow와 YAML AST fail-closed 검사
- ChatGPT Codex Connector의 `gihohoho/upgrade-rpg` 단일 repository 연결과 조회 검증
- repository Actions 8개 full-SHA allowlist와 full-length SHA 강제 적용
- `ghcr-production-publish` environment 생성과 `main` 전용 rule 적용
- checksum-pinned Trivy, BuildKit provenance/SBOM, Cosign exact-digest 검증 설계
- source-controlled reviewer hard gate `false`

## 아직 미완료

- 비공개 저장소 게시 승인 모델 선택: `github-enterprise-cloud-required-reviewer` / `owner-only-source-controlled-two-step` / `keep-publishing-disabled`
- 선택한 승인 모델의 보호 절차 구성과 검증
- Python dependency/build-system hash lock, pinned pip, immutable Dockerfile frontend 구성·검증
- GitHub Actions/environment live 설정 재확인
- 게시 승인 모델과 재현성 gate가 모두 검증된 뒤 source-controlled gate 변경과 첫 workflow 실행
- 실제 backend image build digest
- 관리형 PostgreSQL 공급자/상품/region/private network
- actual provider CA/endpoint/secret
- reverse proxy 제품/DNS/certificate
- image login/build/push 실행 결과와 isolated container start
- 실제 배포

CI credential 우선안은 GitHub Actions `GITHUB_TOKEN`입니다. 실제 token/PAT/credential은 저장소·채팅에 넣지 않으며, local credential은 아직 deferred입니다.

GitHub Free/Pro/Team의 required reviewer는 공개 저장소에서만 지원되므로, 현재 비공개 저장소에 collaborator를 추가하는 것만으로는 보호 규칙을 만들 수 없습니다. 승인 모델과 재현성 gate를 모두 구성·검증하고 GitHub 설정을 live 재확인하기 전에는 `PUBLISH_REVIEWER_GATE_READY`를 리터럴 `"false"`로 유지하며 workflow를 실행하지 않습니다.

---

## 원본: `docs/archive/production-deployment/README.md`

# Production Deployment Archive

이 폴더는 운영 배포 준비 과정에서 완료되어 현재 판단 문서에서 내려온 단계 기록을 보관합니다.
현재 작업 판단은 `docs/current/`와 루트 `AGENTS.md`를 우선합니다.
