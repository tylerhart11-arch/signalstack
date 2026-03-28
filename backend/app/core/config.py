from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


LOCAL_DEV_FRONTEND_ORIGIN_REGEX = (
    r"^https?://("
    r"localhost|127\.0\.0\.1|0\.0\.0\.0|"
    r"10(?:\.\d{1,3}){3}|"
    r"192\.168(?:\.\d{1,3}){2}|"
    r"172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2}"
    r")(?::\d+)?$"
)


class Settings(BaseSettings):
    app_name: str = Field(default="SignalStack API", validation_alias="APP_NAME")
    api_prefix: str = Field(default="/api", validation_alias="API_PREFIX")
    frontend_origin: str = Field(default="http://localhost:3000", validation_alias="FRONTEND_ORIGIN")
    frontend_origin_regex: str | None = Field(
        default=LOCAL_DEV_FRONTEND_ORIGIN_REGEX,
        validation_alias="FRONTEND_ORIGIN_REGEX",
    )
    database_url: str = Field(
        default="postgresql+psycopg://signalstack:signalstack@localhost:5432/signalstack",
        validation_alias="DATABASE_URL",
    )
    refresh_on_startup: bool = Field(default=True, validation_alias="SIGNALSTACK_REFRESH_ON_STARTUP")
    background_refresh_enabled: bool = Field(
        default=True,
        validation_alias="SIGNALSTACK_BACKGROUND_REFRESH_ENABLED",
    )
    refresh_interval_hours: int = Field(
        default=1,
        validation_alias="SIGNALSTACK_REFRESH_INTERVAL_HOURS",
        ge=1,
    )
    exchange_calendar: str | None = Field(default="XNYS", validation_alias="SIGNALSTACK_EXCHANGE_CALENDAR")
    market_timezone: str = Field(default="America/New_York", validation_alias="SIGNALSTACK_MARKET_TIMEZONE")
    market_open_hour: int = Field(default=9, validation_alias="SIGNALSTACK_MARKET_OPEN_HOUR", ge=0, le=23)
    market_open_minute: int = Field(default=30, validation_alias="SIGNALSTACK_MARKET_OPEN_MINUTE", ge=0, le=59)
    market_close_hour: int = Field(default=16, validation_alias="SIGNALSTACK_MARKET_CLOSE_HOUR", ge=0, le=23)
    market_close_minute: int = Field(default=0, validation_alias="SIGNALSTACK_MARKET_CLOSE_MINUTE", ge=0, le=59)
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
