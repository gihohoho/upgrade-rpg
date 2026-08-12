# PostgreSQL / Alembic 로컬 설치·확인 체크리스트 — v284

이번 단계에서는 DB를 만들거나 지우지 않습니다. migration도 생성하거나 적용하지 않습니다.

## 확인된 기호 컴퓨터 환경

- Python: 3.11.4
- 실제 backend 가상환경: `backend/.venv`
- Docker: 29.6.1
- Docker Compose: v5.3.0
- SQLAlchemy: 2.0.51
- Alembic: 1.18.5
- asyncpg: 0.31.0
- psycopg: 3.3.4
- FastAPI: 0.139.0
- Alembic revision: 0개

필수 설치 조건은 모두 준비되어 있습니다.

## 가상환경 활성화

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 실행

```bash
.venv\Scripts\activate
```

활성화되면 현재 Python 경로가 `backend/.venv`를 사용해야 합니다.

## backend 의존성 동기화가 필요할 때만

현재 필수 패키지가 모두 설치되어 있으므로 지금 다시 설치할 필요는 없습니다.

나중에 패키지 누락 오류가 생긴 경우에만 실행합니다.

실행 위치: `backend` 폴더  
`.venv` 상태: 켜진 상태

```bash
python -m pip install -e ".[dev]"
```

## 설치 상태 읽기 전용 확인

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_postgres_alembic_prerequisites.py
```

## Alembic 상태 읽기 전용 확인

v284 ZIP을 적용한 뒤 실행합니다.

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_alembic_readonly_state.py
```

이 도구는 `history`, `heads`, `current`만 실행하며 DB schema를 변경하지 않습니다.

## Docker 상태 읽기 전용 확인

실행 위치: 프로젝트 루트  
`.venv` 상태: 필요 없음 / 켜져 있거나 꺼져 있어도 상관없음

```bash
docker compose ps
docker compose ls
docker volume ls
docker compose config
```

위 명령은 컨테이너나 volume을 삭제하지 않습니다.

## 아직 실행하지 않을 명령

```txt
python scripts/setup_dev_db.py --reset
docker compose down -v
python -m alembic revision --autogenerate
python -m alembic upgrade head
python -m alembic downgrade
python -m alembic stamp head
```

위 명령은 schema, 데이터, volume 또는 migration 이력을 변경할 수 있으므로 별도 승인 전 실행하지 않습니다.

## Vue/npm 관련

v284에서 새 npm 라이브러리나 프레임워크를 추가하지 않았습니다.
DB/Alembic 상태 확인에는 `npm install`이나 `npm run dev`가 필요하지 않습니다.
