# Next Steps — v321

1. `python tools/check_github_actions_ghcr_static_plan.py --strict`
2. `python tools/check_codex_handoff_readiness.py --strict`
3. v321 preparation commit의 정확한 40자 SHA와 변경 범위를 기호가 검토·명시 승인
4. 승인 직후 GitHub Actions allowlist/full SHA와 environment `main` rule을 live 재확인
5. 별도 authorization commit에서만 source-controlled `PUBLISH_REVIEWER_GATE_READY` 변경을 검토
7. gate 변경이 승인·검증된 경우에만 수동 workflow를 실행하고 정적 검사, 로컬 build, SBOM, Trivy gate를 확인
8. pushed exact digest의 BuildKit provenance/SBOM, Trivy, Cosign 검증을 확인
9. 통과한 exact digest만 후보로 기록하고 isolated container start는 별도 단계로 진행

기호는 `owner-only-source-controlled-two-step`을 선택했고 dependency/frontend 입력 잠금도 완료했습니다. 고정 repository는 `ghcr.io/gihohoho/upgrade-rpg-backend`입니다. 현재 gate는 리터럴 `"false"`라 GHCR login 전에 실패합니다. 정확한 preparation SHA 승인과 GitHub live 재확인 전에는 workflow를 실행하지 않습니다. authorization당 한 번 실행한 뒤 성공·실패와 관계없이 gate를 즉시 닫습니다. 실제 token/PAT/credential은 파일·Git·로그·채팅에 넣지 않습니다. ZIP은 기본 생성하지 않으며 Codex가 검증 후 직접 commit/push합니다.
