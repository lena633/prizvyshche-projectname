from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Настройки считывания из файла .env
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    data_path: Path = Path("data/large.jsonl")

    log_level: str = "INFO"

    large_amount_threshold: int = 3000


settings = Settings()
