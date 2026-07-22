# Upgrade RPG Codex next prompt — v338

프로젝트 루트의 `AGENTS.md`, `NEXT_CHAT_HANDOFF.md`, `docs/current/CURRENT_STATUS.md`를 먼저 읽고 계속 지켜주세요. 기호는 코딩을 거의 모르므로 한국어로 쉽게 설명하고, 모든 터미널 명령 위에 실행 위치, Python `.venv` 상태, 새 설치 여부를 적어주세요. 필요한 extension·권한·설치는 해결될 때까지 요청해주세요.

Codex가 개발 서버와 기존 local PostgreSQL dependency를 필요에 따라 관리하고, 변경 뒤 Git add/commit/push까지 직접 합니다. ZIP과 Git 명령 안내는 필요 없습니다. root handoff와 `docs/handoff/` mirror는 매 작업 동기화합니다.

## 현재 고정값

```txt
latest: v338.render-private-ghcr-exact-digest-connect-verified-service-creation-blocked
strict result: render-ghcr-read-credential-exact-digest-connect-verified
next safe stage: review-render-service-settings-and-database-initialization-plan
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
Neon read-only connectivity: direct/pooled verified with TLS 1.3 hostname verification
Render account/plan/payment: connected/Hobby (legacy)/no card
Render registry credential/service/deploy: present/not created/not executed
Render credential action ready/approved/executed: yes/yes/yes
production deployment approval ready/approved/executed: no/no/no
```

Render 전용 GitHub classic PAT는 `read:packages` only, 만료일 2027-07-23으로 만들고 `upgrade-rpg-ghcr-read` credential에 저장했습니다. 첫 PAT는 브라우저 검사 출력에 노출된 것을 감지해 Render에 저장하지 않고 즉시 GitHub에서 폐기했습니다. 교체 PAT 값은 채팅·파일·Git·로그에 기록하지 않았습니다.

verified exact digest는 Render `Existing Image`에서 `Connect`에 성공했고 서비스 설정 화면까지 열렸습니다. `Deploy Web Service`는 누르지 않았으므로 Web Service 생성과 배포는 모두 없습니다. sanitized evidence는 `deploy/review/render-private-ghcr-connect-v338.json`입니다.

## 공급망 안전 baseline

- CI credential: GitHub Actions `GITHUB_TOKEN`
- source-controlled lifecycle gate: `deploy/github-actions-ghcr-publish-lifecycle.json`
- lifecycle: `attempt-recorded` / `publishReviewerGateReady=false`
- run `29909291344`: provenance/SBOM, exact-digest Trivy 0건, Cosign sign/verify 성공
- single-run policy: `run_attempt=1`, single dispatch, immediate closure, `closureCommitSha`, rerun 금지
- 역사 결과 `review-recorded-workflow-attempt-evidence` 보존
- isolated evidence: `deploy/review/isolated-image-pull-validation-v333.json`

## 다음 작업

문서와 정적 검사로만 다음 두 계획을 분리 검토해주세요.

1. Render Free Singapore 서비스 설정: 이름, region, Free instance, health check path, environment variable inventory, auto-deploy 차단, exact digest 유지, rollback 경계
2. Neon 기본 `neondb`와 계획상 `rpg_game` 차이를 포함한 DB 생성·schema/data 초기화·이식 계획

현재 열린 Render 탭은 서비스 설정 handoff 상태입니다. 읽기 전용 확인에 재사용할 수 있지만 `Deploy Web Service`를 누르지 마세요. 새 PAT를 다시 만들거나 credential을 교체하지 마세요. actual Neon URL, JWT/admin secret, CORS origin도 아직 Render에 넣지 마세요.

실제 Web Service 생성, env 주입, DB write/restore/seed, Alembic mutation, production deploy는 각 실행 범위를 문서화하고 준비 commit의 정확한 40자리 SHA를 기호가 별도 승인하기 전까지 실행하지 않습니다.

## 첫 검사

실행 위치: 프로젝트 루트
Python `.venv` 상태: 셸 활성화는 꺼짐, `backend/.venv/Scripts/python.exe` 직접 사용
새 설치 여부: 없음

```bash
python tools/check_render_private_ghcr_connect.py --strict
python tools/check_neon_readonly_connectivity.py --evidence
python tools/check_production_provider_selection.py --strict
python tools/check_production_deployment_plan.py --strict
python tools/check_github_actions_ghcr_static_plan.py --strict
python tools/check_codex_handoff_readiness.py --strict
```

첫 검사의 v338 기대 결과는 `render-ghcr-read-credential-exact-digest-connect-verified`, 다음 단계는 `review-render-service-settings-and-database-initialization-plan`입니다. v337 account readiness, v336 Neon evidence, v335 provider selection, v334 deployment baseline을 보존합니다.

별도 승인 전에는 Web Service/deploy, DB/Alembic mutation, auth/API write, Vue Preview/Apply/write, 게임 콘텐츠·밸런스를 변경하지 않습니다.
