from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="SignalStack API", validation_alias="APP_NAME")
    api_prefix: str = Field(default="/api", validation_alias="API_PREFIX")
    frontend_origin: str = Field(default="http://localhost:3000", validation_alias="FRONTEND_ORIGIN")
    database_url: str = Field(
        default="postgresql+psycopg://signalstack:signalstack@localhost:5432/signalstack",
        validation_alias="DATABASE_URL",
    )
    use_demo_data: bool = Field(default=True, validation_alias="SIGNALSTACK_USE_DEMO_DATA")
    refresh_on_startup: bool = Field(default=True, validation_alias="SIGNALSTACK_REFRESH_ON_STARTUP")
    market_lookback_days: int = Field(default=160, validation_alias="SIGNALSTACK_MARKET_LOOKBACK_DAYS")
    fred_api_key: str | None = Field(default=None, validation_alias="FRED_API_KEY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
