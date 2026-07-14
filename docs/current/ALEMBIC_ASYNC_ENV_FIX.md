# Alembic asyncpg online 실행 수정 — v284

## 확인된 실제 오류

기호 컴퓨터에서 아래 읽기 전용 명령을 실행했을 때:

```bash
python -m alembic current
```

`sqlalchemy.exc.MissingGreenlet` 오류가 발생했습니다.

원인은 다음 조합이었습니다.

- DB URL: `postgresql+asyncpg://...`
- 기존 Alembic online 실행: 동기식 `engine_from_config()`와 `with connectable.connect()`

`asyncpg`는 비동기 드라이버이므로 동기식 연결 경로에서 I/O를 시도하면 `MissingGreenlet`이 발생합니다.

## v284 수정

`backend/alembic/env.py`를 SQLAlchemy/Alembic async 엔진 구조로 변경했습니다.

- `async_engine_from_config()` 사용
- `async with connectable.connect()` 사용
- `await connection.run_sync(do_run_migrations)`로 Alembic 동기 migration context 연결
- `asyncio.run(run_async_migrations())`로 CLI 진입
- 종료 시 `await connectable.dispose()` 수행

이 수정은 Alembic이 DB에 연결하는 **실행 방식만** 바꿉니다.

변경하지 않은 항목:

- DB schema
- DB 데이터
- Docker volume
- `.env`
- seed
- Alembic revision
- migration upgrade/downgrade/stamp
- API route/response body
- 인증 및 write 로직

## 읽기 전용 재확인

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 활성화된 상태

```bash
python tools/check_alembic_readonly_state.py
```

이 도구는 아래 세 명령만 실행합니다.

- `alembic history`
- `alembic heads`
- `alembic current`

`current`는 DB에 연결해 현재 revision을 읽지만 schema나 migration history를 변경하지 않습니다.

### 정상적으로 가능한 결과

현재 revision 파일이 0개이므로 다음은 정상일 수 있습니다.

- `history`: 출력 없음
- `heads`: 출력 없음
- `current`: 출력 없음, 종료코드 0

`current`가 출력 없이 성공하면 DB 연결은 됐지만 아직 Alembic stamp/revision이 없다는 의미일 수 있습니다.

### 다음 오류가 나오면

- `ConnectionRefusedError`: PostgreSQL 컨테이너가 꺼져 있거나 55432 포트가 열리지 않은 상태
- 비밀번호 오류: compose와 현재 설정의 계정/비밀번호 불일치 가능성
- DB 없음 오류: 대상 DB가 아직 없거나 이름이 다를 가능성
- `MissingGreenlet`: v284 `backend/alembic/env.py`가 적용되지 않은 상태

이 단계에서는 오류가 나더라도 아래 명령은 실행하지 않습니다.

```txt
python scripts/setup_dev_db.py --reset
docker compose down -v
python -m alembic revision --autogenerate
python -m alembic upgrade head
python -m alembic downgrade
python -m alembic stamp head
```
