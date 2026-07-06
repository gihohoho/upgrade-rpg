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

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
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
node tools/smoke_seed_extraction.js
```
