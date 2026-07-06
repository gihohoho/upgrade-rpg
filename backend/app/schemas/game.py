from pydantic import BaseModel, Field


class GameSavePayload(BaseModel):
    save_version: int = Field(alias="saveVersion")
    server_state: dict = Field(alias="serverState")


class MasterDataResponseData(BaseModel):
    characters: list[dict] = []
    skills: list[dict] = []
    items: list[dict] = []
    bosses: list[dict] = []
    field_zones: list[dict] = []
    enhancement_rules: list[dict] = []
