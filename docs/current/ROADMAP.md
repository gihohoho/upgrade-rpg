# Roadmap — v311

## 완료

- Vue/FastAPI/PostgreSQL 기본 분리
- PostgreSQL 22 application tables / 748 rows 구조·데이터 검증
- 최초 revision `v295_initial_schema` 생성·수동 검토·왕복 migration 검증
- restore rehearsal/source baseline stamp 및 post-check
- baseline completion lock 및 next-revision candidate 0 확인
- live runtime/DB health/Docker readiness 확인
- SQLAlchemy pool, shutdown dispose, production fail-closed guard 적용
- non-root FastAPI Dockerfile 및 별도 운영 Compose 초안
- multiline engine URL binding 검사 오탐 AST 수정 및 사용자 PC 통과
- 운영 secret/TLS/container 정적 template와 checker 검증
- worker/pool/max_connections review 계산과 확장 시나리오
- 관리형 PostgreSQL 우선 검토 및 bundled TLS 대안 경계
- reverse proxy/HTTPS/network allowlist 계획
- isolated container Stage 0~4 승인 계획

## 다음 순서

1. v311 checker를 사용자 PC에서 실행
2. 실제 예상 동시 사용자/트래픽과 replica 목표를 확인해 40 후보 재검토
3. 관리형 PostgreSQL 또는 bundled PostgreSQL 운영 방향 승인
4. reverse proxy 제품, DNS, HTTPS certificate 운영 방향 승인
5. image digest 공급 source와 승인 기록 형식 확정
6. 별도 승인 후 `docker compose ... config` render-only 검토
7. config 결과 통과 후에만 pull/build 승인 검토
8. isolated project name/resource 계획 통과 후에만 up/down 승인 검토

## 계속 보류

- 실제 운영 secret/인증서/CA 입력
- production Compose config/build/pull/up/down
- PostgreSQL `max_connections` 실제 변경
- 새 Alembic revision 또는 source migration
- 게임 콘텐츠 개발
- Vue Preview/Apply/write/인증 연결
