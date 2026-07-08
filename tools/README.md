# tools

이 폴더는 개발/검증용 보조 스크립트를 모아둔 곳입니다.
게임 실행 코드에는 직접 포함되지 않습니다.

## 빠른 smoke test

자주 쓰는 핵심 검사만 실행합니다.

```bash
# 위치: 프로젝트 루트
bash tools/run_smoke_core.sh
```

전체 smoke test를 실행합니다.

```bash
# 위치: 프로젝트 루트
bash tools/run_smoke_all.sh
```

## 백엔드 live check

FastAPI 서버와 Docker PostgreSQL이 켜져 있을 때 실행합니다.

```bash
# 위치: backend 폴더 + 가상환경 activate 상태
python scripts/check_admin_readonly_api.py
```

## 기타 주요 도구

```txt
check_backend_ready.py        로컬 백엔드/Docker/PostgreSQL 준비 상태 점검
extract_seed_data.js          현재 JS 마스터 데이터를 JSON seed로 추출
smoke_*.js / smoke_*.py       단계별 정적 smoke test
```
