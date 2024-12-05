# Path: backend/app/config.py
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Project directory
    PROJECT_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # Server
    BACKEND_HOST: str = "46.8.29.89"
    BACKEND_PORT: int = 8000
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str = "development-secret-key"  # Временный ключ для разработки
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://46.8.29.89",
        "http://46.8.29.89:8000",
        "http://46.8.29.89:3000",
        "http://localhost:3000"
    ]
    
    # S3 Storage (опциональные настройки для разработки)
    S3_ENDPOINT_URL: str = "https://storage.yandexcloud.net"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    S3_BUCKET_NAME: str = "development-bucket"
    
    # Upload settings
    UPLOAD_DIR: str = os.path.join(PROJECT_DIR, "uploads")
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024

    class Config:
        env_file = ".env"

def get_settings() -> Settings:
    return Settings()