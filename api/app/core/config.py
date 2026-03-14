from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    ENVIRONMENT: Literal["DEV", "HML", "PRD"] = "DEV"
    
    DB: str = "postgres"
    HOST: str = "localhost"
    DB_USER: str = "postgres"
    PASSWORD: str = "postgres"
    DATABASE: str = "fastapi"
    PORT: int = 5432
    
    # Security / Rate Limit Settings
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
