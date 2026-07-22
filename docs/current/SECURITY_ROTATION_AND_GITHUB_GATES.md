# Security rotation and GitHub gates — v327

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

## 다음 보안 검토

newer exact base image digest, runtime 최소화, fixed Python dependency를 먼저 검토합니다. `--ignore-unfixed=false`나 HIGH/CRITICAL gate 완화는 자동으로 승인하지 않습니다. 새 preparation/workflow 실행에는 별도 사용자 승인이 필요합니다.

현재 필요한 extension, 설치, 추가 GitHub 권한은 없습니다. 로컬 `gh` CLI token은 만료 상태이지만 signed-in GitHub 연결로 필요한 확인을 완료했으므로 지금 재인증은 필요하지 않습니다.
