# Upgrade RPG Codex next prompt — v337

프로젝트 루트의 `AGENTS.md`, `NEXT_CHAT_HANDOFF.md`, `docs/current/CURRENT_STATUS.md`를 먼저 읽고 계속 지켜주세요. 기호는 코딩을 거의 모르므로 한국어로 쉽게 설명하고, 모든 터미널 명령 위에 실행 위치, Python `.venv` 상태, 새 설치 여부를 적어주세요. 필요한 extension·권한·설치는 해결될 때까지 요청해주세요.

Codex가 개발 서버와 기존 local PostgreSQL dependency를 필요에 따라 관리하고, 변경 뒤 Git add/commit/push까지 직접 합니다. ZIP과 Git 명령 안내는 필요 없습니다. root handoff와 `docs/handoff/` mirror는 매 작업 동기화합니다.

## 현재 고정값

```txt
latest: v337.render-account-inspected-private-ghcr-credential-approval-required
strict result: render-hobby-no-card-existing-image-private-ghcr-credential-required
next safe stage: owner-complete-github-confirm-access-then-resume-approved-render-credential-flow
deployment safety baseline: v334.production-deploy-plan-reviewed-inputs-blocked
baseline result: production-deploy-plan-reviewed-inputs-blocked
baseline next stage marker: select-production-targets-and-complete-executable-deploy-plan
GitHub remote: https://github.com/gihohoho/upgrade-rpg.git
GHCR repository: ghcr.io/gihohoho/upgrade-rpg-backend
visibility/platform: private / linux/amd64
production reference: ghcr.io/gihohoho/upgrade-rpg-backend@sha256:ff939391517452a3ec477adaa0f8556d3525f9d0c6fb5f9d0df11d8f3d8461d2
provider selection: Render Free Web Service Singapore + Neon Free PostgreSQL 16 Singapore
fixed monthly cost: USD 0
Neon account/project: connected/created (PostgreSQL 16, AWS Singapore)
Neon credential: exposed initial password rotated; new URLs local-only, not deployed
Neon read-only connectivity: direct/pooled verified with TLS 1.3 hostname verification
Render account/plan/payment: connected/Hobby (legacy)/no card
Render registry credential/service/deploy: absent/not created/not executed
Render credential action ready/approved/executed: yes/yes/no
production deployment approval ready/approved/executed: no/no/no
```

Render는 무료 Hobby workspace에 결제수단을 처음부터 넣지 않습니다. 한도 초과 시 과금 대신 일시 중지를 선택합니다. 첫 주소는 Render `onrender.com` managed HTTPS이고 custom domain/DNS는 보류합니다. 이 무료 구성은 SLA production이 아니라 cold start를 허용한 개인용 public preview입니다.

## 공급망 증거와 안전 baseline

- source-controlled lifecycle gate: `deploy/github-actions-ghcr-publish-lifecycle.json`
- lifecycle: `attempt-recorded` / `publishReviewerGateReady=false`
- CI credential: GitHub Actions `GITHUB_TOKEN`
- preparation/authorization/closure/evidence: `36e8720a53ef7ff6a8334de6bc99646998d63fc9` / `26a11356e33c978afa8cd8a4881500fa62cdbc5c` / `1c4a982b2a35d3d45f59e7d9faefcdecca69e6c5` / `1f0340ddfcf3c8a74cf14110d5957627d4c5d38a`
- run `29909291344`, artifacts `8525220616`, `8525254543`
- run_attempt=1, single dispatch, immediate closure, closureCommitSha 기록, rerun 금지
- 역사 lifecycle 결과 `review-recorded-workflow-attempt-evidence` 보존
- isolated evidence: `deploy/review/isolated-image-pull-validation-v333.json`
- reviewed plan: `deploy/production-deploy-plan.example.json`
- provider selection: `deploy/production-provider-selection.example.json`

## 다음 작업

Neon Free PostgreSQL 16 AWS Singapore 프로젝트는 생성됐고 Neon Auth는 사용하지 않습니다. 채팅에 노출된 최초 `neondb_owner` 비밀번호는 재설정해 폐기했습니다. 새 direct/pooled URL은 `deploy/.env.production`에만 있고 채팅·Git·로그에는 없습니다. Direct/Pooler 모두 PostgreSQL 16.14, TLS 1.3 인증서·호스트 검증, read-only transaction을 통과했습니다.

Render `Hobby (legacy)`/no-card account와 `Existing Image`/GitHub credential 양식은 읽기 전용으로 확인했습니다. credential/PAT/Web Service/deploy는 아직 없습니다.

사용자는 Render 전용 classic PAT 생성·저장과 exact image `Connect` 검증을 승인했습니다. GitHub `Confirm access` 탭에서 인증 앱 verification code 입력만 사용자가 직접 완료해야 합니다.

1. 사용자가 “GitHub Confirm access 완료”라고 알리기 전에는 브라우저 작업을 재개하지 않습니다.
2. 완료 후 classic PAT를 `render-upgrade-rpg-ghcr-read`, 365일, `read:packages` only로 생성합니다. 기존 CLI OAuth token은 재사용하지 않습니다.
3. token을 채팅·파일·로그에 출력하지 않고 Render `upgrade-rpg-ghcr-read` GitHub credential에 직접 저장합니다.
4. verified exact digest를 입력해 `Connect`로 pull 접근만 검증합니다. Web Service 생성/deploy는 누르지 않습니다.
5. 현재 Neon `neondb`와 계획상 `rpg_game`의 DB 초기화 계획은 별도 승인 범위로 유지합니다.

실제 resource 생성, DB 초기화/이식, GHCR PAT 생성·주입, backend deploy는 각 범위를 명확히 한 뒤 실행 준비 commit의 정확한 40자리 SHA를 별도 승인받기 전까지 실행하지 않습니다.

## 첫 읽기 전용 검사

실행 위치: 프로젝트 루트
Python `.venv` 상태: 셸 활성화는 꺼짐, `backend/.venv/Scripts/python.exe` 직접 사용
새 설치 여부: 없음

```bash
python tools/check_neon_readonly_connectivity.py --evidence
python tools/check_production_provider_selection.py --strict
python tools/check_production_deployment_plan.py --strict
python tools/check_github_actions_ghcr_static_plan.py --strict
python tools/check_codex_handoff_readiness.py --strict
```

v337 현재 결과는 `render-hobby-no-card-existing-image-private-ghcr-credential-required`, 다음 단계는 `owner-complete-github-confirm-access-then-resume-approved-render-credential-flow`입니다. 첫 정적 검사에서는 v336 Neon evidence와 v335/v334 baseline을 계속 보존합니다.

별도 승인 전에는 production resource, GHCR credential, DB/Alembic mutation, auth/API write, Vue Preview/Apply/write, 게임 콘텐츠·밸런스를 변경하지 않습니다.
