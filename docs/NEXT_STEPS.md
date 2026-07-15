# Next Steps — v317

1. `python tools/check_github_actions_ghcr_static_plan.py --strict`
2. GitHub 플러그인에 `gihohoho/upgrade-rpg` repository 접근 권한 부여 요청
3. 허용 action별 upstream 40자리 commit SHA 검토
4. repository Actions 설정과 `ghcr-production-publish` environment 보호 규칙 검토
5. `.github/workflows/` 생성 여부 별도 승인
6. workflow 정적 검증 뒤 workflow 실행 여부 별도 승인
7. base image pull, backend build, GHCR push를 각각 별도 승인
8. pushed exact digest의 provenance/SBOM/signature 검증 뒤 isolated container start 별도 승인
9. 이후 관리형 PostgreSQL provider와 reverse proxy 제품 선택

고정 repository는 `ghcr.io/gihohoho/upgrade-rpg-backend`입니다. 실제 token/PAT/credential은 파일·Git·채팅에 넣지 않습니다. ZIP은 기본 생성하지 않으며 Codex가 검증 후 직접 commit/push합니다.
