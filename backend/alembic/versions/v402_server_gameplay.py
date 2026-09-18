"""Add server-owned online gameplay and atomic action receipts.

Existing character snapshots are unchanged by this additive migration.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "v402_server_gameplay"
down_revision = "v377_auth_email_public_security"
branch_labels = None
depends_on = None


def common_columns():
    return [
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    ]


def upgrade():
    op.create_table(
        "game_sessions",
        *common_columns(),
        sa.Column(
            "snapshot_id",
            sa.Integer(),
            sa.ForeignKey("user_save_snapshots.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("session_key", sa.String(64), nullable=False, unique=True),
        sa.Column("auth_version", sa.Integer(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("connected", sa.Boolean(), nullable=False),
        sa.Column("connection_key", sa.String(64), nullable=True),
        sa.Column("lease_until", sa.DateTime(timezone=True), nullable=False),
        sa.Column("settled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revision", sa.BigInteger(), nullable=False),
        sa.Column("rng_seed", sa.String(64), nullable=False),
        sa.Column("rng_cursor", sa.BigInteger(), nullable=False),
        sa.Column("runtime_json", postgresql.JSONB(), nullable=False),
    )
    op.create_index("ix_game_sessions_id", "game_sessions", ["id"])
    op.create_index("ix_game_sessions_lease_until", "game_sessions", ["lease_until"])
    op.create_table(
        "game_action_receipts",
        *common_columns(),
        sa.Column(
            "snapshot_id",
            sa.Integer(),
            sa.ForeignKey("user_save_snapshots.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("request_id", sa.String(64), nullable=False),
        sa.Column("request_hash", sa.String(64), nullable=False),
        sa.Column("session_key", sa.String(64), nullable=False),
        sa.Column("result_json", postgresql.JSONB(), nullable=False),
        sa.UniqueConstraint("snapshot_id", "request_id", name="uq_game_action_request"),
    )
    op.create_index("ix_game_action_receipts_id", "game_action_receipts", ["id"])
    op.create_index("ix_game_action_receipts_snapshot_id", "game_action_receipts", ["snapshot_id"])


def downgrade():
    op.drop_table("game_action_receipts")
    op.drop_table("game_sessions")
