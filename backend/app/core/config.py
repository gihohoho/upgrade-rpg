import ssl
from functools import lru_cache
from urllib.parse import parse_qs, urlsplit

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


LOCAL_DEV_CORS_ORIGINS = (
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
)

LOCAL_JWT_SECRET = "change-me-before-production"
LOCAL_ADMIN_WRITE_KEY = "local-admin-dev-key"
PRODUCTION_ENVIRONMENTS = {"prod", "production"}


class Settings(BaseSettings):
    app_name: str = "Idle RPG Backend"
    environment: str = "local"
    debug: bool = True
    api_prefix: str = "/api/v1"
    database_url: str = "postgresql+asyncpg://rpg_user:rpg_password@127.0.0.1:55432/rpg_game"

    # SQLAlchemy runtime pool defaults are deliberately conservative. Local
    # development keeps the same single-engine behavior while production can
    # override every value through environment variables without code edits.
    db_pool_pre_ping: bool = True
    db_pool_size: int = Field(default=5, ge=1, le=100)
    db_max_overflow: int = Field(default=10, ge=0, le=200)
    db_pool_timeout_seconds: int = Field(default=30, ge=1, le=300)
    db_pool_recycle_seconds: int = Field(default=1800, ge=30, le=86400)

    jwt_secret_key: str = LOCAL_JWT_SECRET
    access_token_expire_minutes: int = 1440
    # Local-only guard for dangerous admin write endpoints until real login/RBAC is added.
    # Read-only admin APIs do not require this key.
    admin_write_dev_key: str = LOCAL_ADMIN_WRITE_KEY

    # pydantic-settings는 list[str] 환경변수를 JSON으로 먼저 파싱하려고 하므로,
    # 로컬 .env에서는 문자열로 받고 아래 프로퍼티에서 JSON/쉼표 형식을 모두 허용합니다.
    cors_origins_raw: str = Field(
        default="http://localhost:5500,http://127.0.0.1:5500,http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000",
        validation_alias="CORS_ORIGINS",
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @model_validator(mode="after")
    def validate_production_runtime_guard(self) -> "Settings":
        """Fail closed when production is started with local unsafe defaults."""
        environment = self.environment.strip().lower()
        if environment not in PRODUCTION_ENVIRONMENTS:
            return self

        errors: list[str] = []
        if self.debug:
            errors.append("DEBUG must be false in production")
        if self.jwt_secret_key == LOCAL_JWT_SECRET:
            errors.append("JWT_SECRET_KEY must not use the local default in production")
        if self.admin_write_dev_key == LOCAL_ADMIN_WRITE_KEY:
            errors.append("ADMIN_WRITE_DEV_KEY must not use the local default in production")
        if len(self.jwt_secret_key.strip()) < 32:
            errors.append("JWT_SECRET_KEY must contain at least 32 characters in production")
        if len(self.admin_write_dev_key.strip()) < 32:
            errors.append("ADMIN_WRITE_DEV_KEY must contain at least 32 characters in production")

        try:
            parsed_database_url = urlsplit(self.database_url)
            database_host = (parsed_database_url.hostname or "").strip().lower()
            database_query = parse_qs(parsed_database_url.query, keep_blank_values=True)
        except ValueError:
            errors.append("DATABASE_URL must be a valid URL in production")
        else:
            if parsed_database_url.scheme != "postgresql+asyncpg":
                errors.append("DATABASE_URL must use postgresql+asyncpg in production")
            if not database_host:
                errors.append("DATABASE_URL must contain a host in production")
            elif database_host in {"localhost", "127.0.0.1", "::1"}:
                errors.append("DATABASE_URL must not target localhost in production")
            if not parsed_database_url.path.strip("/"):
                errors.append("DATABASE_URL must contain a database name in production")
            conflicting_tls_keys = sorted(
                set(database_query)
                & {"channel_binding", "ssl", "sslmode", "sslrootcert"}
            )
            if conflicting_tls_keys:
                errors.append(
                    "DATABASE_URL must not contain TLS query parameters in production; "
                    "the application injects a verified SSL context"
                )

        if errors:
            raise ValueError("; ".join(errors))
        return self

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


def build_database_connect_args(
    current_settings: Settings | None = None,
) -> dict[str, object]:
    """Use the system CA store with hostname verification for production DB TLS."""
    selected_settings = current_settings or settings
    if selected_settings.environment.strip().lower() not in PRODUCTION_ENVIRONMENTS:
        return {}

    context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    if context.cert_store_stats().get("x509_ca", 0) < 1:
        raise RuntimeError("production database system CA trust store is empty")
    return {"ssl": context}
