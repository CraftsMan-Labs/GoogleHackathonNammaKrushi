from __future__ import annotations

import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # App Settings
    APP_NAME: str = "Namma Krushi"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./namma_krushi.db"

    # Security
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "namma-krushi-secret-key-change-in-production"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Google AI
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = "gemini-pro"
    GEMINI_VISION_MODEL: str = "gemini-pro-vision"
    GEMINI_LIVE_MODEL: str = "gemini-live-2.5-flash-preview"

    # Google APIs
    GOOGLE_SEARCH_API_KEY: Optional[str] = os.getenv("GOOGLE_SEARCH_API_KEY")
    GOOGLE_SEARCH_CSE_ID: Optional[str] = os.getenv("GOOGLE_SEARCH_CSE_ID")
    GOOGLE_VISION_API_KEY: Optional[str] = os.getenv("GOOGLE_VISION_API_KEY")

    # External APIs
    WEATHER_API_KEY: Optional[str] = os.getenv("WEATHER_API_KEY")
    OPENWEATHER_API_KEY: Optional[str] = os.getenv("OPENWEATHER_API_KEY")
    WEATHER_API_URL: str = "https://api.openweathermap.org/data/2.5"

    # Exa AI Search API
    EXA_API_KEY: Optional[str] = os.getenv("EXA_API_KEY")
    EXA_API_URL: str = "https://api.exa.ai"

    # Voice Settings
    SPEECH_LANGUAGE_CODE: str = "kn-IN"  # Kannada
    VOICE_NAME: str = "kn-IN-Standard-A"

    class Config:
        env_file = ".env"
        extra = "allow"
        case_sensitive = True


settings = Settings()
