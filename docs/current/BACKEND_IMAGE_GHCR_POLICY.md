# Backend image GHCR policy — v320

## 확정값

```txt
GitHub remote: https://github.com/gihohoho/upgrade-rpg.git
namespace: gihohoho
repository: ghcr.io/gihohoho/upgrade-rpg-backend
visibility: private
target platform: linux/amd64
production reference: ghcr.io/gihohoho/upgrade-rpg-backend@sha256:<approved-64-hex-digest>
```

`gihohoho`는 기호가 직접 확인한 GitHub repository owner이며 placeholder가 아닙니다.

## 인증정보와 권한

- CI는 실행 때만 제공되는 `GITHUB_TOKEN`을 사용합니다.
- 실제 token 값은 파일, Git, 채팅, 로그, artifact에 기록하지 않습니다.
- 사용자 승인을 받아 workflow creation approved: yes이며 workflow 파일을 만들었습니다.
- 사용자 승인을 받아 CI의 GHCR login/build/push는 승인되었지만, 비공개 저장소 게시 승인 모델이 미정이어서 현재 publish gate가 차단합니다.
- GitHub Free/Pro/Team의 required reviewer는 공개 저장소에서만 지원되므로, 비공개 저장소에 collaborator를 추가하는 것만으로는 required reviewer 보호를 구성할 수 없습니다.
- local credential strategy는 계속 deferred입니다. PAT이나 장기 Docker credential을 만들지 않았습니다.
- static workflow plan present/verified: yes/yes입니다.
- action SHAs approved: yes이며 repository 설정도 full-length SHA만 허용합니다.
- 최종 backend 이미지는 tag가 아니라 exact `sha256` digest로만 production Compose에 넣습니다.

## 현재 실행 상태

```txt
workflow file present: yes
workflow creation approved/executed: yes/yes
workflow execution approved/executed: yes/no
CI registry login/build/push approved: yes/yes/yes
CI registry login/build/push executed: no/no/no
publish environment exists/main-only: yes/yes
required reviewer/prevent self-review: no/no
publish approval model: undecided
PUBLISH_REVIEWER_GATE_READY: source-controlled false
container start approved/executed: no/no
```

## 다음 안전 단계

기호가 비공개 저장소의 게시 승인 모델을 아래 셋 중 하나로 선택합니다.

- `github-enterprise-cloud-required-reviewer`
- `owner-only-source-controlled-two-step`
- `keep-publishing-disabled`

선택한 모델의 보호 절차와 dependency/toolchain 재현성 gate를 모두 구성·검증하고 GitHub 설정을 live 재확인하기 전에는 source-controlled `PUBLISH_REVIEWER_GATE_READY`를 리터럴 `"false"`로 유지하며 workflow를 실행하지 않습니다. `keep-publishing-disabled`를 선택하면 gate를 바꾸지 않고 게시를 계속 비활성화합니다.
