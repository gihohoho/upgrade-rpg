from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AdminChangePreviewRequest(BaseModel):
    target_type: str = Field(examples=["item_template", "boss", "drop_table"])
    target_id: str
    before: dict = Field(default_factory=dict)
    after: dict = Field(default_factory=dict)
    reason: str | None = None


class AdminMasterDataEditPreviewRequest(BaseModel):
    """Dry-run request for the static admin edit draft form.

    This request is intentionally preview-only. The endpoint that consumes it must
    validate the draft against the current DB row but must not mutate the database.
    """

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    domain: str = Field(min_length=1, max_length=80)
    id: int = Field(ge=1)
    draft: dict[str, Any] = Field(default_factory=dict)
    reason: str | None = Field(default=None, max_length=500)
    dry_run: bool = Field(default=True, alias="dryRun")


class AdminMasterDataEditApplyRequest(AdminMasterDataEditPreviewRequest):
    """Guarded request that can actually apply a validated scalar master-data edit.

    The endpoint must require the exact confirmation phrase before mutating DB.
    """

    confirm_text: str = Field(default="", alias="confirmText", max_length=80)
    dry_run: bool = Field(default=False, alias="dryRun")


class AdminChangeApplyRequest(AdminChangePreviewRequest):
    confirmed: bool = False
