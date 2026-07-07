"""Check the local save snapshot API.

Run from the backend folder while FastAPI is running:

    python scripts/check_save_snapshot_api.py
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
import urllib.parse
from typing import Any

DEFAULT_BASE_URL = "http://127.0.0.1:8000/api/v1"


def request_json(method: str, url: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Accept": "application/json", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {error.code}: {detail}") from error


def request_status(method: str, url: str, body: dict[str, Any] | None = None) -> tuple[int, str]:
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Accept": "application/json", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--slot-key", default="smoke")
    args = parser.parse_args()

    now = int(time.time() * 1000)
    save_payload = {
        "saveVersion": 5,
        "clientSaveKey": "idleRpgSaveV22",
        "slotKey": args.slot_key,
        "snapshot": {
            "saveVersion": 5,
            "player": {
                "gold": 12345,
                "inventory": [],
                "storage": [],
                "trash": [],
                "mailbox": [],
            },
            "currentZoneIndex": 0,
            "currentZoneType": "field",
            "smokeSavedAt": now,
        },
        "summary": {"gold": 12345, "currentZoneIndex": 0, "smokeSavedAt": now},
        "source": "smoke-test",
        "note": "save snapshot API smoke test",
    }

    encoded_slot_key = urllib.parse.quote(args.slot_key, safe="")
    save_url = f"{args.base_url.rstrip('/')}/game/save"
    load_url = f"{args.base_url.rstrip('/')}/game/load?slotKey={encoded_slot_key}"
    slots_url = f"{args.base_url.rstrip('/')}/game/save-slots"
    invalid_slot_url = f"{args.base_url.rstrip('/')}/game/save"

    saved = request_json("POST", save_url, save_payload)
    loaded = request_json("GET", load_url)
    slots = request_json("GET", slots_url)
    invalid_slot_payload = {**save_payload, "slotKey": "../bad-slot"}
    invalid_slot_status, invalid_slot_body = request_status("POST", invalid_slot_url, invalid_slot_payload)

    failures: list[str] = []
    if not saved.get("ok"):
        failures.append("save response ok=false")
    if not loaded.get("ok"):
        failures.append("load response ok=false")
    if saved.get("type") != "game.save":
        failures.append("save response type mismatch")
    if loaded.get("type") != "game.load":
        failures.append("load response type mismatch")
    if not slots.get("ok"):
        failures.append("slots response ok=false")
    if slots.get("type") != "game.save_slots":
        failures.append("slots response type mismatch")
    slot_keys = [slot.get("slotKey") for slot in slots.get("payload", {}).get("slots", [])]
    if args.slot_key not in slot_keys:
        failures.append("saved slot is missing from slots response")
    if loaded.get("payload", {}).get("exists") is not True:
        failures.append("loaded payload exists is not true")
    if loaded.get("payload", {}).get("saveVersion") != 5:
        failures.append("loaded saveVersion mismatch")
    if loaded.get("payload", {}).get("snapshot", {}).get("smokeSavedAt") != now:
        failures.append("loaded snapshot smokeSavedAt mismatch")
    saved_integrity = saved.get("payload", {}).get("integrity") or {}
    loaded_integrity = loaded.get("payload", {}).get("integrity") or {}
    if not saved_integrity.get("snapshotSha256"):
        failures.append("saved integrity snapshotSha256 missing")
    if saved_integrity.get("snapshotSha256") != loaded_integrity.get("snapshotSha256"):
        failures.append("saved/loaded integrity snapshotSha256 mismatch")
    if not isinstance(saved_integrity.get("snapshotBytes"), int) or saved_integrity.get("snapshotBytes", 0) <= 0:
        failures.append("saved integrity snapshotBytes invalid")
    if invalid_slot_status != 422:
        failures.append(f"invalid slotKey should return 422, got {invalid_slot_status}")

    result = {
        "ok": not failures,
        "saveUrl": save_url,
        "loadUrl": load_url,
        "slotsUrl": slots_url,
        "invalidSlotUrl": invalid_slot_url,
        "saved": saved.get("data"),
        "loaded": loaded.get("data"),
        "slots": slots.get("data"),
        "savedIntegrity": saved.get("payload", {}).get("integrity"),
        "loadedIntegrity": loaded.get("payload", {}).get("integrity"),
        "invalidSlotStatus": invalid_slot_status,
        "invalidSlotBody": invalid_slot_body[:500],
        "failures": failures,
    }

    if failures:
        print("save snapshot API check failed")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1

    print("save snapshot API check passed")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
