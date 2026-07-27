# Backend image GHCR policy — v354

## 고정값

```txt
version: v354.v351-provider-release-prepared-exact-sha-approval-required
remote: https://github.com/gihohoho/upgrade-rpg.git
repository: ghcr.io/gihohoho/upgrade-rpg-backend
visibility/platform: private / linux/amd64
CI credential: GitHub Actions GITHUB_TOKEN
reference mode: digest-only
publish lifecycle: attempt-recorded / publishReviewerGateReady=false / current run recorded
```

verified production reference:

```txt
ghcr.io/gihohoho/upgrade-rpg-backend@sha256:f3bf6eed45e46e9d2022df4ab62eb6ca55b1ec0997b8ed342ae250c4a60052c1
```

run `30180738530`에서 build, SBOM, Trivy HIGH/CRITICAL 0건, SLSA provenance/SBOM, Cosign sign/verify를 통과했습니다. v342 isolated runtime에서도 exact digest, `linux/amd64`, UID 65532, system CA 119개, read-only rootfs, health 200을 확인하고 임시 자원을 모두 제거했습니다.

image publish는 `owner-only-source-controlled-two-step`과 `deploy/github-actions-ghcr-publish-lifecycle.json`을 사용합니다. run_attempt=1, single dispatch, immediate closure, rerun 금지를 유지합니다. 이전 시도와 artifact 상세는 lifecycle JSON과 `docs/CHANGELOG.md`에 보존합니다.

## 현재 배포 경계

`deploy/production-deploy-plan.example.json`은 검토 완료됐지만 필수 운영 입력이 미확정이라 approval ready가 `false`입니다. exact-SHA 실행 승인이 있기 전에는 production runtime에 적용하지 않습니다.

actual secret을 repository에 넣지 않고, tag·unsigned digest·미검증 digest를 production reference로 사용하지 않습니다. root build context는 env 파일을 제외하며 Trivy `--ignore-unfixed=false`를 유지합니다. byte-for-byte deterministic image라고 주장하지 않습니다.

v351 새 image는 run `30226905547`에서 게시·공급망 검증을 통과했고 v353 isolated 검증과 cleanup까지 완료했습니다. 새 verified candidate는 `ghcr.io/gihohoho/upgrade-rpg-backend@sha256:143be5eb21ec8c9318c7d0c4f3fbd5ac2de32439977a1d660c7247b6d3a507ac`입니다. 다음 단계는 backend/static provider release 준비 commit의 정확한 SHA owner 승인입니다.
