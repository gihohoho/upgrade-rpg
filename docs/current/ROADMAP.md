# Roadmap — v333

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
latest: v333.isolated-image-pull-runtime-validation-complete-deploy-blocked
result: isolated-image-pull-runtime-validation-complete-production-deploy-blocked
lifecycle: attempt-recorded / gate=false
next safe stage: review-isolated-validation-and-approve-production-deploy-plan
```

## 다음 순서

1. 완료: verified candidate evidence 검토
2. 완료: production reference 정적 반영
3. 완료: isolated exact-digest pull/runtime validation/cleanup
4. production deploy 계획과 실제 deploy는 다시 별도 승인

정책을 자동 완화하지 않고 기존 다섯 run도 rerun하지 않습니다. isolated validation은 통과했지만 production runtime/deployment는 아직 적용하지 않았습니다.
