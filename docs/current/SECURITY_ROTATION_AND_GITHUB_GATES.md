# Security rotation and GitHub gates — v330

## Secret 원칙

실제 secret 값은 적지 않습니다. token, PAT, Docker credential, production `.env`, CA/cert/key를 Git·채팅·로그·artifact에 넣지 않습니다. 나중에 사용한 credential이 생기면 사용 완료 후 회전·폐기 여부를 이 문서에 기록합니다.

## GitHub gate 상태

2026-07-22T01:21:58Z 확인:

- external action allowlist와 full-length SHA enforcement 정상
- GitHub-owned/verified creator blanket false
- default `GITHUB_TOKEN`: contents/packages read-only
- Actions PR create/approve false
- fork write token와 secret 전달 false
- `ghcr-production-publish`: main-only, secrets 0, variables 0
- required reviewer/prevent self-review: 비공개 개인 저장소 제약으로 unavailable

따라서 owner-only source-controlled two-step을 사용합니다. `run_attempt=1`, single dispatch, immediate closure, 정확한 `closureCommitSha`, rerun 금지를 유지합니다.

## 최신 evidence

- approved preparation `b35dfacf427162b348a6bd29eb030778edc7741c`
- authorization/closure/record `04e002060e576f19f4d8687b33635a414486206d` / `64e5ae0f5e5385ba00df16bb10ac33789ca3760a` / `303a2ed01c69c29894efdcde4ead6c2291c3d8bc`
- run `29883012957`: validation/build/SBOM 성공 후 Trivy에서 failure
- vulnerability 27건: Debian HIGH 18, CRITICAL 6, Python HIGH 3
- artifact `8515504259`, SHA-256 `6a5dfd4cd96754fd365323c7c6a7d1edf18542b5e5729e44220d7bf21ace4c50`, 만료 `2026-08-05T01:26:39Z`
- publish skipped: login/push/provenance/Cosign 미실행, registry mutation 없음

## v328 보안 준비

- Alpine 3.23 exact linux/amd64 digest와 musllinux binary-only hash lock을 채택했습니다.
- 최종 runtime에서 pip/setuptools/wheel/ensurepip과 사용되지 않는 JWT 의존성을 제거했습니다.
- 로컬 Trivy 0.70의 `--ignore-unfixed=false` HIGH/CRITICAL gate는 0건으로 통과했습니다.
- gate 완화나 예외 추가는 하지 않았고 새 workflow도 실행하지 않았습니다.
- 새 preparation SHA 승인 뒤 authorization 직전에 GitHub live 설정을 4시간 이내 기준으로 다시 확인합니다.

## 4차 run 보안 결과

- 2026-07-22T02:37:10Z allowlist/full SHA/default read-only/fork token·secret false/environment main-only를 재확인했습니다.
- GHCR login과 push가 실행되어 digest `sha256:6e4aefad0cdf1767670b7f736477dd9e00f17bf49a03fa471828df6667c41149`가 존재합니다.
- provenance/SBOM은 존재하지만 SLSA v1 경로 검사 실패로 exact-digest Trivy와 Cosign이 실행되지 않았습니다.
- unsigned·미검증 digest는 production reference에 넣거나 deploy하지 않습니다.
- workflow의 `SLSA.buildType` 검사만 `SLSA.buildDefinition.buildType`으로 바꾸는 focused fix가 후보입니다.

현재 필요한 extension·설치는 없습니다. `gh` keyring의 기존 계정 token은 만료 상태지만 Windows Git 자격 증명을 명령별 `GH_TOKEN`으로만 사용해 `repo`/`workflow` 작업을 완료했고 token 값을 저장·출력하지 않았습니다. 이 token에는 `read:org`와 `read:packages`가 없지만 현재 evidence 기록에는 필요하지 않습니다. 나중에 로컬에서 GHCR package metadata를 직접 조회해야 할 때만 `read:packages` 권한을 요청합니다.

## v330 preparation 보안 상태

- 4차 run의 login/push/digest 증거를 lifecycle history에 보존했습니다.
- 새 lifecycle은 `preparation-closed`, gate `false`, approval `null`, not-dispatched입니다.
- provenance 검사는 `SLSA`/`buildDefinition` 객체와 `buildDefinition.buildType`을 순서대로 fail-closed 확인합니다.
- workflow source/semantic/per-step SHA-256 잠금을 새 내용으로 갱신했습니다.
- 새 exact preparation SHA 승인 전에는 authorization, workflow, GHCR login/push를 실행하지 않습니다.
