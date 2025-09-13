import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application configuration settings
    Loads from environment variables and .env file
    """
    
    # Supabase Configuration
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    supabase_jwt_secret: str = os.getenv("SUPABASE_JWT_SECRET", "")
    
    # Database Configuration
    database_url: str = os.getenv("DATABASE_URL", "")
    
    # JWT Configuration
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "backend-jwt-secret-key-production-12345")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_access_token_expire_minutes: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # API Configuration
    api_v1_str: str = os.getenv("API_V1_STR", "/api/v1")
    project_name: str = os.getenv("PROJECT_NAME", "Notes App Backend")
    
    # Application Configuration
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()
