# Managed PostgreSQL / reverse proxy HTTPS selection — v312

## 확정한 운영 기본 방향

기호의 승인에 따라 다음을 운영 기본 방향으로 확정했습니다.

```txt
database mode: managed-postgresql-selected
database TLS: verify-full-with-provider-ca
public entrypoint: external-reverse-proxy-https-selected
backend replicas/workers: 1/1
backend 1 replica / 1 worker
reverse proxy product: deferred
compose config render approved: yes
compose config render executed on user PC: no
image pull/build approved: no
container start approved: no
actual production values applied: no
```

이 선택은 실제 관리형 DB 계정을 만들거나 secret을 입력했다는 뜻이 아닙니다. 현재는 repository의 운영 template과 승인 경계를 이 방향에 맞게 고정한 상태입니다.

## 관리형 PostgreSQL 경계

운영 Compose에서 bundled PostgreSQL service와 PostgreSQL data volume을 제거했습니다. backend는 선택할 관리형 공급자의 TLS endpoint로만 연결합니다.

필수 조건:

- 관리형 DB hostname이 인증서 이름과 일치
- `sslmode=verify-full`
- 공급자가 승인한 CA를 `/run/secrets/postgres_ca.pem`으로 mount
- 실제 username/password/hostname은 배포 platform의 secret에서 주입
- private network 또는 IP allowlist에는 backend의 승인된 egress만 허용
- provider connection limit가 v311 계산값과 맞는지 확인
- backup/PITR, maintenance window, region, 비용을 provider 선택 전에 확인

현재 계산 기준:

```txt
backend replicas/workers: 1/1
backend 1 replica / 1 worker
pool size/max overflow: 5/10
application burst: 15
non-application reserve: 10
recommended minimum max_connections: 30
review candidate max_connections: 40
```

`40`은 provider 상품 선택 시 비교할 review 후보일 뿐 실제 적용값이 아닙니다.

## 외부 reverse proxy HTTPS 경계

- 외부 공개 진입점은 HTTPS `443`
- backend `8000` host publish 금지
- proxy와 backend는 사전에 생성된 external edge network로 연결
- proxy upstream은 `http://backend:8000`
- HTTP `80`은 사용할 경우 HTTPS redirect 전용
- DNS, certificate, ACME, proxy image/product는 아직 미선택

제품을 아직 `deferred`로 둔 이유는 배포 위치에 따라 관리형 ingress, Caddy, Nginx 등의 책임 범위가 달라지기 때문입니다. 제품 선택 전에도 backend host port 비공개와 HTTPS-only 공개 계약은 고정할 수 있습니다.

## backend image 경계

production Compose는 이제 `build:`를 사용하지 않고 digest-pinned `BACKEND_IMAGE`를 요구합니다.

```txt
<approved-registry>/upgrade-rpg-backend@sha256:<approved-64-hex-digest>
```

실제 registry, image source, base image digest는 아직 승인하지 않았습니다. 따라서 pull/build도 실행하지 않습니다.

## config render-only 승인

현재 승인된 Docker 범위는 container를 만들지 않는 `docker compose config`뿐입니다.

프로젝트 wrapper는 실제 `.env`와 secret을 읽지 않고 임시 review sentinel을 만든 뒤 정확히 config만 호출합니다. raw render 결과는 파일로 저장하지 않습니다.

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

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

## 현재 실행 환경의 한계

handoff ZIP을 만든 환경에는 Docker CLI가 없어 실제 `docker compose config`를 실행하지 못했습니다. 대신 다음을 완료했습니다.

- Compose YAML 구조 검사
- v312 정적 selection checker
- render wrapper의 fake Docker smoke
- 실제 Docker가 없을 때 fail-closed 동작 확인

따라서 다음 첫 작업은 기호 PC에서 위 wrapper 명령을 1회 실행하여 결과를 전달하는 것입니다.

## 계속 차단

```txt
actual production env/secret/CA/certificate/key creation: no
managed DB connection/query: no
image pull/build: no
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
database/TLS mode: managed-postgresql-selected / verify-full-with-provider-ca
public entrypoint: external-reverse-proxy-https-selected
backend replicas/workers: 1/1
backend 1 replica / 1 worker
compose config render approved/executed: yes/no
result: managed-postgresql-reverse-proxy-selection-verified-config-render-approved
next safe stage: run-config-render-only-on-docker-capable-host
```
