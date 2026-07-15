# Roadmap — v316

## 현재 완료

- PostgreSQL/Alembic baseline
- runtime pool/lifecycle hardening
- managed PostgreSQL + reverse proxy HTTPS + backend 1/1 선택
- Compose config render-only 실제 통과
- GHCR/private/linux-amd64/base digest 선택
- GitHub namespace `gihohoho` 확정
- Codex용 `AGENTS.md`와 안전 인수인계 준비

## 다음 승인 순서

1. GitHub Actions 최소 permissions와 trigger를 정적 문서로 설계
2. SBOM/provenance/signature/vulnerability gate 설계
3. workflow 파일 생성 여부 별도 승인
4. workflow 정적 검증
5. base image pull 별도 승인
6. backend image build 별도 승인
7. GHCR push와 pushed digest 확인 별도 승인
8. isolated container 실행 별도 승인

현재는 1~2의 **설계 문서와 검사기만** 허용됩니다.
