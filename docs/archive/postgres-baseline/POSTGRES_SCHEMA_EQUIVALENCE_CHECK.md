# PostgreSQL schema 동등성 읽기 전용 점검 — v289

현재 실제 DB는 22개 테이블과 748개 row를 가진 기존 schema입니다.
최초 Alembic baseline 전에 SQLAlchemy metadata와 실제 PostgreSQL 구조가 같은지 읽기 전용으로 비교합니다.

## v288 실제 결과

기호 컴퓨터의 최초 실행 결과는 다음 두 차이만 표시했습니다.

```txt
[type] user_profiles: add_attack_speed: model=FLOAT db=DOUBLE PRECISION
[type] user_profiles: farm_atk_bonus: model=FLOAT db=DOUBLE PRECISION
```

이 두 컬럼은 `Mapped[float]`로 선언되어 SQLAlchemy 모델에서는 `FLOAT`로 표현됩니다.
PostgreSQL은 precision 없는 `FLOAT`를 `DOUBLE PRECISION`으로 취급하고 reflection 시에도 `DOUBLE PRECISION`으로 돌려줍니다.
따라서 실제 저장 타입 차이가 아니라 **동일 타입의 표현 차이(false positive)** 입니다.

## v289 수정

`tools/check_postgres_schema_equivalence.py`에 PostgreSQL FLOAT alias 정규화를 추가했습니다.

```txt
FLOAT             -> DOUBLE PRECISION
FLOAT(1..24)      -> REAL
FLOAT(25..53)     -> DOUBLE PRECISION
```

이 정규화는 비교 문자열만 바꾸며 DB schema, SQLAlchemy model, row 데이터는 변경하지 않습니다.

## 비교 범위

- table 존재 여부
- column 존재 여부
- PostgreSQL column type와 alias 정규화
- nullable
- primary key
- foreign key와 `ON DELETE` / `ON UPDATE`
- unique constraint
- index
- check constraint

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

## v289 적용 후 기대 결과

실제 DB나 모델에 다른 차이가 없다면 다음이 기대됩니다.

```txt
분류: structurally-equivalent
타입 정규화: postgresql-float-aliases.v1
차이: 0개
```

실제 결과를 다시 수집하기 전에는 기대값을 확정 결과로 간주하지 않습니다.

## 결과 의미

### `structurally-equivalent`

현재 도구가 비교하는 범위에서 SQLAlchemy metadata와 실제 PostgreSQL 구조 차이가 0개입니다.
이 결과만으로 바로 `stamp head`를 실행하지 않습니다.
backup/restore 리허설과 별도 빈 DB 최초 migration 검증이 먼저입니다.

### `review-required`

alias 정규화 이후에도 하나 이상의 실제 구조 차이가 있습니다.
출력되는 category와 table/detail을 기준으로 먼저 분석합니다.

### `connection-failed`

PostgreSQL 연결이나 Python package 환경을 확인합니다.
DB 변경 명령으로 해결하지 않습니다.

## 제한 사항

PostgreSQL reflection과 SQLAlchemy 표현 방식이 다른 일부 default/expression은 자동 동일 판정에서 제외했습니다.
차이 0개 이후에도 최초 revision 파일과 별도 빈 DB 결과를 수동 검토해야 합니다.
