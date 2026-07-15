기호의 Upgrade RPG 프로젝트를 이어서 진행합니다.

이번에 첨부하는 최신 ZIP `rpg_v308_runtime_config_hardening_ready.zip`을 반드시 기준으로 작업해주세요.

========================
사용자/응답 방식
========================

사용자는 코딩을 거의 모르는 기호입니다.
항상 한국어로 쉽고 자세하게 설명해주세요.

모든 터미널 명령은 바로 위에 다음을 함께 적어주세요.

- 실행 위치
- Python 가상환경 `.venv`를 켜야 하는지/꺼도 되는지

실제 backend 가상환경은 프로젝트 루트가 아니라 `backend/.venv`입니다.
Git Bash에서는 `backend` 폴더에서 `source .venv/Scripts/activate`로 켭니다.
Vue/npm 명령은 `frontend/vue-app`에서 실행하며 Python `.venv`가 필요 없습니다.

설치·확인 항목과 새 도구를 빠짐없이 알려주세요. 새 설치가 없으면 없다고 명확히 적어주세요.
Git 명령은 프로젝트 루트에서 한 줄로 주세요.

```bash
git status && git add . && git commit -m "..." && git push
```

DB/env/seed/인증/API body/route/write/migration/Docker volume처럼 위험한 작업은 작은 승인 경계로 진행하고 실제 결과 확인 후 다음 단계로 넘어가세요.

========================
현재 최신 기준
========================

- 최신 작업: `v308.runtime-config-hardening-ready`
- readiness version: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

현재 legacy 화면:

- 게임: `index.html`
- 관리자: `admin.html`
- legacy JS/CSS: `src/`

현재 Vue 앱:

- 위치: `frontend/vue-app/`
- `/admin` GET 연결 완료: health, requirements, domains, catalog, detail, relations
- Preview/Apply/write/인증은 Vue에 연결하지 않음

당분간 게임 콘텐츠 개발은 하지 않습니다.
장비/스킬/보스/필드/드랍률/밸런스/강화 수치 추가·조정은 보류합니다.

========================
PostgreSQL/Alembic 완료 상태
========================

```txt
classification: alembic-managed-baseline-complete
source rpg_game: public 23/749, application 22/748
source current revision: v295_initial_schema
restore rehearsal rpg_game_restore_rehearsal_v290: 23/749 / v302 report verified
migration test DB: 23/1 / differences=0
v304 source report: verified
v305 completion: postgres-baseline-completion-state-verified
v306 next revision preflight: next-revision-not-required-current-schema-equivalent
v306 candidate operations: 0 / next revision required no
v307 strict + require-health: passed
PostgreSQL: 16.14
Docker PostgreSQL: running/healthy
```

고정값:

```txt
backup: local-backups/postgres/rpg_game_20260714_130403_KST_v290.custom.dump
backup SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
revision: v295_initial_schema
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
schema digest: 7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921
data digest: ecb19e57283dc6b780426339bfc46f2bac14da63a618249808f30132508f9244
```

로컬 backup/review evidence는 Git/ZIP/채팅에 포함하지 않습니다.

========================
v308 runtime config hardening
========================

추가·변경 파일:

```txt
backend/app/core/config.py
backend/app/db/session.py
backend/app/main.py
backend/.env.example
backend/Dockerfile
deploy/docker-compose.production.yml
deploy/README.md
tools/check_runtime_config_hardening.py
tools/smoke/backend/smoke_runtime_config_hardening.py
docs/current/POSTGRES_RUNTIME_CONFIG_HARDENING.md
docs/current/POSTGRES_PRODUCTION_DEPLOYMENT_TEMPLATE.md
```

적용 상태:

```txt
pool_pre_ping: true
pool_size: 5
max_overflow: 10
pool_timeout: 30 seconds
pool_recycle: 1800 seconds
shutdown: await engine.dispose()
production guard: DEBUG/local default secret/short secret fail closed
backend Dockerfile: non-root / Uvicorn only / no automatic Alembic
production Compose: separate template / no Adminer / no PostgreSQL host port
actual backend/.env: unchanged
local docker-compose.yml: unchanged
DB schema/data/Alembic revision: unchanged
```

========================
다음 첫 작업 — v308 읽기 전용 검증
========================

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_runtime_config_hardening.py --strict --require-health
```

정상 기대 결과:

```txt
result: runtime-config-hardening-verified-local-runtime-preserved
next safe stage: separate-production-secrets-tls-and-container-validation
```

`blocked-or-failed`가 나오면 `.env`, Docker, DB, Alembic을 임의 변경하지 말고 전체 출력을 검토하세요.

========================
다음 단계 안전 순서
========================

1. v308 actual strict + health 결과 확인
2. local runtime/DB health 회귀 없음 확인
3. 남은 운영 경고를 secret/TLS/image/reverse proxy로 분류
4. production Compose를 실행하지 않고 정적 검증 준비
5. worker 수와 pool/max_connections 계산
6. 실제 운영 secret/TLS/container build는 별도 승인
7. 전체 smoke 및 새 ZIP 후 다음 승인 경계 이동

========================
절대 변경/실행 금지
========================

- actual `.env`
- production secret/TLS 실제 입력
- production Compose build/up/pull/down
- Docker container/volume 변경 또는 삭제
- source/rehearsal stamp 재실행
- 새 revision/autogenerate/upgrade/downgrade
- DB 생성/삭제/복원
- seed/인증/API route/body/write
- Preview/Apply request body
- 게임 콘텐츠/밸런스

========================
검증 원칙
========================

코드나 구조를 건드렸다면 최소 확인:

- 관련 전용 smoke
- JS 문법 검사
- `python -m compileall -q backend/app backend/scripts backend/alembic tools`
- `bash tools/run_smoke_core.sh`
- Vue 변경 시 `npm ci`와 `npm run build`
- ZIP 무결성 및 제외 파일 검사

작업 후 답변에는 다음을 포함하세요.

1. 이번에 한 일
2. 검증 완료한 것
3. 서버 재실행 명령 — 실행 위치와 `.venv` 상태 포함
4. git 명령 — 프로젝트 루트에서 한 줄
5. 다음 추천 단계

코드 또는 문서를 변경했다면 새 ZIP도 같이 만들어주세요.
