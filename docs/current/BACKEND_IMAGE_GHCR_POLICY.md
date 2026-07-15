# Backend image GHCR policy — v319

## 확정값

```txt
GitHub remote: https://github.com/gihohoho/upgrade-rpg.git
namespace: gihohoho
repository: ghcr.io/gihohoho/upgrade-rpg-backend
visibility: private
target platform: linux/amd64
production reference: ghcr.io/gihohoho/upgrade-rpg-backend@sha256:<approved-64-hex-digest>
```

`gihohoho`는 기호가 직접 확인한 GitHub repository owner이며 placeholder가 아닙니다. 앞으로 임의로 바꾸지 않습니다.

## 인증정보 정책

- CI의 우선안은 GitHub Actions가 실행 시 제공하는 `GITHUB_TOKEN`입니다.
- 실제 token 값은 파일, Git, 채팅에 기록하지 않습니다.
- 로컬 `docker login`과 개인 PAT 생성은 아직 승인되지 않았습니다.
- `.github/workflows/` 생성과 workflow 실행도 아직 승인되지 않았습니다.
- 최소 permissions, `workflow_dispatch` only, SBOM/provenance/signature/vulnerability gate의 정적 plan은 검증 완료했습니다.
- action별 최신 정식 release와 upstream 40자리 SHA 후보는 v318에서 검토·고정했습니다.
- 이 SHA는 사용자 승인값이 아닙니다. repository Actions settings는 읽기 전용 검토를 마쳤고 `ghcr-production-publish` environment는 존재하지 않음을 확인했습니다.
- 최종 backend 이미지는 tag가 아니라 exact `sha256` digest로 production Compose에 넣습니다.

## 현재 차단 상태

```txt
docker login approved: no
image pull/build/push approved: no/no/no
workflow creation approved: no
static workflow plan present/verified: yes/yes
action SHA candidates reviewed: yes
action SHAs approved: no
GitHub connector repository access: verified, upgrade-rpg only
repository Actions settings reviewed/changed: yes/no
publish environment configured: no
container start approved: no
```

## 다음 안전 단계

외부 action 허용 범위를 v318에서 검토한 9개 repository로 제한하고 full-length SHA 강제를 켜는 repository Actions settings 변경 승인을 먼저 받습니다. `ghcr-production-publish` environment 생성과 실제 workflow 파일 생성은 이후 각각 별도 승인받습니다.
