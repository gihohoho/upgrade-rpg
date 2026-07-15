#!/usr/bin/env python3
"""Validate the v319 GitHub connector and Actions settings review without mutations."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any

TOOL_VERSION = "v319.github-connector-actions-settings-reviewed"
READY_RESULT = "github-connector-actions-settings-verified-workflow-not-created"
BLOCKED_RESULT = "blocked-or-failed"
NEXT_SAFE_STAGE = "request-repository-actions-supply-chain-settings-change-approval"
REMOTE = "https://github.com/gihohoho/upgrade-rpg.git"
REPOSITORY = "gihohoho/upgrade-rpg"
IMAGE_REPOSITORY = "ghcr.io/gihohoho/upgrade-rpg-backend"
WORKFLOW_PATH = ".github/workflows/publish-backend-ghcr.yml"
CERTIFICATE_IDENTITY = (
    "https://github.com/gihohoho/upgrade-rpg/"
    ".github/workflows/publish-backend-ghcr.yml@refs/heads/main"
)
ALLOWED_ACTIONS = (
    "actions/checkout",
    "docker/setup-buildx-action",
    "docker/login-action",
    "docker/build-push-action",
    "aquasecurity/trivy-action",
    "anchore/sbom-action",
    "actions/attest",
    "sigstore/cosign-installer",
    "actions/upload-artifact",
)
EXPECTED_ACTION_REVIEWS = {
    "actions/checkout": ("v7.0.0", "9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0"),
    "docker/setup-buildx-action": ("v4.2.0", "bb05f3f5519dd87d3ba754cc423b652a5edd6d2c"),
    "docker/login-action": ("v4.4.0", "af1e73f918a031802d376d3c8bbc3fe56130a9b0"),
    "docker/build-push-action": ("v7.3.0", "53b7df96c91f9c12dcc8a07bcb9ccacbed38856a"),
    "aquasecurity/trivy-action": ("v0.36.0", "ed142fd0673e97e23eac54620cfb913e5ce36c25"),
    "anchore/sbom-action": ("v0.24.0", "e22c389904149dbc22b58101806040fa8d37a610"),
    "actions/attest": ("v4.1.1", "a1948c3f048ba23858d222213b7c278aabede763"),
    "sigstore/cosign-installer": ("v4.1.2", "6f9f17788090df1f26f669e9d70d6ae9567deba6"),
    "actions/upload-artifact": ("v7.0.1", "043fb46d1a93c77aae656e7c1c64a875d1fc6a0a"),
}


class StaticWorkflowPlanError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise StaticWorkflowPlanError(message)


def _read(path: Path) -> str:
    if not path.is_file():
        raise StaticWorkflowPlanError(f"required file is missing: {path.as_posix()}")
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(_read(path))
    except json.JSONDecodeError as exc:
        raise StaticWorkflowPlanError(f"invalid JSON: {path.as_posix()}: {exc}") from exc
    _require(isinstance(payload, dict), "plan JSON root must be an object")
    return payload


def _bool(payload: dict[str, Any], key: str) -> bool:
    value = payload.get(key)
    _require(isinstance(value, bool), f"{key} must be a boolean")
    return value


def inspect_static_workflow_plan(root: Path) -> dict[str, Any]:
    plan = _read_json(root / "deploy/github-actions-ghcr-static-plan.example.json")
    document = _read(root / "docs/current/GITHUB_ACTIONS_GHCR_STATIC_WORKFLOW_PLAN.md")

    _require(plan.get("schemaVersion") == TOOL_VERSION, "unexpected v319 schemaVersion")
    _require(_bool(plan, "reviewOnly") is True, "plan must remain review-only")
    _require(plan.get("githubRemote") == REMOTE, "GitHub remote changed")
    _require(plan.get("repository") == REPOSITORY, "GitHub repository changed")
    _require(plan.get("defaultBranch") == "main", "default branch must remain main")
    _require(plan.get("registry") == "ghcr.io", "registry must remain GHCR")
    _require(plan.get("imageRepository") == IMAGE_REPOSITORY, "image repository changed")
    _require(plan.get("targetPlatform") == "linux/amd64", "target platform changed")
    _require(plan.get("workflowPathPlanned") == WORKFLOW_PATH, "planned workflow path changed")
    for key in (
        "workflowFilePresent",
        "workflowCreationApproved",
        "workflowExecutionApproved",
        "registryLoginApproved",
        "imageBuildApproved",
        "imagePushApproved",
        "registryMutationApproved",
        "repositoryActionsSettingsMutationApproved",
        "publishEnvironmentCreationApproved",
    ):
        _require(_bool(plan, key) is False, f"{key} must remain false")

    trigger = plan.get("triggerPolicy")
    _require(isinstance(trigger, dict), "triggerPolicy must be an object")
    _require(trigger.get("allowedEvents") == ["workflow_dispatch"], "only workflow_dispatch is allowed")
    forbidden_events = trigger.get("forbiddenEvents")
    _require(isinstance(forbidden_events, list), "forbiddenEvents must be a list")
    for event in ("push", "pull_request", "pull_request_target", "schedule", "release", "repository_dispatch", "workflow_run"):
        _require(event in forbidden_events, f"unsafe trigger is not forbidden: {event}")
    _require(trigger.get("requiredRef") == "refs/heads/main", "required ref must remain main")
    source_commit = trigger.get("sourceCommitInput")
    _require(isinstance(source_commit, dict), "sourceCommitInput must be an object")
    _require(source_commit.get("required") is True, "source commit input must be required")
    _require(source_commit.get("pattern") == "^[0-9a-f]{40}$", "source commit must be a full lowercase SHA")
    _require(source_commit.get("mustEqualGithubSha") is True, "source commit must equal github.sha")
    _require(trigger.get("approvalReasonInputRequired") is True, "approval reason input must be required")
    environment = trigger.get("environment")
    _require(isinstance(environment, dict), "environment policy must be an object")
    _require(environment.get("name") == "ghcr-production-publish", "publish environment name changed")
    _require(environment.get("requiredReviewers") is True, "publish environment must require reviewers")
    _require(environment.get("preventSelfReview") is True, "publish environment must prevent self-review")
    _require(environment.get("deploymentBranch") == "main", "publish environment must allow main only")
    _require(environment.get("configured") is False, "unverified environment must remain unconfigured")
    concurrency = trigger.get("concurrency")
    _require(isinstance(concurrency, dict), "concurrency must be an object")
    _require(concurrency.get("group") == "ghcr-backend-publish", "concurrency group changed")
    _require(concurrency.get("cancelInProgress") is False, "publish jobs must not auto-cancel each other")

    permissions = plan.get("permissionsPolicy")
    _require(isinstance(permissions, dict), "permissionsPolicy must be an object")
    read_only = {"contents": "read"}
    _require(permissions.get("workflowDefault") == read_only, "workflow default permissions must be contents: read only")
    _require(permissions.get("validateJob") == read_only, "validate job permissions are not minimal")
    _require(permissions.get("buildScanJob") == read_only, "build/scan job must not receive write permission")
    _require(
        permissions.get("publishAttestSignJob") == {
            "contents": "read",
            "packages": "write",
            "attestations": "write",
            "id-token": "write",
        },
        "publish/attest/sign permissions changed",
    )
    forbidden_writes = permissions.get("forbiddenWritePermissions")
    _require(isinstance(forbidden_writes, list), "forbiddenWritePermissions must be a list")
    for name in ("contents", "actions", "checks", "deployments", "issues", "pull-requests", "security-events", "statuses"):
        _require(name in forbidden_writes, f"forbidden write permission missing: {name}")

    action_policy = plan.get("actionPolicy")
    _require(isinstance(action_policy, dict), "actionPolicy must be an object")
    _require(action_policy.get("requireFullLengthCommitSha") is True, "full action SHA pinning must be required")
    _require(action_policy.get("requiredShaPattern") == "^[0-9a-f]{40}$", "action SHA pattern changed")
    _require(action_policy.get("reviewedOn") == "2026-07-15", "action SHA review date changed")
    _require(action_policy.get("resolvedActionShaCandidatesReviewed") is True, "action SHA candidates are not reviewed")
    _require(action_policy.get("resolvedActionShasApproved") is False, "reviewed candidates must not be treated as approved")
    _require(action_policy.get("workflowCreationBlockedUntilApproved") is True, "workflow creation must remain blocked")
    allowlist = action_policy.get("allowlist")
    _require(isinstance(allowlist, list), "action allowlist must be a list")
    repositories = tuple(item.get("repository") for item in allowlist if isinstance(item, dict))
    _require(repositories == ALLOWED_ACTIONS, "action allowlist or order changed")
    for item in allowlist:
        repository = item.get("repository")
        expected_release, expected_sha = EXPECTED_ACTION_REVIEWS[repository]
        _require(item.get("reviewedRelease") == expected_release, f"reviewed release changed: {repository}")
        _require(item.get("reviewedSha") == expected_sha, f"reviewed SHA changed: {repository}")
        _require(re.fullmatch(r"[0-9a-f]{40}", expected_sha) is not None, f"reviewed SHA is not full length: {repository}")
        _require(
            item.get("releaseUrl") == f"https://github.com/{repository}/releases/tag/{expected_release}",
            f"official release URL changed: {repository}",
        )
        _require(item.get("upstreamTagCommitVerified") is True, f"upstream tag commit is unverified: {repository}")
        _require(item.get("approvedSha") is None, f"action SHA was set before approval: {item.get('repository')}")

    gates = plan.get("supplyChainGates")
    _require(isinstance(gates, dict), "supplyChainGates must be an object")
    _require(gates.get("failurePolicy") == "fail-closed", "supply-chain gates must fail closed")
    _require(gates.get("prePushOrder") == [
        "repository-static-checks",
        "build-local-oci-linux-amd64",
        "generate-spdx-json-sbom",
        "validate-sbom-subject",
        "scan-high-critical-vulnerabilities",
    ], "pre-push gate order changed")
    vulnerability = gates.get("vulnerabilityGate")
    _require(isinstance(vulnerability, dict), "vulnerabilityGate must be an object")
    _require(vulnerability.get("scanner") == "trivy", "vulnerability scanner changed")
    _require(vulnerability.get("severity") == ["HIGH", "CRITICAL"], "HIGH and CRITICAL severities must block")
    _require(vulnerability.get("exitCodeOnFinding") == 1, "vulnerability findings must return exit code 1")
    _require(vulnerability.get("ignoreUnfixed") is False, "unfixed vulnerabilities must not be ignored")
    _require(vulnerability.get("allowIgnoreFile") is False, "Trivy ignore files require a separate approval")
    _require(vulnerability.get("allowInlineExceptions") is False, "inline vulnerability exceptions are forbidden")
    _require(gates.get("postPushOrder") == [
        "capture-exact-registry-digest",
        "attest-build-provenance",
        "attest-spdx-sbom",
        "cosign-keyless-sign-digest",
        "verify-provenance-and-sbom-attestations",
        "verify-cosign-identity-and-issuer",
        "emit-reviewed-candidate-digest",
    ], "post-push gate order changed")
    attestation = gates.get("attestationVerification")
    _require(isinstance(attestation, dict), "attestationVerification must be an object")
    _require(attestation.get("subjectMustEqualPushedDigest") is True, "attestation subject must equal pushed digest")
    _require(attestation.get("repository") == REPOSITORY, "attestation repository changed")
    _require(attestation.get("signerWorkflow") == WORKFLOW_PATH, "attestation signer workflow changed")
    signature = gates.get("signatureVerification")
    _require(isinstance(signature, dict), "signatureVerification must be an object")
    _require(signature.get("mode") == "sigstore-keyless-oidc", "signature mode must remain keyless OIDC")
    _require(signature.get("oidcIssuer") == "https://token.actions.githubusercontent.com", "OIDC issuer changed")
    _require(signature.get("certificateIdentity") == CERTIFICATE_IDENTITY, "certificate identity changed")
    _require(signature.get("subjectMustEqualPushedDigest") is True, "signature subject must equal pushed digest")
    _require(gates.get("automaticDeployment") is False, "automatic deployment is forbidden")
    _require(gates.get("productionReferenceUpdate") is False, "production reference must not update automatically")
    _require(gates.get("candidateDigestReleasedOnlyAfterAllGates") is True, "candidate digest must wait for all gates")

    artifacts = plan.get("artifactPolicy")
    _require(isinstance(artifacts, dict), "artifactPolicy must be an object")
    _require(artifacts.get("sbomFormat") == "spdx-json", "SBOM format must remain SPDX JSON")
    _require(artifacts.get("scanReportFormat") == "json", "scan report format must remain JSON")
    _require(artifacts.get("retentionDays") == 14, "artifact retention must remain 14 days")
    _require(artifacts.get("secretsAllowed") is False, "artifact must not contain secrets")
    _require(artifacts.get("rawEnvironmentAllowed") is False, "artifact must not contain raw environment data")

    review = plan.get("repositoryReview")
    _require(isinstance(review, dict), "repositoryReview must be an object")
    _require(review.get("reviewedOn") == "2026-07-15", "repository review date changed")
    connector = review.get("githubConnector")
    _require(isinstance(connector, dict), "githubConnector review must be an object")
    _require(connector.get("installationOwner") == "gihohoho", "connector installation owner changed")
    _require(
        connector.get("repositorySelection") == "selected-repositories-only",
        "connector must remain limited to selected repositories",
    )
    _require(
        connector.get("selectedRepositories") == [REPOSITORY],
        "connector repository selection changed",
    )
    _require(connector.get("repositoryAccessVerified") is True, "connector repository access is not verified")
    _require(connector.get("visibility") == "private", "reviewed repository visibility changed")
    _require(connector.get("defaultBranch") == "main", "reviewed repository default branch changed")

    settings = review.get("actionsSettings")
    _require(isinstance(settings, dict), "actionsSettings review must be an object")
    _require(settings.get("reviewed") is True, "Actions settings review is missing")
    _require(settings.get("allowedActions") == "all", "reviewed Actions allow policy changed")
    _require(
        settings.get("requireFullLengthCommitSha") is False,
        "full-length action SHA setting changed before approval",
    )
    _require(settings.get("artifactRetentionDays") == 90, "reviewed artifact retention changed")
    fork = settings.get("forkPullRequestWorkflows")
    _require(isinstance(fork, dict), "fork workflow review must be an object")
    _require(fork.get("runWorkflows") is True, "reviewed fork workflow setting changed")
    _require(fork.get("sendWriteTokens") is False, "fork workflows must not receive write tokens")
    _require(fork.get("sendSecretsAndVariables") is False, "fork workflows must not receive secrets")
    _require(fork.get("requireApproval") is True, "fork workflows must require approval")
    _require(
        settings.get("defaultWorkflowPermissions") == "read-contents-and-packages",
        "default GITHUB_TOKEN permissions changed",
    )
    _require(
        settings.get("allowActionsCreateApprovePullRequests") is False,
        "Actions must not create or approve pull requests by default",
    )
    _require(
        settings.get("privateRepositoryReusableWorkflowAccess") == "not-accessible",
        "private reusable workflow access changed",
    )

    publish_environment = review.get("publishEnvironment")
    _require(isinstance(publish_environment, dict), "publishEnvironment review must be an object")
    _require(publish_environment.get("reviewed") is True, "publish environment review is missing")
    _require(publish_environment.get("name") == "ghcr-production-publish", "publish environment name changed")
    _require(publish_environment.get("exists") is False, "publish environment was created before approval")
    _require(publish_environment.get("configured") is False, "publish environment was configured before approval")

    setup = plan.get("requiredRepositorySetup")
    _require(isinstance(setup, dict), "requiredRepositorySetup must be an object")
    for key in (
        "githubConnectorRepositoryAccess",
        "githubConnectorSelectedRepositoryOnly",
        "actionsSettingsReviewed",
        "publishEnvironmentReviewed",
    ):
        _require(_bool(setup, key) is True, f"verified repository review must remain true: {key}")
    for key in (
        "fullLengthActionShaPolicyEnabled",
        "restrictedActionAllowlistEnabled",
        "publishEnvironmentConfigured",
    ):
        _require(_bool(setup, key) is False, f"unapproved repository setup must remain false: {key}")
    _require(plan.get("nextSafeStage") == NEXT_SAFE_STAGE, "unexpected next safe stage")

    workflow_dir = root / ".github/workflows"
    _require(not workflow_dir.exists() or not any(workflow_dir.rglob("*")), "workflow file exists before approval")
    for marker in (
        TOOL_VERSION,
        "workflow_dispatch",
        "pull_request_target",
        "contents: read",
        "packages: write",
        "attestations: write",
        "id-token: write",
        "HIGH,CRITICAL",
        "Sigstore keyless OIDC",
        CERTIFICATE_IDENTITY,
        "selected-repositories-only",
        "read-contents-and-packages",
        "environment는 아직 존재하지 않습니다",
    ):
        _require(marker in document, f"static plan document is missing marker: {marker}")
    _require(re.search(r"40자리 commit SHA", document) is not None, "document is missing full SHA policy")

    return {
        "toolVersion": TOOL_VERSION,
        "repository": REPOSITORY,
        "imageRepository": IMAGE_REPOSITORY,
        "trigger": "workflow_dispatch-only",
        "workflowFilePresent": False,
        "workflowCreationApproved": False,
        "actionShaCandidatesReviewed": True,
        "actionShasApproved": False,
        "githubConnectorRepositoryAccess": True,
        "actionsSettingsReviewed": True,
        "publishEnvironmentConfigured": False,
        "supplyChainGate": "fail-closed",
        "result": READY_RESULT,
        "nextSafeStage": NEXT_SAFE_STAGE,
    }


def render(result: dict[str, Any]) -> str:
    return "\n".join((
        "GitHub Actions/GHCR static workflow plan verification (read-only)",
        "No workflow, token, Docker, registry, DB, or Alembic mutation was created or executed.",
        "",
        f"- repository/image: {result['repository']} / {result['imageRepository']}",
        f"- trigger: {result['trigger']}",
        "- minimal publish permissions: contents=read, packages=write, attestations=write, id-token=write",
        "- pre-push gates: static checks, local OCI build, SPDX SBOM, HIGH/CRITICAL scan",
        "- post-push gates: digest, provenance, SBOM attestation, keyless signature, verification",
        "- workflow file/creation approved: no/no",
        "- action SHA candidates reviewed/approved: yes/no",
        "- GitHub connector repository access: verified (upgrade-rpg only)",
        "- repository Actions settings reviewed/changed: yes/no",
        "- publish environment reviewed/configured: yes/no",
        f"- result: {result['result']}",
        f"- next safe stage: {result['nextSafeStage']}",
    ))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        result = inspect_static_workflow_plan(root)
    except StaticWorkflowPlanError as exc:
        payload = {"toolVersion": TOOL_VERSION, "result": BLOCKED_RESULT, "reason": str(exc)}
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print("GitHub Actions/GHCR static workflow plan verification")
            print(f"- result: {BLOCKED_RESULT}")
            print(f"- reason: {exc}")
        return 1 if args.strict else 0
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else render(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
