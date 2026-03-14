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
    
    # JWT Auth Settings
    SECRET_KEY: str = "super_secret_key_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15 
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 5

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
