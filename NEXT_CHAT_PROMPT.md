# Upgrade RPG Codex next prompt — v340

프로젝트 루트의 `AGENTS.md`, `NEXT_CHAT_HANDOFF.md`, `docs/current/CURRENT_STATUS.md`를 먼저 읽고 계속 지켜주세요. 기호는 코딩을 거의 모르므로 한국어로 쉽게 설명하고, 모든 터미널 명령 위에 실행 위치, Python `.venv` 상태, 새 설치 여부를 적어주세요. 필요한 extension·권한·설치는 해결될 때까지 요청해주세요.

Codex가 개발 서버와 기존 local PostgreSQL dependency를 필요에 따라 관리하고, 변경 뒤 Git add/commit/push까지 직접 합니다. ZIP과 Git 명령 안내는 필요 없습니다. root handoff와 `docs/handoff/` mirror는 매 작업 동기화합니다.

## 현재 고정값

```txt
latest: v340.render-neon-separated-plans-reviewed-bootstrap-fix-required
strict result: render-neon-separated-plans-reviewed-fail-closed
next safe stage: prepare-neon-verify-full-bootstrap-fix-and-new-image
render plan: v340.render-service-settings-reviewed-creation-blocked
neon plan: v340.neon-initialization-migration-reviewed-execution-blocked
render checkpoint: v338.render-private-ghcr-exact-digest-connect-verified-service-creation-blocked
render checkpoint result: render-ghcr-read-credential-exact-digest-connect-verified
render checkpoint next stage: review-render-service-settings-and-database-initialization-plan
tooling checkpoint: v339.code-review-graph-cli-only-trial-built-ponytail-principle-applied
tooling result: code-review-graph-cli-only-built-hooks-mcp-disabled
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

## 로컬 코드 리뷰 보조 도구 — v339

Code Review Graph 2.3.7은 `%LOCALAPPDATA%\UpgradeRPGTools\code-review-graph`의 독립 환경에 CLI-only로 설치했습니다. 첫 로컬 그래프 상태는 385 files / 4,242 nodes / 35,407 edges이며 `.code-review-graph/`는 Git에서 제외합니다. backend `.venv`와 프로젝트 dependency는 변경하지 않았습니다.

`code-review-graph install`, MCP, Codex hook/instruction 주입, watch/daemon, Git hook, cloud embedding은 사용하지 않습니다. 다중 파일 리뷰가 실제로 필요할 때만 수동 CLI 결과를 보조 evidence로 사용하고, 그래프 위험도만으로 결함이나 수정 필요성을 단정하지 않습니다.

Ponytail 플러그인은 설치하지 않았습니다. 새 추상화·의존성·파일보다 기존 기능을 먼저 사용하고 요청하지 않은 미래용 구조를 만들지 않는 최소 구현 원칙만 `AGENTS.md`에 반영했습니다. 안전·보안·검증·접근성 요구는 단순화를 이유로 생략하지 않습니다.

## Render/Neon 분리 계획 — v340

두 계획은 `docs/current/RENDER_SERVICE_SETTINGS_PLAN.md`, `docs/current/NEON_DATABASE_INITIALIZATION_MIGRATION_PLAN.md`와 대응하는 `deploy/*.example.json` 계약으로 검토 완료했습니다.

Neon production branch의 기본 `neondb`는 system-CA hostname verification과 read-only transaction에서 public table 0개, `alembic_version` 없음으로 확인됐습니다. 새 `rpg_game` DB는 만들지 않습니다. 검증된 local custom dump의 22 application tables / 748 rows를 direct URL로 restore한 뒤 exact `v295_initial_schema`를 stamp하는 계획입니다.

현재 v338 image는 SQLAlchemy `asyncpg` production engine에 system-CA verify-full SSLContext를 전달하지 않아 Neon runtime 연결에 실패합니다. `deploy/production.env.example`에도 `ENVIRONMENT=production`, `DEBUG=false`, `PORT=8000`이 빠져 있습니다. 따라서 현재 digest로 Render Web Service를 만들지 않습니다.

고정 순서는 bootstrap fix → 새 exact-digest image publish/isolated validation → DB 초기화 전용 exact-SHA 승인 후 Neon restore/stamp → Render 생성 전용 exact-SHA 승인 후 Web Service create/deploy입니다.

## 공급망 안전 baseline

- CI credential: GitHub Actions `GITHUB_TOKEN`
- source-controlled lifecycle gate: `deploy/github-actions-ghcr-publish-lifecycle.json`
- lifecycle: `attempt-recorded` / `publishReviewerGateReady=false`
- run `29909291344`: provenance/SBOM, exact-digest Trivy 0건, Cosign sign/verify 성공
- single-run policy: `run_attempt=1`, single dispatch, immediate closure, `closureCommitSha`, rerun 금지
- 역사 결과 `review-recorded-workflow-attempt-evidence` 보존
- isolated evidence: `deploy/review/isolated-image-pull-validation-v333.json`

## 다음 작업

Neon verify-full bootstrap과 production env inventory의 focused fix를 준비해주세요. 아직 actual secret을 파일에 기록하거나 새 image publish, Neon restore/stamp, Render Web Service 생성·배포를 실행하지 마세요.

기호에게 지금 필요한 선택은 추천 Render 서비스 이름 `upgrade-rpg-api` 사용 여부 확인뿐입니다. 이후 DB 초기화 준비 commit과 Render 생성 준비 commit은 각각 정확한 40자리 SHA 승인을 별도로 받습니다.

## 첫 검사

실행 위치: 프로젝트 루트
Python `.venv` 상태: 셸 활성화는 꺼짐, `backend/.venv/Scripts/python.exe` 직접 사용
새 설치 여부: 없음

```bash
python tools/check_render_neon_separated_plan.py --strict
python tools/check_render_private_ghcr_connect.py --strict
python tools/check_neon_readonly_connectivity.py --evidence
python tools/check_production_provider_selection.py --strict
python tools/check_production_deployment_plan.py --strict
python tools/check_github_actions_ghcr_static_plan.py --strict
python tools/check_codex_handoff_readiness.py --strict
```

첫 검사의 v340 기대 결과는 `render-neon-separated-plans-reviewed-fail-closed`, 다음 단계는 `prepare-neon-verify-full-bootstrap-fix-and-new-image`입니다. v338 Render Connect, v337 account readiness, v336 Neon evidence, v335 provider selection, v334 deployment baseline을 보존합니다.

별도 승인 전에는 Web Service/deploy, DB/Alembic mutation, auth/API write, Vue Preview/Apply/write, 게임 콘텐츠·밸런스를 변경하지 않습니다.
