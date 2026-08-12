# Managed PostgreSQL / reverse proxy HTTPS selection — current through v321

## 확정한 운영 기본 방향

```txt
database mode: managed-postgresql-selected
database TLS: verify-full-with-provider-ca
public entrypoint: external-reverse-proxy-https-selected
backend replicas/workers: 1/1
backend 1 replica / 1 worker
reverse proxy product: deferred
config render approved: yes
config render executed on user PC: yes
image pull/build approved: no
container start approved: no
actual production values applied: no
```

이 선택은 실제 관리형 DB 계정을 만들거나 secret을 입력했다는 뜻이 아닙니다. repository의 운영 template과 승인 경계를 이 방향에 맞게 고정한 상태입니다.

## 관리형 PostgreSQL 경계

운영 Compose에는 bundled PostgreSQL service와 DB volume이 없습니다. backend는 향후 선택할 관리형 공급자의 TLS endpoint로만 연결합니다.

필수 조건:

- 관리형 DB hostname과 인증서 이름 일치
- `sslmode=verify-full`
- 승인된 provider CA를 `/run/secrets/postgres_ca.pem`으로 mount
- 실제 username/password/hostname은 배포 platform secret에서 주입
- private network 또는 IP allowlist에는 승인된 backend egress만 허용
- provider connection limit가 v311 계산값과 맞는지 확인
- backup/PITR, maintenance window, region, 비용 검토

현재 계산 기준:

```txt
backend replicas/workers: 1/1
pool size/max overflow: 5/10
application burst: 15
non-application reserve: 10
recommended minimum max_connections: 30
review candidate max_connections: 40
```

`40`은 실제 적용값이 아니라 provider 상품 비교 후보입니다.

## 외부 reverse proxy HTTPS 경계

- 외부 공개 진입점은 HTTPS `443`
- backend `8000` host publish 금지
- proxy와 backend는 사전에 생성된 external edge network로 연결
- proxy upstream은 `http://backend:8000`
- HTTP `80`은 사용할 경우 HTTPS redirect 전용
- DNS, certificate, ACME, proxy image/product는 아직 미선택

제품은 아직 고정하지 않습니다. 제품 선택 전에도 backend host port 비공개와 HTTPS-only 공개 계약은 유지됩니다.

## config render-only 실제 결과

기호 PC에서 안전 wrapper가 정상 통과했습니다.

```txt
rendered services: backend
host ports/build/named volumes absent: True/True/True
managed DB service absent / backend replicas: True/1
digest/production guard/TLS/edge rendered: True/True/True/True
image pull/build executed: no
container/network/volume mutation executed: no
DB/Alembic mutation executed: no
result: production-compose-config-render-verified-no-runtime-mutation
```

안전 요약은 `deploy/review/production-compose-config-render-v312.json`에 기록했고 raw render는 저장하지 않았습니다.

## backend image 경계

production Compose는 `build:`를 사용하지 않고 digest-pinned `BACKEND_IMAGE`를 요구합니다.

```txt
ghcr.io/gihohoho/upgrade-rpg-backend@sha256:f3bf6eed45e46e9d2022df4ab62eb6ca55b1ec0997b8ed342ae250c4a60052c1
```

registry, namespace, target platform, base image digest는 아직 선택하지 않았습니다. 따라서 pull/build/push는 실행하지 않습니다.

## 다음 안전 단계

```txt
review-render-report-and-approve-backend-image-source-digest
```

현재 이미지와 credential 판단은 `BACKEND_IMAGE_GHCR_POLICY.md`를 우선합니다.

## 계속 차단

```txt
actual production env/secret/CA/certificate/key creation: no
registry credential application: no
managed DB connection/query: no
image pull/build/push: no/no/no
container create/start/stop/remove: no
network/volume create/remove: no
Alembic revision/stamp/upgrade/downgrade: no
DB create/drop/restore/reset/seed: no
```

## 읽기 전용 정적 검사

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_production_managed_postgres_reverse_proxy_selection.py --strict
```

정상 결과:

```txt
compose config render approved/executed: yes/yes
result: managed-postgresql-reverse-proxy-selection-verified-config-render-complete
next safe stage: review-render-report-and-approve-backend-image-source-digest
```
