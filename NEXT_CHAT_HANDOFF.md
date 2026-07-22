# Upgrade RPG Codex handoff — v336

## 현재 상태

```txt
latest: v336.neon-readonly-connectivity-verified-render-onboarding-required
strict result: neon-direct-pooled-readonly-connectivity-verified
next safe stage: owner-connect-render-and-review-database-initialization-plan
deployment safety baseline: v334.production-deploy-plan-reviewed-inputs-blocked
baseline result: production-deploy-plan-reviewed-inputs-blocked
baseline next stage marker: select-production-targets-and-complete-executable-deploy-plan
GitHub remote: https://github.com/gihohoho/upgrade-rpg.git
GHCR repository: ghcr.io/gihohoho/upgrade-rpg-backend
verified reference: ghcr.io/gihohoho/upgrade-rpg-backend@sha256:ff939391517452a3ec477adaa0f8556d3525f9d0c6fb5f9d0df11d8f3d8461d2
provider selection: Render Free Singapore + Neon Free PostgreSQL 16 Singapore
fixed monthly cost: USD 0
Neon account/project: connected/created (PostgreSQL 16, AWS Singapore)
Neon credential: exposed initial password rotated; new URLs local-only, not deployed
Neon read-only connectivity: direct/pooled verified with TLS 1.3 hostname verification
Render account/service/deploy: not connected/not created/not executed
approval ready/approved/executed: no/no/no
```

## v335 선택 결과

개인 프로젝트에서 비용을 최소화하기 위해 Render Free Web Service와 Neon Free PostgreSQL을 모두 Singapore에 두는 조합을 선택했습니다. 첫 공개 주소는 Render가 제공하는 `onrender.com` HTTPS이고 custom domain/DNS는 아직 필요 없습니다. Render secret에 runtime 값을 넣고 private GHCR exact digest를 manual image-backed service로 배포할 계획입니다.

Render에는 처음에 결제수단을 등록하지 않아 한도 초과 시 과금 대신 서비스가 일시 중지되게 합니다. Render Free는 15분 유휴 뒤 잠들며 첫 요청에 약 1분 cold start가 있을 수 있습니다. Neon Free는 100 CU-hours/project/month, 0.5 GB, 6시간 restore history입니다. 이 구성은 SLA production이 아닌 개인용 public preview입니다.

선택 문서는 `docs/current/PRODUCTION_PROVIDER_SELECTION.md`, 정적 계약은 `deploy/production-provider-selection.example.json`, checker는 `tools/check_production_provider_selection.py`입니다.

## Neon onboarding checkpoint — 2026-07-22

기호가 Neon Free PostgreSQL 16 AWS Singapore 프로젝트를 생성했고 Neon Auth는 선택하지 않았습니다. 최초 connection string을 채팅에 붙인 직후 `neondb_owner` 비밀번호를 재설정해 노출 credential을 폐기했습니다. 새 비밀번호와 connection string은 채팅·Git·로그에 받지 않습니다.

로컬 입력 파일 `deploy/.env.production`은 Git과 Docker build context에서 제외됩니다. 새 direct/pooled URL은 이 파일에만 저장됐고 채팅·Git·로그에는 기록하지 않았습니다. `tools/check_neon_readonly_connectivity.py --execute`로 두 연결 모두 PostgreSQL 16.14, TLS 1.3 인증서·호스트 검증, `neondb`/`neondb_owner`, read-only transaction을 확인했습니다. DB write·create, schema/data 초기화, restore, Alembic mutation은 실행하지 않았습니다.

sanitized evidence는 `deploy/review/neon-readonly-connectivity-v336.json`이며 `python tools/check_neon_readonly_connectivity.py --evidence`로 secret 없이 재검증합니다. 첫 검사에서 Neon Proxy 뒤 `pg_stat_ssl`을 클라이언트 TLS 판정에 잘못 사용해 direct 단계가 실패했지만, 클라이언트 TLS transport의 인증서·cipher·version을 직접 확인하도록 수정한 뒤 Direct/Pooler가 모두 통과했습니다.

## 아직 사용자 작업이 필요한 것

Render Hobby에 로그인해야 합니다. Render 결제수단은 추가하지 않습니다. DB 이름은 현재 Neon 기본 `neondb`이고 계획상 대상은 `rpg_game`이므로, DB 생성과 schema/data 초기화는 별도 실행 계획과 승인 뒤에만 진행합니다. 필요한 extension·로컬 설치는 없습니다.

로그인 뒤에도 resource 생성, GHCR `read:packages` PAT 생성·주입, DB schema/data 초기화·이식, actual deploy는 실행 준비 범위와 exact 40자리 SHA 승인을 별도로 확인합니다.

## 공급망과 승인 경계

- CI credential: GitHub Actions `GITHUB_TOKEN`
- private repository required reviewer: 현재 plan에서 unavailable, exact-SHA owner approval 유지
- source-controlled lifecycle gate: `deploy/github-actions-ghcr-publish-lifecycle.json`
- lifecycle: `attempt-recorded` / `publishReviewerGateReady=false`
- preparation/authorization/closure/evidence: `36e8720a53ef7ff6a8334de6bc99646998d63fc9` / `26a11356e33c978afa8cd8a4881500fa62cdbc5c` / `1c4a982b2a35d3d45f59e7d9faefcdecca69e6c5` / `1f0340ddfcf3c8a74cf14110d5957627d4c5d38a`
- run `29909291344`, artifacts `8525220616`, `8525254543`
- run_attempt=1, single dispatch, immediate closure, closureCommitSha 기록, rerun 금지
- 역사 lifecycle 결과 `review-recorded-workflow-attempt-evidence` 보존
- Trivy HIGH/CRITICAL 0, SBOM, provenance, Cosign sign/verify 성공
- isolated evidence: `deploy/review/isolated-image-pull-validation-v333.json`
- reviewed execution plan: `deploy/production-deploy-plan.example.json`

## 유지할 경계

- backend replicas/workers 1/1, Neon PostgreSQL 16, TLS `verify-full`
- auto-deploy와 automatic migration 금지
- 실제 secret/token/PAT/password/CA/cert/key를 Git·채팅·로그·artifact에 기록하지 않음
- DB create/delete/restore/reset/seed/write와 Alembic mutation은 별도 승인 전 금지
- 인증/API write, Vue Preview/Apply/write, 게임 콘텐츠·밸런스 변경 금지
- v334 production input은 실제 resource가 생기기 전까지 계속 unresolved

## 첫 검사

실행 위치: 프로젝트 루트
Python `.venv` 상태: 셸 활성화는 꺼짐, `backend/.venv/Scripts/python.exe` 직접 사용
새 설치 여부: 없음

```bash
python tools/check_neon_readonly_connectivity.py --evidence
python tools/check_production_provider_selection.py --strict
python tools/check_production_deployment_plan.py --strict
python tools/check_github_actions_ghcr_static_plan.py --strict
python tools/check_codex_handoff_readiness.py --strict
```

v336 기대값은 `neon-direct-pooled-readonly-connectivity-verified`, 다음 단계는 `owner-connect-render-and-review-database-initialization-plan`입니다. v335 provider-selection 결과와 v334 deployment baseline도 보존합니다.

서버 재시작은 이 공급자 선택·문서 작업에 필요하지 않습니다.
