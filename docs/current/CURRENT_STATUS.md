# Current Status — v359

## 현재 결과

```txt
latest: v359.avatar-category-reset-refund-interface-polished-field-gain-halving-audited-static-deploy-gate-preparation-required
strict result: avatar-category-reset-refund-interface-polished-field-gain-halving-audited-static-deploy-gate-preparation-required
next safe stage: prepare-v359-static-content-deploy-exact-sha-gate
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
production deployment approval ready/approved/executed: no/no/no
Render public preview deployment ready/approved/executed: yes/yes/yes
```

## Render/Neon 분리 계획 체크포인트 — 2026-07-26

- 두 계획과 fail-closed 계약 검토 완료
- v341 source에 runtime/Alembic 공용 system-CA hostname-verifying SSLContext 적용 완료
- `deploy/render.production.env.example`에 Render 전용 non-secret/secret placeholder inventory 분리
- 실제 Neon direct read-only bootstrap 통과
- 새 v341 exact image 게시와 isolated Alpine CA-store/runtime 검증 완료
- Neon `neondb` 초기화 완료: 22 application tables / 748 rows + `alembic_version` 1 row
- 새 `rpg_game` DB를 만들지 않고 기존 빈 `neondb` 사용
- verified local dump: 22 application tables / 748 rows / no Alembic
- Neon 이식: direct verify-full restore → digest 검증 → exact v295 stamp → 23/749 검증
- Render: Singapore / Free / 1 instance / port 8000 / health `/api/v1/health`
- platform health에는 DB를 포함하지 않고 `/api/v1/health/db`는 수동 확인
- 서비스 이름 `upgrade-rpg-api`는 owner 확인 완료
- production DB mutation: restore 1회 + exact v295 stamp 1회 완료 / Render mutation 없음
- v345 read-only completion guard와 focused smoke 준비 완료
- asyncpg system-CA와 PostgreSQL 16/libpq exported-Windows-system-CA `verify-full` read-only preflight 통과
- 최종 public tables/total rows: 23/749 / current revision: v295_initial_schema
- application UTC-canonical schema/data digest 불변 / Render service mutation 없음

## 로컬 리뷰 도구 체크포인트 — 2026-07-26

- Code Review Graph 2.3.7을 사용자 전용 독립 환경에 CLI-only로 설치하고 로컬 그래프를 생성했습니다.
- 현재 그래프 상태: 385 files / 4,242 nodes / 35,407 edges
- `.code-review-graph/`는 Git 제외이며 backend `.venv`와 프로젝트 dependency는 변경하지 않았습니다.
- MCP, Codex hooks/instructions, watch/daemon, Git hook, cloud embedding은 구성하지 않았습니다.
- Ponytail 플러그인은 설치하지 않고 최소 구현 원칙만 `AGENTS.md`에 반영했습니다.
- 이 도구는 다중 파일 리뷰의 보조 evidence이며 위험도 출력만으로 결함을 판정하지 않습니다.

## 비용 최소 공급자 선택

- runtime: Render Free Web Service, Singapore, 512 MB/0.1 CPU, 단일 instance
- database: Neon Free PostgreSQL 16, AWS Singapore (`aws-ap-southeast-1`)
- public HTTPS: Render가 발급하는 `onrender.com` 주소와 managed TLS
- deployment: private GHCR의 exact digest를 사용하는 manual image-backed service
- fixed monthly cost: $0
- payment method: Render에 처음에는 등록하지 않음
- classification: SLA production이 아닌 개인용 public preview

Render 무료 app은 15분 유휴 뒤 잠들고 첫 요청에서 약 1분의 cold start가 생길 수 있습니다. Neon Free는 프로젝트당 월 100 CU-hours, 0.5 GB storage, 6시간 restore history 범위입니다. 상세 근거와 비교는 `PRODUCTION_PROVIDER_SELECTION.md`, 정적 계약은 `deploy/production-provider-selection.example.json`에 있습니다.

## Neon onboarding checkpoint — 2026-07-22

- Neon Free PostgreSQL 16 AWS Singapore 프로젝트 생성 완료
- Neon Auth 비활성 선택
- 채팅에 노출된 최초 `neondb_owner` 비밀번호 재설정·폐기 완료
- 새 direct/pooled URL은 채팅·Git·앱·배포 플랫폼에 주입하지 않고 로컬 제외 파일에만 저장
- Git/Docker 제외 로컬 입력 파일: `deploy/.env.production`
- Direct/Pooler 모두 PostgreSQL 16.14, TLS 1.3 인증서·호스트 검증, read-only transaction 통과
- sanitized evidence: `deploy/review/neon-readonly-connectivity-v336.json`

## 아직 남은 것

- 기존 Static Site와 exact source를 고정하는 v358 static-only fail-closed 계약/checker 준비
- gate 준비 commit의 exact SHA 승인 시 기존 Render Static Site 수동 deploy 1회
- 공개 게임에서 12단계 `607%`, 16단계 `2121%`와 13+ 증가 공식 read-only 확인
- 다음 콘텐츠·밸런스 변경은 기호가 별도로 요청한 범위에서 진행
- custom domain/DNS와 SLA production 전환은 보류

Neon DB/schema/data 초기화, Render backend public preview, frontend Static Site v351 배포와 CORS/no-fallback 검증은 완료됐습니다. v334 generic SLA production plan의 별도 host·domain·edge·rollback 입력은 계속 `unresolved`입니다.

## Render account checkpoint — 2026-07-22

- workspace: `Hobby (legacy)`
- payment method: `No card on file`
- existing service: total 1 / active 0 / owner-suspended 1
- target source: Web Service → Existing Image
- GitHub Container Registry 지원 확인
- registry credential: `upgrade-rpg-ghcr-read` 생성 완료
- dedicated classic PAT: `read:packages` only, 만료일 2027-07-23, 실제 값 미기록
- exact-digest `Connect`: 성공, 서비스 설정 화면 진입 확인
- Web Service/payment/deploy mutation: 없음
- sanitized evidence: `deploy/review/render-account-readiness-v337.json`
- credential/Connect evidence: `deploy/review/render-private-ghcr-connect-v338.json`

## Render private GHCR checkpoint — 2026-07-23

- Render credential action approval: ready/approved/executed = yes/yes/yes
- GitHub `Confirm access`: 사용자 완료
- 첫 PAT: 브라우저 검사 출력 노출을 감지해 Render에 저장하지 않고 즉시 GitHub에서 폐기
- 교체 PAT: `read:packages` 외 scope 없음, 2027-07-23 만료, Render에 값 출력 없이 저장
- exact reference `Connect`: 성공
- Web Service/env/payment/deploy: 생성·주입·변경·실행하지 않음

## 검증된 배포 후보

- exact reference: `ghcr.io/gihohoho/upgrade-rpg-backend@sha256:f3bf6eed45e46e9d2022df4ab62eb6ca55b1ec0997b8ed342ae250c4a60052c1`
- GitHub Actions run `30180738530`: SBOM, Trivy HIGH/CRITICAL 0, provenance, Cosign sign/verify 성공
- current live isolated evidence: `deploy/review/isolated-image-pull-validation-v342.json`
- new v351 candidate isolated evidence: `deploy/review/isolated-image-pull-validation-v353.json`
- source-controlled lifecycle gate: `deploy/github-actions-ghcr-publish-lifecycle.json`
- historical v341 lifecycle: `attempt-recorded`, `publishReviewerGateReady=false`; current history의 여섯 번째 성공 기록으로 보존
- CI credential: GitHub Actions `GITHUB_TOKEN`
- 개인 비공개 저장소 required reviewer는 없으므로 exact-SHA owner approval을 유지

## v351 image 게시·isolated 완료와 provider release 준비 — v353/v354

- source baseline: `81beaa0864c3422fb9fc2071b9c4965936ecafac`
- lifecycle: `attempt-recorded` / gate `false` / approved preparation `b48dfd0751b12b1b3afb6474f9d35359ba2f8177`
- workflow run: `30226905547` / run_attempt=1 / success / rerun 금지
- exact image: `ghcr.io/gihohoho/upgrade-rpg-backend@sha256:143be5eb21ec8c9318c7d0c4f3fbd5ac2de32439977a1d660c7247b6d3a507ac`
- supply chain: local/registry Trivy HIGH·CRITICAL 0, SLSA provenance, SPDX-2.3, Cosign verify 통과
- isolated: linux/amd64, UID 65532, CA 119, read-only rootfs, health 200, cleanup 통과
- GitHub live settings: selected actions/full SHA/read permissions/main-only environment 유지
- workflow dispatch/registry mutation/Render deploy: 1회/실행/미실행
- provider preparation: backend exact-image + frontend v351 exact-source, 둘 다 미승인·미실행
- 다음 승인 범위: 기존 Render backend/static 서비스 각각 수동 deploy 1회와 read-only 검증
- contract/checker: `deploy/v351-public-release-gates.example.json` / `tools/check_v351_public_release_gates.py`

## 안전 경계

- backend replicas/workers 1/1, PostgreSQL TLS `verify-full`, automatic deploy/migration 금지
- actual secret/token/PAT/password/CA/cert/key를 Git·채팅·로그·artifact에 기록하지 않음
- DB create/delete/restore/reset/seed/write와 Alembic mutation은 별도 구체적 요청·승인 전 금지
- 인증/API write, Vue Preview/Apply/write, 게임 콘텐츠·밸런스 변경 금지
- resource 생성과 실제 deploy 전 실행 준비 commit의 정확한 40자리 SHA 승인 필요

## 장비 스킬 피해 공식 변경과 전체 감사 — v357

- 12-1 `-초월- 어둠을 지배하는 고리 +20`
  - 공격력: `69.1B` 유지
  - 스킬 피해: `488.6%` → `607.0%`
  - 모든 피해: 내부 `173.9%` 유지, 현재 UI 세 자리 유효숫자 표시는 `174%`
- 16단계 `무의식 : 넥스의 몽환의 어둠 +20`
  - 공격력: `369B` 유지
  - 스킬 피해: `800.8%` → `2121.0%`
  - 모든 피해: 내부 `225.8%` 유지
- +20 목표는 12단계 `607%`와 16단계 `2121%`를 단계당 `1.36721871444...`배 기하 보간·외삽
- +1~+19는 +0 기본값 `10 × 단계`와 각 단계 +20 목표 사이를 기존 `enhanceTable.sdmg` 진행률로 보간
- 13/14/15/17/18단계 +20 `829.9 / 1134.7 / 1551.3 / 2899.9 / 3964.8%`, 39단계 `2823673.9%`
- 17단계 이후 실제 스킬 피해 실측값은 저장소에 없어 새 기준을 받기 전까지 위 기하비율을 추정 외삽
- 17단계 스태프 추가 스킬 계수 `2097179%`, 창 치명 피해 `803447%`, 18단계 보석 공격력 `851B`·평타 피해 `7506%`는 정확히 유지
- 1~12단계 일반 장비 60종과 탈리스만 5종, 단계별 5개 일반 장비 그룹의 +0/+20 결과 감사 완료
- 0~20 강화 단조 증가, 16단계 +0~+20 명시값과 12~39단계 새 공식 검증 완료
- 1~39단계 source/template/drop seed 기본 스킬·모든 피해 3중 일치
- 변경하지 않음: 1~11단계, 공격력, 모든 피해, 나머지 4그룹, generated seed, Neon DB, backend image/API
- 전체 장비 단일 공식은 없지만 누락은 없음: 1~11 고정값과 옵션별 구간·예외 공식, 12+ 생성·보간 공식 사용
- 별도 감사 결과 추가 스킬 계수의 기존 2차 외삽은 22단계부터 감소하고 33단계부터 음수가 됨. 이번 스킬 피해 전용 변경에서는 건드리지 않았으며 실제 고단계 기준이 필요한 후속 항목
- 공식 문서: `docs/current/EQUIPMENT_PROGRESSION_FORMULA_AUDIT.md`
- 회귀 검사: `tools/smoke/game/smoke_equipment_progression_formulas.js`
- 실제 공개 반영: v358 static-only gate 준비와 그 준비 commit의 별도 exact-SHA 승인 전 미실행, 기존 Render Static Site 1회만 필요
- 로컬 환경: Windows 전역 `DEBUG=release`가 backend boolean 설정과 충돌하므로 core 검사 자식 프로세스에서만 unset하고 시스템 값은 변경하지 않음

## 다음 단계

v359 게임 변경과 회귀 검사는 준비 완료이며 아직 공개 Static Site에는 배포하지 않았습니다. 다음 단계에서 Codex가 static-only fail-closed 계약/checker를 준비하고 push합니다. 기호가 그 gate 준비 commit의 정확한 40자리 SHA를 별도 승인하면 기존 Static Site를 exact source로 수동 deploy 한 번 실행하고 게임 화면을 read-only로 검증합니다. backend image 게시·배포, Neon DB write, seed import는 필요하지 않습니다.

## 아바타 분류·강화 초기화 인터페이스·필드 전수 감사 — v359

- 아바타 특수장비 툴팁과 관리창의 분류를 각각 `[무기 아바타]`, `[오라 아바타]`, `[클론 레어 아바타]`로 표시하고 파란색 계열 `#6eb4ff`로 통일했습니다.
- 강화된 탈리스만/휘장 초기화는 원본 +0 재료 수량을 `2^강화단계`로 복원합니다. +1/+2/+3/+4/+5/+6은 각각 2/4/8/16/32/64개입니다.
- 브라우저 기본 `confirm`을 제거하고 선택 장비, `강화품 1개 → +0 반환 개수`, 되돌릴 수 없다는 경고를 보여주는 게임 내부 모달로 교체했습니다.
- 초기화 확인 사이 선택 장비나 강화 단계가 달라지면 실행을 취소하는 재검증을 추가했습니다.
- 탈리스만/휘장 관리창에서는 쓸 수 없는 20/50/200회 강화 버튼을 숨기고 장착, 1회 강화·초기화, 보관함, 휴지통 순서로 재배치했습니다. 좁은 화면에서는 한 열로 접힙니다.
- 앞으로 사용자에게 보이는 버튼·기능은 시각 위계, 간격, 문구, 반응형, 확인·취소 흐름을 함께 완성하고 브라우저에서 확인한다는 상시 규칙을 `AGENTS.md`에 추가했습니다.
- 필드 데이터는 정적 source 40개와 backend generated 40개가 모두 일치하며, 순수공격력 보상이 있는 8~40단계 33개가 전부 같은 공통 지급 경로의 `0.5` 배율을 통과합니다. 1~7단계는 원래 해당 보상이 없습니다.
- 로컬 Chrome 실측에서 +0 2개와 +3 1개가 초기화 뒤 +0 10개로 합쳐졌고, 경고창과 새 버튼 배치, 무기 아바타의 파란 분류 표시를 확인했습니다.
- 캐시 키는 CSS와 변경 JavaScript 모두 `?v=359`입니다.
- 변경 없음: generated seed 내용, Neon DB, backend image/API, Render 서비스.
- 검증: JavaScript 문법, focused runtime smoke, 로컬 브라우저 UI/동작 검사 통과.

## 아바타 강화·아이템 편의·필드 성장·캐시 보정 — v358

- v357 16단계 `2121%`는 disk/5500 HTTP에 있었지만 Chrome의 이전 `stat-system.js` 캐시로 구버전 수치를 표시하는 현상을 재현했습니다.
- 변경된 여섯 JavaScript 태그에 최종 `?v=358.1`을 붙여 일반 새로고침으로 최신 코드가 로드됩니다.
- 공개 Static Site는 아직 v351 exact source이며 v357/v358은 별도 exact-SHA 승인 전 미배포입니다.
- 세 기본 아바타만 +0~+20 강화 가능:
  - 공통 +20 공격력 `88.2B`
  - 무기 아바타: 평타 치명타 피해 증폭 `33.0%`
  - 오라 아바타: 추가 스킬공격 계수 증폭 `33.0%`
  - 클론 레어 아바타: 스킬 치명타 확률 `10.0%`, 피해 배율 `150.0%`
- +0~+19는 기존 심연 특수장비 진행률을 재사용하며 상세 표는 공식 감사 문서에 있습니다.
- 스킬 치명타 확률/피해가 실제 각 스킬 피해에 적용됩니다.
- 강화권은 묶음이 남아 있으면 같은 창에서 계속 사용하고, 마지막 사용 후에도 “모두 사용함” 상태로 창을 유지합니다.
- 강화된 탈리스만/휘장은 강화창의 `+0으로 분해`로 1개를 +0 한 개로 되돌립니다. 재료 환급은 없습니다.
- 필드 순수공격력은 기존 최종 정수 지급량을 절반으로 지급하며 첫 필드는 `0.5`를 지급합니다.
- 로컬 Chrome에서 무기 아바타 +0 강화창과 장착 +2 탈리스만 분해 버튼을 확인했습니다.
- 변경 없음: generated seed, Neon DB, backend image/API
- focused smoke와 JavaScript 문법 검사 통과

승인된 v346 SHA로 Render Free Web Service `upgrade-rpg-api`를 Singapore에 만들고 승인된 env 14개와 exact image를 사용해 최초 deploy를 한 번 실행했습니다. service `srv-d9iro458nd3s73acgmsg`, deploy `dep-d9iro4l8nd3s73acgnmg`는 Live이며 공개 주소는 `https://upgrade-rpg-api.onrender.com`입니다.

Render 내부 health와 공개 `/api/v1/health`, Neon read-only `/api/v1/health/db`가 모두 HTTP 200 `status=ok`입니다. DB/Alembic write, image 변경, custom domain/DNS, 결제수단, 자동 retry·두 번째 deploy는 실행하지 않았습니다. 당시 다음 단계였던 live backend 확인과 frontend 배포/CORS origin 검토는 v347~v355에서 완료했습니다.

기호가 push된 v354 provider release preparation commit `05f1af8ed1316e2cf0e0f39ac795b3ff60bccb62`를 승인했습니다. 기존 두 서비스의 deploy를 각각 정확히 한 번 실행하고 read-only 검증까지 완료했습니다. DB/Alembic/admin write/콘텐츠 변경/자동 retry는 실행하지 않았습니다.

현재 필요한 extension이나 설치는 없습니다. 서버 재시작도 필요하지 않습니다.

## v351 provider release 배포·공개 검증 완료 — v355

- backend service/image: `srv-d9iro458nd3s73acgmsg` / `ghcr.io/gihohoho/upgrade-rpg-backend@sha256:143be5eb21ec8c9318c7d0c4f3fbd5ac2de32439977a1d660c7247b6d3a507ac`
- backend deploy: `dep-d9jeuf3eo5us73ba6cgg` / image updated / Live / 40.2초 / 정확히 1회
- frontend service/source: `srv-d9iu337aqgkc73am4lh0` / `81beaa0864c3422fb9fc2071b9c4965936ecafac`
- frontend deploy: `dep-d9jev7gu01pc73favje0` / manual specific commit / Live / 19.6초 / 정확히 1회
- Static Site auto-deploy: Off
- backend health: HTTP 200, 483ms
- Neon DB health: HTTP 200, 131ms, read-only 요청 1회
- index/admin: HTTP 200 / 200
- CORS: exact `https://gihohoho-upgrade-rpg.onrender.com`
- master-data: HTTP 200, 1,346ms, decoded 559,786 bytes, gzip, `game.master_data`
- browser game: backend master-data runtime applied 로그 확인, fallback 경고 0, 오류·경고 0
- public admin: read-only, 11 domains / 729 rows, general write UI blocked, write key missing
- 콘텐츠 준비도: 공개 no-fallback + 관리자 guarded read-only 확인 완료, 당시 첫 콘텐츠 범위 선택 준비 완료; v356 첫 장비 기준과 v357 두 번째 실측 기준 반영 완료
- Render 설정 검사 출력에 포함된 backend/static deploy hook은 즉시 재발급했고 새 값은 기록하지 않음
- sanitized evidence: `deploy/review/render-v351-provider-release-v355.json`

## Frontend static/CORS recovery 결과 — v350

- 실제 배포 대상: legacy `index.html`, `admin.html`, `src/**/*.js`, `src/**/*.css`
- Render Free Static Site: `gihohoho-upgrade-rpg`, service `srv-d9iu337aqgkc73am4lh0`
- 게임/관리자 주소: `https://gihohoho-upgrade-rpg.onrender.com/index.html`, `/admin.html`
- production API: `https://upgrade-rpg-api.onrender.com/api/v1`
- local `127.0.0.1:5500`: 기존 local backend 유지
- packaging: `node tools/build_legacy_static_site.mjs` → `frontend/legacy-dist`
- public admin: secret 없는 read-only preview, admin write 미승인
- approved/deployed SHA: `b13b1775093716800d7361ee1e8f94d8112eefc1`
- static deploy: `dep-d9iu33faqgkc73am4m3g` Live, auto-deploy Off
- backend CORS recovery deploy: `dep-d9ivfmvlk1mc73fbcv40` Live, 실제 exact `CORS_ORIGINS`
- health/preflight CORS: HTTP 200/exact allow-origin
- static raw bytes: 핵심 자산 세 개 모두 approved source SHA-256과 일치
- game master-data: HTTP 200, 464,098 bytes, 약 1.98초/1.83초
- browser game integration: v350 당시 frontend 1.5초 timeout으로 JS fallback, v355에서 해결
- 관리자 browser check: 화면 렌더링, 이전 `RpgAdminFieldHelp` 오류 로그 미재현
- recovery 자동 retry·두 번째 deploy: 없음
- 당시 다음 단계: frontend timeout focused fix와 콘텐츠 준비도 재검토, v351~v355에서 완료
- 당시 콘텐츠 준비도: 미완료였으나 v355 no-fallback/admin guarded 검증으로 완료
- 현재 extension·설치: 없음
- GitHub App: `gihohoho/upgrade-rpg` 단일 저장소 접근 확인 완료
- 필요한 사용자 조치: 현재 없음

## Master-data latency focused fix와 blocking-I/O audit — v351

- browser master-data 기본 timeout: 1,500ms → 5,000ms
- backend: 1KB 이상 응답에 GZip level 5 적용
- middleware 실제 순서: CORS → GZip → route
- backend runtime: 77 files / async 99 / sync 200 / async FastAPI route 28
- 문제 탐지: sync FastAPI route 0 / async 내부 blocking-I/O 0 / unexpected async-without-await 0
- frontend runtime: 70 files / blocking browser call 0
- offline tooling 별도 분류: Python 148 files / blocking calls 371, JavaScript 94 files / sync calls 126
- master-data 11개 DB 조회: 동일 `AsyncSession`의 안전한 순차 await 유지
- sanitized evidence: `deploy/review/master-data-latency-blocking-io-audit-v351.json`
- provider deploy·DB/Alembic/admin write·콘텐츠 변경: 없음
- 당시 다음 단계: v351 backend image와 frontend static release gate 준비, v352~v355에서 완료
- 당시 콘텐츠 준비도: 미완료였으나 v355에서 실제 public no-fallback과 admin guarded 검증 완료
