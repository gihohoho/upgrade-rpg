# Backend image GHCR policy — v321

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
- 사용자 승인을 받아 CI의 GHCR login/build/push는 승인됐고, 기호는 `owner-only-source-controlled-two-step`을 선택했습니다. 정확한 preparation SHA 승인은 아직 없어 현재 publish gate가 차단합니다.
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
publish approval model: owner-only-source-controlled-two-step
PUBLISH_REVIEWER_GATE_READY: source-controlled false
dependency/frontend input lock: complete
exact preparation SHA approval: pending
container start approved/executed: no/no
```

## 다음 안전 단계

v321 준비 commit을 검증·push한 뒤 Codex가 정확한 40자 SHA와 범위를 제시합니다. 기호가 그 SHA를 명시적으로 승인하기 전에는 source-controlled `PUBLISH_REVIEWER_GATE_READY`를 리터럴 `"false"`로 유지하며 workflow를 실행하지 않습니다. 승인 후에도 GitHub 설정을 live 재확인하고 별도 authorization commit에서만 gate를 열며, authorization당 한 번 실행한 뒤 성공·실패와 관계없이 즉시 다시 닫습니다.
