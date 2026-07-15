# Roadmap — v319

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
- 허용 action 9개의 최신 정식 release와 upstream 40자리 commit SHA 후보 검토
- ChatGPT Codex Connector를 `gihohoho/upgrade-rpg` 저장소 하나에만 연결하고 실제 repository 조회 확인
- repository Actions settings와 `ghcr-production-publish` environment 존재 여부 읽기 전용 검토

## 다음 승인 순서

1. v318에서 검토한 9개 action SHA 후보 승인과 repository action allowlist/full-length SHA 설정 변경 여부 확인
2. `ghcr-production-publish` environment 생성과 보호 규칙 별도 승인
3. workflow 파일 생성 여부 별도 승인
4. workflow 정적 검증
5. workflow 실행과 base image pull 별도 승인
6. backend image build 별도 승인
7. GHCR push와 pushed digest/supply-chain verification 별도 승인
8. isolated container 실행 별도 승인

현재는 1의 repository Actions settings 변경도 아직 승인되지 않았습니다. workflow 파일 생성은 계속 허용되지 않습니다.
