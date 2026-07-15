# NEXT CHAT HANDOFF — Upgrade RPG v312

## 기준 ZIP

- `rpg_v312_managed_postgres_reverse_proxy_config_render_ready.zip`

## 현재 기준

- 최신 작업: `v312.production-managed-postgres-reverse-proxy-config-render-ready`
- readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

## PostgreSQL/Alembic 고정 상태

```txt
classification: alembic-managed-baseline-complete
source rpg_game: public 23/749, application 22/748
current revision: v295_initial_schema
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
v305 completion: passed
v306 candidate operations: 0 / next revision required no
```

source/rehearsal stamp, 새 revision, upgrade/downgrade는 다시 실행하지 않습니다.

## Runtime 고정 상태

```txt
v307 live DB health and local Docker readiness: passed
v308 pool/lifecycle/production guard/Dockerfile/Compose: applied
v309 runtime engine AST inspector: passed
v310 production static validation baseline: passed
remaining local production warnings: 9
```

## v312 확정

기호 승인:

```txt
database: managed-postgresql-selected
TLS: verify-full-with-provider-ca
public entrypoint: external-reverse-proxy-https-selected
backend replicas/workers: 1/1
reverse proxy product: deferred
```

변경 내용:

- production Compose를 backend-only로 변경
- bundled PostgreSQL/Adminer/named DB volume/host port/build 제거
- digest-pinned `BACKEND_IMAGE` 필수
- provider CA Compose secret과 external edge network 필수
- `deploy/production-architecture-selection.example.json` 추가
- `deploy/reverse-proxy/README.md` 추가
- `tools/check_production_managed_postgres_reverse_proxy_selection.py` 추가
- `tools/render_production_compose_config.py` 추가
- 전용 fail-closed smoke 2개 추가
- config render approved: yes
- config render executed on user PC: no
- pull/build/container start approved: no

handoff 제작 환경에는 Docker CLI가 없어 실제 `docker compose config`를 실행하지 못했습니다. fake Docker smoke로 wrapper가 config 이외 명령을 호출하지 않는 것은 검증했습니다.

## 다음 첫 작업

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_production_managed_postgres_reverse_proxy_selection.py --strict
```

정상 결과 핵심:

```txt
database/TLS mode: managed-postgresql-selected / verify-full-with-provider-ca
public entrypoint: external-reverse-proxy-https-selected
backend replicas/workers: 1/1
compose config render approved/executed: yes/no
result: managed-postgresql-reverse-proxy-selection-verified-config-render-approved
next safe stage: run-config-render-only-on-docker-capable-host
```

그다음 같은 위치/가상환경에서 승인된 config render-only:

```bash
python tools/render_production_compose_config.py --execute --confirm-stage v312-config-render-only
```

정상 결과 핵심:

```txt
rendered services: backend
host ports/build/named volumes absent: True/True/True
managed DB service absent / backend replicas: True/1
image pull/build executed: no
container/network/volume mutation executed: no
DB/Alembic mutation executed: no
result: production-compose-config-render-verified-no-runtime-mutation
next safe stage: review-render-report-and-approve-backend-image-source-digest
```

실행 결과를 그대로 전달받은 뒤 다음 단계로 갑니다.

## 다음 안전 순서

1. config render 결과 검토
2. backend image registry/source/base image/digest 기록 형식 결정
3. 별도 승인 후 pull 또는 build를 각각 작은 경계로 진행
4. 관리형 PostgreSQL provider/region/private network/connection limit 선택
5. reverse proxy 제품/DNS/certificate 운영 방식 선택
6. isolated start와 cleanup 각각 별도 승인

## 계속 금지

- 실제 `backend/.env`, production env, JWT/Admin secret 변경
- 실제 password/CA/cert/key 파일 생성·입력·커밋
- Docker pull/build/up/down/run/start/stop/rm
- Docker container/network/volume 생성·변경·삭제
- managed PostgreSQL 실제 연결/query/설정 변경
- source/rehearsal stamp 재실행
- Alembic revision/autogenerate/upgrade/downgrade
- DB create/drop/restore/reset/seed
- 인증/API route path/response body/write logic
- Vue Preview/Apply/write 연결
- 게임 콘텐츠/밸런스 변경
