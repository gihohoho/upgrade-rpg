# Upgrade RPG

웹 기반 방치형 Upgrade RPG 프로젝트입니다. 공개 버전은 v351, 로컬 source checkpoint와 Alembic head는 v377이며 실제 local/Neon DB는 v377/v295입니다.

## 새 작업 시작

1. [AGENTS.md](AGENTS.md)
2. [NEXT_CHAT_HANDOFF.md](NEXT_CHAT_HANDOFF.md)
3. [현재 상태](docs/current/CURRENT_STATUS.md)

전체 문서는 [Docs Hub](docs/README.md), 문서 위치·중복·마감 규칙은 [Documentation System](docs/DOCUMENTATION_SYSTEM.md)을 봅니다.

## 로컬에서 게임 확인하기

Git Bash 터미널을 사용합니다. Python 3.11, Git과 Docker Desktop이 필요하며 Vue를 볼 때만 Node.js가 필요합니다. Docker Desktop을 먼저 켜고, 이미 정상 실행 중인 서버는 다시 켜지 않고 그대로 사용합니다.

### 처음 한 번: backend 준비

- 실행 위치: `backend` 폴더
- Python `.venv` 상태: 꺼짐 → 생성 후 켜짐
- 새 설치 여부: 있음(처음 설치하거나 dependency가 바뀐 경우만)

```bash
cd "/c/Users/HOME/Desktop/Upgrade RPG/backend"
test -d .venv || python -m venv .venv
source .venv/Scripts/activate
python -m pip install -e ".[dev]"
test -f .env || cp .env.example .env
```

### 터미널 1: PostgreSQL과 Adminer

- 실행 위치: 프로젝트 루트
- Python `.venv` 상태: 꺼짐
- 새 설치 여부: 없음

```bash
cd "/c/Users/HOME/Desktop/Upgrade RPG"
docker compose up -d postgres adminer
docker compose ps
```

### 터미널 2: FastAPI backend

- 실행 위치: `backend` 폴더
- Python `.venv` 상태: 켜짐
- 새 설치 여부: 없음

```bash
cd "/c/Users/HOME/Desktop/Upgrade RPG/backend"
source .venv/Scripts/activate
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 터미널 3: 실제 legacy 게임

- 실행 위치: 프로젝트 루트
- Python `.venv` 상태: 꺼짐
- 새 설치 여부: 없음

```bash
cd "/c/Users/HOME/Desktop/Upgrade RPG"
python -m http.server 5500 --bind 127.0.0.1
```

브라우저 확인 주소:

- 게임: <http://127.0.0.1:5500/index.html>
- 관리자: <http://127.0.0.1:5500/admin.html>
- backend 상태: <http://127.0.0.1:8000/api/v1/health>
- DB 상태: <http://127.0.0.1:8000/api/v1/health/db>
- API 문서: <http://127.0.0.1:8000/docs>
- Adminer: <http://127.0.0.1:8081>

Adminer 로컬 접속값은 `PostgreSQL / postgres / rpg_user / rpg_password / rpg_game` 순서입니다.

`file://`로 `index.html`을 열면 API origin이 달라지므로 사용하지 않습니다.

### 선택: Vue 개발 화면

현재 실제 게임은 legacy 화면이며 Vue는 전체 프론트엔드 전환 작업공간입니다. 기능 동등성이 확인될 때까지 공개 화면은 legacy를 유지합니다.

- 실행 위치: `frontend/vue-app` 폴더
- Python `.venv` 상태: 필요 없음
- 새 설치 여부: `npm ci`는 처음 한 번 또는 dependency 변경 시에만 있음

```bash
cd "/c/Users/HOME/Desktop/Upgrade RPG/frontend/vue-app"
test -d node_modules || npm ci
npm run dev
```

확인 주소: <http://127.0.0.1:5173>

### 종료

backend, legacy, Vue 터미널은 각각 `Ctrl+C`로 종료합니다. PostgreSQL 데이터는 지우지 않고 멈추기만 합니다.

- 실행 위치: 프로젝트 루트
- Python `.venv` 상태: 꺼짐
- 새 설치 여부: 없음

```bash
cd "/c/Users/HOME/Desktop/Upgrade RPG"
docker compose stop
```

`docker compose down -v`, DB reset·seed, `alembic upgrade/downgrade/stamp`는 임의로 실행하지 않습니다. 새 PC나 빈 Docker volume에서 DB 상태 검사가 실패하면 Codex에게 먼저 확인합니다. local DB는 recovery1 검증 뒤 v377로 적용했고 Neon은 v295입니다. 인증 요청 보호 503과 이메일 없는 기존 계정 로그인 차단은 해결됐습니다. 다음 단계는 Brevo sender·전용 API key를 준비해 local 실제 이메일 가입 흐름을 검증하는 것입니다.

## 핵심 폴더

- `index.html`, `admin.html`, `src/`: 실제 legacy 게임과 관리자 화면
- `backend/`: FastAPI, SQLAlchemy, Alembic
- `frontend/vue-app/`: Vue TypeScript + Pinia 전체 전환 작업공간
- `deploy/`: 배포 계약과 정제된 증거
- `docs/`: 현재 상태, reference, 계약, guide, archive
- `tools/`: checker, report, smoke

## 현재 고정값

```txt
GHCR: ghcr.io/gihohoho/upgrade-rpg-backend
target: linux/amd64
database: Neon PostgreSQL 16 Singapore
hosting: Render Free Web Service + Static Site
public backend/static: v351 Live
local source checkpoint: v377 / migration source head v377 / local DB v377 / Neon DB v295
```
