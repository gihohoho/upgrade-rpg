# Security rotation and GitHub gates — v321

이 문서는 기호가 2026-07-15에 허용한 GitHub·숨김 파일·`.env` 작업 권한과, 나중에 반드시 다시 확인하거나 교체할 보안 항목을 한곳에 기록합니다. 실제 secret 값은 이 문서에 적지 않습니다.

## 계속 적용하는 권한

- Codex는 VS Code/Codex 터미널을 사용하고 이미 실행 중인 개발 서버를 재사용할 수 있습니다.
- 백엔드 `127.0.0.1:8000`과 프론트엔드 `127.0.0.1:5173`은 문제가 없으면 작업마다 종료·재시작하지 않습니다.
- GitHub repository의 Actions, workflow, action SHA, environment, variables와 필요한 저장소 설정은 Codex가 작업 목적 안에서 구성할 수 있습니다.
- 숨김 파일과 `.env`는 필요한 경우 Codex가 점검·수정할 수 있습니다. 단, 실제 secret을 Git, 로그, 채팅, artifact에 노출하거나 커밋하지 않습니다.
- 필요한 extension, 권한, 설치 또는 사용자만 할 수 있는 계정 작업이 생기면 Codex가 요청하고, 해결되지 않으면 다음 handoff에도 계속 기록합니다.

## 지금 적용된 GitHub 보호

```txt
Actions policy: gihohoho + 명시된 외부 action만 허용
full-length action SHA required: yes
default GITHUB_TOKEN: contents/packages read-only
Actions PR create/approve: off
fork write token/secrets: off
environment: ghcr-production-publish
deployment branch: main only
environment secrets/variables: none
```

모든 외부 action은 전체 40자리 commit SHA로 고정했습니다. Trivy action의 전이 action 허용 문제를 없애기 위해 공식 Trivy `0.70.0` Linux 64-bit release asset을 고정 SHA-256으로 검증해 설치합니다. 개인 비공개 저장소에서 GitHub Artifact Attestations API를 사용할 수 없으므로 `actions/attest`는 사용하지 않고, Docker BuildKit의 registry provenance/SBOM과 Sigstore Cosign keyless 서명을 사용합니다.

이 GitHub 설정 상태는 2026-07-15 브라우저에서 확인한 snapshot이며 로컬 strict checker가 live API를 호출하는 것은 아닙니다. gate 변경 직전에 Actions allowlist/full SHA와 environment/main rule을 로그인된 화면 또는 API로 다시 확인합니다.

workflow 전체 UTF-8 소스는 SHA-256 `9c3384f5f8d879320d41b04833a63842744e55c14cd12743c9aea0a3a74e8c5a`, 파싱된 실행 의미 구조는 SHA-256 `9a7af533b42854977897b26fe0aae364667f9be65a7d9dfab4c51a2bf1c31652`로 각각 잠갔습니다. step이나 shell 본문이 한 곳이라도 바뀌면 정적 검사가 실패하며, source lock을 갱신해도 semantic lock이 별도로 실행 의미 변조를 차단합니다. 의도적인 workflow 변경은 별도 보안 검토와 두 승인 해시 갱신이 필요합니다.

두 전역 해시 외에도 action/run step별 잠금과 parsed secret 경로 allowlist를 적용했습니다. root Docker build context에서는 `.env`/`*.env`/`.envrc` 계열을 예제까지 모두 제외합니다. negation은 `!deploy/secrets/README.md` 하나만 허용하고 `!backend/**`, `!**/*` 같은 broad 재포함도 차단합니다. root 정책을 우선 덮어쓸 수 있는 `backend/Dockerfile.production.dockerignore` 생성도 금지합니다. 이는 파일을 Git에서 지우는 것이 아니라 Docker daemon/BuildKit으로 전송하지 않게 하는 보호입니다.

## 현재 게시 차단 조건

GitHub의 collaborator 화면에는 기호 한 명만 있고, `ghcr-production-publish` 환경 화면에는 required reviewer와 prevent self-review 설정이 나타나지 않았습니다. GitHub Free/Pro/Team의 required reviewer는 공개 저장소에서만 지원되므로, 이 비공개 저장소에 collaborator를 추가하는 것만으로는 required reviewer 보호를 구성할 수 없습니다.

워크플로에는 이 상황을 우회하지 못하도록 다음 fail-closed 조건이 들어 있습니다.

```txt
source-controlled gate: PUBLISH_REVIEWER_GATE_READY
required value: true
current workflow value: false
check position: GHCR login 이전 첫 단계
current effect: publish job fails before registry access
```

기호는 2026-07-20에 게시 승인 모델로 `owner-only-source-controlled-two-step`을 선택했습니다. 독립 reviewer가 없다는 잔여 위험을 알고 선택한 것이며 native required reviewer와 동등하다고 보지 않습니다.

준비 단계에서는 gate를 `false`로 둔 commit을 먼저 검증·push합니다. Codex가 그 정확한 40자 SHA와 범위를 제시하고 기호가 별도 메시지로 승인한 뒤에만 GitHub 설정을 live 재확인하고 별도 authorization commit을 검토합니다. authorization당 workflow는 한 번만 실행하며, 성공·실패·취소와 관계없이 즉시 gate를 닫는 commit이 필요합니다.

dependency/frontend 입력 잠금은 완료했습니다. Python 전체 전이 의존성은 Linux/amd64 wheel exact version + SHA-256, pip는 `26.1.2`, build-system은 `setuptools 80.10.2`/`wheel 0.46.3`, Dockerfile frontend는 exact digest입니다. byte-for-byte 동일 image를 보장한다고 주장하지 않으며 실제 결과 digest 검증은 SBOM/Trivy/provenance/Cosign으로 계속 수행합니다.

## 기호에게 필요한 계정 작업

현재 바로 필요한 설치나 extension은 없습니다. 이 작업의 commit/push가 끝나면 Codex가 정확한 preparation SHA를 제시합니다. 다음 게시 단계로 가려면 기호가 그 40자 SHA와 범위를 명시적으로 승인해야 합니다. 승인 전에는 source-controlled hard gate가 `false`여서 GHCR 게시가 차단되며 workflow도 실행하지 않습니다.

## 나중에 교체·재확인할 보안 항목

실제 값이 생성되거나 사용된 항목만 체크합니다. 이번 v321 작업에서는 실제 secret, PAT, registry credential, production `.env`, CA/cert/key를 만들거나 읽지 않았으므로 즉시 회전할 값은 없습니다.

- [ ] owner-only 승인 모델의 잔여 위험과 계정·environment 보호를 주기적으로 재검토
- [ ] source-controlled `PUBLISH_REVIEWER_GATE_READY`가 보호 규칙보다 먼저 바뀌지 않았는지 확인
- [ ] gate 변경 직전 GitHub Actions policy와 publish environment/main rule을 live 화면/API로 재확인
- [ ] action SHA와 upstream 보안 권고를 정기적으로 재검토
- [x] Python dependency/build-system hash lock, pinned pip, immutable Dockerfile frontend 구성·정적 검증
- [ ] 정확한 preparation SHA를 기호가 별도 메시지로 승인했는지 확인
- [ ] workflow 시도 뒤 성공·실패와 관계없이 gate를 즉시 `false`로 되돌렸는지 확인
- [ ] GHCR package visibility와 접근 주체 재검토
- [ ] 실제 production secret/JWT/Admin secret을 배포 전 생성하고 배포 후 회전 주기 기록
- [ ] managed PostgreSQL credential과 provider CA 교체 절차 확인
- [ ] reverse proxy TLS key/certificate 갱신 절차 확인
- [ ] 더 이상 필요 없는 GitHub token/PAT/credential 즉시 폐기

## 로컬 GitHub CLI 상태

브라우저 기반 GitHub 연결은 정상입니다. 로컬 `gh` CLI에 저장된 기존 계정 token은 401로 만료되어 API 호출에 사용할 수 없습니다. 현재 작업은 로그인된 GitHub 브라우저/Connector로 처리했으므로 막히지 않았고, CLI 재인증은 실제로 필요한 단계가 생길 때만 기호에게 요청합니다.
