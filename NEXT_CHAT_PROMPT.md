기호의 Upgrade RPG 프로젝트를 이어서 진행합니다.

최신 ZIP `rpg_v288_postgres_baseline_schema_equivalence_preflight.zip`을 기준으로 작업해주세요.

현재 실제 PostgreSQL 상태:

- PostgreSQL 16.14
- DB `rpg_game`, 12 MB
- SQLAlchemy model 22 tables / public 22 tables
- total rows 748
- `alembic_version` 없음
- current revision 없음
- `/api/v1/health/db` 정상
- 분류 `existing-schema-without-alembic-baseline`
- 기존 데이터 보존형 Alembic baseline 전략 확정

v287에서 Windows subprocess UTF-8/cp949 혼합 decode 오류를 수정했습니다.
v288에서 `tools/check_postgres_schema_equivalence.py`를 추가했습니다.

다음 첫 작업은 사용자가 실행한 아래 결과를 분석하는 것입니다.

```bash
python tools/check_postgres_schema_equivalence.py
```

결과가 `structurally-equivalent`이면 backup/restore와 별도 빈 임시 DB 최초 migration 검증 계획을 작성하세요.
결과가 `review-required`이면 category/table별 차이를 먼저 분석하세요.

사용자 명시 승인 전에는 다음을 변경하거나 실행하지 마세요.

- DB schema/data
- Docker container/volume
- `.env`
- seed
- Alembic revision 생성
- upgrade/downgrade/stamp
- API route path/body
- 실제 write 로직
- 인증

항상 npm/Python 명령에 실행 위치와 `.venv` 상태를 적어주세요.
실제 backend 가상환경은 `backend/.venv`입니다.
