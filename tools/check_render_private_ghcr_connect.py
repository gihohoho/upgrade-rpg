#!/usr/bin/env python3
"""Validate the sanitized v338 Render private-GHCR Connect evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any


SCHEMA_VERSION = "v338.render-private-ghcr-exact-digest-connect-verified-service-creation-blocked"
RESULT = "render-ghcr-read-credential-exact-digest-connect-verified"
NEXT_SAFE_STAGE = "review-render-service-settings-and-database-initialization-plan"
EVIDENCE_PATH = Path("deploy/review/render-private-ghcr-connect-v338.json")
EXPECTED_REFERENCE = (
    "ghcr.io/gihohoho/upgrade-rpg-backend@sha256:"
    "ff939391517452a3ec477adaa0f8556d3525f9d0c6fb5f9d0df11d8f3d8461d2"
)
HANDOFF_PATHS = (
    Path("AGENTS.md"),
    Path("NEXT_CHAT_PROMPT.md"),
    Path("NEXT_CHAT_HANDOFF.md"),
    Path("docs/current/CURRENT_STATUS.md"),
    Path("docs/handoff/NEXT_CHAT_PROMPT.md"),
    Path("docs/handoff/NEXT_CHAT_HANDOFF.md"),
)


class RenderConnectError(RuntimeError):
    """Raised when the evidence or handoff state violates the v338 boundary."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RenderConnectError(message)


def load_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing evidence: {path.as_posix()}")
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), "evidence root must be an object")
    return data


def verify(root: Path) -> dict[str, Any]:
    evidence_path = root / EVIDENCE_PATH
    evidence_text = evidence_path.read_text(encoding="utf-8") if evidence_path.is_file() else ""
    require(not re.search(r"ghp_[A-Za-z0-9]{20,}", evidence_text), "PAT-like value found in evidence")
    evidence = load_json(evidence_path)

    require(evidence.get("schemaVersion") == SCHEMA_VERSION, "schemaVersion differs")
    require(evidence.get("result") == RESULT, "result differs")
    require(evidence.get("nextSafeStage") == NEXT_SAFE_STAGE, "next safe stage differs")
    require(evidence.get("secretOrPersonalDataRecorded") is False, "secret recording flag must be false")

    approval = evidence.get("ownerAuthorization", {})
    for key in (
        "githubConfirmAccessCompletedByOwner",
        "credentialCreationApproved",
        "credentialStorageApproved",
        "exactDigestConnectApproved",
    ):
        require(approval.get(key) is True, f"owner authorization missing: {key}")
    for key in ("webServiceCreationApproved", "deploymentApproved"):
        require(approval.get(key) is False, f"blocked authorization must remain false: {key}")

    credential = evidence.get("credential", {})
    require(credential.get("renderCredentialName") == "upgrade-rpg-ghcr-read", "credential name differs")
    require(credential.get("registry") == "github", "registry differs")
    require(credential.get("username") == "gihohoho", "registry username differs")
    require(credential.get("tokenType") == "personal-access-token-classic", "token type differs")
    require(credential.get("expiresOn") == "2027-07-23", "token expiration differs")
    require(credential.get("scopes") == ["read:packages"], "token scopes are not minimal")
    for key in ("repoScope", "writePackagesScope", "deletePackagesScope", "actualTokenRecorded"):
        require(credential.get(key) is False, f"credential safety flag must remain false: {key}")
    require(credential.get("storedOnlyInRender") is True, "replacement token storage boundary differs")

    incident = evidence.get("rotationIncident", {})
    require(incident.get("firstTokenExposedInBrowserInspectionOutput") is True, "incident record missing")
    require(incident.get("firstTokenStoredInRender") is False, "exposed token must not be stored in Render")
    require(incident.get("firstTokenRevokedOnGitHub") is True, "exposed token must be revoked")
    require(incident.get("replacementTokenValueOutput") is False, "replacement token must not be output")
    require(incident.get("replacementTokenStoredInRender") is True, "replacement token storage not recorded")

    connect = evidence.get("connectValidation", {})
    require(connect.get("imageReference") == EXPECTED_REFERENCE, "exact image reference differs")
    require(connect.get("privateRegistryAccessAccepted") is True, "private registry access not verified")
    require(connect.get("serviceConfigurationFormReached") is True, "service form was not reached")

    mutations = evidence.get("mutations", {})
    require(mutations.get("registryCredentialCreated") is True, "credential creation not recorded")
    for key in (
        "paymentMethodAdded",
        "webServiceCreated",
        "environmentSecretsInjected",
        "deployExecuted",
        "databaseMutationExecuted",
        "alembicMutationExecuted",
    ):
        require(mutations.get(key) is False, f"blocked mutation must remain false: {key}")

    for relative in HANDOFF_PATHS:
        text = (root / relative).read_text(encoding="utf-8")
        require(SCHEMA_VERSION in text, f"{relative.as_posix()} is missing v338 schema marker")
        require(RESULT in text, f"{relative.as_posix()} is missing v338 result marker")
        require(NEXT_SAFE_STAGE in text, f"{relative.as_posix()} is missing v338 next-stage marker")

    require(
        (root / "NEXT_CHAT_PROMPT.md").read_bytes()
        == (root / "docs/handoff/NEXT_CHAT_PROMPT.md").read_bytes(),
        "NEXT_CHAT_PROMPT mirror differs",
    )
    require(
        (root / "NEXT_CHAT_HANDOFF.md").read_bytes()
        == (root / "docs/handoff/NEXT_CHAT_HANDOFF.md").read_bytes(),
        "NEXT_CHAT_HANDOFF mirror differs",
    )

    return {
        "schemaVersion": SCHEMA_VERSION,
        "result": RESULT,
        "nextSafeStage": NEXT_SAFE_STAGE,
        "imageReference": EXPECTED_REFERENCE,
        "webServiceCreated": False,
        "deployExecuted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="return non-zero on any mismatch")
    parser.add_argument("--json", action="store_true", help="print JSON")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        result = verify(root)
    except (OSError, json.JSONDecodeError, RenderConnectError) as exc:
        if args.json:
            print(json.dumps({"result": "blocked-or-failed", "reason": str(exc)}, ensure_ascii=False, indent=2))
        else:
            print(f"result: blocked-or-failed\nreason: {exc}")
        return 1 if args.strict else 0

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Render private GHCR exact-digest Connect verification (sanitized)")
        print(f"- image: {result['imageReference']}")
        print("- credential: read:packages only / actual value not recorded")
        print("- Web Service created/deploy executed: no/no")
        print(f"result: {result['result']}")
        print(f"next safe stage: {result['nextSafeStage']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
