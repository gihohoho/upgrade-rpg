# Local Dev Setup - v077

이 문서는 `v077_backend_env_fix_and_seed_extractor` 기준 로컬 개발환경 세팅 순서입니다.

목표는 아래 3개가 정상 작동하는 상태를 만드는 것입니다.

```txt
1. GitHub 저장소
2. Python 가상환경 + FastAPI
3. Docker PostgreSQL
```

## 0. 현재 권장 위치

프로젝트 루트 예시:

```bash
~/Desktop/Upgrade RPG
```

`backend` 폴더 안에서 작업할 때와 프로젝트 루트에서 작업할 때가 다릅니다.
명령어에 `cd backend`, `cd ..`가 있으면 꼭 위치를 확인하세요.

## 1. Git 확인

프로젝트 루트에서:

```bash
git status
git remote -v
```

정상 기준:

```txt
working tree clean
origin  https://github.com/... 또는 git@github.com:...
```

## 2. Python 가상환경

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate
pip install -e .[dev]
```

Git Bash에서는 아래처럼 활성화합니다.

```bash
source .venv/Scripts/activate
```

PowerShell에서는 아래처럼 활성화합니다.

```powershell
.venv\Scripts\Activate.ps1
```

## 3. backend/.env 만들기

`backend` 폴더 안에서:

```bash
cp .env.example .env
```

`backend/.env`는 개인 로컬 설정 파일이므로 Git에 올리지 않습니다.

## 4. Docker PostgreSQL 실행

프로젝트 루트로 이동합니다.

```bash
cd ..
```

PostgreSQL과 Adminer를 실행합니다.

```bash
docker compose up -d
```

상태 확인:

```bash
docker ps
```

정상 기준:

```txt
upgrade_rpg_postgres
upgrade_rpg_adminer
```

## 5. FastAPI 실행

```bash
cd backend
source .venv/Scripts/activate
uvicorn app.main:app --reload
```

브라우저에서 확인:

```txt
http://localhost:8000/docs
http://localhost:8000/api/v1/health
http://localhost:8000/api/v1/health/db
```

## 6. Adminer로 DB 보기

Docker 실행 후 브라우저에서:

```txt
http://localhost:8081
```

입력값:

```txt
System: PostgreSQL
Server: postgres
Username: rpg_user
Password: rpg_password
Database: rpg_game
```

## 7. 개발환경 점검 스크립트

프로젝트 루트에서:

```bash
python tools/check_backend_ready.py
```

DB 연결까지 확인하려면 PostgreSQL 컨테이너가 켜진 상태에서:

```bash
python tools/check_backend_ready.py --db
```


## 8. 이번 세팅에서 확인된 오류 해결

### CORS_ORIGINS 파싱 오류

아래 오류가 나오면 `.env`의 `CORS_ORIGINS` 형식을 확인하세요.

```txt
pydantic_settings.exceptions.SettingsError: error parsing value for field "cors_origins"
```

권장 형식:

```env
CORS_ORIGINS='["http://localhost:5500","http://127.0.0.1:5500","http://localhost:5173","http://127.0.0.1:5173","http://localhost:3000","http://127.0.0.1:8000","http://localhost:8000"]'
```

v077부터는 쉼표 형식도 읽을 수 있게 `backend/app/core/config.py`를 보강했습니다.

### asyncpg 없음 오류

아래 오류가 나오면 가상환경에서 `asyncpg`를 설치하세요.

```txt
ModuleNotFoundError: No module named 'asyncpg'
```

해결:

```bash
cd backend
source .venv/Scripts/activate
pip install asyncpg
```

v077부터는 `backend/pyproject.toml` 의존성에 `asyncpg`가 포함되어 있습니다. 새 가상환경에서는 `pip install -e .[dev]`로 같이 설치됩니다.

## 9. JS 마스터 데이터 seed 추출

프로젝트 루트에서 실행합니다.

```bash
node tools/extract_seed_data.js
node tools/smoke_seed_extraction.js
```

출력 위치:

```txt
backend/seeds/generated/
```

## 다음 단계

로컬 개발환경이 준비되면 다음은 아래 작업입니다.

```txt
현재 JS 마스터 데이터 추출 도구 실행
bosses/zones/skills 데이터를 JSON seed로 변환
/game/master-data API 구현 준비
```


> 로컬 PostgreSQL은 기본 포트 `5432`가 아니라 `55432`를 사용한다. Windows에서 기존 PostgreSQL과 충돌을 피하기 위한 프로젝트 기준이다. 자세한 내용은 `docs/LOCAL_DB_PORT_POLICY.md`를 참고한다.
