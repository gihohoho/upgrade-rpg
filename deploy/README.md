# Production deployment template — v308

`deploy/docker-compose.production.yml`은 실제 운영 실행 파일이 아니라 **검토용 안전 초안**입니다.
현재 로컬 `docker-compose.yml`을 대체하지 않으며 자동 실행하지 않습니다.

운영 적용 전에 반드시 별도로 확정할 항목:

- digest가 고정된 `POSTGRES_IMAGE`
- TLS가 포함된 `DATABASE_URL`
- 32자 이상의 `JWT_SECRET_KEY`, `ADMIN_WRITE_DEV_KEY`
- PostgreSQL password secret 파일 경로
- 실제 CORS origin
- reverse proxy/HTTPS/외부 네트워크
- worker 수와 PostgreSQL `max_connections`를 반영한 pool 크기
- backup과 migration 별도 승인 절차

운영 템플릿은 PostgreSQL/Adminer host port를 공개하지 않으며 Adminer service를 포함하지 않습니다.
FastAPI 시작 command에도 Alembic migration을 넣지 않습니다.
