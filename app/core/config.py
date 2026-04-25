# ============================================
# CONFIGURACIÓN CORE - Settings
# ============================================

from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    # App
    APP_NAME: str = "POS v3 - Sistema de Punto de Venta"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    TESTING: bool = False  # Para tests
    
    # Database - URLs completas con driver
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/pos_test"
    DATABASE_URL_SYNC: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/pos_test"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
