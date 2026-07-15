# Isolated production validation plan — v312

이 폴더는 승인 경계와 안전한 검사 도구만 보관합니다. 실제 production secret, CA, certificate, key 또는 production env 파일을 두지 않습니다.

## Stage 0 — 완료: 정적 검증과 운영 방향 선택

- 관리형 PostgreSQL 선택
- 외부 reverse proxy HTTPS 선택
- backend 1 replica / 1 Uvicorn worker 선택
- pool 5 + overflow 10, `max_connections` review 후보 40 유지
- 실제 Docker, DB, Alembic mutation 없음

## Stage 1 — 승인됨: config render only

container, image, network, volume을 만들지 않고 Compose 치환 결과만 검토합니다.

프로젝트가 제공하는 안전 wrapper:

```txt
python tools/render_production_compose_config.py --execute --confirm-stage v312-config-render-only
```

wrapper는 실제 `.env`나 secret을 읽지 않고 임시 review sentinel만 사용하며, 정확히 `docker compose ... config`만 호출합니다. raw render 결과는 저장하거나 출력하지 않고 안전 요약만 표시합니다.

중단 조건:

- Docker/Compose CLI가 없음
- backend 이외 service가 렌더됨
- `ports:`, `build:`, PostgreSQL/Adminer service 또는 named volume이 렌더됨
- backend image가 digest 형식이 아님
- `ENVIRONMENT=production`, `DEBUG=false`, TLS `verify-full`, CA secret 경계가 사라짐
- external edge network 또는 replica 1 계약이 달라짐

현재 상태:

```txt
compose config render approved: yes
compose config render executed on user PC: no
actual production value used: no
container/image/network/volume mutation approved: no
```

## Stage 2 — 별도 승인 필요: image source/digest 검토와 pull/build

- backend image registry/source 결정
- base image와 backend image exact digest 기록
- build context 제외 파일 재검사
- pull과 build는 각각 별도 승인

현재 Stage 2는 승인되지 않았습니다.

## Stage 3 — 별도 승인 필요: isolated start

- 고유 project/network 이름 사용
- 실제 production DB/secret 대신 승인된 isolated test 자원 사용
- host port 공개 없음
- Alembic 자동 실행 없음
- schema/data write 검증 없음

현재 Stage 3은 승인되지 않았습니다.

## Stage 4 — 별도 승인 필요: isolated cleanup

실제 생성 목록을 먼저 확인하고 해당 isolated resource만 제거합니다. 기존 local PostgreSQL container/volume은 절대 변경하지 않습니다.

## 현재 고정 상태

```txt
actual Docker config command executed in handoff environment: no (Docker CLI unavailable)
actual Docker container/image/network/volume mutation executed: no
actual production secret used: no
actual CA/certificate/key created: no
actual DB connection/write executed: no
actual Alembic command executed: no
isolated container execution approved: no
```
