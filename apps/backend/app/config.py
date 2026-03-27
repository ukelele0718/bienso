from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/vehicle_lpr"
    initial_balance_vnd: int = 100_000
    charge_per_event_vnd: int = 2_000

    model_config = SettingsConfigDict(env_prefix="APP_")


settings = Settings()
