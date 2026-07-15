# Next Steps — v319

1. `python tools/check_github_actions_ghcr_static_plan.py --strict`
2. 연결 완료된 Codex GitHub App이 `gihohoho/upgrade-rpg` 하나에만 접근하는 상태 유지
3. v318에서 검토한 9개 action upstream 40자리 commit SHA 후보 승인 여부 확인
4. repository의 외부 action allowlist 제한과 full-length SHA 강제 변경 여부 별도 승인
5. `ghcr-production-publish` environment 생성과 required reviewer/prevent self-review/main 제한을 별도 승인
6. `.github/workflows/` 생성 여부 별도 승인
7. workflow 정적 검증 뒤 workflow 실행 여부 별도 승인
8. base image pull, backend build, GHCR push를 각각 별도 승인
9. pushed exact digest의 provenance/SBOM/signature 검증 뒤 isolated container start 별도 승인
10. 이후 관리형 PostgreSQL provider와 reverse proxy 제품 선택

고정 repository는 `ghcr.io/gihohoho/upgrade-rpg-backend`입니다. 실제 token/PAT/credential은 파일·Git·채팅에 넣지 않습니다. ZIP은 기본 생성하지 않으며 Codex가 검증 후 직접 commit/push합니다.
