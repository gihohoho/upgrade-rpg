# FastAPI Backend Foundation Draft

이 폴더는 현재 HTML/JS 게임을 나중에 **FastAPI + PostgreSQL** 서버 구조로 옮기기 위한 1차 뼈대입니다.

현재 단계의 목표는 실제 게임 로직을 모두 서버로 옮기는 것이 아니라, 아래 기준을 먼저 고정하는 것입니다.

```txt
1. 관리자 페이지 요구사항 V1 고정
2. PostgreSQL DB 설계 초안 고정
3. FastAPI 프로젝트 폴더 구조 고정
4. API 응답 계약과 백엔드 라우터 구조 연결
```

## 실행 전 준비

Python 3.11 이상을 권장합니다.

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate  # Git Bash
# PowerShell: .venv\\Scripts\\Activate.ps1
pip install -e .[dev]
cp .env.example .env  # Git Bash
# PowerShell: Copy-Item .env.example .env
```

## PostgreSQL 실행

프로젝트 루트에서 Docker PostgreSQL을 먼저 실행합니다.

```bash
cd ..
docker compose up -d
```

DB 연결 확인은 FastAPI 실행 후 `/api/v1/health/db`에서 합니다.

## 로컬 실행

실행 위치: `backend` 폴더  
`.venv` 상태: 켜진 상태

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

브라우저에서 확인:

```txt
http://localhost:8000/docs
http://localhost:8000/api/v1/health
http://localhost:8000/api/v1/health/db
```

## 현재 포함된 구조

```txt
backend/
  app/
    main.py
    api/
      router.py
      routes/
        health.py
        game.py
        admin.py
    core/
      config.py
      response.py
      security.py
    db/
      session.py
      base.py
    models/
      user.py
      character.py
      skill.py
      item.py
      boss.py
      field.py
      enhancement.py
      mailbox.py
      admin.py
    schemas/
      common.py
      game.py
      admin.py
    services/
      game_service.py
      admin_service.py
  alembic/
  sql/
    schema_draft.sql
  pyproject.toml
  .env.example
```

## 아직 하지 않은 것

```txt
실제 게임 테이블 마이그레이션 적용
실제 로그인/인증 구현
현재 JS 게임 데이터 seed 추출
전투/드랍/강화 로직 서버 이전
관리자 페이지 UI 제작
```

이번 단계는 **뼈대와 설계 초안**입니다.


## v077 참고

이번 버전부터 아래 내용이 보강되었습니다.

```txt
asyncpg 의존성 명시
CORS_ORIGINS JSON/쉼표 형식 모두 지원
JS 마스터 데이터 seed 추출 도구 추가
```

seed 추출은 프로젝트 루트에서 실행합니다.

```bash
node tools/extract_seed_data.js
node tools/smoke/game/smoke_seed_extraction.js
```


## Local DB seed import

위치: **backend 폴더**

DB를 초기화하고 seed 데이터를 넣으려면:

```bash
python scripts/setup_dev_db.py --reset --seed --verify
```

DB를 건드리지 않고 seed JSON만 확인하려면:

```bash
python scripts/setup_dev_db.py --dry-run
```

자세한 설명은 `../docs/SEED_IMPORT.md`를 확인하세요.



## v079 seed import connection fix

- `backend/scripts/setup_dev_db.py`를 sync SQLAlchemy + `psycopg` 방식으로 변경했습니다.
- Windows/Docker 환경에서 `asyncpg.exceptions.ConnectionDoesNotExistError`가 seed import 중 발생하는 문제를 피하기 위한 수정입니다.
- `backend/pyproject.toml`에 `psycopg[binary]` 의존성을 추가했습니다.


> 로컬 PostgreSQL은 기본 포트 `5432`가 아니라 `55432`를 사용한다. Windows에서 기존 PostgreSQL과 충돌을 피하기 위한 프로젝트 기준이다. 자세한 내용은 `docs/LOCAL_DB_PORT_POLICY.md`를 참고한다.

## v081 master-data API 확인

`/api/v1/game/master-data`는 PostgreSQL seed 테이블을 실제로 읽습니다.

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
uvicorn app.main:app --reload
```

다른 터미널에서 확인:

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
python scripts/check_master_data_api.py
```

브라우저에서는 아래 주소를 엽니다.

```txt
http://127.0.0.1:8000/api/v1/game/master-data
```

## v083 - master-data asset 옵션

기본 master-data API는 백신 오탐과 응답 크기 증가를 줄이기 위해 긴 SVG/data URL 이미지 문자열을 제외합니다.

위치: **브라우저 주소창**

```txt
http://127.0.0.1:8000/api/v1/game/master-data
```

이미지 문자열까지 포함하려면:

위치: **브라우저 주소창**

```txt
http://127.0.0.1:8000/api/v1/game/master-data?includeAssets=true
```

터미널 확인:

위치: **backend 폴더 + 가상환경 activate 상태**

```bash
python scripts/check_master_data_api.py
python scripts/check_master_data_api.py --include-assets
```

## v084 note

- `/api/v1/game/master-data` 기본 응답에서 최상위 asset 필드뿐 아니라 `options`, `conditions`, `rules`, `raw` 같은 중첩 JSON 안의 `data:image...` 문자열도 제거합니다.
- asset 문자열이 필요한 경우에는 `?includeAssets=true`를 사용합니다.



## Master-data parity 검사

FastAPI 서버가 켜진 상태에서 실행합니다.

위치: backend 폴더 + 가상환경 activate 상태

```bash
python scripts/check_master_data_parity.py
python scripts/check_master_data_parity.py --include-assets
```

이 검사는 현재 JS seed JSON과 `/api/v1/game/master-data` 응답이 같은지 비교합니다.


### v087 note

`lightsabre`처럼 기본 발동확률이 없는 스킬은 `procRate: null`로 유지합니다. `python scripts/setup_dev_db.py --reset --seed --verify`를 다시 실행해야 DB에 반영됩니다.

### v099 save snapshot API bridge

유저 진행 데이터 마이그레이션의 첫 단계로 `idleRpgSaveV22` localStorage 원본을 PostgreSQL `user_save_snapshots`에 저장/조회하는 API와 브라우저 테스트 함수를 추가했습니다. 아직 게임 로딩 흐름은 localStorage를 유지합니다.



## v273 local CORS

Vue 개발 서버(`http://127.0.0.1:5173`)에서 FastAPI(`http://127.0.0.1:8000`)를 호출할 때 CORS 오류가 나지 않도록 local/debug 환경의 기본 개발 origin을 보강했습니다.

CORS 설정은 서버 시작 시점에 반영됩니다. ZIP을 교체했는데도 Vue 화면에서 CORS 오류가 계속 보이면 FastAPI 서버를 완전히 종료하고 다시 실행합니다.

변경하지 않은 것:

```txt
.env 파일
DB 구조
seed
인증
API route path
API 응답 body
write 로직
Write Guard
```
