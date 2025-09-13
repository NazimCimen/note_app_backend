from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # Supabase Configuration
    supabase_url: str
    supabase_key: str
    supabase_jwt_secret: str
    
    # Database Configuration
    database_url: str
    
    # API Configuration
    api_v1_str: str = "/api/v1"
    project_name: str = "Notes App Backend"
    
    # Environment
    debug: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()