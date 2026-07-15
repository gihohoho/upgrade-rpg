# Next Steps — v315

1. `python tools/check_codex_handoff_readiness.py --strict`
2. GitHub Actions 최소 `permissions`와 안전한 trigger를 정적 문서로 설계
3. SBOM/provenance/signature/vulnerability gate를 fail-closed 검사로 설계
4. `.github/workflows/` 생성 여부 별도 승인
5. base image pull, backend build, GHCR push를 각각 별도 승인
6. pushed exact digest 검증 뒤 isolated container start 별도 승인
7. 이후 관리형 PostgreSQL provider와 reverse proxy 제품 선택

고정 repository는 `ghcr.io/gihohoho/upgrade-rpg-backend`입니다. 실제 token/PAT/credential은 파일·Git·ZIP·채팅에 넣지 않습니다.
