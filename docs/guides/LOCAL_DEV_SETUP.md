# Local Dev Setup — v375

매일 사용하는 설치·실행·종료 명령은 루트 [README.md](../../README.md)의 `로컬에서 게임 확인하기`가 단일 기준입니다. 이 문서는 새 PC와 오류 상황에서 확인할 안전 경계만 보충합니다.

## 준비물

- Git Bash
- Python 3.11
- Docker Desktop
- Node.js/npm: 선택적 Vue 화면을 볼 때만 필요
- `backend/.env`: 없을 때만 `.env.example`에서 복사하며 Git에 올리지 않음
- `backend/.venv`: backend dependency 전용

## 현재 DB 경계

- Alembic source head: `v377_auth_email_public_security`
- 실제 local/Neon DB current: `v295_initial_schema`
- v377 apply/stamp/downgrade: local·Neon 모두 0회
- local apply preflight: Alembic 전 safe-stop, report 없음, marker 보존·재실행 금지
- Neon: untouched, backup/apply marker 없음

새 PC나 빈 Docker volume에서는 README의 서버 실행까지만 진행하고, schema reset·seed·migration은 Codex에게 현재 승인 범위를 확인한 뒤 진행합니다. `docker compose down -v`, `setup_dev_db.py --reset`, `alembic upgrade/downgrade/stamp`를 문제 해결용으로 사용하지 않습니다.

## 빠른 상태 점검

- 실행 위치: 프로젝트 루트
- Python `.venv` 상태: 꺼짐
- 새 설치 여부: 없음

```bash
cd "/c/Users/HOME/Desktop/Upgrade RPG"
docker compose ps
curl http://127.0.0.1:8000/api/v1/health
curl http://127.0.0.1:8000/api/v1/health/db
```

정상 기대값:

- `upgrade_rpg_postgres`: running/healthy
- backend health: HTTP 200
- DB health: HTTP 200

## 자주 생기는 문제

### 브라우저 `Failed to fetch`

1. `http://127.0.0.1:5500/index.html`로 열었는지 확인합니다.
2. backend `127.0.0.1:8000`이 실행 중인지 확인합니다.
3. PostgreSQL `127.0.0.1:55432`가 healthy인지 확인합니다.
4. `file://`와 임의 포트를 사용하지 않습니다.

### 포트가 이미 사용 중

기존 정상 서버가 있으면 새로 실행하지 않고 그 서버를 재사용합니다. 실행 터미널을 찾을 수 없을 때만 Codex에게 해당 프로세스 확인을 요청합니다.

### DB health 실패

Docker Desktop과 `docker compose ps`를 먼저 확인합니다. 빈 DB인지, 기존 v295 DB가 중지된 것인지 구분하지 않은 상태에서 reset·volume 삭제·migration을 실행하지 않습니다.

### 이메일 가입이 끝까지 진행되지 않음

v377 이메일 lifecycle·공개 보안 source와 private environment 준비는 완료됐지만 실제 DB
migration과 Brevo sender/key·실제 메일은 아직 완료되지 않았습니다. `8db9bcb`의 격리
왕복·local backup은 새 SHA에 stale이고 local apply는 Alembic 전에 안전 중단됐으므로 같은
action을 재실행하지 않습니다. 현재 로컬에서는 전체 이메일 가입 end-to-end 성공을 정상
기대값으로 두지 않습니다.

## 추가 문서

- [현재 상태](../current/CURRENT_STATUS.md)
- [PostgreSQL migration runbook](../reference/database/POSTGRES_DEPLOYMENT_MIGRATION_RUNBOOK.md)
- [Local CORS](../reference/frontend/LOCAL_DEV_CORS.md)
- [브라우저 점검](MASTER_DATA_BROWSER_CHECKLIST.md)
