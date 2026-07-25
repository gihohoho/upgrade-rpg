#!/usr/bin/env python3
"""Static/runtime smoke for the production asyncpg verify-full bootstrap."""

from __future__ import annotations

import os
import ssl
import sys
from pathlib import Path

from pydantic import ValidationError


ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))
os.environ["ENVIRONMENT"] = "local"
os.environ["DEBUG"] = "false"

from app.core.config import Settings, build_database_connect_args  # noqa: E402


SAFE_SECRET = "s" * 40
SAFE_ADMIN_KEY = "a" * 40
SAFE_DATABASE_URL = (
    "postgresql+asyncpg://neondb_owner:password@"
    "ep-example.ap-southeast-1.aws.neon.tech/neondb"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def production_settings(database_url: str = SAFE_DATABASE_URL) -> Settings:
    return Settings(
        _env_file=None,
        environment="production",
        debug=False,
        database_url=database_url,
        jwt_secret_key=SAFE_SECRET,
        admin_write_dev_key=SAFE_ADMIN_KEY,
        **{"CORS_ORIGINS": "[]"},
    )


def expect_invalid(database_url: str, marker: str) -> None:
    try:
        production_settings(database_url)
    except ValidationError as exc:
        require(marker in str(exc), f"missing validation marker: {marker}")
        return
    raise AssertionError(f"unsafe production DATABASE_URL was accepted: {marker}")


def main() -> int:
    selected = production_settings()
    connect_args = build_database_connect_args(selected)
    context = connect_args.get("ssl")
    require(isinstance(context, ssl.SSLContext), "production SSLContext is missing")
    require(context.check_hostname is True, "production hostname verification is disabled")
    require(context.verify_mode == ssl.CERT_REQUIRED, "production certificate verification is disabled")
    require(context.minimum_version >= ssl.TLSVersion.TLSv1_2, "production TLS minimum is below TLSv1.2")
    require(context.cert_store_stats().get("x509_ca", 0) > 0, "production CA trust store is empty")

    local = Settings(_env_file=None)
    require(build_database_connect_args(local) == {}, "local runtime must not inject production TLS args")

    expect_invalid(
        SAFE_DATABASE_URL + "?sslmode=require",
        "must not contain TLS query parameters",
    )
    expect_invalid(
        "postgresql+asyncpg://user:password@127.0.0.1:5432/neondb",
        "must not target localhost",
    )
    expect_invalid(
        "postgresql://user:password@db.example.test:5432/neondb",
        "must use postgresql+asyncpg",
    )

    session_source = (BACKEND / "app/db/session.py").read_text(encoding="utf-8")
    alembic_source = (BACKEND / "alembic/env.py").read_text(encoding="utf-8")
    for label, source in (("runtime", session_source), ("alembic", alembic_source)):
        require("build_database_connect_args" in source, f"{label} does not use shared TLS connect args")
        require("connect_args=build_database_connect_args()" in source, f"{label} connect_args binding differs")

    print("Neon production database bootstrap smoke")
    print("- production system CA + certificate + hostname verification: yes")
    print("- local runtime behavior preserved: yes")
    print("- conflicting TLS query/local target/wrong driver rejected: yes")
    print("- runtime and Alembic shared connect args: yes")
    print("- result: neon-production-database-bootstrap-verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
