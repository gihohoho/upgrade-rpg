"""Add verified email identity and single-use email action tokens.

Revision ID: v371_email_identity_lifecycle
Revises: v295_initial_schema
Create Date: 2026-08-11

This revision is intentionally source-only until an exact migration approval is
given. Existing accounts keep nullable email fields; public registration code is
responsible for requiring a validated address for every new account.
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "v371_email_identity_lifecycle"
down_revision: str | None = "v295_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add nullable legacy-safe identity fields and a new empty token table."""
    op.add_column("users", sa.Column("email_original", sa.String(length=254), nullable=True))
    op.add_column("users", sa.Column("email_canonical", sa.String(length=254), nullable=True))
    op.add_column(
        "users",
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column(
            "auth_version",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_users_email_canonical",
        "users",
        ["email_canonical"],
        unique=True,
    )

    op.create_table(
        "user_email_action_tokens",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("purpose", sa.String(length=40), nullable=False),
        sa.Column("token_digest", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "delivery_status",
            sa.String(length=20),
            server_default=sa.text("'pending'"),
            nullable=False,
        ),
        sa.Column("delivery_attempted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("provider_message_id", sa.String(length=160), nullable=True),
        sa.Column("delivery_error_code", sa.String(length=80), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "purpose IN ('verify_email', 'password_reset', 'account_deletion')",
            name="ck_user_email_action_tokens_purpose",
        ),
        sa.CheckConstraint(
            "delivery_status IN ('pending', 'sent', 'failed')",
            name="ck_user_email_action_tokens_delivery_status",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_user_email_action_tokens_id"),
        "user_email_action_tokens",
        ["id"],
        unique=False,
    )
    op.create_index(
        "ix_user_email_action_tokens_token_digest",
        "user_email_action_tokens",
        ["token_digest"],
        unique=True,
    )
    op.create_index(
        "ix_user_email_action_tokens_user_purpose_expires",
        "user_email_action_tokens",
        ["user_id", "purpose", "expires_at"],
        unique=False,
    )
    op.create_index(
        "ix_user_email_action_tokens_expires_at",
        "user_email_action_tokens",
        ["expires_at"],
        unique=False,
    )


def downgrade() -> None:
    """Remove the v371 token table and email identity columns."""
    op.drop_index(
        "ix_user_email_action_tokens_expires_at",
        table_name="user_email_action_tokens",
    )
    op.drop_index(
        "ix_user_email_action_tokens_user_purpose_expires",
        table_name="user_email_action_tokens",
    )
    op.drop_index(
        "ix_user_email_action_tokens_token_digest",
        table_name="user_email_action_tokens",
    )
    op.drop_index(
        op.f("ix_user_email_action_tokens_id"),
        table_name="user_email_action_tokens",
    )
    op.drop_table("user_email_action_tokens")

    op.drop_index("ix_users_email_canonical", table_name="users")
    op.drop_column("users", "auth_version")
    op.drop_column("users", "email_verified_at")
    op.drop_column("users", "email_canonical")
    op.drop_column("users", "email_original")
