"""
Configuration settings for FastAPI i18n demo using Pydantic Settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Default locale
    default_locale: str = "en"
    
    # Supported locales
    supported_locales: list[str] = ["en", "es", "he"]
    
    # Locale directory path
    locale_dir: str = "locale"
    
    # Application name
    app_name: str = "FastAPI i18n Demo"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Create a global settings instance
settings = Settings()

