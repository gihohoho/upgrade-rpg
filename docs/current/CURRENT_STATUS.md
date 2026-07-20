# Current Status — v321

## 현재 기준

- 최신 작업: `v321.owner-only-reproducibility-locked-publish-gated`
- handoff: current repository + Git `main` (ZIP 기본 생성 없음)
- readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`
- 개발 서버: 정상 프로세스가 있으면 `127.0.0.1:8000`, `127.0.0.1:5173` 계속 재사용

## 고정 PostgreSQL/Alembic 상태

```txt
classification: alembic-managed-baseline-complete
source DB: rpg_game
source public tables/rows: 23/749
source application tables/rows: 22/748
current revision: v295_initial_schema
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
schema digest: 7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921
data digest: ecb19e57283dc6b780426339bfc46f2bac14da63a618249808f30132508f9244
next revision required: no
```

## 운영 방향

```txt
managed PostgreSQL + provider CA verify-full
external reverse proxy HTTPS
backend replicas/workers: 1/1
max_connections review candidate: 40
Compose config render: 기호 PC 통과
```

## GHCR와 GitHub Actions

```txt
GitHub remote: https://github.com/gihohoho/upgrade-rpg.git
namespace: gihohoho
repository: ghcr.io/gihohoho/upgrade-rpg-backend
visibility: private
target platform: linux/amd64
base image digest approved: yes
CI credential strategy: github-actions-github-token
local credential strategy: deferred
workflow file/creation approved: yes/yes
workflow execution approved/executed: yes/no
CI workflow/login/build/push approved: yes/yes/yes/yes
CI login/build/push executed: no/no/no
repository Actions allowlist/full SHA: configured/configured
publish environment/main-only: present/configured
required reviewer/prevent self-review: missing/missing
publish approval model: owner-only-source-controlled-two-step
PUBLISH_REVIEWER_GATE_READY: source-controlled false
dependency/frontend input lock: complete (exact versions + SHA-256)
exact preparation SHA approval: pending
GitHub repository settings evidence: 2026-07-15 browser snapshot (not live API check)
```

## v321 GitHub 설정과 공급망 잠금 결과

- Codex GitHub 연결은 `gihohoho/upgrade-rpg` selected repository 하나로 제한되어 있습니다.
- 외부 action은 승인한 8개 repository의 전체 40자리 SHA만 허용합니다.
- 기본 `GITHUB_TOKEN`은 contents/packages read-only이고 Actions의 PR 생성·승인은 꺼져 있습니다.
- `ghcr-production-publish` environment는 존재하며 deployment branch는 `main`만 허용합니다.
- owner 외 collaborator는 0명이고 required reviewer/prevent self-review 설정 UI가 없어 보호가 미완성입니다.
- environment secret과 variable은 0개입니다.
- 위 repository 설정은 2026-07-15 브라우저에서 확인한 snapshot입니다. 로컬 strict checker는 GitHub API를 실시간 조회하지 않으므로 gate 변경 직전에 live 설정을 다시 확인해야 합니다.
- workflow publish job의 첫 단계가 `PUBLISH_REVIEWER_GATE_READY=true`를 확인하며, 현재 파일에 리터럴 `"false"`로 고정되어 GHCR login 전에 실패합니다. repository/environment variable로 우회할 수 없습니다.
- workflow 전체 UTF-8 소스는 SHA-256 `9c3384f5f8d879320d41b04833a63842744e55c14cd12743c9aea0a3a74e8c5a`, 파싱된 실행 의미 구조는 SHA-256 `9a7af533b42854977897b26fe0aae364667f9be65a7d9dfab4c51a2bf1c31652`로 정적 검사기에 고정되어, step 추가·삭제·재배열이나 shell 본문 변조가 별도 검토 없이 통과하지 않습니다.
- action/run step별 해시와 exact env/key, parsed secret 경로 allowlist도 별도로 검사합니다. 유일한 secret 표현식 허용 위치는 GHCR login의 `${{ secrets.GITHUB_TOKEN }}` password입니다.
- root Docker build context에서 `.env`, `.env.*`, `*.env`, `*.env.*`, `.envrc`를 모두 제외하며, env 파일 재포함 규칙을 금지합니다.

## 공급망 workflow

`.github/workflows/publish-backend-ghcr.yml`은 `workflow_dispatch` 전용입니다. 40자리 source SHA와 `main`, 확인 입력을 검사한 뒤 정적 검사, 로컬 OCI build, SPDX SBOM, checksum-pinned Trivy `HIGH,CRITICAL` gate를 거칩니다. 게시가 허용된 이후에도 push된 exact digest를 다시 Trivy로 검사하고 Docker BuildKit `mode=max` provenance/SBOM을 검사한 뒤에만 Sigstore Cosign keyless 서명과 identity/issuer 검증을 수행합니다.

개인 비공개 저장소에서는 GitHub Artifact Attestations API를 사용할 수 없어 `actions/attest`와 `attestations: write`는 사용하지 않습니다.

Python application/build dependency는 CPython 3.11 Linux/amd64용 exact version과 선택 wheel SHA-256으로 잠겼습니다. pip는 `26.1.2`, build-system은 `setuptools 80.10.2`와 `wheel 0.46.3`, Dockerfile frontend는 `docker/dockerfile:1.21.0@sha256:27f9262d43452075f3c410287a2c43f5ef1bf7ec2bb06e8c9eeb1b8d453087bc`로 고정했습니다. source distribution은 금지하고 `--require-hashes` 다운로드 검증을 사용합니다. 다만 파일 timestamp와 builder 구현까지 포함한 byte-for-byte 동일 image를 보장한다고 과장하지는 않습니다.

## 계속 적용되는 작업 권한

- Codex는 실행 중인 개발 서버를 재사용하고 VS Code/Codex 터미널을 사용할 수 있습니다.
- GitHub Actions/workflow/SHA/environment/variable 설정은 Codex가 목적 범위 안에서 처리합니다.
- 숨김 파일과 `.env`는 필요한 경우 다룰 수 있지만 실제 secret은 Git·로그·채팅·artifact에 노출하지 않습니다.
- 나중에 바꿀 보안 항목은 `docs/current/SECURITY_ROTATION_AND_GITHUB_GATES.md`에 기록합니다.
- 필요한 extension, 권한, 설치 또는 사용자 계정 작업은 계속 요청합니다.

## 현재 차단과 다음 단계

기호는 2026-07-20에 `owner-only-source-controlled-two-step`을 선택했고 dependency/frontend 입력 잠금도 완료됐습니다. workflow와 CI registry 작업은 아직 실행하지 않았습니다. 다음 단계는 이 v321 준비 작업을 commit·push한 뒤 Codex가 정확한 40자 preparation SHA와 범위를 제시하고, 기호가 그 SHA를 명시적으로 승인하는 것입니다. 그 승인 전에는 gate를 바꾸지 않습니다. 승인 뒤에도 GitHub Actions allowlist/full SHA와 environment main-only 설정을 live 재확인하고, 별도 authorization commit에서만 gate를 열어 한 번 실행한 뒤 성공·실패와 관계없이 즉시 다시 닫습니다.

정상 strict 결과:

```txt
result: github-actions-ghcr-owner-only-reproducibility-ready-publish-gated
next safe stage: review-and-approve-exact-preparation-sha
```
