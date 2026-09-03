# tools

이 폴더는 Upgrade RPG 프로젝트의 검증/보조 스크립트를 모아둔 곳입니다.

## 핵심 smoke

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
```

## 전체 smoke

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_all.sh
```

## backend readiness 확인

실행 위치: 프로젝트 루트

```bash
python tools/check_backend_ready.py
```

## legacy 경로 의존성 보고서

v269에서 추가한 구조 전환 보조 도구입니다.

실행 위치: 프로젝트 루트

```bash
python tools/report_legacy_path_dependencies.py --write
```

보고서가 최신인지 확인할 때:

실행 위치: 프로젝트 루트

```bash
python tools/report_legacy_path_dependencies.py --check
```

생성되는 문서:

```txt
docs/generated/LEGACY_PATH_DEPENDENCIES.md
```

이 도구는 새 contract가 아닙니다. Vue/FastAPI/DB 전환 전에 기존 legacy 경로를 움직여도 되는지 판단하기 위한 보조 도구입니다.

## Vue game domain 의존성 보고서

실행 위치: 프로젝트 루트
Python `.venv` 상태: 필요 없음

```bash
python tools/report_vue_game_domain_dependencies.py
python tools/report_vue_game_domain_dependencies.py --check
node tools/smoke/frontend/smoke_vue_game_domain_foundation.js
```

`docs/generated/VUE_GAME_DOMAIN_DEPENDENCIES.md`에 legacy state·systems·rules의 browser·난수·시각·timer 의존성과 v384 typed domain 분리 경계를 기록합니다. v385~v392 smoke는 마을/HUD·필드·보스·가방/장비·보관함/휴지통·스킬/강화·상점/설정 adapter와 legacy형 좌우 창·utility/mobile modal·가독성 계층이 snapshot load/save·전투 timer·난수·아이템/스킬/Gold/재료·영구 설정을 바꾸지 않는지 확인합니다. 검사는 DB·서버·배포를 변경하지 않습니다.

## PostgreSQL/Alembic readiness 보고서

실행 위치: 프로젝트 루트  
`.venv` 상태: 켜진 상태 권장

```bash
python tools/report_postgres_alembic_readiness.py --check
```

생성 문서:

```txt
docs/generated/POSTGRES_ALEMBIC_READINESS.md
```

## PostgreSQL/Alembic 로컬 사전 점검

실행 위치: 프로젝트 루트  
`.venv` 상태: 켜진 상태

```bash
python tools/check_postgres_alembic_prerequisites.py
```

이 도구는 DB 접속, Docker 시작, `.env` 변경, migration 실행을 하지 않습니다. Docker와 Python 패키지/필수 파일 존재만 확인합니다.

## PostgreSQL runtime 읽기 전용 상태

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_postgres_runtime_readonly_state.py
```

Windows Docker 출력은 `tools/_safe_subprocess.py`가 UTF-8/cp949 혼합 환경에서도 안전하게 처리합니다.

## PostgreSQL / SQLAlchemy schema 동등성 점검

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_postgres_schema_equivalence.py
```

이 도구는 columns/types/nullability/PK/FK/unique/index/check를 읽기 전용으로 비교하며 schema/data와 Alembic 이력을 변경하지 않습니다.

## 승인된 PostgreSQL backup 생성/검증

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/create_postgres_backup.py --execute
```

이 도구는 실행 직전에 schema/preflight gate를 다시 확인하고, `rpg_game` custom dump를 `local-backups/postgres/`에 생성한 뒤 `pg_restore --list`, SHA-256, source count snapshot, manifest를 검증합니다.

- `.dump`는 민감 데이터이므로 업로드/Git/전달 ZIP 포함 금지
- restore, DB 생성/삭제, Docker resource 변경, `.env`, Alembic mutation은 실행하지 않음
- `--execute`가 없으면 실제 파일을 만들지 않음

- `downgrade_postgres_migration_test_database.py`: 검토된 isolated migration DB를 base로 downgrade하고 source/rehearsal 보존을 검증합니다.


## 원본 baseline stamp 읽기 전용 preflight

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_postgres_source_baseline_stamp_preflight.py --strict
```

이 도구는 verified backup, restore rehearsal, reviewed revision, isolated migration 왕복 결과와 현재 source schema/data를 읽기 전용으로 대조합니다. `stamp`, `upgrade`, `downgrade`, DB 생성·삭제·복원, `.env` 변경, row write를 실행하지 않습니다. 통과 후 다음 단계도 원본 DB가 아니라 restore rehearsal DB stamp 검증부터 별도 승인으로 진행합니다.

## PostgreSQL baseline 완료 상태 읽기 전용 확인

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_postgres_baseline_completion_state.py --strict
```

이 도구는 source/rehearsal/migration DB, v302/v304 실행 보고서, application digest, exact revision 파일 집합을 읽기 전용으로 확인합니다. stamp 재실행, revision 생성, autogenerate, upgrade, downgrade, DB create/drop/restore, row write를 실행하지 않습니다.
