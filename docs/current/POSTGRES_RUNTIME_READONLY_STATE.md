# PostgreSQL 런타임 비파괴 상태 점검 — v287

기호 컴퓨터에서 실제 실행 결과를 수집했습니다.

## 실제 확인 결과

- Docker Compose 프로젝트: `upgraderpg`
- 실행 컨테이너: 2개
- PostgreSQL volume: `upgraderpg_rpg_postgres_data`
- PostgreSQL 연결: 정상
- DB: `rpg_game`
- 접속 사용자: `rpg_user`
- PostgreSQL: 16.14
- DB 크기: 12 MB
- SQLAlchemy 모델 테이블: 22개
- 실제 `public` 테이블: 22개
- 전체 row: 748개
- `alembic_version`: 없음
- 현재 Alembic revision: 없음
- `GET /api/v1/health/db`: HTTP 200, `status=ok`
- 최종 분류: `existing-schema-without-alembic-baseline`

보존 가치가 명확한 데이터도 존재합니다.

- `users`: 1
- `user_profiles`: 1
- `characters`: 1
- `user_save_snapshots`: 2
- `admin_change_logs`: 13
- 마스터 데이터 및 관계 데이터 다수

따라서 현재 DB를 초기화하거나 빈 DB처럼 최초 migration을 바로 적용하면 안 됩니다.

## Windows 출력 오류 수정

첫 실행에서 DB 점검 자체는 완료됐지만, Docker subprocess 출력 reader thread에서 아래 오류가 함께 발생했습니다.

```txt
UnicodeDecodeError: 'cp949' codec can't decode byte ...
```

원인은 Windows 기본 console 인코딩 `cp949`와 Docker의 UTF-8 출력이 섞인 것입니다.

v287에서는 subprocess 출력을 bytes로 받은 뒤 다음 순서로 안전하게 해석합니다.

1. UTF-8 BOM 포함 형식
2. 운영체제 기본 인코딩
3. `cp949`
4. 마지막에는 replacement 방식으로 오류 없이 출력

공통 helper:

```txt
tools/_safe_subprocess.py
```

적용 도구:

- `tools/check_postgres_runtime_readonly_state.py`
- `tools/check_postgres_alembic_prerequisites.py`
- `tools/check_alembic_readonly_state.py`

## 실행 방법

backend 가상환경 활성화:

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash에서 실행

```bash
source .venv/Scripts/activate
```

상태 재확인:

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_postgres_runtime_readonly_state.py
```

이 도구는 Docker 조회, PostgreSQL metadata/`SELECT COUNT(*)`, FastAPI GET health만 사용합니다.
DB schema/data, Docker resource, `.env`, seed, Alembic history를 변경하지 않습니다.

## 현재 결론

현재 DB는 **기존 데이터 보존형 Alembic baseline** 대상입니다.

다음 단계는 table 개수만 비교하는 수준을 넘어 columns, types, nullability, PK, FK, unique, index, check 구조가 SQLAlchemy metadata와 같은지 읽기 전용으로 확인하는 것입니다.

## 계속 실행 금지

```txt
python scripts/setup_dev_db.py --reset
docker compose down -v
python -m alembic revision --autogenerate
python -m alembic upgrade head
python -m alembic downgrade
python -m alembic stamp head
```
