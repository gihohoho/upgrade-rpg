# Upgrade RPG

현재 기준: **v311.production-capacity-tls-network-isolated-plan**

## 현재 구조

- legacy 게임: `index.html`
- legacy 관리자: `admin.html`
- legacy JS/CSS: `src/`
- Vue 앱: `frontend/vue-app/`
- FastAPI: `backend/`
- 운영 배포 검토 template: `deploy/`
- 실제 Python 가상환경: `backend/.venv`

게임 콘텐츠, Vue write/인증, 새 Alembic revision은 계속 보류합니다.

## PostgreSQL/Alembic

```txt
classification: alembic-managed-baseline-complete
source: public 23/749, application 22/748
current revision: v295_initial_schema
next revision candidate operations: 0
```

## Runtime

- v307 live DB health와 Docker readiness 통과
- v308 pool/lifecycle/production fail-closed/Dockerfile/Compose 적용
- v309 AST engine binding 검사 사용자 PC 통과
- v310 production secret/TLS/container 정적 template 검사 통과
- 남은 운영 경고 9개는 local/production 분리 항목

## v311 읽기 전용 검사

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_production_capacity_tls_network_plan.py --strict
```

현재 계산 기준은 backend 1 replica × 1 worker, pool 5 + overflow 10입니다. `max_connections` review 후보는 40이며 실제 DB에는 적용하지 않았습니다.

## 기본 검증

```bash
python -m compileall -q backend/app backend/scripts backend/alembic tools
bash tools/run_smoke_core.sh
```
