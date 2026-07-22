# Backend image GHCR policy — v329

## 고정값

```txt
version: v329.fourth-owner-only-attempt-recorded-provenance-inspection-failed
remote: https://github.com/gihohoho/upgrade-rpg.git
repository: ghcr.io/gihohoho/upgrade-rpg-backend
visibility/platform: private / linux/amd64
credential: GitHub Actions GITHUB_TOKEN
reference mode: digest-only
lifecycle: attempt-recorded / publishReviewerGateReady=false
```

`owner-only-source-controlled-two-step` source-controlled lifecycle gate를 사용합니다. authorization은 승인된 preparation의 직접 자식이며 lifecycle 파일만 변경합니다. workflow는 repository owner, `run_attempt=1`, single dispatch만 허용하고 접수 즉시 immediate closure로 gate를 닫습니다. rerun은 금지합니다. 종료 뒤 별도 `attempt-recorded` commit이 정확한 `closureCommitSha`와 실제 run/digest/signature 증거를 남깁니다. 일반 R 계약 next stage는 `review-recorded-workflow-attempt-evidence`입니다.

## 3차 실행 기록

- preparation `b35dfacf427162b348a6bd29eb030778edc7741c`
- authorization `04e002060e576f19f4d8687b33635a414486206d`
- closure `64e5ae0f5e5385ba00df16bb10ac33789ca3760a`
- evidence `303a2ed01c69c29894efdcde4ead6c2291c3d8bc`
- run `29883012957`: failure at local Trivy HIGH/CRITICAL gate
- image build와 SPDX SBOM 성공, 27건 발견
- artifact `8515504259`, SHA-256 `6a5dfd4cd96754fd365323c7c6a7d1edf18542b5e5729e44220d7bf21ace4c50`
- publish skipped, login/push/provenance/Cosign 미실행, digest 없음, signature 미검증

## Fail-closed 원칙

- exact dependency와 action SHA를 유지합니다.
- root `.dockerignore`는 `.env`/`*.env`/`.envrc`를 제외하고 재포함을 금지합니다.
- `backend/Dockerfile.production.dockerignore`는 만들지 않습니다.
- Trivy `--ignore-unfixed=false` 및 HIGH/CRITICAL gate를 자동 완화하지 않습니다.
- byte-for-byte deterministic image를 보장한다고 주장하지 않습니다.
- 모든 검증을 통과하고 Cosign 확인까지 끝난 exact digest만 후보로 사용합니다.

## v328 runtime focused fix

기반 이미지는 Python 3.11.15 Alpine 3.23의 `linux/amd64` manifest digest로 고정했습니다. Ubuntu 검증은 manylinux lock, 운영 빌드는 musllinux lock을 사용합니다. 최종 runtime은 비루트 UID/GID 65532로 실행하며 pip/setuptools/wheel/ensurepip을 포함하지 않습니다. 사용되지 않는 `python-jose[cryptography]`도 제거했습니다. 로컬 Trivy 0.70 동일 gate 결과는 HIGH/CRITICAL 0건입니다.

4차 run은 GHCR push까지 성공해 digest `sha256:6e4aefad0cdf1767670b7f736477dd9e00f17bf49a03fa471828df6667c41149`를 만들었지만 SLSA v1 provenance 경로 검사에서 실패했습니다. exact-digest Trivy와 Cosign은 미실행이므로 이 digest는 검증 완료 후보가 아닙니다.

다음 안전 단계는 `review-recorded-provenance-inspection-evidence`입니다. focused fix와 새 workflow는 별도 승인 전 실행하지 않습니다.
