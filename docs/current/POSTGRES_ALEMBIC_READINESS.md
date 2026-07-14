# PostgreSQL / Alembic Readiness — v289

이 문서는 현재 프로젝트 파일을 기준으로 PostgreSQL과 Alembic 도입 준비 상태를 자동 분석한 결과입니다.

중요: 이 보고서는 **읽기 전용 정적 분석**입니다. DB 연결, `.env` 변경, schema 생성/삭제, seed import, migration 생성/적용을 수행하지 않습니다.

## 결론

- 현재 backend는 이미 PostgreSQL 전용 타입과 두 드라이버를 전제로 설계되어 있습니다.
- FastAPI 런타임은 `asyncpg`, 로컬 schema/seed 도구는 `psycopg` 사용을 전제로 분리되어 있습니다.
- SQLAlchemy 모델은 존재하지만 Alembic revision 체계는 아직 시작되지 않았습니다.
- v284에서 사용자 실제 `MissingGreenlet` 결과를 근거로 Alembic online 경로를 async engine 방식으로 수정했습니다.
- 기호 컴퓨터에서 `alembic history`, `heads`, `current`가 모두 정상 완료되고 PostgreSQL 연결이 확인되었습니다.
- 기호 컴퓨터의 실제 runtime 점검에서 모델/DB 테이블 22개, 전체 row 748개, `alembic_version` 없음, DB health 정상 결과가 확인되었습니다.
- 현재 분류는 `existing-schema-without-alembic-baseline`이며 기존 데이터 보존형 전략으로 확정되었습니다.
- v287에서 Windows Docker 출력의 UTF-8/cp949 혼합 decode 오류를 보완했습니다.
- v288에서는 columns/types/nullability/PK/FK/unique/index/check 구조를 읽기 전용으로 비교합니다.
- v289에서는 PostgreSQL `FLOAT` alias를 정규화해 `DOUBLE PRECISION` reflection false positive를 제거합니다.
- 따라서 다음 위험 단계는 바로 migration을 적용하는 것이 아니라, **상세 schema 동등성 → 백업/복원 → 별도 빈 DB migration 검증** 순서여야 합니다.

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
| Alembic revision 수 | 0개 |
| Alembic script template | 없음 |

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
- 현재 revision: 0개
- `history`, `heads`, `current` 읽기 전용 수집 도구: `tools/check_alembic_readonly_state.py`
- Docker/schema/table count/health 읽기 전용 수집 도구: `tools/check_postgres_runtime_readonly_state.py`
- SQLAlchemy metadata/실제 PostgreSQL 상세 구조 비교: `tools/check_postgres_schema_equivalence.py`

## 현재 차단 요소 / 실제 검증 필요 지점

- `backend/alembic/script.py.mako` migration 템플릿이 없습니다.
- Alembic revision 파일이 아직 0개입니다.
- 현재 로컬 스키마 생성은 Alembic이 아니라 `Base.metadata.create_all()`을 사용합니다.
- `setup_dev_db.py --reset`은 `public` 스키마 전체를 삭제하는 고위험 경로입니다.

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

1. `docker compose up -d postgres adminer`
2. container가 `healthy`인지 확인
3. `/api/v1/health/db`가 `ok`인지 확인
4. 비어 있는 개발 DB에서만 backup/restore 명령을 리허설
5. `docker compose down -v`는 데이터 전체 삭제이므로 승인 전 금지

### Stage C — Alembic 실행 방식 검증

1. 사용자 실제 환경에서 sync `engine_from_config()` + asyncpg 조합의 `MissingGreenlet` 확인
2. v284에서 `async_engine_from_config()` + `connection.run_sync()` 방식으로 수정
3. 전용 Alembic async env smoke 추가
4. `history`, `heads`, `current`를 읽기 전용 도구로 다시 수집
5. `current`가 DB 연결 오류를 내면 container/URL 상태를 확인하되 schema는 변경하지 않음
6. 이 단계에서도 revision 생성, upgrade, downgrade, stamp는 실행하지 않음

### Stage D — baseline 전략 선택

실제 DB 상태 수집 결과, 현재 프로젝트는 다음으로 확정되었습니다.

- `existing-schema-without-alembic-baseline`
- 모델/실제 테이블 22개 일치
- 전체 row 748개 보존 필요
- `alembic_version` 없음

다만 table 개수 일치만으로 stamp하지 않고 상세 schema 동등성을 먼저 확인합니다.

`alembic stamp head`는 migration을 실행하지 않고 이력만 기록하므로, schema가 정확히 일치한다고 검증하기 전에는 사용하면 안 됩니다.

### Stage E — 사용자 승인 후 첫 migration

1. DB 백업
2. 첫 revision 생성
3. 생성된 migration 파일 수동 검토
4. 임시 빈 DB에서 upgrade/downgrade 왕복
5. table/index/FK/JSONB/Numeric 비교
6. smoke 및 `/health/db` 확인
7. 그 후에만 실제 개발 DB 적용

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

상세 전략은 `docs/current/POSTGRES_ALEMBIC_BASELINE_STRATEGY.md`를 기준으로 합니다.

## 이번 단계에서 변경하지 않은 것

- DB schema
- Docker volume
- `.env`
- seed
- Alembic revision 생성
- migration 적용/rollback/stamp
- API route path/response body
- 인증/Write Guard/write 로직
- 게임 콘텐츠

## 다음 승인 전 체크포인트

아래 결과를 기호 컴퓨터에서 확인한 뒤 다음 단계로 갑니다.

- `python tools/check_postgres_schema_equivalence.py` 결과
- 상세 column/type/nullability/PK/FK/unique/index/check 차이 여부
- DB backup 생성 위치와 파일명
- backup restore 리허설 대상 임시 DB
- 별도 빈 DB 최초 revision upgrade/downgrade 검증 계획
