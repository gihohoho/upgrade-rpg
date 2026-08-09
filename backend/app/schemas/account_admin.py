from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AccountAdminBootstrapRequest(BaseModel):
    """Request the one-time promotion of the first real administrator."""

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    reason: str | None = Field(default=None, max_length=500)


class AccountAdminStatusPreviewRequest(BaseModel):
    """Preview one account activation/suspension change without writing."""

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    base_is_active: bool = Field(alias="baseIsActive")
    next_is_active: bool = Field(alias="nextIsActive")
    reason: str = Field(min_length=2, max_length=500)


class AccountAdminStatusApplyRequest(AccountAdminStatusPreviewRequest):
    """Apply a reviewed account status change after exact confirmation."""

    confirm_text: str = Field(default="", alias="confirmText", max_length=180)
