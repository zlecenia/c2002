import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./fleet_management.db")

    # Security
    secret_key: str = os.getenv("SECRET_KEY", "fleet-management-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # API
    api_v1_str: str = "/api/v1"
    project_name: str = "Fleet Management System"

    # CORS
    backend_cors_origins: list = ["*"]  # Allow all origins for Replit

    class Config:
        case_sensitive = True


settings = Settings()
