# PostgreSQL / Alembic Readiness — v309

이 문서는 현재 프로젝트 파일을 기준으로 PostgreSQL과 Alembic 도입 준비 상태를 자동 분석한 결과입니다.

중요: 이 보고서는 **읽기 전용 정적 분석**입니다. DB 연결, `.env` 변경, schema 생성/삭제, seed import, migration 생성/적용을 수행하지 않습니다.

## 결론

- 현재 backend는 이미 PostgreSQL 전용 타입과 두 드라이버를 전제로 설계되어 있습니다.
- FastAPI 런타임은 `asyncpg`, 로컬 schema/seed 도구는 `psycopg` 사용을 전제로 분리되어 있습니다.
- SQLAlchemy 모델과 수동 검토가 끝난 최초 Alembic revision 1개가 존재합니다.
- v284에서 사용자 실제 `MissingGreenlet` 결과를 근거로 Alembic online 경로를 async engine 방식으로 수정했습니다.
- 기호 컴퓨터에서 `alembic history`, `heads`, `current`가 모두 정상 완료되고 PostgreSQL 연결이 확인되었습니다.
- 기호 컴퓨터의 실제 runtime 점검에서 모델/DB 테이블 22개, 전체 row 748개, `alembic_version` 없음, DB health 정상 결과가 확인되었습니다.
- 사용자 PC의 v304 source post-check 결과로 현재 분류는 `alembic-managed-baseline-complete`로 전환되었습니다.
- v287에서 Windows Docker 출력의 UTF-8/cp949 혼합 decode 오류를 보완했습니다.
- v288에서는 columns/types/nullability/PK/FK/unique/index/check 구조를 읽기 전용으로 비교합니다.
- v289에서는 PostgreSQL `FLOAT` alias를 정규화해 `DOUBLE PRECISION` reflection false positive를 제거합니다.
- v290에서는 schema 차이 0개를 gate로 사용하는 backup/restore read-only preflight, client 도구 점검, 민감 backup 경로와 분리 DB 경계를 추가합니다.
- v291에서는 승인된 source backup 한 단계만 수행하는 custom dump 생성, TOC 검증, SHA-256, source snapshot, manifest 도구를 추가합니다.
- v292에서는 verified backup의 SHA-256과 source baseline을 다시 확인하고, target DB가 없을 때만 빈 `rpg_game_restore_rehearsal_v290`을 생성하는 도구를 추가합니다.
- v293에서는 exact verified backup을 빈 target에 single transaction으로 복원하고, table별 row count와 SQLAlchemy schema 동등성을 확인하는 도구를 추가합니다.
- v294에서는 verified restore DB를 보존한 채 `rpg_game_migration_empty_v290`을 0 tables / 0 rows 상태로 생성·검증합니다.
- v295 최초 실행에서는 Alembic autogenerate가 빈 `alembic_version` 제어 테이블을 만들었고, 기존 사후 검사가 이를 비정상으로 오판했습니다.
- v296에서는 정확히 `alembic_version` 1 table / 0 rows / recorded revision 없음만 recovery workspace로 허용하고, `--inspect-workspace` 후 기존 placeholder를 재사용합니다.
- v297에서는 generated revision의 nested `op.f(...)` naming helper를 migration operation 집계에서 제외해 v296 parser false positive를 제거합니다.
- v298에서는 사용자 review bundle의 exact revision SHA를 기준으로 22 tables / 209 columns / 42 indexes / types / nullable / PK / FK / unique / downgrade dependency order 수동 검토를 완료하고, isolated migration DB `upgrade head` 실행 가드를 추가합니다.
- v299에서는 사용자 PC에서 성공한 isolated `upgrade head` 결과를 전제로 exact `downgrade base`만 허용하고, target이 빈 `alembic_version` placeholder 상태로 복귀하는지 검증하는 가드를 추가합니다.
- v300에서는 verified first upgrade와 verified downgrade evidence를 모두 고정하고, 같은 isolated DB의 두 번째 `upgrade head` 결과가 첫 upgrade signature와 정확히 같은지 검증하는 가드를 추가합니다.
- 사용자 PC에서 v300 `upgrade -> downgrade base -> upgrade` 왕복이 실제 성공했고 first/second upgrade signatures가 동일함을 확인했습니다.
- v301에서는 source 22 tables / 748 rows / no Alembic, exact backup/revision, restore evidence, v300 round-trip head를 한 번에 읽기 전용으로 재검사하는 source baseline stamp preflight를 추가합니다.
- 사용자 PC에서 v301 preflight가 `ready-for-separate-restore-rehearsal-stamp-approval`로 실제 통과했습니다.
- v302에서는 exact restore rehearsal DB만 대상으로 고정하고, 22개 application table 구조와 전체 748개 row-content SHA-256을 stamp 전후 비교하는 guard를 추가합니다.
- 사용자 승인 후 restore rehearsal `stamp head`와 source `stamp head`가 각각 실행·검증되었습니다.
- v303 rehearsal post-check는 23/749, application 22/748, digest preserved, v302 report verified로 통과했습니다.
- v304 source post-check는 23/749, application 22/748, revision `v295_initial_schema`, v304 report verified로 통과했습니다.
- v305에서는 baseline 완료 상태를 읽기 전용 checker와 회귀 smoke로 고정했습니다.
- v306에서는 단일 Alembic graph, 승인 model source snapshot, canonical schema comparison, read-only `compare_metadata()`와 sequence ownership을 함께 확인하며 새 revision 필요 여부만 판정합니다.
- 사용자 PC에서 v306 preflight가 candidate operation 0개, 새 revision 불필요로 실제 통과했습니다.
- v307에서는 exact runtime DB/driver, FastAPI startup mutation, DB health contract, Docker running/healthy, env key inventory, manual migration runbook을 읽기 전용으로 점검합니다.
- 사용자 PC의 v307 `--require-health` 결과가 통과했고 production hardening warning 12개를 수집했습니다.
- v308에서는 명시적 async pool 5개 옵션, shutdown `engine.dispose()`, production fail-closed guard, non-root FastAPI Dockerfile, 별도 운영 Compose 초안을 추가합니다.
- v309에서는 여러 줄 `create_async_engine(settings.database_url, ...)` 호출을 한 줄 문자열 검사로 오판하던 readiness 검사기를 Python AST 기반으로 수정합니다.

## 현재 구조 요약

| 항목 | 현재 상태 |
|---|---|
| SQLAlchemy model table 수 | 22개 |
| PostgreSQL `JSONB` mapped column | 26개 |
| 큰 수/확률용 `Numeric` mapped column | 10개 |
| `ForeignKey` 선언 | 21개 |
| 명시적 `UniqueConstraint` 선언 | 5개 |
| async session | 있음 |
| Docker PostgreSQL 16 | 있음 |
| 로컬 host port 55432 | 있음 |
| Adminer 8081 | 있음 |
| `.env.example` asyncpg URL | 있음 |
| Alembic 설정 파일 | 있음 |
| Alembic env | 있음 |
| Alembic asyncpg-compatible online env | 있음 |
| Alembic versions 폴더 | 있음 |
| Alembic revision 수 | 1개 |
| Alembic script template | 있음 |

## Python 의존성 선언

- `sqlalchemy`: `backend/pyproject.toml`에 선언됨
- `asyncpg`: `backend/pyproject.toml`에 선언됨
- `psycopg`: `backend/pyproject.toml`에 선언됨
- `alembic`: `backend/pyproject.toml`에 선언됨

개별 패키지를 따로 설치하기보다, backend 가상환경에서 프로젝트 의존성을 한 번에 설치하는 방식을 기준으로 합니다.

```bash
python -m pip install -e ".[dev]"
```

## 현재 SQLAlchemy model 목록

| 테이블 | 모델 | 파일 |
|---|---|---|
| `admin_roles` | `AdminRole` | `backend/app/models/admin.py` |
| `admin_user_roles` | `AdminUserRole` | `backend/app/models/admin.py` |
| `admin_change_logs` | `AdminChangeLog` | `backend/app/models/admin.py` |
| `bosses` | `Boss` | `backend/app/models/boss.py` |
| `drop_tables` | `DropTable` | `backend/app/models/boss.py` |
| `drop_table_items` | `DropTableItem` | `backend/app/models/boss.py` |
| `characters` | `Character` | `backend/app/models/character.py` |
| `enhancement_groups` | `EnhancementGroup` | `backend/app/models/enhancement.py` |
| `enhancement_levels` | `EnhancementLevel` | `backend/app/models/enhancement.py` |
| `field_zones` | `FieldZone` | `backend/app/models/field.py` |
| `item_templates` | `ItemTemplate` | `backend/app/models/item.py` |
| `item_instances` | `ItemInstance` | `backend/app/models/item.py` |
| `user_inventory_slots` | `UserInventorySlot` | `backend/app/models/item.py` |
| `user_equipment_slots` | `UserEquipmentSlot` | `backend/app/models/item.py` |
| `user_mailbox_messages` | `UserMailboxMessage` | `backend/app/models/mailbox.py` |
| `skills` | `Skill` | `backend/app/models/skill.py` |
| `character_skills` | `CharacterSkill` | `backend/app/models/skill.py` |
| `skill_levels` | `SkillLevel` | `backend/app/models/skill.py` |
| `user_character_skills` | `UserCharacterSkill` | `backend/app/models/skill.py` |
| `users` | `User` | `backend/app/models/user.py` |
| `user_profiles` | `UserProfile` | `backend/app/models/user.py` |
| `user_save_snapshots` | `UserSaveSnapshot` | `backend/app/models/user.py` |

## 현재 DB 실행 경로

### FastAPI 런타임

- 파일: `backend/app/db/session.py`
- URL: `postgresql+asyncpg://...`
- 방식: `create_async_engine()` + `AsyncSession`
- 연결 확인 API: `GET /api/v1/health/db`

### 로컬 schema/seed 도구

- 파일: `backend/scripts/setup_dev_db.py`
- URL 변환: `postgresql+asyncpg://...` → `postgresql+psycopg://...`
- 방식: sync SQLAlchemy + psycopg
- `--create-schema`: 누락 테이블 생성
- `--seed`: seed import
- `--verify`: table count 조회
- `--reset`: `public` schema 전체 삭제 후 재생성 — **사용자 승인 전 실행 금지**

### Alembic

- 설정: `backend/alembic.ini`
- env: `backend/alembic/env.py`
- metadata: `Base.metadata`
- online 방식: `async_engine_from_config()` + `connection.run_sync()`
- 현재 revision: 1개
- `history`, `heads`, `current` 읽기 전용 수집 도구: `tools/check_alembic_readonly_state.py`
- Docker/schema/table count/health 읽기 전용 수집 도구: `tools/check_postgres_runtime_readonly_state.py`
- SQLAlchemy metadata/실제 PostgreSQL 상세 구조 비교: `tools/check_postgres_schema_equivalence.py`
- backup/restore schema gate와 client 도구 확인: `tools/check_postgres_backup_restore_preflight.py`
- 승인된 source backup 생성/검증: `tools/create_postgres_backup.py`
- isolated target restore 및 검증: `tools/restore_postgres_rehearsal_database.py`
- empty migration test DB 생성: `tools/create_postgres_migration_test_database.py`
- 최초 revision 생성·자동 검토: `tools/create_postgres_initial_alembic_revision.py`
- 최초 revision 수동 검토: `docs/current/POSTGRES_INITIAL_ALEMBIC_REVISION_MANUAL_REVIEW.md`
- isolated migration DB upgrade guard: `tools/upgrade_postgres_migration_test_database.py`
- isolated migration DB downgrade guard: `tools/downgrade_postgres_migration_test_database.py`
- isolated migration round-trip re-upgrade guard: `tools/reupgrade_postgres_migration_test_database.py`
- source baseline stamp read-only preflight: `tools/check_postgres_source_baseline_stamp_preflight.py`
- restore rehearsal stamp guard: `tools/stamp_postgres_restore_rehearsal_database.py`
- source baseline stamp final guard: `tools/stamp_postgres_source_database.py`
- baseline completion state lock: `tools/check_postgres_baseline_completion_state.py`
- next revision read-only preflight: `tools/check_postgres_next_revision_preflight.py`
- deployment/runtime readiness preflight: `tools/check_postgres_deployment_runtime_readiness.py`
- runtime config hardening verification: `tools/check_runtime_config_hardening.py`

## 현재 차단 요소 / 실제 검증 필요 지점

- 현재 로컬 스키마 생성은 Alembic이 아니라 `Base.metadata.create_all()`을 사용합니다.
- `setup_dev_db.py --reset`은 `public` 스키마 전체를 삭제하는 고위험 경로입니다.
- docker-compose.yml은 로컬 고정 DB 비밀번호를 사용하므로 운영 secret 분리가 필요합니다.
- Adminer 8081 공개는 로컬 전용이며 운영 구성에서 분리해야 합니다.

## SQLite 의존성 점검

backend runtime/model/schema 경로에서 SQLite URL이나 SQLite 전용 타입은 발견되지 않았습니다.
현재 모델은 오히려 PostgreSQL `JSONB`에 직접 의존하므로 SQLite를 임시 대체 DB로 사용하면 동일 동작을 보장할 수 없습니다.

## 안전한 도입 순서

### Stage A — 설치/실행 환경만 확인

1. Docker Desktop 설치 여부 확인
2. `docker compose` 사용 가능 여부 확인
3. backend `.venv`에서 프로젝트 Python 의존성 설치 여부 확인
4. `asyncpg`, `psycopg`, `alembic`, `sqlalchemy` import 확인
5. 아직 DB 생성/삭제/migration은 실행하지 않음

### Stage B — 로컬 PostgreSQL과 백업 경로 확인

1. 기존 container가 `healthy`인지 읽기 전용으로 확인
2. `/api/v1/health/db`가 `ok`인지 확인
3. schema equivalence가 `structurally-equivalent`, 차이 0개인지 확인
4. `tools/check_postgres_backup_restore_preflight.py`로 host/container client 도구 확인
5. 사용자 승인 후 `tools/create_postgres_backup.py --execute`로 source backup 생성·검증
6. backup은 `local-backups/postgres/`에만 저장하고 Git/전달 ZIP에서 제외
7. v292 승인 후 `tools/create_postgres_restore_rehearsal_database.py --execute`로 빈 target DB 생성 및 검증
8. v293 승인 후 `tools/restore_postgres_rehearsal_database.py --execute`로 exact backup을 target에만 single transaction restore
9. restore 후 target 22 tables / 748 rows / table별 counts / schema differences=0 확인
10. v294 승인 후 `tools/create_postgres_migration_test_database.py --execute`로 0 tables / 0 rows empty migration DB 생성
11. v297에서 `tools/create_postgres_initial_alembic_revision.py --inspect-workspace`로 placeholder 상태를 읽기 전용 확인
12. 같은 v297 도구의 `--execute`로 existing placeholder를 재사용하고 nested `op.f(...)` helper를 제외한 실제 operations만 자동 검토
13. v298에서 exact revision SHA `24a30adb...`를 모델과 수동 교차 검토하고 isolated DB upgrade guard를 준비
14. 사용자 별도 승인 후 `tools/upgrade_postgres_migration_test_database.py --execute`로 migration test DB에만 첫 `upgrade head`
15. v299에서 같은 DB의 `downgrade base`를 검증하고 빈 Alembic placeholder로 복귀
16. v300에서 `tools/reupgrade_postgres_migration_test_database.py --execute`로 두 번째 `upgrade head`와 첫 결과를 exact 비교
17. 사용자 PC에서 왕복 signatures 동일과 source/rehearsal 보존을 실제 확인
18. v301에서 `tools/check_postgres_source_baseline_stamp_preflight.py --strict`로 source/backup/revision/round-trip evidence를 읽기 전용 재검사
19. 사용자 PC에서 v301 preflight 실제 통과 확인
20. v302에서 `tools/stamp_postgres_restore_rehearsal_database.py --inspect`로 exact target/revision과 schema/data content signatures를 읽기 전용 수집
21. 사용자 별도 승인 후에만 restore rehearsal DB에 `stamp head` 실행
22. stamp 성공 조건은 application schema/data signatures 동일 + `alembic_version` 1 table/1 row 추가뿐
23. 사용자 PC에서 rehearsal post-check와 v302 report verified 확인
24. v304 exact source guard를 별도 승인 후 1회 실행하고 source 23/749, application 22/748, revision `v295_initial_schema` 확인
25. v304 source execution report verified와 rehearsal/migration 무변경 확인
26. v305 completion checker로 세 DB, 두 실행 report, exact revision set을 읽기 전용 고정
27. v306 next-revision preflight로 single head/model snapshot/canonical schema/Alembic candidate diff/sequence ownership 확인
28. 사용자 PC에서 candidate operation 0개와 새 revision 불필요를 실제 확인
29. v307 deployment/runtime readiness로 exact runtime DB, startup mutation 부재, Docker health, env key, 운영 migration runbook 확인
30. 사용자 PC에서 v307 `--require-health` 통과와 production hardening warning 12개 확인
31. v308에서 pool/lifecycle/production guard와 별도 배포 template를 DB/.env/Docker mutation 없이 보강
32. v309에서 multiline runtime engine URL binding 검사 오탐을 AST 기반으로 수정
33. 다음 revision/autogenerate/upgrade/downgrade는 별도 승인 전까지 금지
34. `docker compose down -v`는 데이터 전체 삭제이므로 승인 전 금지

### Stage C — Alembic 실행 방식 검증

1. 사용자 실제 환경에서 sync `engine_from_config()` + asyncpg 조합의 `MissingGreenlet` 확인
2. v284에서 `async_engine_from_config()` + `connection.run_sync()` 방식으로 수정
3. 전용 Alembic async env smoke 추가
4. `history`, `heads`, `current`를 읽기 전용 도구로 다시 수집
5. `current`가 DB 연결 오류를 내면 container/URL 상태를 확인하되 schema는 변경하지 않음
6. 이 단계에서도 revision 생성, upgrade, downgrade, stamp는 실행하지 않음

### Stage D — baseline 전략 및 완료 상태

초기 수집 시점에는 `existing-schema-without-alembic-baseline`이었습니다. backup, restore rehearsal, empty migration DB 왕복, exact digest 비교를 거쳐 source와 rehearsal에 baseline stamp가 완료되었습니다.

현재 확정 상태:

- classification: `alembic-managed-baseline-complete`
- source/rehearsal: 23 public tables / 749 rows
- application: 22 tables / 748 rows preserved
- current revision: `v295_initial_schema`
- source/rehearsal application digest identical
- v302/v304 execution reports verified

이전 `stamp head`는 완료됐으며 재실행하지 않습니다.

### Stage E — 다음 revision 준비

1. v306 next-revision read-only preflight 실제 결과 확인
2. candidate operation 0개면 single baseline을 유지하고 새 revision을 만들지 않음
3. model/schema 변경 의도가 생길 때만 별도 review 단계로 이동
4. autogenerate 실행 전 별도 승인 경계 마련
5. 생성되더라도 source가 아닌 isolated migration DB에서만 검토·왕복
6. table/index/FK/JSONB/Numeric와 API 영향 비교
7. 그 후에만 다음 migration 실행 여부를 별도 승인

현재는 새 revision 생성, autogenerate, upgrade, downgrade가 모두 미승인입니다.

### Stage F — 운영·배포 runtime readiness

1. `tools/check_postgres_deployment_runtime_readiness.py --strict`로 exact runtime DB와 driver 확인
2. FastAPI startup/lifespan에 자동 create_all/upgrade/stamp가 없는지 확인
3. `GET /api/v1/health/db`가 SELECT 1 read-only 계약인지 확인
4. Docker Compose PostgreSQL running/healthy, restart, healthcheck, named volume 확인
5. `.env`는 값이 아니라 key inventory만 확인하고 secret은 출력하지 않음
6. v308에서 pool, shutdown lifecycle, production config guard, FastAPI image와 별도 운영 Compose 초안을 보강
7. 실제 운영 secret/TLS/image digest/reverse proxy 적용은 다음 별도 단계로 분리
8. 운영 migration은 서버 시작과 분리하고 backup/isolated/별도 승인 원칙을 유지

## Rollback 원칙

- 코드 rollback과 DB rollback을 분리합니다.
- migration 전 DB backup을 반드시 만듭니다.
- downgrade가 안전한지 임시 DB에서 먼저 확인합니다.
- seed import와 schema migration을 한 명령에 묶지 않습니다.
- `setup_dev_db.py --reset`과 `docker compose down -v`는 복구 불가능한 로컬 데이터 삭제가 될 수 있으므로 명시 승인 없이는 실행하지 않습니다.

## 기호 컴퓨터에서 사용할 사전 점검

v283에서 추가한 도구는 설치 상태만 확인하고 DB에는 접속하지 않습니다.

```bash
python tools/check_postgres_alembic_prerequisites.py
```

JSON 결과가 필요할 때:

```bash
python tools/check_postgres_alembic_prerequisites.py --json
```

모든 필수 항목이 설치되어야 성공 코드로 끝나게 확인할 때:

```bash
python tools/check_postgres_alembic_prerequisites.py --strict
```

Alembic 읽기 전용 상태를 한 번에 수집할 때:

```bash
python tools/check_alembic_readonly_state.py
```

이 도구의 `current`만 DB에 연결해 현재 revision을 읽으며, schema와 migration history는 변경하지 않습니다.

PostgreSQL runtime/schema/data 존재 여부를 읽기 전용으로 수집할 때:

```bash
python tools/check_postgres_runtime_readonly_state.py
```

SQLAlchemy metadata와 실제 PostgreSQL 상세 구조를 비교할 때:

```bash
python tools/check_postgres_schema_equivalence.py
```

backup/restore 실행 전 gate와 client 도구를 읽기 전용으로 확인할 때:

```bash
python tools/check_postgres_backup_restore_preflight.py
```

승인된 source backup을 생성하고 archive/체크섬을 검증할 때:

```bash
python tools/create_postgres_backup.py --execute
```

승인된 빈 restore rehearsal DB를 target이 없을 때만 생성할 때:

```bash
python tools/create_postgres_restore_rehearsal_database.py --execute
```

검증된 backup을 이미 생성된 빈 target DB에만 restore하고 결과를 검증할 때:

```bash
python tools/restore_postgres_rehearsal_database.py --execute
```

상세 전략은 `docs/current/POSTGRES_ALEMBIC_BASELINE_STRATEGY.md`를 기준으로 합니다.

## v308에서 변경하지 않은 것

- DB schema/data
- Docker container/volume
- `.env`
- seed
- 새 Alembic revision 생성/autogenerate
- upgrade/downgrade/stamp 재실행
- API route path/response body
- 인증/Write Guard/write 로직
- 게임 콘텐츠

## 다음 읽기 전용 체크포인트

```bash
python tools/check_runtime_config_hardening.py --strict --require-health
```

통과 조건은 v307 live runtime 상태 유지, 명시적 pool 옵션 5개, shutdown `engine.dispose()`, production unsafe default 차단, local Compose 보존, non-root Dockerfile과 별도 운영 Compose template 안전 경계입니다.

## v291-v293 backup / restore rehearsal 역사적 경계

- backup 폴더: `local-backups/postgres/`
- 실제 verified backup: `rpg_game_20260714_130403_KST_v290.custom.dump`
- source DB: `rpg_game` / 22 tables / 748 rows
- `pg_restore --list` TOC 검증과 SHA-256/source snapshot/manifest 완료
- restore rehearsal DB: `rpg_game_restore_rehearsal_v290`
- v292는 target 존재 여부 확인 후 없을 때만 owner `rpg_user`, template `template0` 빈 DB 생성
- 생성 후 target tables 0, Alembic table 없음, source 22/748 유지 확인
- v293은 `pg_restore --single-transaction --exit-on-error`로 exact backup을 target에만 복원
- restore 후 target 22 tables / 748 rows / table별 counts / schema differences=0 검증
- empty migration test DB: `rpg_game_migration_empty_v290`
- 이 구간의 restore/migration 준비는 완료됐습니다. 현재는 DB drop/restore와 기존 stamp 재실행이 금지됩니다.
