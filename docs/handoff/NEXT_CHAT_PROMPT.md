# Upgrade RPG Codex next prompt — v334

프로젝트 루트의 `AGENTS.md`, `NEXT_CHAT_HANDOFF.md`, `docs/current/CURRENT_STATUS.md`를 먼저 읽고 계속 지켜주세요. 기호는 코딩을 거의 모르므로 한국어로 쉽게 설명하고, 모든 터미널 명령 위에 실행 위치, Python `.venv` 상태, 새 설치 여부를 적어주세요. 필요한 extension·권한·설치는 해결될 때까지 요청해주세요.

Codex가 개발 서버와 기존 local PostgreSQL dependency를 필요에 따라 관리하고, 변경 뒤 Git add/commit/push까지 직접 합니다. ZIP과 Git 명령 안내는 필요 없습니다. root handoff와 `docs/handoff/` mirror는 매 작업 동기화합니다.

## 현재 고정값

```txt
latest: v334.production-deploy-plan-reviewed-inputs-blocked
strict result: production-deploy-plan-reviewed-inputs-blocked
next safe stage: select-production-targets-and-complete-executable-deploy-plan
GitHub remote: https://github.com/gihohoho/upgrade-rpg.git
GHCR repository: ghcr.io/gihohoho/upgrade-rpg-backend
visibility/platform: private / linux/amd64
CI credential: GitHub Actions GITHUB_TOKEN
local pull credential: GitHub CLI OAuth read:packages → Docker credential store
publish model: owner-only-source-controlled-two-step
source-controlled lifecycle gate: deploy/github-actions-ghcr-publish-lifecycle.json
lifecycle: attempt-recorded / publishReviewerGateReady=false
production reference: ghcr.io/gihohoho/upgrade-rpg-backend@sha256:ff939391517452a3ec477adaa0f8556d3525f9d0c6fb5f9d0df11d8f3d8461d2
production deploy plan reviewed: yes
approval ready/approved/executed: no/no/no
```

운영 구조는 managed PostgreSQL + provider CA `verify-full` + external reverse proxy HTTPS + backend replicas/workers 1/1입니다. Alembic current는 `v295_initial_schema`, 새 revision 필요는 `no`입니다.

## 보존할 공급망 증거

- preparation/authorization/closure/evidence: `36e8720a53ef7ff6a8334de6bc99646998d63fc9` / `26a11356e33c978afa8cd8a4881500fa62cdbc5c` / `1c4a982b2a35d3d45f59e7d9faefcdecca69e6c5` / `1f0340ddfcf3c8a74cf14110d5957627d4c5d38a`
- run `29909291344`, artifacts `8525220616`, `8525254543`
- run_attempt=1, single dispatch, immediate closure, closureCommitSha 기록, rerun 금지
- 일반 lifecycle 결과 단계 `review-recorded-workflow-attempt-evidence`는 역사 계약으로 유지
- isolated evidence: `deploy/review/isolated-image-pull-validation-v333.json`

## 이번 다음 작업

`docs/current/PRODUCTION_DEPLOYMENT_PLAN.md`와 `deploy/production-deploy-plan.example.json`은 검토 완료했지만 아래 입력이 아직 없습니다.

1. production host/provider/region/OS와 접속 방식
2. managed PostgreSQL provider/product/region/endpoint/network
3. provider CA PEM과 host mount path
4. reverse proxy/ingress, domain, DNS, certificate 발급·갱신 방식
5. 실제 secret 주입 위치
6. external edge network 이름
7. managed DB backup 상태와 첫 배포 rollback 담당

기호에게 이 정보를 쉽게 요청한 뒤, 실제 값을 Git에 넣지 말고 실행 가능한 final deploy plan을 준비해주세요. 실제 production resource 변경 전에는 그 준비 commit의 정확한 40자리 SHA를 별도 승인받아야 합니다.

## 첫 읽기 전용 검사

실행 위치: 프로젝트 루트
Python `.venv` 상태: 셸 활성화는 꺼짐, `backend/.venv/Scripts/python.exe` 직접 사용
새 설치 여부: 없음

```bash
python tools/check_production_deployment_plan.py --strict
python tools/check_github_actions_ghcr_static_plan.py --strict
python tools/check_codex_handoff_readiness.py --strict
```

기대값:

```txt
result: production-deploy-plan-reviewed-inputs-blocked
next safe stage: select-production-targets-and-complete-executable-deploy-plan
```

별도 승인 전에는 production GHCR login/pull, Compose up/down, container/network/volume/DNS/proxy 변경, actual managed DB 연결을 실행하지 않습니다. DB write/reset/seed/restore, Alembic mutation, auth/API write, Vue Preview/Apply/write, 게임 콘텐츠·밸런스는 구체적 요청 전 금지합니다.
