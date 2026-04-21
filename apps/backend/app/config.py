from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/vehicle_lpr"
    initial_balance_vnd: int = 100_000
    charge_per_event_vnd: int = 2_000
    event_dedup_window_sec: int = 30  # Set to 0 to disable deduplication

    model_config = SettingsConfigDict(env_prefix="APP_")


settings = Settings()
