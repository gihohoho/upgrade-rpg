# PostgreSQL v295 기준선 역사

> 완료된 상세 문서를 검색 가능한 한 파일로 통합한 읽기 전용 역사입니다.
> 현재 판단에는 `docs/current/`와 `docs/generated/`를 사용하세요.
> 원본 파일은 Git commit `270d57bd234ede18cee7168f4b5da36b1a08df18` 이전 이력에서 복원할 수 있습니다.

---

## 원본: `docs/current/POSTGRES_INITIAL_ALEMBIC_REVISION_CREATION.md`

# PostgreSQL 최초 Alembic revision `op.f` parser 복구 — v297

## 실제 원인

v296은 기존 빈 `alembic_version` placeholder를 정상적으로 재사용해 revision 파일을 생성했습니다. 하지만 자동 검토 함수가 revision 함수 내부의 모든 `op.*` 호출을 migration operation으로 수집하면서, 아래와 같은 nested naming helper까지 실제 작업으로 오판했습니다.

```python
op.create_index(op.f("ix_example"), "example", ["value"], unique=False)
op.drop_index(op.f("ix_example"), table_name="example")
```

`op.f(...)`는 constraint/index 이름이 naming convention 처리를 이미 마쳤음을 나타내는 Alembic helper입니다. 테이블이나 데이터를 변경하는 operation이 아닙니다.

사용자 실제 결과:

```txt
result: blocked-or-failed
reason: unexpected Alembic operations: upgrade=['f'], downgrade=['f']
```

실패 처리에서 생성된 revision Python 파일과 review artifact는 자동 정리됐습니다. DB에는 기존 `alembic_version` 1 table / 0 rows / recorded revision 없음 상태만 유지됩니다.

## v297 수정

```txt
ALEMBIC_NON_OPERATION_HELPERS = {'f'}
```

- nested `op.f(...)`를 operation count와 allowlist 검사에서 제외
- `op.create_table`, `op.create_index`, `op.drop_index`, `op.drop_table`은 계속 실제 operation으로 검사
- `op.execute`, `bulk_insert`, destructive upgrade, constructive downgrade는 계속 차단
- smoke fake revision에도 실제 Alembic 형태의 nested `op.f(...)`를 넣어 재현 및 회귀 검증
- operation 결과에 `f`가 다시 나타나면 smoke 실패

## 고정 경계

```txt
source DB: rpg_game (read-only)
rehearsal DB: rpg_game_restore_rehearsal_v290 (read-only)
revision workspace: rpg_game_migration_empty_v290
revision ID: v295_initial_schema
```

- `backend/.env` 미수정
- child process `DATABASE_URL`만 target override
- 기존 empty `alembic_version` placeholder 재사용
- revision row 기록 없음
- application table mutation 없음
- upgrade/downgrade/stamp/createdb/dropdb/pg_restore 없음

## 실행

실행 위치: `backend` 폴더
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/create_postgres_initial_alembic_revision.py --inspect-workspace && python tools/create_postgres_initial_alembic_revision.py --execute
```

## 성공 기대값

```txt
result: initial-alembic-revision-created-and-automatically-reviewed
revision ID: v295_initial_schema
upgrade create_table: 22
downgrade drop_table: 22
reviewed tables/columns: 22 / 209
migration DB tables before/after: 1 / 1
migration workspace before/after: empty-alembic-version-placeholder / empty-alembic-version-placeholder
migration DB alembic_version before/after: True / True
alembic_version rows before/after: 0 / 0
```

review bundle:

```txt
local-review-artifacts/alembic/v295_initial_schema_review_bundle.zip
```

이 bundle 수동 검토 전에는 generated revision commit 또는 `upgrade head`를 실행하지 않습니다.

## v297 실제 성공 결과

사용자 환경에서 revision 생성과 자동 검토가 성공했습니다.

```txt
revision ID: v295_initial_schema
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
upgrade create_table: 22
upgrade create_index: 42
downgrade drop_table: 22
reviewed tables/columns: 22 / 209
migration DB tables before/after: 1 / 1
alembic_version rows before/after: 0 / 0
```

v298에서 review bundle의 exact revision을 수동 교차 검토했고 통과했습니다. 이후 기준은 아래 문서입니다.

```txt
docs/current/POSTGRES_INITIAL_ALEMBIC_REVISION_MANUAL_REVIEW.md
docs/current/POSTGRES_MIGRATION_TEST_UPGRADE.md
```

---

## 원본: `docs/current/POSTGRES_MIGRATION_TEST_DB_CREATION.md`

# PostgreSQL 빈 migration test DB 생성 — v294

## 목적

최초 Alembic revision을 원본 `rpg_game`이나 복원 리허설 DB에서 실행하지 않고, 완전히 분리된 빈 DB에서 검증하기 위한 준비 단계입니다.

```txt
source DB: rpg_game
verified restore DB: rpg_game_restore_rehearsal_v290
empty migration test DB: rpg_game_migration_empty_v290
```

## 선행 완료 상태

- source: 22 tables / 748 rows / schema differences=0
- verified backup SHA-256 확인 완료
- restore rehearsal: 22 tables / 748 rows / schema differences=0
- source before/after 동일
- restore report 생성 완료

## v294 도구

```txt
tools/create_postgres_migration_test_database.py
```

실행 전 gate:

1. schema/preflight가 계속 정상인지 확인
2. exact backup 파일명과 SHA-256 재확인
3. v293 restore report 성공 결과 재확인
4. source live table 목록과 table별 row counts 재확인
5. restore rehearsal live 22 tables / 748 rows / differences=0 재확인
6. `rpg_game_migration_empty_v290`가 존재하지 않는지 확인

생성 방식:

```txt
createdb
owner: rpg_user
template: template0
encoding/collation/locale: source와 동일
```

생성 후 검증:

- migration test DB public tables 0개
- total rows 0개
- `alembic_version` 없음
- source 22 tables / 748 rows 유지
- restore rehearsal 22 tables / 748 rows 유지

## 실행 명령

실행 위치: `backend` 폴더
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/create_postgres_migration_test_database.py --execute
```

## 성공 기대값

```txt
result: migration-test-database-created-empty-and-verified
migration test DB: rpg_game_migration_empty_v290
target public tables: 0
target total rows: 0
target alembic_version: absent
source tables/rows before/after: 22/748 -> 22/748
rehearsal tables/rows before/after: 22/748 -> 22/748
```


## 사용자 PC 실제 완료 결과

```txt
result: migration-test-database-created-empty-and-verified
migration test DB: rpg_game_migration_empty_v290
target public tables: 0
target total rows: 0
target alembic_version: absent
source tables/rows before/after: 22/748 -> 22/748
rehearsal tables/rows before/after: 22/748 -> 22/748
```

이 DB는 v295 최초 revision autogenerate의 유일한 target으로 보존합니다.

## 여전히 금지

- raw `python -m alembic revision --autogenerate` 직접 실행
- `python -m alembic upgrade head`
- `python -m alembic downgrade`
- `python -m alembic stamp head`
- `dropdb`
- source/rehearsal DB write
- `.env` 변경
- Docker container/volume 변경

빈 DB 생성 성공이 확인되었으며, v295 guarded 도구로 최초 revision 파일 생성·자동 검토를 진행합니다. 수동 검토 전에는 upgrade를 실행하지 않습니다.

---

## 원본: `docs/current/POSTGRES_MIGRATION_TEST_DOWNGRADE.md`

# PostgreSQL isolated migration test DB downgrade — v299

## 승인된 대상

```txt
rpg_game_migration_empty_v290
```

## 시작 상태

```txt
revision: v295_initial_schema
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
public tables: 23
model tables: 22
alembic_version rows: 1
schema: structurally-equivalent
differences: 0
model table rows: 모두 0
```

v298 upgrade 검증 보고서도 다음 위치에서 확인합니다.

```txt
local-review-artifacts/alembic/v295_initial_schema.upgrade-v298.json
```

## 허용 명령

```txt
python -m alembic --config alembic.ini downgrade base
```

자식 프로세스의 `DATABASE_URL`만 `rpg_game_migration_empty_v290`으로 override합니다. `backend/.env`는 수정하지 않습니다.

## 실행 전 gate

- exact revision 파일과 SHA-256 일치
- 수동 검토 결과 일치
- v298 upgrade report 결과 일치
- target current revision이 정확히 `v295_initial_schema`
- target schema differences=0
- source `rpg_game`: 22 tables / 748 rows 유지
- rehearsal DB: 22 tables / 748 rows / differences=0 유지

## 성공 조건

```txt
public tables: ['alembic_version']
application tables remaining: 0
alembic_version rows: 0
current revisions: []
total rows: 0
schema classification: review-required
differences: 22
source/rehearsal: 작업 전후 동일
```

`differences=22`는 오류가 아니라, base 상태에서 모델 테이블 22개가 아직 없다는 뜻입니다.

## 생성되는 로컬 보고서

```txt
local-review-artifacts/alembic/v295_initial_schema.downgrade-v299.json
```

이 파일은 Git/전달 ZIP/채팅에서 제외합니다.

## 아직 금지

```txt
source DB upgrade/stamp
migration DB 자동 재-upgrade
createdb/dropdb
pg_restore
.env/Docker volume 변경
seed/인증/API write 변경
```


## 사용자 PC 실제 실행 결과 — 2026-07-14

```txt
result: migration-test-database-downgraded-to-base-and-verified
target public tables after downgrade: 1
target application tables remaining: 0
target total rows: 0
target current revisions: []
expected empty-workspace schema: review-required / differences=22
source tables/rows preserved: 22/748
rehearsal tables/rows preserved: 22/748
```

다음 기준 문서: `docs/current/POSTGRES_MIGRATION_TEST_ROUNDTRIP.md`

---

## 원본: `docs/current/POSTGRES_MIGRATION_TEST_ROUNDTRIP.md`

# PostgreSQL isolated migration round-trip re-upgrade — v300 completed

## 실행 전 전제 상태

```txt
v298 first upgrade: migration-test-database-upgraded-and-verified
v299 downgrade: migration-test-database-downgraded-to-base-and-verified
current target: rpg_game_migration_empty_v290
public tables: ['alembic_version']
recorded revisions: []
total rows: 0
differences: 22
```

## 허용 작업

대상 DB에 exact command 한 번만 허용합니다.

```bash
python -m alembic --config alembic.ini upgrade head
```

실제 사용자 명령은 프로젝트 루트에서 다음 도구를 사용합니다.

```bash
python tools/reupgrade_postgres_migration_test_database.py --inspect && python tools/reupgrade_postgres_migration_test_database.py --execute
```

## 필수 로컬 증거

```txt
local-review-artifacts/alembic/v295_initial_schema.upgrade-v298.json
local-review-artifacts/alembic/v295_initial_schema.downgrade-v299.json
```

둘 중 하나라도 없거나 revision/SHA/result가 다르면 실행하지 않습니다.

## 성공 조건

```txt
result: migration-test-database-roundtrip-upgraded-and-verified
public tables: 23
model tables: 22
total rows: 1
current revision: ['v295_initial_schema']
schema: structurally-equivalent / differences=0
first/second upgrade signatures: identical
source/rehearsal preserved: 22/748
```

비교 signature에는 DB/user, public table 목록, table별 row count, total rows, Alembic revision, schema classification, difference count가 포함됩니다.

## 금지

- 이 단계에서 downgrade 재실행
- source/rehearsal DB write
- stamp/revision 생성
- createdb/dropdb/pg_restore
- `.env` 또는 Docker volume 변경
- 자동 retry

성공 보고서:

```txt
local-review-artifacts/alembic/v295_initial_schema.roundtrip-upgrade-v300.json
```

이 로컬 보고서는 Git/전달 ZIP/채팅에 포함하지 않습니다.


## 사용자 PC 실제 완료 결과

```txt
result: migration-test-database-roundtrip-upgraded-and-verified
public tables: 23
model tables: 22
total rows: 1
current revision: ['v295_initial_schema']
schema: structurally-equivalent / differences=0
first/second upgrade signatures: identical
round-trip: upgrade -> downgrade base -> upgrade verified
source/rehearsal preserved: 22/748
```

성공 보고서는 `local-review-artifacts/`에만 보존하며 Git/전달 ZIP/채팅에 포함하지 않습니다.

---

## 원본: `docs/current/POSTGRES_MIGRATION_TEST_UPGRADE.md`

# PostgreSQL isolated migration test DB upgrade — v298

## 대상

```txt
rpg_game_migration_empty_v290
```

## exact revision

```txt
revision: v295_initial_schema
SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
manual review: passed
```

## 실행 전 필수 상태

- source `rpg_game`: 22 tables / 748 rows / no Alembic baseline
- rehearsal DB: 22 tables / 748 rows / differences=0
- migration DB: only `alembic_version`, 0 rows, recorded revisions 없음
- revision file exact SHA 일치
- manual review manifest 결론: `approved-for-isolated-empty-migration-database-upgrade-only`

## 허용 명령

```txt
python -m alembic --config alembic.ini upgrade head
```

자식 프로세스 `DATABASE_URL`만 `rpg_game_migration_empty_v290`으로 override합니다. `backend/.env`는 수정하지 않습니다.

## 성공 조건

```txt
public tables: 23
model tables: 22
alembic_version rows: 1
current revision: v295_initial_schema
model table rows: 모두 0
schema: structurally-equivalent
differences: 0
source/rehearsal: 작업 전후 동일
```

## 아직 금지

```txt
downgrade
stamp
source DB upgrade
createdb/dropdb
pg_restore
.env/Docker volume 변경
```

## 사용자 PC 실제 실행 결과 — 2026-07-14

```txt
result: migration-test-database-upgraded-and-verified
target public tables: 23
target model tables: 22
target total rows including Alembic control row: 1
target current revision: ['v295_initial_schema']
target schema: structurally-equivalent / differences=0
source tables/rows preserved: 22/748
rehearsal tables/rows preserved: 22/748
```

다음 기준 문서: `docs/current/POSTGRES_MIGRATION_TEST_DOWNGRADE.md`

---

## 원본: `docs/current/POSTGRES_NEXT_REVISION_READONLY_PLAN.md`

# PostgreSQL next revision read-only plan — v306

## 현재 결론

v305에서 최초 baseline 완료 상태가 실제 통과했습니다. v306은 새 revision을 만들지 않고 Alembic metadata candidate diff가 존재하는지만 읽기 전용으로 확인합니다.

## v306 안전 순서

1. v305 completion state 재확인
2. Alembic graph single base/single head 확인
3. approved model source snapshot 확인
4. canonical SQLAlchemy/PostgreSQL schema differences=0 확인
5. PostgreSQL read-only transaction과 SQL write guard 활성화
6. Alembic `compare_metadata()`로 type/default/nullable/index/constraint 후보 수집
7. integer PK sequence ownership과 unowned sequence 확인
8. 후보 0개면 새 revision을 만들지 않음
9. 후보가 있으면 변경 의도 검토 단계에서 정지
10. autogenerate, revision 생성, upgrade/downgrade는 별도 승인

## v306에서 실행하지 않는 명령

```txt
python -m alembic revision --autogenerate
python -m alembic revision
python -m alembic upgrade head
python -m alembic downgrade
python -m alembic stamp head
createdb
dropdb
pg_restore
docker compose down -v
```

## 결과별 다음 경계

### 차이 0개

```txt
next-revision-not-required-current-schema-equivalent
```

현재 single baseline revision을 유지합니다. schema 변경 요구가 생기기 전까지 migration 작업을 멈춥니다.

### 후보 차이 있음

```txt
next-revision-review-required-schema-differences-detected
```

자동 생성하지 않습니다. 각 후보가 의도한 변경인지, 기존 748개 row에 어떤 영향을 주는지, schema migration과 data migration을 분리해야 하는지부터 검토합니다.

---

## 원본: `docs/current/POSTGRES_RESTORE_REHEARSAL_DB_CREATION.md`

# PostgreSQL restore rehearsal database creation — v292

## 목적

v292는 검증된 v291 backup을 실제 원본 DB와 완전히 분리된 빈 PostgreSQL DB에 복원하기 전, **빈 리허설 DB 하나만 안전하게 만드는 단계**입니다.

승인된 target DB:

```txt
rpg_game_restore_rehearsal_v290
```

원본 DB:

```txt
rpg_game
```

원본 DB와 target DB 이름은 고정되어 있으며 서로 바꿀 수 없습니다.

## 사용자 PC에서 이미 확인된 backup

```txt
backup: local-backups/postgres/rpg_game_20260714_130403_KST_v290.custom.dump
size: 126.60 KB
SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
source tables: 22
source total rows: 748
TOC table definitions/data entries: 22 / 22
```

backup과 `local-backups/` 폴더는 민감정보 보존 대상이므로 Git, 전달 ZIP, 채팅에 포함하지 않습니다.

## 실행 도구

```txt
tools/create_postgres_restore_rehearsal_database.py
```

이 도구는 다음 순서로 실행됩니다.

1. schema equivalence와 backup/restore preflight gate 재확인
2. 원본 `rpg_game`이 22 tables / 748 rows / Alembic 이력 없음인지 확인
3. 사용자가 승인한 정확한 backup filename/manifest와 실제 dump의 SHA-256 재계산·비교
4. PostgreSQL catalog에서 target DB 존재 여부 확인
5. target이 이미 있으면 즉시 중단
6. 없을 때만 `createdb`로 정확히 한 번 생성
7. source와 같은 encoding/collation/locale provider 사용
8. owner `rpg_user`, template `template0` 고정
9. target public table 0개와 `alembic_version` 없음 확인
10. 원본 DB가 여전히 22 tables / 748 rows인지 다시 확인

## 실행 명령

먼저 가상환경 활성화:

실행 위치: `backend` 폴더
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/create_postgres_restore_rehearsal_database.py --execute
```

## 성공 기준

```txt
result: restore-rehearsal-database-created-empty-and-verified
target DB: rpg_game_restore_rehearsal_v290
target public tables: 0
target alembic_version: absent
source tables before/after: 22 / 22
source rows before/after: 748 / 748
```

## 이번 단계에서 실행하지 않는 것

- `pg_restore`
- target DB table/data 생성
- `dropdb`
- 원본 DB schema/data 변경
- `.env` 변경
- Docker container/volume 변경
- Alembic revision/upgrade/downgrade/stamp
- API/auth/write/game content 변경

## 실패 시 원칙

- target DB가 이미 있으면 생성·복원·삭제 모두 중단합니다.
- 생성 후 검증이 예상과 다르면 자동 `dropdb`를 하지 않습니다.
- 오류 결과를 먼저 분석한 뒤 별도 승인 범위를 정합니다.

## 다음 승인 경계

빈 target DB 생성과 검증이 성공한 뒤에만, verified dump를 `pg_restore`로 target에 쓰는 작업을 별도로 승인받습니다.


## 사용자 PC 실제 완료 결과

```txt
result: restore-rehearsal-database-created-empty-and-verified
target public tables: 0
target alembic_version: absent
source tables before/after: 22 / 22
source rows before/after: 748 / 748
```

다음 승인 단계는 `tools/restore_postgres_rehearsal_database.py --execute`이며 상세 경계는 `POSTGRES_RESTORE_REHEARSAL.md`를 기준으로 합니다.

---

## 원본: `docs/current/POSTGRES_RESTORE_REHEARSAL_STAMP_GUARD.md`

# PostgreSQL restore rehearsal baseline stamp post-check — v303

## 현재 상황

사용자 PC에서 다음 단계가 실제로 진행됐습니다.

```txt
v301 source baseline stamp preflight: passed
v302 rehearsal --inspect: passed
v302 rehearsal stamp execution: user approved and executed
```

stamp 전 실제 승인 digest:

```txt
application tables/rows: 22 / 748
schema digest: 7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921
data digest: ecb19e57283dc6b780426339bfc46f2bac14da63a618249808f30132508f9244
```

그 직후 기존 v302 `--inspect`는 다음 오류를 냈습니다.

```txt
SourceBaselinePreflightError: rehearsal table list differs from approved snapshot
```

이 오류는 stamp를 다시 해야 한다는 뜻이 아닙니다. v302 `--inspect`가 stamp 이후에도
`alembic_version`이 없는 22-table 사전 상태만 허용했던 검사기 버그입니다.

## v303 수정 사항

`tools/stamp_postgres_restore_rehearsal_database.py --inspect`가 rehearsal DB의
현재 상태를 먼저 읽고 다음 두 상태를 구분합니다.

```txt
pre-stamp:
  22 public tables / 748 rows / no alembic_version

post-stamp:
  23 public tables / 749 rows
  application tables/rows: 22 / 748
  alembic_version: 1 table / 1 row
  current revision: v295_initial_schema
```

post-stamp에서는 다음을 모두 읽기 전용으로 검증합니다.

- exact target: `rpg_game_restore_rehearsal_v290`
- exact revision: `v295_initial_schema`
- revision SHA-256
- 22개 application table / 748개 application row 유지
- stamp 전 승인 schema/data digest 유지
- 원본 `rpg_game`이 22/748, no Alembic 상태로 유지
- migration test DB가 검증된 v300 endpoint와 일치
- 로컬 v302 실행 보고서가 있으면 실행 전후 signature와 현재 상태 일치

## 읽기 전용 post-check

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

이 명령은 다음을 실행하지 않습니다.

```txt
stamp 재실행
rollback
upgrade/downgrade
DB create/drop/restore
source DB mutation
application row write
.env/Docker 변경
```

## 정상 기대 결과

v302 실행 보고서가 정상 생성돼 있으면:

```txt
lifecycle state: post-stamp
public tables/rows: 23/749
current revision: ['v295_initial_schema']
application tables/rows: 22/748
approved pre-stamp application digests preserved: yes
source DB current state preserved: yes
migration test DB current state preserved: yes
v302 execution report: verified
result: restore-rehearsal-stamp-current-state-verified
```

stamp는 성공했지만 실행 보고서 저장 전에 후속 검사가 끊긴 경우에도 current DB 상태가
정상이라면 다음처럼 분류합니다.

```txt
v302 execution report: missing
result: restore-rehearsal-stamp-current-state-verified-report-missing
```

이 경우에도 stamp를 다시 실행하지 않습니다. 별도의 로컬 evidence 복구 단계만 검토합니다.

## 사용자 PC 실제 v303 결과

```txt
lifecycle state: post-stamp
public tables/rows: 23/749
current revision: ['v295_initial_schema']
application tables/rows: 22/748
approved pre-stamp application digests preserved: yes
source DB current state preserved: yes
migration test DB current state preserved: yes
v302 execution report: verified
result: restore-rehearsal-stamp-current-state-verified
```

이 결과로 restore rehearsal stamp 단계는 완료됐으며 v304 source final guard 준비 단계로 이동했습니다.

## 계속 금지

- v302 `--execute` 재실행
- 원본 `rpg_game` stamp/upgrade/downgrade
- migration test DB 추가 변경
- 새 Alembic revision
- DB create/drop/restore
- Docker volume 삭제
- `.env`, seed, 인증, API route/body, Write Guard 변경

---

## 원본: `docs/current/POSTGRES_RUNTIME_ENGINE_BINDING_INSPECTOR_FIX.md`

# PostgreSQL runtime engine binding inspector fix — v309

## 문제

v308에서 SQLAlchemy pool 옵션을 명시하면서 `create_async_engine()` 호출이 여러 줄로 정리되었습니다. 실제 runtime은 계속 첫 번째 인자로 `settings.database_url`을 사용했지만, v307 readiness 검사기는 아래처럼 한 줄 문자열만 찾았습니다.

```txt
create_async_engine(settings.database_url
```

따라서 정상적인 여러 줄 호출을 `runtime engine bypasses settings.database_url`로 오판했습니다. DB 연결, `.env`, Docker, Alembic 또는 application data 문제는 아니었습니다.

## v309 수정

- Python AST로 `create_async_engine()` 호출을 분석합니다.
- 첫 positional argument 또는 `url=`/`database_url=` keyword가 정확히 `settings.database_url`인지 확인합니다.
- 줄바꿈, 들여쓰기, pool keyword 추가 여부와 무관하게 판정합니다.
- literal URL이나 `settings.audit_database_url` 같은 다른 설정은 허용하지 않습니다.
- 기존 결과 계약 `runtime-config-hardening-verified-local-runtime-preserved`는 유지합니다.

## 안전 경계

이 수정은 정적 검사기와 smoke만 변경합니다.

```txt
DB schema/data 변경: 없음
backend/.env 변경: 없음
Docker 실행/변경: 없음
Alembic revision/stamp/upgrade/downgrade: 없음
FastAPI route/response body 변경: 없음
runtime engine/pool 설정 변경: 없음
```

## 재검증 명령

```bash
python tools/check_runtime_config_hardening.py --strict --require-health
```

정상 결과:

```txt
result: runtime-config-hardening-verified-local-runtime-preserved
next safe stage: separate-production-secrets-tls-and-container-validation
```

---

## 원본: `docs/current/POSTGRES_SOURCE_BASELINE_STAMP_FINAL_GUARD.md`

# PostgreSQL source baseline stamp final guard and post-check — v304

## 목적과 완료 상태

v304는 원본 PostgreSQL DB `rpg_game`의 baseline stamp를 exact target/revision/backup/rehearsal 경계로 제한하고, 실행 전후 application schema/data를 비교하기 위해 준비됐습니다.

사용자 별도 승인 후 source baseline stamp가 정확히 한 번 실행됐고, 읽기 전용 post-check와 로컬 execution report 검증까지 완료됐습니다.

## 정확히 고정된 경계

```txt
target DB: rpg_game
owner/user: rpg_user
revision: v295_initial_schema
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
backup SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
required rehearsal result: restore-rehearsal-stamp-current-state-verified
```

승인 application digest:

```txt
schema: 7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921
data: ecb19e57283dc6b780426339bfc46f2bac14da63a618249808f30132508f9244
```

## 실행 전에 검증했던 것

- `.env`의 source DB가 정확히 `rpg_game`인지
- source가 22 application tables / 748 rows / no Alembic인지
- source schema differences가 0인지
- verified backup, revision, manual review가 유지되는지
- rehearsal이 23/749, `v295_initial_schema`, v302 report verified인지
- migration DB가 v300 왕복 endpoint인지
- source/rehearsal application integrity가 정확히 같은지

사전 성공 결과:

```txt
result: ready-for-separate-source-baseline-stamp-execution-approval
```

## 실제 실행에 사용된 승인 경계

```txt
--confirm-target rpg_game
--confirm-revision v295_initial_schema
--confirm-backup-sha256 b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
--confirm-rehearsal-result restore-rehearsal-stamp-current-state-verified
```

허용된 변화는 다음뿐이었습니다.

```txt
source application tables/rows: 22/748 그대로
source application schema/data digest: 그대로
new control table: alembic_version 1개
new control row: v295_initial_schema 1개
public tables/rows after: 23/749
restore rehearsal DB: 무변경
migration DB: 무변경
```

## 사용자 PC 실제 post-check 결과

```txt
lifecycle state: post-stamp
source public tables/rows: 23/749
source application tables/rows: 22/748
source current revision: ['v295_initial_schema']
source/rehearsal application digests identical: yes
v304 execution report: verified
result: source-baseline-stamp-current-state-verified
```

기존 application 22개 table / 748 rows와 schema/data digest는 보존됐습니다.

## 현재 사용 방법

읽기 전용 post-check는 여전히 사용할 수 있습니다.

실행 위치: 프로젝트 루트
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/stamp_postgres_source_database.py --inspect
```

하지만 source stamp는 완료됐으므로 `--execute`를 다시 실행하지 않습니다.

현재 baseline 전체 완료 상태는 v305 도구로 확인합니다.

```bash
python tools/check_postgres_baseline_completion_state.py --strict
```

## 계속 금지

- source/rehearsal stamp 재실행
- 새 revision/autogenerate
- source/rehearsal/migration upgrade/downgrade
- DB create/drop/restore
- `.env`, Docker volume, seed, 인증, API/write 변경
- 게임 콘텐츠/밸런스 변경

---

## 원본: `docs/current/POSTGRES_SOURCE_BASELINE_STAMP_PREFLIGHT.md`

# PostgreSQL source baseline stamp preflight — v301

## 목적

기존 데이터가 있는 원본 `rpg_game`에 Alembic baseline을 기록하기 전에, 지금까지의 backup/restore/revision/왕복 migration 증거와 현재 DB 상태를 다시 읽기 전용으로 확인합니다.

이 단계에서는 `stamp head`를 실행하지 않습니다.

## 현재 실제 전제

```txt
source rpg_game: 22 tables / 748 rows / differences=0 / alembic_version 없음
restore rehearsal: 22 tables / 748 rows / differences=0 / alembic_version 없음
migration test: 23 public tables / current v295_initial_schema / differences=0
round trip: upgrade -> downgrade base -> upgrade / signatures identical
```

## 실행

실행 위치: 프로젝트 루트
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_postgres_source_baseline_stamp_preflight.py --strict
```

## 읽기 전용 확인 항목

- exact verified backup 파일명과 SHA-256
- source snapshot 22 tables / 748 rows
- restore rehearsal 22 tables / 748 rows / differences=0
- reviewed revision `v295_initial_schema`와 exact SHA-256
- manual/automated revision review 통과
- v300 round-trip 보고서 성공 및 first/second signature 동일
- 현재 migration DB가 revision head와 differences=0 상태인지
- 현재 source가 differences=0이고 `alembic_version`이 없는지

## 성공 결과

```txt
result: ready-for-separate-restore-rehearsal-stamp-approval
```

이 결과는 원본 stamp 승인이 아닙니다. 다음 mutation은 source 복사본인 `rpg_game_restore_rehearsal_v290`에서만 별도 승인 후 stamp rehearsal로 진행합니다.


## 사용자 PC 실제 결과

2026-07-14 사용자 PC에서 `--strict`가 실제 통과했습니다.

```txt
source tables/rows: 22/748
source alembic_version: False
source schema: structurally-equivalent / differences=0
reviewed revision: v295_initial_schema
migration test current revision: ['v295_initial_schema']
result: ready-for-separate-restore-rehearsal-stamp-approval
```

이 결과를 근거로 v302 restore rehearsal stamp guard 준비 단계로 이동했습니다. 원본 source stamp는 승인되지 않았습니다.

## 다음 안전 단계

1. restore rehearsal DB가 현재 22 tables / 748 rows / no Alembic인지 재확인
2. exact target URL을 restore rehearsal DB로 고정
3. exact command를 `alembic stamp head` 하나로 제한
4. 전후 schema와 application row counts가 동일한지 확인
5. `alembic_version` table 1개와 revision row 1개만 추가됐는지 확인
6. source와 migration DB 무변경 확인
7. rehearsal stamp 통과 후에도 source stamp는 다시 별도 승인

## 금지

```txt
source rpg_game stamp/upgrade/downgrade
restore rehearsal stamp 사용자 승인 전 실행
새 revision 생성
DB create/drop/restore
.env/Docker 변경
```

---

## 원본: `docs/archive/postgres-baseline/POSTGRES_INITIAL_ALEMBIC_REVISION_CREATION.md`

# PostgreSQL 최초 Alembic revision `op.f` parser 복구 — v297

## 실제 원인

v296은 기존 빈 `alembic_version` placeholder를 정상적으로 재사용해 revision 파일을 생성했습니다. 하지만 자동 검토 함수가 revision 함수 내부의 모든 `op.*` 호출을 migration operation으로 수집하면서, 아래와 같은 nested naming helper까지 실제 작업으로 오판했습니다.

```python
op.create_index(op.f("ix_example"), "example", ["value"], unique=False)
op.drop_index(op.f("ix_example"), table_name="example")
```

`op.f(...)`는 constraint/index 이름이 naming convention 처리를 이미 마쳤음을 나타내는 Alembic helper입니다. 테이블이나 데이터를 변경하는 operation이 아닙니다.

사용자 실제 결과:

```txt
result: blocked-or-failed
reason: unexpected Alembic operations: upgrade=['f'], downgrade=['f']
```

실패 처리에서 생성된 revision Python 파일과 review artifact는 자동 정리됐습니다. DB에는 기존 `alembic_version` 1 table / 0 rows / recorded revision 없음 상태만 유지됩니다.

## v297 수정

```txt
ALEMBIC_NON_OPERATION_HELPERS = {'f'}
```

- nested `op.f(...)`를 operation count와 allowlist 검사에서 제외
- `op.create_table`, `op.create_index`, `op.drop_index`, `op.drop_table`은 계속 실제 operation으로 검사
- `op.execute`, `bulk_insert`, destructive upgrade, constructive downgrade는 계속 차단
- smoke fake revision에도 실제 Alembic 형태의 nested `op.f(...)`를 넣어 재현 및 회귀 검증
- operation 결과에 `f`가 다시 나타나면 smoke 실패

## 고정 경계

```txt
source DB: rpg_game (read-only)
rehearsal DB: rpg_game_restore_rehearsal_v290 (read-only)
revision workspace: rpg_game_migration_empty_v290
revision ID: v295_initial_schema
```

- `backend/.env` 미수정
- child process `DATABASE_URL`만 target override
- 기존 empty `alembic_version` placeholder 재사용
- revision row 기록 없음
- application table mutation 없음
- upgrade/downgrade/stamp/createdb/dropdb/pg_restore 없음

## 실행

실행 위치: `backend` 폴더
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/create_postgres_initial_alembic_revision.py --inspect-workspace && python tools/create_postgres_initial_alembic_revision.py --execute
```

## 성공 기대값

```txt
result: initial-alembic-revision-created-and-automatically-reviewed
revision ID: v295_initial_schema
upgrade create_table: 22
downgrade drop_table: 22
reviewed tables/columns: 22 / 209
migration DB tables before/after: 1 / 1
migration workspace before/after: empty-alembic-version-placeholder / empty-alembic-version-placeholder
migration DB alembic_version before/after: True / True
alembic_version rows before/after: 0 / 0
```

review bundle:

```txt
local-review-artifacts/alembic/v295_initial_schema_review_bundle.zip
```

이 bundle 수동 검토 전에는 generated revision commit 또는 `upgrade head`를 실행하지 않습니다.

## v297 실제 성공 결과

사용자 환경에서 revision 생성과 자동 검토가 성공했습니다.

```txt
revision ID: v295_initial_schema
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
upgrade create_table: 22
upgrade create_index: 42
downgrade drop_table: 22
reviewed tables/columns: 22 / 209
migration DB tables before/after: 1 / 1
alembic_version rows before/after: 0 / 0
```

v298에서 review bundle의 exact revision을 수동 교차 검토했고 통과했습니다. 이후 기준은 아래 문서입니다.

```txt
docs/current/POSTGRES_INITIAL_ALEMBIC_REVISION_MANUAL_REVIEW.md
docs/archive/postgres-baseline/POSTGRES_MIGRATION_TEST_UPGRADE.md
```

---

## 원본: `docs/archive/postgres-baseline/POSTGRES_MIGRATION_TEST_UPGRADE.md`

# PostgreSQL isolated migration test DB upgrade — v298

## 대상

```txt
rpg_game_migration_empty_v290
```

## exact revision

```txt
revision: v295_initial_schema
SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
manual review: passed
```

## 실행 전 필수 상태

- source `rpg_game`: 22 tables / 748 rows / no Alembic baseline
- rehearsal DB: 22 tables / 748 rows / differences=0
- migration DB: only `alembic_version`, 0 rows, recorded revisions 없음
- revision file exact SHA 일치
- manual review manifest 결론: `approved-for-isolated-empty-migration-database-upgrade-only`

## 허용 명령

```txt
python -m alembic --config alembic.ini upgrade head
```

자식 프로세스 `DATABASE_URL`만 `rpg_game_migration_empty_v290`으로 override합니다. `backend/.env`는 수정하지 않습니다.

## 성공 조건

```txt
public tables: 23
model tables: 22
alembic_version rows: 1
current revision: v295_initial_schema
model table rows: 모두 0
schema: structurally-equivalent
differences: 0
source/rehearsal: 작업 전후 동일
```

## 아직 금지

```txt
downgrade
stamp
source DB upgrade
createdb/dropdb
pg_restore
.env/Docker volume 변경
```

## 사용자 PC 실제 실행 결과 — 2026-07-14

```txt
result: migration-test-database-upgraded-and-verified
target public tables: 23
target model tables: 22
target total rows including Alembic control row: 1
target current revision: ['v295_initial_schema']
target schema: structurally-equivalent / differences=0
source tables/rows preserved: 22/748
rehearsal tables/rows preserved: 22/748
```

다음 기준 문서: `docs/archive/postgres-baseline/POSTGRES_MIGRATION_TEST_DOWNGRADE.md`

---

## 원본: `docs/archive/postgres-baseline/README.md`

# PostgreSQL baseline archive

v282~v304 PostgreSQL/Alembic 최초 baseline의 고유한 과거 기록을 보관합니다.

현재 문서와 byte-for-byte 동일했던 사본은 v334에서 제거했습니다. 현재 운영 기준은 `../../current/`의 다음 문서를 봅니다.

- `POSTGRES_BASELINE_COMPLETION_STATE.md`
- `POSTGRES_NEXT_REVISION_PREFLIGHT.md`
- `POSTGRES_DEPLOYMENT_RUNTIME_READINESS.md`
- `POSTGRES_RUNTIME_CONFIG_HARDENING.md`
- `POSTGRES_DEPLOYMENT_MIGRATION_RUNBOOK.md`

여기의 과거 `stamp`, `upgrade`, `downgrade`, DB 생성·복원 기록을 새 실행 승인으로 해석하지 않습니다.
