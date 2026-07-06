from pydantic import BaseModel, Field


class AdminChangePreviewRequest(BaseModel):
    target_type: str = Field(examples=["item_template", "boss", "drop_table"])
    target_id: str
    before: dict = Field(default_factory=dict)
    after: dict = Field(default_factory=dict)
    reason: str | None = None


class AdminChangeApplyRequest(AdminChangePreviewRequest):
    confirmed: bool = False
