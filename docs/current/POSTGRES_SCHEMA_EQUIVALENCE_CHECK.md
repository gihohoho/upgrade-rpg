# PostgreSQL schema 동등성 읽기 전용 점검 — v288

현재 실제 DB는 테이블 22개와 데이터 748개를 가진 기존 schema입니다.
최초 Alembic baseline 전에 SQLAlchemy metadata와 실제 PostgreSQL 구조가 같은지 더 자세히 확인해야 합니다.

## 추가 도구

```txt
tools/check_postgres_schema_equivalence.py
```

비교 범위:

- table 존재 여부
- column 존재 여부
- PostgreSQL column type
- nullable
- primary key
- foreign key와 `ON DELETE` / `ON UPDATE`
- unique constraint
- index
- check constraint

이 도구는 DB catalog를 읽기만 합니다.

실행하지 않는 작업:

- `CREATE`, `ALTER`, `DROP`
- `INSERT`, `UPDATE`, `DELETE`
- Alembic revision 생성
- `upgrade`, `downgrade`, `stamp head`
- Docker/volume 변경
- `.env` 수정

## 실행 방법

backend 가상환경 활성화:

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash에서 실행

```bash
source .venv/Scripts/activate
```

schema 비교:

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_postgres_schema_equivalence.py
```

JSON 결과:

```bash
python tools/check_postgres_schema_equivalence.py --json
```

차이가 있을 때 종료 코드도 실패로 받고 싶을 때:

```bash
python tools/check_postgres_schema_equivalence.py --strict
```

## 결과 의미

### `structurally-equivalent`

현재 도구가 비교하는 범위에서 SQLAlchemy metadata와 실제 PostgreSQL 구조 차이가 0개입니다.

이 결과만으로 바로 `stamp head`를 실행하지 않습니다.
다음으로 backup/restore와 별도 빈 DB 최초 migration 검증이 필요합니다.

### `review-required`

하나 이상의 구조 차이가 있습니다.
출력되는 category와 table/detail을 기준으로 차이를 먼저 해결해야 합니다.

예시 category:

```txt
missing-table
extra-table
missing-column
extra-column
type
nullable
primary-key
foreign-key
unique
index
check
```

### `connection-failed`

PostgreSQL 연결이나 Python package 환경을 확인해야 합니다.
DB 변경 명령으로 해결하려고 하면 안 됩니다.

## 제한 사항

PostgreSQL reflection과 SQLAlchemy 표현 방식이 다른 일부 default/expression은 자동 동일 판정에서 제외했습니다.
따라서 차이 0개 이후에도 최초 revision 파일과 별도 빈 DB 결과를 수동 검토해야 합니다.
