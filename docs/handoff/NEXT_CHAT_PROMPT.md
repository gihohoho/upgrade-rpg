기호의 Upgrade RPG 프로젝트를 이어서 진행합니다.

이번에 첨부하는 최신 ZIP `rpg_v309_runtime_engine_source_binding_inspector_fix_ready.zip`을 반드시 기준으로 작업해주세요.

========================
사용자/응답 방식
========================

사용자는 코딩을 거의 모르는 기호입니다. 항상 한국어로 쉽고 자세하게 설명해주세요.
모든 터미널 명령 바로 위에 실행 위치와 `backend/.venv` 상태를 적어주세요.
Git Bash backend 가상환경: `backend` 폴더에서 `source .venv/Scripts/activate`
Vue/npm: `frontend/vue-app`, Python `.venv` 불필요
Git 명령은 프로젝트 루트에서 한 줄로 주세요.

```bash
git status && git add . && git commit -m "..." && git push
```

DB/env/seed/인증/API body/route/write/migration/Docker volume은 작은 승인 경계로 진행합니다.

========================
현재 기준
========================

- 최신 작업: `v309.runtime-engine-source-binding-inspector-fix`
- readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`
- PostgreSQL baseline: `alembic-managed-baseline-complete`
- source: 23/749, application 22/748, revision `v295_initial_schema`
- v306 candidate operations: 0, next revision required no
- v307 strict + require-health: passed
- v308 pool/lifecycle/production guard/Dockerfile/production Compose 적용

고정 증거:

```txt
restore rehearsal DB: rpg_game_restore_rehearsal_v290
migration DB: rpg_game_migration_empty_v290
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
schema digest: 7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921
data digest: ecb19e57283dc6b780426339bfc46f2bac14da63a618249808f30132508f9244
v305 completion: postgres-baseline-completion-state-verified
v306 result: next-revision-not-required-current-schema-equivalent
```

========================
v309 검사기 오탐 수정
========================

사용자 PC의 v308 결과:

```txt
blocked-or-failed
runtime engine bypasses settings.database_url
```

실제 `backend/app/db/session.py`는 여러 줄 `create_async_engine()` 호출의 첫 인자로 `settings.database_url`을 사용합니다. 오류 원인은 한 줄 문자열 검사였습니다. v309에서는 AST로 positional 또는 `url=`/`database_url=`의 정확한 `settings.database_url`을 확인합니다. 실제 runtime/DB/.env/Docker/Alembic 동작은 변경하지 않았습니다.

========================
다음 첫 작업
========================

실행 위치: `backend` 폴더 / `.venv` 꺼짐

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트 / `backend/.venv` 켜짐

```bash
python tools/check_runtime_config_hardening.py --strict --require-health
```

정상 기대:

```txt
result: runtime-config-hardening-verified-local-runtime-preserved
next safe stage: separate-production-secrets-tls-and-container-validation
```

계속 금지: actual `.env`, production secret/TLS 실제 입력, production Compose build/up/pull/down, Docker volume 변경, stamp 재실행, revision/autogenerate/upgrade/downgrade, DB 생성/삭제/복원, seed/인증/API route/body/write, 게임 콘텐츠 변경.

코드 변경 시 관련 smoke, Python compileall, JS 문법, core smoke, ZIP 무결성/제외 파일 검사를 수행하고 새 ZIP을 제공하세요.
