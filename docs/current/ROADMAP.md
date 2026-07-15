# Roadmap — v320

## 현재 완료

- PostgreSQL/Alembic baseline과 runtime pool/lifecycle hardening
- managed PostgreSQL + reverse proxy HTTPS + backend 1/1 선택
- Compose config render-only 실제 통과
- GHCR private/linux-amd64/base digest와 namespace `gihohoho` 확정
- Codex GitHub Connector를 `gihohoho/upgrade-rpg` 하나로 제한
- repository Actions 외부 action 8개 full-SHA allowlist와 full-length SHA 강제
- 기본 `GITHUB_TOKEN` read-only와 fork write token/secret 차단
- `ghcr-production-publish` environment 생성과 `main` 전용 branch rule
- `workflow_dispatch` 전용 workflow 파일 작성
- YAML AST 기반 exact event/job/permission/action/gate 정적 검사
- 로컬 OCI + SPDX SBOM + checksum-pinned Trivy HIGH/CRITICAL gate
- pushed exact digest 재검사 + BuildKit mode=max provenance/SBOM + Cosign keyless sign/verify 설계
- source-controlled `PUBLISH_REVIEWER_GATE_READY="false"` hard gate
- 개발 서버 재사용, GitHub 작업, 숨김 파일/.env 권한을 handoff 규칙에 반영

## 다음 순서

1. 기호가 `github-enterprise-cloud-required-reviewer`, `owner-only-source-controlled-two-step`, `keep-publishing-disabled` 중 비공개 저장소 게시 승인 모델 하나를 선택
2. 선택한 모델에 필요한 보호 절차를 별도로 설계·구성
3. environment `main` rule과 선택한 승인 절차를 화면·정적 검사로 다시 확인
4. Python application/build dependency hash lock, pinned pip, immutable Dockerfile frontend로 재현성 gate 구성·검증
5. 게시 승인 모델과 재현성 gate가 모두 검증된 경우에만 별도 검토 commit으로 source-controlled gate 변경을 검토
6. gate 변경이 승인·검증된 경우에만 `workflow_dispatch`를 한 번 수동 실행하고 validate/build/SBOM/Trivy 결과를 단계별 확인
7. exact digest provenance/SBOM/Trivy/Cosign 검증이 모두 통과한 경우에만 후보 digest 기록
8. production reference 변경 없이 isolated container 검증을 별도 단계로 진행

GitHub Free/Pro/Team의 required reviewer는 공개 저장소에서만 지원되므로, 비공개 저장소에 collaborator를 추가하는 것만으로는 1번을 해결할 수 없습니다. 현재는 승인 모델 선택이 필요하며, 게시를 허용하는 모델이어도 4번 재현성 gate까지 끝나기 전에는 gate를 `false`로 유지하고 workflow를 실행하지 않습니다. `keep-publishing-disabled`를 선택하면 게시 단계는 진행하지 않습니다.
