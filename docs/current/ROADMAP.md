# Roadmap — v325

## 현재 완료

- PostgreSQL/Alembic baseline과 runtime pool/lifecycle hardening
- managed PostgreSQL + reverse proxy HTTPS + backend 1/1 선택
- Compose config render-only 실제 통과
- GHCR private/linux-amd64/base digest와 namespace `gihohoho` 확정
- Codex GitHub Connector를 `gihohoho/upgrade-rpg` 하나로 제한
- repository Actions 외부 action 8개 full-SHA allowlist와 full-length SHA 강제
- 기본 `GITHUB_TOKEN` read-only, PR 승인 차단, fork write token/secret 차단
- `ghcr-production-publish` environment와 `main` 전용 branch rule
- `workflow_dispatch` 전용 GHCR 후보 workflow
- Linux/amd64 Python dependency/build-system/pip/frontend exact version + SHA-256 잠금
- local OCI + SPDX SBOM + checksum-pinned Trivy HIGH/CRITICAL gate
- pushed exact digest provenance/SBOM/Trivy + Cosign keyless sign/verify
- `owner-only-source-controlled-two-step` 게시 승인 모델 선택
- v321 exact SHA 승인 이력 보존
- v322 source-controlled lifecycle gate 기본 closed
- authorization direct-parent + lifecycle-only 변경 강제
- repository owner + `run_attempt=1` + Actions API single-dispatch 방어
- run 접수 직후 immediate closure(C에서는 `closureCommitSha=null`)와 R evidence commit의 parent closure SHA 기록 절차
- 종료 뒤 `attempt-recorded` evidence commit과 non-success conclusion의 registry mutation/signature job·step 증거 분리
- Docker build record 자동 artifact 비활성화
- post-push failure digest/partial evidence 보존 설계
- authorization-open에서 closed root 전용 세 handoff smoke만 제외하고 앱·백엔드 전체 core smoke를 유지하는 `SKIP_GHCR_HANDOFF_SMOKES=1` 실행 계약
- 2026-07-20 GitHub live 재확인 및 fork write token/secret drift 복원
- 첫 owner-only run `29716038891`을 접수하고 즉시 gate 폐쇄·evidence 기록; dependency 설치 실패로 registry mutation 없음
- bootstrap pip 대상 Python을 `3.11`로 수정하고 첫 실패를 `priorAttemptEvidence`로 보존한 retry preparation
- 두 번째 owner-only run `29877813770` 접수, immediate closure와 evidence 기록
- workflow bootstrap/repository checks 통과 후 Dockerfile bootstrap target 문제로 로컬 image build 실패; registry mutation 없음

## 현재 단계

```txt
latest: v325.second-owner-only-attempt-recorded-failed-pre-registry-image-build
result: github-actions-ghcr-owner-only-attempt-recorded-publish-gated
lifecycle: attempt-recorded
workflow/login/build/push executed: yes/no/attempted-failed/no
next safe stage: review-recorded-workflow-attempt-evidence
```

## 다음 순서

1. run `29877813770`의 conclusion과 registry mutation/signature 증거 검토
2. 기호의 승인 뒤 Dockerfile bootstrap target 한 곳을 `3.11`로 수정
3. 새 retry preparation을 검증·commit·push하고 정확한 40자 SHA 승인 대기
4. 승인 직후 GitHub live 보호 상태 재확인
5. 새 A → C → R single-dispatch lifecycle 실행
6. 모든 검증이 끝난 exact digest만 후보로 기록
7. production reference 변경 없이 isolated container 검증은 별도 승인 단계로 진행

현재는 1번 완료 후 focused fix 승인을 기다리는 단계입니다. 기존 승인을 새 SHA에 재사용하지 않습니다. native required reviewer가 없으므로 owner-only 모델은 독립 reviewer와 동등하지 않습니다. 새 승인 전에는 다음 workflow를 실행하지 않습니다.
