# PostgreSQL 최초 Alembic revision 수동 검토 — v298

검토 대상:

- revision ID: `v295_initial_schema`
- 파일: `backend/alembic/versions/v295_initial_schema_initial_postgresql_schema.py`
- SHA-256: `24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa`
- 사용자 review bundle SHA-256: `c4210a57c68a65855fa86e8f9c52dd5b7782aa59182d4c393575a499c49a8db5`

## 결론

**수동 검토 통과**입니다.

이 revision은 SQLAlchemy model과 다음 항목이 모두 일치합니다.

- 테이블: `22 / 22`
- 컬럼: `209 / 209`
- 인덱스: `42 / 42`
- Foreign Key constraint: `21`
- 명시적 Unique constraint: `6`
- Check constraint: `0`
- 컬럼 타입과 길이
- nullable
- Primary Key
- Foreign Key 대상 및 `ondelete` / `onupdate`
- Unique constraint
- Index 컬럼 및 unique 여부
- server default

revision의 upgrade에는 다음 schema 생성 작업만 있습니다.

```txt
create_table: 22
create_index: 42
```

downgrade에는 다음 제거 작업만 있습니다.

```txt
drop_index: 42
drop_table: 22
```

`op.execute`, data insert/delete/update, `alter_column`, upgrade의 drop 작업, 환경변수 또는 DB 비밀번호 문자열은 없습니다.

## FLOAT 확인

다음 두 모델 컬럼은 revision에서도 `sa.Float()`로 생성됩니다.

```txt
user_profiles.farm_atk_bonus
user_profiles.add_attack_speed
```

PostgreSQL에서 precision 없는 `FLOAT`는 `DOUBLE PRECISION`으로 처리됩니다. v289 schema checker의 `postgresql-float-aliases.v1` 정규화 정책과 일치하므로 타입 차이가 아닙니다.

## 기본값 확인

모델에는 Python-side default가 115개 있지만 DB server default는 0개입니다. 생성 revision도 server default 0개로 모델 schema와 일치합니다.

Python-side default는 SQLAlchemy ORM이 INSERT 값을 구성할 때 사용하며, DB 자체 default constraint가 아닙니다. 이번 baseline revision에서 임의로 server default를 추가하지 않습니다.

## downgrade 순서

- downgrade table 순서는 upgrade table 생성 순서의 정확한 역순입니다. (`exact reverse create order`)
- FK를 가진 자식 테이블이 부모 테이블보다 먼저 삭제됩니다.
- FK 의존 순서 위반은 0개입니다.

## 승인 범위

이 수동 검토는 다음 한 단계만 허용합니다.

```txt
rpg_game_migration_empty_v290 에서 alembic upgrade head 리허설
```

아래 작업은 아직 승인하지 않습니다.

```txt
원본 rpg_game upgrade/stamp
rehearsal DB 변경/삭제
migration DB downgrade
DB drop/create
.env 변경
Docker volume 변경
```

빈 migration DB의 upgrade 결과가 `22 model tables + alembic_version`, model table row 0, revision row `v295_initial_schema`, schema differences 0인지 확인한 뒤 다음 경계를 결정합니다.
