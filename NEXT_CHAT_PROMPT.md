기호의 Upgrade RPG 프로젝트를 이어서 진행합니다.

이번에 첨부하는 최신 ZIP `rpg_v311_production_capacity_tls_network_plan_handoff_ready.zip`을 반드시 기준으로 작업해주세요.

========================
사용자/응답 방식
========================

사용자는 코딩을 거의 모르는 기호입니다. 항상 한국어로 쉽고 자세하게 설명해주세요.

모든 터미널 명령 바로 위에 반드시 다음을 함께 적어주세요.

* 실행 위치
* Python 가상환경 `.venv`를 켜야 하는지/꺼도 되는지

실제 backend 가상환경은 프로젝트 루트가 아니라 `backend/.venv`입니다.
Git Bash에서는 `backend` 폴더에서 아래 명령으로 켭니다.

```bash
source .venv/Scripts/activate
```

Vue/npm 명령은 `frontend/vue-app`에서 실행하며 Python `.venv`가 필요 없습니다.

설치해야 할 파일·라이브러리·프레임워크와 사용자가 확인할 항목을 빠짐없이 알려주세요. 새 설치가 없으면 없다고 명확히 적어주세요.

Git 명령은 프로젝트 루트에서 아래 형태의 한 줄 블록으로 주세요.

```bash
git status && git add . && git commit -m "..." && git push
```

필요한 설치와 여러 단계 작업은 허용됩니다. 다만 DB/env/seed/인증/API body/route/write/migration/Docker container·volume/production secret·TLS는 작은 승인 경계로 진행하고 실제 결과를 확인한 뒤 다음 단계로 넘어가세요.

========================
현재 최신 기준
========================

* 최신 작업: `v311.production-capacity-tls-network-isolated-plan`
* readiness: `v250.backend-admin-rollback-snapshot`
* backend splitStatus: `admin-schema-field-constraint-contract-v238`
* backend virtualenv: `backend/.venv`
* legacy 게임: `index.html`
* legacy 관리자: `admin.html`
* legacy JS/CSS: `src/`
* Vue 앱: `frontend/vue-app/`
* Vue는 GET read-only API까지만 연결
* Preview/Apply/write/인증은 Vue에 연결하지 않음
* 게임 콘텐츠와 밸런스 개발은 계속 보류

========================
PostgreSQL/Alembic 완료 상태
========================

```txt
classification: alembic-managed-baseline-complete
source DB: rpg_game
source public tables/rows: 23/749
source application tables/rows: 22/748
source current revision: v295_initial_schema
restore rehearsal DB: rpg_game_restore_rehearsal_v290 / 23/749 / verified
migration test DB: rpg_game_migration_empty_v290 / 23/1 / differences=0
v305 completion: postgres-baseline-completion-state-verified
v306 candidate operations: 0
next revision required: no
```

고정 증거:

```txt
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
schema digest: 7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921
data digest: ecb19e57283dc6b780426339bfc46f2bac14da63a618249808f30132508f9244
backup: local-backups/postgres/rpg_game_20260714_130403_KST_v290.custom.dump
backup SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
```

`local-backups/`와 `local-review-artifacts/`는 기호 PC에만 있으며 Git/ZIP/채팅에 포함하지 않습니다.

기존 source/rehearsal stamp는 완료됐으므로 다시 실행하지 않습니다. 새 revision/autogenerate/upgrade/downgrade도 승인되지 않았습니다.

========================
Runtime 실제 통과 상태
========================

```txt
v307 strict + require-health: passed
Docker PostgreSQL: running=True / healthy=True
FastAPI live DB health GET: ok
v308 pool/lifecycle/production guard/Dockerfile/production Compose: applied
v309 AST runtime engine binding inspector: passed
v310 production static validation: passed
result: runtime-config-hardening-verified-local-runtime-preserved
remaining production warnings: 9
```

남은 경고:

```txt
environment-not-production
debug-enabled
jwt-local-default
admin-write-local-default
compose-local-password
adminer-published
postgres-host-port-published
postgres-image-not-digest-pinned
database-tls-not-configured
```

위 경고는 현재 로컬 개발 환경에서는 예상 상태입니다. 실제 로컬 `.env`나 `docker-compose.yml`을 운영값으로 바꾸지 마세요.

========================
v310 실제 통과 상태
========================

```txt
required Compose placeholders: 9/9
password/CA Compose secrets: True/True
digest-pinned image placeholder: True
TLS example verify-full/CA path: True/True
actual secret values absent: True
Adminer/host ports absent: True/True
backend healthcheck/read-only/non-root: True/True/True
result: production-static-validation-template-verified-runtime-application-blocked
actual production secrets/TLS/container execution approved: no
```

========================
v311 준비 및 완료 내용
========================

추가 파일:

```txt
deploy/production-capacity-plan.example.json
deploy/isolated-validation/README.md
docs/current/POSTGRES_PRODUCTION_CAPACITY_TLS_NETWORK_PLAN.md
tools/check_production_capacity_tls_network_plan.py
tools/smoke/backend/smoke_production_capacity_tls_network_plan.py
```

현재 review-only 계산:

```txt
backend replicas/workers: 1/1
SQLAlchemy engine count: 1
pool steady/burst connections: 5/15
non-application reserve/safety margin: 10/20%
planned peak before safety: 25
recommended/candidate max_connections: 30/40
future 2-replica / 2x2-worker minimums: 50/90
TLS database mode: managed-postgresql-preferred
reverse proxy only / DB internal: True/True
isolated container execution approved: no
```

`max_connections=40`은 실제 PostgreSQL에 적용된 값이 아니라 review 후보입니다.

========================
다음 첫 작업 — 읽기 전용 v311 검사
========================

먼저 아래 명령의 실제 결과를 수집하세요. 이 명령은 프로젝트 파일만 읽으며 실제 env/secret, Docker, DB, Alembic을 건드리지 않습니다.

실행 위치: `backend` 폴더
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_production_capacity_tls_network_plan.py --strict
```

정상 기대 결과:

```txt
recommended/candidate max_connections: 30/40
future 2-replica / 2x2-worker minimums: 50/90
TLS database mode: managed-postgresql-preferred
reverse proxy only / DB internal: True/True
actual Docker command executed: no
actual DB/Alembic mutation executed: no
isolated container execution approved: no
result: production-capacity-tls-network-plan-verified-execution-blocked
next safe stage: approve-provider-and-isolated-container-config-render-only
```

검사가 통과해도 Docker 명령을 실행하지 마세요. 다음 단계는 실제 예상 트래픽/replica 목표, 관리형 PostgreSQL 또는 bundled TLS 선택, reverse proxy 제품/DNS/certificate 방향을 먼저 승인받는 것입니다.

그 뒤에도 첫 Docker 단계는 `compose config` render-only이며 별도 승인 없이는 실행하지 않습니다. build/pull/up/down은 각각 더 뒤의 별도 승인 경계입니다.

========================
절대 변경/실행 금지
========================

사용자 별도 승인 전에는 다음을 변경하거나 실행하지 마세요.

* 실제 `backend/.env`, production env, JWT/Admin secret
* 실제 password/CA/cert/key 파일 생성·입력·커밋
* `docker compose -f deploy/docker-compose.production.yml config/build/pull/up/down`
* Docker container/volume 삭제 또는 변경
* PostgreSQL `max_connections` 실제 변경
* source/rehearsal stamp 재실행
* 새 Alembic revision/autogenerate/upgrade/downgrade
* DB 생성/삭제/복원/reset/seed
* 인증, API route path/response body, write logic/Write Guard
* Vue Preview/Apply/write 연결
* 게임 콘텐츠/장비/스킬/보스/드랍률/밸런스 변경

========================
검증/전달 원칙
========================

코드나 구조를 변경했다면 최소 다음을 확인하세요.

* 관련 전용 smoke
* Python 문법: `python -m compileall -q backend/app backend/scripts backend/alembic tools`
* JavaScript 문법
* `bash tools/run_smoke_core.sh`
* Vue 변경 시 `npm ci`와 `npm run build`
* ZIP 무결성 및 제외 파일 검사

작업 후에는 다음 5개를 포함해 답변하세요.

1. 이번에 한 일
2. 검증 완료한 것
3. 서버 재실행 명령 — 실행 위치와 `.venv` 상태 포함
4. Git 명령 — 프로젝트 루트에서 한 줄
5. 다음 추천 단계

코드 또는 문서를 변경했다면 새 ZIP도 같이 만들어주세요.
