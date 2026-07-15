# Backend image GHCR policy — v315

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
- 실제 token 값은 파일, Git, ZIP, 채팅에 기록하지 않습니다.
- 로컬 `docker login`과 개인 PAT 생성은 아직 승인되지 않았습니다.
- `.github/workflows/` 생성과 workflow 실행도 아직 승인되지 않았습니다.
- 최종 backend 이미지는 tag가 아니라 exact `sha256` digest로 production Compose에 넣습니다.

## 현재 차단 상태

```txt
docker login approved: no
image pull/build/push approved: no/no/no
workflow creation approved: no
container start approved: no
```

## 다음 안전 단계

GitHub Actions의 최소 permissions, trigger, SBOM/provenance/signature/vulnerability gate를 정적 설계 문서와 fail-closed 검사로 준비합니다. 실제 workflow 파일 생성은 별도 승인 뒤에 합니다.
