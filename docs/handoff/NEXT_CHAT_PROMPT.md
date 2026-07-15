기호의 Upgrade RPG 프로젝트를 이어서 진행합니다.

이번에 첨부하는 최신 ZIP `rpg_v313_backend_image_source_digest_policy_handoff_ready.zip`을 반드시 기준으로 작업해주세요.

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

필요한 설치와 여러 단계 작업은 허용됩니다. 다만 DB/env/seed/인증/API body/route/write/migration/Docker image·container·network·volume/registry credential/production secret/TLS는 작은 승인 경계로 진행하고 실제 결과를 확인한 뒤 다음 단계로 넘어가세요.

========================
현재 최신 기준
========================

* 최신 작업: `v313.backend-image-source-digest-policy`
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

source/rehearsal stamp는 완료됐으므로 다시 실행하지 않습니다. 새 revision/autogenerate/upgrade/downgrade도 승인되지 않았습니다.

========================
운영 방향과 실제 통과 상태
========================

```txt
database: managed-postgresql-selected
TLS: verify-full-with-provider-ca
public entrypoint: external-reverse-proxy-https-selected
backend replicas/workers: 1/1
max_connections review candidate: 40
```

기호 PC에서 v312 config render-only가 실제 통과했습니다.

```txt
rendered services: backend
host ports/build/named volumes absent: True/True/True
managed DB service absent / backend replicas: True/1
digest/production guard/TLS/edge rendered: True/True/True/True
image pull/build executed: no
container/network/volume mutation executed: no
DB/Alembic mutation executed: no
result: production-compose-config-render-verified-no-runtime-mutation
```

안전 요약은 `deploy/review/production-compose-config-render-v312.json`에 기록되어 있습니다. raw render와 실제 env/secret은 저장되지 않았습니다.

========================
v313 backend image 정책
========================

```txt
production reference mode: digest-only
repository pattern: <approved-registry>/<approved-namespace>/upgrade-rpg-backend
registry provider: deferred
target platform: deferred
current base image: python:3.11-slim
base image digest approved: no
SBOM/provenance/signature/vulnerability review required: yes/yes/yes/yes
image pull/build/push approved: no/no/no
container start approved: no
```

현재 base image는 mutable tag이므로 exact digest 승인 전 production build를 실행하지 않습니다.

========================
다음 첫 작업 — v313 읽기 전용 검사
========================

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_backend_image_source_digest_policy.py --strict
```

정상 기대 결과:

```txt
config render evidence verified: True
registry/repository/platform: deferred / <placeholder> / deferred
production reference mode: digest-only
current base image: python:3.11-slim
base image digest pinned/approved: False/False
supply-chain gates required: 4/4
image pull/build/push approved: no/no/no
result: backend-image-source-digest-policy-verified-provider-and-build-blocked
next safe stage: select-registry-repository-platform-and-base-image-digest
```

검사 후 registry provider, namespace/repository, target platform, base image exact digest를 먼저 검토합니다. 이 선택 단계에서도 Docker pull/build/push는 실행하지 않습니다.

========================
절대 변경/실행 금지
========================

사용자 별도 승인 전에는 다음을 변경하거나 실행하지 마세요.

* 실제 `backend/.env`, production env, JWT/Admin secret
* 실제 password/CA/cert/key/registry credential 파일 생성·입력·커밋
* Docker image pull/build/push
* Docker container/network/volume create/start/stop/remove
* `docker compose ... up/down/run/start/stop/rm`
* managed PostgreSQL 실제 연결/query/설정 변경
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
