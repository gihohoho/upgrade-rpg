# Upgrade RPG Codex handoff — v344

## 현재 상태

```txt
latest: v344.neon-restore-verified-stamp-recovery-preparation-ready
strict result: neon-restore-verified-stamp-recovery-preparation-ready
next safe stage: owner-approve-neon-stamp-recovery-preparation-sha
render plan: v340.render-service-settings-reviewed-creation-blocked
neon plan: v344.neon-restore-verified-stamp-recovery-preparation-ready
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
Render registry credential/service/deploy: present/not created/not executed
Render credential action ready/approved/executed: yes/yes/yes
production deployment approval ready/approved/executed: no/no/no
```

## Render/Neon 분리 계획 — 2026-07-26

- Render 계약: `deploy/render-service-settings.example.json`
- Neon 계약: `deploy/neon-database-initialization-migration.example.json`
- v341 source: runtime/Alembic 공용 system-CA hostname-verifying SSLContext 적용 완료
- Render env inventory: `deploy/render.production.env.example`로 분리 완료
- 현재 verified image: v341 source 포함, 공급망·isolated CA-store/runtime 검증 완료
- Neon `neondb`: 승인된 restore 뒤 22 application tables / 748 rows / no Alembic
- DB 선택: 새 `rpg_game`을 만들지 않고 기존 빈 `neondb` 사용
- 이식: verified custom dump 22 application tables / 748 rows restore 후 exact `v295_initial_schema` stamp
- 연결: restore/Alembic/runtime 모두 direct; pooled URL은 restore/Alembic에 사용 금지
- 순서: image publish/isolated validation 완료 → Neon restore 1회 완료 → 별도 exact-SHA stamp-only recovery → 별도 exact-SHA Render create/deploy
- Render name: `upgrade-rpg-api`, owner 확인 완료
- v344 tool: `tools/initialize_neon_database.py`, 재복원 금지 + exact SHA/target/backup/revision/action + clean pushed main guard
- read-only preflight: asyncpg system CA와 PostgreSQL 16/libpq exported Windows system CA `verify-full` 모두 통과
- current Neon mutation: restore 1회 완료 / stamp·Render write 없음

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
- lifecycle: `attempt-recorded` / `publishReviewerGateReady=false` / prior five attempts preserved
- run `30180738530`: provenance/SBOM, exact-digest Trivy 0건, Cosign sign/verify 성공
- v341 image preparation/authorization/closure/evidence: `fb231afa5081f5bfd7b459081a58bc5acd6699df` / `f5d69c1bbef101cc9124b9dede18c844ef80b59c` / `ebb5ef46e3115bc358d62d93a64002b8711f4232` / `cf9e0bab121186d2ac51f889f807348cc46f192c`
- v341 image artifact IDs: `8625485901`, `8625478503`
- run policy: `run_attempt=1`, single dispatch, immediate closure, `closureCommitSha`, rerun 금지
- 역사 lifecycle 결과 `review-recorded-workflow-attempt-evidence` 보존
- isolated evidence: `deploy/review/isolated-image-pull-validation-v342.json`
- production plan: `deploy/production-deploy-plan.example.json`
- historical preparation/authorization/closure/record SHA: `36e8720a53ef7ff6a8334de6bc99646998d63fc9` / `26a11356e33c978afa8cd8a4881500fa62cdbc5c` / `1c4a982b2a35d3d45f59e7d9faefcdecca69e6c5` / `1f0340ddfcf3c8a74cf14110d5957627d4c5d38a`
- historical artifact IDs: `8525220616`, `8525254543`
- private plan에는 native required reviewer가 없어 exact-SHA owner approval을 유지
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

사용자가 승인한 v343 SHA `d6df9984e00d08b28fd524dcfefeb492e334d5e9`로 단일 트랜잭션 restore를 한 번 실행했습니다. 22 tables / 748 rows / schema digest는 즉시 일치했지만 legacy data digest가 session timezone offset에 의존해 달라졌고 도구는 stamp 전에 안전하게 중단했습니다.

verified local rehearsal은 `Asia/Seoul`, Neon은 `GMT`이며 양쪽에 44개 `timestamptz` 컬럼이 있습니다. aware datetime을 UTC로 정규화한 application data digest `4ea23cfd2446b522cc9e85e2a8520160427cf8e3987d9b6ab04f4b99fbf6c00c`로 양쪽이 정확히 일치했습니다. sanitized evidence는 `deploy/review/neon-restore-prestamp-verification-v344.json`입니다.

다음 작업은 v344 recovery 준비 commit의 정확한 40자리 SHA를 기호에게 승인받은 뒤 `--resume-stamp`로 기존 복원 상태를 재검증하고 exact v295 stamp만 한 번 실행하는 것입니다. `pg_restore` 재실행은 금지되며 Render 생성·배포도 포함되지 않습니다. 필요한 extension·권한·새 설치는 현재 없습니다.

## 첫 검사

실행 위치: 프로젝트 루트
Python `.venv` 상태: 셸 활성화는 꺼짐, `backend/.venv/Scripts/python.exe` 직접 사용
새 설치 여부: 없음

```bash
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

v344 기대 결과는 `neon-restore-verified-stamp-recovery-preparation-ready`, 다음 단계는 `owner-approve-neon-stamp-recovery-preparation-sha`입니다. v340 Render 계획, v338 Render Connect, v337 account readiness, v336 Neon evidence, v335 provider selection과 v334 deployment baseline을 계속 보존합니다.

서버 재시작은 필요하지 않습니다.
