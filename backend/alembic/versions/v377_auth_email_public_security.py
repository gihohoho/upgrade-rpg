"""Add durable auth email outbox and persistent auth rate limits.

Revision ID: v377_auth_email_public_security
Revises: v371_email_identity_lifecycle
Create Date: 2026-08-15

The new tables contain only source-controlled policy names and HMAC digests.
They do not store a recipient address, raw action token, rendered email body,
IP address, username, bearer token, or provider credential.
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "v377_auth_email_public_security"
down_revision: str | None = "v371_email_identity_lifecycle"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the persistent public-auth security tables."""
    op.create_table(
        "auth_rate_limit_buckets",
        sa.Column("scope", sa.String(length=80), nullable=False),
        sa.Column("subject_digest", sa.String(length=64), nullable=False),
        sa.Column("window_started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "request_count",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "failure_count",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column("blocked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_failure_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "char_length(subject_digest) = 64",
            name="ck_auth_rate_limit_buckets_digest_length",
        ),
        sa.CheckConstraint(
            "request_count >= 0",
            name="ck_auth_rate_limit_buckets_request_count",
        ),
        sa.CheckConstraint(
            "failure_count >= 0",
            name="ck_auth_rate_limit_buckets_failure_count",
        ),
        sa.PrimaryKeyConstraint("scope", "subject_digest"),
    )
    op.create_index(
        "ix_auth_rate_limit_buckets_updated_at",
        "auth_rate_limit_buckets",
        ["updated_at"],
        unique=False,
    )
    op.create_index(
        "ix_auth_rate_limit_buckets_blocked_until",
        "auth_rate_limit_buckets",
        ["blocked_until"],
        unique=False,
    )

    op.create_table(
        "auth_email_outbox",
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("purpose", sa.String(length=40), nullable=False),
        sa.Column("target_digest", sa.String(length=64), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'pending'"),
            nullable=False,
        ),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("claimed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("attempted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "attempt_count",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column("action_token_id", sa.Integer(), nullable=True),
        sa.Column("provider_message_id", sa.String(length=160), nullable=True),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "purpose IN ('verify_email', 'username_recovery', "
            "'password_reset', 'account_deletion')",
            name="ck_auth_email_outbox_purpose",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'preparing', 'sending', 'sent', 'failed', 'suppressed')",
            name="ck_auth_email_outbox_status",
        ),
        sa.CheckConstraint(
            "attempt_count >= 0 AND attempt_count <= 1",
            name="ck_auth_email_outbox_single_attempt",
        ),
        sa.CheckConstraint(
            "char_length(target_digest) = 64",
            name="ck_auth_email_outbox_target_digest_length",
        ),
        sa.CheckConstraint(
            "(status = 'pending' AND attempt_count = 0 AND claimed_at IS NULL "
            "AND attempted_at IS NULL AND completed_at IS NULL) OR "
            "(status = 'preparing' AND attempt_count = 0 AND claimed_at IS NOT NULL "
            "AND attempted_at IS NULL AND completed_at IS NULL) OR "
            "(status = 'sending' AND attempt_count = 1 AND claimed_at IS NOT NULL "
            "AND attempted_at IS NOT NULL AND completed_at IS NULL) OR "
            "(status = 'sent' AND attempt_count = 1 AND attempted_at IS NOT NULL "
            "AND completed_at IS NOT NULL AND provider_message_id IS NOT NULL "
            "AND error_code IS NULL) OR "
            "(status = 'failed' AND attempt_count = 1 AND attempted_at IS NOT NULL "
            "AND completed_at IS NOT NULL AND error_code IS NOT NULL) OR "
            "(status = 'suppressed' AND attempt_count = 0 AND attempted_at IS NULL "
            "AND completed_at IS NOT NULL AND error_code IS NOT NULL)",
            name="ck_auth_email_outbox_state_shape",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["action_token_id"],
            ["user_email_action_tokens.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_auth_email_outbox_id"),
        "auth_email_outbox",
        ["id"],
        unique=False,
    )
    op.create_index(
        "ix_auth_email_outbox_pending",
        "auth_email_outbox",
        ["status", "available_at", "id"],
        unique=False,
    )
    op.create_index(
        "ix_auth_email_outbox_user_purpose",
        "auth_email_outbox",
        ["user_id", "purpose", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_auth_email_outbox_target_purpose",
        "auth_email_outbox",
        ["target_digest", "purpose", "created_at"],
        unique=False,
    )
    op.create_index(
        "uq_auth_email_outbox_pending_target_purpose",
        "auth_email_outbox",
        ["target_digest", "purpose"],
        unique=True,
        postgresql_where=sa.text("status = 'pending'"),
    )
    op.create_index(
        "uq_auth_email_outbox_inflight_target_purpose",
        "auth_email_outbox",
        ["target_digest", "purpose"],
        unique=True,
        postgresql_where=sa.text("status IN ('preparing', 'sending')"),
    )


def downgrade() -> None:
    """Remove only the v377 public-auth security tables."""
    op.drop_index(
        "uq_auth_email_outbox_inflight_target_purpose",
        table_name="auth_email_outbox",
    )
    op.drop_index(
        "uq_auth_email_outbox_pending_target_purpose",
        table_name="auth_email_outbox",
    )
    op.drop_index(
        "ix_auth_email_outbox_target_purpose",
        table_name="auth_email_outbox",
    )
    op.drop_index(
        "ix_auth_email_outbox_user_purpose",
        table_name="auth_email_outbox",
    )
    op.drop_index(
        "ix_auth_email_outbox_pending",
        table_name="auth_email_outbox",
    )
    op.drop_index(
        op.f("ix_auth_email_outbox_id"),
        table_name="auth_email_outbox",
    )
    op.drop_table("auth_email_outbox")

    op.drop_index(
        "ix_auth_rate_limit_buckets_blocked_until",
        table_name="auth_rate_limit_buckets",
    )
    op.drop_index(
        "ix_auth_rate_limit_buckets_updated_at",
        table_name="auth_rate_limit_buckets",
    )
    op.drop_table("auth_rate_limit_buckets")
