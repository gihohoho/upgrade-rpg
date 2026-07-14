기호의 Upgrade RPG 프로젝트를 이어서 진행합니다.

이번에 첨부하는 최신 ZIP `rpg_v294_postgres_migration_test_database_creation_ready.zip`을 반드시 기준으로 작업해주세요.

========================
사용자/응답 방식
========================

사용자는 코딩을 거의 모르는 기호입니다.
항상 한국어로 쉽고 자세하게 설명해주세요.

모든 터미널 명령은 다음을 바로 위에 함께 적어주세요.

- 실행 위치
- Python 가상환경 `.venv`를 켜야 하는지/꺼도 되는지

실제 backend 가상환경은 프로젝트 루트가 아니라 `backend/.venv`입니다.
Git Bash에서는 `backend` 폴더에서 `source .venv/Scripts/activate`로 켭니다.
Vue/npm 명령은 `frontend/vue-app`에서 실행하며 Python `.venv`가 필요 없습니다.

사용자가 확인해야 할 사항, 설치해야 할 파일·라이브러리·프레임워크, 새 도구를 빠짐없이 알려주세요.
새 설치가 없으면 없다고 명확히 적어주세요.

git 명령은 프로젝트 루트에서 아래 형태의 한 줄 블록으로 주세요.

```bash
git status && git add . && git commit -m "..." && git push
```

DB/env/seed/인증/API body/route/write/migration/Docker volume 작업은 작게 나누고 실제 결과를 확인한 뒤 진행하세요.

========================
현재 최신 기준
========================

- 최신 작업: `v294.postgres-migration-empty-database-create-tool`
- readiness version: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

legacy 화면:

- 게임: `index.html`
- 관리자: `admin.html`
- legacy JS/CSS: `src/`

Vue 앱:

- 위치: `frontend/vue-app/`
- `/admin` GET 연결 완료: health, requirements, domains, catalog, detail, relations
- Preview/Apply/write/인증은 Vue에 연결하지 않음

게임 콘텐츠 개발은 계속 보류합니다.

========================
실제 PostgreSQL source 상태
========================

```txt
PostgreSQL: 16.14
DB/user: rpg_game / rpg_user
SQLAlchemy model/public tables: 22 / 22
total rows: 748
alembic_version/current revision: 없음
health/db: HTTP 200
classification: existing-schema-without-alembic-baseline
schema equivalence: structurally-equivalent
differences: 0
```

실제 backup 생성 결과:

```txt
backup: local-backups/postgres/rpg_game_20260714_130403_KST_v290.custom.dump
size: 126.60 KB
SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
source tables/rows: 22 / 748
TOC definitions/data: 22 / 22
```

실제 restore rehearsal 결과:

```txt
result: restore-rehearsal-completed-and-verified
target: rpg_game_restore_rehearsal_v290
public tables/rows: 22 / 748
schema: structurally-equivalent / differences=0
alembic_version: absent
source before/after: 22 tables / 748 rows
```

`.dump`, restore report, `local-backups/`는 민감정보이므로 Git, ZIP, 채팅에 포함하지 않습니다.

========================
v294 추가 사항
========================

- `tools/create_postgres_migration_test_database.py`
- `tools/smoke/backend/smoke_postgres_migration_test_database_creation.py`
- `docs/current/POSTGRES_MIGRATION_TEST_DB_CREATION.md`
- exact backup/SHA-256와 v293 restore report 재검증
- source/rehearsal table별 row counts 재검증
- rehearsal schema differences=0 재검증
- target은 `rpg_game_migration_empty_v290`으로 고정
- target이 존재하면 생성 금지
- 없을 때만 owner `rpg_user`, `template0`으로 빈 DB 생성
- 생성 후 0 tables / 0 rows / `alembic_version` 없음 확인
- source/rehearsal before/after 동일 확인
- restore/drop/Alembic mutation 없음

========================
다음 첫 작업
========================

사용자가 아래 명령을 실제 PC에서 실행한 결과를 확인하세요.

```bash
python tools/create_postgres_migration_test_database.py --execute
```

성공 기준:

```txt
result: migration-test-database-created-empty-and-verified
migration test DB: rpg_game_migration_empty_v290
target public tables: 0
target total rows: 0
target alembic_version: absent
source tables/rows before/after: 22/748 -> 22/748
rehearsal tables/rows before/after: 22/748 -> 22/748
```

성공하면 최초 Alembic revision 생성 계획과 수동 검토 절차를 다음 승인 경계로 진행합니다.
오류가 나오면 자동 retry/drop으로 넘어가지 말고 결과부터 분석하세요.

========================
절대 변경/실행 금지
========================

사용자 별도 승인 전:

- `dropdb`
- `python -m alembic revision --autogenerate`
- `python -m alembic upgrade head`
- `python -m alembic downgrade`
- `python -m alembic stamp head`
- 원본/리허설 DB schema/data
- Docker container/volume 삭제
- `.env`, seed, 인증
- 기존 API route path/response body
- 실제 write/Write Guard
- 게임 콘텐츠

작업 후에는 관련 smoke, compileall, core smoke, ZIP 무결성/제외 검사를 수행하고 새 ZIP을 만들어주세요.
마지막 답변에는 이번에 한 일, 검증, 서버 재실행, git 한 줄, 다음 추천 단계를 포함하세요.
