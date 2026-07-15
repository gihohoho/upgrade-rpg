# Next Steps — v320

1. `python tools/check_github_actions_ghcr_static_plan.py --strict`
2. `python tools/check_codex_handoff_readiness.py --strict`
3. 기호가 `github-enterprise-cloud-required-reviewer`, `owner-only-source-controlled-two-step`, `keep-publishing-disabled` 중 비공개 저장소 게시 승인 모델 하나를 선택
4. 선택한 모델에 필요한 보호 절차를 설계·구성하고 `main` 전용 rule과 함께 재확인
5. Python application/build dependency hash lock, pinned pip, immutable Dockerfile frontend로 재현성 gate를 구성·검증
6. 게시 승인 모델과 재현성 gate가 모두 검증된 경우에만 별도 검토 commit에서 source-controlled `PUBLISH_REVIEWER_GATE_READY` 변경을 검토
7. gate 변경이 승인·검증된 경우에만 수동 workflow를 실행하고 정적 검사, 로컬 build, SBOM, Trivy gate를 확인
8. pushed exact digest의 BuildKit provenance/SBOM, Trivy, Cosign 검증을 확인
9. 통과한 exact digest만 후보로 기록하고 isolated container start는 별도 단계로 진행

GitHub Free/Pro/Team의 required reviewer는 공개 저장소에서만 지원되므로, 비공개 저장소에 collaborator를 추가하는 것만으로는 해결되지 않습니다. 고정 repository는 `ghcr.io/gihohoho/upgrade-rpg-backend`입니다. 현재 gate는 리터럴 `"false"`라 GHCR login 전에 실패하며, 승인 모델과 재현성 gate가 모두 구성·검증되기 전에는 workflow를 실행하지 않습니다. 실제 token/PAT/credential은 파일·Git·로그·채팅에 넣지 않습니다. ZIP은 기본 생성하지 않으며 Codex가 검증 후 직접 commit/push합니다.
