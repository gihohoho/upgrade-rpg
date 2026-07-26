# Current Status — v346

## 현재 결과

```txt
latest: v346.render-service-creation-preparation-ready-exact-sha-gated
strict result: render-service-creation-preparation-ready-exact-sha-gated
next safe stage: owner-approve-render-service-creation-preparation-sha
render plan: v346.render-service-creation-preparation-ready-exact-sha-gated
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

## 아직 하지 않은 것

- Render Web Service 생성
- 계획상 `rpg_game` 데이터베이스 생성
- JWT/admin secret 생성·주입
- production CORS origin 확정
- production deploy

Neon DB/schema/data 초기화는 완료됐지만 Render resource 생성, 배포 플랫폼 secret 주입, production CORS/public URL 확정이 남아 있으므로 v334 deployment plan의 required input은 계속 `unresolved`입니다.

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
- isolated evidence: `deploy/review/isolated-image-pull-validation-v342.json`
- source-controlled lifecycle gate: `deploy/github-actions-ghcr-publish-lifecycle.json`
- lifecycle: `attempt-recorded`, `publishReviewerGateReady=false`, prior five attempts preserved
- CI credential: GitHub Actions `GITHUB_TOKEN`
- 개인 비공개 저장소 required reviewer는 없으므로 exact-SHA owner approval을 유지

## 안전 경계

- backend replicas/workers 1/1, PostgreSQL TLS `verify-full`, automatic deploy/migration 금지
- actual secret/token/PAT/password/CA/cert/key를 Git·채팅·로그·artifact에 기록하지 않음
- DB create/delete/restore/reset/seed/write와 Alembic mutation은 별도 구체적 요청·승인 전 금지
- 인증/API write, Vue Preview/Apply/write, 게임 콘텐츠·밸런스 변경 금지
- resource 생성과 실제 deploy 전 실행 준비 commit의 정확한 40자리 SHA 승인 필요

## 다음 단계

Render용 direct asyncpg `DATABASE_URL`과 서로 다른 강한 JWT/admin secret을 Git/Docker 제외 파일 `deploy/.env.production`에 준비했습니다. `tools/prepare_render_local_environment.py --inspect-local`이 값 출력 없이 14개 필수 키, query 없는 direct URL, secret 강도·분리를 검증합니다.

다음은 이 v346 실행 준비 commit의 정확한 40자리 SHA를 기호가 승인하는 단계입니다. 승인 후에도 실행 직전 `--verify-execution-approval` 관문으로 clean pushed `main`, SHA, service, image, 단일 deploy action을 다시 검사합니다. 승인 전에는 Render를 변경하지 않습니다. 허용 범위는 `upgrade-rpg-api` 서비스 1개 생성, 검토된 env 주입, exact digest 최초 deploy, `/api/v1/health` 대기, `/api/v1/health/db` 한 번의 읽기 확인, managed HTTPS URL과 sanitized evidence 기록입니다. DB/Alembic write, image 변경, custom domain/DNS, 결제수단, 자동 retry·두 번째 deploy는 포함되지 않습니다.

현재 필요한 extension이나 설치는 없습니다. 서버 재시작도 필요하지 않습니다.
