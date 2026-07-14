기호의 Upgrade RPG 프로젝트를 이어서 진행합니다.

이번에 첨부하는 최신 ZIP `rpg_v298_postgres_initial_alembic_manual_review_upgrade_ready.zip`을 반드시 기준으로 작업해주세요.

========================
사용자/응답 방식
========================

사용자는 코딩을 거의 모르는 기호입니다. 항상 한국어로 쉽고 자세하게 설명해주세요.

모든 터미널 명령 바로 위에 실행 위치와 Python `.venv` 상태를 적어주세요.

- backend 가상환경: `backend/.venv`
- Git Bash 활성화: `backend`에서 `source .venv/Scripts/activate`
- Vue/npm: `frontend/vue-app`, Python `.venv` 불필요
- Git: 프로젝트 루트 한 줄 블록

DB/env/seed/인증/API body/route/write/migration/Docker volume 작업은 작은 승인 경계로 진행하세요.

========================
현재 최신 기준
========================

- 최신 작업: `v298.postgres-initial-alembic-manual-review-upgrade-ready`
- readiness version: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

게임 콘텐츠 개발과 Vue write/인증 연결은 계속 보류합니다.

========================
실제 PostgreSQL 상태
========================

```txt
source rpg_game: 22 tables / 748 rows / schema differences=0 / alembic_version 없음
restore rehearsal rpg_game_restore_rehearsal_v290: 22 tables / 748 rows / differences=0
migration test DB rpg_game_migration_empty_v290:
  public tables: [alembic_version]
  total rows: 0
  recorded revisions: []
```

backup:

```txt
local-backups/postgres/rpg_game_20260714_130403_KST_v290.custom.dump
SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
```

실제 backup과 `local-backups/`는 Git/전달 ZIP/채팅에 포함하지 않습니다.

========================
검토된 최초 Alembic revision
========================

```txt
revision ID: v295_initial_schema
revision file: backend/alembic/versions/v295_initial_schema_initial_postgresql_schema.py
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
```

v298 수동 교차 검토 결과:

```txt
tables: 22 / 22
columns: 209 / 209
indexes: 42 / 42
FK: 21
explicit Unique: 6
Check: 0
type/nullability/PK/FK/unique/index/server default: all matched
downgrade order: valid
```

수동 검토 결론은 `approved-for-isolated-empty-migration-database-upgrade-only`입니다. 원본 DB upgrade/stamp 승인은 아닙니다.

========================
다음 첫 작업
========================

아직 실제 `upgrade head` 승인은 받지 않은 상태입니다.

먼저 사용자 PC에서 읽기 전용으로 아래를 실행하게 하세요.

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/upgrade_postgres_migration_test_database.py --inspect
```

`ready-for-separate-upgrade-approval`이면 별도 명시 승인을 받은 뒤에만 아래를 실행합니다.

```bash
python tools/upgrade_postgres_migration_test_database.py --execute
```

대상은 `rpg_game_migration_empty_v290`만 허용합니다. source/rehearsal DB, `.env`, Docker volume은 변경하지 않습니다. downgrade/stamp/create/drop/restore는 실행하지 않습니다.

작업 후 관련 smoke, compileall, core smoke, ZIP 무결성/제외 검사를 수행하고 새 ZIP을 만드세요.
