# PostgreSQL production capacity / TLS / network plan — v311 snapshot with v333 runtime evidence

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

아래 블록은 v311 정적 검토 당시 스냅샷이며 현재 실행 상태가 아닙니다.

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

## v333 isolated 실행 결과

기호의 별도 승인 뒤 exact digest pull과 isolated container 실행을 완료했습니다. host port·volume·actual DB connection 없이 internal network와 제한된 security option으로 `/api/v1/health`를 검증했고 모든 임시 자원을 정리했습니다. 따라서 production capacity 값, managed DB, provider CA, external edge network에는 변화가 없습니다. sanitized evidence는 `deploy/review/isolated-image-pull-validation-v333.json`에 있습니다. production deploy는 계속 별도 승인입니다.

## 읽기 전용 검사

```bash
python tools/check_production_capacity_tls_network_plan.py --strict
```
