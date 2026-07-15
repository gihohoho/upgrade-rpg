# PostgreSQL production capacity / TLS / network plan — current through v320

## 목적

현재 backend 1 replica / 1 worker와 SQLAlchemy pool 설정을 기준으로 관리형 PostgreSQL connection capacity와 network/TLS 경계를 유지합니다. 실제 DB 설정이나 Docker resource를 적용하지 않습니다.

## 용량 계산

```txt
backend replicas: 1
Uvicorn workers per replica: 1
SQLAlchemy engines: 1
pool size: 5
max overflow: 10
application steady/burst: 5/15
migration + monitoring + admin + other reserve: 10
planned peak before safety: 25
safety margin: 20%
recommended minimum: 30
review candidate max_connections: 40
candidate spare after planned peak: 15
future 2 replicas minimum: 50
future 2 replicas x 2 workers minimum: 90
```

`40`은 관리형 PostgreSQL 상품 비교 후보이며 실제 적용값이 아닙니다.

## TLS와 network 선택

```txt
database mode: managed-postgresql-selected
bundled PostgreSQL TLS: deferred/not used in selected architecture
public entrypoint: external reverse proxy
public HTTPS: HTTPS `443`
backend host port: none
database host port: none
```

provider CA와 `sslmode=verify-full`을 사용하고 backend는 external edge network에서만 reverse proxy와 통신합니다.

## 승인 상태

```txt
config render approved: yes
config render executed on user PC: yes
image pull/build approved: no
isolated container execution approved: no
actual production values applied: no
```

config render의 안전 요약은 `deploy/review/production-compose-config-render-v312.json`에 있습니다.

## 다음 안전 단계

```txt
select-registry-repository-platform-and-base-image-digest
```

registry/provider/platform/base image digest를 선택해도 pull/build/push는 각각 별도 승인합니다.

## 읽기 전용 검사

```bash
python tools/check_production_capacity_tls_network_plan.py --strict
```
