"""
Environment configuration using Pydantic Settings v2.
Loads from .env file or environment variables.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_port: int = 8000
    app_host: str = "0.0.0.0"
    database_url: str
    db_min_pool_size: int = 2
    db_max_pool_size: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
