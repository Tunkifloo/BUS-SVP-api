"""
Core configuration module.
Handles environment variables and application settings.
"""
from typing import List, Optional
from functools import lru_cache
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self):
        # Application Settings
        self.app_name: str = os.getenv("APP_NAME", "Sistema de Ventas de Pasajes")
        self.app_version: str = os.getenv("APP_VERSION", "1.0.0")
        self.debug: bool = os.getenv("DEBUG", "False").lower() == "true"
        self.secret_key: str = os.getenv("SECRET_KEY", "default-secret-key")
        self.algorithm: str = os.getenv("ALGORITHM", "HS256")
        self.access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

        # Database Settings
        self.database_url: str = os.getenv("DATABASE_URL", "")
        self.database_host: str = os.getenv("DATABASE_HOST", "localhost")
        self.database_port: int = int(os.getenv("DATABASE_PORT", "5432"))
        self.database_name: str = os.getenv("DATABASE_NAME", "bus_system_db")
        self.database_user: str = os.getenv("DATABASE_USER", "postgres")
        self.database_password: str = os.getenv("DATABASE_PASSWORD", "admin")

        # CORS Settings
        self.allowed_origins: List[str] = self._parse_list(os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173"))
        self.allowed_methods: List[str] = self._parse_list(os.getenv("ALLOWED_METHODS", "GET,POST,PUT,DELETE,OPTIONS"))
        self.allowed_headers: List[str] = self._parse_list(os.getenv("ALLOWED_HEADERS", "*"))

        # Email Settings
        self.smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username: Optional[str] = os.getenv("SMTP_USERNAME")
        self.smtp_password: Optional[str] = os.getenv("SMTP_PASSWORD")
        self.smtp_from_email: Optional[str] = os.getenv("SMTP_FROM_EMAIL")

        # File Storage
        self.upload_dir: str = os.getenv("UPLOAD_DIR", "uploads")
        self.max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "5242880"))

        # Logging
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.log_format: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        # Build database URL if not provided
        if not self.database_url:
            self.database_url = f"postgresql+psycopg2://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"

    def _parse_list(self, value: str) -> List[str]:
        """Parse comma-separated string into list."""
        if not value:
            return []
        return [item.strip() for item in value.split(',')]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()