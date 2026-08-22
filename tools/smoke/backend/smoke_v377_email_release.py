#!/usr/bin/env python3
"""Focused temp-fixture smoke for the source-only v377 release guard."""

from __future__ import annotations

import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

from prepare_v377_email_release import (  # noqa: E402
    IMAGE_POLICY_PATH,
    IMAGE_REPOSITORY,
    LIFECYCLE_PATH,
    OLD_IMAGE_DIGEST,
    OLD_IMAGE_REFERENCE,
    PLAN_PATH,
    REQUIRED_ENV_KEYS,
    V351_EVIDENCE_PATH,
    V377ReleaseGuardError,
    close_publish_authorization,
    create_fresh_publish_preparation,
    create_render_preparation,
    load_json,
    open_publish_authorization,
    record_publish_attempt,
    record_render_attempt,
    validate_fresh_publish_preparation,
    validate_render_preparation,
    validate_static_guard,
)


NEW_DIGEST = "sha256:" + "a" * 64
PREPARATION_SHA = "1" * 40
AUTHORIZATION_SHA = "2" * 40
CLOSURE_SHA = "3" * 40
NEW_DEPLOY_ID = "dep-v377emailattempt001"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def expect_blocked(action, message: str) -> None:
    try:
        action()
    except V377ReleaseGuardError:
        return
    raise AssertionError(message)


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def lifecycle_fixture() -> tuple[dict, dict, dict, dict, dict]:
    policy = load_json(IMAGE_POLICY_PATH)
    current = load_json(LIFECYCLE_PATH)
    if current.get("state") == "attempt-recorded":
        previous = current
    else:
        previous = copy.deepcopy(current)
        history = previous["attemptHistory"]
        latest = history[-1]
        previous["state"] = "attempt-recorded"
        previous["publishReviewerGateReady"] = False
        previous["priorApprovedPreparationSha"] = history[-2]["preparationSha"]
        previous["priorAttemptEvidence"] = history[-2]
        previous["attemptHistory"] = history[:-1]
        previous["approvedPreparationSha"] = latest["preparationSha"]
        previous["closure"] = {
            "authorizationSourceSha": latest["authorizationSha"],
            "closureCommitSha": latest["closureSha"],
            "preparedAtUtc": current["githubLiveSettings"]["recheckedAtUtc"],
        }
        previous["observedAttempt"] = {
            "runId": latest["runId"],
            "runUrl": latest["runUrl"],
            "runAttempt": 1,
            "status": "completed",
            "conclusion": latest["conclusion"],
            "imageDigest": latest["imageDigest"],
            "signatureVerified": latest["signatureVerified"],
        }
    prepared = create_fresh_publish_preparation(previous, policy)
    timestamp = now_utc()
    opened = open_publish_authorization(
        prepared,
        preparation_sha=PREPARATION_SHA,
        approved_at_utc=timestamp,
        live_settings_rechecked_at_utc=timestamp,
    )
    closed = close_publish_authorization(
        opened,
        authorization_sha=AUTHORIZATION_SHA,
        run_id=377000001,
        run_status="in_progress",
        closed_at_utc=timestamp,
    )
    recorded = record_publish_attempt(
        closed,
        closure_sha=CLOSURE_SHA,
        conclusion="success",
        image_digest=NEW_DIGEST,
        signature_verified=True,
    )
    return previous, prepared, opened, closed, recorded


def test_static_and_lifecycle() -> dict:
    plan = load_json(PLAN_PATH)
    summary = validate_static_guard(plan)
    require(summary["providerMutationExecuted"] is False, "static guard claimed provider mutation")

    previous, prepared, opened, closed, recorded = lifecycle_fixture()
    require(prepared["attemptHistory"][:-1] == previous["attemptHistory"], "old attempt history changed")
    current_policy = load_json(IMAGE_POLICY_PATH)["currentAttemptEvidence"]
    require(
        prepared["attemptHistory"][-1]["recordCommitSha"] == current_policy["recordCommitSha"],
        "latest completed attempt was not preserved",
    )
    require(
        prepared["attemptHistory"][-1]["conclusion"] == current_policy["conclusion"],
        "latest completed attempt conclusion differs",
    )
    require(prepared["observedAttempt"]["status"] == "not-dispatched", "fresh preparation reused old attempt")
    require(opened["publishReviewerGateReady"] is True, "owner authorization did not open the gate")
    require(closed["publishReviewerGateReady"] is False, "accepted run did not close the gate")
    require(closed["observedAttempt"]["runAttempt"] == 1, "closure attempt differs")
    require(recorded["observedAttempt"]["imageDigest"] == NEW_DIGEST, "new digest was not recorded")

    policy = load_json(IMAGE_POLICY_PATH)
    expected_entry = prepared["attemptHistory"][-1]
    changed_history = copy.deepcopy(prepared)
    changed_history["attemptHistory"][0]["runId"] = -1
    expect_blocked(
        lambda: validate_fresh_publish_preparation(previous, changed_history, expected_entry),
        "mutated historical attempt was accepted",
    )
    expect_blocked(
        lambda: create_fresh_publish_preparation(prepared, policy),
        "a second preparation from the same completed evidence was accepted",
    )
    expect_blocked(
        lambda: record_publish_attempt(
            closed,
            closure_sha=CLOSURE_SHA,
            conclusion="success",
            image_digest=OLD_IMAGE_DIGEST,
            signature_verified=True,
        ),
        "v351 digest reuse was accepted",
    )
    historical_digest = previous["attemptHistory"][-1]["imageDigest"]
    expect_blocked(
        lambda: record_publish_attempt(
            closed,
            closure_sha=CLOSURE_SHA,
            conclusion="success",
            image_digest=historical_digest,
            signature_verified=True,
        ),
        "historical digest reuse was accepted",
    )
    expect_blocked(
        lambda: record_publish_attempt(
            closed,
            closure_sha=CLOSURE_SHA,
            conclusion="success",
            image_digest=NEW_DIGEST,
            signature_verified=False,
        ),
        "unsigned successful publish was accepted",
    )
    return recorded


def render_inventory() -> tuple[dict, dict]:
    evidence = load_json(V351_EVIDENCE_PATH)
    backend = evidence["backend"]
    inventory = {
        "serviceId": backend["serviceId"],
        "currentImageReference": OLD_IMAGE_REFERENCE,
        "latestDeployId": backend["deployId"],
        "environmentKeys": list(REQUIRED_ENV_KEYS),
    }
    return inventory, backend


def test_render(recorded_lifecycle: dict) -> None:
    plan = load_json(PLAN_PATH)
    inventory, backend = render_inventory()
    preparation = create_render_preparation(
        plan,
        recorded_lifecycle,
        inventory,
        source_sha=AUTHORIZATION_SHA,
    )
    serialized = json.dumps(preparation, sort_keys=True)
    require(backend["serviceId"] not in serialized, "raw Render service ID leaked")
    require(backend["deployId"] not in serialized, "raw v351 deploy ID leaked")
    require("https://" not in serialized, "provider endpoint leaked")
    require(preparation["deployAttemptCount"] == 0, "preparation claimed a deploy")

    observation = {
        "serviceId": backend["serviceId"],
        "deployId": NEW_DEPLOY_ID,
        "imageReference": f"{IMAGE_REPOSITORY}@{NEW_DIGEST}",
        "status": "live",
        "attemptCount": 1,
        "automaticRetry": False,
        "environmentKeys": list(REQUIRED_ENV_KEYS),
    }
    attempt = record_render_attempt(preparation, observation, plan)
    attempt_text = json.dumps(attempt, sort_keys=True)
    require(NEW_DEPLOY_ID not in attempt_text, "raw new deploy ID leaked")
    require(backend["serviceId"] not in attempt_text, "raw service ID leaked from attempt")
    require("https://" not in attempt_text, "provider endpoint leaked from attempt")
    require(attempt["deployAttemptCount"] == 1, "Render attempt count differs")
    require(attempt["automaticRetry"] is False, "Render retry record differs")

    missing_key = copy.deepcopy(inventory)
    missing_key["environmentKeys"].remove("AUTH_ABUSE_SECRET")
    expect_blocked(
        lambda: create_render_preparation(plan, recorded_lifecycle, missing_key, source_sha=AUTHORIZATION_SHA),
        "missing Render security key was accepted",
    )
    value_bearing = copy.deepcopy(inventory)
    value_bearing["environmentValues"] = {"BREVO_API_KEY": "must-never-be-read"}
    expect_blocked(
        lambda: create_render_preparation(plan, recorded_lifecycle, value_bearing, source_sha=AUTHORIZATION_SHA),
        "value-bearing Render inventory was accepted",
    )
    expect_blocked(
        lambda: create_render_preparation(plan, recorded_lifecycle, inventory, source_sha=PREPARATION_SHA),
        "wrong published source was accepted",
    )

    old_digest = copy.deepcopy(preparation)
    old_digest["imageDigest"] = OLD_IMAGE_DIGEST
    old_digest["imageReference"] = OLD_IMAGE_REFERENCE
    expect_blocked(
        lambda: validate_render_preparation(old_digest, plan),
        "v351 digest was accepted as a Render candidate",
    )

    old_deploy = copy.deepcopy(observation)
    old_deploy["deployId"] = backend["deployId"]
    expect_blocked(
        lambda: record_render_attempt(preparation, old_deploy, plan),
        "v351 deploy ID was accepted as a new attempt",
    )
    duplicate_attempt = copy.deepcopy(observation)
    duplicate_attempt["attemptCount"] = 2
    expect_blocked(
        lambda: record_render_attempt(preparation, duplicate_attempt, plan),
        "second Render deploy attempt was accepted",
    )
    automatic_retry = copy.deepcopy(observation)
    automatic_retry["automaticRetry"] = True
    expect_blocked(
        lambda: record_render_attempt(preparation, automatic_retry, plan),
        "Render automatic retry was accepted",
    )
    endpoint_bearing = copy.deepcopy(observation)
    endpoint_bearing["publicUrl"] = "https://must-not-be-recorded.invalid"
    expect_blocked(
        lambda: record_render_attempt(preparation, endpoint_bearing, plan),
        "endpoint-bearing Render observation was accepted",
    )


def main() -> int:
    recorded = test_static_and_lifecycle()
    test_render(recorded)
    print("v377 email release guard smoke")
    print("- fresh owner-only publish lifecycle and immutable history: verified")
    print("- old digest/deploy/evidence reuse and rerun: rejected")
    print("- Render environment evidence: required key names only")
    print("- sanitized one-attempt/no-retry Render record: verified")
    print("- network/provider mutation: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
