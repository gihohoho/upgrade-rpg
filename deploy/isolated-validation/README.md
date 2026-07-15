# Isolated production validation plan — v313

이 폴더는 승인 경계와 안전한 검사 도구만 보관합니다. 실제 production secret, CA, certificate, key, registry credential 또는 production env 파일을 두지 않습니다.

## Stage 0 — 완료: 정적 검증과 운영 방향 선택

- 관리형 PostgreSQL 선택
- 외부 reverse proxy HTTPS 선택
- backend 1 replica / 1 Uvicorn worker 선택
- pool 5 + overflow 10, `max_connections` review 후보 40 유지
- 실제 Docker, DB, Alembic mutation 없음

## Stage 1 — 완료: config render only

기호 PC에서 아래 안전 wrapper가 통과했습니다.

```txt
python tools/render_production_compose_config.py --execute --confirm-stage v312-config-render-only
```

완료 상태:

```txt
compose config render approved/executed: yes/yes
rendered services: backend
host ports/build/named volumes absent: True/True/True
image pull/build executed: no
container/image/network/volume mutation executed: no
```

민감정보 없는 요약 증거만 `deploy/review/production-compose-config-render-v312.json`에 기록했습니다. raw render는 저장하지 않았습니다.

## Stage 2A — 완료: image source/digest policy

- production image는 digest-only
- registry provider와 target platform은 아직 deferred
- source commit, base image digest, backend image digest 기록 필수
- SBOM/provenance/signature/vulnerability review 필수
- 현재 base image `python:3.11-slim`은 mutable tag이므로 build 차단

현재 상태:

```txt
pull/build/push approved: no/no/no
registry credential applied: no
actual image digest applied: no
```

## Stage 2B — 별도 승인 필요: registry/repository/platform/base digest 선택

먼저 다음을 문서로 확정합니다.

- registry provider
- namespace/repository
- target platform
- base image exact digest
- credential 보관 방식

선택만으로 Docker 명령을 실행하지 않습니다.

## Stage 2C — 각각 별도 승인 필요: pull/build/push

- base image pull
- backend image build
- SBOM/provenance/scan
- registry push
- pushed digest/signature 검증

각 작업은 하나씩 실행하고 결과를 확인한 뒤 다음으로 이동합니다.

## Stage 3 — 별도 승인 필요: isolated start

- 고유 project/network 이름 사용
- 실제 production DB/secret 대신 승인된 isolated test 자원 사용
- host port 공개 없음
- Alembic 자동 실행 없음
- schema/data write 검증 없음

## Stage 4 — 별도 승인 필요: isolated cleanup

실제 생성 목록을 먼저 확인하고 해당 isolated resource만 제거합니다. 기존 local PostgreSQL container/volume은 절대 변경하지 않습니다.

## 현재 고정 상태

```txt
actual Docker config command executed on user PC: yes (config only)
actual Docker image pull/build/push executed: no/no/no
actual Docker container/network/volume mutation executed: no
actual production secret/registry credential used: no
actual CA/certificate/key created: no
actual DB connection/write executed: no
actual Alembic command executed: no
isolated container execution approved: no
```
