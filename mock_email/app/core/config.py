from functools import lru_cache

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]
ENV_FILE = ROOT_DIR / ".env"


class EmailConfig(BaseSettings):
    host: str = "localhost"
    port: int = 8001
    request_per_minute: int = 100
    burst_per_second: int = 10
    daily_quota: int = 10000


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE if ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
    )

    # Environment
    env: str = "development"

    debug: bool = False

    # Email
    email: EmailConfig


@lru_cache
def get_config() -> Config:
    return Config()


config = get_config()
