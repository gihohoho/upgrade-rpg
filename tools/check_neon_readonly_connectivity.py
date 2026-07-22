#!/usr/bin/env python3
"""Validate and read-only probe local Neon direct and pooled URLs without leaking secrets."""

from __future__ import annotations

import argparse
import asyncio
import json
import ssl
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

import asyncpg


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV_FILE = ROOT / "deploy/.env.production"
EXPECTED_REGION_SUFFIX = ".ap-southeast-1.aws.neon.tech"
EXPECTED_DATABASE = "neondb"
EXPECTED_ROLE = "neondb_owner"
EVIDENCE_FILE = ROOT / "deploy/review/neon-readonly-connectivity-v336.json"
VERSION = "v336.neon-readonly-connectivity-verified-render-onboarding-required"
RESULT = "neon-direct-pooled-readonly-connectivity-verified"
NEXT_STAGE = "owner-connect-render-and-review-database-initialization-plan"


class NeonCheckError(RuntimeError):
    """A safe-to-display Neon validation failure."""


@dataclass(frozen=True)
class ConnectionTarget:
    label: str
    host: str
    port: int
    database: str
    user: str
    password: str
    pooled: bool
    sslmode: str


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise NeonCheckError(message)


def _load_local_values(path: Path) -> dict[str, str]:
    _require(path.is_file(), "local Neon env file is missing")
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        _require("=" in line, "local Neon env file contains an invalid line")
        key, value = line.split("=", 1)
        key = key.strip()
        _require(key not in values, f"duplicate local env key: {key}")
        values[key] = value.strip()
    return values


def _parse_target(label: str, raw_url: str, *, pooled: bool) -> ConnectionTarget:
    _require(bool(raw_url), f"{label} URL is empty")
    _require("\n" not in raw_url and "\r" not in raw_url, f"{label} URL must be one line")
    parsed = urlsplit(raw_url)
    _require(parsed.scheme in {"postgres", "postgresql"}, f"{label} URL scheme must be postgresql")
    _require(bool(parsed.username), f"{label} URL user is missing")
    _require(parsed.password is not None, f"{label} URL password is missing")
    _require(bool(parsed.hostname), f"{label} URL host is missing")
    _require(not parsed.fragment, f"{label} URL must not contain a fragment")

    host = str(parsed.hostname).lower()
    database = unquote(parsed.path.lstrip("/"))
    user = unquote(str(parsed.username))
    password = unquote(str(parsed.password))
    query = parse_qs(parsed.query, keep_blank_values=True)
    sslmode_values = query.get("sslmode", [])
    _require(len(sslmode_values) == 1, f"{label} URL must contain exactly one sslmode")
    sslmode = sslmode_values[0].lower()

    _require(host.endswith(EXPECTED_REGION_SUFFIX), f"{label} URL is not an AWS Singapore Neon endpoint")
    _require(("-pooler" in host) is pooled, f"{label} URL pooler host classification differs")
    _require(database == EXPECTED_DATABASE, f"{label} URL database must remain {EXPECTED_DATABASE}")
    _require(user == EXPECTED_ROLE, f"{label} URL role must remain {EXPECTED_ROLE}")
    _require(bool(password), f"{label} URL password is empty")
    _require(sslmode in {"require", "verify-full"}, f"{label} URL must require TLS")

    return ConnectionTarget(
        label=label,
        host=host,
        port=parsed.port or 5432,
        database=database,
        user=user,
        password=password,
        pooled=pooled,
        sslmode=sslmode,
    )


def _same_endpoint(direct: ConnectionTarget, pooled: ConnectionTarget) -> bool:
    return pooled.host.replace("-pooler", "", 1) == direct.host


def _validate_pair(values: dict[str, str]) -> tuple[ConnectionTarget, ConnectionTarget]:
    direct = _parse_target(
        "direct", values.get("NEON_DIRECT_DATABASE_URL", ""), pooled=False
    )
    pooled = _parse_target(
        "pooled", values.get("NEON_POOLED_DATABASE_URL", ""), pooled=True
    )
    _require(_same_endpoint(direct, pooled), "direct and pooled URLs do not target the same Neon endpoint")
    _require(direct.port == pooled.port, "direct and pooled URL ports differ")
    _require(direct.database == pooled.database, "direct and pooled URL databases differ")
    _require(direct.user == pooled.user, "direct and pooled URL roles differ")
    _require(direct.password == pooled.password, "direct and pooled URL credentials differ")
    return direct, pooled


def _verified_ssl_context() -> ssl.SSLContext:
    context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    return context


def _validate_evidence(path: Path) -> dict[str, object]:
    _require(path.is_file(), "sanitized Neon evidence file is missing")
    try:
        evidence = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise NeonCheckError(f"sanitized Neon evidence is invalid ({type(exc).__name__})") from None
    _require(evidence.get("schemaVersion") == VERSION, "Neon evidence schema version differs")
    _require(evidence.get("provider") == "Neon Free", "Neon evidence provider differs")
    _require(evidence.get("region") == "aws-ap-southeast-1", "Neon evidence region differs")
    _require(evidence.get("postgresMajor") == 16, "Neon evidence PostgreSQL major differs")
    _require(evidence.get("database") == EXPECTED_DATABASE, "Neon evidence database differs")
    _require(evidence.get("role") == EXPECTED_ROLE, "Neon evidence role differs")
    _require(evidence.get("neonAuthEnabled") is False, "Neon Auth must remain disabled")

    credential = evidence.get("credential")
    _require(isinstance(credential, dict), "Neon evidence credential section is missing")
    _require(credential.get("initialExposedPasswordRotated") is True, "initial Neon password rotation is not recorded")
    _require(credential.get("actualValuesStoredInEvidence") is False, "Neon evidence must not contain credential values")

    checks = evidence.get("checks")
    _require(isinstance(checks, dict), "Neon evidence checks section is missing")
    for key in (
        "directConnected",
        "pooledConnected",
        "certificateRequired",
        "hostnameVerified",
        "readOnlyTransaction",
        "selectOnly",
    ):
        _require(checks.get(key) is True, f"Neon evidence check is not true: {key}")
    _require(checks.get("tlsVersion") == "TLSv1.3", "Neon evidence TLS version differs")

    mutations = evidence.get("mutations")
    _require(isinstance(mutations, dict), "Neon evidence mutation section is missing")
    for key in ("databaseWrite", "databaseCreate", "schemaChange", "dataRestore", "alembic"):
        _require(mutations.get(key) is False, f"Neon mutation must remain false: {key}")
    _require(evidence.get("secretOrEndpointRecorded") is False, "secret or endpoint must not be recorded")
    _require(evidence.get("result") == RESULT, "Neon evidence result differs")
    _require(evidence.get("nextSafeStage") == NEXT_STAGE, "Neon evidence next stage differs")
    return evidence


async def _probe(target: ConnectionTarget) -> dict[str, object]:
    connection: asyncpg.Connection | None = None
    try:
        connection = await asyncpg.connect(
            host=target.host,
            port=target.port,
            user=target.user,
            password=target.password,
            database=target.database,
            ssl=_verified_ssl_context(),
            timeout=20,
            command_timeout=10,
            statement_cache_size=0 if target.pooled else 100,
            server_settings={"application_name": "upgrade-rpg-neon-readonly-check"},
        )
        transport = getattr(connection, "_transport", None)
        tls_object = transport.get_extra_info("ssl_object") if transport is not None else None
        _require(tls_object is not None, f"{target.label} client transport is not using TLS")
        tls_version = tls_object.version()
        tls_cipher = tls_object.cipher()
        peer_certificate = tls_object.getpeercert()
        _require(bool(tls_version), f"{target.label} TLS version is unavailable")
        _require(bool(tls_cipher), f"{target.label} TLS cipher is unavailable")
        _require(bool(peer_certificate), f"{target.label} peer certificate is unavailable")

        async with connection.transaction(readonly=True):
            identity = await connection.fetchrow(
                "SELECT current_database()::text AS database, "
                "current_user::text AS role, "
                "current_setting('server_version')::text AS server_version, "
                "current_setting('transaction_read_only')::text AS transaction_read_only"
            )
            select_one = await connection.fetchval("SELECT 1")

        _require(identity is not None, f"{target.label} identity query returned no row")
        _require(identity["database"] == EXPECTED_DATABASE, f"{target.label} connected database differs")
        _require(identity["role"] == EXPECTED_ROLE, f"{target.label} connected role differs")
        _require(identity["transaction_read_only"] == "on", f"{target.label} transaction is not read-only")
        server_version = str(identity["server_version"])
        _require(server_version.split(".", 1)[0] == "16", f"{target.label} PostgreSQL major version is not 16")
        _require(select_one == 1, f"{target.label} SELECT 1 failed")
        return {
            "connected": True,
            "database": EXPECTED_DATABASE,
            "role": EXPECTED_ROLE,
            "serverVersion": server_version,
            "readOnlyTransaction": True,
            "tls": True,
            "tlsVersion": str(tls_version),
            "tlsCipherPresent": True,
            "peerCertificatePresent": True,
            "hostnameVerification": True,
        }
    except NeonCheckError:
        raise
    except Exception as exc:  # Never include the original message; it may echo a DSN.
        raise NeonCheckError(f"{target.label} connection failed ({type(exc).__name__})") from None
    finally:
        if connection is not None:
            await connection.close()


async def _run(env_file: Path, *, execute: bool) -> int:
    values = _load_local_values(env_file)
    direct, pooled = _validate_pair(values)
    print("Neon read-only connectivity validation")
    print("- local URL file: present, Git-excluded path expected; values not printed")
    print("- target: PostgreSQL 16 / AWS Singapore / neondb / neondb_owner")
    print("- URL pair: direct + pooled, same endpoint and credential")
    print("- TLS policy: certificate-required + hostname verification (verify-full equivalent)")
    if not execute:
        print("- database connection attempted: no")
        print("- result: neon-readonly-connectivity-ready")
        return 0

    for target in (direct, pooled):
        result = await _probe(target)
        print(
            f"- {target.label}: connected=yes, TLS={result['tlsVersion']}, "
            f"hostname-verified=yes, read-only=yes, PostgreSQL={result['serverVersion']}"
        )
    print("- database writes/migrations attempted: no")
    print("- result: neon-direct-pooled-readonly-connectivity-verified")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV_FILE)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--execute", action="store_true", help="perform two read-only TLS connections")
    mode.add_argument("--evidence", action="store_true", help="validate sanitized committed evidence only")
    args = parser.parse_args()
    try:
        if args.evidence:
            evidence = _validate_evidence(EVIDENCE_FILE)
            print("Neon sanitized connectivity evidence verification")
            print(f"- PostgreSQL: {evidence['postgresMajor']} / region: {evidence['region']}")
            print("- direct/pooled + TLS hostname verification + read-only: verified")
            print("- secret/endpoint recorded: no")
            print(f"- result: {RESULT}")
            print(f"- next safe stage: {NEXT_STAGE}")
            return 0
        return asyncio.run(_run(args.env_file.resolve(), execute=args.execute))
    except NeonCheckError as exc:
        print(f"Neon read-only connectivity check failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
