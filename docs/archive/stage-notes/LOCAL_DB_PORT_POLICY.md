# Local DB Port Policy

## Decision

로컬 개발용 PostgreSQL은 호스트 포트 `55432`를 사용한다.

```txt
Host PC: 127.0.0.1:55432
Docker container: postgres:5432
```

`docker-compose.yml` 기준:

```yaml
ports:
  - "55432:5432"
```

`backend/.env` 기준:

```env
DATABASE_URL="postgresql+asyncpg://rpg_user:rpg_password@127.0.0.1:55432/rpg_game"
```

## Why

Windows 개발 환경에서 기본 PostgreSQL 포트 `5432`가 다른 로컬 PostgreSQL 또는 기존 서비스와 충돌할 수 있었다.
실제로 Docker 컨테이너 내부 접속은 정상인데 Python에서 `127.0.0.1:5432` 접속 시 비밀번호 오류가 발생했다.

따라서 이 프로젝트는 로컬 호스트 포트를 `55432`로 고정한다.

## Commands

위치: **프로젝트 루트**

```bash
docker compose down -v --remove-orphans
docker compose up -d --force-recreate
docker ps
```

`docker ps`에서 아래처럼 보이면 정상이다.

```txt
0.0.0.0:55432->5432/tcp
```

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
python -c "import psycopg; conn=psycopg.connect('postgresql://rpg_user:rpg_password@127.0.0.1:55432/rpg_game'); print(conn.execute('select 1').fetchone()); conn.close()"
python scripts/setup_dev_db.py --reset --seed --verify
```
