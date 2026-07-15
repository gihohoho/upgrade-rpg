# Security rotation and GitHub gates — v320

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

workflow 전체 UTF-8 소스는 SHA-256 `83393cb875cf43ce1bc30d245c100482818af96cd7b5417d81b9cb45ce62a993`, 파싱된 실행 의미 구조는 SHA-256 `2f1b1baf3f7db363f2f175b98623ec97e59a785592ae32d023f4b5123f2bd4c0`으로 각각 잠갔습니다. step이나 shell 본문이 한 곳이라도 바뀌면 정적 검사가 실패하며, source lock을 갱신해도 semantic lock이 별도로 실행 의미 변조를 차단합니다. 의도적인 workflow 변경은 별도 보안 검토와 두 승인 해시 갱신이 필요합니다.

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

현재 게시 승인 모델은 `undecided`입니다. 기호가 아래 셋 중 하나를 선택해야 합니다.

1. `github-enterprise-cloud-required-reviewer`: GitHub Enterprise Cloud에서 required reviewer와 prevent self-review를 구성합니다.
2. `owner-only-source-controlled-two-step`: owner 단독 운영을 전제로 source-controlled 2단계 승인 절차를 별도로 설계·정적 검사합니다.
3. `keep-publishing-disabled`: gate를 계속 `false`로 두고 GHCR 게시를 비활성화합니다.

게시를 허용하는 모델을 선택하더라도, 선택한 절차와 `main` 전용 deployment branch rule을 구성하고 화면·정적 검사로 다시 확인한 뒤 검토된 별도 commit에서만 gate 변경을 다룹니다. 선택·구성·검증 전에는 gate를 `true`로 바꾸거나 workflow를 실행하지 않습니다.

또한 dependency/toolchain 재현성 gate가 아직 `incomplete`입니다. Python application/build requirement의 hash lock, pinned pip, immutable Dockerfile frontend를 첫 게시 전에 별도로 구성·검증해야 합니다. 게시 승인 모델만 정해져도 이 조건이 남아 있으면 gate를 `true`로 바꾸지 않습니다.

## 기호에게 필요한 계정 작업

현재 바로 필요한 설치나 extension은 없습니다. 다음 게시 단계로 가려면 기호가 위 세 승인 모델 중 하나를 선택해 Codex에게 알려줘야 합니다. collaborator 추가만으로는 현재 비공개 저장소의 required reviewer 제한을 해결할 수 없습니다. 모델 선택 전에는 workflow 파일은 존재해도 source-controlled hard gate가 `false`여서 GHCR 게시가 차단되며, workflow도 실행하지 않습니다.

## 나중에 교체·재확인할 보안 항목

실제 값이 생성되거나 사용된 항목만 체크합니다. 이번 v320 작업에서는 실제 secret, PAT, registry credential, production `.env`, CA/cert/key를 만들거나 읽지 않았으므로 즉시 회전할 값은 없습니다.

- [ ] 선택한 비공개 저장소 게시 승인 모델과 관련 계정·environment 보호를 주기적으로 재검토
- [ ] source-controlled `PUBLISH_REVIEWER_GATE_READY`가 보호 규칙보다 먼저 바뀌지 않았는지 확인
- [ ] gate 변경 직전 GitHub Actions policy와 publish environment/main rule을 live 화면/API로 재확인
- [ ] action SHA와 upstream 보안 권고를 정기적으로 재검토
- [ ] 첫 게시 전 Python dependency/build-system hash lock, pinned pip, immutable Dockerfile frontend를 구성·검증
- [ ] GHCR package visibility와 접근 주체 재검토
- [ ] 실제 production secret/JWT/Admin secret을 배포 전 생성하고 배포 후 회전 주기 기록
- [ ] managed PostgreSQL credential과 provider CA 교체 절차 확인
- [ ] reverse proxy TLS key/certificate 갱신 절차 확인
- [ ] 더 이상 필요 없는 GitHub token/PAT/credential 즉시 폐기

## 로컬 GitHub CLI 상태

브라우저 기반 GitHub 연결은 정상입니다. 로컬 `gh` CLI에 저장된 기존 계정 token은 401로 만료되어 API 호출에 사용할 수 없습니다. 현재 작업은 로그인된 GitHub 브라우저/Connector로 처리했으므로 막히지 않았고, CLI 재인증은 실제로 필요한 단계가 생길 때만 기호에게 요청합니다.
