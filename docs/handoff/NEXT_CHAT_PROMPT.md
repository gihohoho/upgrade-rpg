기호의 Upgrade RPG 프로젝트를 이어서 진행합니다.

이번에 첨부하는 최신 ZIP `rpg_v290_postgres_backup_restore_preflight_ready.zip`을 반드시 기준으로 작업해주세요.

========================
사용자/응답 방식
========================

사용자는 코딩을 거의 모르는 기호입니다.
항상 한국어로 쉽고 자세하게 설명해주세요.

모든 터미널 명령은 다음을 바로 위에 함께 적어주세요.

- 실행 위치
- Python 가상환경 `.venv`를 켜야 하는지/꺼도 되는지

실제 backend 가상환경은 프로젝트 루트가 아니라 `backend/.venv`입니다.
Git Bash에서는 `backend` 폴더에서 `source .venv/Scripts/activate`로 켭니다.
Vue/npm 명령은 `frontend/vue-app`에서 실행하며 Python `.venv`가 필요 없습니다.

사용자가 확인해야 할 사항, 설치해야 할 파일·라이브러리·프레임워크, 새로 추가되는 도구를 빠짐없이 알려주세요.
새 설치가 없으면 없다고 명확히 적어주세요.

git 명령은 프로젝트 루트에서 아래 형태의 한 줄 블록으로 주세요.

```bash
git status && git add . && git commit -m "..." && git push
```

필요한 라이브러리/파일 설치와 여러 단계 작업은 허용됩니다.
다만 DB/env/seed/인증/API body/route/write/migration/Docker volume처럼 위험한 작업은 작게 나누고 실제 결과를 확인한 뒤 진행하세요.

========================
현재 최신 기준
========================

- 최신 작업: `v290.postgres-backup-restore-preflight-gate`
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
실제 PostgreSQL 보존 기준
========================

사용자 컴퓨터에서 이전 읽기 전용 단계로 확인한 실제 결과:

```txt
Docker Compose project: upgraderpg
containers: running(2)
volume: upgraderpg_rpg_postgres_data
PostgreSQL: 16.14
DB: rpg_game / rpg_user
DB size: 12 MB
SQLAlchemy model tables: 22
public tables: 22
total rows: 748
alembic_version: 없음
current revision: 없음
health/db: HTTP 200, status=ok
classification: existing-schema-without-alembic-baseline
```

보존 대상 예시:

```txt
users: 1
user_profiles: 1
characters: 1
user_save_snapshots: 2
admin_change_logs: 13
```

현재 DB는 초기화 대상이 아니라 기존 데이터 보존형 Alembic baseline 대상입니다.

========================
v289 schema gate 상태
========================

v288 실제 차이는 아래 두 개였고 둘 다 PostgreSQL alias 표현 차이였습니다.

```txt
user_profiles.add_attack_speed: model=FLOAT, db=DOUBLE PRECISION
user_profiles.farm_atk_bonus: model=FLOAT, db=DOUBLE PRECISION
```

v289에서 아래 정규화를 추가했습니다.

```txt
FLOAT -> DOUBLE PRECISION
FLOAT(1..24) -> REAL
FLOAT(25..53) -> DOUBLE PRECISION
```

ZIP 제작 샌드박스에는 `psycopg`와 PostgreSQL/Docker client가 없어 실제 DB에 연결하지 못했습니다.
따라서 기호 컴퓨터에서 v289 checker를 다시 실행해 `structurally-equivalent`, 차이 0개인지 먼저 확인해야 합니다.

========================
v290 완료
========================

- `tools/check_postgres_backup_restore_preflight.py` 추가
- schema equivalence 차이 0개 선행 gate
- host/container `pg_dump`, `pg_restore`, `createdb`, `dropdb` 사용 가능 여부 확인
- backup 위치 `local-backups/postgres/` 확정
- 파일명 `rpg_game_YYYYMMDD_HHMMSS_KST_v290.custom.dump` 확정
- SHA-256 sidecar와 민감정보/Git/ZIP 제외 규칙 확정
- source DB `rpg_game` restore 금지
- restore rehearsal DB `rpg_game_restore_rehearsal_v290` 확정
- empty migration test DB `rpg_game_migration_empty_v290` 확정
- restore 전후 table/row/schema 비교 계획 확정
- 별도 빈 DB 최초 Alembic 검증 계획 확정
- 전용 smoke와 core smoke 등록
- `.gitignore`, `.dockerignore`에 `/local-backups/` 제외 규칙 추가
- 실제 backup/restore/DB 생성·삭제/migration은 실행하지 않음

========================
다음 첫 작업 — v291 후보
========================

1. `backend/.venv` 활성화
2. `python tools/check_postgres_schema_equivalence.py` 실제 결과 확인
3. 차이 0개이면 `python tools/check_postgres_backup_restore_preflight.py` 실행
4. `ready-for-user-approval` 여부와 selected execution mode 확인
5. `review-required` 또는 `connection-failed`이면 backup/migration으로 넘어가지 않음
6. 준비 완료여도 실제 backup 생성은 사용자에게 별도 승인 요청
7. 승인 전에는 `pg_dump`, `createdb`, `pg_restore`, `dropdb` 실제 명령 실행 금지
8. backup 생성 후에도 DB 생성/restore/삭제는 각각 별도 승인

========================
절대 변경/실행 금지
========================

사용자 명시 승인 전에는 다음을 변경하거나 실행하지 마세요.

- 원본 DB schema/data
- Docker container/volume 삭제
- `.env`
- seed
- 인증
- 기존 API route path/response body
- 실제 write 로직/Write Guard
- Preview/Apply request body
- Alembic revision 생성
- upgrade/downgrade/stamp
- 실제 backup/restore
- DB 생성/삭제

```txt
python scripts/setup_dev_db.py --reset
docker compose down -v
python -m alembic revision --autogenerate
python -m alembic upgrade head
python -m alembic downgrade
python -m alembic stamp head
pg_dump 실제 backup 명령
createdb 실제 DB 생성 명령
pg_restore 실제 restore 명령
dropdb 실제 DB 삭제 명령
```

========================
Contract/검증 원칙
========================

새 Contract가 필요할 때는 실제 현재 환경 결과를 먼저 수집하고, 환경 차이를 확인한 뒤 등록하세요.
Frontend/backend 목록, 반환 객체, parity, Admin ReadOnly 검사를 누락하지 마세요.

코드나 구조를 건드렸다면 최소 확인:

- 관련 전용 smoke
- JS 문법 검사
- `python -m compileall -q backend/app backend/scripts backend/alembic tools`
- `bash tools/run_smoke_core.sh`
- Vue 변경 시 `npm ci`와 `npm run build`
- ZIP 무결성 및 제외 파일 검사

항상 마지막 답변에는 다음 5개를 포함하세요.

1. 이번에 한 일
2. 검증 완료한 것
3. 서버 재실행 명령 — 실행 위치와 `.venv` 상태 포함
4. git 명령 — 프로젝트 루트에서 한 줄
5. 다음 추천 단계

작업 후에는 새 ZIP도 같이 만들어주세요.
