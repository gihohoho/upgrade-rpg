# GitHub Actions / GHCR workflow plan — v321

```txt
version: v321.owner-only-reproducibility-locked-publish-gated
repository: gihohoho/upgrade-rpg
image: ghcr.io/gihohoho/upgrade-rpg-backend
workflow: .github/workflows/publish-backend-ghcr.yml
workflow 파일 생성: 완료
workflow 실행: 하지 않음
registry mutation: 하지 않음
```

## GitHub repository 설정 결과

아래 설정은 2026-07-15 로그인된 GitHub 브라우저에서 확인한 snapshot입니다. 로컬 strict checker는 GitHub API를 실시간 조회하지 않으므로 이후 설정이 바뀌어도 자동으로 알 수 없습니다. source-controlled gate 변경 직전에 Actions policy와 environment/main rule을 화면 또는 API로 다시 확인해야 합니다.

- Actions는 `gihohoho` 소유 action과 명시한 외부 action 8개만 허용합니다.
- 모든 외부 action은 검토한 40자리 commit SHA로만 실행할 수 있습니다.
- “Allow actions created by GitHub”와 “Marketplace verified creators” 포괄 허용은 꺼져 있습니다.
- 기본 `GITHUB_TOKEN`은 contents/packages read-only이며 Actions의 PR 생성·승인은 꺼져 있습니다.
- fork workflow에는 write token과 secret을 보내지 않습니다.
- `ghcr-production-publish` environment를 만들었고 deployment branch는 `main`만 허용합니다.
- environment secret과 variable은 현재 0개입니다.

## 트리거와 입력

허용 trigger는 `workflow_dispatch` 하나뿐입니다. `push`, `pull_request`, `pull_request_target`, `schedule`, `release`, `repository_dispatch`, `workflow_run`은 금지합니다.

수동 실행 시 다음 세 입력을 모두 검사합니다.

- `source_commit`: 소문자 40자리 SHA이며 `github.sha`와 같아야 함
- `approval_reason`: 앞뒤 공백 제거 후 10자 이상이며 로그에 출력하지 않음
- `confirm_publish`: 기본값 `false`, 실행하려면 명시적으로 `true`

실행 ref는 `refs/heads/main`이어야 하고 checkout 후 `git rev-parse HEAD`도 입력 SHA와 같아야 합니다.

## 최소 permissions

```yaml
workflow default / validate / build_scan:
  contents: read

publish_sign_verify:
  contents: read
  packages: write
  id-token: write
```

`actions`, `checks`, `contents`, `deployments`, `issues`, `pull-requests`, `security-events`, `statuses`의 write 권한은 주지 않습니다. 현재 저장소에서는 GitHub Artifact Attestations API를 사용할 수 없으므로 `attestations: write`와 `actions/attest`도 사용하지 않습니다.

## full-SHA action allowlist

```txt
actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0
actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405
docker/setup-buildx-action@bb05f3f5519dd87d3ba754cc423b652a5edd6d2c
docker/login-action@af1e73f918a031802d376d3c8bbc3fe56130a9b0
docker/build-push-action@53b7df96c91f9c12dcc8a07bcb9ccacbed38856a
anchore/sbom-action@e22c389904149dbc22b58101806040fa8d37a610
sigstore/cosign-installer@6f9f17788090df1f26f669e9d70d6ae9567deba6
actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a
```

## fail-closed 공급망 순서

게시 전:

1. 저장소 정적 검사, Python compileall, 전체 core smoke
2. registry에 올리지 않는 로컬 `linux/amd64` OCI build
3. SPDX JSON SBOM 생성과 구조 검사
4. 공식 Trivy `0.70.0` Linux 64-bit asset를 SHA-256 `8b4376d5d6befe5c24d503f10ff136d9e0c49f9127a4279fd110b727929a5aa9`로 검증
5. Trivy `HIGH,CRITICAL`, `ignore-unfixed: false`, `exit-code: 1`

게시 후:

1. `sha256:` exact digest 확보
2. Docker BuildKit `provenance: mode=max`와 `sbom: true`
3. exact digest에서 provenance와 SBOM을 `docker buildx imagetools inspect`로 다시 읽어 검사
4. registry에 push된 exact digest 자체를 Trivy로 다시 검사
5. 위 검사가 모두 통과한 뒤 Sigstore Cosign keyless OIDC로 exact digest 서명
6. 고정 workflow identity와 GitHub OIDC issuer로 서명 검증
7. 모든 검사가 끝난 digest만 후보로 출력

자동 deploy와 production image reference 갱신은 하지 않습니다. artifact는 secret과 raw environment를 포함하지 않으며 14일만 보관합니다.

## 잠긴 dependency/frontend 입력

운영과 CI의 Python 입력은 `backend/requirements/`에 고정했습니다. `runtime.in`과 `dev.in`은 사람이 검토하는 exact direct version이고, `runtime-linux-amd64-py311.lock`과 `dev-linux-amd64-py311.lock`은 전체 전이 의존성과 선택 Linux/amd64 wheel SHA-256을 담습니다. `pip-bootstrap.lock`은 pip `26.1.2` 자체를 먼저 고정합니다.

설치는 고정 대상 플랫폼으로 `pip download --require-hashes --only-binary=:all:`을 먼저 수행하고, 그 임시 wheel 폴더에서 `--no-index --require-hashes`로 설치합니다. build-system은 `setuptools==80.10.2`, `wheel==0.46.3`으로 고정했습니다. Dockerfile frontend는 `docker/dockerfile:1.21.0@sha256:27f9262d43452075f3c410287a2c43f5ef1bf7ec2bb06e8c9eeb1b8d453087bc`입니다. `tools/generate_backend_linux_dependency_locks.py --check`와 정적 checker가 파일 형식과 모든 입력 SHA-256을 검사합니다.

이 잠금은 dependency와 frontend 입력의 무단 변경 및 다른 배포 파일 선택을 차단합니다. 파일 timestamp나 builder 내부 구현까지 포함해 동일 source가 byte-for-byte 동일 image를 만든다고 주장하지는 않습니다. 실제 결과는 계속 exact digest, SBOM, Trivy, provenance, Cosign으로 검증합니다.

raw workflow와 lock SHA-256이 Windows `core.autocrlf`에 따라 달라지지 않도록 root `.gitattributes`에서 저장소 텍스트를 `eol=lf`로 고정하고 정적 검사합니다.

검사기는 workflow 전체 UTF-8 소스를 SHA-256 `9c3384f5f8d879320d41b04833a63842744e55c14cd12743c9aea0a3a74e8c5a`, 파싱된 실행 의미 구조를 SHA-256 `9a7af533b42854977897b26fe0aae364667f9be65a7d9dfab4c51a2bf1c31652`로 각각 잠그고 각 job의 step 이름·개수·순서도 정확히 확인합니다. 따라서 검사 명령 뒤 `|| true`를 붙이거나 secret 전송 step을 추가하는 등, marker만 남겨 둔 우회도 fail-closed로 차단합니다. smoke는 변조된 소스 해시를 일부러 승인한 상황에서도 의미 구조 잠금이 차단하는지 따로 검증합니다. 의도적인 workflow 수정은 별도 보안 검토와 함께 두 승인 해시를 갱신해야 합니다.

두 전역 해시를 모두 의도적으로 갱신하는 작업에도 대비해 action step 전체, run step 본문·env·허용 키를 개별 잠금으로 다시 검사합니다. secret/token 표현식은 파싱된 YAML 경로 기준으로 GHCR login password의 `${{ secrets.GITHUB_TOKEN }}` 하나만 허용합니다. root build context `.`에는 실제 env 파일이 전송되지 않도록 `.dockerignore`의 `.env`, `.env.*`, `**/.env`, `**/.env.*`, `backend/.env`, `*.env`, `*.env.*`, `.envrc`, `**/.envrc`를 필수로 검사합니다. Docker secret 안내 문서용 `!deploy/secrets/README.md`만 negation으로 허용하고 `!backend/**`, `!**/*` 같은 모든 broad 재포함 규칙은 금지합니다. root 정책을 우선 덮어쓰는 `backend/Dockerfile.production.dockerignore` 파일도 금지합니다.

## 선택된 owner-only 2단계 승인

저장소에는 owner 외 collaborator가 0명이고, GitHub environment 화면에도 required reviewer와 prevent self-review 설정이 나타나지 않아 두 보호를 구성하지 못했습니다. 더 중요한 원인은 GitHub Free/Pro/Team의 required reviewer가 공개 저장소에서만 지원된다는 점입니다. 따라서 현재 비공개 저장소에 collaborator를 추가하는 것만으로는 이 차단을 해결할 수 없습니다.

그래서 publish job의 첫 단계에서, GHCR login보다 먼저 source-controlled `PUBLISH_REVIEWER_GATE_READY` 값이 정확히 `true`인지 확인합니다. 현재 workflow 파일에는 리터럴 `"false"`로 고정되어 있어 repository/environment variable로 우회할 수 없고, workflow가 수동 실행되더라도 publish job은 registry 접근 전에 실패합니다.

기호는 2026-07-20에 `owner-only-source-controlled-two-step`을 선택했습니다. 독립 reviewer가 없다는 위험을 source-controlled 절차로 줄이되, native required reviewer와 같은 수준의 독립 승인을 제공한다고 표현하지 않습니다.

1. preparation commit에서는 dependency/frontend 잠금과 전체 검증을 끝내고 gate를 `false`로 유지한 채 push합니다.
2. Codex가 정확한 40자 preparation SHA와 변경 범위를 제시하고 기호가 그 SHA를 명시적으로 승인합니다.
3. 승인 뒤 GitHub Actions allowlist/full SHA와 environment main-only 설정을 live 재확인합니다.
4. 별도 authorization commit에서만 source-controlled gate를 열고 정확한 실행 SHA를 다시 검토합니다.
5. 수동 workflow는 authorization당 한 번만 실행합니다.
6. 성공·실패·취소와 관계없이 별도 commit으로 gate를 즉시 `false`로 되돌립니다.

현재는 1단계 준비 상태이며 정확한 preparation SHA 승인은 아직 없습니다. 따라서 gate는 계속 `false`이고 workflow를 실행하지 않습니다.
