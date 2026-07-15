# GitHub Actions / GHCR static workflow plan — v319

## 목적과 현재 경계

이 문서는 backend 이미지를 `ghcr.io/gihohoho/upgrade-rpg-backend`에 게시하는 미래 workflow의 안전 조건을 먼저 고정합니다. 현재 단계에서는 `.github/workflows/` 파일을 만들지 않고 workflow, Docker login/build/push, registry 변경도 실행하지 않습니다.

```txt
plan: review-only
version: v319.github-connector-actions-settings-reviewed
workflow file present/approved: no/no
workflow execution approved: no
registry login/build/push approved: no/no/no
target: linux/amd64
credential: GitHub Actions GITHUB_TOKEN
next: repository Actions supply-chain settings 변경 승인 요청
```

## v319 GitHub 연결과 repository 설정 검토 결과

2026-07-15에 ChatGPT Codex Connector 설치와 실제 repository 조회를 확인했습니다. 설치 범위는 `selected-repositories-only`이며 선택된 저장소는 `gihohoho/upgrade-rpg` 하나입니다. 다른 개인 저장소, 조직 저장소, 앞으로 만들 저장소는 선택하지 않았습니다.

GitHub repository Actions 설정은 읽기 전용으로 다음과 같이 확인했습니다.

| 항목 | 현재 값 | 변경 여부 |
|---|---|---|
| 허용 action | 모든 action과 reusable workflow | 변경 안 함 |
| full-length action SHA 강제 | 꺼짐 | 변경 안 함 |
| artifact/log 보관 | 90일 | 변경 안 함 |
| fork workflow | 실행 켜짐, write token 꺼짐, secret/variable 전달 꺼짐, 승인 필요 켜짐 | 변경 안 함 |
| 기본 `GITHUB_TOKEN` | `read-contents-and-packages` | 변경 안 함 |
| Actions의 PR 생성·승인 | 꺼짐 | 변경 안 함 |
| 다른 private repository의 Actions 구성요소 접근 | `not-accessible` | 변경 안 함 |

`ghcr-production-publish` environment는 아직 존재하지 않습니다. 따라서 required reviewer, prevent self-review, `main` deployment branch 제한도 아직 구성되지 않았습니다. 이번 단계에서는 repository Actions 설정과 environment를 변경하거나 생성하지 않았습니다.

다음 외부 변경 후보는 허용 action을 아래 v318 allowlist repository로 제한하고 repository의 full-length SHA 강제를 켜는 것입니다. 이 변경은 기호의 별도 승인을 받은 뒤에만 실행합니다. Environment 생성과 workflow 파일 생성은 그 뒤의 별도 승인 경계입니다.

## 안전한 trigger

- 초기 trigger는 `workflow_dispatch` 하나만 허용합니다.
- `push`, `pull_request`, `pull_request_target`, `schedule`, `release`, `repository_dispatch`, `workflow_run`은 허용하지 않습니다.
- workflow는 기본 branch `main`에 있을 때만 수동 실행하고, 실행 시 `github.ref == refs/heads/main`을 다시 검사합니다.
- 사용자가 입력한 source commit은 소문자 40자리 SHA여야 하며 `github.sha`와 정확히 같아야 합니다.
- publish job은 `ghcr-production-publish` environment를 사용합니다. required reviewer, prevent self-review, `main` deployment branch 제한이 설정되기 전에는 실행을 승인하지 않습니다.
- concurrency group은 `ghcr-backend-publish`, `cancel-in-progress: false`입니다. 게시 중인 작업을 새 작업이 자동 취소하거나 덮어쓰지 않습니다.

`pull_request_target`은 높은 권한을 받을 수 있으므로 publish workflow에서 명시적으로 금지합니다. PR 코드나 fork 코드를 checkout해 registry credential/OIDC와 함께 실행하지 않습니다.

## 최소 permissions

| 범위 | 허용 permissions | 이유 |
|---|---|---|
| workflow 기본 | `contents: read` | 모든 미지정 권한을 `none`으로 축소 |
| validate job | `contents: read` | repository 정적 검사만 수행 |
| build/scan job | `contents: read` | registry 쓰기 없이 local OCI build·SBOM·scan |
| publish/attest/sign job | `contents: read`, `packages: write`, `attestations: write`, `id-token: write` | GHCR push, provenance/SBOM attestation, keyless 서명에만 사용 |

`contents`, `actions`, `checks`, `deployments`, `issues`, `pull-requests`, `security-events`, `statuses`의 write 권한은 금지합니다. SARIF 업로드도 처음에는 사용하지 않아 `security-events: write`를 추가하지 않습니다.

`id-token: write`는 publish/attest/sign job에만 부여합니다. 장기 PAT나 서명 private key를 만들지 않고 GitHub OIDC 기반의 짧은 수명 자격증명을 사용합니다.

## action 공급망 규칙

- 모든 `uses:`는 tag나 branch가 아니라 검토된 40자리 commit SHA로 고정합니다.
- 2026-07-15에 각 공식 GitHub 저장소의 최신 정식 release tag와 실제 upstream commit을 대조했습니다.
- 아래 값은 **검토 후보**이며 사용자 승인값이 아닙니다. 계획 JSON의 `approvedSha`는 계속 모두 `null`입니다.
- 기호가 workflow 파일 생성을 별도로 승인하기 전에는 `.github/workflows/`를 만들지 않습니다.
- 허용 후보는 `actions/checkout`, Docker 공식 actions, `aquasecurity/trivy-action`, `anchore/sbom-action`, `actions/attest`, `sigstore/cosign-installer`, `actions/upload-artifact`로 제한합니다.
- repository Actions 설정에서도 가능하면 full-length SHA 강제와 허용 action 범위를 적용합니다.

### v318 action SHA 검토 후보

| repository | 정식 release | 검토한 40자리 commit SHA |
|---|---|---|
| [`actions/checkout`](https://github.com/actions/checkout/releases/tag/v7.0.0) | `v7.0.0` | `9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0` |
| [`docker/setup-buildx-action`](https://github.com/docker/setup-buildx-action/releases/tag/v4.2.0) | `v4.2.0` | `bb05f3f5519dd87d3ba754cc423b652a5edd6d2c` |
| [`docker/login-action`](https://github.com/docker/login-action/releases/tag/v4.4.0) | `v4.4.0` | `af1e73f918a031802d376d3c8bbc3fe56130a9b0` |
| [`docker/build-push-action`](https://github.com/docker/build-push-action/releases/tag/v7.3.0) | `v7.3.0` | `53b7df96c91f9c12dcc8a07bcb9ccacbed38856a` |
| [`aquasecurity/trivy-action`](https://github.com/aquasecurity/trivy-action/releases/tag/v0.36.0) | `v0.36.0` | `ed142fd0673e97e23eac54620cfb913e5ce36c25` |
| [`anchore/sbom-action`](https://github.com/anchore/sbom-action/releases/tag/v0.24.0) | `v0.24.0` | `e22c389904149dbc22b58101806040fa8d37a610` |
| [`actions/attest`](https://github.com/actions/attest/releases/tag/v4.1.1) | `v4.1.1` | `a1948c3f048ba23858d222213b7c278aabede763` |
| [`sigstore/cosign-installer`](https://github.com/sigstore/cosign-installer/releases/tag/v4.1.2) | `v4.1.2` | `6f9f17788090df1f26f669e9d70d6ae9567deba6` |
| [`actions/upload-artifact`](https://github.com/actions/upload-artifact/releases/tag/v7.0.1) | `v7.0.1` | `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` |

정적 검사기는 repository, release, SHA, 공식 release URL, upstream tag commit 확인 상태를 모두 고정합니다. 어느 하나라도 바뀌거나 `approvedSha`가 사용자 승인 전에 채워지면 fail-closed로 실패합니다.

## pre-push fail-closed gate

1. 현재 repository strict/smoke를 통과합니다.
2. `linux/amd64` local OCI 산출물을 만들되 registry에 push하지 않습니다.
3. SPDX JSON SBOM을 생성하고 대상이 같은 OCI 산출물인지 검사합니다.
4. Trivy로 `HIGH,CRITICAL`을 검사하며 발견 시 exit code `1`로 실패합니다.
5. `--ignore-unfixed`, `.trivyignore`, inline 예외는 초기 정책에서 허용하지 않습니다.

어느 단계든 실패하거나 결과 파일이 없으면 publish job으로 진행하지 않습니다.

## push 이후 공급망 완결 gate

서명과 registry attestation은 exact pushed digest가 있어야 하므로 push 이후 수행됩니다. 이 단계에서 실패하면 이미 private GHCR에 들어간 이미지는 production candidate로 발표하지 않고 자동 배포도 하지 않습니다.

1. registry가 반환한 exact `sha256` digest를 캡처합니다.
2. 같은 digest를 subject로 build provenance와 SPDX SBOM attestation을 생성합니다.
3. Sigstore keyless OIDC로 같은 digest를 서명합니다.
4. GitHub attestation은 repository와 정확한 signer workflow를 지정해 검증합니다.
5. Cosign은 OIDC issuer `https://token.actions.githubusercontent.com`와 다음 certificate identity를 정확히 요구합니다.

```txt
https://github.com/gihohoho/upgrade-rpg/.github/workflows/publish-backend-ghcr.yml@refs/heads/main
```

6. provenance, SBOM, signature 검증이 모두 통과한 경우에만 reviewed candidate digest를 출력합니다.
7. Compose production reference 갱신과 container start/deploy는 별도 승인 단계로 유지합니다.

## 산출물 보관

- SBOM: SPDX JSON
- vulnerability report: JSON
- 보관 기간: 14일
- 실제 secret, raw environment, token, 인증 header는 artifact에 넣지 않습니다.

## 아직 필요한 권한과 사용자 확인

- Codex GitHub 플러그인의 `gihohoho/upgrade-rpg` 단일 repository 연결과 읽기 권한은 해결됐습니다.
- repository Actions settings 변경은 아직 승인되지 않았습니다.
- `ghcr-production-publish` environment 생성은 아직 승인되지 않았습니다.
- action별 upstream 40자리 SHA 후보 승인과 workflow 파일 생성 승인도 아직 필요합니다.
- 필요한 extension, repository 권한, 설치 항목이 생기면 Codex가 기호에게 요청하고 해결되지 않으면 다음 작업에서도 다시 요청합니다.

## 공식 근거

- [GitHub Docs — Publishing Docker images](https://docs.github.com/en/actions/tutorials/publish-packages/publish-docker-images)
- [GitHub Docs — Workflow syntax and permissions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
- [GitHub Docs — Managing Actions settings](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository)
- [GitHub Docs — Artifact attestations and SLSA](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/increase-security-rating)
- [GitHub Docs — Deployment environments and reviewers](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/control-deployments)
- [Sigstore — Cosign quickstart](https://docs.sigstore.dev/quickstart/quickstart-cosign/)
- [Trivy — Filtering by severity and status](https://trivy.dev/docs/latest/configuration/filtering/)
