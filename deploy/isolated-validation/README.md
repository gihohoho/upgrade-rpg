# Isolated production container validation plan — v311

이 폴더는 **실행 계획만** 보관합니다. 실제 secret, CA, certificate, key, production env 파일을 두지 않습니다.

## 승인 단계

### Stage 0 — 현재 허용: project-file static validation

- v310 secret/TLS/container template checker
- v311 capacity/TLS/network plan checker
- Python 문법, 전용 smoke, core smoke
- Docker 명령 없음

### Stage 1 — 별도 승인 필요: config render only

목표는 container를 만들지 않고 production Compose의 치환 결과와 service/network/volume 구성을 검토하는 것입니다.

계획 명령:

```txt
docker compose --project-name rpg-prod-review-v311 \
  --env-file <temporary-review-env-path> \
  -f deploy/docker-compose.production.yml config
```

중단 조건:

- placeholder 또는 실제 secret이 출력물에 노출됨
- host `ports:`가 backend/PostgreSQL에 생김
- Adminer가 포함됨
- production/debug guard가 변함
- 예상하지 않은 volume/network가 생성될 가능성이 있음

현재 Stage 1은 승인되지 않았으며 명령을 실행하지 않습니다.

### Stage 2 — 별도 승인 필요: digest verification and image pull/build

- 승인된 exact digest 기록
- pull/build 전에 공급 source와 digest 재확인
- production 이름/volume 사용 금지
- build context에 `.env`, secret, backup이 없는지 재검사

현재 Stage 2는 승인되지 않았습니다.

### Stage 3 — 별도 승인 필요: isolated start

- 고유 project name 사용
- production DB, production volume, production network와 분리
- 임시 review secret만 사용하며 실제 운영 secret 사용 금지
- host port 공개 없이 container health와 network만 확인
- Alembic 자동 실행 금지
- DB schema/data write 검증 금지

현재 Stage 3은 승인되지 않았습니다.

### Stage 4 — 별도 승인 필요: isolated cleanup

생성한 project name과 resource 목록을 먼저 확인한 후 해당 isolated resource만 제거합니다. 기존 로컬 PostgreSQL container/volume과 `rpg_postgres_data`를 변경하거나 삭제하지 않습니다.

## 현재 고정 상태

```txt
actual Docker command executed: no
actual production secret used: no
actual CA/certificate/key created: no
actual DB connection/write executed: no
actual Alembic command executed: no
isolated container execution approved: no
```
