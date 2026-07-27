# v351 공개 release gate — v354

## 현재 결론

v351 source의 master-data timeout 5초와 backend GZip 변경은 새 GHCR exact image로 게시됐고 공급망·isolated 검증까지 통과했습니다. 아직 Render 공개 환경에는 적용하지 않았습니다.

```txt
source baseline: 81beaa0864c3422fb9fc2071b9c4965936ecafac
workflow run: 30226905547 / run_attempt=1 / success
lifecycle: attempt-recorded / gate=false / rerun forbidden
new exact image:
  ghcr.io/gihohoho/upgrade-rpg-backend@sha256:143be5eb21ec8c9318c7d0c4f3fbd5ac2de32439977a1d660c7247b6d3a507ac
isolated evidence:
  deploy/review/isolated-image-pull-validation-v353.json
Render backend/static deploy: unapproved / unexecuted
```

정적 계약은 `deploy/v351-public-release-gates.example.json`, fail-closed 검사는 `tools/check_v351_public_release_gates.py`입니다.

## 완료된 image 단계

사용자가 준비 SHA `b48dfd0751b12b1b3afb6474f9d35359ba2f8177`을 승인했습니다.

1. authorization `7578eb665c03ee0fcb9399929328ce684cdd1b31`
2. workflow run `30226905547` 접수
3. immediate closure `5d547126322dbe3c235e855cc9c2f7337342ae36`
4. evidence `5c842deec6d1f496679a144897f485b07428810b`
5. local/registry Trivy HIGH·CRITICAL 0건
6. SLSA BuildKit provenance, SPDX-2.3 SBOM 87 packages
7. Cosign GitHub OIDC sign/verify
8. isolated linux/amd64 runtime, UID 65532, system CA 119, health 200
9. 임시 container/network/local image cleanup

workflow는 한 번만 실행됐고 rerun하지 않습니다. Render와 DB는 이 단계에서 변경하지 않았습니다.

## v354 provider release 준비

새 exact image를 기존 backend Web Service `srv-d9iro458nd3s73acgmsg`에 한 번 적용하고, v351 exact source를 기존 Static Site `srv-d9iu337aqgkc73am4lh0`에 한 번 배포하는 계약을 준비했습니다.

현재 상태는 둘 다 `prepared=true`, `approved=false`, `executed=false`입니다. Static Site auto-deploy는 계속 꺼져 있습니다.

push된 v354 준비 commit의 정확한 40자리 SHA를 기호가 별도 승인한 뒤에만 다음을 수행합니다.

1. clean pushed `main`과 계약 SHA 확인
2. backend existing-image exact digest 변경·수동 deploy 1회
3. `/api/v1/health`와 `/api/v1/health/db` read-only 확인
4. frontend exact source 수동 deploy 1회
5. `/index.html`, `/admin.html`, CORS 확인
6. 공개 master-data 무폴백과 관리자 guarded read-only 흐름 확인
7. sanitized evidence 기록

## 승인에 포함되지 않는 것

- DB write, restore, reset, seed
- Alembic revision, stamp, upgrade, downgrade
- admin write와 게임 콘텐츠·밸런스 변경
- custom domain, DNS, 결제 변경
- 자동 deploy, 자동 retry, 두 번째 deploy
- GitHub Actions 추가 dispatch 또는 rerun

실제 공개 게임이 backend master-data를 폴백 없이 로드하고 관리자 guarded 콘텐츠 작업 흐름까지 검증되면 콘텐츠 추가·수정을 시작하기 좋은 시점인지 기호에게 먼저 알립니다.

현재 필요한 extension·권한·새 설치는 없습니다.
