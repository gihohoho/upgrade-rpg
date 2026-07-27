# Upgrade RPG Codex handoff — v354

## 현재 상태

```txt
latest: v354.v351-provider-release-prepared-exact-sha-approval-required
strict result: v351-provider-release-prepared-exact-sha-approval-required
next safe stage: owner-approve-v354-v351-provider-release-preparation-sha
v353 image checkpoint: v351-image-publish-and-isolated-validation-complete
v352 preparation checkpoint: v352.v351-public-release-gates-prepared-backend-image-approval-required
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
verified reference: ghcr.io/gihohoho/upgrade-rpg-backend@sha256:f3bf6eed45e46e9d2022df4ab62eb6ca55b1ec0997b8ed342ae250c4a60052c1
provider selection: Render Free Singapore + Neon Free PostgreSQL 16 Singapore
fixed monthly cost: USD 0
Neon project/read-only connectivity: created/verified
Render account/plan/payment: connected/Hobby (legacy)/no card
Render registry credential/service/deploy: present/created/executed
Render credential action ready/approved/executed: yes/yes/yes
production deployment approval ready/approved/executed: no/no/no
Render public preview deployment ready/approved/executed: yes/yes/yes
```

## Render/Neon 분리 계획 — 2026-07-26

- Render 계약: `deploy/render-service-settings.example.json`
- Neon 계약: `deploy/neon-database-initialization-migration.example.json`
- v341 source: runtime/Alembic 공용 system-CA hostname-verifying SSLContext 적용 완료
- Render env inventory: `deploy/render.production.env.example`로 분리 완료
- 현재 verified image: v341 source 포함, 공급망·isolated CA-store/runtime 검증 완료
- Neon `neondb`: 초기화 완료 / application 22 tables·748 rows / public 23 tables·749 rows / exact v295
- DB 선택: 새 `rpg_game`을 만들지 않고 기존 빈 `neondb` 사용
- 이식: verified custom dump 22 application tables / 748 rows restore 후 exact `v295_initial_schema` stamp
- 연결: restore/Alembic/runtime 모두 direct; pooled URL은 restore/Alembic에 사용 금지
- 순서: image publish/isolated validation 완료 → Neon restore+exact v295 완료 → 별도 exact-SHA Render create/deploy
- Render name: `upgrade-rpg-api`, owner 확인 완료
- v345 tool: `tools/initialize_neon_database.py`, restore/stamp mutation 경로 비활성 + read-only completion guard
- v346 local prep: `tools/prepare_render_local_environment.py`, Git/Docker 제외 env와 secret-safe 검사
- v347 live: `https://upgrade-rpg-api.onrender.com`, Free Singapore, first deploy health/DB health 200
- read-only preflight: asyncpg system CA와 PostgreSQL 16/libpq exported Windows system CA `verify-full` 모두 통과
- current Neon mutation: restore 1회 + exact v295 stamp 1회 완료 / Render write 없음

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

Render workspace는 `Hobby (legacy)`이고 결제수단은 없습니다. v337 검사 당시 active service는 0개였으며 `Existing Image`와 GitHub Container Registry credential 흐름을 확인했습니다. 현재는 backend Web Service와 frontend Static Site가 각각 1개씩 있습니다. v337 evidence는 `deploy/review/render-account-readiness-v337.json`입니다.

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
- lifecycle: `attempt-recorded` / `publishReviewerGateReady=false` / approved preparation `b48dfd0751b12b1b3afb6474f9d35359ba2f8177`
- lifecycle state machine: `preparation-closed` → `authorization-open` → `authorization-closed-awaiting-evidence` → `attempt-recorded`
- run `30226905547`: run_attempt=1, provenance/SBOM, exact-digest Trivy 0건, Cosign sign/verify 성공
- v351 image preparation/authorization/closure/evidence: `b48dfd0751b12b1b3afb6474f9d35359ba2f8177` / `7578eb665c03ee0fcb9399929328ce684cdd1b31` / `5d547126322dbe3c235e855cc9c2f7337342ae36` / `5c842deec6d1f496679a144897f485b07428810b`
- v351 image artifact IDs: `8638838292`, `8638825538`
- verified v351 candidate: `ghcr.io/gihohoho/upgrade-rpg-backend@sha256:143be5eb21ec8c9318c7d0c4f3fbd5ac2de32439977a1d660c7247b6d3a507ac`
- run policy: `run_attempt=1`, single dispatch, immediate closure, `closureCommitSha`, rerun 금지
- 역사 lifecycle 결과 `review-recorded-workflow-attempt-evidence` 보존
- new candidate isolated evidence: `deploy/review/isolated-image-pull-validation-v353.json`
- current live image isolated evidence: `deploy/review/isolated-image-pull-validation-v342.json`
- production plan: `deploy/production-deploy-plan.example.json`
- historical preparation/authorization/closure/record SHA: `36e8720a53ef7ff6a8334de6bc99646998d63fc9` / `26a11356e33c978afa8cd8a4881500fa62cdbc5c` / `1c4a982b2a35d3d45f59e7d9faefcdecca69e6c5` / `1f0340ddfcf3c8a74cf14110d5957627d4c5d38a`
- historical artifact IDs: `8525220616`, `8525254543`
- private plan에는 native required reviewer가 없어 exact-SHA owner approval을 유지
- actual deploy는 placeholder 없는 실행 준비 commit의 정확한 40자리 SHA를 기호가 별도 승인한 뒤에만 실행

## 유지할 안전 경계

- 추가 Render Web Service 생성, 자동 deploy, 승인되지 않은 추가 deploy 금지
- Render payment method 추가 금지
- actual Neon URL, JWT/admin secret, CORS origin의 Render 주입 금지
- DB create/delete/restore/reset/seed/write와 Alembic mutation 금지
- 인증/API write, Vue Preview/Apply/write, 게임 콘텐츠·밸런스 변경 금지
- auto-deploy, automatic migration, automatic retry 금지
- actual secret/token/PAT/password/CA/cert/key를 Git·채팅·로그·artifact에 기록하지 않음

## 다음 단계

사용자가 승인한 v343 SHA `d6df9984e00d08b28fd524dcfefeb492e334d5e9`로 단일 트랜잭션 restore를 한 번 실행했습니다. 22 tables / 748 rows / schema digest는 즉시 일치했지만 legacy data digest가 session timezone offset에 의존해 달라졌고 도구는 stamp 전에 안전하게 중단했습니다.

verified local rehearsal은 `Asia/Seoul`, Neon은 `GMT`이며 양쪽에 44개 `timestamptz` 컬럼이 있습니다. aware datetime을 UTC로 정규화한 application data digest `4ea23cfd2446b522cc9e85e2a8520160427cf8e3987d9b6ab04f4b99fbf6c00c`로 양쪽이 정확히 일치했습니다. sanitized evidence는 `deploy/review/neon-restore-prestamp-verification-v344.json`입니다.

사용자가 승인한 v344 SHA `cf0f506b6ae9dc9d4c02f3ab5313ca68be32676c`로 기존 복원 상태를 재검증하고 exact `v295_initial_schema`만 stamp했습니다. `pg_restore`는 재실행하지 않았습니다. 최종 public 23 tables / total 749 rows, application 22 tables / 748 rows, unchanged schema/data digest, Alembic 1 row를 확인했습니다. sanitized evidence는 `deploy/review/neon-initialization-completed-v345.json`입니다.

승인된 v346 SHA `81d1c4faa59194e8928d54fbecac28694ab139ab`로 Render Free Web Service `upgrade-rpg-api`를 Singapore에 생성하고 env 14개와 exact image로 첫 deploy를 한 번 실행했습니다. service `srv-d9iro458nd3s73acgmsg`, deploy `dep-d9iro4l8nd3s73acgnmg`는 Live입니다.

공개 `/api/v1/health`와 한 번 요청한 `/api/v1/health/db`가 모두 HTTP 200 `status=ok`입니다. DB/Alembic write, image 변경, custom domain/DNS, 결제, 자동 retry·두 번째 deploy는 없었습니다. 다음은 live backend 검토와 frontend 배포/CORS origin 계획이며 필요한 extension·권한·새 설치는 현재 없습니다.

승인된 v348 SHA `b13b1775093716800d7361ee1e8f94d8112eefc1`로 Render Free Static Site `gihohoho-upgrade-rpg`를 만들고 exact commit 최초 deploy를 한 번 실행했습니다. service `srv-d9iu337aqgkc73am4lh0`, deploy `dep-d9iu33faqgkc73am4m3g`는 Live이고 auto-deploy는 Off입니다. 공개 주소 `https://gihohoho-upgrade-rpg.onrender.com/index.html`, `/admin.html`은 둘 다 HTTP 200입니다.

Render GitHub App은 `gihohoho/upgrade-rpg` 단일 private repository만 접근하도록 기호가 Confirm access를 완료했습니다. 핵심 정적 자산 세 개의 remote raw byte SHA-256은 approved source와 모두 일치합니다.

승인된 recovery SHA `e64d42d812d78de023dc6cbd7f960263bc1c2d15`로 backend CORS deploy `dep-d9ivfmvlk1mc73fbcv40`를 정확히 한 번 실행했습니다. deploy는 40.1초 만에 Live가 됐고 actual `CORS_ORIGINS`는 exact frontend origin 배열입니다. health와 preflight는 모두 HTTP 200이며 exact allow-origin을 반환합니다.

공개 게임의 CORS 오류는 사라졌지만 `/game/master-data` 464,098-byte 응답이 약 1.98초/1.83초 걸려 frontend 1.5초 timeout을 넘고 기존 JS 데이터로 폴백합니다. 공개 관리자 새 탭에서는 이전 `RpgAdminFieldHelp is not loaded` 오류 로그가 재현되지 않았습니다.

v351 source에서 frontend master-data 기본 timeout을 5초로 늘리고 backend 1KB 이상 응답에 GZip level 5를 적용했습니다. 전체 runtime blocking-I/O audit는 sync FastAPI route 0, async 내부 blocking 호출 0, frontend blocking 호출 0으로 통과했습니다. offline tooling은 Python 148 files/371 blocking calls와 JavaScript 94 files/126 sync calls를 별도 확인하고 `intentional-one-shot-cli`로 분류했습니다. master-data의 11개 DB 조회는 하나의 `AsyncSession`을 공유하므로 위험한 동시 task로 바꾸지 않고 순차 await를 유지했습니다.

v352 준비 SHA 승인 뒤 v351 backend image workflow를 정확히 한 번 실행했습니다. run `30226905547`은 성공했고 새 exact digest의 Trivy·SLSA provenance·SPDX SBOM·Cosign과 v353 isolated runtime/CA-store/cleanup이 모두 통과했습니다. lifecycle은 `attempt-recorded`, gate false이며 rerun은 금지합니다.

v354에서 기존 Render backend 서비스의 새 exact-image 수동 deploy 1회와 기존 Static Site의 v351 exact-source 수동 deploy 1회를 묶은 fail-closed provider release 계약을 준비했습니다. 다음은 push된 v354 preparation commit의 정확한 40자리 SHA를 기호가 승인하는 단계입니다. 승인 전에는 Render를 변경하지 않습니다.

실제 공개 게임의 무폴백 로드와 관리자 guarded 콘텐츠 흐름을 확인하기 전까지 콘텐츠 추가·수정 시작 시점은 아닙니다. 현재 필요한 사용자 조치·extension·권한·새 설치는 없습니다.

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

v354 기대 결과는 `v351-provider-release-prepared-exact-sha-approval-required`, 다음 단계는 `owner-approve-v354-v351-provider-release-preparation-sha`입니다. v353의 `v351-image-publish-and-isolated-validation-complete`, v351의 `runtime-blocking-io-audit-passed`, v350 recovery, v348 static deploy, v347 backend, v345 Neon 완료, v342 live image, v338 Render Connect, v335 provider selection과 v334 generic deployment baseline도 계속 보존합니다.

서버 재시작은 필요하지 않습니다.
