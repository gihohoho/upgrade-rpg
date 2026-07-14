# 다음 추천 단계

## 현재 완료

- v284에서 실제 `MissingGreenlet` 원인을 확인하고 Alembic online env를 asyncpg 호환 방식으로 수정
- 읽기 전용 `history/heads/current` 통합 확인 도구 추가
- DB schema/data/env/seed/revision은 변경하지 않음

## 기호가 먼저 확인할 명령

v284 ZIP 적용 후 실행합니다.

### 가상환경 활성화

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 실행

```bash
.venv\Scripts\activate
```

### Alembic 읽기 전용 상태 확인

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_alembic_readonly_state.py
```

## 다음 작업 — v285

`로컬 PostgreSQL 비파괴 런타임 상태 확인`

1. `MissingGreenlet` 재발 여부 확인
2. Docker container/volume 목록 확인
3. PostgreSQL health 확인
4. `/api/v1/health/db` 결과 확인
5. DB에 보존할 데이터 존재 여부 확인
6. revision 생성/upgrade/stamp 없이 baseline 전략만 문서화

## 계속 실행 금지

```txt
python scripts/setup_dev_db.py --reset
docker compose down -v
python -m alembic revision --autogenerate
python -m alembic upgrade head
python -m alembic downgrade
python -m alembic stamp head
```

## 설치 관련

- 새 라이브러리/프레임워크 추가 없음
- 기호 컴퓨터의 필수 Python/Docker 패키지는 이미 모두 확인됨
- npm 패키지 변경 없음
