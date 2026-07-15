# PostgreSQL production capacity / TLS / network plan — v311

## 목적

v310 정적 template 검증을 통과한 상태에서 실제 운영 secret, Docker, DB, Alembic을 건드리지 않고 다음 운영 결정을 숫자와 승인 경계로 고정합니다.

- FastAPI worker와 SQLAlchemy pool이 요구하는 PostgreSQL 연결 수 계산
- PostgreSQL `max_connections` 후보값 계산
- bundled PostgreSQL TLS와 관리형 PostgreSQL 선택 기준
- reverse proxy / HTTPS / network allowlist 경계
- isolated container 검증의 실행 전 단계 구분

이 문서는 **계획 및 정적 검증 전용**입니다. 계산값은 실제 DB에 적용되지 않습니다.

## 현재 코드에서 확인되는 실행 단위

```txt
backend container replicas: 1
Uvicorn workers per replica: 1
SQLAlchemy engine count: 1
DB_POOL_SIZE per worker: 5
DB_MAX_OVERFLOW per worker: 10
application steady connections: 5
application burst connections: 15
```

현재 `backend/Dockerfile`의 Uvicorn 명령에는 `--workers`가 없으므로 container당 worker는 1개입니다. SQLAlchemy engine은 Python process마다 하나이므로 worker 또는 replica를 늘리면 pool도 같은 비율로 늘어납니다.

## v311 기준 계산식

```txt
engine_count = backend_replicas × uvicorn_workers_per_replica
application_steady = engine_count × DB_POOL_SIZE
application_burst = engine_count × (DB_POOL_SIZE + DB_MAX_OVERFLOW)
non_application_reserve = migration + monitoring + admin_emergency + other_reserved
raw_recommendation = ceil((application_burst + background_burst + non_application_reserve) × 1.20)
recommended_minimum = raw_recommendation을 10 단위로 올림
```

현재 review-only 입력값:

```txt
application burst: 15
non-application reserve: 10
20% safety 포함 raw: 30
recommended minimum: 30
review candidate max_connections: 40
candidate spare above recommended minimum: 10
```

`40`은 실제 PostgreSQL 설정값이 아니라 첫 isolated 검증 전에 검토할 후보입니다. 관리형 DB의 상품별 connection limit 또는 bundled PostgreSQL의 실제 `max_connections`, 메모리, workload를 확인한 후 별도 승인해야 합니다.

## 확장 시나리오

| 시나리오 | replicas | workers/replica | app burst | 동일 reserve와 20% 여유 기준 최소 후보 |
|---|---:|---:|---:|---:|
| 현재 단일 process | 1 | 1 | 15 | 30 |
| backend 2 replicas | 2 | 1 | 30 | 50 |
| 2 replicas × 2 workers | 2 | 2 | 60 | 90 |

worker/replica를 늘리기 전에 pool을 먼저 재계산해야 합니다. 단순히 worker만 늘리면 PostgreSQL 연결 수가 예상보다 빠르게 증가합니다.

## TLS 선택 기준

### 우선 검토안: 관리형 PostgreSQL

현재 v311 계획의 우선 검토값은 `managed-postgresql-preferred`입니다.

장점:

- 서버 인증서 발급·교체와 TLS endpoint 운영 책임을 공급자가 담당
- hostname verification과 공급자 CA를 이용한 `verify-full` 검증 경계가 명확함
- DB container와 데이터 volume을 애플리케이션 host에서 직접 운영하지 않아도 됨

확인 필요:

- 승인된 CA 획득 경로와 rotation 절차
- private network 또는 IP allowlist
- connection limit와 pooler 제공 여부
- backup/PITR, maintenance, region, 비용
- 운영 hostname이 인증서 이름과 일치하는지

### 대안: bundled PostgreSQL TLS

bundled PostgreSQL을 선택할 경우 아래가 모두 별도 설계·승인되어야 합니다.

- PostgreSQL server certificate와 private key
- CA chain과 파일 권한
- `ssl=on`, `ssl_cert_file`, `ssl_key_file`, 필요 시 `ssl_ca_file`
- 인증서 교체와 reload/restart 절차
- DB container/volume backup·restore·upgrade 책임
- host 또는 reverse proxy에서 PostgreSQL port를 공개하지 않는 내부 network 경계

현재 production Compose는 bundled PostgreSQL TLS server 설정을 완료한 상태가 아니므로 실행하면 안 됩니다.

## reverse proxy / HTTPS / network 경계

- 외부 공개 진입점은 reverse proxy의 HTTPS `443`만 허용합니다.
- HTTP `80`을 열 경우 HTTPS redirect 전용으로만 사용합니다.
- FastAPI `8000`은 host에 직접 공개하지 않고 `edge` network 내부에서 proxy만 접근합니다.
- PostgreSQL `5432`는 `backend_internal` network에서 backend만 접근합니다.
- Adminer는 운영 구성에 포함하지 않습니다.
- 관리형 DB를 사용할 경우 DB allowlist/private network에는 backend egress만 허용합니다.
- proxy가 전달하는 client IP/protocol header는 신뢰 proxy 범위를 제한한 뒤에만 사용합니다.
- CORS origin은 실제 승인된 HTTPS origin만 명시합니다.
- TLS certificate/key는 Git, ZIP, image, Docker build context에 포함하지 않습니다.

아직 reverse proxy 제품과 실제 DNS/certificate는 선택하거나 적용하지 않았습니다.

## image digest 승인 경계

- `POSTGRES_IMAGE`의 `<approved-64-hex-digest>`는 실제 digest로 아직 교체하지 않습니다.
- backend base image와 PostgreSQL image 모두 공급 source, tag, digest, 확인 날짜를 기록합니다.
- 승인된 digest로만 isolated pull/build를 진행합니다.
- digest 변경은 자동 반영하지 않고 재검토합니다.

## 다음 isolated container 승인 단계

상세 명령과 중단 조건은 `deploy/isolated-validation/README.md`에 기록합니다.

현재 승인 상태:

```txt
actual production values applied: no
actual secret/CA/cert/key created: no
Docker config/build/pull/up/down executed: no
isolated container execution approved: no
DB/Alembic mutation approved: no
```

## 읽기 전용 검사

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태 권장

```bash
python tools/check_production_capacity_tls_network_plan.py --strict
```

정상 결과:

```txt
recommended/candidate max_connections: 30/40
TLS database mode: managed-postgresql-preferred
reverse proxy only / DB internal: True/True
isolated container execution approved: no
result: production-capacity-tls-network-plan-verified-execution-blocked
next safe stage: approve-provider-and-isolated-container-config-render-only
```
