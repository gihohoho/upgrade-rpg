# Roadmap — v313

## 완료

- PostgreSQL/Alembic baseline 완성
- runtime health/pool/lifecycle/production guard 검증
- 관리형 PostgreSQL + provider CA verify-full 선택
- 외부 reverse proxy HTTPS 선택
- backend 1 replica / 1 worker 선택
- backend-only production Compose와 immutable image 경계
- 기호 PC에서 config render-only 통과
- config render 안전 요약 증거 기록
- digest-only backend image 정책과 공급망 검증 게이트 추가

## 다음 순서

1. v313 image policy 정적 검사
2. registry provider 선택
3. namespace/repository 이름 선택
4. production target platform 선택
5. `python:3.11-slim` base image exact digest 검토
6. 별도 승인 후 base image pull
7. 별도 승인 후 backend image build
8. SBOM/provenance/vulnerability 결과 검토
9. 별도 승인 후 registry push와 digest/signature 검증
10. 관리형 PostgreSQL provider/region/private network/connection limit 선택
11. reverse proxy 제품/DNS/certificate 운영 방식 선택
12. isolated start와 cleanup을 각각 별도 승인

## 계속 보류

- 실제 production secret/CA/cert/key/registry credential
- Docker pull/build/push/up/down/resource 변경
- managed DB 실제 연결
- 새 Alembic revision과 DB mutation
- 게임 콘텐츠와 Vue write/인증
