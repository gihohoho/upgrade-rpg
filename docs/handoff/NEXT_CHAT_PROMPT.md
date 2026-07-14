기호의 Upgrade RPG 프로젝트를 이어서 진행합니다.

이번에 첨부하는 최신 ZIP `rpg_v304_postgres_source_baseline_stamp_final_guard_ready.zip`을 반드시 기준으로 작업해주세요.

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

- 최신 작업: `v304.postgres-source-baseline-stamp-final-guard`
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
application tables: 22
application rows: 748
schema: structurally-equivalent / differences=0
alembic_version: 없음
current revision: 없음
classification: existing-schema-without-alembic-baseline
source stamp actual execution: 미승인
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
public tables/rows: 23/749
application tables/rows: 22/748
current revision: v295_initial_schema
v302 stamp: 사용자 승인 후 실제 실행 완료
v303 post-check: restore-rehearsal-stamp-current-state-verified
v302 execution report: verified
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
v301 source baseline stamp preflight: 통과
v302 restore rehearsal pre-stamp inspect: 통과
v302 restore rehearsal stamp: 통과
v303 restore rehearsal post-check: 통과
v303 result: restore-rehearsal-stamp-current-state-verified
v302 execution report: verified
```

승인 application digest:

```txt
schema digest: 7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921
data digest: ecb19e57283dc6b780426339bfc46f2bac14da63a618249808f30132508f9244
```

필수 로컬 증거는 Git/전달 ZIP/채팅에 포함하지 않습니다.

```txt
local-backups/
local-review-artifacts/alembic/v295_initial_schema.upgrade-v298.json
local-review-artifacts/alembic/v295_initial_schema.downgrade-v299.json
local-review-artifacts/alembic/v295_initial_schema.roundtrip-upgrade-v300.json
local-review-artifacts/alembic/v295_initial_schema.restore-rehearsal-stamp-v302.json
```

========================
v304 source final guard
========================

추가 파일:

```txt
tools/stamp_postgres_source_database.py
tools/smoke/backend/smoke_postgres_source_baseline_stamp_guard.py
docs/current/POSTGRES_SOURCE_BASELINE_STAMP_FINAL_GUARD.md
```

`--inspect`는 다음을 읽기 전용으로 확인합니다.

- exact target `rpg_game`
- exact revision/SHA-256
- exact backup/SHA-256와 로컬 evidence
- source 22/748/no Alembic/differences=0
- source application schema/data digest
- rehearsal 23/749/current revision/v302 report verified
- migration DB verified v300 endpoint
- source/rehearsal application integrity equality

실제 source stamp 경로는 존재하지만, 사용자 별도 승인 전에는 실행하지 않습니다.
향후 실행은 target, revision, backup SHA-256, rehearsal result 네 confirmation이 모두 정확히 일치해야 합니다.

========================
다음 첫 작업 — 읽기 전용 v304 source final inspect
========================

먼저 사용자 PC에서 아래 명령의 실제 결과를 수집하세요.

실행 위치: `backend` 폴더
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/stamp_postgres_source_database.py --inspect
```

정상 기대 핵심:

```txt
lifecycle state: pre-stamp
exact target DB: rpg_game
exact revision: v295_initial_schema
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
source public tables/rows: 22/748
source current revision: []
source application tables/rows: 22/748
source application schema digest: 7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921
source application data digest: ecb19e57283dc6b780426339bfc46f2bac14da63a618249808f30132508f9244
backup SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
rehearsal post-stamp: verified / 23/749
migration test current revision: ['v295_initial_schema']
source/rehearsal application digests identical: yes
result: ready-for-separate-source-baseline-stamp-execution-approval
```

통과해도 source `--execute`를 바로 실행하지 마세요.
실제 source stamp는 사용자 별도 명시 승인 후에만 진행합니다.

========================
다음 단계 안전 순서
========================

1. v304 source final inspect 실제 결과 확인
2. exact target/revision/backup/rehearsal report/digests 재확인
3. source stamp 실제 실행 여부 별도 명시 승인
4. 승인 후 exact confirmation flags를 포함한 실행 명령 1회 제공
5. source application schema/data digest 보존 확인
6. source `alembic_version` 1 table/1 row와 revision만 추가 확인
7. rehearsal/migration DB 무변경 확인
8. 실패 시 자동 재시도 금지, read-only inspect 먼저 실행
9. source post-check와 v304 execution report 검증
10. Alembic baseline 운영 완료 상태 문서화

========================
절대 변경/실행 금지
========================

사용자 별도 명시 승인 전에는 다음을 변경하거나 실행하지 마세요.

- 원본 source `rpg_game` stamp actual execution
- 원본 DB upgrade/downgrade
- restore rehearsal stamp 재실행
- migration test DB 추가 upgrade/downgrade/stamp
- Docker container/volume 삭제
- `.env`
- seed
- 인증
- 기존 API route path/response body
- 실제 write 로직/Write Guard
- Preview/Apply request body
- 새 Alembic revision 생성
- DB 생성/삭제/복원
- 게임 콘텐츠/밸런스 변경

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
