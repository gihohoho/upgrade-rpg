# Upgrade RPG Codex next prompt — v352

프로젝트 루트의 `AGENTS.md`, `NEXT_CHAT_HANDOFF.md`, `docs/current/CURRENT_STATUS.md`를 먼저 읽고 계속 지켜주세요. 기호는 코딩을 거의 모르므로 한국어로 쉽게 설명하고, 모든 터미널 명령 위에 실행 위치, Python `.venv` 상태, 새 설치 여부를 적어주세요. 필요한 extension·권한·설치는 해결될 때까지 요청해주세요.

Codex가 개발 서버와 기존 local PostgreSQL dependency를 필요에 따라 관리하고, 변경 뒤 Git add/commit/push까지 직접 합니다. ZIP과 Git 명령 안내는 필요 없습니다. root handoff와 `docs/handoff/` mirror는 매 작업 동기화합니다.

## 현재 고정값

```txt
latest: v352.v351-public-release-gates-prepared-backend-image-approval-required
strict result: v351-backend-image-preparation-closed-owner-approval-required
next safe stage: owner-approve-v352-v351-backend-image-preparation-sha
v351 source checkpoint: v351.master-data-latency-focused-fix-blocking-io-audited / master-data-latency-fix-blocking-io-audit-ready
v351 source next stage (completed): prepare-v351-image-and-static-release-exact-sha-gates
frontend plan: v351.master-data-latency-focused-fix-blocking-io-audited
v350 prior checkpoint: v350.backend-cors-recovered-browser-timeout-followup-required / backend-cors-recovered-browser-timeout-followup-required
v350 prior next stage (completed): prepare-frontend-master-data-timeout-fix-and-content-readiness-review
render plan: v347.render-service-created-initial-deploy-verified
render prior next stage (completed): review-render-live-service-and-prepare-frontend-deployment-plan
neon plan: v345.neon-initialization-completed-verified-render-preparation-required
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
production reference: ghcr.io/gihohoho/upgrade-rpg-backend@sha256:f3bf6eed45e46e9d2022df4ab62eb6ca55b1ec0997b8ed342ae250c4a60052c1
provider selection: Render Free Web Service Singapore + Neon Free PostgreSQL 16 Singapore
fixed monthly cost: USD 0
Neon account/project: connected/created (PostgreSQL 16, AWS Singapore)
Neon read-only connectivity: direct/pooled verified with TLS 1.3 hostname verification
Render account/plan/payment: connected/Hobby (legacy)/no card
Render registry credential/service/deploy: present/created/executed
Render credential action ready/approved/executed: yes/yes/yes
production deployment approval ready/approved/executed: no/no/no
Render public preview deployment ready/approved/executed: yes/yes/yes
```

Render 전용 GitHub classic PAT는 `read:packages` only, 만료일 2027-07-23으로 만들고 `upgrade-rpg-ghcr-read` credential에 저장했습니다. 첫 PAT는 브라우저 검사 출력에 노출된 것을 감지해 Render에 저장하지 않고 즉시 GitHub에서 폐기했습니다. 교체 PAT 값은 채팅·파일·Git·로그에 기록하지 않았습니다.

v338 checkpoint 당시 verified exact digest는 Render `Existing Image`에서 `Connect`에 성공했고 서비스 설정 화면까지 열렸지만 `Deploy Web Service`는 누르지 않았습니다. 이후 v347에서 backend Web Service 최초 배포를 완료했습니다. v338 sanitized evidence는 `deploy/review/render-private-ghcr-connect-v338.json`입니다.

## 로컬 코드 리뷰 보조 도구 — v339

Code Review Graph 2.3.7은 `%LOCALAPPDATA%\UpgradeRPGTools\code-review-graph`의 독립 환경에 CLI-only로 설치했습니다. 첫 로컬 그래프 상태는 385 files / 4,242 nodes / 35,407 edges이며 `.code-review-graph/`는 Git에서 제외합니다. backend `.venv`와 프로젝트 dependency는 변경하지 않았습니다.

`code-review-graph install`, MCP, Codex hook/instruction 주입, watch/daemon, Git hook, cloud embedding은 사용하지 않습니다. 다중 파일 리뷰가 실제로 필요할 때만 수동 CLI 결과를 보조 evidence로 사용하고, 그래프 위험도만으로 결함이나 수정 필요성을 단정하지 않습니다.

Ponytail 플러그인은 설치하지 않았습니다. 새 추상화·의존성·파일보다 기존 기능을 먼저 사용하고 요청하지 않은 미래용 구조를 만들지 않는 최소 구현 원칙만 `AGENTS.md`에 반영했습니다. 안전·보안·검증·접근성 요구는 단순화를 이유로 생략하지 않습니다.

## Render/Neon 분리 계획과 bootstrap fix — v341

두 계획은 `docs/current/RENDER_SERVICE_SETTINGS_PLAN.md`, `docs/current/NEON_DATABASE_INITIALIZATION_MIGRATION_PLAN.md`와 대응하는 `deploy/*.example.json` 계약으로 검토 완료했습니다.

Neon production branch의 기본 `neondb`는 처음에는 public table 0개, `alembic_version` 없음이었고 새 `rpg_game` DB는 만들지 않았습니다. 현재는 검증된 local custom dump의 22 application tables / 748 rows를 direct URL로 restore하고 exact `v295_initial_schema` stamp까지 완료했습니다.

Render 서비스 이름은 기호가 `upgrade-rpg-api`로 확정했습니다. v341 source는 SQLAlchemy runtime과 Alembic에 같은 system-CA hostname-verifying SSLContext를 전달하며, `deploy/render.production.env.example`에 Render 전용 환경변수 inventory를 분리했습니다. 실제 Neon direct URL을 프로세스에만 주입한 read-only 검사도 통과했습니다.

v341 source를 포함한 새 image는 게시와 isolated Alpine system CA store, runtime health, architecture, cleanup 검증을 완료했습니다. Render 생성·배포는 아직 하지 않았습니다.

고정 순서는 image publish/isolated validation 완료 → Neon restore 1회 완료 → DB stamp recovery 전용 exact-SHA 승인 후 exact v295 stamp만 실행 → Render 생성 전용 exact-SHA 승인 후 Web Service create/deploy입니다.

## 공급망 안전 baseline

- CI credential: GitHub Actions `GITHUB_TOKEN`
- source-controlled lifecycle gate: `deploy/github-actions-ghcr-publish-lifecycle.json`
- lifecycle: `preparation-closed` / `publishReviewerGateReady=false` / approval `null` / prior six attempts preserved
- lifecycle state machine: `preparation-closed` → `authorization-open` → `authorization-closed-awaiting-evidence` → `attempt-recorded`
- run `30180738530`: provenance/SBOM, exact-digest Trivy 0건, Cosign sign/verify 성공
- current preparation/authorization/closure/evidence: `fb231afa5081f5bfd7b459081a58bc5acd6699df` / `f5d69c1bbef101cc9124b9dede18c844ef80b59c` / `ebb5ef46e3115bc358d62d93a64002b8711f4232` / `cf9e0bab121186d2ac51f889f807348cc46f192c`
- current artifact IDs: `8625485901`, `8625478503`
- single-run policy: `run_attempt=1`, single dispatch, immediate closure, `closureCommitSha`, rerun 금지
- 역사 결과 `review-recorded-workflow-attempt-evidence` 보존
- isolated evidence: `deploy/review/isolated-image-pull-validation-v342.json`
- production plan: `deploy/production-deploy-plan.example.json`
- historical preparation/authorization/closure/record SHA: `36e8720a53ef7ff6a8334de6bc99646998d63fc9` / `26a11356e33c978afa8cd8a4881500fa62cdbc5c` / `1c4a982b2a35d3d45f59e7d9faefcdecca69e6c5` / `1f0340ddfcf3c8a74cf14110d5957627d4c5d38a`
- historical artifact IDs: `8525220616`, `8525254543`
- private plan에는 native required reviewer가 없어 exact-SHA owner approval을 유지

## 다음 작업

승인된 v343 SHA `d6df9984e00d08b28fd524dcfefeb492e334d5e9`로 Neon restore를 한 번 실행했습니다. 22 application tables / 748 rows / schema digest가 일치했고 stamp 전에 legacy data digest 비교가 session timezone 차이로 멈췄습니다. UTC-normalized digest는 verified rehearsal과 Neon이 정확히 일치하며 `alembic_version`은 없습니다.

사용자가 승인한 v344 SHA `cf0f506b6ae9dc9d4c02f3ab5313ca68be32676c`로 기존 복원 상태를 재검증하고 exact `v295_initial_schema`만 stamp했습니다. 최종 public 23 tables / total 749 rows, application 22 tables / 748 rows, unchanged UTC-normalized schema/data digest를 확인했습니다. restore와 stamp 재실행은 모두 비활성화했습니다.

Render 실행 준비는 완료됐습니다. Git/Docker 제외 `deploy/.env.production`에 direct asyncpg `DATABASE_URL`과 서로 다른 강한 JWT/admin secret이 준비됐고 값은 출력·문서화·커밋하지 않았습니다.

승인된 v346 SHA `81d1c4faa59194e8928d54fbecac28694ab139ab`로 Render Free Web Service `upgrade-rpg-api`를 Singapore에 생성하고 env 14개와 exact image로 최초 deploy를 한 번 실행했습니다. service `srv-d9iro458nd3s73acgmsg`, deploy `dep-d9iro4l8nd3s73acgnmg`는 Live이며 공개 주소는 `https://upgrade-rpg-api.onrender.com`입니다.

Render 내부 health, 공개 `/api/v1/health`, 단 한 번 요청한 `/api/v1/health/db`가 모두 HTTP 200 `status=ok`입니다. 최초 deploy 승인은 소비됐고 retry·두 번째 deploy는 금지합니다. 다음은 live backend 검토와 frontend 배포 위치, exact CORS origin, frontend API base URL 계획입니다.

승인된 v348 SHA `b13b1775093716800d7361ee1e8f94d8112eefc1`로 Render Free Static Site `gihohoho-upgrade-rpg`를 만들고 exact commit 최초 deploy를 한 번 실행했습니다. service `srv-d9iu337aqgkc73am4lh0`, deploy `dep-d9iu33faqgkc73am4m3g`는 Live이고 auto-deploy는 Off입니다. 공개 주소는 `https://gihohoho-upgrade-rpg.onrender.com/index.html`과 `/admin.html`이며 둘 다 HTTP 200입니다.

Render GitHub App은 `gihohoho/upgrade-rpg` 단일 private repository만 접근하도록 기호가 Confirm access를 완료했습니다. 핵심 정적 자산 세 개의 remote raw byte SHA-256은 approved source와 모두 일치합니다.

승인된 recovery SHA `e64d42d812d78de023dc6cbd7f960263bc1c2d15`로 backend CORS deploy `dep-d9ivfmvlk1mc73fbcv40`를 정확히 한 번 실행했습니다. deploy는 40.1초 만에 Live가 됐고 actual `CORS_ORIGINS`는 exact frontend origin 배열입니다. health와 preflight는 모두 HTTP 200이며 exact `Access-Control-Allow-Origin`을 반환합니다.

공개 게임의 CORS 오류는 사라졌지만 `/game/master-data` 464,098-byte 응답이 약 1.98초/1.83초 걸려 frontend 1.5초 timeout을 넘습니다. 따라서 게임은 아직 기존 JS 데이터로 폴백합니다. 공개 관리자 새 탭에서는 이전 `RpgAdminFieldHelp is not loaded` 오류 로그가 재현되지 않았습니다.

v351 source에서 frontend master-data 기본 timeout을 5초로 늘리고 backend 1KB 이상 응답에 GZip level 5를 적용했습니다. 전체 runtime blocking-I/O audit는 sync FastAPI route 0, async 내부 blocking 호출 0, frontend blocking 호출 0으로 통과했습니다. offline tooling은 Python 148 files/371 blocking calls와 JavaScript 94 files/126 sync calls를 별도 확인하고 `intentional-one-shot-cli`로 분류했습니다. master-data의 11개 DB 조회는 하나의 `AsyncSession`을 공유하므로 위험한 동시 task로 바꾸지 않고 순차 await를 유지했습니다.

v352에서 v351 source baseline `81beaa0864c3422fb9fc2071b9c4965936ecafac`의 backend image publish lifecycle을 `preparation-closed`, gate false, approval null, not-dispatched로 준비했습니다. v341 성공 run은 여섯 번째 history로 보존했습니다.

다음은 push된 v352 preparation commit의 정확한 40자리 SHA를 기호가 승인하는 단계입니다. 이번 승인은 backend image의 workflow 1회 게시와 공급망·isolated 검증까지만 포함합니다. Render backend exact-image deploy와 frontend Static Site deploy는 새 digest 확인 뒤 별도 준비 commit·별도 exact-SHA 승인을 받습니다. 실제 공개 게임의 무폴백 로드와 관리자 guarded 콘텐츠 흐름을 확인하기 전까지 콘텐츠 추가·수정 시작 시점은 아닙니다.

현재 필요한 사용자 조치, extension, 권한, 새 설치는 없습니다.

## 첫 검사

실행 위치: 프로젝트 루트
Python `.venv` 상태: 셸 활성화는 꺼짐, `backend/.venv/Scripts/python.exe` 직접 사용
새 설치 여부: 없음

```bash
python tools/check_v351_public_release_gates.py --strict
python tools/smoke/backend/smoke_v351_public_release_gates.py
python tools/check_runtime_blocking_io.py --strict
python tools/smoke/backend/smoke_master_data_latency_guard.py
node tools/smoke/game/smoke_master_data_auto_boot_policy.js
python tools/check_frontend_static_deployment_plan.py --strict
node tools/smoke/frontend/smoke_legacy_static_deployment_preparation.js
python tools/prepare_render_local_environment.py --inspect-local
python tools/smoke/backend/smoke_render_service_creation_preparation.py
python tools/initialize_neon_database.py
python tools/smoke/backend/smoke_neon_database_initialization_guard.py
python tools/check_render_neon_separated_plan.py --strict
python tools/smoke/backend/smoke_neon_production_database_bootstrap.py
python tools/check_render_private_ghcr_connect.py --strict
python tools/check_neon_readonly_connectivity.py --evidence
python tools/check_production_provider_selection.py --strict
python tools/check_production_deployment_plan.py --strict
python tools/check_github_actions_ghcr_static_plan.py --strict
python tools/check_codex_handoff_readiness.py --strict
```

v352 기대 결과는 `v351-backend-image-preparation-closed-owner-approval-required`, 다음 단계는 `owner-approve-v352-v351-backend-image-preparation-sha`입니다. v351의 `runtime-blocking-io-audit-passed`와 `prepare-v351-image-and-static-release-exact-sha-gates`는 완료된 source checkpoint로 보존합니다. v350 recovery, v348 static deploy, v347 backend, v345 Neon 완료, v342 image, v338 Render Connect, v335 provider selection, v334 generic deployment baseline도 보존합니다.

별도 승인 전에는 추가 deploy, Render env 변경, DB/Alembic mutation, auth/API write, Vue Preview/Apply/write, 게임 콘텐츠·밸런스를 변경하지 않습니다.
