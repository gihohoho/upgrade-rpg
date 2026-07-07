# Seed Import Connection Fix

## 배경

Windows + Docker Desktop 환경에서 `python scripts/setup_dev_db.py --reset --seed --verify` 실행 중 아래 오류가 발생할 수 있었습니다.

```txt
asyncpg.exceptions.ConnectionDoesNotExistError: connection was closed in the middle of operation
```

FastAPI의 `/api/v1/health/db`는 정상인데 seed import에서만 끊기는 경우, 앱 실행용 async DB 연결 문제가 아니라 **로컬 DB 초기화/대량 seed import 스크립트가 asyncpg로 동작하면서 생기는 안정성 문제**에 가깝습니다.

## 변경 사항

`backend/scripts/setup_dev_db.py`를 동기식 SQLAlchemy + `psycopg` 드라이버 방식으로 변경했습니다.

- FastAPI 앱: 기존처럼 `postgresql+asyncpg://...` 사용 가능
- 로컬 seed import 스크립트: 내부에서 `postgresql+psycopg://...`로 변환해 사용

## 실행 위치

위치: **backend 폴더**

```bash
python scripts/setup_dev_db.py --reset --seed --verify
```

## 의존성

새 가상환경에서는 아래 명령어로 설치합니다.

위치: **backend 폴더**

```bash
pip install -e .[dev]
```

이미 가상환경을 만든 상태라면 아래만 추가로 설치해도 됩니다.

위치: **backend 폴더**

```bash
pip install "psycopg[binary]"
```
