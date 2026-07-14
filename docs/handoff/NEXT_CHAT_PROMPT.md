기호의 Upgrade RPG 프로젝트를 이어서 진행합니다.

이번에 첨부하는 최신 ZIP `rpg_v302_postgres_restore_rehearsal_stamp_guard_ready.zip`을 반드시 기준으로 작업해주세요.

========================
사용자/응답 방식
========================

사용자는 코딩을 거의 모르는 기호입니다.
항상 한국어로 쉽고 자세하게 설명해주세요.

모든 터미널 명령은 바로 위에 다음을 함께 적어주세요.

- 실행 위치
- Python 가상환경 `.venv`를 켜야 하는지/꺼도 되는지

실제 backend 가상환경은 프로젝트 루트가 아니라 `backend/.venv`입니다.
Git Bash에서는 `backend` 폴더에서 `source .venv/Scripts/activate`로 켭니다.
Vue/npm 명령은 `frontend/vue-app`에서 실행하며 Python `.venv`가 필요 없습니다.

사용자가 확인해야 할 사항, 설치해야 할 파일·라이브러리·프레임워크, 새로 추가되는 도구를 빠짐없이 알려주세요.
새 설치가 없으면 없다고 명확히 적어주세요.

git 명령은 프로젝트 루트에서 아래 형태의 한 줄 블록으로 주세요.

```bash
git status && git add . && git commit -m "..." && git push
```

필요한 라이브러리/파일 설치와 여러 단계 작업은 허용됩니다.
다만 DB/env/seed/인증/API body/route/write/migration/Docker volume처럼 위험한 작업은 작은 승인 경계로 진행하고 실제 결과를 확인한 뒤 다음 단계로 넘어가세요.

========================
현재 최신 기준
========================

- 최신 작업: `v302.postgres-restore-rehearsal-stamp-head-guard-ready`
- readiness version: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

현재 legacy 화면:

- 게임: `index.html`
- 관리자: `admin.html`
- legacy JS/CSS: `src/`

현재 Vue 앱:

- 위치: `frontend/vue-app/`
- `/admin` GET 연결 완료: health, requirements, domains, catalog, detail, relations
- Preview/Apply/write/인증은 Vue에 연결하지 않음

당분간 게임 콘텐츠 개발은 하지 않습니다.
장비/스킬/보스/필드/드랍률/밸런스/강화 수치 추가·조정은 보류합니다.

========================
실제 PostgreSQL/Alembic 완료 상태
========================

원본 DB:

```txt
DB: rpg_game
owner/user: rpg_user
PostgreSQL: 16.14
tables: 22
rows: 748
schema: structurally-equivalent / differences=0
alembic_version: 없음
current revision: 없음
classification: existing-schema-without-alembic-baseline
```

검증된 backup:

```txt
file: local-backups/postgres/rpg_game_20260714_130403_KST_v290.custom.dump
SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
TOC definitions/data: 22 / 22
```

복원 리허설 DB:

```txt
DB: rpg_game_restore_rehearsal_v290
tables: 22
rows: 748
schema: structurally-equivalent / differences=0
alembic_version: 없음
```

migration 테스트 DB:

```txt
DB: rpg_game_migration_empty_v290
public tables: 23
model tables: 22
total rows including Alembic control row: 1
current revision: v295_initial_schema
schema: structurally-equivalent / differences=0
```

최초 revision:

```txt
revision ID: v295_initial_schema
revision file: backend/alembic/versions/v295_initial_schema_initial_postgresql_schema.py
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
manual review: passed
create_table/create_index: 22 / 42
drop_table/drop_index: 22 / 42
```

사용자 PC에서 실제 완료된 검증:

```txt
v298: upgrade head 성공
v299: downgrade base 성공
v300: 두 번째 upgrade head 성공
sequence: upgrade -> downgrade base -> upgrade
first/second upgrade signatures: identical
source/rehearsal preserved: 22 tables / 748 rows
v301 source baseline stamp preflight: 실제 통과
v301 result: ready-for-separate-restore-rehearsal-stamp-approval
```

필수 로컬 증거는 아래에 있으며 Git/전달 ZIP/채팅에 포함하지 않습니다.

```txt
local-backups/
local-review-artifacts/alembic/v295_initial_schema.upgrade-v298.json
local-review-artifacts/alembic/v295_initial_schema.downgrade-v299.json
local-review-artifacts/alembic/v295_initial_schema.roundtrip-upgrade-v300.json
```

========================
v302 준비 완료 범위
========================

추가 파일:

```txt
tools/stamp_postgres_restore_rehearsal_database.py
tools/smoke/backend/smoke_postgres_restore_rehearsal_stamp_guard.py
docs/current/POSTGRES_RESTORE_REHEARSAL_STAMP_GUARD.md
```

고정 경계:

```txt
exact target: rpg_game_restore_rehearsal_v290
exact revision: v295_initial_schema
exact revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
allowed Alembic operation: stamp head only
```

v302 guard는 table count뿐 아니라 22개 application table의 구조 SHA-256과 전체 748개 row-content SHA-256을 수집하고 stamp 전후 exact 비교하도록 준비됐습니다.
성공 시 허용되는 유일한 차이는 `alembic_version` 1 table과 revision row 1개입니다.
source와 migration DB의 전체 signatures도 전후 같아야 합니다.

이번 ZIP 준비 과정에서는 실제 PostgreSQL stamp를 실행하지 않았습니다.
전용 smoke의 stamp는 fake subprocess로만 검증했습니다.

========================
다음 첫 작업 — 읽기 전용 v302 inspect
========================

먼저 사용자 PC에서 아래 명령의 실제 결과를 수집하세요.
이 명령은 모든 DB를 읽기만 하며 stamp/upgrade/downgrade를 실행하지 않습니다.

실행 위치: `backend` 폴더
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/stamp_postgres_restore_rehearsal_database.py --inspect
```

정상 기대 핵심:

```txt
exact target DB: rpg_game_restore_rehearsal_v290
exact revision: v295_initial_schema
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
source preflight: ready-for-separate-restore-rehearsal-stamp-approval
rehearsal application tables/rows: 22/748
rehearsal schema digest: <SHA-256>
rehearsal data digest: <SHA-256>
result: ready-for-separate-restore-rehearsal-stamp-execution-approval
```

inspect가 통과해도 실제 rehearsal stamp를 바로 실행하지 마세요.
전체 출력 확인 후 사용자에게 mutation 범위를 다시 설명하고 별도 명시 승인을 받아야 합니다.

========================
다음 단계 안전 순서
========================

1. v302 `--inspect` 실제 결과 확인
2. exact target/revision/SHA와 digests 확인
3. 사용자에게 실제 mutation이 `alembic_version` 1 table/1 row 추가뿐임을 설명
4. 사용자 별도 명시 승인
5. 승인 후 restore rehearsal DB에서만 exact `stamp head`
6. application schema/data digest 동일 확인
7. current revision `v295_initial_schema` 확인
8. source/migration DB signatures 동일 확인
9. rehearsal stamp 결과 통과 뒤 원본 source stamp guard 설계
10. 원본 source stamp는 다시 별도 승인

========================
절대 변경/실행 금지
========================

사용자 명시 승인 전에는 다음을 변경하거나 실행하지 마세요.

- `python tools/stamp_postgres_restore_rehearsal_database.py --execute ...`
- 원본 `rpg_game`의 schema/data/Alembic 이력
- 원본 DB `upgrade`, `downgrade`, `stamp`
- migration test DB의 추가 upgrade/downgrade/stamp
- Docker container/volume 삭제
- `.env`
- seed
- 인증
- 기존 API route path/response body
- 실제 write 로직/Write Guard
- Preview/Apply request body
- 새 Alembic revision 생성
- DB 생성/삭제/복원

```txt
python scripts/setup_dev_db.py --reset
docker compose down -v
python -m alembic revision --autogenerate
python -m alembic upgrade head
python -m alembic downgrade
python -m alembic stamp head
createdb
dropdb
pg_restore
```

========================
Contract/검증 원칙
========================

새 Contract가 필요할 때는 실제 현재 환경 결과를 먼저 수집하고, 환경 차이를 확인한 뒤 등록하세요.
Frontend/backend 목록, 반환 객체, parity, Admin ReadOnly 검사를 누락하지 마세요.

코드나 구조를 건드렸다면 최소 확인:

- 관련 전용 smoke
- JS 문법 검사
- `python -m compileall -q backend/app backend/scripts backend/alembic tools`
- `bash tools/run_smoke_core.sh`
- Vue 변경 시 `npm ci`와 `npm run build`
- ZIP 무결성 및 제외 파일 검사

작업 후에는 다음 5개를 포함해 답변하세요.

1. 이번에 한 일
2. 검증 완료한 것
3. 서버 재실행 명령 — 실행 위치와 `.venv` 상태 포함
4. git 명령 — 프로젝트 루트에서 한 줄
5. 다음 추천 단계

코드 또는 문서를 변경했다면 새 ZIP도 같이 만들어주세요.
