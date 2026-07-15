# PostgreSQL production capacity / TLS / network plan — v311 calculation, v312 selection

## 목적

v311에서 계산한 worker/pool/`max_connections` 기준을 유지하면서, v312에서 기호가 승인한 관리형 PostgreSQL과 외부 reverse proxy HTTPS 방향을 현재 계약으로 고정합니다. 이 문서는 실제 DB 설정이나 Docker resource를 적용하지 않습니다.

## 현재 실행 단위

```txt
backend replicas: 1
Uvicorn workers per replica: 1
SQLAlchemy engine count: 1
DB_POOL_SIZE per worker: 5
DB_MAX_OVERFLOW per worker: 10
application steady connections: 5
application burst connections: 15
```

현재 `backend/Dockerfile`의 Uvicorn command에는 `--workers`가 없으므로 worker는 1개입니다. production Compose에도 `replicas: 1`을 명시했습니다.

## 계산식과 현재 후보

```txt
engine_count = replicas × workers
application_burst = engine_count × (pool_size + max_overflow)
non_application_reserve = migration + monitoring + admin_emergency + other
raw = ceil((application_burst + reserve) × 1.20)
recommended_minimum = raw를 10 단위로 올림
```

현재 review-only 값:

```txt
application burst: 15
non-application reserve: 10
safety margin: 20%
recommended minimum: 30
review candidate max_connections: 40
candidate spare after planned peak: 15
```

`40`은 관리형 DB 상품의 connection limit를 비교하기 위한 후보일 뿐 실제 적용값이 아닙니다.

## 확장 시나리오

| 시나리오 | replicas | workers/replica | app burst | 동일 reserve/여유 기준 최소 |
|---|---:|---:|---:|---:|
| 현재 | 1 | 1 | 15 | 30 |
| backend 2 replicas | 2 | 1 | 30 | 50 |
| 2 replicas × 2 workers | 2 | 2 | 60 | 90 |

replica 또는 worker를 늘리기 전에 provider connection limit와 pool을 다시 계산해야 합니다.

## v312 TLS/database 선택

현재 값은 `managed-postgresql-selected`입니다.

관리형 PostgreSQL 필수 조건:

- provider hostname과 인증서 이름 일치
- `sslmode=verify-full`
- provider CA mount
- private network 또는 backend egress IP allowlist
- backup/PITR와 maintenance 정책 확인
- connection limit가 최소 30, review 후보 40을 수용하는지 확인

bundled PostgreSQL TLS는 대안 검토 기록으로만 남깁니다. server certificate/private key/rotation/backup/upgrade 책임이 모두 별도로 승인되지 않는 한 production Compose에 다시 넣지 않습니다.

## reverse proxy / HTTPS / network

현재 public entrypoint는 `external-reverse-proxy-https-selected`입니다.

- 외부 진입은 HTTPS `443`
- backend `8000` host publish 없음
- production Compose는 external `edge` network 이름을 요구
- proxy upstream은 `http://backend:8000`
- 관리형 DB는 Compose network가 아니라 provider private endpoint/allowlist로 보호
- reverse proxy 제품/DNS/certificate는 아직 선택하지 않음

## 현재 승인 상태

```txt
config render approved: yes
config render executed on user PC: no
image pull/build approved: no
isolated container execution approved: no
actual production values applied: no
```

handoff 환경에는 Docker CLI가 없어 실제 config 명령은 실행하지 못했습니다. 다음 안전 단계는 `run-config-render-only-on-docker-capable-host`입니다.

## 읽기 전용 검사

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_production_capacity_tls_network_plan.py --strict
```

정상 결과:

```txt
recommended/candidate max_connections: 30/40
future 2-replica / 2x2-worker minimums: 50/90
TLS database mode: managed-postgresql-selected
reverse proxy only / managed DB boundary: True/True
compose config render approved/executed: yes/no
result: production-capacity-tls-network-plan-verified-execution-blocked
next safe stage: run-config-render-only-on-docker-capable-host
```
