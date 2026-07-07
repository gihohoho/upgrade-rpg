from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Idle RPG Backend"
    environment: str = "local"
    debug: bool = True
    api_prefix: str = "/api/v1"
    database_url: str = "postgresql+asyncpg://rpg_user:rpg_password@127.0.0.1:55432/rpg_game"
    jwt_secret_key: str = "change-me-before-production"
    access_token_expire_minutes: int = 1440
    # Local-only guard for dangerous admin write endpoints until real login/RBAC is added.
    # Read-only admin APIs do not require this key.
    admin_write_dev_key: str = "local-admin-dev-key"

    # pydantic-settings는 list[str] 환경변수를 JSON으로 먼저 파싱하려고 하므로,
    # 로컬 .env에서는 문자열로 받고 아래 프로퍼티에서 JSON/쉼표 형식을 모두 허용합니다.
    cors_origins_raw: str = Field(
        default="http://localhost:5500,http://127.0.0.1:5500,http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000",
        validation_alias="CORS_ORIGINS",
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins(self) -> list[str]:
        value = self.cors_origins_raw.strip()
        if not value:
            return []

        # JSON 리스트 형식: '["http://localhost:5173", "http://127.0.0.1:5500"]'
        if value.startswith("["):
            import json

            parsed = json.loads(value)
            if not isinstance(parsed, list):
                raise ValueError("CORS_ORIGINS JSON value must be a list")
            return [str(item).strip() for item in parsed if str(item).strip()]

        # 쉼표 형식: 'http://localhost:5173,http://127.0.0.1:5500'
        return [item.strip() for item in value.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
