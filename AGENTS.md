# Upgrade RPG Codex working rules — v363

이 파일은 저장소 전체에 적용됩니다. 작업 시작 시 이 파일, `NEXT_CHAT_HANDOFF.md`, `docs/current/CURRENT_STATUS.md`를 먼저 읽습니다.

## 사용자와 설명

- 사용자는 코딩을 거의 모르는 **기호**입니다. 항상 쉽고 자세한 한국어로 설명합니다.
- 모든 터미널 명령 바로 위에 **실행 위치**, **Python `.venv` 상태**, **새 설치 여부**를 적습니다.
- backend 가상환경은 `backend/.venv`입니다. Git Bash에서는 `backend`에서 `source .venv/Scripts/activate`로 켭니다.
- Vue/npm은 `frontend/vue-app`에서 실행하며 Python `.venv`가 필요 없습니다.
- 필요한 extension, GitHub/repository/app 권한, 설치가 있으면 기호에게 요청하고 해결될 때까지 `NEXT_CHAT_PROMPT.md`, `NEXT_CHAT_HANDOFF.md`에도 반복 기록합니다.
- 공개 게임이 backend master-data를 폴백 없이 로드하고 관리자 guarded 콘텐츠 작업 흐름이 검증되어 콘텐츠 추가·수정을 시작하기 좋은 시점이 되면 기호에게 먼저 명확히 알립니다.
- 매 작업에서 루트 `NEXT_CHAT_PROMPT.md`, `NEXT_CHAT_HANDOFF.md`와 `docs/handoff/` mirror를 동기화합니다.
- 변경·검증 뒤 Codex가 `git status`, `git add`, `git commit`, `git push`를 직접 실행합니다. Git 명령 안내와 ZIP은 기호가 별도로 요구하지 않는 한 제공하지 않습니다.

## 개발 서버와 로컬 자원

- Codex는 터미널을 자유롭게 사용하고 **실행 중인 개발 서버를 재사용**합니다.
- backend `127.0.0.1:8000`, Vue `127.0.0.1:5173`, legacy static `127.0.0.1:5500`이 정상이면 재시작하지 않습니다.
- legacy 통합 확인은 `http://127.0.0.1:5500/index.html`, `/admin.html`을 사용합니다. `file://`는 origin이 `null`이라 API 통합 검증에 사용하지 않습니다.
- 기존 local PostgreSQL dependency의 단순 시작·중지는 가능하지만 reset·recreate·volume 삭제·seed·restore·migration은 별도 요청 전 금지합니다.
- Windows 전역 환경변수 `DEBUG=release`는 backend의 boolean `DEBUG`와 충돌합니다. backend/core 검사는 시스템 값을 바꾸지 말고 해당 자식 프로세스에서만 `DEBUG`를 unset하거나 `DEBUG=false`로 덮어씁니다.
- 서버를 재시작하지 않았으면 완료 답변에 “서버 재시작 불필요”라고 적습니다.

## 최소 구현 원칙

- 새 추상화·의존성·파일을 만들기 전에 기존 코드, Python/JavaScript 표준 기능, 브라우저·DB·프레임워크 기본 기능으로 해결할 수 있는지 먼저 확인합니다.
- 요청하지 않은 미래용 구조·설정·scaffolding은 만들지 않으며, 안전·보안·검증·접근성 요구는 단순화를 이유로 생략하지 않습니다.
- 사용자에게 보이는 버튼·기능을 추가하거나 바꿀 때 기능만 연결하지 않고 기존 화면의 시각 위계, 버튼 배치, 간격, 문구, 반응형 동작까지 함께 완성하고 실제 브라우저에서 확인합니다.
- 파괴적이거나 되돌리기 어려운 동작에는 브라우저 기본 `alert`/`confirm`을 쓰지 않고 기존 게임 UI와 일관된 확인·취소 모달을 사용하며, 결과와 반환 수량을 실행 전에 명확히 보여줍니다.
- 동작·수치·상태를 바꾸면 연관된 화면 제목, 고정 설명, 툴팁, 모달 안내, 버튼 문구, 로그, 캐시 키, source/generated seed, 회귀 검사와 현재 문서를 함께 전수 검색해 실제 동작과 같은 내용으로 동기화합니다.
- 생성형 인벤토리·아이템 이미지는 모두 동일한 정사각형 크기로 만듭니다. 이미지 파일 자체에는 테두리, 프레임, 카드판, inset panel, margin band를 넣지 않고 아이템과 효과가 네 변 가까이 닿도록 화면을 여백 없이 채우며, 종류를 한눈에 알아볼 수 있다면 일부가 잘리는 close-up 구도를 허용합니다. 고전 한국식 횡스크롤 액션 RPG·던전앤파이터풍의 굵은 외곽선, 선명한 만화식 명암, 작은 슬롯 판독성을 기준으로 합니다.
- 일반 장비 생성형 이미지는 64px에서도 종류가 보이는 단일 물체와 굵은 실루엣을 유지하되, 너무 밋밋하지 않도록 2~3개의 목적 있는 장식, 금속 하이라이트, 보석과 절제된 마력 효과를 허용합니다. 이미지 안에 글자·숫자·로고·희귀도 테두리·무관한 날개·과도한 입자·물체를 가리는 광채·복잡한 세공을 넣지 않습니다.
- 같은 일반 장비 계열도 승급 단계마다 별도 PNG를 만듭니다. 기본 이미지의 물체 정체성, 실루엣, 카메라 각도, 배치와 주요 부품을 유지한 채 단계가 오를수록 재질, 중심색, 기존 부품의 장식, 룬과 마력 효과를 점진적으로 발전시킵니다. 전혀 다른 물체로 재설계하거나 CSS 테두리만 바꿔 승급 이미지를 대신하지 않습니다.
- 일반 장비 계열은 `-현-`, `-진-`, `-초월-`, `★심연★`, `★연옥★`, `★진 연옥★`, `★초월 연옥★` 같은 승급 표식을 제거한 이름이 같으면 같은 계열입니다. 또한 `끝없는 절망 : 티아매트의 불신`이 `절망 : 티아매트의 불신`을, `영원한 파멸 : 베리아스의 불신`이 `파멸 : 베리아스의 불신`을 포함하는 것처럼 더 긴 상위 이름 안에 기본 장비 이름 전체가 들어 있으면 같은 계열로 봅니다. 여러 후보가 있으면 가장 긴 기본 이름을 우선하며 불명확하면 사용자에게 확인합니다.
- 게임 UI에서는 이미지 파일과 별개로 모든 아이템에 등급별 CSS 테두리를 일관되게 적용합니다. 기본 등급은 효과 없는 흰색 테두리이고, 강력·빛나는·초월·해방·찬란·짙은·영롱 등 상위 단계는 색상, 이중선, 광채와 절제된 애니메이션을 점진적으로 강화합니다. 이 판정은 장착칸, 가방, 보관함, 휴지통, 관리창과 지급 미리보기 등 아이템이 표시되는 모든 위치에서 유지하며 실제 브라우저 슬롯 크기와 `prefers-reduced-motion`에서도 확인합니다.
- 가방·보관함·휴지통에서 아이템을 이동·사용·장착해제·삭제해도 뒤 아이템을 자동으로 당기지 않고 원래 칸을 빈 칸으로 유지합니다. 새 아이템은 가장 앞의 빈 칸을 사용하고, 사용자가 각 패널의 `위로 정렬` 버튼을 눌렀을 때만 기존 상대 순서를 보존한 채 빈 칸을 제거합니다.

## Code Review Graph 제한 시험

- Code Review Graph 2.3.7은 사용자 전용 독립 환경에 설치한 **CLI-only 보조 도구**입니다. backend `.venv`와 프로젝트 dependency에는 포함하지 않습니다.
- Codex가 다중 파일 변경, 영향 범위, 생소한 코드 경로, PR·복합 버그 검토에 도움이 된다고 판단하면 수동 CLI를 적극 사용하고 결과를 원본 코드·테스트와 대조합니다.
- 좁은 `search`·`query`부터 사용하고 광범위 `impact`는 실제 필요할 때만 사용합니다. `install`, MCP, Codex hooks/instructions, watch/daemon, Git hook은 사용하지 않습니다.

## GitHub와 secret

- 기호는 작업 목적 안에서 Actions, workflow, action SHA, environment, variables와 필요한 GitHub 설정을 Codex가 구성하도록 허용했습니다.
- 숨김 파일과 `.env`는 점검·수정할 수 있지만 실제 secret/token/PAT/password/CA/cert/key를 Git·채팅·로그·artifact에 노출하거나 커밋하지 않습니다.
- root `.dockerignore`는 `.env`/`*.env`/`.envrc` 계열을 모두 제외하고 재포함을 금지합니다. `backend/Dockerfile.production.dockerignore`는 만들지 않습니다.
- 나중에 회전·폐기할 항목은 `docs/current/SECURITY_ROTATION_AND_GITHUB_GATES.md`에 기록합니다.
- 사용자 계정 선택, 추가 로그인, 결제/플랜, 실제 운영 공급자 선택처럼 Codex가 대신할 수 없는 일만 요청합니다.

## 현재 고정 상태

```txt
latest: v364.normal-equipment-tiered-icon-rule-ring-family-ready
strict result: normal-equipment-tiered-icon-rule-ring-family-ready
next safe stage: generate-v365-normal-equipment-tiered-icons-tier10-family-remainder
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
deployment safety baseline: v334.production-deploy-plan-reviewed-inputs-blocked / production-deploy-plan-reviewed-inputs-blocked
baseline next stage marker: select-production-targets-and-complete-executable-deploy-plan
GitHub remote: https://github.com/gihohoho/upgrade-rpg.git
GHCR repository: ghcr.io/gihohoho/upgrade-rpg-backend (private)
target: linux/amd64
verified production reference: ghcr.io/gihohoho/upgrade-rpg-backend@sha256:f3bf6eed45e46e9d2022df4ab62eb6ca55b1ec0997b8ed342ae250c4a60052c1
verified v351 candidate: ghcr.io/gihohoho/upgrade-rpg-backend@sha256:143be5eb21ec8c9318c7d0c4f3fbd5ac2de32439977a1d660c7247b6d3a507ac
Render live reference: ghcr.io/gihohoho/upgrade-rpg-backend@sha256:143be5eb21ec8c9318c7d0c4f3fbd5ac2de32439977a1d660c7247b6d3a507ac
architecture: managed PostgreSQL + verify-full + provider-managed HTTPS ingress + backend 1/1
Alembic current: v295_initial_schema / new revision needed: no
```

- CI credential은 GitHub Actions `GITHUB_TOKEN`, local pull은 GitHub CLI OAuth `read:packages` → Docker credential store입니다.
- image publish model은 `owner-only-source-controlled-two-step`입니다.
- source-controlled lifecycle gate는 `deploy/github-actions-ghcr-publish-lifecycle.json`의 `attempt-recorded`, `publishReviewerGateReady=false`입니다. 이전 run 6건은 `attemptHistory`에 보존하고 현재 run은 `observedAttempt`에 기록합니다.
- run `30226905547`은 run_attempt=1 단일 실행으로 build/SBOM/Trivy/provenance/Cosign을 통과했고 exact digest `sha256:143be5eb21ec8c9318c7d0c4f3fbd5ac2de32439977a1d660c7247b6d3a507ac`은 v353 isolated runtime/CA-store/cleanup까지 통과했습니다.
- 과거 run `30180738530`과 digest `sha256:f3bf6eed45e46e9d2022df4ab62eb6ca55b1ec0997b8ed342ae250c4a60052c1`은 이전 Render live image의 공급망·v342 isolated 증거로 보존합니다.
- 운영 배포 계획은 `deploy/production-deploy-plan.example.json`과 `docs/current/PRODUCTION_DEPLOYMENT_PLAN.md`에서 검토 완료했습니다.
- production host, managed DB, provider CA, reverse proxy/domain/certificate, secret injection, edge network, first-deploy rollback 입력은 아직 미확정입니다.
- production deployment approval ready/approved/executed는 `no/no/no`입니다.
- Render public preview deployment ready/approved/executed는 `yes/yes/yes`입니다.
- Render GitHub App은 `gihohoho/upgrade-rpg` 단일 저장소만 접근하도록 연결됐습니다.
- frontend Static Site `gihohoho-upgrade-rpg`는 v351 exact source `81beaa0864c3422fb9fc2071b9c4965936ecafac`로 Live이며 auto-deploy는 꺼져 있습니다.
- 공개 게임/관리자 주소는 `https://gihohoho-upgrade-rpg.onrender.com/index.html`, `/admin.html`이고 둘 다 HTTP 200입니다.
- 승인된 recovery SHA `e64d42d812d78de023dc6cbd7f960263bc1c2d15`로 backend CORS deploy `dep-d9ivfmvlk1mc73fbcv40`를 정확히 한 번 실행했고 Live입니다.
- 실제 `CORS_ORIGINS`는 exact frontend origin 배열로 저장됐으며 health/preflight 200과 exact `Access-Control-Allow-Origin`을 확인했습니다.
- v351 source는 master-data 기본 timeout을 5초로 늘리고 backend 1KB 이상 응답에 GZip을 적용했습니다. 새 image/static deploy 뒤 공개 master-data는 1,346ms, gzip, no-fallback으로 검증됐습니다.
- v352 준비 SHA 승인으로 authorization `7578eb665c03ee0fcb9399929328ce684cdd1b31` → closure `5d547126322dbe3c235e855cc9c2f7337342ae36` → evidence `5c842deec6d1f496679a144897f485b07428810b` 전이를 완료했습니다.
- 기호가 exact v354 준비 SHA `05f1af8ed1316e2cf0e0f39ac795b3ff60bccb62`를 승인했고, backend image update deploy `dep-d9jeuf3eo5us73ba6cgg`와 Static Site v351 deploy `dep-d9jev7gu01pc73favje0`가 각각 정확히 한 번 실행되어 Live입니다.
- `/api/v1/health`, `/api/v1/health/db`, `/index.html`, `/admin.html`, exact CORS, gzip master-data no-fallback, 관리자 guarded read-only 흐름이 모두 검증됐습니다. DB health는 한 번만 요청했고 DB/Alembic/admin write/콘텐츠 변경/자동 retry는 실행하지 않았습니다.
- sanitized provider evidence는 `deploy/review/render-v351-provider-release-v355.json`입니다.
- v356에서 12단계 `607%` 기준을 반영했고, v357에서 16단계 `무의식 : 넥스의 몽환의 어둠 +20 = 2121%` 실측 기준을 추가해 고단계 공식을 다시 조정했습니다.
- 12단계 이상 `skill_all` 장비는 +0 기본값을 유지합니다. +20 목표는 12단계 `607%`와 16단계 `2121%`를 단계당 `1.36721871444...`배 기하 보간·외삽하고, +1~+19는 기존 `enhanceTable.sdmg` 진행률을 그대로 사용합니다.
- +20 스킬 피해는 13단계 `829.9%`, 14단계 `1134.7%`, 15단계 `1551.3%`, 17단계 `2899.9%`, 18단계 `3964.8%`, 39단계 `2823673.9%`입니다. 17단계 이후 실제 스킬 피해 실측값은 저장소에 없어 새 기준이 생기기 전까지 위 비율을 추정 외삽합니다.
- 사용자 교차 기준인 16단계 공격력 `369B`·기존 모든 피해 내부값 `225.8%`, 17단계 추가 스킬 계수 `2097179%`·치명 피해 `803447%`, 18단계 공격력 `851B`·평타 피해 `7506%`는 변경 없이 정확히 일치합니다.
- 1~12단계 일반 장비 60종과 탈리스만 5종을 감사했고 누락·중복은 없습니다. 전체 장비 단일 공식은 없으며 1~11 고정 데이터와 옵션별 구간·예외 공식, 12+ 생성·보간 공식이 함께 사용됩니다.
- 공격력, 모든 피해, 1~11단계, 나머지 4개 장비 그룹, generated seed, Neon DB와 backend는 변경하지 않았습니다. 상세 근거는 `docs/current/EQUIPMENT_PROGRESSION_FORMULA_AUDIT.md`입니다.
- 별도 감사에서 추가 스킬 계수의 기존 2차 외삽이 22단계부터 감소하고 33단계부터 음수가 되는 문제를 확인했습니다. 이번 스킬 피해 전용 범위에서는 바꾸지 않으며 실제 고단계 기준을 받아 별도 작업으로 다룹니다.
- v358은 세 기본 아바타 +0~+20 성장과 +20 `88.2B`, 무기 평타 치명 피해 증폭 `33%`, 오라 추가 스킬공격 계수 증폭 `33%`, 클론 스킬 치명 `10%/150%`를 실제 전투 합산까지 연결합니다.
- v358에서 스킬강화권 창 유지와 강화 탈리스만/휘장 `+0으로 분해`를 추가했고, v359에서 분해 반환량을 `2^강화단계`로 보완했습니다. v358의 필드 절반 지급은 v360에서 표시 상승량 100%·성공 확률 50% 규칙으로 대체됐습니다.
- Chrome 구형 JavaScript 캐시를 재현해 변경 스크립트에 최종 `?v=358.1` 캐시 키를 붙였습니다. 공개 Static Site는 아직 v351이므로 v357/v358 콘텐츠는 미배포입니다.
- v358 공개 반영은 backend image나 DB 작업 없이 기존 Render Static Site 수동 배포 1회만 필요합니다. 먼저 static-only fail-closed 계약/checker를 별도 준비한 뒤, 그 gate 준비 commit의 정확한 40자리 SHA를 기호가 승인하기 전에는 실행하지 않습니다.
- 전체 runtime blocking-I/O audit는 sync FastAPI route 0, async 내부 blocking 호출 0, frontend entrypoint·source blocking 호출 0으로 통과했습니다.
- offline tooling은 Python 148 files/371 blocking calls, JavaScript 94 files/126 sync calls를 별도 확인했고 서버·브라우저 event loop 밖의 `intentional-one-shot-cli`로 분류했습니다.
- master-data의 11개 async DB 조회는 하나의 `AsyncSession`을 공유하므로 동시 task로 바꾸지 않고 안전한 순차 실행을 유지합니다.
- 공개 정적 자산 세 개의 raw byte SHA-256은 approved source와 일치합니다. 새 관리자 탭에서는 이전 `RpgAdminFieldHelp` 오류 로그가 재현되지 않았습니다.
- 비용 최소 공급자는 Render Free Web Service Singapore + Neon Free PostgreSQL 16 Singapore로 선택했습니다.
- 첫 공개 주소는 Render `onrender.com` managed HTTPS이며 custom domain과 DNS 변경은 보류합니다.
- 무료 구성은 SLA production이 아닌 개인용 public preview이고 월 고정비 $0, idle cold start 허용 조건입니다.
- Neon Free PostgreSQL 16 AWS Singapore 프로젝트는 생성됐고 Neon Auth는 사용하지 않습니다. 채팅에 노출된 최초 `neondb_owner` 비밀번호는 2026-07-22에 재설정해 폐기했습니다.
- 새 Neon direct/pooled URL은 앱·배포 플랫폼에 아직 주입하지 않고 Git/Docker 제외 경로 `deploy/.env.production`에만 보관합니다.
- Direct/Pooler 모두 PostgreSQL 16.14, TLS 1.3 인증서·호스트 검증, read-only transaction을 통과했습니다. sanitized evidence는 `deploy/review/neon-readonly-connectivity-v336.json`입니다.
- Render `Hobby (legacy)` workspace는 연결됐고 결제수단·billing 정보가 없습니다. 현재 backend Web Service와 frontend Static Site가 각각 1개씩 있습니다.
- GitHub `Confirm access`는 사용자가 완료했고 Render 전용 classic PAT는 `read:packages` only, 만료일 2027-07-23으로 생성해 `upgrade-rpg-ghcr-read` credential에 저장했습니다. 실제 값은 Git·파일·채팅에 기록하지 않습니다.
- 브라우저 검사 출력에 노출된 첫 PAT는 Render에 저장하지 않고 즉시 GitHub에서 폐기했습니다. 교체 PAT는 값 출력 없이 전달했으며 회전 기록은 `docs/current/SECURITY_ROTATION_AND_GITHUB_GATES.md`에 있습니다.
- v355 Render 설정 검사 출력에 backend/static deploy hook 값이 포함돼 두 hook을 즉시 재발급했습니다. 새 값은 기록하지 않았고 회전은 추가 deploy를 만들지 않았습니다.
- v338 checkpoint에서 verified exact digest를 Render `Existing Image`로 `Connect`해 private GHCR 접근과 서비스 설정 화면 진입을 확인했으며, 그 시점에는 Web Service 생성·env 주입·deploy를 실행하지 않았습니다.
- Render 서비스 이름은 `upgrade-rpg-api`로 기호가 확정했습니다.
- v341 source는 production SQLAlchemy/Alembic에 system-CA hostname-verifying SSLContext를 공유 주입하고 Render env inventory를 분리했습니다.
- 실제 Neon direct URL을 프로세스에만 주입한 read-only bootstrap에서 TLS 연결과 빈 `neondb` 상태를 재확인했습니다.
- v341 source를 포함한 exact image로 Render Free Web Service `upgrade-rpg-api`를 Singapore에 생성했고 첫 deploy가 Live입니다.
- Neon production branch의 `neondb` 초기화가 완료됐습니다. 22 application tables / 748 rows와 `alembic_version` 1 table / 1 row, exact `v295_initial_schema`를 포함해 public 23 tables / total 749 rows입니다. 새 `rpg_game` DB는 만들지 않습니다.
- `tools/initialize_neon_database.py`의 mutation 경로는 모두 비활성화됐고 기본/static 및 `--inspect` read-only 완료 검증만 허용합니다.
- Git/Docker 제외 `deploy/.env.production`에는 Render용 direct asyncpg `DATABASE_URL`과 서로 다른 강한 JWT/admin secret이 준비됐습니다. 값은 출력·문서화·커밋하지 않습니다.
- 승인된 v346 SHA `81d1c4faa59194e8928d54fbecac28694ab139ab`로 서비스 1개 생성, env 14개 주입, exact image 최초 deploy를 한 번 실행했습니다. 재사용·자동 retry·두 번째 deploy는 금지합니다.
- 공개 주소는 `https://upgrade-rpg-api.onrender.com`이며 `/api/v1/health`와 `/api/v1/health/db`가 각각 HTTP 200 `status=ok`를 반환했습니다.
- 첫 공개 frontend는 실제 legacy 화면을 Render Free Static Site `gihohoho-upgrade-rpg`로 배포하는 계획입니다. 예상 주소는 `/index.html`, `/admin.html`이며 Vue shell은 이번 배포 대상이 아닙니다.
- `tools/build_legacy_static_site.mjs`는 `index.html`, `admin.html`, `src/**/*.js`, `src/**/*.css`, `src/assets/**/*.png`만 `frontend/legacy-dist`에 묶고 secret·DB endpoint 형태가 있으면 실패합니다.
- `src/api/runtime-config.js`는 로컬 host에서는 기존 local API를 유지하고 그 밖의 host에서만 `https://upgrade-rpg-api.onrender.com/api/v1`을 사용합니다.
- frontend Static Site 최초 배포와 backend CORS recovery deploy는 완료됐습니다. recovery 1회 승인은 소비됐고 추가 provider deploy는 새 승인 전 실행하지 않습니다.
- 공개 `admin.html`에는 admin write key를 넣지 않으며 read-only public preview로만 취급합니다.
- 현재 필요한 extension·권한·설치는 없습니다.
- Windows PostgreSQL 16/OpenSSL의 `sslrootcert=system` 오류는 Windows 시스템 공개 CA를 Git 제외 로컬 PEM으로 내보내 `verify-full`에 전달하는 방식으로 해결했고, asyncpg와 libpq read-only preflight가 모두 통과했습니다.
- 승인된 v343 commit `d6df9984e00d08b28fd524dcfefeb492e334d5e9`로 Neon restore를 한 번 실행했고 22 application tables / 748 rows / schema digest가 일치했습니다. legacy data digest는 session timezone 차이로 실패해 stamp 전에 안전하게 중단했습니다.
- v343 안전 중단 시점에 aware datetime을 UTC로 정규화한 digest `4ea23cfd2446b522cc9e85e2a8520160427cf8e3987d9b6ab04f4b99fbf6c00c`가 verified rehearsal과 Neon에서 일치했고, 당시 `alembic_version`은 없었습니다.
- 승인된 v344 commit `cf0f506b6ae9dc9d4c02f3ab5313ca68be32676c`로 복원 상태를 재검증하고 exact v295 stamp만 실행했습니다. application digest는 불변이며 최종 23/749 검증을 통과했습니다.
- 복원·stamp·Render 최초 deploy 재실행은 금지합니다. 당시 다음 단계였던 live backend·frontend·CORS 검토는 v347~v355에서 완료됐습니다.
- 이번 image 게시 approval은 모두 소비됐으며 Neon restore/stamp나 Render 생성·배포 권한으로 재사용하지 않습니다.
- v343 Neon 초기화 approval도 restore 시도와 안전 중단으로 소비됐으며 stamp 권한으로 재사용하지 않습니다.
- v344 stamp recovery approval도 성공 실행으로 소비됐으며 Render 생성·배포 권한으로 재사용하지 않습니다.

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
node tools/smoke/game/smoke_equipment_progression_formulas.js
python tools/check_v351_public_release_gates.py --strict
python tools/smoke/backend/smoke_v351_public_release_gates.py
python tools/check_runtime_blocking_io.py --strict
python tools/smoke/backend/smoke_master_data_latency_guard.py
node tools/smoke/game/smoke_master_data_auto_boot_policy.js
python tools/check_frontend_static_deployment_plan.py --strict
node tools/smoke/frontend/smoke_legacy_static_deployment_preparation.js
python tools/check_render_neon_separated_plan.py --strict
python tools/smoke/backend/smoke_neon_production_database_bootstrap.py
python tools/check_neon_readonly_connectivity.py --evidence
python tools/check_production_provider_selection.py --strict
python tools/check_production_deployment_plan.py --strict
python tools/check_github_actions_ghcr_static_plan.py --strict
python tools/check_codex_handoff_readiness.py --strict
```

변경 영역 전용 checker/smoke부터 1회 실행하고 실패할 때만 확대합니다. 문서·handoff·상태값만 바꾸면 전체 core smoke를 반복하지 않습니다. 핵심 로직·DB/Alembic·API 계약·공통 구조·여러 영역을 함께 바꾸거나 실제 배포 후보 직전에는 `bash tools/run_smoke_core.sh`를 1회 실행합니다. Python 변경은 해당 compileall, JavaScript 변경은 문법 검사를 수행합니다. Vue 변경 시에만 `npm ci`, `npm run build`를 실행합니다.

완료 답변에는 한 일, 검증, 서버 재시작 여부, commit/push, 다음 단계, 필요한 extension/권한/설치를 포함합니다.
