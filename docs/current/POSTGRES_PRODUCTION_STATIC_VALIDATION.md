# PostgreSQL production secrets / TLS / container static validation — v310

## 목적

실제 운영 secret, 인증서, `.env`, Docker container/volume 또는 DB를 변경하지 않고 운영 배포 template의 안전 경계를 정적으로 검증합니다.

## 검사 범위

- 운영 Compose 필수 변수가 fail-fast `${NAME:?message}` 형태인지
- PostgreSQL password와 CA가 Compose secret 파일로 연결되는지
- `production.env.example`에 실제 secret이 없고 placeholder만 존재하는지
- PostgreSQL image가 digest pin 입력을 필수로 요구하는지
- DATABASE_URL 예시가 `sslmode=verify-full`과 CA 경로를 요구하는지
- Adminer와 host `ports:`가 운영 Compose에 없는지
- backend가 non-root/read-only/no-new-privileges/tmpfs인지
- backend healthcheck가 `/api/v1/health`를 확인하는지
- server 시작 command에 Alembic migration이 없는지
- 실제 배포 파일과 secret 경로가 Git/Docker build context에서 제외되는지

## 중요한 한계

이 단계는 정적 template 검증입니다. 다음은 확인하거나 실행하지 않습니다.

- 실제 secret 값의 존재 또는 강도
- 실제 CA/서버 인증서 유효성
- PostgreSQL 서버 TLS 설정
- image digest의 실제 공급망 승인 여부
- Docker build/pull/up/down
- container network 연결
- DB query 또는 migration

현재 bundled PostgreSQL service 자체의 TLS server 설정은 아직 승인되지 않았습니다. 실제 배포에서는 관리형 TLS PostgreSQL을 사용하거나 별도 승인된 server certificate 설정을 마련한 뒤 isolated container 검증으로 넘어갑니다.

## 읽기 전용 명령

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태 권장

```bash
python tools/check_production_secrets_tls_container_static.py --strict
```

정상 결과:

```txt
result: production-static-validation-template-verified-runtime-application-blocked
actual production secrets/TLS/container execution approved: no
next safe stage: separate-production-values-capacity-and-isolated-container-plan
```


## v310 실제 통과와 v311 후속

기호 PC와 handoff 검증에서 v310 strict checker가 기대값대로 통과했습니다. 실제 secret, Docker, DB, Alembic mutation은 없었습니다. 후속 용량·TLS 선택·network·isolated container 계획은 `POSTGRES_PRODUCTION_CAPACITY_TLS_NETWORK_PLAN.md`와 v311 checker로 분리했습니다.
