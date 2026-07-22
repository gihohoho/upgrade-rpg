# Upgrade RPG Codex handoff — v327

## 작업 원칙

- 시작할 때 `AGENTS.md`, 이 파일, `docs/current/CURRENT_STATUS.md`를 먼저 읽습니다.
- 기호에게 한국어로 쉽게 설명하고 모든 명령 전에 실행 위치, Python `.venv` 상태, 새 설치 여부를 적습니다.
- 필요한 extension·권한·설치는 해결될 때까지 요청과 handoff 기록을 반복합니다.
- 실행 중인 개발 서버를 재사용하며 필요할 때만 재시작합니다.
- Codex가 검증 뒤 git add/commit/push까지 직접 합니다. ZIP과 Git 명령 안내는 제공하지 않습니다.
- actual secret/token/PAT/credential/CA/cert/key는 Git·채팅·로그·artifact에 넣지 않습니다.
- 검증은 변경 영역의 전용 checker/smoke 1회부터 시작하고 실패할 때만 확대합니다. 문서·handoff·상태값 변경에는 전체 core smoke를 실행하지 않습니다. 전체 `bash tools/run_smoke_core.sh`는 backend 핵심 로직, DB/Alembic, API 계약, 공통 구조, 여러 영역 변경 또는 실제 배포 후보 직전에만 1회 실행합니다.

## 현재 고정값

```txt
latest: v327.third-owner-only-attempt-recorded-vulnerability-gated
strict result: github-actions-ghcr-owner-only-attempt-recorded-publish-gated
next safe stage: review-recorded-vulnerability-gate-evidence
GitHub remote: https://github.com/gihohoho/upgrade-rpg.git
GHCR namespace: gihohoho
repository: ghcr.io/gihohoho/upgrade-rpg-backend
visibility/platform: private / linux/amd64
CI credential: GitHub Actions GITHUB_TOKEN
local credential/PAT: deferred
publish approval model: owner-only-source-controlled-two-step
source-controlled lifecycle gate: attempt-recorded / publishReviewerGateReady=false
workflow/login/build/push executed: yes/no/yes/no
```

운영 구조는 managed PostgreSQL + provider CA `verify-full` + external reverse proxy HTTPS + backend 1 replica/1 worker입니다. Vue는 GET read-only까지만 연결하며 Preview/Apply/write/auth는 보류합니다. Alembic current revision은 `v295_initial_schema`, 새 revision 필요 상태는 `no`입니다.

## Source-controlled lifecycle gate

경로: `deploy/github-actions-ghcr-publish-lifecycle.json`

- P `preparation-closed`
- A `authorization-open`
- C `authorization-closed-awaiting-evidence`
- R `attempt-recorded` (현재)

authorization은 승인된 preparation의 direct child이고 lifecycle 파일 하나만 변경합니다. workflow는 repository owner, `run_attempt=1`, GitHub API로 확인한 single dispatch만 허용하며 rerun은 금지합니다. run 접수 즉시 immediate closure commit으로 C 상태를 만들고 gate를 닫습니다. C는 자기 SHA를 기록할 수 없어 `closureCommitSha=null`이고, 종료 뒤 별도 R evidence commit이 부모 C의 정확한 `closureCommitSha`와 실제 run/digest/signature 결과를 기록합니다. 일반 계약 next stage `review-recorded-workflow-attempt-evidence`는 보존하며, 이번 구체적 next stage는 `review-recorded-vulnerability-gate-evidence`입니다.

## 세 번째 owner-only 시도

```txt
approved preparation: b35dfacf427162b348a6bd29eb030778edc7741c
authorization: 04e002060e576f19f4d8687b33635a414486206d
immediate closure: 64e5ae0f5e5385ba00df16bb10ac33789ca3760a
evidence record: 303a2ed01c69c29894efdcde4ead6c2291c3d8bc
run ID: 29883012957
run URL: https://github.com/gihohoho/upgrade-rpg/actions/runs/29883012957
run_attempt: 1
status/conclusion: completed / failure
image digest: null
signature verified: false
```

결과:

- validation과 repository check 전부 성공
- local linux/amd64 image build 성공
- SPDX SBOM 생성·구조 검사 성공
- checksum-pinned Trivy 설치 성공
- `Block HIGH and CRITICAL vulnerabilities in local image` 단계 실패
- 27건: Debian HIGH 18, Debian CRITICAL 6, Python HIGH 3
- Trivy `FixedVersion` 기준 fixable 2건, unfixed 25건
- artifact ID `8515504259`, 이름 `backend-sbom-and-vulnerability-report-04e002060e576f19f4d8687b33635a414486206d`, 472046 bytes
- artifact SHA-256 `6a5dfd4cd96754fd365323c7c6a7d1edf18542b5e5729e44220d7bf21ace4c50`, 만료 `2026-08-05T01:26:39Z`
- artifact 내용: `sbom.spdx.json`, `trivy-results.json`
- publish job 전체 skipped: GHCR login/push, provenance, Cosign 미실행
- registry mutation 없음, image digest 없음, signature 미검증

fixable Python 항목은 `jaraco.context 5.3.0 → 6.1.0`과 `wheel 0.45.1 → 0.46.2`입니다. `ecdsa 0.19.2`의 HIGH와 Debian 24건은 현재 report에 fixed version이 없습니다. 정책의 `--ignore-unfixed=false`가 의도대로 게시를 차단했습니다.

## 이전 시도 보존

- run `29716038891`: workflow bootstrap dependency 단계 실패, build/login/push 미실행, evidence `1f12ea59eb54385337557e9754f86731ec53d253`
- run `29877813770`: Dockerfile bootstrap target 문제로 local build 실패, login/push 미실행, evidence `c93a0327bc25941865f4ee8d600a4f903886a4fe`
- 세 run 모두 rerun 금지이며 lifecycle `attemptHistory`와 현재 evidence에 보존됩니다.

## GitHub 보안 설정

2026-07-22T01:21:58Z 재확인:

- 외부 action allowlist와 full-length SHA 강제 정상
- GitHub-owned/verified creator blanket false
- fork write token/secret 전달 false
- 기본 `GITHUB_TOKEN` contents/packages read-only, PR 생성·승인 false
- `ghcr-production-publish` 존재, main-only, secrets/variables 0/0
- native required reviewer/prevent self-review는 비공개 개인 저장소 제약으로 없음

## 다음 작업

먼저 아래 읽기 전용 검사를 실행합니다.

실행 위치: `backend` 폴더
Python `.venv` 상태: 꺼짐
새 설치 여부: 없음

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트
Python `.venv` 상태: `backend/.venv` 켜짐
새 설치 여부: 없음

```bash
python tools/check_github_actions_ghcr_static_plan.py --strict
python tools/check_codex_handoff_readiness.py --strict
```

기대값:

```txt
result: github-actions-ghcr-owner-only-attempt-recorded-publish-gated
next safe stage: review-recorded-vulnerability-gate-evidence
```

그 다음 artifact 근거로 새 exact base image digest, runtime multi-stage/minimal image, dependency 업데이트 범위를 검토합니다. HIGH/CRITICAL 또는 `--ignore-unfixed=false` gate는 자동 완화하지 않습니다. focused fix와 새 preparation/workflow 실행은 기호의 별도 승인 뒤 진행합니다.

## 안전 경계

별도 요청 전에는 DB write/restore/reset/seed, Alembic mutation, auth/API write, Vue Preview/Apply/write, 게임 콘텐츠·밸런스, production Compose/container/network/volume, production reference 변경과 자동 deploy를 실행하지 않습니다. 현재 필요한 extension·설치·추가 권한은 없고 서버 재시작도 불필요합니다.
