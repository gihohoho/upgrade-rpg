# Current Status — v332

## 현재 결과

```txt
latest: v332.verified-digest-production-reference-static-prepared
strict result: verified-digest-production-reference-static-prepared-runtime-blocked
next safe stage: review-production-reference-and-approve-isolated-pull-validation
GitHub remote: https://github.com/gihohoho/upgrade-rpg.git
GHCR repository: ghcr.io/gihohoho/upgrade-rpg-backend
lifecycle: attempt-recorded
publishReviewerGateReady: false
```

CI credential은 GitHub Actions `GITHUB_TOKEN`이고 local PAT는 deferred입니다. workflow는 `deploy/github-actions-ghcr-publish-lifecycle.json`의 `owner-only-source-controlled-two-step` source-controlled lifecycle gate를 사용하며 `run_attempt=1`, single dispatch, immediate closure, rerun 금지를 강제합니다. 5차 run은 성공 evidence로 기록했고, v332에서 verified digest를 production reference에 정적으로 고정했습니다. 현재 구체적 단계는 `review-production-reference-and-approve-isolated-pull-validation`입니다.

## 세 번째 실행

- 승인 preparation `b35dfacf427162b348a6bd29eb030778edc7741c`
- authorization `04e002060e576f19f4d8687b33635a414486206d`
- closure `64e5ae0f5e5385ba00df16bb10ac33789ca3760a`
- evidence `303a2ed01c69c29894efdcde4ead6c2291c3d8bc`
- run `29883012957`: completed/failure
- validation, repository checks, local image build, SPDX SBOM 성공
- Trivy HIGH/CRITICAL gate: 27건(Debian 24, Python 3)으로 실패
- artifact `8515504259`, SHA-256 `6a5dfd4cd96754fd365323c7c6a7d1edf18542b5e5729e44220d7bf21ace4c50`, 14일 보존
- publish job skipped: GHCR login/push/provenance/Cosign 미실행, digest 없음, signature 미검증

Trivy 기준 fixed version이 있는 항목은 `jaraco.context 6.1.0`, `wheel 0.46.2` 두 건이며 25건은 현재 fixed version이 없습니다. `--ignore-unfixed=false`와 HIGH/CRITICAL gate는 의도대로 작동했으므로 자동 완화하지 않습니다.

## 네 번째 실행

- preparation/authorization/closure/evidence: `13b15409929d77b4e6209481596e4f4550a22ba5` / `4fb31f51ca0de15d77a73390b5a07e394ffce12a` / `ddf475c1a2449feb50ef2af1a536e4150cf0ad59` / `f945214f2387b6aa191655d3740e18ef862bd6fb`
- run `29886540317`: completed/failure
- validation, 전체 repository checks, local linux/amd64 build, SPDX SBOM, local Trivy HIGH/CRITICAL gate 모두 성공
- GHCR login/build/push 성공, digest `sha256:6e4aefad0cdf1767670b7f736477dd9e00f17bf49a03fa471828df6667c41149`
- registry provenance와 SBOM은 존재하지만 workflow가 SLSA v1의 `SLSA.buildDefinition.buildType` 대신 구형 `SLSA.buildType`을 검사해 실패
- exact-digest Trivy와 Cosign sign/verify는 미실행, signature 미검증
- artifact `8516735247` / `8516749365`, SHA-256 `ff23e73c5c7aa8cd2abc8de88f043b1601debaf43652e3d76ff353f5e243d86b` / `f3d5b685c98bed863e07c35f8dd82aec7523c8c538de69c2c96da20ffda2e3e9`, 14일 보존
- pushed digest는 unsigned·미검증 상태이므로 production reference나 deploy에 사용하지 않음

## GitHub 설정

2026-07-22T09:41:21Z 기준 allowlist/full SHA, 기본 token read-only, fork write token/secret false, `ghcr-production-publish` main-only와 secrets/variables 0/0을 authorization 직전에 재확인했습니다. native required reviewer/prevent self-review는 비공개 개인 저장소 제약으로 없습니다.

## 다섯 번째 실행 — verified candidate

- preparation/authorization/closure/evidence: `36e8720a53ef7ff6a8334de6bc99646998d63fc9` / `26a11356e33c978afa8cd8a4881500fa62cdbc5c` / `1c4a982b2a35d3d45f59e7d9faefcdecca69e6c5` / `1f0340ddfcf3c8a74cf14110d5957627d4c5d38a`
- run `29909291344`: completed/success, `run_attempt=1`
- validation, repository checks, local build/SBOM/Trivy, GHCR login/build/push 성공
- SLSA v1 provenance/SBOM, exact-digest Trivy 0건, Cosign keyless sign/verify 성공
- verified digest: `sha256:ff939391517452a3ec477adaa0f8556d3525f9d0c6fb5f9d0df11d8f3d8461d2`
- artifact `8525220616` / `8525254543`, SHA-256 `c08e483754d357f2f7120659cea455e670bc570a5fb0db3eadfbc0b217f1e30e` / `697fbb38e30d9328d65e392da819eb1645cb42be5059ca502c29cd3b9241db65`, 14일 보존
- lifecycle `attempt-recorded`, gate `false`, rerun 금지
- production reference는 verified exact digest로 정적 고정됐으며 pull/deploy는 미실행

## 로컬 Failed to fetch 확인

- backend `127.0.0.1:8000`과 Vue `127.0.0.1:5173` 프로세스는 실행 중입니다.
- local PostgreSQL `127.0.0.1:55432` 연결이 거부되어 `/api/v1/health/db`와 `/api/v1/game/master-data`가 500입니다.
- legacy HTML용 `127.0.0.1:5500` 서버도 현재 꺼져 있습니다.
- 따라서 `index.html`·`admin.html`의 `Failed to fetch`는 배포 준비상 의도된 정상 상태가 아니라, 로컬 DB와 legacy 정적 서버가 실행되지 않은 개발 환경 문제입니다.

## 이후 콘텐츠·DB 변경 원칙

- 콘텐츠·코드·DB 개발은 가능하지만 현재 pinned image는 변경 전 snapshot으로 유지됩니다.
- 코드나 image 포함 콘텐츠가 바뀌면 최신 배포 전에 새 image build·SBOM·Trivy·provenance·Cosign 검증이 필요합니다.
- DB row 변경은 image digest와 별개지만 호환성 검증이 필요합니다.
- DB schema 변경은 새 Alembic revision과 배포 순서를 별도 승인·검토합니다.

## v330 focused fix 준비

- workflow는 `SLSA` 객체와 `SLSA.buildDefinition` 객체를 각각 검사합니다.
- `buildType`은 SLSA v1 실제 경로인 `SLSA.buildDefinition.buildType`에서만 확인합니다.
- 구형 `SLSA.buildType`으로 되돌리거나 `buildDefinition` 검사를 제거하면 mutation smoke가 차단합니다.
- workflow source/semantic SHA-256은 `3331484f280a12a239275785bef625f18656c62ccbe33e8707a296ac2e204843` / `526c4d21f9bc223e25829f60bf804f9167f6905b9129ffe1e70d85f354d57126`으로 잠겼습니다.
- 현재 lifecycle은 `preparation-closed`, gate `false`, `approvedPreparationSha=null`, `observedAttempt.status=not-dispatched`입니다.
- 새 workflow/login/build/push는 실행하지 않았습니다.

## 운영·개발 경계

- target `linux/amd64`, private GHCR
- managed PostgreSQL + provider CA `verify-full` + external reverse proxy HTTPS + backend 1/1
- Alembic current `v295_initial_schema`, 새 revision 필요 없음
- Vue GET read-only 외 Preview/Apply/write/auth 보류
- DB/Alembic/auth/API write/게임/production Compose·deploy는 별도 요청 전 금지
- actual secret/token/PAT/credential은 파일·Git·로그·채팅·artifact에 기록하지 않음

## v328 focused fix 준비 결과

- exact base: `python:3.11.15-alpine3.23@sha256:ac0151f0eec4b7ba78bc47d337f328c6db706e7255b35b2327c2749f058c82fe`
- Ubuntu 검증용 manylinux lock과 운영용 musllinux lock을 분리하고 모두 SHA-256으로 고정했습니다.
- multi-stage build와 UID/GID `65532` 비루트 실행을 적용하고 최종 runtime에서 pip/setuptools/wheel/ensurepip을 제거했습니다.
- 앱에서 사용되지 않는 `python-jose[cryptography]`와 전이 의존성 8개를 runtime에서 제거했습니다.
- 로컬 linux/amd64 후보는 약 40.2MB이며 Python 3.11.15와 앱 핵심 import를 확인했습니다.
- Trivy 0.70 동일 정책 `HIGH,CRITICAL`, `--ignore-unfixed=false` 결과는 OS 0건, Python 0건입니다.
- Distroless Debian 12 후보는 실제 동일 검사에서 41건으로 실패해 채택하지 않았습니다.
- 위 내용은 v328 preparation commit 시점의 준비 결과입니다. 그 시점에 lifecycle은 `preparation-closed`, 승인 SHA는 `null`, 새 workflow는 미실행이었습니다. 현재 상태는 위의 다섯 번째 실행 기록과 같이 `attempt-recorded`입니다.

다음 단계는 정적으로 고정한 production reference를 검토한 뒤 isolated pull/validation을 별도 승인하는 것입니다. 현재 필요한 extension·설치·추가 권한은 없습니다. 배포 정적 준비에는 서버 재시작이 불필요하지만 legacy 화면을 사용하려면 기존 local PostgreSQL과 별도 정적 서버를 시작해야 합니다. 로컬 token은 `read:packages`가 없어 GHCR package API 조회는 할 수 없지만 Actions evidence로 candidate 검증을 완료했습니다.

검증은 기호의 요청에 따라 위험도 기반 최소 범위로 실행합니다. 문서·handoff·상태값 변경에는 관련 strict checker와 handoff smoke만 사용하고 전체 core smoke는 실행하지 않습니다. 전체 smoke는 핵심 로직·DB/Alembic·API 계약·공통 구조·여러 영역 변경 또는 실제 배포 후보 직전에만 1회 실행합니다.
