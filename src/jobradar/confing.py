from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Настройки считывания из файла .env
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    # Путь к файлу бюджета (используем строгий Path вместо str для удобства mypy и pathlib)
    data_path: Path = Path("data/large.jsonl")
    
    # Уровень логирования приложения
    log_level: str = "INFO"
    
    # Порог для определения крупных бюджетных статей общины (например, больше 3000 тыс. грн)
    large_amount_threshold: int = 3000

settings = Settings()