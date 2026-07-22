# Roadmap — v331

## 완료

- production topology, PostgreSQL/Alembic baseline, GHCR namespace/repository/base digest 정책 확정
- GitHub Actions action allowlist/full SHA/default read-only/environment main-only 구성
- `owner-only-source-controlled-two-step` source-controlled lifecycle gate 구현
- direct-parent/lifecycle-only authorization, `run_attempt=1`, single dispatch, immediate closure, rerun 금지 구현
- three owner-only attempts recorded without GHCR mutation
- 3차 run `29883012957`: local linux/amd64 image와 SPDX SBOM 생성 성공, Trivy HIGH/CRITICAL gate에서 차단
- artifact `8515504259`에 SBOM과 vulnerability report 보존

## 현재

```txt
latest: v331.fifth-owner-only-attempt-recorded-verified-candidate
result: github-actions-ghcr-owner-only-attempt-recorded-publish-gated
lifecycle: attempt-recorded / gate=false
next safe stage: review-verified-candidate-evidence-before-production-reference
```

## 다음 순서

1. verified candidate evidence 검토
2. production reference 반영 또는 isolated pull/validation 범위 별도 승인
3. 승인된 범위만 정적 검증
4. production deploy는 다시 별도 승인

정책을 자동 완화하지 않고 기존 다섯 run도 rerun하지 않습니다. production reference나 deployment는 별도 승인 단계입니다.
