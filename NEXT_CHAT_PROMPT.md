기호의 Upgrade RPG 프로젝트를 이어서 진행합니다.

이번에 첨부하는 최신 ZIP `rpg_v289_postgres_float_normalization_handoff_ready.zip`을 반드시 기준으로 작업해주세요.

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

- 최신 작업: `v289.postgres-float-type-normalization-handoff`
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
실제 PostgreSQL 상태
========================

사용자 컴퓨터에서 읽기 전용으로 확인한 실제 결과:

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
v288 실제 결과와 v289 수정
========================

v288 checker 실제 결과는 아래 두 차이뿐이었습니다.

```txt
user_profiles.add_attack_speed: model=FLOAT, db=DOUBLE PRECISION
user_profiles.farm_atk_bonus: model=FLOAT, db=DOUBLE PRECISION
```

PostgreSQL은 precision 없는 `FLOAT`를 `DOUBLE PRECISION`으로 취급합니다.
v289에서 schema checker의 타입 alias 정규화를 추가했습니다.

```txt
FLOAT -> DOUBLE PRECISION
FLOAT(1..24) -> REAL
FLOAT(25..53) -> DOUBLE PRECISION
```

이 수정은 비교 로직만 바꾸며 DB schema/data와 SQLAlchemy model은 변경하지 않았습니다.

v289 적용 후 첫 확인 명령:

실행 위치: `backend` 폴더
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_postgres_schema_equivalence.py
```

실제 다른 차이가 없다면 `structurally-equivalent`, 차이 0개가 기대되지만 반드시 실제 결과를 먼저 확인하세요.

========================
v289 정리 사항
========================

- `tools/check_postgres_schema_equivalence.py` FLOAT alias 정규화
- schema equivalence smoke 보강
- 다음 채팅 handoff smoke를 현재 기준으로 갱신하고 core smoke에 등록
- 중복된 오래된 `tools/smoke_next_chat_handoff.py` 제거
- 생성 산출물 `backend/idle_rpg_backend.egg-info/` 제거
- `.gitignore`에 `*.egg-info/` 추가
- 동일 내용 중복 파일 `backend/env.example` 제거
- 실제 예시 파일은 `backend/.env.example` 하나로 유지
- 루트/current/handoff 문서 v289 동기화
- 전달 ZIP에서 `.git`, `backend/.venv`, `backend/.env`, `node_modules`, `dist`, cache 제외

========================
다음 첫 작업 — v290
========================

1. v289 checker의 사용자 실제 결과 확인
2. 차이 0개이면 backup/restore preflight 진행
3. backup 파일 위치·파일명·민감정보 보존 규칙 확정
4. `pg_dump`, `pg_restore`, `createdb`, `dropdb` 사용 가능 여부만 먼저 점검
5. 원본 `rpg_game`과 완전히 분리된 restore rehearsal DB 경계 확정
6. restore 전후 table/row count 비교 계획 작성
7. 별도 빈 DB 최초 Alembic migration 검증 계획 작성
8. 실제 backup/restore/DB 생성·삭제는 사용자 승인 후 작은 단계로 실행

alias 정규화 후에도 `review-required`가 나오면 backup/migration으로 넘어가지 말고 새로운 차이만 분석하세요.

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

```txt
python scripts/setup_dev_db.py --reset
docker compose down -v
python -m alembic revision --autogenerate
python -m alembic upgrade head
python -m alembic downgrade
python -m alembic stamp head
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
