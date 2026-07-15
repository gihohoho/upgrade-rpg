기호의 Upgrade RPG 프로젝트를 이어서 진행합니다.

이번에 첨부하는 최신 ZIP `rpg_v306_postgres_next_revision_readonly_preflight_ready.zip`을 반드시 기준으로 작업해주세요.

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

사용자가 확인해야 할 사항, 설치해야 할 파일·라이브러리·프레임워크, 새로 추가되는 도구를 빠짐없이 알려주세요.
새 설치가 없으면 없다고 명확히 적어주세요.

git 명령은 프로젝트 루트에서 아래 형태의 한 줄 블록으로 주세요.

```bash
git status && git add . && git commit -m "..." && git push
```

필요한 라이브러리/파일 설치와 여러 단계 작업은 허용됩니다.
다만 DB/env/seed/인증/API body/route/write/migration/Docker volume처럼 위험한 작업은 작은 승인 경계로 진행하고 실제 결과를 확인한 뒤 다음 단계로 넘어가세요.

========================
현재 최신 기준
========================

- 최신 작업: `v306.postgres-next-revision-readonly-preflight`
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
실제 PostgreSQL/Alembic 완료 상태
========================

원본 DB:

```txt
DB: rpg_game
owner/user: rpg_user
PostgreSQL: 16.14
public tables/rows: 23/749
application tables/rows: 22/748
schema: structurally-equivalent / differences=0
alembic_version: 있음 / 1 row
current revision: v295_initial_schema
runtime classification: alembic-managed
project classification: alembic-managed-baseline-complete
v304 source execution report: verified
v305 completion check: postgres-baseline-completion-state-verified
```

검증된 backup:

```txt
file: local-backups/postgres/rpg_game_20260714_130403_KST_v290.custom.dump
SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
TOC definitions/data: 22 / 22
```

복원 리허설 DB:

```txt
DB: rpg_game_restore_rehearsal_v290
public tables/rows: 23/749
application tables/rows: 22/748
current revision: v295_initial_schema
v302 execution report: verified
```

migration 테스트 DB:

```txt
DB: rpg_game_migration_empty_v290
public tables/rows: 23/1
model tables: 22
current revision: v295_initial_schema
schema: structurally-equivalent / differences=0
```

최초 revision:

```txt
revision ID: v295_initial_schema
revision file: backend/alembic/versions/v295_initial_schema_initial_postgresql_schema.py
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
manual review: passed
create_table/create_index: 22 / 42
drop_table/drop_index: 22 / 42
```

사용자 PC 실제 완료:

```txt
v298 upgrade head: 성공
v299 downgrade base: 성공
v300 second upgrade head: 성공
first/second upgrade signatures: identical
v301 source preflight: 통과
v302 rehearsal stamp: 통과
v303 rehearsal post-check: 통과 / report verified
v303 result: restore-rehearsal-stamp-current-state-verified
v304 source stamp: 통과
v304 source post-check: source-baseline-stamp-current-state-verified
v304 source execution report: verified
v305 completion check: postgres-baseline-completion-state-verified
```

승인 application digest:

```txt
schema digest: 7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921
data digest: ecb19e57283dc6b780426339bfc46f2bac14da63a618249808f30132508f9244
```

필수 로컬 증거는 Git/전달 ZIP/채팅에 포함하지 않습니다.

```txt
local-backups/
local-review-artifacts/alembic/v295_initial_schema.upgrade-v298.json
local-review-artifacts/alembic/v295_initial_schema.downgrade-v299.json
local-review-artifacts/alembic/v295_initial_schema.roundtrip-upgrade-v300.json
local-review-artifacts/alembic/v295_initial_schema.restore-rehearsal-stamp-v302.json
local-review-artifacts/alembic/v295_initial_schema.source-stamp-v304.json
```

========================
v306 next revision read-only preflight
========================

추가 파일:

```txt
tools/check_postgres_next_revision_preflight.py
tools/smoke/backend/smoke_postgres_next_revision_preflight.py
docs/current/POSTGRES_NEXT_REVISION_PREFLIGHT.md
docs/current/POSTGRES_NEXT_REVISION_READONLY_PLAN.md
```

preflight는 다음을 읽기 전용으로 확인합니다.

- v305 baseline completion 유지
- Alembic graph single base/single head
- exact reviewed revision 1개
- 승인 SQLAlchemy model/Alembic env source snapshot 13개
- canonical schema 22/22, differences=0
- PostgreSQL read-only transaction + SQL write guard
- Alembic `compare_metadata()` candidate operations
- type/server default/nullable/index/constraint 비교
- integer PK sequence ownership과 unowned sequence

이 도구는 Alembic CLI의 revision/autogenerate/upgrade/downgrade/stamp를 호출하지 않습니다.

========================
다음 첫 작업 — 읽기 전용 v306 next-revision preflight
========================

실행 위치: `backend` 폴더
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_postgres_next_revision_preflight.py --strict
```

정상 변경 없음 기대 핵심:

```txt
baseline completion: postgres-baseline-completion-state-verified
exact source DB: rpg_game
source current revision: ['v295_initial_schema']
Alembic graph heads/bases: ['v295_initial_schema']/['v295_initial_schema']
approved model source snapshot: matched / 13 files
SQLAlchemy metadata tables: 22
canonical schema: structurally-equivalent / differences=0
Alembic candidate operations: 0
next revision required: no
result: next-revision-not-required-current-schema-equivalent
next safe stage: keep-single-baseline-no-new-revision
```

후보가 있으면 `next-revision-review-required-schema-differences-detected`로 중지하고 자동 생성하지 않습니다.

이 명령은 revision 생성, autogenerate CLI, stamp, upgrade, downgrade, DB create/drop/restore, row write를 실행하지 않습니다.

========================
다음 단계 안전 순서
========================

1. v306 next-revision preflight 실제 결과 확인
2. candidate operation 0개면 새 revision 생성하지 않음
3. 후보가 있으면 table/column/index/FK/default/nullable 변경 의도 검토
4. 기존 748개 row 영향과 data migration 필요 여부 확인
5. autogenerate는 사용자 별도 승인 전 금지
6. 향후 revision은 isolated migration DB에서 먼저 검토·왕복
7. source 적용은 다시 별도 승인

========================
절대 변경/실행 금지
========================

- source/rehearsal stamp 재실행
- 새 Alembic revision 생성/autogenerate
- source/rehearsal/migration upgrade/downgrade
- DB 생성/삭제/복원
- Docker container/volume 삭제
- `.env`
- seed
- 인증
- 기존 API route path/response body
- 실제 write 로직/Write Guard
- Preview/Apply request body
- 게임 콘텐츠/밸런스 변경

```txt
python scripts/setup_dev_db.py --reset
docker compose down -v
python -m alembic revision --autogenerate
python -m alembic upgrade head
python -m alembic downgrade
python -m alembic stamp head
createdb
dropdb
pg_restore
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

작업 후에는 다음 5개를 포함해 답변하세요.

1. 이번에 한 일
2. 검증 완료한 것
3. 서버 재실행 명령 — 실행 위치와 `.venv` 상태 포함
4. git 명령 — 프로젝트 루트에서 한 줄
5. 다음 추천 단계

코드 또는 문서를 변경했다면 새 ZIP도 같이 만들어주세요.
