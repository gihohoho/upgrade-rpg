# Roadmap — v330

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
latest: v330.slsa-v1-provenance-path-preparation
result: github-actions-ghcr-owner-only-provenance-path-preparation-ready-publish-gated
lifecycle: preparation-closed / gate=false
next safe stage: review-and-approve-exact-provenance-path-preparation-sha
```

## 다음 순서

1. v330 preparation 검증·commit·push
2. 새 preparation의 exact 40자 SHA 승인
3. 새 A → C → R single dispatch
4. exact-digest Trivy와 Cosign까지 통과한 digest만 isolated 검증 후보로 사용

정책을 자동 완화하지 않고 기존 네 run도 rerun하지 않습니다. production reference나 deployment는 별도 승인 단계입니다.
