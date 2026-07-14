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
docs/current/LEGACY_PATH_DEPENDENCIES.md
```

이 도구는 새 contract가 아닙니다. Vue/FastAPI/DB 전환 전에 기존 legacy 경로를 움직여도 되는지 판단하기 위한 보조 도구입니다.

## PostgreSQL/Alembic readiness 보고서

실행 위치: 프로젝트 루트  
`.venv` 상태: 켜진 상태 권장

```bash
python tools/report_postgres_alembic_readiness.py --check
```

생성 문서:

```txt
docs/current/POSTGRES_ALEMBIC_READINESS.md
```

## PostgreSQL/Alembic 로컬 사전 점검

실행 위치: 프로젝트 루트  
`.venv` 상태: 켜진 상태

```bash
python tools/check_postgres_alembic_prerequisites.py
```

이 도구는 DB 접속, Docker 시작, `.env` 변경, migration 실행을 하지 않습니다. Docker와 Python 패키지/필수 파일 존재만 확인합니다.
