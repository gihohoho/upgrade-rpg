# Roadmap — v308

## 완료

- Vue/FastAPI/PostgreSQL 기본 분리
- PostgreSQL schema 22 tables / 748 application rows 검증
- 최초 revision `v295_initial_schema` 생성·수동 검토
- isolated upgrade → downgrade → upgrade 왕복
- restore rehearsal/source baseline stamp 및 post-check
- v305 baseline completion lock
- v306 next revision preflight: candidate operation 0, 새 revision 불필요
- v307 live runtime/DB health/Docker readiness 통과

## 현재 단계

- v308 pool/lifecycle/production guard/배포 template 준비 완료
- 실제 DB, `.env`, Docker 실행 상태 변경 없음

## 다음 순서

1. 기호님 PC에서 v308 strict + health 실행
2. local runtime/health 회귀 없음 확인
3. 남은 운영 경고를 secret/TLS/image/reverse proxy로 재분류
4. production Compose를 실행하지 않고 정적 검증 강화
5. 운영 secret 입력 방법과 TLS 연결 옵션 설계
6. worker 수·pool·PostgreSQL max connections 계산
7. 별도 승인 후에만 container build 및 isolated deployment smoke 검토

## 계속 보류

- 게임 콘텐츠 개발
- 새 Alembic revision
- source DB migration 실행
- 실제 production secret/TLS/Docker 적용
- Vue Preview/Apply/write/인증 연결
