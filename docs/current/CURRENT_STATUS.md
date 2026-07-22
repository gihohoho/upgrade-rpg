# Current Status — v327

## 현재 결과

```txt
latest: v327.third-owner-only-attempt-recorded-vulnerability-gated
strict result: github-actions-ghcr-owner-only-attempt-recorded-publish-gated
next safe stage: review-recorded-vulnerability-gate-evidence
GitHub remote: https://github.com/gihohoho/upgrade-rpg.git
GHCR repository: ghcr.io/gihohoho/upgrade-rpg-backend
lifecycle: attempt-recorded
publishReviewerGateReady: false
```

CI credential은 GitHub Actions `GITHUB_TOKEN`이고 local PAT는 deferred입니다. workflow는 `deploy/github-actions-ghcr-publish-lifecycle.json`의 `owner-only-source-controlled-two-step` source-controlled lifecycle gate를 사용하며 `run_attempt=1`, single dispatch, immediate closure, rerun 금지를 강제합니다. 일반 R 상태 계약의 다음 단계 `review-recorded-workflow-attempt-evidence`는 유지하고, 현재 구체적 단계는 `review-recorded-vulnerability-gate-evidence`입니다.

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

## 다음 단계

artifact를 근거로 newer exact base digest, runtime image 최소화/multi-stage, Python dependency 업데이트를 검토합니다. focused fix와 새 preparation/workflow는 기호의 별도 승인 뒤 진행합니다. 현재 필요한 extension·설치·추가 권한은 없고 서버 재시작도 불필요합니다.
