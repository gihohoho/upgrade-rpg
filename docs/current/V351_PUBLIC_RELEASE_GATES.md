# v351 공개 release gate — v355

## 현재 결론

v351 source의 master-data timeout 5초와 backend GZip 변경은 새 GHCR exact image로 게시됐고 공급망·isolated 검증과 Render 공개 배포·브라우저 통합 검증까지 통과했습니다.

```txt
source baseline: 81beaa0864c3422fb9fc2071b9c4965936ecafac
workflow run: 30226905547 / run_attempt=1 / success
lifecycle: attempt-recorded / gate=false / rerun forbidden
new exact image:
  ghcr.io/gihohoho/upgrade-rpg-backend@sha256:143be5eb21ec8c9318c7d0c4f3fbd5ac2de32439977a1d660c7247b6d3a507ac
isolated evidence:
  deploy/review/isolated-image-pull-validation-v353.json
Render backend/static deploy: approved / executed / live
content readiness: public no-fallback + guarded admin read-only verified
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

## v354 provider release 준비 — 완료된 역사

새 exact image를 기존 backend Web Service `srv-d9iro458nd3s73acgmsg`에 한 번 적용하고, v351 exact source를 기존 Static Site `srv-d9iu337aqgkc73am4lh0`에 한 번 배포하는 계약을 준비했습니다.

당시 상태는 둘 다 `prepared=true`, `approved=false`, `executed=false`였습니다. Static Site auto-deploy는 계속 꺼져 있습니다.

기호가 push된 v354 준비 commit `05f1af8ed1316e2cf0e0f39ac795b3ff60bccb62`를 별도 승인했고 다음을 정확히 한 번 수행했습니다.

1. clean pushed `main`과 계약 SHA 확인
2. backend existing-image exact digest 변경·수동 deploy 1회
3. `/api/v1/health`와 `/api/v1/health/db` read-only 확인
4. frontend exact source 수동 deploy 1회
5. `/index.html`, `/admin.html`, CORS 확인
6. 공개 master-data 무폴백과 관리자 guarded read-only 흐름 확인
7. sanitized evidence 기록

## v355 실행·검증 결과

- backend deploy: `dep-d9jeuf3eo5us73ba6cgg` / exact image / Live / 40.2초
- frontend deploy: `dep-d9jev7gu01pc73favje0` / exact v351 source / Live / 19.6초
- health/DB health: HTTP 200 / 200, DB health read-only 1회
- index/admin: HTTP 200 / 200
- CORS: exact frontend origin
- master-data: HTTP 200, 1,346ms, gzip, browser runtime applied, fallback 경고 없음
- admin: read-only, 11 domains / 729 rows, general write UI blocked, write key missing
- sanitized evidence: `deploy/review/render-v351-provider-release-v355.json`
- next safe stage: `select-first-content-and-balance-change-scope`

Render 설정 검사 출력에 backend/static deploy hook 값이 포함돼 두 hook을 즉시 재발급했습니다. 새 값은 기록하지 않았고 재발급은 추가 deploy를 만들지 않았습니다.

## 승인에 포함되지 않아 실행하지 않은 것

- DB write, restore, reset, seed
- Alembic revision, stamp, upgrade, downgrade
- admin write와 게임 콘텐츠·밸런스 변경
- custom domain, DNS, 결제 변경
- 자동 deploy, 자동 retry, 두 번째 deploy
- GitHub Actions 추가 dispatch 또는 rerun

실제 공개 게임이 backend master-data를 폴백 없이 로드하고 관리자 guarded read-only 흐름까지 검증됐습니다. 이제 첫 콘텐츠·밸런스 변경 범위를 기호와 선택하기 좋은 시점입니다.

현재 필요한 extension·권한·새 설치는 없습니다.
