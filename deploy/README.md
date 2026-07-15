# Production deployment review template — v311

`deploy/docker-compose.production.yml`은 실제 운영 실행 파일이 아니라 **정적 검토용 안전 초안**입니다. 현재 로컬 `docker-compose.yml`을 대체하지 않으며 자동 실행하지 않습니다.

## 포함된 안전 경계

- digest 입력이 필수인 PostgreSQL image placeholder
- PostgreSQL password와 CA PEM을 Compose secret 파일로 분리
- `ENVIRONMENT=production`, `DEBUG=false`
- JWT/Admin key/CORS/DATABASE_URL 필수 입력
- Adminer 제외
- PostgreSQL/FastAPI host `ports:` 미공개
- backend non-root/read-only/no-new-privileges/tmpfs
- backend `/api/v1/health` container healthcheck
- FastAPI 시작 command에 자동 Alembic 없음

## v311 review-only 계획

- `production-capacity-plan.example.json`: worker/pool/max_connections 계산 입력
- 현재 application burst 15, recommended minimum 30, review 후보 40
- 관리형 PostgreSQL 우선 검토, bundled PostgreSQL TLS는 별도 server certificate 설계 필요
- reverse proxy/HTTPS 공개 진입점과 backend/DB 내부 network 분리
- `isolated-validation/README.md`: config/build/run/cleanup 단계별 승인 경계

## 예시 파일

- `production.env.example`: 실제 값이 없는 변수 목록과 TLS URL 형태
- `production-capacity-plan.example.json`: 실제 적용이 없는 숫자·선택 계획
- `secrets/README.md`: 실제 secret 파일을 Git/ZIP에 넣지 않는 규칙

## 아직 승인되지 않은 것

- 실제 secret과 CA 파일 생성·입력
- PostgreSQL server TLS 설정 또는 관리형 DB 연결
- image digest 공급망 승인
- reverse proxy/HTTPS 실제 설정
- Docker Compose config render
- Docker build/pull/up/down
- container network 및 DB 연결 검증
- PostgreSQL `max_connections` 실제 적용

bundled PostgreSQL을 실제 운영에 사용할 경우 server certificate 설정을 별도로 설계해야 합니다. 관리형 TLS PostgreSQL을 사용할 경우에도 CA, hostname verification, connection limit, network allowlist를 별도로 검증해야 합니다.
