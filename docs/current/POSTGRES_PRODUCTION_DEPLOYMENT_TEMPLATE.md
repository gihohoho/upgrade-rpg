# FastAPI/PostgreSQL 운영 배포 template — v310

## 파일

```txt
backend/Dockerfile
deploy/docker-compose.production.yml
deploy/production.env.example
deploy/secrets/README.md
deploy/README.md
```

이 파일들은 정적 검토용 초안입니다. 현재 로컬 `docker-compose.yml`을 대체하지 않으며 자동 실행하지 않습니다.

## FastAPI image 경계

- Python 3.11 slim 기반
- non-root `app` 사용자
- `.env`와 실제 secret 파일을 image에 복사하지 않음
- Uvicorn만 시작
- command/entrypoint에서 자동 migration 미실행

## 운영 Compose 경계

- Adminer service 없음
- PostgreSQL와 backend host `ports:` 공개 없음
- PostgreSQL password와 CA PEM은 Compose secret 파일 사용
- `POSTGRES_IMAGE`는 digest-pinned 값을 외부에서 필수 입력
- `DATABASE_URL`은 TLS와 인증서 검증이 적용된 주소를 외부에서 필수 입력
- `ENVIRONMENT=production`, `DEBUG=false` 강제
- backend read-only filesystem, tmpfs, no-new-privileges 적용
- backend `/api/v1/health` healthcheck 포함
- 내부 PostgreSQL network 분리

## example의 역할

`deploy/production.env.example`은 실제 값이 없는 inventory입니다.

- image digest: placeholder
- password/CA: host path placeholder
- JWT/Admin key: 32자 이상 별도 생성 placeholder
- DB URL: `sslmode=verify-full`과 CA 경로 예시
- CORS: 승인 origin placeholder

실제 값으로 바꾼 파일은 Git과 전달 ZIP에 포함하지 않습니다.

## 별도 승인 전 금지

```txt
docker compose -f deploy/docker-compose.production.yml build/pull/up/down
운영 secret 또는 인증서 생성·입력
TLS PostgreSQL server 설정 변경
운영 DB 연결
DNS/reverse proxy 공개
자동 migration 추가
```

bundled PostgreSQL service의 TLS server 설정은 아직 준비되지 않았습니다. 실제 적용 전 관리형 PostgreSQL 사용 여부 또는 별도 server certificate 설정을 확정해야 합니다.
