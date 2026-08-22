import asyncio
from logging.config import fileConfig
import os

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import build_database_connect_args, settings
from app.db.base import Base
from app.models import *  # noqa: F401,F403 - Alembic metadata collection

config = context.config
existing_connection = config.attributes.get("connection")
if existing_connection is None:
    config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

ALEMBIC_V377_GUARD_MODE = "v377"
ALEMBIC_V377_LOCK_TIMEOUT_MS = "5000"
ALEMBIC_V377_STATEMENT_TIMEOUT_MS = "120000"
ALEMBIC_V377_APPLICATION_NAMES = {
    "upgrade-rpg-v377-isolated-migration",
    "upgrade-rpg-v377-target-migration",
}


def build_alembic_connect_args(*, guard_required: bool = False) -> dict[str, object]:
    """Add bounded server settings only for the exact v377 execution guards."""
    connect_args = dict(build_database_connect_args())
    names = (
        "ALEMBIC_GUARD_MODE",
        "ALEMBIC_LOCK_TIMEOUT_MS",
        "ALEMBIC_STATEMENT_TIMEOUT_MS",
        "ALEMBIC_APPLICATION_NAME",
    )
    values = {name: str(os.environ.get(name) or "").strip() for name in names}
    if not any(values.values()):
        if guard_required:
            raise RuntimeError("missing_v377_alembic_guard_environment")
        return connect_args
    if values != {
        "ALEMBIC_GUARD_MODE": ALEMBIC_V377_GUARD_MODE,
        "ALEMBIC_LOCK_TIMEOUT_MS": ALEMBIC_V377_LOCK_TIMEOUT_MS,
        "ALEMBIC_STATEMENT_TIMEOUT_MS": ALEMBIC_V377_STATEMENT_TIMEOUT_MS,
        "ALEMBIC_APPLICATION_NAME": values["ALEMBIC_APPLICATION_NAME"],
    } or values["ALEMBIC_APPLICATION_NAME"] not in ALEMBIC_V377_APPLICATION_NAMES:
        raise RuntimeError("invalid_v377_alembic_guard_environment")
    connect_args["server_settings"] = {
        "lock_timeout": f"{ALEMBIC_V377_LOCK_TIMEOUT_MS}ms",
        "statement_timeout": f"{ALEMBIC_V377_STATEMENT_TIMEOUT_MS}ms",
        "application_name": values["ALEMBIC_APPLICATION_NAME"],
    }
    return connect_args


def run_migrations_offline() -> None:
    """Generate SQL without opening a database connection."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run Alembic's synchronous migration context on an async connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Open the configured asyncpg connection through SQLAlchemy's async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=build_alembic_connect_args(),
    )

    try:
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
    finally:
        await connectable.dispose()


def run_migrations_online() -> None:
    """Run online commands such as `alembic current` with the async DB URL."""
    if existing_connection is not None:
        if not isinstance(existing_connection, Connection):
            raise RuntimeError("invalid_existing_alembic_connection")
        # The target apply guard owns this synchronous connection and its outer
        # transaction. Validate the exact process guard here because no async
        # engine/connect_args path is used in this mode.
        build_alembic_connect_args(guard_required=True)
        do_run_migrations(existing_connection)
        return
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
