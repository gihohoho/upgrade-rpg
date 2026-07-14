기호의 Upgrade RPG 프로젝트를 이어서 진행합니다.

이번에 첨부하는 최신 ZIP `rpg_v299_postgres_migration_test_downgrade_base_ready.zip`을 반드시 기준으로 작업해주세요.

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

- 최신 작업: `v299.postgres-migration-test-downgrade-base-ready`
- readiness version: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

게임 콘텐츠 개발과 Vue write/인증 연결은 계속 보류합니다.

========================
실제 PostgreSQL 상태
========================

```txt
source rpg_game: 22 tables / 748 rows / schema differences=0 / alembic_version 없음
restore rehearsal: 22 tables / 748 rows / differences=0
migration test DB rpg_game_migration_empty_v290:
  public tables: 23
  model tables: 22
  total rows: 1
  current revision: v295_initial_schema
  schema differences: 0
```

verified backup과 실제 DB 보고서는 `local-backups/`, `local-review-artifacts/` 아래에 있으며 Git/전달 ZIP/채팅에 포함하지 않습니다.

========================
검토된 최초 Alembic revision
========================

```txt
revision ID: v295_initial_schema
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
manual review: passed
```

v298에서 isolated migration DB의 `upgrade head`가 실제로 성공했습니다.

========================
다음 첫 작업 — 사용자 승인 완료
========================

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/downgrade_postgres_migration_test_database.py --execute
```

대상은 `rpg_game_migration_empty_v290`만 허용합니다. exact `downgrade base` 후 애플리케이션 테이블 0개, 빈 `alembic_version`, revision rows 0개, differences=22를 확인합니다. source/rehearsal DB는 변경하지 않습니다.

성공 후 다음 단계는 별도 승인으로 두 번째 `upgrade head` 왕복 재현성 검증입니다. 원본 DB stamp/upgrade와 DB 삭제는 아직 실행하지 않습니다.

작업 후 관련 smoke, compileall, core smoke, ZIP 무결성/제외 검사를 수행하고 새 ZIP을 만드세요.
