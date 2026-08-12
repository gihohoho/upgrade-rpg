# Docker PostgreSQL Guide

## Docker를 쓰는 이유

PostgreSQL을 컴퓨터에 직접 설치하지 않고, Docker 컨테이너로 띄워서 개발합니다.

장점:

```txt
설치/삭제가 쉬움
개발 DB를 재생성하기 쉬움
팀원이 같은 DB 환경을 맞추기 쉬움
```

## 포함된 서비스

`docker-compose.yml`에는 2개 서비스가 있습니다.

```txt
postgres = PostgreSQL DB
adminer = 브라우저에서 DB를 볼 수 있는 간단한 관리 도구
```

## 실행

프로젝트 루트에서:

```bash
docker compose up -d
```

## 중지

```bash
docker compose down
```

## DB 데이터까지 완전히 삭제

주의: 저장된 로컬 DB 데이터가 전부 사라집니다.

```bash
docker compose down -v
```

## 상태 확인

```bash
docker ps
```

또는:

```bash
docker compose ps
```

## PostgreSQL 접속 정보

```txt
Host: localhost
Port: 55432
Database: rpg_game
User: rpg_user
Password: rpg_password
```

FastAPI에서 쓰는 주소:

```txt
postgresql+asyncpg://rpg_user:rpg_password@127.0.0.1:55432/rpg_game
```

## Adminer 접속

```txt
http://localhost:8081
```

Adminer에서 입력:

```txt
System: PostgreSQL
Server: postgres
Username: rpg_user
Password: rpg_password
Database: rpg_game
```

주의: Adminer 컨테이너 안에서는 DB 서버 이름이 `localhost`가 아니라 `postgres`입니다.

## 자주 나는 문제

### 1. port is already allocated

이미 55432 포트를 다른 PostgreSQL이 쓰고 있다는 뜻입니다.

해결 후보:

```txt
기존 PostgreSQL 종료
또는 docker-compose.yml에서 "5433:5432"로 변경
```

포트를 5433으로 바꾸면 `backend/.env`의 DATABASE_URL도 바꿔야 합니다.

```txt
postgresql+asyncpg://rpg_user:rpg_password@localhost:5433/rpg_game
```

### 2. Docker daemon is not running

Docker Desktop이 꺼져 있는 상태입니다.
Docker Desktop을 실행한 뒤 다시 시도하세요.

### 3. /api/v1/health/db가 실패함

확인 순서:

```bash
docker compose ps
cat backend/.env
python tools/check_backend_ready.py --db
```

DB 컨테이너가 healthy 상태인지 먼저 확인하세요.


### 4. asyncpg가 없다고 나옴

FastAPI 실행 중 아래 오류가 나오면 Python 가상환경에 PostgreSQL async 드라이버가 없는 상태입니다.

```txt
ModuleNotFoundError: No module named 'asyncpg'
```

해결:

```bash
cd backend
source .venv/Scripts/activate
pip install asyncpg
```

### 5. CORS_ORIGINS 파싱 오류

아래 오류가 나오면 `backend/.env`의 CORS_ORIGINS 형식을 확인하세요.

```txt
SettingsError: error parsing value for field "cors_origins"
```

권장 형식:

```env
CORS_ORIGINS='["http://localhost:5500","http://127.0.0.1:5500","http://localhost:5173","http://127.0.0.1:5173","http://localhost:3000","http://127.0.0.1:8000","http://localhost:8000"]'
```


> 로컬 PostgreSQL은 기본 포트 `5432`가 아니라 `55432`를 사용한다. Windows에서 기존 PostgreSQL과 충돌을 피하기 위한 프로젝트 기준이다. 자세한 내용은 `docs/archive/history/PROJECT_HISTORY.md`를 참고한다.
