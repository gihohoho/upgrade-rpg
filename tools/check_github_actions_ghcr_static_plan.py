#!/usr/bin/env python3
"""Validate the v317 GitHub Actions/GHCR plan without creating or running a workflow."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any

TOOL_VERSION = "v317.github-actions-ghcr-static-workflow-plan"
READY_RESULT = "github-actions-ghcr-static-plan-verified-workflow-not-created"
BLOCKED_RESULT = "blocked-or-failed"
NEXT_SAFE_STAGE = "review-action-shas-repository-settings-and-workflow-creation-approval"
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

    _require(plan.get("schemaVersion") == TOOL_VERSION, "unexpected v317 schemaVersion")
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
    _require(action_policy.get("resolvedActionShasApproved") is False, "unreviewed action SHAs must not be approved")
    _require(action_policy.get("workflowCreationBlockedUntilResolved") is True, "workflow creation must remain blocked")
    allowlist = action_policy.get("allowlist")
    _require(isinstance(allowlist, list), "action allowlist must be a list")
    repositories = tuple(item.get("repository") for item in allowlist if isinstance(item, dict))
    _require(repositories == ALLOWED_ACTIONS, "action allowlist or order changed")
    for item in allowlist:
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

    setup = plan.get("requiredRepositorySetup")
    _require(isinstance(setup, dict), "requiredRepositorySetup must be an object")
    for key in (
        "githubConnectorRepositoryAccess",
        "actionsSettingsReviewed",
        "fullLengthActionShaPolicyEnabled",
        "publishEnvironmentConfigured",
    ):
        _require(_bool(setup, key) is False, f"unverified repository setup must remain false: {key}")
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
        "actionShasApproved": False,
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
        "- action SHAs approved: no",
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
