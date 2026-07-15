# FastAPI/PostgreSQL 운영 배포 template — v308

## 추가 파일

```txt
backend/Dockerfile
deploy/docker-compose.production.yml
deploy/README.md
```

이 파일들은 검토용 초안이며 현재 로컬 `docker-compose.yml`을 대체하거나 자동 실행하지 않습니다.

## FastAPI image 경계

- Python 3.11 slim 기반
- non-root `app` 사용자
- `.env` 파일을 image에 복사하지 않음
- Uvicorn만 시작
- command/entrypoint에서 자동 migration 미실행

## 운영 Compose 경계

- Adminer service 없음
- PostgreSQL host `ports` 공개 없음
- backend도 reverse proxy 연결을 위한 `expose`만 사용
- PostgreSQL password는 Compose secret 파일 사용
- `POSTGRES_IMAGE`는 승인된 digest 고정 image를 외부에서 필수 입력
- `DATABASE_URL`은 TLS가 포함된 운영 주소를 필수 입력
- `ENVIRONMENT=production`, `DEBUG=false` 강제
- backend read-only filesystem과 `no-new-privileges` 적용
- 내부 PostgreSQL network 분리

## 별도 승인 전 금지

```txt
docker compose -f deploy/docker-compose.production.yml up/build/pull
운영 secret 생성·입력
TLS 인증서/DB 파라미터 변경
운영 DB 연결
DNS/reverse proxy 공개
자동 migration 추가
```

실제 운영 적용 전에는 image digest, TLS 방식, secret 저장소, reverse proxy, worker/pool 계산, backup/복구 절차를 다시 별도 검증합니다.
