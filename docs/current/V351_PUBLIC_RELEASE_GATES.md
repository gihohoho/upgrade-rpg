# v351 공개 release gate 준비 — v352

## 결론

v351 source의 master-data timeout 5초와 backend GZip 변경은 로컬 검증을 통과했지만 아직 공개 환경에 적용되지 않았습니다. 공개 적용은 두 단계로 분리합니다.

1. backend 새 GHCR image 게시와 공급망·isolated 검증
2. 새 exact image의 Render backend deploy와 v351 exact source의 Static Site deploy

이번 v352 준비 commit은 1번의 **image 게시 승인 대상**만 만듭니다. 2번 provider deploy는 새 digest와 isolated evidence가 나온 뒤 별도 준비 commit과 별도 exact-SHA 승인을 받아야 합니다.

정적 계약은 `deploy/v351-public-release-gates.example.json`, fail-closed 검사는 `tools/check_v351_public_release_gates.py`입니다.

## 고정한 source

```txt
v351 baseline commit: 81beaa0864c3422fb9fc2071b9c4965936ecafac
branch: main
backend runtime change: backend/app/main.py
frontend runtime changes:
  src/api/master-data-boot-policy.js
  src/api/master-data-runtime-switch.js
```

계약은 위 파일과 legacy static builder의 SHA-256을 고정합니다. preparation commit은 이 baseline의 후손이어야 하고, 실제 authorization은 push된 preparation commit의 직계 자식이며 lifecycle JSON 한 파일만 바꿀 수 있습니다.

## 현재 GHCR gate

```txt
lifecycle: preparation-closed
publishReviewerGateReady: false
approvedPreparationSha: null
ownerApproval.recorded: false
prior attempt history: 6
new workflow dispatch: no
new registry mutation: no
```

과거 v341 성공 run `30180738530`은 여섯 번째 history 항목으로 보존했습니다. 새 slot은 `not-dispatched`이며 사용자가 정확한 v352 40자리 SHA를 승인하기 전에는 열리지 않습니다.

GitHub live 설정도 read-only로 재확인했습니다.

- selected action allowlist와 full SHA pinning 유지
- default workflow permissions read
- Actions의 PR 승인 권한 없음
- private fork write token/secret 전달 없음
- environment `ghcr-production-publish` 존재
- custom branch policy는 `main` 하나
- environment secret/variable 0/0
- native required reviewer 없음, admin bypass 가능

따라서 개인 private repository에서는 기존 `owner-only-source-controlled-two-step`을 유지합니다.

## 승인 뒤 허용될 image 단계

정확한 v352 preparation SHA 승인 뒤에도 곧바로 Render deploy까지 허용되는 것은 아닙니다.

1. lifecycle-only direct-child authorization commit
2. workflow `run_attempt=1` 한 번 dispatch
3. run 접수 직후 lifecycle gate 즉시 closure
4. SBOM, Trivy HIGH/CRITICAL 0, provenance, Cosign 결과 기록
5. 새 exact digest isolated pull/runtime/CA-store/cleanup 검증
6. 그 뒤 provider release 준비 commit 작성

자동 rerun, 두 번째 dispatch, tag 기반 deploy, 검증 전 Render deploy는 금지합니다.

## frontend와 콘텐츠 경계

Static Site `gihohoho-upgrade-rpg`의 auto-deploy는 계속 꺼져 있습니다. v351 frontend source deploy는 새 backend exact image가 준비되고 provider release SHA가 별도 승인된 뒤에만 한 번 실행합니다.

공개 게임의 backend master-data 무폴백 로드와 관리자 guarded 콘텐츠 흐름을 모두 검증하기 전에는 콘텐츠 추가·수정 시작 시점이 아닙니다. 조건이 충족되면 기호에게 먼저 명확히 알립니다.

현재 필요한 extension·권한·새 설치는 없습니다.
