from functools import lru_cache
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "analytics_db"

    MOCK_API_BASE_URL: str = "http://localhost:8000"
    INGESTION_BATCH_SIZE: int = 5000
    INGESTION_PAGE_SIZE: int = 1000

    LOG_LEVEL: str = "INFO"
    APP_ENV: str = "development"

    @property
    def DATABASE_URL(self) -> str:
        password = quote_plus(self.DB_PASSWORD)

        return (
            f"mysql+pymysql://{self.DB_USER}:{password}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()