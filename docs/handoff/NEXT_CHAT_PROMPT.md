# Upgrade RPG 다음 Codex 작업 프롬프트 — v327

기호의 Upgrade RPG 프로젝트를 현재 Git `main` 최신 상태에서 이어서 진행합니다. 먼저 `AGENTS.md`, `NEXT_CHAT_HANDOFF.md`, `docs/current/CURRENT_STATUS.md`를 읽고 저장소 규칙을 지켜주세요.

기호는 코딩을 거의 모릅니다. 항상 한국어로 쉽게 설명하고, 모든 터미널 명령 바로 위에 실행 위치, Python `.venv` 상태, 새 설치 여부를 적어주세요. 필요한 extension, 권한, 설치가 있으면 요청하고 해결될 때까지 다음 handoff에도 기록하세요. Codex가 변경·검증 뒤 git add/commit/push까지 직접 하며 ZIP과 Git 명령 안내는 제공하지 않습니다. 실행 중인 개발 서버는 재사용하고 필요할 때만 재시작합니다.

검증은 위험도에 맞춰 최소 범위부터 실행하세요. 기본은 변경 영역의 전용 checker/smoke 1회이고 실패할 때만 범위를 넓힙니다. 문서·handoff·상태값·검사 결과 문자열만 바꾼 경우에는 관련 strict checker와 handoff smoke만 실행하며 전체 `bash tools/run_smoke_core.sh`는 실행하지 않습니다. 전체 smoke는 backend 핵심 로직, DB/Alembic, API 계약, 공통 구조, 여러 영역 변경 또는 실제 배포 후보 직전에만 1회 실행하고 단순 문구 수정 뒤 반복하지 않습니다.

```txt
latest: v327.third-owner-only-attempt-recorded-vulnerability-gated
strict result: github-actions-ghcr-owner-only-attempt-recorded-publish-gated
next safe stage: review-recorded-vulnerability-gate-evidence
GitHub remote: https://github.com/gihohoho/upgrade-rpg.git
GHCR namespace: gihohoho
backend repository: ghcr.io/gihohoho/upgrade-rpg-backend
visibility: private
target platform: linux/amd64
CI credential strategy: github-actions-github-token
publish approval model: owner-only-source-controlled-two-step
source-controlled lifecycle gate: attempt-recorded / publishReviewerGateReady=false
run_attempt=1: required
single dispatch: required
immediate closure: required
```

`deploy/github-actions-ghcr-publish-lifecycle.json`은 P `preparation-closed` → A `authorization-open` → C `authorization-closed-awaiting-evidence` → R `attempt-recorded` 상태를 지원합니다. authorization은 승인된 preparation의 직접 자식이고 lifecycle 파일 하나만 바꿉니다. run 접수 즉시 immediate closure로 gate를 닫고, 종료 뒤 별도 evidence commit에서 부모 closure의 정확한 `closureCommitSha`와 실제 결과를 기록합니다. 모든 run은 `run_attempt=1`, single dispatch이고 rerun 금지입니다. 일반 계약 next stage 문자열 `review-recorded-workflow-attempt-evidence`도 유지합니다.

3차 실행 증거:

- preparation: `b35dfacf427162b348a6bd29eb030778edc7741c` (기호 승인·소비 완료)
- authorization: `04e002060e576f19f4d8687b33635a414486206d`
- closure: `64e5ae0f5e5385ba00df16bb10ac33789ca3760a`
- evidence: `303a2ed01c69c29894efdcde4ead6c2291c3d8bc`
- run: `29883012957` / `https://github.com/gihohoho/upgrade-rpg/actions/runs/29883012957` / failure
- validation과 로컬 image build 및 SPDX SBOM은 성공, Trivy HIGH/CRITICAL gate가 27건을 찾아 게시를 차단
- artifact `8515504259`, SHA-256 `6a5dfd4cd96754fd365323c7c6a7d1edf18542b5e5729e44220d7bf21ace4c50`, `sbom.spdx.json`과 `trivy-results.json`, 14일 보존
- publish job skipped: GHCR login/push/provenance/Cosign 미실행, image digest 없음, signature 미검증

첫 작업은 읽기 전용 v327 검사입니다.

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

정상 기대 결과:

```txt
result: github-actions-ghcr-owner-only-attempt-recorded-publish-gated
next safe stage: review-recorded-vulnerability-gate-evidence
```

다음에는 artifact의 27개 항목을 근거로 exact base image digest 갱신, runtime image 최소화, fixed version이 있는 Python package 2건을 포함한 dependency 조정을 검토하세요. `--ignore-unfixed=false`나 HIGH/CRITICAL gate를 자동 완화하지 말고, focused fix와 새 preparation은 기호의 별도 승인 뒤 진행하세요. 기존 세 run은 rerun하지 말고 새 workflow도 승인 전 실행하지 마세요.

사용자 별도 요청 전에는 DB/Alembic/auth/API write/Vue Preview·Apply·write/게임 콘텐츠와 밸런스/production Compose·container·network·volume/자동 deploy를 변경하거나 실행하지 마세요. actual secret/token/PAT/credential/CA/cert/key는 Git·채팅·로그·artifact에 넣지 않습니다.
