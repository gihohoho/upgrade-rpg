# Upgrade RPG Codex next prompt — v336

프로젝트 루트의 `AGENTS.md`, `NEXT_CHAT_HANDOFF.md`, `docs/current/CURRENT_STATUS.md`를 먼저 읽고 계속 지켜주세요. 기호는 코딩을 거의 모르므로 한국어로 쉽게 설명하고, 모든 터미널 명령 위에 실행 위치, Python `.venv` 상태, 새 설치 여부를 적어주세요. 필요한 extension·권한·설치는 해결될 때까지 요청해주세요.

Codex가 개발 서버와 기존 local PostgreSQL dependency를 필요에 따라 관리하고, 변경 뒤 Git add/commit/push까지 직접 합니다. ZIP과 Git 명령 안내는 필요 없습니다. root handoff와 `docs/handoff/` mirror는 매 작업 동기화합니다.

## 현재 고정값

```txt
latest: v336.neon-readonly-connectivity-verified-render-onboarding-required
strict result: neon-direct-pooled-readonly-connectivity-verified
next safe stage: owner-connect-render-and-review-database-initialization-plan
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
Render account/service/deploy: not connected/not created/not executed
approval ready/approved/executed: no/no/no
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

1. sanitized evidence `deploy/review/neon-readonly-connectivity-v336.json`을 정적으로 재검증합니다. 실제 URL을 출력하거나 live 검사를 불필요하게 반복하지 않습니다.
2. Render Hobby 로그인과 결제수단 미등록 상태를 확인한 뒤 Free image-backed Web Service Singapore 설정을 준비합니다.
3. 현재 Neon DB `neondb`와 계획상 `rpg_game`의 차이를 해소하는 DB 생성·schema/data 이식 계획을 작성·검토합니다. 별도 구체적 승인 전 실행하지 않습니다.
4. exact image, health path, secret 이름, certificate strategy를 실제 Render 입력과 연결하되 deploy는 exact-SHA 승인 전 실행하지 않습니다.

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

기대값은 v336 `neon-direct-pooled-readonly-connectivity-verified`와 `owner-connect-render-and-review-database-initialization-plan`입니다. v335 provider-selection 결과와 v334 deployment baseline은 계속 보존합니다.

별도 승인 전에는 production resource, GHCR credential, DB/Alembic mutation, auth/API write, Vue Preview/Apply/write, 게임 콘텐츠·밸런스를 변경하지 않습니다.
