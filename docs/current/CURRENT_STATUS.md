# Current Status — v328

## 현재 결과

```txt
latest: v328.alpine-musllinux-runtime-minimization-preparation
strict result: github-actions-ghcr-owner-only-runtime-minimization-preparation-ready-publish-gated
next safe stage: review-and-approve-exact-runtime-minimization-preparation-sha
GitHub remote: https://github.com/gihohoho/upgrade-rpg.git
GHCR repository: ghcr.io/gihohoho/upgrade-rpg-backend
lifecycle: preparation-closed
publishReviewerGateReady: false
```

CI credential은 GitHub Actions `GITHUB_TOKEN`이고 local PAT는 deferred입니다. workflow는 `deploy/github-actions-ghcr-publish-lifecycle.json`의 `owner-only-source-controlled-two-step` source-controlled lifecycle gate를 사용하며 `run_attempt=1`, single dispatch, immediate closure, rerun 금지를 강제합니다. 일반 R 상태 계약의 다음 단계 `review-recorded-workflow-attempt-evidence`는 유지하고, 현재 구체적 단계는 `review-and-approve-exact-runtime-minimization-preparation-sha`입니다.

## 세 번째 실행

- 승인 preparation `b35dfacf427162b348a6bd29eb030778edc7741c`
- authorization `04e002060e576f19f4d8687b33635a414486206d`
- closure `64e5ae0f5e5385ba00df16bb10ac33789ca3760a`
- evidence `303a2ed01c69c29894efdcde4ead6c2291c3d8bc`
- run `29883012957`: completed/failure
- validation, repository checks, local image build, SPDX SBOM 성공
- Trivy HIGH/CRITICAL gate: 27건(Debian 24, Python 3)으로 실패
- artifact `8515504259`, SHA-256 `6a5dfd4cd96754fd365323c7c6a7d1edf18542b5e5729e44220d7bf21ace4c50`, 14일 보존
- publish job skipped: GHCR login/push/provenance/Cosign 미실행, digest 없음, signature 미검증

Trivy 기준 fixed version이 있는 항목은 `jaraco.context 6.1.0`, `wheel 0.46.2` 두 건이며 25건은 현재 fixed version이 없습니다. `--ignore-unfixed=false`와 HIGH/CRITICAL gate는 의도대로 작동했으므로 자동 완화하지 않습니다.

## GitHub 설정

2026-07-22T01:21:58Z 기준 allowlist/full SHA, 기본 token read-only, fork write token/secret false, `ghcr-production-publish` main-only와 secrets/variables 0/0을 재확인했습니다. native required reviewer/prevent self-review는 비공개 개인 저장소 제약으로 없습니다.

## 운영·개발 경계

- target `linux/amd64`, private GHCR
- managed PostgreSQL + provider CA `verify-full` + external reverse proxy HTTPS + backend 1/1
- Alembic current `v295_initial_schema`, 새 revision 필요 없음
- Vue GET read-only 외 Preview/Apply/write/auth 보류
- DB/Alembic/auth/API write/게임/production Compose·deploy는 별도 요청 전 금지
- actual secret/token/PAT/credential은 파일·Git·로그·채팅·artifact에 기록하지 않음

## v328 focused fix 준비 결과

- exact base: `python:3.11.15-alpine3.23@sha256:ac0151f0eec4b7ba78bc47d337f328c6db706e7255b35b2327c2749f058c82fe`
- Ubuntu 검증용 manylinux lock과 운영용 musllinux lock을 분리하고 모두 SHA-256으로 고정했습니다.
- multi-stage build와 UID/GID `65532` 비루트 실행을 적용하고 최종 runtime에서 pip/setuptools/wheel/ensurepip을 제거했습니다.
- 앱에서 사용되지 않는 `python-jose[cryptography]`와 전이 의존성 8개를 runtime에서 제거했습니다.
- 로컬 linux/amd64 후보는 약 40.2MB이며 Python 3.11.15와 앱 핵심 import를 확인했습니다.
- Trivy 0.70 동일 정책 `HIGH,CRITICAL`, `--ignore-unfixed=false` 결과는 OS 0건, Python 0건입니다.
- Distroless Debian 12 후보는 실제 동일 검사에서 41건으로 실패해 채택하지 않았습니다.
- lifecycle은 `preparation-closed`, 승인 SHA는 `null`, 새 workflow는 미실행입니다.

다음 단계는 준비 commit의 정확한 40자 SHA 승인입니다. 현재 필요한 extension·설치·추가 권한은 없고 서버 재시작도 불필요합니다.

검증은 기호의 요청에 따라 위험도 기반 최소 범위로 실행합니다. 문서·handoff·상태값 변경에는 관련 strict checker와 handoff smoke만 사용하고 전체 core smoke는 실행하지 않습니다. 전체 smoke는 핵심 로직·DB/Alembic·API 계약·공통 구조·여러 영역 변경 또는 실제 배포 후보 직전에만 1회 실행합니다.
