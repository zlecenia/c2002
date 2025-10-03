"""
Application configuration
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Connect++ CPP"
    APP_PORT: int = 8080
    APP_VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/fleetdb"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://192.168.1.100:8080"
    ]
    
    # WebSocket
    WS_PING_INTERVAL: int = 30
    WS_PING_TIMEOUT: int = 10
    
    # Device Settings
    DEVICE_MODE: str = "production"
    ENABLE_OFFLINE_MODE: bool = True
    SYNC_INTERVAL: int = 300
    
    # Sensor Configuration
    PRESSURE_LOW_MIN: float = -20.0
    PRESSURE_LOW_MAX: float = 0.0
    PRESSURE_MEDIUM_MIN: float = 0.0
    PRESSURE_MEDIUM_MAX: float = 50.0
    PRESSURE_HIGH_MIN: float = 0.0
    PRESSURE_HIGH_MAX: float = 300.0
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
