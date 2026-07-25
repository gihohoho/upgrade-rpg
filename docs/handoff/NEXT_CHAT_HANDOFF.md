# Upgrade RPG Codex handoff — v339

## 현재 상태

```txt
latest: v338.render-private-ghcr-exact-digest-connect-verified-service-creation-blocked
tooling checkpoint: v339.code-review-graph-cli-only-trial-built-ponytail-principle-applied
tooling result: code-review-graph-cli-only-built-hooks-mcp-disabled
strict result: render-ghcr-read-credential-exact-digest-connect-verified
next safe stage: review-render-service-settings-and-database-initialization-plan
deployment safety baseline: v334.production-deploy-plan-reviewed-inputs-blocked
baseline result: production-deploy-plan-reviewed-inputs-blocked
baseline next stage marker: select-production-targets-and-complete-executable-deploy-plan
GitHub remote: https://github.com/gihohoho/upgrade-rpg.git
GHCR repository: ghcr.io/gihohoho/upgrade-rpg-backend
verified reference: ghcr.io/gihohoho/upgrade-rpg-backend@sha256:ff939391517452a3ec477adaa0f8556d3525f9d0c6fb5f9d0df11d8f3d8461d2
provider selection: Render Free Singapore + Neon Free PostgreSQL 16 Singapore
fixed monthly cost: USD 0
Neon project/read-only connectivity: created/verified
Render account/plan/payment: connected/Hobby (legacy)/no card
Render registry credential/service/deploy: present/not created/not executed
Render credential action ready/approved/executed: yes/yes/yes
production deployment approval ready/approved/executed: no/no/no
```

## 로컬 코드 리뷰 보조 도구 — 2026-07-26

- Code Review Graph 2.3.7은 `%LOCALAPPDATA%\UpgradeRPGTools\code-review-graph`의 사용자 전용 독립 환경에 CLI-only로 설치했습니다.
- 첫 로컬 그래프 상태는 385 files / 4,242 nodes / 35,407 edges이며 저장소의 `.code-review-graph/`는 Git에서 제외합니다.
- backend `.venv`와 프로젝트 dependency는 변경하지 않았습니다.
- `code-review-graph install`, MCP, Codex hook/instruction 주입, watch/daemon, Git hook, cloud embedding은 사용하지 않습니다.
- 다중 파일 리뷰 때만 수동 CLI 결과를 보조 evidence로 사용하며 그래프 위험도만으로 결함을 단정하지 않습니다.
- Ponytail 플러그인은 설치하지 않았고 최소 구현 원칙 두 줄만 `AGENTS.md`에 반영했습니다.

## 완료된 공급자 준비

개인 프로젝트 비용 최소안은 Render Free Web Service와 Neon Free PostgreSQL 16을 Singapore에 두는 구성입니다. 첫 공개 주소는 Render `onrender.com` managed HTTPS이며 custom domain/DNS는 보류합니다. 고정 월 비용은 $0이고 cold start를 허용하는 개인용 public preview입니다.

Neon Free PostgreSQL 16 AWS Singapore 프로젝트는 생성됐고 Neon Auth는 사용하지 않습니다. 채팅에 노출된 최초 `neondb_owner` 비밀번호는 재설정해 폐기했습니다. 새 direct/pooled URL은 Git/Docker 제외 파일 `deploy/.env.production`에만 있으며 Direct/Pooler 모두 PostgreSQL 16.14, TLS 1.3 인증서·호스트 검증과 read-only transaction을 통과했습니다. sanitized evidence는 `deploy/review/neon-readonly-connectivity-v336.json`입니다.

Render workspace는 `Hobby (legacy)`, 결제수단 없음, active service 0개입니다. v337에서 `Existing Image`와 GitHub Container Registry credential 흐름을 확인했고 evidence는 `deploy/review/render-account-readiness-v337.json`입니다.

## Render private GHCR Connect — 2026-07-23

기호가 Render 전용 classic PAT 생성·저장과 exact-digest `Connect`를 승인했고 GitHub `Confirm access`를 직접 완료했습니다.

- credential name: `upgrade-rpg-ghcr-read`
- token type: classic PAT
- scope: `read:packages` only
- expiration: 2027-07-23
- registry username: `gihohoho`
- image: verified exact digest

첫 PAT는 브라우저 검사 출력에 값이 노출된 것을 감지했습니다. Render에는 저장하지 않고 즉시 GitHub에서 폐기했습니다. 교체 PAT는 값 출력 없이 Render에 직접 전달하고 브라우저 메모리에서도 제거했습니다. 실제 값은 Git·파일·문서·evidence에 없습니다.

교체 credential로 exact digest `Connect`에 성공했고 Render 서비스 설정 화면의 Singapore/Free/환경변수/`Deploy Web Service` 단계까지 진입했습니다. `Deploy Web Service`는 누르지 않았으므로 Web Service 생성, env 주입, 배포는 없습니다. sanitized evidence는 `deploy/review/render-private-ghcr-connect-v338.json`입니다.

## 공급망과 승인 경계

- CI credential: GitHub Actions `GITHUB_TOKEN`
- source-controlled lifecycle gate: `deploy/github-actions-ghcr-publish-lifecycle.json`
- lifecycle: `attempt-recorded` / `publishReviewerGateReady=false`
- run `29909291344`: provenance/SBOM, exact-digest Trivy 0건, Cosign sign/verify 성공
- run policy: `run_attempt=1`, single dispatch, immediate closure, `closureCommitSha`, rerun 금지
- 역사 lifecycle 결과 `review-recorded-workflow-attempt-evidence` 보존
- isolated evidence: `deploy/review/isolated-image-pull-validation-v333.json`
- actual deploy는 placeholder 없는 실행 준비 commit의 정확한 40자리 SHA를 기호가 별도 승인한 뒤에만 실행

## 유지할 안전 경계

- Render Web Service 생성과 `Deploy Web Service` 실행 금지
- Render payment method 추가 금지
- actual Neon URL, JWT/admin secret, CORS origin의 Render 주입 금지
- DB create/delete/restore/reset/seed/write와 Alembic mutation 금지
- 인증/API write, Vue Preview/Apply/write, 게임 콘텐츠·밸런스 변경 금지
- auto-deploy, automatic migration, automatic retry 금지
- actual secret/token/PAT/password/CA/cert/key를 Git·채팅·로그·artifact에 기록하지 않음

## 다음 단계

문서와 fail-closed 정적 검사로 다음 두 계획을 분리 준비합니다.

1. Render Free Singapore 서비스 생성 직전 설정: name, region, Free instance, health check, environment inventory, exact digest, auto-deploy 차단, rollback
2. Neon 기본 `neondb`와 계획상 `rpg_game` 차이를 포함한 DB 생성·schema/data 초기화·이식 계획

현재 Render 탭은 서비스 설정 화면에서 handoff 상태입니다. 읽기 전용 확인에는 재사용할 수 있지만 배포 버튼은 누르지 않습니다. 필요한 extension·로컬 설치는 현재 없습니다.

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

v338 기대 결과는 `render-ghcr-read-credential-exact-digest-connect-verified`, 다음 단계는 `review-render-service-settings-and-database-initialization-plan`입니다. v337 account readiness, v336 Neon evidence, v335 provider selection과 v334 deployment baseline을 계속 보존합니다.

서버 재시작은 필요하지 않습니다.
