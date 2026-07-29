# Upgrade RPG Codex next prompt — v362

프로젝트 루트의 `AGENTS.md`, `NEXT_CHAT_HANDOFF.md`, `docs/current/CURRENT_STATUS.md`를 먼저 읽고 계속 지켜주세요. 기호는 코딩을 거의 모르므로 한국어로 쉽게 설명하고, 모든 터미널 명령 위에 실행 위치, Python `.venv` 상태, 새 설치 여부를 적어주세요. 필요한 extension·권한·설치는 해결될 때까지 요청해주세요.

Codex가 개발 서버와 기존 local PostgreSQL dependency를 필요에 따라 관리하고, 변경 뒤 Git add/commit/push까지 직접 합니다. ZIP과 Git 명령 안내는 필요 없습니다. root handoff와 `docs/handoff/` mirror는 매 작업 동기화합니다.

## 현재 고정값

```txt
latest: v362.item-grade-frames-stable-manual-compact-inventory-ready-static-deploy-gate-preparation-required
strict result: item-grade-frames-stable-manual-compact-inventory-ready-static-deploy-gate-preparation-required
next safe stage: prepare-v362-static-content-deploy-exact-sha-gate
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
visibility/platform: private / linux/amd64
production reference: ghcr.io/gihohoho/upgrade-rpg-backend@sha256:f3bf6eed45e46e9d2022df4ab62eb6ca55b1ec0997b8ed342ae250c4a60052c1
Render live reference: ghcr.io/gihohoho/upgrade-rpg-backend@sha256:143be5eb21ec8c9318c7d0c4f3fbd5ac2de32439977a1d660c7247b6d3a507ac
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
- lifecycle: `attempt-recorded` / `publishReviewerGateReady=false` / approved preparation `b48dfd0751b12b1b3afb6474f9d35359ba2f8177`
- lifecycle state machine: `preparation-closed` → `authorization-open` → `authorization-closed-awaiting-evidence` → `attempt-recorded`
- run `30226905547`: run_attempt=1, provenance/SBOM, exact-digest Trivy 0건, Cosign sign/verify 성공
- current preparation/authorization/closure/evidence: `b48dfd0751b12b1b3afb6474f9d35359ba2f8177` / `7578eb665c03ee0fcb9399929328ce684cdd1b31` / `5d547126322dbe3c235e855cc9c2f7337342ae36` / `5c842deec6d1f496679a144897f485b07428810b`
- current artifact IDs: `8638838292`, `8638825538`
- verified v351 candidate: `ghcr.io/gihohoho/upgrade-rpg-backend@sha256:143be5eb21ec8c9318c7d0c4f3fbd5ac2de32439977a1d660c7247b6d3a507ac`
- single-run policy: `run_attempt=1`, single dispatch, immediate closure, `closureCommitSha`, rerun 금지
- 역사 결과 `review-recorded-workflow-attempt-evidence` 보존
- new candidate isolated evidence: `deploy/review/isolated-image-pull-validation-v353.json`
- current live image isolated evidence: `deploy/review/isolated-image-pull-validation-v342.json`
- production plan: `deploy/production-deploy-plan.example.json`
- historical preparation/authorization/closure/record SHA: `36e8720a53ef7ff6a8334de6bc99646998d63fc9` / `26a11356e33c978afa8cd8a4881500fa62cdbc5c` / `1c4a982b2a35d3d45f59e7d9faefcdecca69e6c5` / `1f0340ddfcf3c8a74cf14110d5957627d4c5d38a`
- historical artifact IDs: `8525220616`, `8525254543`
- private plan에는 native required reviewer가 없어 exact-SHA owner approval을 유지

## 다음 작업

v362까지 다음을 완료했습니다.

- 16단계 `무의식 : 넥스의 몽환의 어둠 +20`은 로컬 계산 `369B / 2121% / 225.8%`이며, 특수장비 이미지 최종 캐시 식별자는 `?v=361`입니다.
- 공개 Render Static Site는 아직 v351이므로 v357~v362 변경이 없는 것이 정상입니다.
- 스킬강화권 창 유지와 모든 보상 필드의 순수공격력 **표시 상승량 100%·성공 확률 50%**를 구현했습니다. source/generated 40개를 대조했고 보상이 있는 8~40단계 33개 전체가 공통 50% 판정 경로를 사용합니다.
- 필드존 선택 고정 설명과 각 필드 툴팁에 `처치 시 50% / 성공 시 표시 상승량 100% / 실패 시 상승 없음`을 함께 표시합니다.
- 무기/오라/클론 레어 아바타 +0~+20 성장과 +20 `88.2B`, 각각 `평타 치명 피해 증폭 33%` / `추가 스킬공격 계수 증폭 33%` / `스킬 치명 10%·150%`를 구현했습니다.
- 아바타 분류를 `[무기 아바타]`, `[오라 아바타]`, `[클론 레어 아바타]`로 나누고 파란색 계열로 변경했습니다.
- 탈리스만/휘장 강화 초기화는 `2^강화단계`만큼 +0을 반환합니다. 전용 게임 내부 확인 모달과 정리된 버튼 배치를 사용하며 +3 실측에서 +0 8개 반환을 확인했습니다.
- 상시 UI 규칙: 새 버튼·기능은 시각 위계, 배치, 간격, 문구, 반응형, 확인·취소 흐름까지 함께 완성하고 실제 브라우저에서 검증합니다. 파괴적 기능은 브라우저 기본 alert/confirm을 쓰지 않습니다.
- 상시 동기화 규칙: 동작·수치·상태를 바꾸면 관련 화면 제목, 고정 설명, 툴팁, 모달 안내, 버튼 문구, 로그, 캐시 키, source/generated seed, 회귀 검사와 현재 문서를 함께 전수 검색해 실제 동작과 같은 내용으로 맞춥니다.
- built-in `image_gen`으로 특수무기·목걸이·반지 4단계, 아바타 3종 2단계, 탈리스만 4단계, 휘장 단일 이미지를 만들었습니다. 최종 23개 256×256 PNG가 특수장비 38개에 계열·등급별로 연결됩니다.
- 23개 아이콘은 v361에서 모두 다시 생성했습니다. 이미지 안쪽의 세로 카드·테두리·빈 여백을 없애고, 아이템과 효과가 정사각형의 약 90~100%를 채우는 full-bleed close-up으로 통일했습니다. 일부 크롭은 종류를 즉시 알아볼 수 있을 때 허용합니다.
- v361의 `테두리 없음·여백 없이 정사각형을 채움`은 PNG 파일 내부에 카드 프레임을 그리지 않는다는 뜻으로 유지합니다. v362부터 게임 UI에는 별도의 CSS 등급 테두리를 항상 적용합니다.
- 기본 등급은 효과 없는 흰색 테두리이며 강력·빛나는·초월·해방·찬란·짙은·영롱 단계는 색, 이중선, 광채와 절제된 애니메이션이 점진적으로 강화됩니다. 장착칸·가방·보관함·휴지통·관리창·지급 미리보기에서 같은 판정을 사용하고 `prefers-reduced-motion`을 존중합니다.
- 가방·보관함·휴지통에서 아이템을 옮기거나 사용해도 뒤 아이템이 자동으로 당겨지지 않습니다. 원래 칸은 비어 있고 새 아이템은 첫 빈 칸을 사용합니다.
- 세 패널 헤더의 `↑ 위로 정렬` 버튼을 눌렀을 때만 기존 상대 순서를 유지하면서 빈 칸을 제거합니다.
- 로컬 Chrome에서 가방 5번째 아이템을 보관함과 휴지통으로 옮겨 5번째 칸이 비고 6번째 아이템이 그대로인 것을 확인했으며, 복구 후 원래 25/60·보관함 0·휴지통 0 상태로 되돌렸습니다.
- 이미지 생성 조건·계열별 프롬프트·파일 매핑은 `docs/current/SPECIAL_EQUIPMENT_AI_ICON_ASSETS.md`에 기록했습니다.
- 정적 배포 빌드는 기존 JS/CSS에 `src/assets/**/*.png`만 추가 허용하며, 23개 PNG 포함 여부와 PNG signature를 fail-closed smoke로 검사합니다.
- 스킬 치명타 확률/피해를 실제 스킬 피해 계산에 연결했습니다.
- generated field/item/drop seed는 동기화했지만 Neon DB write, backend image/API, Render 서비스는 변경하지 않았습니다.

다음 단계에서는 v362 static-only fail-closed 배포 계약/checker를 준비하고 push합니다. 그 준비 commit의 exact SHA를 기호가 별도 승인하기 전에는 Render Static Site deploy를 실행하지 않습니다.

승인된 v343 SHA `d6df9984e00d08b28fd524dcfefeb492e334d5e9`로 Neon restore를 한 번 실행했습니다. 22 application tables / 748 rows / schema digest가 일치했고 stamp 전에 legacy data digest 비교가 session timezone 차이로 멈췄습니다. UTC-normalized digest는 verified rehearsal과 Neon이 정확히 일치하며 `alembic_version`은 없습니다.

사용자가 승인한 v344 SHA `cf0f506b6ae9dc9d4c02f3ab5313ca68be32676c`로 기존 복원 상태를 재검증하고 exact `v295_initial_schema`만 stamp했습니다. 최종 public 23 tables / total 749 rows, application 22 tables / 748 rows, unchanged UTC-normalized schema/data digest를 확인했습니다. restore와 stamp 재실행은 모두 비활성화했습니다.

Render 실행 준비는 완료됐습니다. Git/Docker 제외 `deploy/.env.production`에 direct asyncpg `DATABASE_URL`과 서로 다른 강한 JWT/admin secret이 준비됐고 값은 출력·문서화·커밋하지 않았습니다.

승인된 v346 SHA `81d1c4faa59194e8928d54fbecac28694ab139ab`로 Render Free Web Service `upgrade-rpg-api`를 Singapore에 생성하고 env 14개와 exact image로 최초 deploy를 한 번 실행했습니다. service `srv-d9iro458nd3s73acgmsg`, deploy `dep-d9iro4l8nd3s73acgnmg`는 Live이며 공개 주소는 `https://upgrade-rpg-api.onrender.com`입니다.

Render 내부 health, 공개 `/api/v1/health`, 단 한 번 요청한 `/api/v1/health/db`가 모두 HTTP 200 `status=ok`입니다. 최초 deploy 승인은 소비됐고 retry·두 번째 deploy는 금지합니다. 당시 다음 단계였던 live backend·frontend 위치·CORS/API base 검토는 v348~v355에서 완료됐습니다.

승인된 v348 SHA `b13b1775093716800d7361ee1e8f94d8112eefc1`로 Render Free Static Site `gihohoho-upgrade-rpg`를 만들고 exact commit 최초 deploy를 한 번 실행했습니다. service `srv-d9iu337aqgkc73am4lh0`, deploy `dep-d9iu33faqgkc73am4m3g`는 Live이고 auto-deploy는 Off입니다. 공개 주소는 `https://gihohoho-upgrade-rpg.onrender.com/index.html`과 `/admin.html`이며 둘 다 HTTP 200입니다.

Render GitHub App은 `gihohoho/upgrade-rpg` 단일 private repository만 접근하도록 기호가 Confirm access를 완료했습니다. 핵심 정적 자산 세 개의 remote raw byte SHA-256은 approved source와 모두 일치합니다.

승인된 recovery SHA `e64d42d812d78de023dc6cbd7f960263bc1c2d15`로 backend CORS deploy `dep-d9ivfmvlk1mc73fbcv40`를 정확히 한 번 실행했습니다. deploy는 40.1초 만에 Live가 됐고 actual `CORS_ORIGINS`는 exact frontend origin 배열입니다. health와 preflight는 모두 HTTP 200이며 exact `Access-Control-Allow-Origin`을 반환합니다.

v350 당시 CORS 오류는 사라졌지만 `/game/master-data` 464,098-byte 응답이 약 1.98초/1.83초로 1.5초 timeout을 넘어 기존 JS 데이터로 폴백했습니다. 이 문제는 v351 수정과 v355 배포에서 1,346ms·gzip·no-fallback으로 해결됐고, 공개 관리자 오류 로그도 재현되지 않았습니다.

v351 source에서 frontend master-data 기본 timeout을 5초로 늘리고 backend 1KB 이상 응답에 GZip level 5를 적용했습니다. 전체 runtime blocking-I/O audit는 sync FastAPI route 0, async 내부 blocking 호출 0, frontend blocking 호출 0으로 통과했습니다. offline tooling은 Python 148 files/371 blocking calls와 JavaScript 94 files/126 sync calls를 별도 확인하고 `intentional-one-shot-cli`로 분류했습니다. master-data의 11개 DB 조회는 하나의 `AsyncSession`을 공유하므로 위험한 동시 task로 바꾸지 않고 순차 await를 유지했습니다.

v352 준비 SHA 승인 뒤 v351 backend image workflow를 정확히 한 번 실행했습니다. run `30226905547`은 성공했고 새 exact digest의 Trivy·SLSA provenance·SPDX SBOM·Cosign과 v353 isolated runtime/CA-store/cleanup이 모두 통과했습니다. lifecycle은 `attempt-recorded`, gate false이며 rerun은 금지합니다.

기호가 v354 준비 SHA `05f1af8ed1316e2cf0e0f39ac795b3ff60bccb62`를 승인했습니다. Render backend는 새 exact image로 deploy `dep-d9jeuf3eo5us73ba6cgg`, Static Site는 v351 exact source로 deploy `dep-d9jev7gu01pc73favje0`를 각각 정확히 한 번 실행했고 둘 다 Live입니다. health/DB health/index/admin/CORS/gzip master-data를 확인했으며 게임 runtime은 backend master-data 적용 로그와 fallback 경고 0건, 관리자는 read-only·전체 쓰기 UI blocked·write key missing을 확인했습니다. DB/Alembic/admin write/콘텐츠 변경/자동 retry는 없었습니다.

v356에서 12단계 `607%` 기준을 반영했고 v357에서 16단계 `무의식 : 넥스의 몽환의 어둠 +20 = 2121%` 기준을 추가해 12단계 이후 `skill_all` 장비 공식을 다시 조정했습니다. +20 목표는 두 기준점을 단계당 `1.36721871444...`배 기하 보간·외삽하고 +1~+19는 기존 강화표 진행률을 사용합니다. 13/14/15/17/18단계 +20은 각각 `829.9 / 1134.7 / 1551.3 / 2899.9 / 3964.8%`입니다. 17단계 이후 실제 스킬 피해 기준은 저장소에 없어 새 실측값이 생기기 전까지 추정 외삽임을 유지합니다.

별도 공식 감사에서 추가 스킬 계수의 기존 2차 외삽이 22단계부터 감소하고 33단계부터 음수가 되는 문제를 확인했습니다. 이번 요청은 스킬 피해 증가만이므로 그 옵션은 바꾸지 않았습니다. 실제 18단계 이후 추가 스킬 계수 기준을 받기 전에는 임의 수정하지 않습니다.

1~12단계 일반 장비 60종과 탈리스만 5종을 감사했습니다. 전체 장비 단일 공식은 없고 1~11 고정값·옵션별 예외 공식과 12+ 생성 공식이 함께 사용되지만 누락·중복·비의도 불일치는 없습니다. 상세 문서는 `docs/current/EQUIPMENT_PROGRESSION_FORMULA_AUDIT.md`, 회귀 검사는 `tools/smoke/game/smoke_equipment_progression_formulas.js`입니다.

공격력·모든 피해·나머지 4그룹·generated seed·Neon DB·backend image는 변경하지 않았습니다. 17단계 추가 스킬 계수 `2097179%`·치명 피해 `803447%`, 18단계 `851B / 평타 피해 7506%`도 기존값을 고정했습니다. 다음 단계에서는 기존 Static Site, exact source commit, auto-deploy Off, 수동 deploy 1회, backend/DB/env 무변경과 read-only 검증을 고정하는 v358 static-only fail-closed gate를 먼저 준비합니다. 그 gate 준비 commit의 정확한 40자리 SHA를 기호가 별도 승인하기 전에는 공개 배포하지 않습니다. sanitized provider evidence `deploy/review/render-v351-provider-release-v355.json`과 재발급된 deploy hook 보안 상태는 계속 보존합니다.

현재 필요한 사용자 조치, extension, 권한, 새 설치는 없습니다.

기호 PC의 Windows 전역 `DEBUG=release`는 backend boolean 설정과 충돌합니다. backend/core 검사에서는 시스템 값을 변경하지 말고 해당 자식 프로세스에서만 `DEBUG`를 unset하거나 `DEBUG=false`로 덮어쓰세요.

## 첫 검사

실행 위치: 프로젝트 루트
Python `.venv` 상태: 셸 활성화는 꺼짐, `backend/.venv/Scripts/python.exe` 직접 사용
새 설치 여부: 없음

```bash
node tools/smoke/game/smoke_equipment_progression_formulas.js
node tools/smoke/game/smoke_runtime_item_quality_of_life.js
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

v362 focused smoke는 v361 이미지 회귀와 함께 등급 프레임 판정, 기본 흰색 테두리, 세 저장 공간의 빈 칸 유지, 첫 빈 칸 배치, 수동 위로 정렬과 세 버튼을 고정합니다. PNG 원본과 이미지 URL은 v361 그대로이며 CSS·관련 JavaScript 로드 키는 `?v=362`입니다. 다음 단계는 `prepare-v362-static-content-deploy-exact-sha-gate`입니다. v357 장비 공식, v355 provider release, v353 image, v351 blocking-I/O, v350 recovery, v348 static deploy, v347 backend, v345 Neon, v342 이전 image, v338 Render Connect, v335 provider selection, v334 generic deployment baseline도 보존합니다.

별도 승인 전에는 추가 deploy, Render env 변경, DB/Alembic mutation, auth/API write, Vue Preview/Apply/write, 게임 콘텐츠·밸런스를 변경하지 않습니다.
