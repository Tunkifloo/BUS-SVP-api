"""
Core configuration module.
Handles environment variables and application settings.
"""
from typing import List, Optional
from pydantic import BaseSettings, validator
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application Settings
    app_name: str = "Sistema de Ventas de Pasajes"
    app_version: str = "1.0.0"
    debug: bool = False
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Database Settings
    database_url: str
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "bus_system_db"
    database_user: str
    database_password: str

    # CORS Settings
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    allowed_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allowed_headers: List[str] = ["*"]

    # Email Settings
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: Optional[str] = None

    # File Storage
    upload_dir: str = "uploads"
    max_file_size: int = 5242880  # 5MB

    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @validator('allowed_origins', pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v

    @validator('allowed_methods', pre=True)
    def parse_cors_methods(cls, v):
        """Parse CORS methods from comma-separated string."""
        if isinstance(v, str):
            return [method.strip() for method in v.split(',')]
        return v

    @validator('database_url', pre=True)
    def build_database_url(cls, v, values):
        """Build database URL if not provided."""
        if v:
            return v

        user = values.get('database_user')
        password = values.get('database_password')
        host = values.get('database_host', 'localhost')
        port = values.get('database_port', 5432)
        db_name = values.get('database_name')

        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()