# Current Status — v369

## 현재 결과

```txt
latest: v369.starter-skill-book-and-weapon-master-skill-icons-applied
strict result: starter-skill-book-and-weapon-master-skill-icons-applied
next safe stage: owner-review-v369-local-icons-and-select-next-character-step
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

v369에서 초보자 무기와 스킬강화권, 현재 검신 스킬까지 로컬 아이콘 범위를 넓혔습니다. 다음 단계는 로컬 `http://127.0.0.1:5500/index.html`에서 v369의 21개 아이콘을 기호가 확인한 뒤, 다음 캐릭터의 스킬 이미지 또는 별도 static release 범위를 선택하는 것입니다. 기존 Render Static Site의 v351 공개본은 그대로 유지합니다.

## 초보자 무기·스킬강화권·검신 스킬 아이콘 — v369

- 초보자 무기 `리버레이션 스태프` 1장, 스킬강화권 10장, 검신(`weapon_master`) 스킬 10장을 각각 별도 256×256 PNG와 `?v=369` 캐시로 적용했습니다.
- 스킬강화권은 `Q → W → E → R → T → F → D → SQ → SW → M` 순서의 한 계열입니다. Q 기본형부터 바로 전 단계를 직접 편집해 같은 책의 실루엣·구도와 중심 문양을 유지하면서 재질·룬·오라만 절제되게 발전시킵니다.
- 검신 기본 스킬 중 `Q`·`W`·`R`·`T`·`F`·`D`는 초록색 자동·패시브, `E`는 파란색 버프입니다. `SQ`·`SW`·`M`은 기능 유형과 관계없이 보라색 강화·진각성 계열입니다. 현재 검신에는 사용자가 직접 누르는 기본 액티브 스킬이 없습니다.
- 스킬 아이콘은 사용자가 제시한 예시처럼 어두운 배경, 굵고 단순한 단일 문양·동작 실루엣과 작은 슬롯 판독성을 기준으로 합니다. 파일 안에는 `Q`·`W` 같은 키 문자, 숫자, 이름과 설명을 넣지 않고 UI에서 따로 표시합니다.
- 추후 추가할 캐릭터는 같은 슬롯 키라도 검신 이미지를 공유하지 않고 캐릭터별 전용 폴더와 별도 PNG를 사용합니다. 장비·강화권·스킬 이미지 내부 프레임과 UI의 등급별 CSS 테두리도 계속 분리합니다.
- 프로젝트 파일은 `src/assets/equipment/liberation-staff.png`, `src/assets/skill-books/`의 10장, `src/assets/skills/weapon-master/`의 10장입니다. built-in `image_gen` 작업 원본은 Git 밖 `C:\Users\HOME\.codex\generated_images\019f64cb-07a2-7bb3-81e9-e66fdced3b76`에 보존합니다.
- 장비 능력치·강화 공식, 스킬 수치·발동 확률·전투 로직, backend API/image, Neon DB와 Render 서비스는 변경하지 않았습니다. 공개 Static Site는 계속 v351입니다.
- 정적 generated seed 4개(`skills`, `item_templates`, `drop_table_items`, `manifest`)는 현재 로컬 이미지 URL로 재추출했습니다. 실제 DB write·seed 실행·migration은 하지 않았습니다.
- 전체 파일·색 분류·발전 규칙은 `docs/current/STARTER_SKILL_BOOK_AND_SKILL_AI_ICON_ASSETS.md`에 기록했습니다. v369 전용/관련 smoke와 core smoke가 통과했고, 실제 Chrome 게임 화면의 기본 스킬 8개와 별도 21개 검수 화면이 256→68px 정사각형으로 로드됐으며 브라우저 오류는 0건입니다.

## v363 단순 결정 시안 후손 43장 전체 교체 — v368

- 기준 commit `a696e1be3fe27beddc545cbba01e1e438573b7cc`에서 추가된 단순 파랑·금색 결정 원본 15개와, v365에서 티어별로 파생된 현재 파일을 Git 이력으로 다시 추적했습니다.
- 현재 10~20단계에 남은 후손은 총 55장이었습니다. v364에서 반지 `skill_all` 6장, v367에서 4원소 크리스탈 `atk_inc` 6장을 이미 교체했고, 이번에는 나머지 **13계열 43장**을 모두 새로 생성·적용했습니다.
- 10·11·12·18·19·20단계 3계열: `군신의 가호가 담긴 보석`은 전쟁신 루비 메달, `루나 베네딕티오`는 초승달 진주 부적, `영창 : 불멸의 혼`은 영혼 불꽃 흑마도서로 교체했습니다.
- 13·14·15단계 5계열: `마음을 새긴 바다`는 조개 펜던트, `종말의 시간`은 금 간 회중시계, `광란을 품은 자`는 갑주 악마 심장, `세계수의 뿌리`는 살아 있는 나무뿌리, `어나이얼레이터`는 흑적 마력포로 교체했습니다.
- 16·17단계 5계열: 넥스의 몽환의 어둠은 꿈의 눈 부적, 검은 기운은 봉인된 암흑 소용돌이 장치, 잠식된 의복은 타락한 망토, 원초의 꿈 스태프·창은 각각 초승달 지팡이와 넓은 창날 무기로 교체했습니다.
- 같은 계열의 다음 단계는 바로 전 단계 PNG를 편집 원본으로 사용해 물체 정체성·실루엣·각도·크롭을 유지하고 재질·룬·오라만 발전시켰습니다. 43장은 모두 별도 256×256 PNG이며 SHA-256 중복은 0건입니다.
- `tools/smoke/game/smoke_equipment_icon_families.js`에 43장 전체 SHA-256을 fail-closed로 고정했습니다. 기존 반지/4원소 교체와 합쳐 v363 시안에서 파생되어 현재 사용되는 단순 결정 PNG는 0개입니다.
- 일반 장비 URL과 `icon-utils.js` 로드 캐시는 `?v=368`입니다. 검토용 43장 모음판은 Git 제외 `local-review-artifacts/v368-v363-descendants-43-icons.png`에 보존했습니다.
- 장비 전용 smoke와 legacy static 배포 smoke가 통과했습니다. 로컬 Chrome에서 `icon-utils.js?v=368`, 일반 장비 URL `?v=368`, 원본 256×256 → 화면 61×61 정사각형 렌더링, 콘솔 오류 0건을 확인했습니다. 공개 Render Static Site는 계속 v351이며 이번 v368은 배포하지 않았습니다.

## 4원소 크리스탈 6단계·계열 테두리 동기화 — v367

- v367 당시에는 10·11·12·18·19·20단계 `올 엘리멘탈 크리스탈` 6장만 사용자가 확인한 불·물·바람·빛 사분할 보석 발전형으로 교체했습니다. 같은 v363 묶음의 나머지 단순 결정 후손 43장은 v368에서 추가로 전부 교체했습니다.
- 여섯 이미지는 같은 사분할 실루엣, 원소 위치, 발톱 위치, 카메라 각도와 크롭을 유지하고 청은색 룬 → 초월 마력선 → 흑보라 연옥 금속 → 금색 최종 장식 순으로 발전합니다.
- 이름 키워드만으로 CSS 등급을 추측하던 누락을 보완했습니다. 일반 장비는 확인된 계열 단계표를 먼저 사용합니다.
- 21·22·23단계와 24·25·26단계는 각각 `basic → rare → transcendent`입니다. 따라서 `끝없는` T23과 `영원한` T26도 초월 테두리입니다.
- 30·31·35·36단계는 같은 기본형 계열이며 `basic → rare → transcendent → liberated`입니다. 따라서 T35는 초월, T36은 해방 테두리입니다.
- 이름 기반 기존 판정은 다른 장비의 fallback으로 유지하고, 위 확정 계열만 tier 기반 단계표로 먼저 판정합니다.
- 일반 장비 이미지와 `icon-utils.js` 캐시 식별자를 모두 `?v=367`로 갱신했습니다.
- focused smoke는 1~39단계 195개 URL·PNG 규격, 4원소 6개 SHA-256과 상이성, T21~23·T24~26·T30/31/35/36의 등급 순서를 fail-closed로 고정합니다.
- 로컬 브라우저 DOM에서 `?v=367` 로딩과 T23 `item-frame-transcendent`를 확인했고, 기본형과 최종형 PNG를 직접 확대 확인했습니다.
- 변경 없음: 장비 능력치·강화 공식·드롭률, field 규칙, backend API/image, Neon DB, Render 서비스와 공개 v351 Static Site.

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

- 이전의 “같은 계열은 PNG 하나를 공유하고 CSS 테두리만 변경” 규칙을 폐기했습니다. 최종 목표는 일반 장비 195개에 각각 별도 PNG 195개입니다.
- 같은 계열은 기본 물체의 정체성, 실루엣, 카메라 각도, 크롭과 주요 부품을 유지하고 단계마다 재질·중심색·기존 장식·룬·마력 효과를 점진적으로 발전시킵니다.
- 승급 표식을 제거한 이름이 같으면 같은 계열이며, 더 긴 상위 이름 안에 기본 이름 전체가 포함돼도 같은 계열입니다. 기호가 고친 21·22·23단계와 24·25·26단계 통합 분류를 보존했습니다.
- `어둠을 지배하는 고리`의 기본 → 진 → 초월 → 연옥 → 진 연옥 → 초월 연옥 6개를 굵은 외곽선과 만화식 명암의 새 화풍으로 다시 생성했습니다. 기본 형상은 유지하면서 은색·청색 룬 → 보라·청록 에너지 → 검붉은 연옥 → 금색·청록 최종 장식으로 발전합니다.
- 새 반지 6개 모두 `src/assets/equipment/`의 서로 다른 256×256 PNG이며 일반 장비 캐시 식별자는 `?v=364`입니다. 기존 14계열 기본 이미지는 다음 묶음에서 단계별로 교체할 때까지 안전한 fallback으로 유지합니다.
- 실제 Chrome `http://127.0.0.1:5500/index.html`에서 10·11·12·18단계 반지를 지급했습니다. 가방에서 서로 다른 이미지가 정사각형 슬롯을 채우고 기본·진·초월·연옥 CSS 테두리가 함께 적용됐으며, DOM에서도 `dark-dominion-ring[-단계].png?v=364`와 `item-frame-radiant`를 확인했습니다.
- 집중 검사: 10~20단계 로컬 이미지 55/55, 반지 단계 이미지 6/6 고유, 전체 에셋 20개 PNG signature·256×256, 정적 배포 산출물 포함 통과.
- 변경 없음: 장비 스펙·강화 공식·드롭률, 필드 규칙, backend API/image, Neon DB, Render 서비스.

## 일반 장비 이미지 계열 분류와 10~20단계 첫 묶음 — v363

> 아래는 v363 당시 기록입니다. 이미지 공유·115개 목표·`?v=363` 규칙은 v364에서 폐기됐으며 현재 판단에는 사용하지 않습니다.

- 1~39단계 일반 장비 195개를 전수 추출했습니다. 승인된 승급 표식만 제거해 같은 이름을 묶으면 고유 이미지 115개가 필요합니다.
- `-현-`, `-진-`, `-초월-`, `★심연★`, `★연옥★`, `★진 연옥★`, `★초월 연옥★`만 계열 표식으로 제거합니다. `끝없는 절망`, `영원한 파멸`처럼 실제 이름이 바뀌는 경우는 별도 계열입니다.
- v363 첫 묶음은 10~20단계 일반 장비 55개를 대상으로 했습니다. 10계열 5개, 13계열 5개, 16계열 5개로 고유 PNG 15개를 만들었습니다.
- built-in `image_gen`을 사용했으며 새 API 키·extension·dependency 설치는 없습니다. 최종 파일은 `src/assets/equipment/`의 동일한 256×256 PNG입니다.
- 아이콘은 단일 물체, 굵은 실루엣, 2~3개 중심 색, 절제된 명암과 짙은 남색 full-bleed 배경을 사용합니다. 글자·숫자·로고·내장 테두리·입자·날개·과도한 광채와 복잡한 세공은 넣지 않았습니다.
- `마음을 새긴 바다`·`-진- 마음을 새긴 바다`·`★심연★ 마음을 새긴 바다`는 같은 조개 펜던트 PNG를 공유하고, 기본 흰색 → 진 파란색 → 심연 보라색 CSS 프레임으로 승급을 나타냅니다.
- `어둠을 지배하는 고리` 계열은 10·11·12·18·19·20단계가 같은 PNG를 공유하며 기본 → 진 → 초월 → 연옥 → 진 연옥 → 초월 연옥 순서로 CSS 프레임이 강화됩니다.
- 보스 드롭 원본, 신규 획득 준비 단계와 기존 저장 데이터의 가방·보관함·휴지통·장착칸·우편을 같은 이미지 정규화 경로로 갱신합니다.
- 브라우저 캐시 식별자는 일반 장비 이미지와 관련 JavaScript 모두 `?v=363`입니다. 특수장비 PNG는 변경하지 않아 `?v=361`을 유지합니다.
- 전체 분류, 공통 프롬프트와 파일 매핑: `docs/current/NORMAL_EQUIPMENT_AI_ICON_ASSETS.md`
- 집중 검사: 55개 대상의 로컬 이미지 55/55, 고유 이미지 15개, 공유 계열/등급 순서, PNG signature·256×256, 정적 배포 포함 여부 통과.
- 실제 Chrome에서 13·14·15단계 `마음을 새긴 바다`가 동일한 `engraved-sea-heart.png?v=363`을 사용하고 CSS 등급만 `basic / rare / dark`로 바뀌는 것을 확인했습니다. 원본은 256×256, 지급 목록 렌더링은 40×40이며 브라우저 오류는 0건입니다.
- 변경 없음: 장비 스펙·강화 공식·드롭률, 필드 규칙, backend API/image, Neon DB, Render 서비스.

## 등급 테두리·위치 유지 인벤토리·수동 위로 정렬 — v362

- v361의 23개 256×256 이미지 파일은 다시 생성하거나 수정하지 않았습니다. 파일 내부의 full-bleed 그림은 유지하고, 게임 UI에서 CSS 등급 프레임을 별도로 적용합니다.
- 이름 기준 등급은 기본 → 강력 → 빛나는 → 초월 → 해방 → 찬란 → 짙은 → 영롱 순으로 판별합니다. 기본은 장식·광채·애니메이션 없는 흰색 테두리이며 상위 단계에서 색, 이중선, 광채와 절제된 애니메이션이 점진적으로 강화됩니다.
- 등급 프레임은 장착칸, 가방, 보관함, 휴지통, 아이템 관리창과 테스트 지급 미리보기에서 같은 `getItemFrameGrade()`·`applyItemFrameClass()`를 사용합니다. 높은 단계 애니메이션은 `prefers-reduced-motion`에서 꺼집니다.
- 가방·보관함·휴지통은 아이템 이동·사용·장착·휴지통 이동 후 중간 항목을 자동으로 당기지 않습니다. 원래 위치는 빈 칸으로 남고 새 아이템은 가장 앞의 빈 칸을 사용합니다.
- 세 패널 헤더에 `↑ 위로 정렬` 버튼을 추가했습니다. 버튼을 눌렀을 때만 기존 아이템의 상대 순서를 유지하면서 빈 칸을 제거합니다.
- 실제 Chrome에서 가방 5번째 아이템을 보관함과 휴지통으로 각각 이동했을 때 5번째 칸은 비고 6번째 아이템은 그대로 유지됐습니다. `가방으로`·`가방으로 복구`를 누르면 첫 빈 칸인 원래 5번째 칸으로 돌아왔고 원래 25/60·보관함 0·휴지통 0 상태로 복구했습니다.
- 실제 렌더링에서 기본 흰색, 초월 청록, 해방 금색, 찬란 분홍·청록, 짙은 보라, 영롱 다색 테두리와 관리창·장착칸 공통 적용을 확인했습니다.
- CSS와 변경 JavaScript 로드 키는 `?v=362`이며, 다시 만들지 않은 PNG 원본의 이미지 URL은 `?v=361`을 유지합니다.
- 상시 규칙은 `AGENTS.md`에 기록했습니다. 이미지 파일 자체에는 카드형 프레임을 넣지 않되 게임 UI의 등급별 CSS 테두리는 항상 유지합니다.
- 변경 없음: 23개 PNG 원본, 장비 스펙·밸런스, 필드 규칙, Neon DB, backend API/image, Render 서비스.

## 테두리 없는 정사각형 full-bleed 특수장비 아이콘 — v361

- v360 아이콘의 정사각형 파일 안에 세로 카드 프레임·inset panel·빈 여백이 다시 들어가 실제 가방 슬롯에서 크기와 정렬이 어긋나 보이는 문제를 재현했습니다.
- built-in `image_gen` 편집으로 23개를 모두 독립적인 1:1 아이콘으로 다시 만들었습니다. 최종 파일은 같은 256×256 PNG이며 테두리·프레임·카드판·rounded rectangle·margin band가 없습니다.
- 고정 판정 문구는 `테두리 없음·여백 없이 정사각형을 채움`입니다.
- 아이템과 마력 효과는 정사각형의 약 90~100%를 차지합니다. 반지·목걸이·무기·갑옷·문양의 종류가 즉시 보이면 체인, 손잡이, 어깨, 광채 일부가 가장자리에서 잘리는 close-up을 허용합니다.
- 특수무기·목걸이·반지는 기본 → 초월 → 해방 → 짙은, 아바타 3종은 기본 → 찬란한, 탈리스만은 기본 → 초월 → 찬란한 → 영롱한 순서로 기본 실루엣·구도·정렬을 유지하고 색·장식·룬·마력 효과만 발전시켰습니다.
- 고전 한국식 횡스크롤 액션 RPG·던전앤파이터풍의 작은 인벤토리 아이콘을 상시 기준으로 삼는 규칙을 `AGENTS.md`에 추가했습니다.
- 브라우저가 같은 파일명의 v360 이미지를 재사용하지 않도록 `getSpecialEquipIconUrl()` 결과와 `icon-utils.js` 로드 키를 `?v=361`로 갱신했습니다.
- 생성·검수 규칙과 계열별 프롬프트: `docs/current/SPECIAL_EQUIPMENT_AI_ICON_ASSETS.md`
- 변경 없음: 장비 스펙·밸런스, 필드 1배·50% 규칙, Neon DB, backend API/image, Render 서비스.

## 필드 1배·50% 규칙과 AI 특수장비 아이콘 — v360

- 필드 순수공격력 성공 보상에서 `gain *= 0.5`를 제거해 각 필드에 표시된 상승량을 100% 지급합니다.
- 순수공격력 보상이 있는 8~40단계 33개 필드의 최종 성공 확률은 모두 50%입니다. 1~7단계는 원래 순수공격력 보상이 없습니다.
- 정적 source와 generated field seed 모두 `prob=0.5`이며, 기존 backend master-data가 과거 `prob=1`을 보내도 공통 `getFieldFarmRewardProbability()`가 런타임을 50%로 고정합니다.
- 필드존 선택 패널에 `처치 시 50% / 성공 시 표시 상승량 100% / 실패 시 상승 없음` 고정 안내를 추가하고 각 필드 툴팁도 확률·성공·실패·최대 누적을 분리 표시합니다.
- 변경 연관 항목을 빠짐없이 맞추도록 제목·설명·툴팁·모달·버튼·로그·캐시·source/seed·검사·문서를 함께 검색하고 동기화하는 상시 규칙을 `AGENTS.md`에 추가했습니다.
- built-in `image_gen`으로 특수무기·목걸이·반지 4단계, 아바타 3종 2단계, 탈리스만 4단계, 휘장 단일 아이콘을 생성했습니다.
- 최종 에셋은 23개 256×256 PNG이며 `src/assets/special-equipment/`에 저장했습니다.
- 특수장비 38개가 이름/슬롯 판별을 통해 23개 파일을 공유합니다. 기존 저장 데이터 placeholder와 보스/테스트 지급 화면도 새 아이콘으로 정규화됩니다.
- 캐시 키는 관련 CSS/JavaScript 모두 `?v=360`입니다.
- generated field/item/drop seed는 동기화했지만 local/Neon DB write, backend image/API, Render 서비스는 변경하지 않았습니다.
- 이미지 생성 프롬프트와 매핑: `docs/current/SPECIAL_EQUIPMENT_AI_ICON_ASSETS.md`
- 검증: JavaScript 문법, focused runtime/seed smoke, 23개 PNG signature·256×256·이름 매핑, local Chrome static mode 필드 설명과 특수보스 6단계 아이콘 확인 통과.

## 아바타 분류·강화 초기화 인터페이스·필드 전수 감사 — v359

- 아바타 특수장비 툴팁과 관리창의 분류를 각각 `[무기 아바타]`, `[오라 아바타]`, `[클론 레어 아바타]`로 표시하고 파란색 계열 `#6eb4ff`로 통일했습니다.
- 강화된 탈리스만/휘장 초기화는 원본 +0 재료 수량을 `2^강화단계`로 복원합니다. +1/+2/+3/+4/+5/+6은 각각 2/4/8/16/32/64개입니다.
- 브라우저 기본 `confirm`을 제거하고 선택 장비, `강화품 1개 → +0 반환 개수`, 되돌릴 수 없다는 경고를 보여주는 게임 내부 모달로 교체했습니다.
- 초기화 확인 사이 선택 장비나 강화 단계가 달라지면 실행을 취소하는 재검증을 추가했습니다.
- 탈리스만/휘장 관리창에서는 쓸 수 없는 20/50/200회 강화 버튼을 숨기고 장착, 1회 강화·초기화, 보관함, 휴지통 순서로 재배치했습니다. 좁은 화면에서는 한 열로 접힙니다.
- 앞으로 사용자에게 보이는 버튼·기능은 시각 위계, 간격, 문구, 반응형, 확인·취소 흐름을 함께 완성하고 브라우저에서 확인한다는 상시 규칙을 `AGENTS.md`에 추가했습니다.
- v359 당시 필드 데이터 40개와 공통 `0.5` 지급 배율을 확인했지만, 이 절반 지급 규칙은 v360에서 표시 상승량 100%·성공 확률 50%로 대체됐습니다.
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
- v358 당시 필드 순수공격력을 기존 최종 정수 지급량의 절반으로 바꿨지만, 이 규칙은 v360에서 표시 상승량 100%·성공 확률 50%로 대체됐습니다.
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

- 실제 배포 대상: legacy `index.html`, `admin.html`, `src/**/*.js`, `src/**/*.css`, `src/assets/**/*.png`
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
