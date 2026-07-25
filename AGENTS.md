# Upgrade RPG Codex working rules — v339

이 파일은 저장소 전체에 적용됩니다. 작업 시작 시 이 파일, `NEXT_CHAT_HANDOFF.md`, `docs/current/CURRENT_STATUS.md`를 먼저 읽습니다.

## 사용자와 설명

- 사용자는 코딩을 거의 모르는 **기호**입니다. 항상 쉽고 자세한 한국어로 설명합니다.
- 모든 터미널 명령 바로 위에 **실행 위치**, **Python `.venv` 상태**, **새 설치 여부**를 적습니다.
- backend 가상환경은 `backend/.venv`입니다. Git Bash에서는 `backend`에서 `source .venv/Scripts/activate`로 켭니다.
- Vue/npm은 `frontend/vue-app`에서 실행하며 Python `.venv`가 필요 없습니다.
- 필요한 extension, GitHub/repository/app 권한, 설치가 있으면 기호에게 요청하고 해결될 때까지 `NEXT_CHAT_PROMPT.md`, `NEXT_CHAT_HANDOFF.md`에도 반복 기록합니다.
- 매 작업에서 루트 `NEXT_CHAT_PROMPT.md`, `NEXT_CHAT_HANDOFF.md`와 `docs/handoff/` mirror를 동기화합니다.
- 변경·검증 뒤 Codex가 `git status`, `git add`, `git commit`, `git push`를 직접 실행합니다. Git 명령 안내와 ZIP은 기호가 별도로 요구하지 않는 한 제공하지 않습니다.

## 개발 서버와 로컬 자원

- Codex는 터미널을 자유롭게 사용하고 **실행 중인 개발 서버를 재사용**합니다.
- backend `127.0.0.1:8000`, Vue `127.0.0.1:5173`, legacy static `127.0.0.1:5500`이 정상이면 재시작하지 않습니다.
- legacy 통합 확인은 `http://127.0.0.1:5500/index.html`, `/admin.html`을 사용합니다. `file://`는 origin이 `null`이라 API 통합 검증에 사용하지 않습니다.
- 기존 local PostgreSQL dependency의 단순 시작·중지는 가능하지만 reset·recreate·volume 삭제·seed·restore·migration은 별도 요청 전 금지합니다.
- 서버를 재시작하지 않았으면 완료 답변에 “서버 재시작 불필요”라고 적습니다.

## 최소 구현 원칙

- 새 추상화·의존성·파일을 만들기 전에 기존 코드, Python/JavaScript 표준 기능, 브라우저·DB·프레임워크 기본 기능으로 해결할 수 있는지 먼저 확인합니다.
- 요청하지 않은 미래용 구조·설정·scaffolding은 만들지 않으며, 안전·보안·검증·접근성 요구는 단순화를 이유로 생략하지 않습니다.

## Code Review Graph 제한 시험

- Code Review Graph 2.3.7은 사용자 전용 독립 환경에 설치한 **CLI-only 보조 도구**입니다. backend `.venv`와 프로젝트 dependency에는 포함하지 않습니다.
- `code-review-graph install`, MCP 연결, Codex hooks/instructions, watch/daemon, Git hook은 사용하지 않습니다. 필요한 다중 파일 리뷰에서만 수동 CLI 결과를 보조 evidence로 사용합니다.

## GitHub와 secret

- 기호는 작업 목적 안에서 Actions, workflow, action SHA, environment, variables와 필요한 GitHub 설정을 Codex가 구성하도록 허용했습니다.
- 숨김 파일과 `.env`는 점검·수정할 수 있지만 실제 secret/token/PAT/password/CA/cert/key를 Git·채팅·로그·artifact에 노출하거나 커밋하지 않습니다.
- root `.dockerignore`는 `.env`/`*.env`/`.envrc` 계열을 모두 제외하고 재포함을 금지합니다. `backend/Dockerfile.production.dockerignore`는 만들지 않습니다.
- 나중에 회전·폐기할 항목은 `docs/current/SECURITY_ROTATION_AND_GITHUB_GATES.md`에 기록합니다.
- 사용자 계정 선택, 추가 로그인, 결제/플랜, 실제 운영 공급자 선택처럼 Codex가 대신할 수 없는 일만 요청합니다.

## 현재 고정 상태

```txt
latest: v338.render-private-ghcr-exact-digest-connect-verified-service-creation-blocked
tooling checkpoint: v339.code-review-graph-cli-only-trial-built-ponytail-principle-applied
tooling result: code-review-graph-cli-only-built-hooks-mcp-disabled
strict result: render-ghcr-read-credential-exact-digest-connect-verified
next safe stage: review-render-service-settings-and-database-initialization-plan
deployment safety baseline: v334.production-deploy-plan-reviewed-inputs-blocked / production-deploy-plan-reviewed-inputs-blocked
baseline next stage marker: select-production-targets-and-complete-executable-deploy-plan
GitHub remote: https://github.com/gihohoho/upgrade-rpg.git
GHCR repository: ghcr.io/gihohoho/upgrade-rpg-backend (private)
target: linux/amd64
verified production reference: ghcr.io/gihohoho/upgrade-rpg-backend@sha256:ff939391517452a3ec477adaa0f8556d3525f9d0c6fb5f9d0df11d8f3d8461d2
architecture: managed PostgreSQL + verify-full + provider-managed HTTPS ingress + backend 1/1
Alembic current: v295_initial_schema / new revision needed: no
```

- CI credential은 GitHub Actions `GITHUB_TOKEN`, local pull은 GitHub CLI OAuth `read:packages` → Docker credential store입니다.
- image publish model은 `owner-only-source-controlled-two-step`입니다.
- source-controlled lifecycle gate는 `deploy/github-actions-ghcr-publish-lifecycle.json`의 `attempt-recorded`, `publishReviewerGateReady=false`입니다.
- run `29909291344`은 build/SBOM/Trivy/provenance/Cosign을 통과했고 image는 v333 isolated runtime 검증과 cleanup까지 완료했습니다.
- 운영 배포 계획은 `deploy/production-deploy-plan.example.json`과 `docs/current/PRODUCTION_DEPLOYMENT_PLAN.md`에서 검토 완료했습니다.
- production host, managed DB, provider CA, reverse proxy/domain/certificate, secret injection, edge network, first-deploy rollback 입력은 아직 미확정입니다.
- production deployment approval ready/approved/executed는 `no/no/no`입니다.
- 비용 최소 공급자는 Render Free Web Service Singapore + Neon Free PostgreSQL 16 Singapore로 선택했습니다.
- 첫 공개 주소는 Render `onrender.com` managed HTTPS이며 custom domain과 DNS 변경은 보류합니다.
- 무료 구성은 SLA production이 아닌 개인용 public preview이고 월 고정비 $0, idle cold start 허용 조건입니다.
- Neon Free PostgreSQL 16 AWS Singapore 프로젝트는 생성됐고 Neon Auth는 사용하지 않습니다. 채팅에 노출된 최초 `neondb_owner` 비밀번호는 2026-07-22에 재설정해 폐기했습니다.
- 새 Neon direct/pooled URL은 앱·배포 플랫폼에 아직 주입하지 않고 Git/Docker 제외 경로 `deploy/.env.production`에만 보관합니다.
- Direct/Pooler 모두 PostgreSQL 16.14, TLS 1.3 인증서·호스트 검증, read-only transaction을 통과했습니다. sanitized evidence는 `deploy/review/neon-readonly-connectivity-v336.json`입니다.
- Render `Hobby (legacy)` workspace는 연결됐고 결제수단·billing 정보가 없습니다. 기존 service 1개는 owner-suspended이며 active service는 0개입니다.
- GitHub `Confirm access`는 사용자가 완료했고 Render 전용 classic PAT는 `read:packages` only, 만료일 2027-07-23으로 생성해 `upgrade-rpg-ghcr-read` credential에 저장했습니다. 실제 값은 Git·파일·채팅에 기록하지 않습니다.
- 브라우저 검사 출력에 노출된 첫 PAT는 Render에 저장하지 않고 즉시 GitHub에서 폐기했습니다. 교체 PAT는 값 출력 없이 전달했으며 회전 기록은 `docs/current/SECURITY_ROTATION_AND_GITHUB_GATES.md`에 있습니다.
- verified exact digest를 Render `Existing Image`에서 `Connect`해 private GHCR 접근과 서비스 설정 화면 진입을 확인했습니다. Web Service 생성, env 주입, deploy는 실행하지 않았습니다.

## 승인과 안전 경계

실제 운영 배포는 입력을 모두 확정한 실행 준비 commit의 정확한 40자리 SHA를 기호가 별도 승인한 뒤에만 진행합니다. 한 번의 exact-SHA 승인은 문서에 적힌 GHCR login/pull, final Compose render, backend start/replace, read-only health, 기존 proxy route 확인 범위만 허용합니다.

다음은 그 승인에도 포함되지 않으며 별도 구체적 요청 없이는 실행하지 않습니다.

- DB create/delete/restore/reset/seed/write
- Alembic revision/autogenerate/stamp/upgrade/downgrade
- 인증, API route/response/write logic 변경
- Vue Preview/Apply/write 연결
- 게임 콘텐츠·밸런스 변경
- Docker volume 삭제, `docker compose down -v`
- production image 자동 갱신, 자동 deploy, 자동 retry

## 폴더와 문서

- `docs/current/`: 현재 판단·계획·runbook
- `docs/guides/`: 실제 사용 가이드
- `docs/contracts/`: API·관리자 계약
- `docs/archive/`: 과거 고유 기록
- `docs/handoff/`: 루트 handoff mirror
- `deploy/review/`: sanitized 정적/runtime 증거
- `local-backups/`, `local-review-artifacts/`: Git 제외 로컬 보존 자료이며 자동 삭제하지 않습니다.
- legacy `index.html`, `admin.html`, `src/`는 Vue 이식 전까지 이동하거나 대규모 재작성하지 않습니다.

## 다음 검사와 검증 원칙

프로젝트 루트에서 `backend/.venv` Python으로 먼저 실행합니다.

```bash
python tools/check_neon_readonly_connectivity.py --evidence
python tools/check_production_provider_selection.py --strict
python tools/check_production_deployment_plan.py --strict
python tools/check_github_actions_ghcr_static_plan.py --strict
python tools/check_codex_handoff_readiness.py --strict
```

변경 영역 전용 checker/smoke부터 1회 실행하고 실패할 때만 확대합니다. 문서·handoff·상태값만 바꾸면 전체 core smoke를 반복하지 않습니다. 핵심 로직·DB/Alembic·API 계약·공통 구조·여러 영역을 함께 바꾸거나 실제 배포 후보 직전에는 `bash tools/run_smoke_core.sh`를 1회 실행합니다. Python 변경은 해당 compileall, JavaScript 변경은 문법 검사를 수행합니다. Vue 변경 시에만 `npm ci`, `npm run build`를 실행합니다.

완료 답변에는 한 일, 검증, 서버 재시작 여부, commit/push, 다음 단계, 필요한 extension/권한/설치를 포함합니다.
