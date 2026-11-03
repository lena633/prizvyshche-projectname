from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    data_path: Path = Path("data/large.jsonl")
    log_level: str = "INFO"
    batch_size: int = 500
    api_token: str = ""  # Добавили токен для будущих интеграций

def mask(secret: str) -> str:
    """Лишає видимими лише останні чотири символи."""
    if len(secret) <= 4:
        return "****"
    return "*" * (len(secret) - 4) + secret[-4:]
