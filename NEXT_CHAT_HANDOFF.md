# Upgrade RPG Codex handoff — v368

## 현재 상태

```txt
latest: v368.v363-crystal-draft-descendants-fully-replaced
strict result: v363-crystal-draft-descendants-fully-replaced
next safe stage: owner-review-v368-local-equipment-icons-and-select-next-content-step
v355 provider checkpoint: v355.v351-provider-release-deployed-verified-content-ready / v351-provider-release-deployed-verified-content-ready / select-first-content-and-balance-change-scope
v354 provider preparation checkpoint: v354.v351-provider-release-prepared-exact-sha-approval-required / v351-provider-release-prepared-exact-sha-approval-required / owner-approve-v354-v351-provider-release-preparation-sha
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
Render live reference: ghcr.io/gihohoho/upgrade-rpg-backend@sha256:143be5eb21ec8c9318c7d0c4f3fbd5ac2de32439977a1d660c7247b6d3a507ac
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

공개 `/api/v1/health`와 한 번 요청한 `/api/v1/health/db`가 모두 HTTP 200 `status=ok`입니다. DB/Alembic write, image 변경, custom domain/DNS, 결제, 자동 retry·두 번째 deploy는 없었습니다. 당시 다음 단계였던 live backend·frontend·CORS 검토는 v348~v355에서 완료됐습니다.

승인된 v348 SHA `b13b1775093716800d7361ee1e8f94d8112eefc1`로 Render Free Static Site `gihohoho-upgrade-rpg`를 만들고 exact commit 최초 deploy를 한 번 실행했습니다. service `srv-d9iu337aqgkc73am4lh0`, deploy `dep-d9iu33faqgkc73am4m3g`는 Live이고 auto-deploy는 Off입니다. 공개 주소 `https://gihohoho-upgrade-rpg.onrender.com/index.html`, `/admin.html`은 둘 다 HTTP 200입니다.

Render GitHub App은 `gihohoho/upgrade-rpg` 단일 private repository만 접근하도록 기호가 Confirm access를 완료했습니다. 핵심 정적 자산 세 개의 remote raw byte SHA-256은 approved source와 모두 일치합니다.

승인된 recovery SHA `e64d42d812d78de023dc6cbd7f960263bc1c2d15`로 backend CORS deploy `dep-d9ivfmvlk1mc73fbcv40`를 정확히 한 번 실행했습니다. deploy는 40.1초 만에 Live가 됐고 actual `CORS_ORIGINS`는 exact frontend origin 배열입니다. health와 preflight는 모두 HTTP 200이며 exact allow-origin을 반환합니다.

v350 당시 공개 게임은 `/game/master-data` 464,098-byte 응답이 약 1.98초/1.83초로 1.5초 timeout을 넘어 기존 JS 데이터로 폴백했습니다. 이 문제는 v351 수정과 v355 배포에서 1,346ms·gzip·no-fallback으로 해결됐고 공개 관리자 오류 로그도 재현되지 않았습니다.

v351 source에서 frontend master-data 기본 timeout을 5초로 늘리고 backend 1KB 이상 응답에 GZip level 5를 적용했습니다. 전체 runtime blocking-I/O audit는 sync FastAPI route 0, async 내부 blocking 호출 0, frontend blocking 호출 0으로 통과했습니다. offline tooling은 Python 148 files/371 blocking calls와 JavaScript 94 files/126 sync calls를 별도 확인하고 `intentional-one-shot-cli`로 분류했습니다. master-data의 11개 DB 조회는 하나의 `AsyncSession`을 공유하므로 위험한 동시 task로 바꾸지 않고 순차 await를 유지했습니다.

v352 준비 SHA 승인 뒤 v351 backend image workflow를 정확히 한 번 실행했습니다. run `30226905547`은 성공했고 새 exact digest의 Trivy·SLSA provenance·SPDX SBOM·Cosign과 v353 isolated runtime/CA-store/cleanup이 모두 통과했습니다. lifecycle은 `attempt-recorded`, gate false이며 rerun은 금지합니다.

기호가 exact v354 준비 SHA `05f1af8ed1316e2cf0e0f39ac795b3ff60bccb62`를 승인했습니다. backend image update deploy `dep-d9jeuf3eo5us73ba6cgg`와 Static Site v351 exact-source deploy `dep-d9jev7gu01pc73favje0`를 각각 정확히 한 번 실행했고 둘 다 Live입니다. auto-deploy와 automatic retry는 계속 Off입니다.

공개 health/DB health/index/admin/CORS/gzip master-data를 검증했습니다. master-data는 1,346ms, `gzip`, HTTP 200이며 게임 runtime applied 로그가 있고 fallback 경고·브라우저 오류는 없습니다. 관리자는 read-only, 11 domains/729 rows, 전체 쓰기 UI blocked, write key missing이며 어떤 write 버튼도 실행하지 않았습니다. sanitized evidence는 `deploy/review/render-v351-provider-release-v355.json`입니다.

Render 설정 검사 출력에 포함된 backend/static deploy hook은 둘 다 즉시 재발급했고 새 값은 기록하지 않았습니다. DB/Alembic/admin write/콘텐츠·밸런스 변경/custom domain/DNS/payment/추가 Actions·두 번째 deploy는 없었습니다.

## 장비 스킬 피해 공식 변경과 전체 감사 — v357

- 12-1 `-초월- 어둠을 지배하는 고리 +20`: 공격력 `69.1B`, 스킬 피해 `607%`, 모든 피해 내부값 `173.9%`
- 16단계 `무의식 : 넥스의 몽환의 어둠 +20`: 공격력 `369B`, 스킬 피해 `2121%`, 기존 모든 피해 내부값 `225.8%`
- +20 단계 공식: 12단계 `607%`와 16단계 `2121%`를 단계당 `1.36721871444...`배 기하 보간하고 17단계 이후 같은 비율로 외삽
- 강화 공식: +0 기본값 `10 × 단계`를 유지하고 +1~+19는 기존 `enhanceTable.sdmg` 진행률로 해당 단계 +20 목표까지 보간
- +20 결과: 13단계 `829.9%`, 14단계 `1134.7%`, 15단계 `1551.3%`, 17단계 `2899.9%`, 18단계 `3964.8%`, 39단계 `2823673.9%`
- 17단계 이후 실제 스킬 피해 실측 기준은 저장소에 없으므로 새 기준이 생기기 전까지 위 기하비율을 추정 외삽
- 대상: 12~39단계에서 각 단계 첫 번째 `skill_all` 장비 28종, 그중 사용자 요청의 13+는 27종
- 비대상: 1~11단계, 공격력, 모든 피해, 공격력 추가, 평타 피해, 추가 스킬, 평타 치명
- 비대상 교차 기준: 17단계 스태프 추가 스킬 계수 `2097179%`, 창 치명 피해 `803447%`, 18단계 보석 공격력 `851B`·평타 피해 `7506%` 정확히 유지
- 감사: 1~12단계 일반 장비 60종 + 탈리스만 5종, 12~39단계 스킬 장비 전 강화, 16단계 +0~+20 명시값, seed 3중 일치, 12~39 비대상 2,940조합 해시 불변
- 공식 판단: 모든 옵션 단일 공식은 없지만 누락은 없으며 1~11 고정·구간별 공식과 12+ 생성 공식이 명시적으로 존재
- 별도 발견: 추가 스킬 계수의 기존 2차 외삽은 22단계부터 감소하고 33단계부터 음수가 되며 이번 스킬 피해 전용 작업에서는 변경하지 않음
- 계산식·기본값 변경 없음: `boss-factories.js`, generated seed, Neon DB, backend image/API
- 상세 문서: `docs/current/EQUIPMENT_PROGRESSION_FORMULA_AUDIT.md`
- 공개 반영: 다음 단계에서 v358 static-only fail-closed gate를 먼저 준비하고, 그 gate 준비 commit의 exact SHA 승인 뒤 기존 Render Static Site 수동 deploy 1회와 read-only 검증만 허용

## 아바타 강화·아이템 편의·필드 성장·캐시 보정 — v358

- 로컬 파일과 5500 HTTP에는 v357의 16단계 `2121%`가 있었지만 기존 Chrome 탭이 이전 `stat-system.js`를 캐시해 구버전 수치를 표시하는 현상을 재현했습니다.
- 공개 `https://gihohoho-upgrade-rpg.onrender.com/index.html`은 아직 승인된 v351 Static Site라 v357/v358 콘텐츠가 없는 것이 정상입니다.
- 변경된 여섯 JavaScript 태그에 최종 캐시 키 `?v=358.1`을 붙여 일반 새로고침에서도 최신 계산/UI 코드가 로드되게 했습니다.
- 세 기본 아바타만 +0~+20 강화 가능으로 연결했습니다. `찬란한 ... 아바타`는 이번 범위에서 제외했습니다.
- 세 아바타 +20 공통 공격력은 `88.2B`입니다.
- `무기 아바타 +20`: 평타 치명타 피해 배율 자체를 곱연산하는 증폭 `33.0%`
- `오라 아바타 +20`: 추가 스킬공격 계수 곱연산 증폭 `33.0%`
- `클론 레어 아바타 +20`: 스킬 치명타 확률 `10.0%`, 스킬 치명타 피해 배율 `150.0%`
- +0~+19는 기존 심연 특수장비의 21단계 성장 진행률로 보간하며 상세 표는 `docs/current/EQUIPMENT_PROGRESSION_FORMULA_AUDIT.md`에 있습니다.
- 기존에 표시만 되던 스킬 치명타 확률/피해를 실제 스킬 피해 계산에 연결했습니다.
- 스킬강화권은 남은 묶음이 있으면 창을 유지하며 연속 사용하고, 마지막 1장을 쓰면 “모두 사용함” 상태로 창을 유지합니다.
- 강화된 탈리스만/휘장에는 `+0으로 분해` 버튼이 보입니다. 선택한 강화품 1개를 같은 종류 +0 한 개로 되돌리며 강화 재료는 환급하지 않습니다.
- v358 당시 모든 필드 순수공격력 지급을 기존 최종 정수 지급값의 절반으로 바꿨지만, 이 규칙은 v360에서 **표시 상승량 100%·성공 확률 50%**로 대체됐습니다.
- 로컬 Chrome에서 무기 아바타 +0 `3.889B / 1.2%`, 강화 가능 버튼, 장착 +2 탈리스만의 분해 버튼을 확인했습니다.
- runtime/master-data source만 변경했으며 generated seed, Neon DB, backend image/API는 변경하지 않았습니다.
- 회귀 검사: `smoke_equipment_progression_formulas.js`, `smoke_runtime_item_quality_of_life.js`

## 아바타 분류·강화 초기화 UI·필드 전수 감사 — v359

- 특수장비로 뭉뚱그리던 아바타 설명을 이름에 따라 `[무기 아바타]`, `[오라 아바타]`, `[클론 레어 아바타]`로 구분하고 분류 색상을 파란 계열 `#6eb4ff`로 변경했습니다. `찬란한 ... 아바타`도 이름에 해당 분류가 있으면 같은 분류를 표시합니다.
- 탈리스만/휘장 강화 초기화 반환량은 `2^강화단계`입니다. +1/+2/+3/+4/+5/+6 → +0 2/4/8/16/32/64개입니다.
- 브라우저 기본 `confirm`을 제거하고 휴지통 경고창 계열의 게임 내부 모달을 추가했습니다. 모달은 대상, 변환 전후 수량, 되돌릴 수 없음 경고를 보여주며 확인 직전에 선택 상태도 재검증합니다.
- 탈리스만/휘장에서는 불필요한 20/50/200회 버튼을 숨기고 장착, 강화·초기화, 보관함, 휴지통 순으로 정리했습니다. 초기화 버튼 자체에도 반환 개수를 표시하고 좁은 화면은 한 열로 접힙니다.
- UI 상시 규칙: 앞으로 사용자에게 보이는 버튼·기능을 추가·변경할 때 시각 위계, 배치, 간격, 문구, 반응형, 확인·취소 흐름을 기능과 함께 완성하고 실제 브라우저에서 확인합니다. 파괴적 동작에는 브라우저 기본 alert/confirm을 사용하지 않습니다.
- v359 당시 필드 전수 감사에서 source/generated 40개와 33개 보상 필드의 공통 `gain *= 0.5` 경로를 확인했습니다. 이 절반 지급 규칙은 바로 아래 v360의 표시 상승량 100%·성공 확률 50% 규칙으로 대체됐습니다.
- 로컬 Chrome에서 +0 2개와 +3 1개를 초기화해 +0 10개가 되는 실제 동작, 전용 경고창, 새 버튼 배치, 아바타 파란 분류를 확인했습니다.
- CSS/변경 JavaScript 캐시 키: `?v=359`
- generated seed 내용, Neon DB, backend image/API, Render 서비스는 변경하지 않았습니다.

## 필드 1배·50% 설명 동기화·AI 특수장비 아이콘 — v360

- 순수공격력 보상이 있는 8~40단계 33개 필드는 처치 시 50% 확률로 각 필드에 표시된 상승량을 100% 지급합니다. 실패 시 상승량은 없습니다.
- source/generated field는 모두 `prob=0.5`이며, 과거 backend master-data의 `prob=1`이 남아 있어도 공통 런타임 helper가 50%로 고정합니다.
- 필드존 선택 고정 설명과 각 필드 툴팁은 확률·성공·실패·최대 누적을 실제 동작과 같은 문구로 표시합니다.
- 동작·수치·상태 변경 시 관련 제목, 고정 설명, 툴팁, 모달, 버튼, 로그, 캐시, source/generated seed, 검사와 현재 문서를 함께 전수 검색·동기화하는 상시 규칙을 `AGENTS.md`에 추가했습니다.
- built-in `image_gen`으로 특수무기·목걸이·반지 4단계, 아바타 3종 2단계, 탈리스만 4단계, 휘장 단일 이미지를 만들었습니다.
- 23개 256×256 PNG는 `src/assets/special-equipment/`에 있고 특수장비 38개가 이름·슬롯·등급에 따라 공유합니다. 기존 저장 placeholder와 보스 테스트 지급도 정규화됩니다.
- 정적 배포 허용 목록에 `src/assets/**/*.png`만 추가했고, 23개 PNG 포함과 signature를 fail-closed smoke로 고정했습니다.
- 최종 캐시 키는 `?v=360`입니다. generated field/item/drop seed는 동기화했지만 Neon DB write, backend image/API, Render deploy는 실행하지 않았습니다.
- 이미지 프롬프트·매핑 문서: `docs/current/SPECIAL_EQUIPMENT_AI_ICON_ASSETS.md`

## 테두리 없는 정사각형 full-bleed 특수장비 아이콘 — v361

- v360 아이콘 23개 안쪽에 있던 세로 카드 프레임·inset panel·빈 여백을 제거하고 모두 독립적인 1:1 close-up으로 다시 생성했습니다.
- 최종 파일은 동일한 256×256 PNG이며 테두리, 프레임, 카드판, rounded rectangle, margin band가 없습니다.
- 고정 판정 문구는 `테두리 없음·여백 없이 정사각형을 채움`입니다.
- 아이템과 마력 효과가 정사각형의 약 90~100%를 채웁니다. 종류가 즉시 보이면 체인·손잡이·어깨·광채 일부가 잘리는 구도를 허용합니다.
- 같은 계열은 기본 실루엣, 카메라 방향, 중심 정렬과 크기를 유지하고 상위 등급에서 색·장식·룬·광채만 발전시켰습니다.
- 고전 한국식 횡스크롤 액션 RPG·던전앤파이터풍, 동일 정사각형 크기, 테두리·카드판 금지, 여백 없는 full-bleed, 실제 브라우저 슬롯 검수를 앞으로의 상시 이미지 규칙으로 `AGENTS.md`에 기록했습니다.
- 같은 파일명의 이전 브라우저 캐시를 피하도록 이미지 URL과 `icon-utils.js` 로드 키를 `?v=361`로 갱신했습니다.
- 상세 생성·검수 규칙: `docs/current/SPECIAL_EQUIPMENT_AI_ICON_ASSETS.md`
- 장비 스펙·필드 규칙·Neon DB·backend API/image·Render 서비스는 변경하지 않았습니다.

## v363 단순 결정 시안 후손 43장 전체 교체 — v368

- 사용자가 지적한 범위는 `올 엘리멘탈 크리스탈` 한 계열이 아니라 commit `a696e1be3fe27beddc545cbba01e1e438573b7cc`에서 추가된 단순 파랑·금색 결정 시안 묶음 전체입니다.
- 해당 commit의 원본 15개와 v365의 티어별 파생 파일을 Git 이력으로 다시 추적했습니다. 현재 10~20단계에서 이어지는 후손은 55장이며, v364 반지 6장과 v367 4원소 크리스탈 6장을 제외한 나머지는 **13계열 43장**이었습니다.
- 10·11·12·18·19·20단계 3계열은 전쟁신 루비 메달, 초승달 진주 부적, 영혼 불꽃 흑마도서로 교체했습니다.
- 13·14·15단계 5계열은 조개 펜던트, 금 간 회중시계, 갑주 악마 심장, 살아 있는 세계수 뿌리, 흑적 마력포로 교체했습니다.
- 16·17단계 5계열은 넥스 꿈의 눈 부적, 봉인된 암흑 소용돌이 장치, 타락한 망토, 원초의 꿈 스태프, 원초의 꿈 창으로 교체했습니다.
- 모든 상위 단계는 같은 계열의 바로 전 단계 PNG를 built-in `image_gen` 편집 원본으로 사용했습니다. 물체 정체성·실루엣·각도·크롭을 유지하고 재질·룬·오라만 발전시켰습니다.
- 최종 43장은 모두 별도 256×256 PNG이고 SHA-256 중복은 0건입니다. `tools/smoke/game/smoke_equipment_icon_families.js`에 43장 전체 해시를 fail-closed로 고정했습니다.
- v364/v367 교체분을 합쳐 v363 단순 결정 시안에서 파생되어 현재 게임이 사용하는 PNG는 0개입니다. 일반 장비와 `icon-utils.js` 캐시는 `?v=368`입니다.
- 검토용 모음판은 Git 제외 `local-review-artifacts/v368-v363-descendants-43-icons.png`에 보존했습니다. 장비 전용 smoke와 legacy static 배포 smoke가 통과했습니다.
- 로컬 Chrome에서 `icon-utils.js?v=368`, 일반 장비 URL `?v=368`, 원본 256×256 → 화면 61×61 정사각형 렌더링과 콘솔 오류 0건을 확인했습니다.
- 앞으로 과거 commit·이미지 묶음의 시안을 폐기할 때는 대표 파일이나 한 계열만 보지 않고, 원본 추가 목록과 모든 tier별 복제·파생 후손을 Git으로 역추적해 함께 처리합니다.
- 변경 없음: 장비 능력치·강화 공식·드롭률, CSS 테두리 규칙, backend API/image, Neon DB, Render 서비스와 공개 v351 Static Site.

## 4원소 크리스탈 6단계·계열 테두리 동기화 — v367

- v367 당시에는 단순 파랑·금색 결정 시안 중 `올 엘리멘탈 크리스탈` 6장만 교체했습니다. 같은 v363 묶음의 나머지 43장은 v368에서 추가로 전부 교체했습니다.
- 10·11·12·18·19·20단계 `올 엘리멘탈 크리스탈`은 사용자가 확인한 불·물·바람·빛 사분할 보석을 기본형으로 삼아, 같은 실루엣·원소 위치·발톱·각도·크롭을 유지한 별도 256×256 발전형 PNG 6개로 다시 생성·적용했습니다.
- 여섯 파일은 `tier-{10,11,12,18,19,20}-atk-inc.png`이며 단계별 SHA-256을 focused smoke에 고정했습니다.
- 확정된 계열 단계가 이름 키워드보다 먼저 CSS 등급을 결정합니다. T21→22→23과 T24→25→26은 `basic → rare → transcendent`, T30→31→35→36은 `basic → rare → transcendent → liberated`입니다.
- 따라서 `끝없는` T23과 `영원한` T26은 초월, T35는 초월, T36은 해방 테두리입니다. 일반 이름 기반 판정은 다른 장비의 fallback으로 유지합니다.
- v367 당시 일반 장비 이미지와 `icon-utils.js` 캐시 식별자는 `?v=367`이었고, 현재는 v368 교체 때문에 `?v=368`입니다.
- 로컬 브라우저 DOM에서 새 캐시 경로와 T23 `item-frame-transcendent`를 확인했고, 기본·최종 4원소 PNG를 원본 크기로 직접 확인했습니다.
- 기본형 시안을 바꾸면 그 계열의 모든 파생 단계 PNG를 같은 작업에서 함께 다시 만들고, 이미지 단계와 CSS 테두리 단계를 항상 같이 맞추는 규칙을 `AGENTS.md`에 추가했습니다.
- 변경 없음: 장비 능력치·강화 공식·드롭률, backend API/image, Neon DB, Render 서비스와 공개 v351 Static Site.

## 9단계 초월 테두리·아이콘 원본 감사 — v366

- 9단계 `-초월- 흑염 : 잠식되는 천공`, `-초월- 흑조 : 갈라지는 천공`이 내부 단어 `천공` 때문에 `luminous`로 잘못 표시되는 충돌을 확인했습니다.
- `-초월-` 명시 표식을 내부의 `영롱`·`천공`·`진 각성`보다 먼저 판정하도록 수정했습니다. `[기본]` 표식도 내부 키워드보다 우선해 `basic`을 유지합니다.
- 1~39단계 일반 장비 195개의 명시 승급 표식을 전수 감사했고 같은 충돌은 위 2건뿐이었습니다.
- `icon-utils.js`의 HTML 캐시 키를 `?v=363`에서 `?v=366`으로 갱신하고 정적 배포 smoke에 고정했습니다. 일반 장비 PNG 자체는 변경하지 않아 이미지 URL `?v=365`를 유지합니다.
- 실제 Chrome에서 9단계 다섯 장비 모두 `item-frame-transcendent`, 2px 청록 테두리, 동일 box-shadow, 원본 256×256 → 화면 40×40, 브라우저 오류 0건을 확인했습니다.
- 195개 PNG를 5개 전체 검토표로 확대 감사했으며 이미지 파일 내부의 직사각형 카드·액자·바깥 테두리는 추가로 발견되지 않았습니다.
- Codex 생성 원본 폴더에는 초기 시안·합본·재생성 후보를 포함해 236개가 남아 있습니다. 프로젝트가 실제 사용하는 최종본은 `src/assets/equipment/`의 195개입니다. 최종 반지 승급 6장과 1단계 회중시계는 프로젝트에 적용됐고, 합본 비교판과 교체 전 시안은 슬롯 자산으로 사용하지 않습니다.

## 일반 장비 1~39단계 AI 이미지 전체 적용 — v365

- 일반 보스 1~39단계의 다섯 장비 종류에 각각 별도 256×256 PNG를 적용해 총 195개를 완성했습니다.
- 파일은 `src/assets/equipment/tier-{2자리 단계}-{장비 종류}.png` 규칙이며 폴더에는 실제 사용 중인 195개만 남겼습니다.
- 게임은 이름의 승급 표식을 추측하지 않고 `tier + equipGroup`으로 정확한 파일을 선택합니다. 모든 URL은 `?v=365` 캐시 식별자를 사용합니다.
- 같은 계열도 PNG를 공유하지 않습니다. 기본 실루엣·각도·구도와 주요 부품을 유지하면서 상위 단계에서 재질·색·장식·룬·마력 효과가 점진적으로 발전합니다.
- 13~15, 21~23, 24~26단계를 포함해 이름이 같거나 `[기본]` 이름을 바탕으로 한 상위 장비의 계열 관계를 이미지 디자인에 반영했습니다.
- 모든 PNG는 1:1 정사각형, 256×256, 이미지 내부 카드·테두리·문자 없음, full-bleed close-up과 굵은 만화형 외곽선을 사용합니다. 등급 테두리는 기존 CSS가 모든 인벤토리 화면에서 별도로 적용합니다.
- 검사 결과: 39단계 / 195장비 / 195고유 URL / 195 PNG signature·256×256 통과. 정적 배포 산출물의 195개 포함 여부도 별도 smoke로 고정했습니다.
- 실제 Chrome `http://127.0.0.1:5500/index.html`에서 1단계와 39단계의 다섯 장비를 확인했습니다. 모두 `?v=365`, 원본 256×256, 화면 40×40 정사각형으로 로드됐고 브라우저 오류는 0건입니다.
- 변경 없음: 장비 능력치·강화 공식·드롭률, 필드 규칙, backend API/image, Neon DB, Render 서비스.
- 전체 규칙과 파일 계약: `docs/current/NORMAL_EQUIPMENT_AI_ICON_ASSETS.md`

## 일반 장비 단계별 발전 이미지 규칙과 반지 6단계 — v364

- 일반 장비 195개는 최종적으로 각각 별도 PNG를 사용합니다. 같은 계열도 PNG를 공유하지 않고 기본 실루엣·카메라 각도·구도와 주요 부품을 유지한 채 단계별 재질·색·장식·룬·마력 효과를 발전시킵니다.
- 승급 표식을 제거한 이름이 같거나 더 긴 상위 이름 안에 기본 이름 전체가 포함되면 같은 계열입니다. 기호가 직접 고친 21·22·23 및 24·25·26단계 통합 표를 보존했습니다.
- v364에서는 `어둠을 지배하는 고리` 기본·진·초월·연옥·진 연옥·초월 연옥 6개를 굵은 외곽선과 만화식 명암의 별도 256×256 PNG로 완성했습니다.
- `src/assets/equipment/`에는 새 반지 6개와 다음 묶음에서 재생성할 기존 기본 이미지 14개, 총 20개가 있습니다. 일반 장비 캐시 키는 `?v=364`입니다.
- 전용 smoke는 10~20단계 55개 로컬 이미지, 반지 단계 6/6 별도 파일, 전체 20개 PNG signature·256×256과 정적 산출물 포함을 확인했습니다.
- 실제 Chrome에서 10·11·12·18단계 반지를 지급해 서로 다른 이미지와 기본·진·초월·연옥 CSS 테두리의 공통 적용을 확인했습니다.
- 다음 묶음은 10·11·12·18·19·20단계 나머지 4계열 24개입니다. 이전 단계 PNG를 편집 원본으로 사용해 같은 계열의 형태를 유지합니다.
- 전체 규칙·파일 매핑: `docs/current/NORMAL_EQUIPMENT_AI_ICON_ASSETS.md`
- 장비 수치·강화 공식·드롭률, 필드 규칙, backend API/image, Neon DB, Render 서비스는 변경하지 않았습니다.

## 일반 장비 이미지 계열 분류와 10~20단계 첫 묶음 — v363

> 아래는 v363 당시 기록입니다. 이미지 공유·115개 목표·`?v=363` 규칙은 v364에서 폐기됐으며 현재 판단에는 사용하지 않습니다.

- 일반 보스 1~39단계 장비 195개를 전수 분류했습니다. 승인된 승급 표식을 제거해 같은 이름을 묶으면 고유 PNG는 115개가 필요합니다.
- 계열 표식은 `-현-`, `-진-`, `-초월-`, `★심연★`, `★연옥★`, `★진 연옥★`, `★초월 연옥★`입니다. `끝없는 절망`, `영원한 파멸`처럼 실제 이름이 바뀌는 경우는 별도 계열입니다.
- v363에서는 10~20단계 장비 55개에 필요한 고유 이미지 15개를 built-in `image_gen`으로 만들었습니다. 모두 `src/assets/equipment/`의 256×256 PNG입니다.
- 같은 계열은 PNG를 공유하고 CSS 프레임만 강화합니다. `마음을 새긴 바다` 계열은 기본 → 진 → 심연, `어둠을 지배하는 고리` 계열은 기본 → 진 → 초월 → 연옥 → 진 연옥 → 초월 연옥 순서입니다.
- 새 아이콘은 글자·숫자·로고·내장 테두리·입자·날개·과도한 광채·복잡한 세공 없이 단일 물체와 굵은 실루엣, 2~3개 중심 색으로 단순하게 만들었습니다.
- 보스 드롭 원본, 신규 획득과 기존 저장 데이터의 가방·보관함·휴지통·장착칸·우편에서 같은 로컬 이미지 경로를 사용합니다.
- 일반 장비 에셋과 관련 JavaScript 캐시 식별자는 `?v=363`입니다. 특수장비 PNG와 URL은 `?v=361` 그대로입니다.
- 전용 smoke에서 10~20단계 55개 전체의 로컬 이미지, 고유 15계열, 승급 이름/등급 공유, PNG signature·256×256과 정적 배포 포함을 확인했습니다.
- 실제 Chrome에서 13·14·15단계 `마음을 새긴 바다`가 동일한 `engraved-sea-heart.png?v=363`을 사용하고 CSS 등급만 `basic / rare / dark`로 바뀌는 것을 확인했습니다. 원본 256×256, 목록 렌더링 40×40, 브라우저 오류 0건입니다.
- 전체 계열표·프롬프트·파일 매핑: `docs/current/NORMAL_EQUIPMENT_AI_ICON_ASSETS.md`
- 변경 없음: 장비 수치·강화 공식·드롭률, 필드 규칙, Neon DB, backend API/image, Render 서비스.

## 등급 CSS 테두리·위치 유지·수동 위로 정렬 — v362

- 사용자 요청에 따라 “게임 화면에서 테두리 없음” 정책은 취소했습니다. 23개 PNG 파일 자체는 다시 만들거나 수정하지 않고 v361 full-bleed 원본을 그대로 사용합니다.
- `getItemFrameGrade()`는 기본·강력·빛나는·초월·해방·찬란·짙은·영롱/천공/진 각성을 구분합니다. 기본은 효과 없는 흰색 테두리이고 상위 단계는 녹색·파란색·청록·금색·분홍·보라 계열의 이중선과 광채를 점진적으로 적용합니다.
- 높은 등급 호흡 효과는 `prefers-reduced-motion`에서 꺼집니다. 장착칸, 가방, 보관함, 휴지통, 관리창과 테스트 지급 미리보기가 같은 `applyItemFrameClass()`를 사용합니다.
- 가방·보관함·휴지통의 이동·사용·장착·강화 분리·+0 복원·휴지통 경로는 `clearItemSlot()`로 원래 칸을 `null`로 남기고, 신규·이동 아이템은 `placeItemInFirstEmptySlot()`로 첫 빈 칸에 둡니다. 공간 판정과 카운트는 실제 채워진 칸 수를 사용합니다.
- 세 패널 헤더에 `↑ 위로 정렬` 버튼을 배치했습니다. `compactPlayerItemContainer()`는 사용자가 버튼을 눌렀을 때만 아이템의 상대 순서를 유지하며 빈 칸을 제거합니다.
- focused runtime smoke에서 가방·보관함·휴지통의 중간 칸 유지, 수동 압축, 등급 판정과 기존 스택·강화 공간 회귀를 통과했습니다.
- 로컬 Chrome에서 가방 5번째 초월 목걸이를 보관함과 휴지통으로 각각 옮겼을 때 5번째 칸은 비고 6번째 초월 무기는 그대로 유지됐습니다. 보관함 `가방으로`와 휴지통 `가방으로 복구`는 첫 빈 칸인 원래 5번째 칸으로 돌려놓았습니다.
- 브라우저 검증 뒤 가방 25/60, 보관함 0/60, 휴지통 0/60과 원래 순서를 복구했습니다. 기본 흰색부터 영롱 다색까지 실제 64×64 렌더링, 관리창·장착칸 공통 프레임과 세 버튼 표시도 확인했습니다.
- CSS와 변경 JavaScript 로드 키는 `?v=362`입니다. 이미지 파일과 이미지 URL `?v=361`은 원본 미변경 때문에 유지합니다.
- 변경 없음: PNG 원본, 장비 수치·밸런스, 필드 규칙, Neon DB, backend API/image, Render 서비스.

현재 필요한 사용자 조치·extension·권한·새 설치는 없습니다. 다음 단계는 10·11·12·18·19·20단계의 나머지 4계열을 같은 실루엣의 단계별 발전형 24개 PNG로 생성·적용하는 것입니다. 전체 이미지 작업이 끝날 때까지 Render Static Site deploy는 실행하지 않습니다.

로컬 검사 주의: Windows 전역 `DEBUG=release`는 backend의 boolean `DEBUG`와 충돌합니다. 시스템 환경변수는 바꾸지 말고 backend/core 검사 자식 프로세스에서만 `DEBUG`를 unset하거나 `DEBUG=false`로 덮어씁니다.

## 첫 검사

실행 위치: 프로젝트 루트
Python `.venv` 상태: 셸 활성화는 꺼짐, `backend/.venv/Scripts/python.exe` 직접 사용
새 설치 여부: 없음

```bash
node tools/smoke/game/smoke_equipment_progression_formulas.js
node tools/smoke/game/smoke_runtime_item_quality_of_life.js
node tools/smoke/game/smoke_equipment_icon_families.js
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

v368 focused smoke는 1~39단계 일반 장비 195개의 서로 다른 로컬 이미지 URL, 정확한 `tier + equipGroup` 매핑, 전체 195개 PNG의 signature·256×256, 4원소 크리스탈 6개와 v368 교체 43개의 SHA-256, T23/T26/T35/T36 상위 테두리와 `icon-utils.js?v=368` 정적 배포 포함을 고정합니다. 다음 단계는 로컬에서 v368 이미지를 검토하고 다음 콘텐츠 작업 또는 별도 static release 범위를 선택하는 것입니다. 공개 Render Static Site는 계속 v351로 유지합니다. v362 인벤토리, v361 특수장비 이미지, v357 장비 공식과 이전 배포·공급자 baseline도 계속 보존합니다.

서버 재시작은 필요하지 않습니다.
