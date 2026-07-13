from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


LOCAL_DEV_CORS_ORIGINS = (
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
)


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
        parsed_origins: list[str]
        if not value:
            parsed_origins = []
        elif value.startswith("["):
            # JSON 리스트 형식: '["http://localhost:5173", "http://127.0.0.1:5500"]'
            import json

            parsed = json.loads(value)
            if not isinstance(parsed, list):
                raise ValueError("CORS_ORIGINS JSON value must be a list")
            parsed_origins = [str(item).strip() for item in parsed if str(item).strip()]
        else:
            # 쉼표 형식: 'http://localhost:5173,http://127.0.0.1:5500'
            parsed_origins = [item.strip() for item in value.split(",") if item.strip()]

        # 기존 로컬 .env가 오래되어 5173(Vite) 포트가 빠져 있어도,
        # local/debug 환경에서는 Vue 개발 서버가 API를 읽을 수 있어야 합니다.
        # 운영에서는 CORS_ORIGINS에 명시한 값만 사용합니다.
        if self.environment == "local" or self.debug:
            merged = [*parsed_origins, *LOCAL_DEV_CORS_ORIGINS]
        else:
            merged = parsed_origins

        return list(dict.fromkeys(merged))


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
