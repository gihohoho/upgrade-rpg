# Roadmap — v321

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
- `owner-only-source-controlled-two-step` 게시 승인 모델 선택
- Linux/amd64 Python dependency/build-system/pip/frontend exact version + SHA-256 잠금
- 개발 서버 재사용, GitHub 작업, 숨김 파일/.env 권한을 handoff 규칙에 반영

## 다음 순서

1. v321 preparation commit의 정확한 40자 SHA와 변경 범위를 기호가 명시 승인
2. environment `main` rule과 Actions allowlist/full SHA를 live 재확인
3. 별도 authorization commit에서만 source-controlled gate 변경을 검토
6. gate 변경이 승인·검증된 경우에만 `workflow_dispatch`를 한 번 수동 실행하고 validate/build/SBOM/Trivy 결과를 단계별 확인
7. exact digest provenance/SBOM/Trivy/Cosign 검증이 모두 통과한 경우에만 후보 digest 기록
8. production reference 변경 없이 isolated container 검증을 별도 단계로 진행

GitHub Free/Pro/Team의 required reviewer는 공개 저장소에서만 지원되므로 owner-only 모델은 독립 reviewer와 동등하지 않습니다. 정확한 preparation SHA 승인과 GitHub live 재확인 전에는 gate를 `false`로 유지하고 workflow를 실행하지 않습니다. 실행 후에는 성공·실패와 관계없이 즉시 gate를 닫습니다.
