# Roadmap — v317

## 현재 완료

- PostgreSQL/Alembic baseline
- runtime pool/lifecycle hardening
- managed PostgreSQL + reverse proxy HTTPS + backend 1/1 선택
- Compose config render-only 실제 통과
- GHCR/private/linux-amd64/base digest 선택
- GitHub namespace `gihohoho` 확정
- Codex용 `AGENTS.md`와 안전 인수인계 준비
- GitHub Actions 최소 permissions와 `workflow_dispatch` 전용 trigger 정적 설계
- SBOM/provenance/signature/HIGH·CRITICAL vulnerability fail-closed gate 설계

## 다음 승인 순서

1. Codex GitHub 플러그인에 `gihohoho/upgrade-rpg` repository 접근 권한 부여
2. 허용 action별 upstream 40자리 commit SHA 검토
3. repository Actions 정책과 `ghcr-production-publish` environment 설정 검토
4. workflow 파일 생성 여부 별도 승인
5. workflow 정적 검증
6. workflow 실행과 base image pull 별도 승인
7. backend image build 별도 승인
8. GHCR push와 pushed digest/supply-chain verification 별도 승인
9. isolated container 실행 별도 승인

현재는 1~3의 **읽기 전용 검토만** 다음 안전 단계입니다. workflow 파일 생성은 아직 허용되지 않습니다.
