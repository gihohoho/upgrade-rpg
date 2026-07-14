기호의 Upgrade RPG 프로젝트를 이어서 진행합니다.

최신 ZIP `rpg_v284_alembic_async_env_fix.zip`을 기준으로 작업해주세요.

현재 완료:

- Vue `/admin` read-only health/requirements/domains/catalog/detail/relations
- PostgreSQL/Alembic 구조 및 설치 조건 점검
- 사용자 실제 `alembic current`에서 `MissingGreenlet` 확인
- sync `engine_from_config()` + asyncpg 문제 수정
- Alembic async online env 적용
- 읽기 전용 `history/heads/current` 통합 확인 도구 추가
- 실제 backend 가상환경 위치는 `backend/.venv`

다음 추천 작업은 `v285 로컬 PostgreSQL 비파괴 런타임 상태 확인`입니다.

목표:

- v284 적용 후 `python tools/check_alembic_readonly_state.py` 결과 확인
- `MissingGreenlet` 재발 여부 확인
- 기존 Docker container/volume 존재 여부 확인
- DB를 삭제하지 않고 PostgreSQL 상태 확인
- `/api/v1/health/db` 실제 결과 확인
- 보존해야 할 DB 데이터 여부 확인
- revision 생성/upgrade/stamp 없이 baseline 전략만 준비

절대 실행 금지:

- `python scripts/setup_dev_db.py --reset`
- `docker compose down -v`
- `python -m alembic revision --autogenerate`
- `python -m alembic upgrade head`
- `python -m alembic downgrade`
- `python -m alembic stamp head`

명령 안내 시 실행 위치와 `.venv` 활성/비활성 여부를 반드시 같이 적어주세요.
Python/FastAPI/Alembic 가상환경은 프로젝트 루트가 아니라 `backend/.venv`입니다.
설치 파일/라이브러리/프레임워크와 사용자가 확인할 사항도 빠짐없이 알려주세요.

작업 후 관련 smoke, JS 문법 검사, compileall, core smoke, ZIP 무결성을 확인하고 새 ZIP을 만들어주세요.
