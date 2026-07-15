# Roadmap — v312

## 완료

- PostgreSQL/Alembic baseline 완성
- runtime health/pool/lifecycle/production guard 검증
- 관리형 PostgreSQL + provider CA verify-full 선택
- 외부 reverse proxy HTTPS 선택
- backend 1 replica / 1 worker 선택
- backend-only production Compose와 immutable image 경계
- config render-only 안전 wrapper와 smoke 준비

## 다음 순서

1. 기호 PC에서 v312 selection checker 실행
2. config render-only wrapper 실행 및 결과 수집
3. render 결과의 backend-only/host-port 없음/digest/TLS/edge 계약 확인
4. backend image registry/source/base image/digest 검토
5. 별도 승인 후 pull 또는 build 중 하나를 작은 경계로 검증
6. 관리형 PostgreSQL provider/region/private network/connection limit 선택
7. reverse proxy 제품/DNS/certificate 운영 방식 선택
8. isolated start와 cleanup은 각각 별도 승인

## 계속 보류

- 실제 production secret/CA/cert/key
- Docker pull/build/up/down/resource 변경
- managed DB 실제 연결
- 새 Alembic revision과 DB mutation
- 게임 콘텐츠와 Vue write/인증
