from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB: str = "sqlite"
    HOST: str = "localhost"
    USER: str = "root"
    PASSWORD: str = "root"
    DATABASE: str = "fastapi"
    PORT: int = 5432

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
